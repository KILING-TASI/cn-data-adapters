# 数据入口与实际范围

## 沪深日线到MarketLens

`python -m cn_data_adapters.market collect --input request.json --online --out-dir reports/new-market`。
request须明确market（SSE/SZSE）、六位code、kind（stock/etf）、start/end；窗口不超过366天。东方财富未复权日线，渠道成交量原值保留；未核单位不转换成股/份，导出volume_shares为空。不能推广到债券或其他市场。

`parse`接受已有`--raw`和真实`--retrieved-at`；`replay`接受snapshot.json及`--raw response.json`。`export`还需`--declaration`，其中priceFactor必须字符串1、factorEvidence明确全区间可比依据、category按MarketLens枚举、indexId明确或空字符串。所得market.csv可用MarketLens现有`import --kind market`入口导入。available_at取本次原取得时点，不是观察日或虚构历史发布时刻。未知复权因子/有公司行动时首版不导出。

本版未接ETF份额、融资买入/偿还、历史成分全集、龙虎榜或大宗交易专用接口。不能把通用下载器当作这些接口已接通。

## 官方响应留档

`python -m cn_data_adapters.source_archive capture --input source.json --online --out-dir reports/new-source`。
source.json提供sourceId、url、purpose。来源ID支持chinaclear/chinabond/shclearing/cnindex/safe/customs/neeq/hkex/sse/szse/cninfo；URL必须属于对应已列官方域名，重定向逐跳复核，不接受私网、账户凭据或非HTTPS。

这只是明确URL的响应捕获，未提供各机构全量结构化数据API、受限名册查询或任意PDF解析。HTTP成功不证明正文有效，响应可能是验证页。原件留在用户新目录，权利另核，不随开源包发布。

## 后续采集优先级

先补公告目录与业绩预告/股东户数字段，再逐源研究融资、ETF份额、交易榜单、海关/外管局和指数成分；A股XBRL与信用曲线另做专业适配和权限核验。SEC CompanyFacts JSON解析不等于通用XBRL解析。中债曲线数据不自动等于转债含权/OAS模型。

## 年鉴与官方统计发布

年鉴全章节原表、发布表格提取及明确数值映射见 [YEARBOOK.md](YEARBOOK.md)。包括暂未用于专业分析的章节；目录和原表覆盖不等于数值覆盖。
