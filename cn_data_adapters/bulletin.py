# SPDX-License-Identifier: MIT
"""Extract literal HTML table cells from a frozen official response; no guessed units."""
import argparse
import hashlib
import json
import sys
import re
from decimal import Decimal
from datetime import datetime, timezone
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from .market import read
from ._contract import loads

class Tables(HTMLParser):
    def __init__(self):
        super().__init__(); self.tables=[]; self.depth=0; self.table=None; self.row=None; self.cell=None; self.hidden=0
    def handle_starttag(self, tag, attrs):
        if tag in ('script','style'): self.hidden+=1
        if tag=='table':
            self.depth+=1
            if self.depth==1: self.table=[]
        if self.depth!=1: return
        if tag=='tr': self.row=[]
        if tag in ('td','th'):
            data=dict(attrs)
            spans={name:int(data.get(name,'1')) for name in ('rowspan','colspan')}
            if any(not 1<=v<=1000 for v in spans.values()): raise ValueError('跨行跨列范围不合理')
            self.cell=dict(text='',kind=tag,**spans)
        if tag=='br' and self.cell is not None: self.cell['text']+='\n'
    def handle_data(self,data):
        if self.cell is not None and not self.hidden and self.depth==1: self.cell['text']+=data
    def handle_endtag(self,tag):
        if tag in ('script','style'): self.hidden=max(0,self.hidden-1)
        if tag in ('td','th') and self.cell is not None and self.depth==1:
            self.cell['text']=self.cell['text'].strip()
            if self.row is not None: self.row.append(self.cell)
            self.cell=None
        if tag=='tr' and self.row is not None and self.depth==1:
            if self.row: self.table.append(self.row)
            self.row=None
        if tag=='table':
            if self.depth==1 and self.table: self.tables.append(self.table)
            self.depth=max(0,self.depth-1)

def extract(raw):
    try: text=raw.decode('utf-8-sig')
    except UnicodeDecodeError: text=raw.decode('gb18030')
    parser=Tables(); parser.feed(text)
    if not parser.tables: raise ValueError('响应没有可识别HTML表格；图片/PDF/脚本数据需专用适配')
    if sum(len(r) for t in parser.tables for r in t)>100000: raise ValueError('表格单元格过多')
    return parser.tables

def map_cells(tables, mapping):
    if not isinstance(mapping,list) or not 1<=len(mapping)<=10000: raise ValueError('映射须为1至10000项列表')
    records=[];seen=set()
    for item in mapping:
        if set(item)!={'indicatorId','tableIndex','rowLabel','columnIndex','expectedHeader','period','unit','scope'}: raise ValueError('映射字段不完整或含未知字段')
        if any(not isinstance(item[k],str) or not item[k].strip() for k in ('indicatorId','rowLabel','expectedHeader','period','unit','scope')): raise ValueError('指标、标签、表头、统计期、单位和范围必须明确')
        t,c=item['tableIndex'],item['columnIndex']
        if type(t) is not int or type(c) is not int or not 0<=t<len(tables) or c<1: raise ValueError('表格或列索引越界')
        table=tables[t]
        if not table or c>=len(table[0]) or table[0][c]['text']!=item['expectedHeader']: raise ValueError('原表表头不符；停止映射，不能沿用旧版猜值')
        matches=[(i,row) for i,row in enumerate(table) if row and row[0]['text']==item['rowLabel']]
        if len(matches)!=1: raise ValueError('行标签不存在或重复；不能猜选')
        r,row=matches[0]
        if c>=len(row) or any(cell['colspan']!=1 or cell['rowspan']!=1 for cell in row): raise ValueError('映射行跨行跨列或列缺失；需专用适配')
        raw=row[c]['text'];unknown=raw in ('','..','...','—','-')
        if not unknown and not re.fullmatch(r'-?\d+(?:\.\d+)?',raw): raise ValueError('单元格不是简单十进制数；括号实际增速等需专门口径')
        key=(item['indicatorId'],item['period'],item['scope'])
        if key in seen: raise ValueError('映射指标、统计期与范围重复')
        seen.add(key)
        records.append(dict(item,value=None if unknown else str(Decimal(raw)),unknownReason='原表缺失符号' if unknown else None,locator={'tableIndex':t,'rowIndex':r,'columnIndex':c},rawText=raw,semanticStatus='user-declared-period-unit-scope'))
    return records

def main(argv=None):
    for stream in (sys.stdout,sys.stderr):
        if hasattr(stream,'reconfigure'): stream.reconfigure(encoding='utf-8')
    p=argparse.ArgumentParser(description='从已冻结官方HTML响应提取表格原文；不猜指标、单位或统计期')
    p.add_argument('--mapping',type=Path,help='明确的指标/原文行列/单位/统计期映射JSON');p.add_argument('--snapshot',type=Path,required=True);p.add_argument('--raw',type=Path,required=True);p.add_argument('--out-dir',type=Path,required=True);a=p.parse_args(argv)
    try:
        if a.out_dir.exists(): raise ValueError('输出目录已存在')
        source=loads(read(a.snapshot).decode('utf-8-sig'));raw=read(a.raw)
        if source.get('schemaVersion')!='cn-public-response-archive/1.0' or source.get('status')!='response-received': raise ValueError('需要已取得官方响应档案')
        if hashlib.sha256(raw).hexdigest()!=source.get('rawSha256') or len(raw)!=source.get('byteCount'): raise ValueError('原件摘要或大小不匹配')
        tables=extract(raw)
        result=dict(schemaVersion='cn-bulletin-cells/1.0',sourceRequest=source['request'],rawSha256=source['rawSha256'],retrievedAt=source['retrievedAt'],extractedAt=datetime.now(timezone.utc).isoformat(),publishedAt=source.get('publishedAt'),tables=tables,observations=[],limitations=['仅保留表格单元格原文与跨行跨列，不自动推断单位、统计期、同比或累计','网页表格可能含导航；需要选择正文数据表并核对注释','取得时点不等于历史首次可得时点；来源内容未认证'])
        if a.mapping:
            mapping_raw=read(a.mapping); result['mappingSha256']=hashlib.sha256(mapping_raw).hexdigest(); result['observations']=map_cells(tables,loads(mapping_raw.decode('utf-8-sig')))
        for observation in result['observations']:
            observation.update(availableAt=source['retrievedAt'],sourceUrl=source['request']['url'],rawSha256=source['rawSha256'])
        a.out_dir.mkdir(parents=True);(a.out_dir/'tables.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        body=''.join('<h2>表 '+str(i+1)+'</h2><table border="1">'+''.join('<tr>'+''.join('<td rowspan="'+str(c['rowspan'])+'" colspan="'+str(c['colspan'])+'">'+escape(c['text'])+'</td>' for c in row)+'</tr>' for row in table)+'</table>' for i,table in enumerate(tables))
        summary=''.join('<li>'+escape(o['rowLabel'])+'：'+escape(str(o['value']) if o['value'] is not None else '未知')+' '+escape(o['unit'])+'；'+escape(o['period'])+'；'+escape(o['scope'])+'</li>' for o in result['observations'])
        (a.out_dir/'打开这里.html').write_text('<!doctype html><meta charset="utf-8"><h1>发布表格与明确映射</h1><p>统计期、地区与单位按映射声明，未自动认证。下一步逐项核对表下注释；取得时点不等于历史首次发布时点。未提供映射时不生成数值指标。</p><ul>'+summary+'</ul>'+body,encoding='utf-8')
        print('已提取 '+str(len(tables))+' 张HTML表格：'+str(a.out_dir/'打开这里.html'));return 0
    except (ValueError,OSError,KeyError,TypeError) as exc: print('未完成：'+str(exc),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
