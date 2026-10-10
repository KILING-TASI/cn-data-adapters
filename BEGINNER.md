# 资料准备

先运行教学入口看结果。真实请求明确基金六位字符串代码、起止日、研究截止日、币种和净值口径；不从名称猜代码。
请求字段：id、source（eastmoney-fund-nav）、fundCode、start、end、asOf、currency（CNY）、frequency（daily）、fields（unit_nav和distribution_text）。
原始响应为渠道原字节，标准快照为JSON。缺原响应时说明不能复查转换，不用缓存JSON摘要冒充原响应摘要。
校验成功退出0；输入或资料处理失败退出2。输出必须是新目录；不覆盖历史报告。

cn-data-adapters demo --out-dir reports/my-teaching


共同采集与观察表的单位、时间及版本范围见 [FORMAT_SCOPE.md](FORMAT_SCOPE.md)。宏观、微观和规则事件保留各自口径，不混作净值。
