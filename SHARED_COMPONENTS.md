# 共享组件总表

检查范围扩为15个活跃仓的Git跟踪Python文件；统一UTF-8、LF及BOM口径。排除tests/test/build/dist及test_文件，非空短入口也登记。

仅用于开发和发布审阅。用户单仓运行无需其他仓或网络；固定副本不要求跟随权威源最新版。更新前核对方法、正反例与许可。哈希不证明语义等价，也不授予第三方数据权利。

本地检查：`python tools/check_shared_code.py`。跨仓检查：`python tools/check_shared_inventory.py 各仓检出目录 --output 检查结果.json`。GitHub Actions的Shared inventory工作流检查当前仓与其他活跃仓main；输出保存为运行附件，历史结果不覆盖。

| 权威来源 | 固定哈希（前12位） | 副本位置 |
|---|---|---|
| cn-data-adapters/cn_data_adapters/teaching.py | 14f328ebf4b7 | portfolio-decision-engine/src/portfolio_engine/nav_collection/teaching.py<br>research-workbench/scripts/nav_collection/teaching.py<br>cn-data-adapters/cn_data_adapters/teaching.py |
| research-workbench/scripts/nav_collection/__init__.py | 1a418cc815f0 | portfolio-decision-engine/src/portfolio_engine/nav_collection/__init__.py<br>research-workbench/scripts/nav_collection/__init__.py |
| cn-data-adapters/cn_data_adapters/public_download.py | 3e73f6b93a95 | research-workbench/scripts/public_download.py<br>cn-data-adapters/cn_data_adapters/public_download.py |
| research-workbench/research_workbench/__main__.py | 4bfdc81d7865 | bjx-ipo-engine/bjx_cli/__main__.py<br>macro-dashboard-engine/macro_dashboard/__main__.py<br>marketlens/scripts/marketlens/__main__.py<br>research-workbench/research_workbench/__main__.py |
| cn-data-adapters/cn_data_adapters/nav.py | 54918a07f8e2 | portfolio-decision-engine/src/portfolio_engine/nav_collection/nav.py<br>research-workbench/scripts/nav_collection/nav.py<br>cn-data-adapters/cn_data_adapters/nav.py |
| research-workbench/scripts/nav_collection/__main__.py | 569de538de51 | portfolio-decision-engine/src/portfolio_engine/nav_collection/__main__.py<br>research-workbench/scripts/nav_collection/__main__.py |
| research-workbench/setup.py | 69d9c745c320 | macro-dashboard-engine/setup.py<br>marketlens/setup.py<br>research-workbench/setup.py |
| cn-data-adapters/cn_data_adapters/contracts/observations.py | a0913536e145 | portfolio-decision-engine/src/portfolio_engine/nav_collection/_observations.py<br>research-workbench/scripts/nav_collection/_observations.py<br>cn-data-adapters/cn_data_adapters/contracts/observations.py |
| cn-data-adapters/cn_data_adapters/tables.py | ab87db7c8a0c | portfolio-decision-engine/src/portfolio_engine/nav_collection/tables.py<br>research-workbench/scripts/nav_collection/tables.py<br>cn-data-adapters/cn_data_adapters/tables.py |
| research-workbench/modules/bjx-newshare-toolkit/scripts/announcement_versions.py | afe0f264ec68 | bjx-ipo-engine/vendor/announcement_versions.py<br>research-workbench/modules/bjx-newshare-toolkit/scripts/announcement_versions.py |
| cn-data-adapters/cn_data_adapters/review_io.py | c8e995fff783 | cn-financial-reconcile/cnreconcile/review_io.py<br>cn-fund-lookthrough/cnlookthrough/review_io.py<br>cn-market-rules/scripts/review_io.py<br>macro-dashboard-engine/scripts/review_io.py<br>marketlens/scripts/marketlens/review_io.py<br>portfolio-decision-engine/src/portfolio_engine/nav_collection/review_io.py<br>portfolio-decision-engine/src/portfolio_engine/review_io.py<br>research-workbench/scripts/nav_collection/review_io.py<br>research-workbench/scripts/review_io.py<br>cn-data-adapters/cn_data_adapters/review_io.py |
| cn-data-adapters/tools/check_shared_code.py | ca56b58560ad | bjx-ipo-engine/tools/check_shared_code.py<br>cn-financial-reconcile/tools/check_shared_code.py<br>cn-fund-lookthrough/tools/check_shared_code.py<br>cn-market-rules/tools/check_shared_code.py<br>macro-dashboard-engine/tools/check_shared_code.py<br>marketlens/tools/check_shared_code.py<br>portfolio-decision-engine/tools/check_shared_code.py<br>research-workbench/tools/check_shared_code.py<br>cn-data-adapters/tools/check_shared_code.py |
| research-workbench/scripts/event_html_controls.py | d256eafb4bcf | cn-financial-reconcile/cnreconcile/html_controls.py<br>cn-fund-lookthrough/cnlookthrough/html_controls.py<br>research-workbench/scripts/event_html_controls.py |
| cn-data-adapters/cn_data_adapters/contracts/collection.py | e2f4aafefdab | portfolio-decision-engine/src/portfolio_engine/nav_collection/_contract.py<br>research-workbench/scripts/nav_collection/_contract.py<br>cn-data-adapters/cn_data_adapters/contracts/collection.py |
| research-workbench/modules/bjx-newshare-toolkit/scripts/compare_original_versions.py | e384f9c4e91c | bjx-ipo-engine/vendor/compare_original_versions.py<br>research-workbench/modules/bjx-newshare-toolkit/scripts/compare_original_versions.py |
| cn-data-adapters/cn_data_adapters/housing_model.py | f6e13afdde95 | macro-dashboard-engine/scripts/housing_model.py<br>cn-data-adapters/cn_data_adapters/housing_model.py |

## 2026-10-15固定组件增补

数据仓维护 matching.py、wdi_core.py、response_archive.py。尾部风险Skill携带固定版本，登记于双方SHARED_CODE.json，运行时不导入兄弟仓。PUBLIC_VALIDATION.json和tools/verify_public_validation.py在15仓分别登记真实公开底稿、混合教学或缺口；通过不等于真实投资效果验收。因子仓与PDE已冻结的兼容副本补入清单，不替换旧算法。
