# SPDX-License-Identifier: MIT
"""Read-only index of an explicitly selected local research-data directory."""
import argparse,json,sys
from pathlib import Path
from ._contract import loads

def main(argv=None):
    p=argparse.ArgumentParser(description='只整理指定资料目录，不扫描其他项目，不清理或修改原件')
    p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args(argv)
    try:
        if a.out.exists():raise ValueError('索引输出已存在')
        if a.root.is_symlink() or not a.root.is_dir():raise ValueError('需要明确的普通目录')
        root=a.root.resolve();rows=[]
        for path in root.rglob('snapshot.json'):
            if len(rows)>=10000:raise ValueError('快照数超过10000，请分目录整理')
            if path.is_symlink() or not path.resolve().is_relative_to(root) or path.stat().st_size>16*1024*1024:raise ValueError('快照链接、越界或过大')
            value=loads(path.read_text(encoding='utf-8-sig'))
            if not isinstance(value,dict):raise ValueError('快照不是对象')
            data=value.get('data');counts=value.get('recordCount')
            if counts is None and isinstance(data,list):counts=len(data)
            rows.append(dict(path=str(path),schemaVersion=value.get('schemaVersion'),status=value.get('status','not-declared'),request=value.get('request'),records=counts,retrievedAt=value.get('retrievedAt'),replayedAt=value.get('replayedAt'),error=value.get('error'),limitations=value.get('limitations',[])))
        a.out.parent.mkdir(parents=True,exist_ok=True)
        with a.out.open('x',encoding='utf-8') as f:json.dump({'root':str(root),'snapshots':rows,'scope':'local index only; source identity, content and completeness are not certified'},f,ensure_ascii=False,indent=2)
        print('已整理 '+str(len(rows))+' 份快照：'+str(a.out));return 0
    except (ValueError,OSError,TypeError) as exc:print('未完成：'+str(exc),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
