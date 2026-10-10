# SPDX-License-Identifier: MIT
"""Explicit official-page capture, not an institutional data API or semantic parser."""
import argparse,json,hashlib,sys
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlsplit
from .public_download import download
from .market import publish
from ._contract import loads

HOSTS={
 'chinaclear':{'www.chinaclear.cn','m.chinaclear.cn'},
 'chinabond':{'www.chinabond.com.cn','yield.chinabond.com.cn','indices.chinabond.com.cn','valuation.chinabond.com.cn'},
 'shclearing':{'www.shclearing.com','www.shclearing.com.cn'},
 'cnindex':{'www.cnindex.com.cn'},'safe':{'www.safe.gov.cn'},
 'customs':{'www.customs.gov.cn'},'neeq':{'www.neeq.com.cn'},
 'hkex':{'www.hkex.com.hk','www.hkexnews.hk'},
 'sse':{'www.sse.com.cn'},'szse':{'www.szse.cn'},
 'cninfo':{'www.cninfo.com.cn','static.cninfo.com.cn'}}

def main(argv=None):
 for stream in (sys.stdout,sys.stderr):
  if hasattr(stream,'reconfigure'):stream.reconfigure(encoding='utf-8')
 p=argparse.ArgumentParser(description='明确官方URL的公开原始响应留档；不自动取得全量证券数据或解释PDF')
 p.add_argument('command',choices=['capture','replay']);p.add_argument('--input',type=Path,required=True);p.add_argument('--raw',type=Path);p.add_argument('--online',action='store_true');p.add_argument('--out-dir',type=Path,required=True);a=p.parse_args(argv)
 try:
  if a.out_dir.exists():raise ValueError('输出目录已存在，未联网')
  if a.input.stat().st_size>16*1024*1024:raise ValueError('输入过大')
  spec=loads(a.input.read_text(encoding='utf-8-sig'));raw=None
  if a.command=='capture':
   if set(spec)!={'sourceId','url','purpose'} or spec['sourceId'] not in HOSTS or not isinstance(spec['purpose'],str) or not spec['purpose'].strip():raise ValueError('需来源ID、公开URL及研究用途')
   if urlsplit(spec['url']).hostname not in HOSTS[spec['sourceId']]:raise ValueError('URL不属于所声明官方来源')
   if not a.online:raise ValueError('取源需明确--online；不使用账户、Cookie或绕过验证')
   now=datetime.now(timezone.utc).isoformat()
   result={'schemaVersion':'cn-public-response-archive/1.0','request':spec,'status':'failed','attemptedAt':now,'retrievedAt':None,'replayedAt':None,'publishedAt':None,'availableAt':None,'data':[],'limitations':['仅原始响应下载，不是结构化数据接口接通','公开可访问不等于再分发授权；不下载认证或付费资料','HTML可能为登录/验证/错误页面，未自动认证正文有效性']}
   try:
    response=download(spec['url'],limit=16*1024*1024,allowed_hosts=HOSTS[spec['sourceId']],return_metadata=True,timeout=30)
    raw=response['raw'];result.update(status='response-received',retrievedAt=datetime.now(timezone.utc).isoformat(),resolvedUrl=response['resolvedUrl'],rawSha256=hashlib.sha256(raw).hexdigest(),byteCount=len(raw))
   except Exception as exc:result['error']=type(exc).__name__+': '+str(exc)
  else:
   if not a.raw or spec.get('schemaVersion')!='cn-public-response-archive/1.0' or spec.get('status')!='response-received':raise ValueError('需已取得快照和冻结原始响应')
   if a.raw.stat().st_size>16*1024*1024:raise ValueError('原始响应过大')
   raw=a.raw.read_bytes()
   if hashlib.sha256(raw).hexdigest()!=spec.get('rawSha256') or len(raw)!=spec.get('byteCount'):raise ValueError('冻结响应摘要不一致')
   result=dict(spec,replayedAt=datetime.now(timezone.utc).isoformat());spec=spec['request']
  publish(a.out_dir,spec,result,raw);print('已保存来源响应记录：'+str(a.out_dir)+'；状态 '+result['status']+'。结构化数据接通仍需单独核验。')
  return 2 if result['status']=='failed' else 0
 except (ValueError,OSError,KeyError,TypeError) as exc:print('未完成：'+str(exc),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
