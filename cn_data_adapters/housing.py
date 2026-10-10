# SPDX-License-Identifier: MIT
"""Paginated city house-price archives; original publisher and channel stay separate."""
import argparse,datetime as dt,hashlib,json,re,sys
from pathlib import Path
from urllib.parse import urlencode
from ._contract import loads
from .market import read
from .public_download import download
from .housing_model import build_house_price_series

def request(spec):
    if set(spec)!={'start','end'}:raise ValueError('房价请求须为start/end月份')
    for value in spec.values():
        if not isinstance(value,str) or not re.fullmatch('[0-9]{4}-[0-9]{2}',value):raise ValueError('月份须为YYYY-MM')
        dt.date.fromisoformat(value+'-01')
    start,end=spec['start'],spec['end'];a,b=(int(start[:4])*12+int(start[5:])),(int(end[:4])*12+int(end[5:]))
    if a>b or b-a>=120 or end>dt.datetime.now(dt.timezone.utc).strftime('%Y-%m'):raise ValueError('区间须为不超过120个月，不能含未来月份')
    return dict(spec)

def main(argv=None):
    for stream in (sys.stdout,sys.stderr):
        if hasattr(stream,'reconfigure'):stream.reconfigure(encoding='utf-8')
    p=argparse.ArgumentParser(description='城市房价同比/环比指数分页留档，不生成官方全国指数')
    p.add_argument('command',choices=['collect','replay']);p.add_argument('--input',type=Path,required=True);p.add_argument('--out-dir',type=Path,required=True);p.add_argument('--online',action='store_true');a=p.parse_args(argv)
    try:
        if a.out_dir.exists():raise ValueError('输出目录已存在')
        inp=loads(read(a.input).decode('utf-8-sig'));old=inp if a.command=='replay' else None
        if old and (old.get('schemaVersion')!='cn-city-house-price-archive/1.0' or old.get('status')!='success'):raise ValueError('回放需要成功快照')
        spec=request(old['request'] if old else inp)
        if not old and not a.online:raise ValueError('联网须明确--online')
        a.out_dir.mkdir(parents=True)
        result=dict(schemaVersion='cn-city-house-price-archive/1.0',status='failed',request=spec,channel='eastmoney',originalPublisher='国家统计局（未逐条原文核验）',attemptedAt=dt.datetime.now(dt.timezone.utc).isoformat(),retrievedAt=old['retrievedAt'] if old else None,replayedAt=dt.datetime.now(dt.timezone.utc).isoformat() if old else None,publishedAt=None,pages=[],data=None)
        try:
            rows=[];pages=None;total=None;total_bytes=0
            for page in range(1,21):
                if old:
                    entry=old['pages'][page-1]
                    if entry['file']!=f'page-{page}.json':raise ValueError('冻结页名不符')
                    raw=read(a.input.parent/entry['file']);url=entry['url']
                    if hashlib.sha256(raw).hexdigest()!=entry['sha256']:raise ValueError('冻结原件摘要不符')
                else:
                    url='https://datacenter-web.eastmoney.com/api/data/v1/get?'+urlencode(dict(reportName='RPT_ECONOMY_HOUSE_PRICE',columns='ALL',pageSize=2000,pageNumber=page,sortColumns='REPORT_DATE',sortTypes='-1',filter="(REPORT_DATE>='"+spec['start']+"-01')(REPORT_DATE<='"+spec['end']+"-01')"))
                    raw=download(url,allowed_hosts={'datacenter-web.eastmoney.com'},limit=16*1024*1024,timeout=30,return_metadata=True)['raw']
                total_bytes+=len(raw)
                if total_bytes>64*1024*1024:raise ValueError('本批响应超过64MiB')
                name=f'page-{page}.json';(a.out_dir/name).write_bytes(raw)
                result['pages'].append(dict(file=name,url=url,sha256=hashlib.sha256(raw).hexdigest(),byteCount=len(raw)))
                payload=loads(raw.decode('utf-8-sig'));body=payload.get('result')
                if not payload.get('success') or not isinstance(body,dict) or not isinstance(body.get('data'),list):raise ValueError('渠道未返回有效报表')
                current_pages=int(body['pages']);current_total=int(body['count'])
                if not 1<=current_pages<=20 or not 1<=current_total<=40000:raise ValueError('页数/记录数无效或超限')
                if pages is not None and (pages!=current_pages or total!=current_total):raise ValueError('分页数量变化')
                pages,total=current_pages,current_total;rows.extend(body['data'])
                if page==pages:break
            if len(rows)!=total or old and len(old['pages'])!=pages:raise ValueError('分页记录不完整')
            if any(not spec['start']<=str(row.get('REPORT_DATE',''))[:7]<=spec['end'] for row in rows):raise ValueError('记录不在请求区间')
            data=build_house_price_series(rows,120)
            result.update(status='success',data=data,retrievedAt=result['retrievedAt'] or dt.datetime.now(dt.timezone.utc).isoformat())
            result['availableAt']=result['retrievedAt'];result['recordCount']=len(rows)
        except Exception as exc:result['error']=type(exc).__name__+': '+str(exc)
        (a.out_dir/'snapshot.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        from html import escape
        summary='资料取得成功，原文未逐项核验' if result['status']=='success' else '未完成'
        table=''
        if result['data']:
            data=result['data'];last=data['dates'][-1];body=''
            for city,series in data['citySeries'].items():
                cells=[series['series'][name][-1] for name in ('new_yoy','new_mom','second_yoy','second_mom')]
                body+='<tr><td>'+escape(city)+'</td>'+''.join('<td>'+('未知' if value is None else str(value))+'</td>' for value in cells)+'</tr>'
            table='<p>已取得'+str(result['recordCount'])+'条城市月份记录，涉及'+str(len(data['citySeries']))+'个城市；区间'+escape(data['dates'][0])+'至'+escape(last)+'。</p><h2>'+escape(last)+'城市明细</h2><p>同比指数100表示与上年同月持平，环比指数100表示与上月持平；不是涨幅百分数。缺项显示未知。</p><div class="table"><table><tr><th>城市</th><th>新房同比指数</th><th>新房环比指数</th><th>二手同比指数</th><th>二手环比指数</th></tr>'+body+'</table></div>'
        (a.out_dir/'打开这里.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>城市房价资料</title><style>body{max-width:1000px;margin:32px auto;padding:0 20px;font:17px/1.7 system-ui}.table{overflow-x:auto}table{border-collapse:collapse;width:100%;min-width:600px}td,th{padding:8px;border-bottom:1px solid #ddd}</style><h1>这批城市房价资料包含什么？</h1><p>状态：'+summary+'。</p>'+table+'<h2>范围与下一步</h2><p>'+escape(result.get('error','逐城核对原文、名单与基期版本。样本等权均值不是官方全国指数，数量70不证明名单已核验。完整月份和来源摘要见snapshot.json。'))+'</p></html>',encoding='utf-8')
        print('城市房价状态：'+result['status']+'；'+str(a.out_dir/'打开这里.html'));return 0 if result['status']=='success' else 2
    except (ValueError,OSError,KeyError,TypeError) as exc:print('未完成：'+str(exc),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
