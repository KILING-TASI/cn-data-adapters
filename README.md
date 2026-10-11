# 研究数据采集与重放

采集和储备研究资料，维护来源、单位、取得时间、冻结重放与离线格式校验。

[![原创代码 MIT](https://img.shields.io/badge/原创代码-MIT-green)](LICENSE) · [当前发行版 v0.4.1](https://github.com/KILING-TASI/cn-data-adapters/releases/tag/v0.4.1) · [运行检查](https://github.com/KILING-TASI/cn-data-adapters/actions)

## 能解决什么问题

**资料从哪里来？当时能否取得？失败、权限和单位缺口在哪里？**

采集、格式与原始留档集中维护；专业工具消费明确的数据记录，不要求全部工具同时安装。

## 快速开始

从[发行页](https://github.com/KILING-TASI/cn-data-adapters/releases/tag/v0.4.1)下载完整源码并解压，需要 Python 3.10 或以上。在源码目录执行：

```text
python try_demo.py --no-open --out-dir reports/first-demo
```

按提示打开新生成的 HTML。Windows 也可双击 `Start-Demo.cmd`，Linux/macOS 可用 `sh Start-Demo.sh`。教学使用原创模拟资料，不自动取真实数据；重复运行使用新目录，历史结果保留。

## 使用自己的资料

先按[资料准备](BEGINNER.md)填写输入，再看[详细命令与方法](USAGE.md)。需要安装CLI时，在自己的Python环境运行：

```text
python -m pip install .
cn-data-adapters --help
```

仓库、Python发行包、安装命令及Skill注册名均为 `cn-data-adapters`。CLI安装和Skill注册是两个步骤：自然语言调用按[SKILL.md](SKILL.md)配置，保留完整资源；不必安装全部仓库。安装普通构建依赖可能联网，教学流程不需要作者缓存。

## 结果范围

年鉴目录和原表覆盖不等于数值覆盖；取得响应不认证原发布者或完整历史事件。

报告中的来源、日期、假设和未知事项需一起阅读。程序运行成功不等于来源已经认证、资料完整或投资判断有效。原创代码采用MIT，第三方代码、公告、研报和数据仍按各自权利范围处理。

## 文档与维护

- [详细命令与方法](USAGE.md)
- [资料准备与排错](BEGINNER.md)
- [Skill调用指引](SKILL.md)
- [版本记录](CHANGELOG.md)
- [许可与第三方范围](THIRD_PARTY_NOTICES.md)
- [验收范围](VALIDATION.md)
- [审计范围](AUDIT_SCOPE.md)
- [年鉴与统计发布](YEARBOOK.md)
- [地区和行业资料](REGIONAL_DATA.md)
- [采集说明](DATA_ACQUISITION.md)
- [契约迁移](CONTRACT_MIGRATION.md)
- [共享组件总表](SHARED_COMPONENTS.md)

[贡献说明](CONTRIBUTING.md) · [安全反馈](SECURITY.md) · [更新与清理](LIFECYCLE.md) · [English](README.en.md)

[按问题选择其他工具](https://github.com/KILING-TASI/research-workbench/blob/main/references/tool-navigation.md)。共12个活跃仓，另有1个供旧记录复查的[历史契约仓](https://github.com/KILING-TASI/cn-research-contracts)。各仓分别发布；main的后续文档整理不改写旧发行包和冻结结果。

## v0.4.1 本轮补强

人口、省级GDP、工业产量选定数据项，原表与数值覆盖台账、来源能力核对。具体参数与边界见[使用说明](USAGE.md)。

## 采集全景与实际覆盖

国家与地区、31行业、公司基本面、预期、交易资金、事件、海外、另类、文本和产业链结构的职责及缺口见[全景对照](PANORAMA.md)。候选目录与采集结果分开，授权范围逐源记录。
