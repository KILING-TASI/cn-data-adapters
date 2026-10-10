# 年鉴与公开统计资料

数据仓面向后续研究储备资料，不以当前专业仓是否使用为采集条件。年鉴包括28个正文篇章与国际附录；就业、生活、教育、卫生、文化、社保及港澳台也纳入目录，不因暂时没有投研专题而删除。

## 年鉴全章节

```text
python -m cn_data_adapters.yearbook --year 2025 --online --out-dir reports/yearbook-index
python -m cn_data_adapters.yearbook --year 2025 --online --max-tables 29 --per-chapter 1 --out-dir reports/yearbook-samples
python -m cn_data_adapters.yearbook --year 2025 --online --max-tables 2000 --out-dir reports/yearbook-originals
```

第一条识别官方目录中的原表，第二条每章下载一张用于验收，第三条逐张下载所有已识别原表。使用 `--chapters 4,6,9` 可分章采集；单表16MiB、每批256MiB、最多2000张，达到上限须拆分。只访问指定年份国家统计局路径，不执行页面脚本，不下载账号或付费内容。输出目录必须全新；原表逐项记录成功、失败、摘要和取得时间。默认顺序采集；`--workers`上限4。图片响应签名异常时停止本批后续请求并冻结异常响应，不重试或绕过验证。已有目录原件可用 `--index-raw 原件路径` 离线重新识别。

2025年目录的数据表为图片。JPEG/PNG仅验证文件签名，不能据此认证数值；HTML或Excel仅标记收到响应。图片留档不等于数值结构化，需OCR及人工核对表头、单位、统计期、注释后另行入库。年鉴2025不是所有记录都属于2025年；不能按版次填统计期。国际附录单独标记，不拼接为国内序列。

## 月度、季度及其他官方发布

`source_archive` 支持明确URL的原始响应留存。统计局、能源、农业、交通、财政、央行、教育、卫生、环境、水利、社保、邮政、工信、文化、专利、港澳统计和国际组织列入允许来源；这些来源登记不表示专用数值接口已经完成。原有证券、海关、外管局来源继续保留。

```text
python -m cn_data_adapters.source_archive capture --input examples/resident-income-request.json --online --out-dir reports/income-source
python -m cn_data_adapters.bulletin --snapshot reports/income-source/snapshot.json --raw reports/income-source/response.json --mapping examples/resident-income-mapping.json --out-dir reports/income-values
```

HTML表格入口保留原文单元格、跨行跨列和来源摘要。映射必须明确原表行名、表头、统计期、单位及地区范围；表头改变、行名重复、跨行跨列或数值含特殊括号时停止，不能猜选。空格等缺失符号转为未知，不能填零。示例映射限定2025年全国居民年度收入、收入中位数和消费支出金额；不能直接用于季度、城乡或其他年份。没有映射时只导出单元格，不生成数值观察。

新增来源遵循同样流程：明确发布机构和获取渠道、核对公开访问与用途范围、冻结原件、解析、数值映射、反例验证、真实请求、离线复现。失败记录不能升级成采集成功。原始资料留在使用者本地；MIT仅覆盖原创程序，源站内容及再分发范围单独处理。

## 国际年度序列

世界银行WDI来源2使用官方分页JSON接口，支持明确的指标代码、1至30个三位地区码及1960年至当前年的年度区间。它不局限于人口，具体指标是否存在及单位、方法需要逐项查官方元数据；地区码可能是聚合地区，不能全部称为国家。最多10页、每页5000条、单页16MiB；分页数量不一致、记录重复或地区/指标/年度不符即失败，不发布部分结果为成功。原始分页响应留档，来源空值与空单位保留未知。

```text
python -m cn_data_adapters.worldbank collect --input examples/worldbank-population-request.json --online --out-dir reports/wdi-population
python -m cn_data_adapters.worldbank replay --input reports/wdi-population/snapshot.json --out-dir reports/wdi-population-replay
```

回放核对每页摘要，保留原取得时间，另记回放时间。新请求不会覆盖旧版本。此入口不进行跨国口径统一，不将国际组织修订数据倒填为过去已知数据。接口说明：https://datahelpdesk.worldbank.org/knowledgebase/articles/898581-api-basic-call-structures 。使用源数据前仍需核对对应数据集的许可和引用要求。
