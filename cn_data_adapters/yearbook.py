# SPDX-License-Identifier: MIT
"""NBS yearbook discovery and bounded original-table archives, without OCR claims."""
import argparse
import hashlib
import json
import re
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from .public_download import download

HOST = 'www.stats.gov.cn'

class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.href = None; self.text = []; self.links = []
    def handle_starttag(self, tag, attrs):
        if tag == 'a': self.href = dict(attrs).get('href'); self.text = []
    def handle_data(self, data):
        if self.href: self.text.append(data)
    def handle_endtag(self, tag):
        if tag == 'a' and self.href:
            self.links.append((self.href, ''.join(self.text).strip())); self.href = None

def decode(raw):
    for encoding in ('utf-8-sig', 'gb18030'):
        try: return raw.decode(encoding)
        except UnicodeDecodeError: pass
    raise ValueError('目录编码无法确认')

def discover(raw, year):
    if not isinstance(year, int) or not 1999 <= year <= datetime.now(timezone.utc).year:
        raise ValueError('年份必须为1999年至当前年；存在性另行核验')
    base = f'https://{HOST}/sj/ndsj/{year}/'
    parser = Links(); parser.feed(decode(raw)); rows = []; seen = set()
    for href, title in parser.links:
        url = urljoin(base, href); parts = urlsplit(url)
        match = re.fullmatch(r'/sj/ndsj/'+str(year)+r'/html/([CA])(\d{2}|fu)-(\d{2,3})\.(jpg|jpeg|png|htm|html|xls|xlsx)', parts.path, re.I)
        if not match or parts.scheme != 'https' or parts.hostname != HOST or parts.query or parts.fragment: continue
        if match[1].upper()=='C' and match[2].isdigit() and not 1<=int(match[2])<=28: continue
        if url in seen: continue
        seen.add(url)
        rows.append({'id': Path(parts.path).stem, 'chapter': int(match[2]) if match[1].upper() == 'C' and match[2].isdigit() else 'appendix',
                     'title': title, 'url': url, 'format': match[4].lower(), 'status': 'discovered',
                     'structuredValues': None, 'observationPeriod': None, 'unit': None})
    if not rows: raise ValueError('未识别年鉴数据表；可能为错误页或目录格式已变化')
    return rows

def fetch(url):
    return download(url, allowed_hosts={HOST}, limit=16*1024*1024, timeout=30, return_metadata=True)

def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'): stream.reconfigure(encoding='utf-8')
    p = argparse.ArgumentParser(description='国家统计局年鉴全章节目录与原表留档；图片不自动变成数值')
    p.add_argument('--year', type=int, required=True); p.add_argument('--online', action='store_true')
    p.add_argument('--index-raw', type=Path, help='离线重解析本地目录原件')
    p.add_argument('--chapters', help='逗号分隔章节；不填则所有已发现章节')
    p.add_argument('--max-tables', type=int, default=0, help='最多下载多少张原表，0表示只建目录，最大2000')
    p.add_argument('--per-chapter', type=int, default=0, help='每章下载上限，0表示不限；1可用于全章节样本验收')
    p.add_argument('--workers',type=int,default=1,help='并发下载数，1至4；默认顺序采集')
    p.add_argument('--out-dir', type=Path, required=True); a = p.parse_args(argv)
    raw=None; record_failure=False
    try:
        if a.out_dir.exists(): raise ValueError('输出目录已存在；请换新目录')
        if not 1<=a.workers<=4: raise ValueError('并发数须为1至4')
        if not 0 <= a.max_tables <= 2000: raise ValueError('下载数量必须为0至2000')
        if not 0 <= a.per_chapter <= 2000: raise ValueError('每章上限须为0至2000')
        if not 1999 <= a.year <= datetime.now(timezone.utc).year: raise ValueError('年份超出范围')
        chapters = {int(x) for x in a.chapters.split(',')} if a.chapters else None
        if chapters is not None and (not chapters or not chapters <= set(range(1,29))): raise ValueError('章节须为1至28')
        record_failure=True
        if a.index_raw:
            if a.index_raw.is_symlink() or a.index_raw.stat().st_size > 16*1024*1024: raise ValueError('目录输入不合要求')
            raw = a.index_raw.read_bytes(); retrieved = None
        else:
            if not a.online: raise ValueError('联网需要--online；离线使用--index-raw')
            raw = fetch(f'https://{HOST}/sj/ndsj/{a.year}/left.htm')['raw']
            retrieved = datetime.now(timezone.utc).isoformat()
        rows = discover(raw, a.year)
        if a.max_tables and not a.online: raise ValueError('原表下载需要--online')
        a.out_dir.mkdir(parents=True); (a.out_dir/'index-response.bin').write_bytes(raw)
        manifest = {'schemaVersion':'cn-yearbook-archive/1.0','edition':a.year,'retrievedAt':retrieved,
                    'parsedAt':datetime.now(timezone.utc).isoformat(),'indexSha256':hashlib.sha256(raw).hexdigest(),
                    'chapterCoverage': sorted({r['chapter'] for r in rows if isinstance(r['chapter'],int)}),
                    'limitations':['目录覆盖不等于数值覆盖','年鉴版次不等于每张表统计期','图片尚未OCR或人工核对','原表权利不随MIT代码许可转移'], 'tables':rows}
        selected=[]; per_chapter={}
        for row in rows:
            if len(selected)>=a.max_tables: break
            if chapters is not None and row['chapter'] not in chapters: continue
            if a.per_chapter and per_chapter.get(row['chapter'],0)>=a.per_chapter: continue
            selected.append(row); per_chapter[row['chapter']]=per_chapter.get(row['chapter'],0)+1
        total_bytes=0; lock=threading.Lock(); stopped=threading.Event()
        def archive(row):
            nonlocal total_bytes
            if stopped.is_set():
                with lock: row.update(status='not-attempted',error='本批源响应异常或字节上限已到，停止后续请求')
                return
            result={}; body=None
            try:
                response=fetch(row['url']);body=response['raw']
                with lock:
                    total_bytes+=len(body)
                    if total_bytes>256*1024*1024: stopped.set();raise ValueError('本批超过256MiB；请分章采集')
                if row['format'] in ('jpg','jpeg') and not body.startswith(b'\xff\xd8\xff'):
                    stopped.set(); raise ValueError('响应不是JPEG原表；停止本批后续请求，不绕过异常响应')
                if row['format']=='png' and not body.startswith(b'\x89PNG\r\n\x1a\n'):
                    stopped.set(); raise ValueError('响应不是PNG原表；停止本批后续请求')
                name=row['id']+'.'+row['format'];(a.out_dir/name).write_bytes(body)
                result.update(status='original-archived' if row['format'] in ('jpg','jpeg','png') else 'response-received',file=name,sha256=hashlib.sha256(body).hexdigest(),byteCount=len(body),retrievedAt=datetime.now(timezone.utc).isoformat())
            except Exception as exc:
                result.update(status='failed',error=type(exc).__name__+': '+str(exc))
                if body is not None:
                    name=row['id']+'.failed-response.bin';(a.out_dir/name).write_bytes(body)
                    result.update(failedResponseFile=name,failedResponseSha256=hashlib.sha256(body).hexdigest(),failedResponseByteCount=len(body))
            with lock: row.update(result)
            time.sleep(0.3)
        with ThreadPoolExecutor(max_workers=a.workers) as pool:
            futures=[pool.submit(archive,row) for row in selected]
            for count,future in enumerate(as_completed(futures),1):
                future.result()
                print(f'原表处理 {count}/{len(selected)}',flush=True)
                with lock:
                    (a.out_dir/'snapshot.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
        manifest['attemptedTables']=sum(r['status'] not in ('discovered','not-attempted') for r in rows)
        (a.out_dir/'snapshot.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
        items = ''.join('<tr><td>'+escape(str(r['chapter']))+'</td><td>'+escape(r['title'])+'</td><td>'+escape(r['status'])+'</td></tr>' for r in rows)
        (a.out_dir/'打开这里.html').write_text('<!doctype html><meta charset="utf-8"><title>年鉴采集结果</title><h1>年鉴目录与原表</h1><p>已识别 '+str(len(rows))+' 张表。原表留档不是数值提取；下一步核对统计期、单位及表下注释。查看 snapshot.json 可复查摘要与失败原因。</p><table><tr><th>章节</th><th>表名</th><th>状态</th></tr>'+items+'</table>',encoding='utf-8')
        print('结果入口：'+str(a.out_dir/'打开这里.html'))
        return 2 if any(r['status'] in ('failed','not-attempted') for r in rows) else 0
    except (ValueError,OSError) as exc:
        if record_failure and not a.out_dir.exists():
            a.out_dir.mkdir(parents=True)
            if raw is not None: (a.out_dir/'index-response.bin').write_bytes(raw)
            failure=dict(schemaVersion='cn-yearbook-archive/1.0',edition=a.year,status='failed',attemptedAt=datetime.now(timezone.utc).isoformat(),error=type(exc).__name__+': '+str(exc),tables=[],indexSha256=hashlib.sha256(raw).hexdigest() if raw is not None else None)
            (a.out_dir/'snapshot.json').write_text(json.dumps(failure,ensure_ascii=False,indent=2),encoding='utf-8')
            (a.out_dir/'打开这里.html').write_text('<!doctype html><meta charset="utf-8"><h1>年鉴采集未完成</h1><p>'+escape(str(exc))+'</p><p>原始响应及失败记录保留；没有用缓存或其他源冒充本次成功。</p>',encoding='utf-8')
        print('未完成：'+str(exc),file=sys.stderr); return 2

if __name__ == '__main__': raise SystemExit(main())
