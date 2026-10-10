# 行业与地区资料

城市房价入口 `cn-data-adapters housing collect/replay` 保留城市及同比/环比指数；原始出版者与获取渠道分别记录。2025年1月至2026年8月实测1400条城市月份记录，并完成冻结回放。每月70个有值城市才给样本等权均值，它不是官方全国指数，数量核对不证明名单或历史首次公开时点。

分省入口 `cn-data-adapters nbs collect/replay` 限定fsnd/fsjd明确指标及结束的统计期。教学反例检查维度、元数据、重复、未知及期间；2024年分省GDP真实请求返回403，本轮不算接通，不使用账号、Cookie或验证绕过。地市、县区以及行政区划历史版本尚未自动接通。

```text
cn-data-adapters housing collect --input examples/housing-request.json --online --out-dir reports/housing
cn-data-adapters housing replay --input reports/housing/snapshot.json --out-dir reports/housing-replay
cn-data-adapters nbs collect --input examples/nbs-provincial-request.json --online --out-dir reports/province
```

行业需求目录在catalogs/industry-coverage.json，以SW2021的31个一级行业登记。它不是指数代码表，也不是已接通标记；专用指标须逐项核对原发布机构、口径、时间和获取/使用条件，不能用域名白名单抵消缺口。当前专业仓未使用的资料仍可留存，不按投研用途删除教育、卫生、文化等年鉴章节。

年鉴图片先保留原件与摘要，再按原表行列转录。现有tables入口可把明确CSV映射成观察表；原取得、统计期、公开和可得时点分开，未知用null。不宣称已完成全部OCR；本轮C06-01两项指标2018—2024年14条经图像阅读转录，软件只校验结构，原件及转录不随代码发布。

本地目录使用 `cn-data-adapters inventory --root 明确目录 --out 新索引.json`，只读指定目录，不清理证据。测量一次运行使用 `cn-data-adapters measure --adapter housing --record 新测量.json -- replay --input 快照.json --out-dir 新目录`，记录逻辑下载尝试、完成响应字节、耗时和Python跟踪内存；不猜token或HTTP重定向层请求数。
