# SPDX-License-Identifier: MIT
"""Explicit provincial NBS observations; no cookie or verification bypass."""
import argparse,calendar,datetime as dt,hashlib,json,re,sys
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlencode
from ._contract import loads,unique,reject_constant
from .market import read
from .public_download import download

def request(spec):
    if set(spec)!={'database','indicator','period'} or spec['database'] not in ('fsnd','fsjd'):raise ValueError('明确分省年度fsnd或季度fsjd、指标和期间')
    if not isinstance(spec['indicator'],str) or not re.fullmatch('[A-Z][0-9]{1,12}',spec['indicator']):raise ValueError('指标代码格式不符；按官方目录确认')
    period=spec['period']
    if not isinstance(period,str) or not re.fullmatch('[0-9]{4}' if spec['database']=='fsnd' else '[0-9]{4}[A-D]',period):raise ValueError('年度用YYYY，季度用YYYYA至YYYYD')
    year=int(period[:4]);month=12 if spec['database']=='fsnd' else (ord(period[-1])-ord('A')+1)*3
    end=dt.date(year,month,calendar.monthrange(year,month)[1])
    if year<1949 or end>dt.date.today():raise ValueError('不能将未结束统计期作为已实现数据采集')
    return dict(spec)

def parse(raw,spec):
    obj=json.loads(raw.decode('utf-8-sig'),object_pairs_hook=unique,parse_float=str,parse_constant=reject_constant)
    if obj.get('returncode')!=200 or not isinstance(obj.get('returndata'),dict):raise ValueError('官方接口未返回有效数据，可能为验证或错误响应')
    data=obj['returndata'];dims={}
    for wd in data['wds']:
        name=wd['wdcode']
        if name in dims:raise ValueError('维度元数据重复')
        nodes={}
        for node in wd['nodes']:
            if node['code'] in nodes:raise ValueError('维度节点重复')
            nodes[node['code']]=node
        dims[name]=nodes
    rows=[];seen=set()
    for node in data['datanodes']:
        codes={}
        for wd in node['wds']:
            if wd['wdcode'] in codes:raise ValueError('记录维度重复')
            codes[wd['wdcode']]=wd['valuecode']
        if set(codes)!={'zb','reg','sj'} or codes['zb']!=spec['indicator'] or codes['sj']!=spec['period']:raise ValueError('记录指标/期间与请求不符')
        key=tuple(codes[x] for x in ('zb','reg','sj'))
        if key in seen:raise ValueError('地区观察重复')
        seen.add(key)
        if any(codes[k] not in dims.get(k,{}) for k in codes):raise ValueError('记录维度未在元数据登记')
        number=node['data'];known=number.get('hasdata')
        if type(known) is not bool:raise ValueError('可得状态不明确')
        value=None
        if known:
            if isinstance(number.get('data'),bool) or number.get('data') is None:raise ValueError('有效数值声明不符')
            decimal=Decimal(str(number['data']))
            if not decimal.is_finite():raise ValueError('数值非有限')
            value=str(decimal)
        indicator=dims['zb'][codes['zb']];region=dims['reg'][codes['reg']]
        rows.append(dict(indicatorId=codes['zb'],indicatorName=indicator.get('cname') or indicator.get('name'),regionCode=codes['reg'],regionName=region.get('cname') or region.get('name'),period=codes['sj'],value=value,unit=indicator.get('unit') or None,unknownReason=None if known else '官方hasdata=false',indicatorNote=indicator.get('exp') or indicator.get('notes'),administrativeVersion=None))
    if not rows:raise ValueError('无观察记录，不等同于各地数值为零')
    return rows

def main(argv=None):
    for stream in (sys.stdout,sys.stderr):
        if hasattr(stream,'reconfigure'):stream.reconfigure(encoding='utf-8')
    p=argparse.ArgumentParser(description='国家数据分省年度/季度，明确指标和统计期；不自动取得市县全集')
    p.add_argument('command',choices=['collect','replay']);p.add_argument('--input',type=Path,required=True);p.add_argument('--out-dir',type=Path,required=True);p.add_argument('--online',action='store_true');a=p.parse_args(argv)
    try:
        if a.out_dir.exists():raise ValueError('输出目录已存在')
        inp=loads(read(a.input).decode('utf-8-sig'));old=inp if a.command=='replay' else None
        if old and (old.get('schemaVersion')!='cn-nbs-provincial-archive/1.0' or old.get('status')!='success'):raise ValueError('回放需成功冻结快照')
        spec=request(old['request'] if old else inp)
        if not old and not a.online:raise ValueError('取数须明确--online')
        a.out_dir.mkdir(parents=True)
        result=dict(schemaVersion='cn-nbs-provincial-archive/1.0',request=spec,status='failed',attemptedAt=dt.datetime.now(dt.timezone.utc).isoformat(),retrievedAt=old['retrievedAt'] if old else None,replayedAt=dt.datetime.now(dt.timezone.utc).isoformat() if old else None,publishedAt=None,data=[],limitations=['仅明确分省指标/期间，不宣称省市区县全覆盖','行政区划版本及历史修订另核，区域总量不隐式相加','单位缺失保留未知；统计期不是公开日或历史首次可得日'])
        try:
            if old:
                raw=read(a.input.parent/'response.json')
                if hashlib.sha256(raw).hexdigest()!=old['rawSha256']:raise ValueError('冻结摘要不符')
                url=old['url']
            else:
                url='https://data.stats.gov.cn/easyquery.htm?'+urlencode(dict(m='QueryData',dbcode=spec['database'],rowcode='reg',colcode='sj',wds=json.dumps([dict(wdcode='zb',valuecode=spec['indicator'])]),dfwds=json.dumps([dict(wdcode='sj',valuecode=spec['period'])])))
                raw=download(url,allowed_hosts={'data.stats.gov.cn'},limit=16*1024*1024,timeout=30,return_metadata=True)['raw']
            (a.out_dir/'response.json').write_bytes(raw);result.update(url=url,rawSha256=hashlib.sha256(raw).hexdigest(),byteCount=len(raw))
            rows=parse(raw,spec);result.update(status='success',data=rows,retrievedAt=result['retrievedAt'] or dt.datetime.now(dt.timezone.utc).isoformat())
            for row in rows:row['availableAt']=result['retrievedAt']
        except Exception as exc:result['error']=type(exc).__name__+': '+str(exc)
        (a.out_dir/'snapshot.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        from html import escape
        state='资料取得成功，原文与区划版本另核' if result['status']=='success' else '未完成；没有用其他来源或缓存冒充成功'
        (a.out_dir/'打开这里.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>分省资料</title><style>body{max-width:1000px;margin:32px auto;padding:0 20px;font:17px/1.7 system-ui}</style><h1>分省资料取得了吗？</h1><p>'+state+'；观察数：'+str(len(result['data']))+'。</p><p>'+escape(result.get('error','核对单位、指标说明、行政区划和修订版本，未知保持未知。'))+'</p><h2>下一步</h2><p>确认官方公开入口可用后再另存新请求，或取得资料后使用本地表格映射。空结果不代表各省数值为零；不绕过访问验证。</p></html>',encoding='utf-8')
        print('分省状态：'+result['status']+'；'+str(a.out_dir/'打开这里.html'));return 0 if result['status']=='success' else 2
    except (ValueError,OSError,KeyError,TypeError) as exc:print('未完成：'+str(exc),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
