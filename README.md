# 研究数据采集与重放

采集和储备研究资料，维护来源、单位、取得时间、冻结重放与离线格式校验。

[原创代码 MIT](LICENSE) · [发行说明](https://github.com/KILING-TASI/cn-data-adapters/releases/tag/v0.4.2) · [运行检查](https://github.com/KILING-TASI/cn-data-adapters/actions) · [English](README.en.md)

当前发布：**v0.4.2 · 普通发行版**。Python **3.10+**；基础功能只需 Python，无第三方运行依赖。

[快速开始](#快速开始) · [使用自己的资料](#使用自己的资料) · [能力与边界](#能力与边界) · [文档与维护](#文档与维护)

## 能解决什么问题

**资料从哪里来？当时能否取得？失败、权限和单位缺口在哪里？**

采集、格式与原始留档集中维护；专业工具消费明确的数据记录，不要求全部工具同时安装。

| 需要准备 | 会得到什么 |
|---|---|
| 明确的来源入口、选定数据项，或原始响应与本地表格字段映射。 | 原始留档、来源与时间记录、格式校验、取得失败和覆盖缺口。 |

## 快速开始

1. 安装 Python 3.10 或以上版本。
2. 下载[完整源码 ZIP](https://github.com/KILING-TASI/cn-data-adapters/releases/download/v0.4.2/cn-data-adapters-v0.4.2-source.zip)并解压，进入包含 `try_demo.py` 的目录。
3. 在该目录打开终端，运行：

```console
python try_demo.py --no-open --out-dir reports/first-demo
```

按终端给出的路径打开 HTML。也可以在源码目录双击 `Start-Demo.cmd`（Windows），或运行 `sh Start-Demo.sh`（Linux/macOS）。教学使用原创模拟资料，不自动取得真实数据。

使用 Git 时，先运行 `git clone https://github.com/KILING-TASI/cn-data-adapters.git`，再运行 `cd cn-data-adapters`，随后执行上面的教学命令。重复运行请指定新目录，历史结果会保留。

## 使用自己的资料

先按[资料准备与排错](BEGINNER.md)整理来源、日期、单位和必要字段，再按[使用说明](USAGE.md)选择对应入口。以下两种使用方式分别配置。

**命令行（CLI）**：在源码目录安装本仓，然后查看可用命令：

```console
python -m pip install .
cn-data-adapters --help
```

基础安装不需要科学计算或 PDF 组件。安装时下载构建工具或可选依赖可能需要联网。

**助手 Skill**：按 [SKILL.md](SKILL.md) 配置，保留完整目录及其引用资源。安装 CLI 不会自动注册 Skill，也不表示已在第三方技能市场上架。

| 身份 | 名称 |
|---|---|
| GitHub 仓库 / Python 发行包 | `cn-data-adapters` |
| 主要命令 | `cn-data-adapters` |
| SKILL.md 中的名称 | `cn-data-adapters` |

本仓可单独使用。需要跨工具功能时，再按说明安装并明确配置对应工具的位置。

## 能力与边界

年鉴目录和原表覆盖不等于数值覆盖；取得响应不认证原发布者或完整历史事件。

报告中的来源、日期、假设和未知事项需一起阅读。程序运行成功不等于来源已经认证、资料完整或投资判断有效。原创代码采用MIT，第三方代码、公告、研报和数据仍按各自权利范围处理。

[采集全景与实际覆盖](PANORAMA.md)：候选目录、原表留档和数值覆盖分别记录。

## 文档与维护

- [详细命令与方法](USAGE.md)
- [资料准备与排错](BEGINNER.md)
- [Skill 调用指引](SKILL.md)
- [版本记录](CHANGELOG.md)
- [许可与第三方范围](THIRD_PARTY_NOTICES.md)
- [验收范围](VALIDATION.md)
- [审计范围](AUDIT_SCOPE.md)
- [年鉴与统计发布](YEARBOOK.md)
- [地区和行业资料](REGIONAL_DATA.md)
- [采集说明](DATA_ACQUISITION.md)
- [契约迁移](CONTRACT_MIGRATION.md)
- [共享组件总表](SHARED_COMPONENTS.md)

[贡献说明](CONTRIBUTING.md) · [安全反馈](SECURITY.md) · [更新与清理](LIFECYCLE.md)

[按问题选择其他工具](https://github.com/KILING-TASI/research-workbench/blob/main/references/tool-navigation.md)；资料契约校验已并入[数据仓](https://github.com/KILING-TASI/cn-data-adapters/blob/main/CONTRACT_MIGRATION.md)。默认分支的文档整理不改写已发布的源码包和历史结果；版本变化见 [CHANGELOG.md](CHANGELOG.md)。
