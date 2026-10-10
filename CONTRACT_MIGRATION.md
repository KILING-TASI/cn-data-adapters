# 契约校验并入数据仓

校验模块位于 `cn_data_adapters.contracts`，仍只读取本地标准JSON，不联网、不依赖其他作者仓库。净值和观察表格式未改版，原始冻结结果不重写。

```text
cn-data-adapters validate --input 你的净值快照.json
cn-data-adapters validate-table --input 你的观察表.json
cn-data-adapters contracts demo --out-dir reports/contracts-demo
```

数据仓也提供旧命令 `cn-research-contracts`，旧参数保持。旧独立Python包和历史发布继续保留；新代码使用 `cn_data_adapters.contracts`。不在新发行包中覆盖 `cn_research_contracts` 的Python命名空间，避免两个发行包争用同一文件。

迁移已有环境时先保留个人资料，再在环境中卸载旧 `cn-research-contracts` 发行包，安装新版 `cn-data-adapters`；同时装两个发行包时，同名命令可能被安装顺序覆盖。最稳妥是新建独立环境。卸载代码不删除报告或冻结原件。

工作台和组合仓随包携带的历史固定格式实现暂时保留。它们是离线独立使用的兼容资源，不自动跟随更新；后续同步须核对方法摘要和正反例，不能按软件版本号直接替换。
