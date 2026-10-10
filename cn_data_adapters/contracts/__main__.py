import argparse,json,sys
from pathlib import Path
from .collection import loads,validate,record,canonical

def main(argv=None):
    for stream in (sys.stdout,sys.stderr):
        if hasattr(stream,'reconfigure'):stream.reconfigure(encoding='utf-8')
    p=argparse.ArgumentParser(description='研究采集格式校验；不认证原发布者或实际收益')
    p.add_argument('command',choices=['validate','validate-table','demo']);p.add_argument('--input',type=Path);p.add_argument('--out-dir',type=Path)
    args=p.parse_args(argv)
    try:
        if args.command in ('validate','validate-table'):
            if args.input is None or args.input.stat().st_size>16*1024*1024:raise ValueError('需要小于16MiB的--input')
            value=loads(args.input.read_text(encoding='utf-8-sig'))
            if args.command=='validate-table':
                from .observations import validate as validate_table
                checked=validate_table(value)
            else:checked=validate(value)
            print(json.dumps(checked,ensure_ascii=False));return 0
        if args.out_dir is None or args.out_dir.exists():raise ValueError('demo需要--out-dir指定新目录')
        req=dict(id='teaching',source='eastmoney-fund-nav',fundCode='900001',start='2026-01-02',end='2026-01-03',asOf='2026-01-03',currency='CNY',frequency='daily',fields=['unit_nav','distribution_text'])
        value=record(req,[{'date':'2026-01-02','nav':'1.0000'},{'date':'2026-01-03','nav':'1.0500'}],name='原创教学基金',origin='teaching')
        args.out_dir.mkdir(parents=True);(args.out_dir/'snapshot.json').write_bytes(canonical(value))
        (args.out_dir/'打开这里.html').write_text('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>格式校验教学</title><style>body{max-width:1000px;margin:32px auto;padding:0 20px;font:17px/1.7 system-ui}</style><h1>这份资料的格式能通过校验吗？</h1><p>已生成符合当前净值契约的原创教学快照，包含两个虚构日期的净值记录。这只展示格式，不是实际基金或投资收益。</p><h2>结果怎么看</h2><p>snapshot.json 保存机器可读的请求、来源、未知状态和记录。格式通过不代表数值或原发布者已经核实。</p><h2>下一步</h2><p>准备自己的标准快照后运行 cn-data-adapters validate --input 你的快照.json；通用观察表使用 validate-table。需要联网采集时选择数据仓的相应采集入口；格式校验本身保持离线。</p>',encoding='utf-8')
        print('教学结果：'+str(args.out_dir/'打开这里.html')+'；机器快照 snapshot.json。不是实际基金或收益。');return 0
    except (ValueError,OSError,TypeError,KeyError) as e:
        print('校验未通过：'+str(e)+'。下一步：核对版本、完整输入及新输出目录。');return 2

if __name__=='__main__':raise SystemExit(main())
