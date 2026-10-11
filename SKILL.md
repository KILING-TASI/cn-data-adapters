---
name: cn-data-adapters
description: 采集限定基金净值、沪深股票或ETF日线，留存原始响应、标准化已有资料并冻结重放；也支持年鉴全章节原表留档、官方发布HTML表格提取、显式观察表映射和官方URL响应留档；也可离线校验已有标准净值和观察表。
metadata:
  version: 0.4.1
license: MIT
---

# 研究资料采集与重放

先确认标的、市场、数据类型、区间和已有资料。净值入口 `python -m cn_data_adapters`；日线入口 `python -m cn_data_adapters.market`；本地CSV映射入口 `python -m cn_data_adapters.tables`。使用各入口的 `--help`；输入与边界见 [DATA_ACQUISITION.md](DATA_ACQUISITION.md)。

明确取数才使用 `--online`。保留原始响应、请求及取得时点；刷新失败保存原因，不能补零或换数据商兜底。重放保留旧取得时点，另记重放时点，新结果不能覆盖历史目录。

MarketLens行情导出只接受明确核对的全区间因子为1及其依据；不自动复权，不猜历史首次可得时间。官方URL留档用 `python -m cn_data_adapters.source_archive`，仅表示收到响应，不代表取得有效正文、全量接口或授权。下载失败保留失败状态，不绕过登录或验证。

年鉴使用 `python -m cn_data_adapters.yearbook`，发布表格使用 `python -m cn_data_adapters.bulletin`。具体入口与数值映射要求见 [YEARBOOK.md](YEARBOOK.md)。目录覆盖、原表留存、单元格提取与数值观察分别报告；图片不宣称已完成OCR，用户声明的统计期和单位不冒充自动核验。

国际年度序列使用 `python -m cn_data_adapters.worldbank`，先明确地区、指标和区间；保留来源空值、空单位及分页摘要，不自动统一国内外统计方法。

本地标准资料校验已合并，入口 `cn-data-adapters validate/validate-table`，见[迁移说明](CONTRACT_MIGRATION.md)。城市/分省、目录与成本入口见[行业地区资料](REGIONAL_DATA.md)。省级真实请求403仍属失败，目录登记不能转述已采集；图像转录不冒充完整OCR。

本轮更新的 `capabilities review` 分开展示来源实现、访问、取得状态、单位与版本政策；本轮未请求不表示源站没有资料。`coverage` 分开统计目录、原件摘要匹配、选定单元格核验和全表覆盖；部分单元格不升级为整张表成功。四张年鉴表的限定事实示例见 [USAGE.md](USAGE.md)，图像原件及首次历史可得时间仍须各自核对。

## 安装与结果状态

本仓可以单独安装；pip安装命令行包不等于在助手中注册Skill。按本仓README安装完整资源，再使用SKILL中的入口。结果生成、资料取得与原文核验分别解释；未知说明影响及补齐路径。原创代码MIT，第三方代码保留许可，公告、研报和数据不随代码许可转移权利。
