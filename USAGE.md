# 研究数据采集与重放：详细使用说明

当前安装与教学入口见[首页](README.md)，资料准备见[BEGINNER](BEGINNER.md)。历史下载说明见[版本记录](CHANGELOG.md)。以下保留具体命令、方法、样本和限制，历史案例按各自日期阅读。

## 数据入口

| 想取得什么 | 安装后入口 | 当前结果范围 |
|---|---|---|
| 年鉴各章节及国际附录 | `cn-data-adapters yearbook --help` | 目录与限定原表留档，图片尚未数值化 |
| 官方HTML发布表格 | `cn-data-adapters bulletin --help` | 单元格提取与明确映射；不猜单位/统计期 |
| 国际年度序列 | `cn-data-adapters worldbank --help` | WDI指定指标/地区/年度与冻结回放 |
| 沪深股票、ETF日行情 | `cn-data-adapters market --help` | 限定日线、未知成交单位保留 |
| 其他官方公开资料 | `cn-data-adapters source-archive --help` | 明确URL原始响应，不等于专用接口接通 |

## 输入与结果

标准化记录使用 `cn-research-collection/1.0`，声明请求、数据、单位、来源、取得时间、重放时间、覆盖与未知原因。
成功只表示这一处理步骤完成，不认证原发布者、完整日历、分红拆分或历史可得性；单位净值不能直接作为完整总回报。
来源渠道和原发布者分开。原始响应SHA与标准化SHA用途不同，字节校验不是数字签名。


## 来源和许可

原创代码MIT；数据与第三方权利见[说明](THIRD_PARTY_NOTICES.md)。输出目录必须为新目录。
其他问题可看[工具导航](https://github.com/KILING-TASI/research-workbench/blob/main/references/tool-navigation.md)。


共同采集与观察表的单位、时间及版本范围见 [FORMAT_SCOPE.md](FORMAT_SCOPE.md)。宏观、微观和规则事件保留各自口径，不混作净值。


[本轮审计范围与未认证事项](AUDIT_SCOPE.md)。


[独立使用与真实渠道验收范围](VALIDATION.md)。


当前版本：[v0.4.0](https://github.com/KILING-TASI/cn-data-adapters/releases/tag/v0.4.0)。发布页提供完整源码、wheel、sdist与校验清单；三个包仅用标准库，pip安装不自动注册Skill。


## 年鉴与官方统计发布

年鉴全章节原表、发布表格提取及明确数值映射见 [YEARBOOK.md](YEARBOOK.md)。包括暂未用于专业分析的章节；目录和原表覆盖不等于数值覆盖。


## 本地校验与行业地区资料

[契约合并与旧命令迁移](CONTRACT_MIGRATION.md) · [城市、分省、行业目录与运行成本](REGIONAL_DATA.md)。


开发维护见[共享组件总表](SHARED_COMPONENTS.md)：固定副本哈希与跨仓遗漏检测分开检查，用户使用本仓不要求其他仓库。
