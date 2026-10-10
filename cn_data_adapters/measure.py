# SPDX-License-Identifier: MIT
"""Measure one explicitly requested adapter run, including failures, without token guesses."""
import argparse,importlib,json,platform,sys,time,tracemalloc,threading
from pathlib import Path

def main(argv=None):
    p=argparse.ArgumentParser(description='记录适配器一次运行的耗时、逻辑下载尝试、完成响应字节与Python峰值内存')
    p.add_argument('--adapter',choices=['yearbook','worldbank','housing','nbs','source_archive','market'],required=True);p.add_argument('--record',type=Path,required=True);p.add_argument('args',nargs=argparse.REMAINDER);a=p.parse_args(argv)
    if a.record.exists():p.error('测量记录已存在；使用新文件')
    forwarded=a.args[1:] if a.args[:1]==['--'] else a.args
    module=importlib.import_module('.'+a.adapter,__package__);original=module.download;lock=threading.Lock();stats={'logicalDownloadAttempts':0,'completedResponseBytes':0,'failedDownloadAttempts':0}
    def measured(*args,**kwargs):
        with lock:stats['logicalDownloadAttempts']+=1
        try:
            result=original(*args,**kwargs);raw=result['raw'] if isinstance(result,dict) else result
            with lock:stats['completedResponseBytes']+=len(raw)
            return result
        except Exception:
            with lock:stats['failedDownloadAttempts']+=1
            raise
    module.download=measured;tracemalloc.start();start=time.perf_counter();code=2;error=None
    try:code=module.main(forwarded)
    except Exception as exc:error=type(exc).__name__+': '+str(exc)
    finally:
        elapsed=time.perf_counter()-start;_,peak=tracemalloc.get_traced_memory();tracemalloc.stop();module.download=original
        record=dict(schemaVersion='adapter-cost-record/1',adapter=a.adapter,arguments=forwarded,exitCode=code,error=error,wallSeconds=elapsed,pythonTrackedPeakBytes=peak,python=sys.version.split()[0],platform=platform.platform(),**stats,scope='logical download calls, not redirect-level HTTP requests; completed bytes exclude failed partial reads; Python tracked peak is not full process memory',tokenUsage=None)
        a.record.parent.mkdir(parents=True,exist_ok=True)
        with a.record.open('x',encoding='utf-8') as f:json.dump(record,f,ensure_ascii=False,indent=2)
    print('运行测量：'+str(a.record));return code

if __name__=='__main__':raise SystemExit(main())
