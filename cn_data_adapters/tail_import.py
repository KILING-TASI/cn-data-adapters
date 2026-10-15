# SPDX-License-Identifier: MIT
"""Explicit offline bridge from tail-risk snapshots to observation-table v1."""
import argparse,hashlib,json,sys
from pathlib import Path
from .market import read
from .contracts.observations import validate,SCHEMA

def convert(raw):
 d=json.loads(raw.decode('utf-8-sig'));schema=d.get('schemaVersion')
 if schema not in ('assets-v1','context-v1'):raise ValueError('requires assets-v1 or context-v1')
 rows=[];gaps=[];retrieved=d.get('retrievedAt')
 for i,r in enumerate(d.get('records',[])):
  if r.get('value') is None or (schema=='assets-v1' and r.get('status')!='available'):gaps.append({'id':r.get('id',i),'reason':'value absent or not freshly obtained'});continue
  if schema=='context-v1':
   year=r['period'];start,end=year+'-01-01',year+'-12-31';entity=r['entityId'];metric=r['metric'];currency=r.get('currency');basis=r['basis'];unit=r['unit'];v=r.get('sourceDecimalText',str(r['value']));version=r.get('version') or 'retrieved-latest-version'
  else:
   start=end=r['date'];entity=r['id'];metric={'quote':'market_price','nav':'published_unit_nav','gold':'contract_close','rate':'reference_rate','yield':'yield_curve_point'}.get(r.get('kind'),'fx_reference');currency=r.get('currency');basis=r.get('historyBasis') or r.get('basis');unit=r.get('unit');v=str(r['value']);version=r.get('historyBasis') or 'retrieved-latest-version'
  if not basis or not unit:raise ValueError('explicit basis and unit required')
  rows.append(dict(id=f'{entity}:{metric}:{end}:{i}',entity=entity,metric=metric,value=v,unit=unit,currency=currency,basis=basis,periodStart=start,periodEnd=end,observedAt=None,publishedAt=None,availableAt=None,retrievedAt=retrieved,sourceUrl=r['sourceUrl'],sourceVersion=version,locator='records['+str(i)+']',verification='declared-not-original-verified'))
 spec=dict(schemaVersion=SCHEMA,asOf=retrieved,rows=rows,rawSourceSha256=hashlib.sha256(raw).hexdigest(),origin='provided-tabular-bytes')
 checked=validate(spec)
 return spec,{'schemaVersion':'tail-risk-observation-bridge/1','inputSchema':schema,'inputResearchCutoff':d.get('targetSession',d.get('asOf')),'validationAsOf':retrieved,'validation':checked,'gaps':gaps,'limits':'validation at actual retrieval time, not historical research cutoff; publication/first availability unknown; no original source authentication or automatic unit conversion'}

def main(argv=None):
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--out-dir',type=Path,required=True);a=p.parse_args(argv)
 try:
  if a.out_dir.exists():raise ValueError('use a new directory')
  raw=read(a.input);spec,receipt=convert(raw);a.out_dir.mkdir(parents=True)
  (a.out_dir/'source-input.json').write_bytes(raw)
  for name,value in [('observations.json',spec),('receipt.json',receipt)]:
   with (a.out_dir/name).open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,allow_nan=False,indent=2)
  print('已导入'+str(len(spec['rows']))+'条声明观察；历史首次可得性仍未知。');return 0
 except (ValueError,KeyError,TypeError,OSError) as e:print('未导入：'+str(e),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
