# SPDX-License-Identifier: MIT
"""Explicit source capability declarations, separate from current request success."""
from datetime import date,datetime
from .review_io import cli


def review(spec):
    if not isinstance(spec,dict):raise ValueError('来源能力输入须为对象')
    if spec.get('inputSchema')!='source-capabilities/1':raise ValueError('需source-capabilities/1输入')
    cutoff=date.fromisoformat(spec['asOf'])
    if cutoff.isoformat()!=spec['asOf']:raise ValueError('截止日期需YYYY-MM-DD')
    sources=spec['sources']
    if not isinstance(sources,list) or len(sources)>200:raise ValueError('最多200项来源')
    ids=set();rows=[]
    for row in sources:
        identity=row['id']
        if not isinstance(identity,str) or not identity.strip() or identity in ids:raise ValueError('来源ID无效或重复')
        ids.add(identity)
        for field in ['provider','entry','scope','frequency','unitPolicy','versionPolicy','rightsNote']:
            if not isinstance(row.get(field),str) or not row[field].strip():raise ValueError('缺少能力说明：'+field)
        if row.get('access') not in {'public','user-authorized','unknown'}:raise ValueError('访问范围须声明')
        if row.get('implementation') not in {'implemented','partial','catalog-only'}:raise ValueError('实现状态无效')
        if row.get('attemptStatus') not in {'available','empty','failed','unauthorized','missing'}:raise ValueError('取得状态无效')
        attempt=row.get('lastAttemptAt');freshness='unknown';included=True
        if attempt is not None:
            dt=datetime.fromisoformat(attempt.replace('Z','+00:00'))
            if dt.tzinfo is None:raise ValueError('取得时间须时区')
            if dt.date()>cutoff:included=False
        data_date=row.get('latestObservationDate');max_age=row.get('maxAgeDays')
        if max_age is not None and (type(max_age) is not int or max_age<0):raise ValueError('新鲜度门槛须非负整数或未知')
        if data_date is not None:
            observed=date.fromisoformat(data_date)
            if observed.isoformat()!=data_date:raise ValueError('观察日期无效')
            if observed>cutoff:included=False
            elif max_age is not None:freshness='stale' if (cutoff-observed).days>max_age else 'within-declared-window'
        status=row['attemptStatus'] if included else 'after-cutoff'
        if status=='available' and (row['implementation']=='catalog-only' or not row.get('evidenceLocator') or attempt is None):raise ValueError('成功状态需实现、取得时间及核验记录定位')
        rows.append(dict(row,reviewStatus=status,freshness=freshness,sourceVerified=False,historicalAvailability=row.get('historicalAvailability','unknown')))
    switches=[]
    for switch in spec.get('switches',[]):
        if switch.get('from') not in ids or switch.get('to') not in ids or switch['from']==switch['to']:raise ValueError('切换来源无效')
        changes=switch.get('methodologyChanges')
        if not isinstance(changes,list) or not changes or any(not isinstance(x,str) or not x.strip() for x in changes):raise ValueError('跨源切换须逐项说明口径差异')
        switches.append(dict(switch,equivalenceCertified=False,automaticFallback=False))
    implementation={'implemented':'入口已实现','partial':'部分实现','catalog-only':'仅登记目录'}
    statuses={'available':'已取得限定资料','empty':'返回空资料','failed':'取得失败','unauthorized':'缺少授权','missing':'本轮未提供取得状态','after-cutoff':'截止后资料'}
    freshness={'unknown':'窗口或观察日期未知','stale':'超过声明窗口','within-declared-window':'在声明窗口内'}
    return {'methodVersion':'source-capabilities/1','conclusion':f"登记{len(rows)}项来源；能力登记不代表本次已经取数，跨源切换不自动视为口径等价。",'sources':rows,'switches':switches,'humanRows':[[r['provider'],implementation[r['implementation']]+'；'+statuses[r['reviewStatus']]+'；时效：'+freshness[r['freshness']]] for r in rows],'limitations':['来源能力与取得成功分别登记；未知时间不补为当前','公开访问不授予再分发权利，保留逐源用途范围说明','日期窗口由使用场景声明，不统一设置新鲜度标准','不同复权、单位、统计范围和修订口径的来源不静默拼接']}

def main(argv=None):
    import argparse,sys
    from pathlib import Path
    from .review_io import read,publish
    p=argparse.ArgumentParser(description='数据来源能力与取得状态')
    p.add_argument('command',choices=['review']);p.add_argument('--input',type=Path,required=True);p.add_argument('--out-dir',type=Path,required=True);a=p.parse_args(argv)
    try:
        if a.out_dir.exists():raise ValueError('输出已存在，历史结果不覆盖')
        spec=read(a.input);publish(spec,review(spec),a.out_dir,'数据来源能力与取得状态');print('已保存来源能力核对：'+str(a.out_dir/'report.html'));return 0
    except (ValueError,OSError,KeyError,TypeError) as exc:print('未完成：'+str(exc),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
