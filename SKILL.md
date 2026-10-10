---
name: cn-data-adapters
description: 采集限定基金净值、沪深股票或ETF日线，留存原始响应、标准化已有资料并冻结重放；也支持显式观察表映射和明确官方URL响应留档。
---

# 研究资料采集与重放

先确认标的、市场、数据类型、区间和已有资料。净值入口 `python -m cn_data_adapters`；日线入口 `python -m cn_data_adapters.market`；本地CSV映射入口 `python -m cn_data_adapters.tables`。使用各入口的 `--help`；输入与边界见 [DATA_ACQUISITION.md](DATA_ACQUISITION.md)。

明确取数才使用 `--online`。保留原始响应、请求及取得时点；刷新失败保存原因，不能补零或换数据商兜底。重放保留旧取得时点，另记重放时点，新结果不能覆盖历史目录。

MarketLens行情导出只接受明确核对的全区间因子为1及其依据；不自动复权，不猜历史首次可得时间。官方URL留档用 `python -m cn_data_adapters.source_archive`，仅表示收到响应，不代表取得有效正文、全量接口或授权。下载失败保留失败状态，不绕过登录或验证。
