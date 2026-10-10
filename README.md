# 研究数据采集与重放

采集与储备研究资料，支持基金净值、沪深日行情、年鉴全章节原表、官方发布表格与世界银行年度序列。保留来源、取得时间、版本和未知事项；当前专业工具未使用的数据也可独立留档。

| 想取得什么 | 安装后入口 | 当前结果范围 |
|---|---|---|
| 年鉴各章节及国际附录 | `cn-data-adapters yearbook --help` | 目录与限定原表留档，图片尚未数值化 |
| 官方HTML发布表格 | `cn-data-adapters bulletin --help` | 单元格提取与明确映射；不猜单位/统计期 |
| 国际年度序列 | `cn-data-adapters worldbank --help` | WDI指定指标/地区/年度与冻结回放 |
| 沪深股票、ETF日行情 | `cn-data-adapters market --help` | 限定日线、未知成交单位保留 |
| 其他官方公开资料 | `cn-data-adapters source-archive --help` | 明确URL原始响应，不等于专用接口接通 |

各入口可独立使用，原始资料保留本地；真实成功和失败范围见 [VALIDATION.md](VALIDATION.md)。

## 先试一次

源码解压后需要Python 3.10或以上，不需要安装其他自家仓库。
Windows运行 `Start-Demo.cmd`，也可执行 `python try_demo.py`；Linux/macOS执行 `sh Start-Demo.sh`。
这是原创教学例子，不取真实数据、不覆盖旧结果。真实研究先看[资料准备](BEGINNER.md)。

## 名称与安装

仓库、发行包、命令和Skill注册名都是 `cn-data-adapters`，Python模块为 `cn_data_adapters`。
在独立Python环境中执行 `python -m pip install .`，再运行 `cn-data-adapters --help`。
仅用标准库，安装CLI不会自动注册Skill；Skill保留完整源码资源。

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

## 参与、更新与清理

[贡献说明](CONTRIBUTING.md) · [安全反馈](SECURITY.md) · [更新、缓存与卸载](LIFECYCLE.md)。

## 本地校验与行业地区资料

[契约合并与旧命令迁移](CONTRACT_MIGRATION.md) · [城市、分省、行业目录与运行成本](REGIONAL_DATA.md)。
