# SPDX-License-Identifier: MIT
"""Archive coverage and reviewed numeric cells are separate, bounded measures."""
import argparse, hashlib, json, sys
from collections import Counter
from pathlib import Path
from ._contract import loads
from .review_io import publish


def regular(root, name):
    if not isinstance(name, str) or not name: raise ValueError('原件路径缺失')
    path=root/name
    if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError('原件缺失、链接或越出指定目录')
    if path.stat().st_size>16*1024*1024: raise ValueError('原件超过16MiB')
    return path


def review(snapshot, root, numeric_reviews=None):
    if not isinstance(snapshot,dict):raise ValueError('年鉴快照须为对象')
    if snapshot.get('schemaVersion')!='cn-yearbook-archive/1.0': raise ValueError('需要年鉴留档快照')
    rows=snapshot['tables']
    if not isinstance(rows,list) or not 1<=len(rows)<=2000: raise ValueError('目录需1至2000张表')
    ids=[r['id'] for r in rows]
    if len(set(ids))!=len(ids): raise ValueError('目录表ID重复')
    numeric_reviews=numeric_reviews or []
    if len(numeric_reviews)>2000: raise ValueError('核验记录超过2000条')
    reviewed={};result=[]
    for record in numeric_reviews:
        key=record['tableId']
        if key not in ids or key in reviewed: raise ValueError('核验表未知或重复')
        if record.get('method') not in {'visual-transcription','ocr-reviewed'}: raise ValueError('核验方法须明确；OCR草稿不能当已核数值')
        if not isinstance(record.get('scope'),str) or not record['scope'].strip(): raise ValueError('须说明核验行列范围')
        count=record.get('verifiedCells')
        if type(count) is not int or count<1: raise ValueError('核验单元格数须为正整数')
        for field in ['unit','observationPeriod','reviewer','reviewedAt','sourceSha256']:
            if not isinstance(record.get(field),str) or not record[field].strip():raise ValueError('核验元数据缺失：'+field)
        from datetime import datetime
        parsed=datetime.fromisoformat(record['reviewedAt'].replace('Z','+00:00'))
        if parsed.tzinfo is None:raise ValueError('核验时间需时区')
        if record.get('fullTableVerified') is not False:raise ValueError('当前仅支持部分单元格核验，不认证全表')
        reviewed[key]=record
    for row in rows:
        status=row['status'];integrity='not-checked';numeric=reviewed.get(row['id'])
        if status in {'original-archived','response-received'}:
            path=regular(root,row['file']);raw=path.read_bytes()
            if hashlib.sha256(raw).hexdigest()!=row.get('sha256'):raise ValueError('原件摘要变化：'+row['id'])
            if row.get('format') in {'jpg','jpeg'} and not raw.startswith(b'\xff\xd8\xff'):raise ValueError('原表不是JPEG')
            if row.get('format')=='png' and not raw.startswith(b'\x89PNG\r\n\x1a\n'):raise ValueError('原表不是PNG')
            integrity='bytes-matched'
        if numeric and (integrity!='bytes-matched' or numeric['sourceSha256']!=row['sha256']):raise ValueError('数值核验未绑定当前原件：'+row['id'])
        result.append({'id':row['id'],'chapter':row['chapter'],'title':row['title'],'archiveStatus':status,'integrity':integrity,'numericReview':numeric,'numericStatus':'selected-cells-reviewed' if numeric else 'not-reviewed','historicalAvailability': 'unknown','nextAction':'继续核验未覆盖行列和注释' if numeric else ('核对表头、单位、期间与注释后转录或OCR复核' if integrity=='bytes-matched' else '补采原件；失败不计作成功')})
    statuses=Counter(r['archiveStatus'] for r in result)
    chapter_rows=[]
    for chapter in sorted({r['chapter'] for r in result},key=lambda x:(isinstance(x,str),str(x).zfill(2))):
        group=[r for r in result if r['chapter']==chapter]
        chapter_rows.append([str(chapter),f"目录{len(group)}；原件摘要匹配{sum(r['integrity']=='bytes-matched' for r in group)}；部分数值核验{sum(r['numericReview'] is not None for r in group)}"])
    cells=sum(r['verifiedCells'] for r in numeric_reviews)
    return {'methodVersion':'yearbook-coverage/1','edition':snapshot['edition'],'conclusion':f"目录{len(result)}张表，原件摘要匹配{sum(r['integrity']=='bytes-matched' for r in result)}张；仅{len(reviewed)}张有部分数值核验，共{cells}个单元格。未认证任何全表数值覆盖。",'archiveStatusCounts':dict(statuses),'verifiedSelectedCells':cells,'fullTablesVerified':0,'tables':result,'humanRows':chapter_rows,'limitations':['原件取得不等于数值核验；部分行列不升级为整表覆盖','核验人员与方法是明确记录，不是软件原件鉴真','年鉴版次不等于观察期；首次发布和历史可得时间未知，不支持无依据的时点回测','来源图片与原文权利另行处理，不随MIT代码许可再分发']}


def main(argv=None):
    p=argparse.ArgumentParser(description='核对年鉴原件与数值核验覆盖；不联网、不修改原件')
    p.add_argument('--snapshot',type=Path,required=True);p.add_argument('--reviews',type=Path);p.add_argument('--out-dir',type=Path,required=True);a=p.parse_args(argv)
    try:
        if a.out_dir.exists():raise ValueError('输出已存在，历史结果不覆盖')
        spec=loads(regular(a.snapshot.parent,a.snapshot.name).read_text('utf-8-sig'))
        records=loads(regular(a.reviews.parent,a.reviews.name).read_text('utf-8-sig')) if a.reviews else []
        result=review(spec,a.snapshot.parent,records)
        publish({'snapshotSha256':hashlib.sha256(a.snapshot.read_bytes()).hexdigest(),'reviews':records},result,a.out_dir,'年鉴覆盖与核验进度')
        print('已保存覆盖与缺口：'+str(a.out_dir/'report.html'));return 0
    except (ValueError,OSError,KeyError,TypeError) as exc:
        print('未完成：'+str(exc),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
