# SPDX-License-Identifier: MIT
"""Bounded WDI annual series with frozen paginated JSON and null preservation."""
import argparse, hashlib, json, re, sys
from datetime import datetime, timezone
from decimal import Decimal
from html import escape
from pathlib import Path
from urllib.parse import urlencode
from .public_download import download
from .market import read
from ._contract import unique, reject_constant, loads

def request(spec):
    if set(spec)!={'countries','indicator','start','end'}: raise ValueError('请求须为countries/indicator/start/end')
    if not isinstance(spec['countries'],list) or not 1<=len(spec['countries'])<=30 or len(set(spec['countries']))!=len(spec['countries']): raise ValueError('需要1至30个不同三位地区码')
    if any(not isinstance(x,str) or not re.fullmatch('[A-Z]{3}',x) for x in spec['countries']): raise ValueError('地区码须为三位大写字符串；聚合地区码不得冒充国家')
    if not isinstance(spec['indicator'],str) or not re.fullmatch('[A-Z0-9_.]{1,100}',spec['indicator']): raise ValueError('指标代码格式不符')
    if any(type(spec[x]) is not int for x in ('start','end')) or not 1960<=spec['start']<=spec['end']<=datetime.now(timezone.utc).year: raise ValueError('年度范围不符')
    return dict(spec)

from .wdi_core import parse

def main(argv=None):
    for stream in (sys.stdout,sys.stderr):
        if hasattr(stream,'reconfigure'):stream.reconfigure(encoding='utf-8')
    p=argparse.ArgumentParser(description='世界银行WDI年度序列；显式地区、指标和区间，不补空值')
    p.add_argument('command',choices=['collect','replay']);p.add_argument('--input',type=Path,required=True);p.add_argument('--online',action='store_true');p.add_argument('--out-dir',type=Path,required=True);a=p.parse_args(argv)
    try:
        if a.out_dir.exists():raise ValueError('输出目录已存在')
        inp=loads(read(a.input).decode('utf-8-sig')); old=None
        if a.command=='replay':
            old=inp
            if old.get('schemaVersion')!='cn-wdi-archive/1.0' or old.get('status')!='success':raise ValueError('需要成功的冻结WDI快照')
            spec=request(old['request'])
        else:
            spec=request(inp)
            if not a.online:raise ValueError('联网需要--online')
        a.out_dir.mkdir(parents=True)
        result=dict(schemaVersion='cn-wdi-archive/1.0',request=spec,status='failed',attemptedAt=datetime.now(timezone.utc).isoformat(),retrievedAt=old['retrievedAt'] if old else None,replayedAt=datetime.now(timezone.utc).isoformat() if old else None,pages=[],data=[],limitations=['WDI来源2年度序列，不等于国内发布口径','单位字段为空时保留未知，需核对指标元数据','地区码可能是聚合地区；不自动认定为国家','冻结版本不代表历史首次发布版本；源数据权利单独核对'])
        try:
            page=1; all_rows=[]; seen=set(); total=None
            while True:
                if old:
                    entry=old['pages'][page-1]
                    if entry['page']!=page or entry['file']!=f'page-{page}.json':raise ValueError('冻结分页顺序或文件名不符')
                    raw=read(a.input.parent/entry['file'])
                    if hashlib.sha256(raw).hexdigest()!=entry['sha256']:raise ValueError('冻结原件摘要不符')
                    url=entry['url']
                else:
                    url='https://api.worldbank.org/v2/country/'+(';'.join(spec['countries']))+'/indicator/'+spec['indicator']+'?'+urlencode(dict(source=2,format='json',date=f'{spec["start"]}:{spec["end"]}',per_page=5000,page=page,footnote='y'))
                    raw=download(url,allowed_hosts={'api.worldbank.org'},limit=16*1024*1024,timeout=30,return_metadata=True)['raw']
                name=f'page-{page}.json';(a.out_dir/name).write_bytes(raw)
                result['pages'].append(dict(page=page,file=name,url=url,sha256=hashlib.sha256(raw).hexdigest(),byteCount=len(raw)))
                meta,rows=parse(raw,spec,page)
                if total is not None and (int(meta['total'])!=total or int(meta['pages'])!=pages):raise ValueError('采集中分页总数变化；需重新冻结')
                total,pages=int(meta['total']),int(meta['pages'])
                for row in rows:
                    key=(row['regionCode'],row['indicatorId'],row['period'])
                    if key in seen:raise ValueError('分页含重复记录')
                    seen.add(key);all_rows.append(row)
                if page==pages:break
                page+=1
            if len(all_rows)!=total:raise ValueError('记录数不符，不能宣称完整区间')
            if old and len(old['pages'])!=pages:raise ValueError('冻结页数不符')
            result.update(status='success',retrievedAt=result['retrievedAt'] or datetime.now(timezone.utc).isoformat(),data=all_rows)
            for row in all_rows:row['availableAt']=result['retrievedAt']
        except Exception as exc:result['error']=type(exc).__name__+': '+str(exc)
        (a.out_dir/'snapshot.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        (a.out_dir/'打开这里.html').write_text('<!doctype html><meta charset="utf-8"><h1>国际年度数据采集</h1><p>状态：'+escape(result['status'])+'；记录数：'+str(len(result['data']))+'</p><p>'+escape(result.get('error','下一步核对单位、地区分类、来源方法和版本；未知值不填零。'))+'</p>',encoding='utf-8')
        print('WDI状态：'+result['status']+'；结果：'+str(a.out_dir/'打开这里.html'));return 0 if result['status']=='success' else 2
    except (ValueError,OSError,KeyError,TypeError) as exc:print('未完成：'+str(exc),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
