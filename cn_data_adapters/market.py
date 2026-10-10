# SPDX-License-Identifier: MIT
"""Bounded daily stock/ETF response archives and explicit MarketLens CSV exports."""
import argparse,csv,hashlib,io,json,re,sys,tempfile,os,shutil
from datetime import date,datetime,timezone
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlencode
from .public_download import download
from ._contract import loads,canonical,digest

SCHEMA='cn-market-daily-archive/1.0'
FIELDS=['date','available_at','instrument','name','index_id','category','open','high','low','close','volume_shares','amount_cny','price_factor']

def read(path):
    path=Path(path)
    if not path.is_file() or path.is_symlink() or path.stat().st_size>16*1024*1024:raise ValueError('输入缺失、链接或超过16MiB')
    return path.read_bytes()

def request(spec):
    if set(spec)!={'market','code','kind','start','end'}:raise ValueError('行情请求须且只须market/code/kind/start/end')
    if spec['market'] not in ('SSE','SZSE') or spec['kind'] not in ('stock','etf'):raise ValueError('限定沪深股票或ETF；证券类型由使用者明确核对')
    if not isinstance(spec['code'],str) or not re.fullmatch('[0-9]{6}',spec['code']):raise ValueError('代码须六位字符串')
    start,end=date.fromisoformat(spec['start']),date.fromisoformat(spec['end'])
    if start>end or (end-start).days>366 or end>datetime.now(timezone.utc).date():raise ValueError('区间须不超过366天且不含未来日期')
    return dict(spec)

def url_for(spec):
    r=request(spec)
    return 'https://push2his.eastmoney.com/api/qt/stock/kline/get?'+urlencode({'secid':('1' if r['market']=='SSE' else '0')+'.'+r['code'],'klt':101,'fqt':0,'beg':r['start'].replace('-',''),'end':r['end'].replace('-',''),'fields1':'f1,f2,f3,f4,f5,f6','fields2':'f51,f52,f53,f54,f55,f56,f57','lmt':1000})

def instant(value):
    parsed=datetime.fromisoformat(value)
    if parsed.tzinfo is None:raise ValueError('时间必须含时区')
    return parsed

def parse(raw,spec,retrieved_at):
    r=request(spec);acquired=instant(retrieved_at)
    if not isinstance(raw,bytes) or len(raw)>16*1024*1024:raise ValueError('行情响应须为不超过16MiB的字节')
    obj=loads(raw.decode('utf-8-sig'));data=obj.get('data')
    if not isinstance(data,dict) or data.get('code')!=r['code'] or str(data.get('market'))!=('1' if r['market']=='SSE' else '0'):raise ValueError('渠道证券身份不匹配')
    if not isinstance(data.get('name'),str) or not data['name'].strip():raise ValueError('渠道名称缺失')
    lines=data.get('klines')
    if not isinstance(lines,list) or not lines or len(lines)>=1000:raise ValueError('无数据或可能截断；不等同无交易')
    rows=[]
    for line in lines:
        if not isinstance(line,str):raise ValueError('行情行须为文本')
        parts=line.split(',')
        if len(parts)!=7:raise ValueError('渠道字段数量变化，停止解析')
        day=date.fromisoformat(parts[0]);nums=[Decimal(v) for v in parts[1:]]
        if not all(v.is_finite() for v in nums):raise ValueError('行情数值非有限')
        op,close,high,low,lots,amount=nums
        if min(op,close,high,low)<=0 or min(lots,amount)<0 or high<max(op,close,low) or low>min(op,close,high):raise ValueError('价格、成交量或金额无效')
        if not r['start']<=parts[0]<=r['end'] or day>acquired.date():raise ValueError('行情日期越界或晚于取得日期')
        rows.append({'date':parts[0],'open':str(op),'close':str(close),'high':str(high),'low':str(low),'volume_shares':None,'providerVolume':str(lots),'amount_cny':str(amount)})
    if [x['date'] for x in rows]!=sorted(set(x['date'] for x in rows)):raise ValueError('行情日期重复或乱序')
    return {'schemaVersion':SCHEMA,'request':r,'status':'success','name':data['name'],'sourceUrl':url_for(r),'rawSha256':hashlib.sha256(raw).hexdigest(),'retrievedAt':retrieved_at,'replayedAt':None,'data':rows,'priceBasis':'unadjusted','volumeBasis':'provider unit not certified; volume_shares remains null','coverage':'unknown: not certified against exchange calendar','identityVerification':'third-party-code-market-matched; kind supplied by caller','rights':'not assessed; local research archive, no redistribution grant'}

def replay(snapshot,raw):
    if snapshot.get('schemaVersion')!=SCHEMA or digest(raw)!=snapshot.get('rawSha256'):raise ValueError('冻结响应摘要或格式版本不匹配')
    rebuilt=parse(raw,snapshot['request'],snapshot['retrievedAt'])
    if rebuilt!=dict(snapshot,replayedAt=None):raise ValueError('冻结快照与原始响应不一致')
    rebuilt['replayedAt']=datetime.now(timezone.utc).isoformat();return rebuilt

def export(snapshot,decl):
    if set(decl)!={'priceFactor','factorEvidence','category','indexId'}:raise ValueError('导出需明确复权因子、依据、类别和指数身份')
    if decl['priceFactor']!='1' or not isinstance(decl['factorEvidence'],str) or not decl['factorEvidence'].strip():raise ValueError('首版只接受已人工核对全区间可比且因子为1；未知或有公司行动不得猜因子')
    if decl['category'] not in ('宽基','行业','主题','跨境','其他') or not isinstance(decl['indexId'],str):raise ValueError('类别或指数标识无效')
    if snapshot['request']['kind']=='stock' and decl['category']!='其他':raise ValueError('股票类别限定其他；不冒充ETF分类')
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=FIELDS);writer.writeheader()
    for row in snapshot['data']:
        values={k:v for k,v in row.items() if k in FIELDS}
        writer.writerow(dict(values,available_at=snapshot['retrievedAt'],instrument=snapshot['request']['market']+':'+snapshot['request']['code'],name=snapshot['name'],index_id=decl['indexId'],category=decl['category'],price_factor='1'))
    return out.getvalue().encode('utf-8')

def publish(out,spec,snapshot,raw,decl=None):
    out=Path(out).absolute()
    if out.exists():raise ValueError('必须使用新输出目录')
    out.parent.mkdir(parents=True,exist_ok=True);stage=Path(tempfile.mkdtemp(prefix='.market-',dir=out.parent))
    try:
        (stage/'request.json').write_bytes(canonical(spec));(stage/'snapshot.json').write_bytes(canonical(snapshot))
        if raw is not None:(stage/'response.json').write_bytes(raw)
        if decl is not None:
            (stage/'export-declaration.json').write_bytes(canonical(decl));(stage/'market.csv').write_bytes(export(snapshot,decl))
        (stage/'receipt.json').write_bytes(canonical({'files':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in stage.iterdir()},'scope':'摘要绑定，不是来源/交易日历/复权认证'}))
        os.rename(stage,out)
    finally:
        if stage.exists():shutil.rmtree(stage)

def main(argv=None):
    for stream in (sys.stdout,sys.stderr):
        if hasattr(stream,'reconfigure'):stream.reconfigure(encoding='utf-8')
    p=argparse.ArgumentParser(description='沪深股票/ETF日线采集、冻结重放及MarketLens行情CSV；不自动复权')
    p.add_argument('command',choices=['collect','parse','replay','export']);p.add_argument('--input',type=Path,required=True);p.add_argument('--raw',type=Path);p.add_argument('--declaration',type=Path);p.add_argument('--retrieved-at');p.add_argument('--out-dir',type=Path,required=True);p.add_argument('--online',action='store_true');a=p.parse_args(argv)
    try:
        if a.out_dir.exists():raise ValueError('输出已存在，未请求来源')
        obj=loads(read(a.input).decode('utf-8-sig'));raw=None;decl=None
        if a.command=='export':
            if not a.raw or not a.declaration:raise ValueError('导出需冻结原始响应和因子声明')
            raw=read(a.raw);snapshot=replay(obj,raw);spec=snapshot['request'];decl=loads(read(a.declaration).decode('utf-8-sig'))
        elif a.command=='replay':
            if not a.raw:raise ValueError('重放需--raw')
            raw=read(a.raw);snapshot=replay(obj,raw);spec=snapshot['request']
        else:
            spec=request(obj)
            if a.command=='collect':
                if not a.online:raise ValueError('取数需要明确--online')
                attempted=datetime.now(timezone.utc).isoformat();received=None
                try:
                    raw=download(url_for(spec),allowed_hosts={'push2his.eastmoney.com'},limit=16*1024*1024,timeout=30)
                    received=datetime.now(timezone.utc).isoformat();snapshot=parse(raw,spec,received)
                except Exception as exc:
                    snapshot={'schemaVersion':SCHEMA,'request':spec,'status':'failed','attemptedAt':attempted,'responseReceivedAt':received,'retrievedAt':received,'data':[],'error':type(exc).__name__+': '+str(exc),'rawSha256':digest(raw) if raw is not None else None}
            else:
                if not a.raw or not a.retrieved_at:raise ValueError('离线解析需--raw和真实取得时点--retrieved-at')
                raw=read(a.raw);snapshot=parse(raw,spec,a.retrieved_at)
        publish(a.out_dir,spec,snapshot,raw,decl)
        print('已保存行情资料：'+str(a.out_dir)+'；状态 '+snapshot['status']+'。取得时间不代表历史首次可得时间。')
        return 2 if snapshot['status']=='failed' else 0
    except (ValueError,OSError,KeyError,TypeError,ArithmeticError) as exc:
        print('未完成：'+str(exc),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
