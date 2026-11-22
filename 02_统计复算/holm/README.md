# 最终四项 Holm 推断与冻结阶段结果

最终稿对预先规定的 K/C、M/C、K/EAX、M/EAX 四项次要比较联合进行 Holm 校正（C）。原核心批次的校正保留为核心阶段快照（A），当时未估计的 EAX 两项在校正计算中以 `p = 1` 占位。EAX 后补报告的原有两项 Holm 校正保留为辅助计算（B）。已核实的执行前材料未给出独立两项家族的明确登记依据。唯一主要比较 K/M 有独立的原始检验，`p = 0.6477298736572265625`。

| 比较 | 有效配对 | 原始 p 的精确命中数（分母均为 1,048,576） | A 核心阶段快照 | B EAX 辅助后补 | C 最终四项推断 |
| --- | ---: | ---: | ---: | ---: | ---: |
| K/M | 198 | 679,194 | — | — | — |
| K/C | 197 | 66 | 0.00025177001953125 | — | 0.00020599365234375 |
| M/C | 197 | 588 | 0.001682281494140625 | — | 0.000560760498046875 |
| K/EAX | 198 | 54 | 1（校正占位，未估计） | 0.000102996826171875 | 0.00020599365234375 |
| M/EAX | 198 | 62 | 1（校正占位，未估计） | 0.000102996826171875 | 0.00020599365234375 |

主文表 2 只呈现原 600 项核心数据及 A，摘要和完整家族推断采用 C。EAX 外部比较使用后续独立时间段运行的 EAX 和原核心批次既有的 M/K，按地图与登记种子匹配。因此联合校正仍基于原来各自的样本、分母、检验算法与计时时段。四项在 0.05 水平的判断与原分别校正一致。

## 登记证据

- 核心准入前的 `新实验预登记候选.md` 统计节同时设定四项家族及 EAX 缺席的占位规则。其 SHA256 为 `0c9729aeb59b845572bfa5271ccbdf46222e80543cb7572a2721a5d9f591d3f2`。核心正式准入的 `runtime_hashes` 绑定文字、统计实现和执行范围记录，首个正式派发绑定准入摘要。
- 2026-11-20 11:26:19（北京时间）记录原 800 槽中先执行 600 个 C/M/K 槽，暂缓 200 个 EAX 槽。2026-11-20 11:33:44 完成核心准入及首派发。
- 2026-11-21 12:43:13 记录 EAX 后补运行合同，沿用原注册计划网格和同一计划摘要。2026-11-21 13:47:29 至 13:47:30 完成 EAX 准入及首派发。核验的后补合同规定独立计时范围与运行门槛，合同所绑定的完成后报告指令要求保留核心四项快照与单列后补方案。EAX 原分析代码及冻结结果记录了 B 的两项 Holm 实际计算。
- [冻结登记与准入证据链](verified_replay/registration_chain.json)记录源文件及原始时间的 SHA256 绑定关系。这是项目内部冻结证据。

## English interpretation

The preregistered secondary family contains K/C, M/C, K/EAX, and M/EAX. The final analysis applies Holm to all four observed raw p values. It yields 0.000206 for K/C, K/EAX, and M/EAX, and 0.000561 for M/C. Table 2 reports the historical core-stage snapshot, in which the two unavailable EAX tests had p = 1 adjustment placeholders and no estimated effects. The two-contrast Holm calculation in the later EAX report is retained as supplementary. The verified pre-run material did not specify a separate two-contrast family. The primary K/M inference remains separate. The EAX workflow ran later and was matched to existing M/K results on map and registered seed.

## 复算与显示值

按同地图和登记种子匹配有效路线。每对以 `10⁶ × (参照长度 − 比较长度) / 参照长度` 从原始整数长度计算精确分数，先图内平均，再按地图等权。每个比较覆盖 20 张地图，其双侧精确符号翻转检验计入与观察统计量绝对值相等的符号配置。Holm 排序、倍乘及单调性调整均使用精确有理数。

从包根目录运行，输出位置须为此前未使用的路径。

```text
python -I -S -B -X utf8 "02_统计复算/holm/replay_holm.py" --bundle . --output ../cmk-holm-replay
```

- [当前复算脚本](replay_holm.py)读取 600 条核心记录和 200 条 EAX 记录，逐项对账两份冻结统计的原始 p 值、配对数量与旧 Holm 值。
- [冻结数值 CSV](verified_replay/holm_comparison.csv)与本轮重算的 CSV 逐字节吻合。兼容已有数据的列名 `core_holm_a_p`、`later_holm_b_p`、`four_observed_holm_c_p` 仍分别指 A、B、C。[旧复算回执](verified_replay/holm_replay_receipt.json)保留上轮将 C 作为敏感性复核时的表述；新执行脚本产生的回执用 `reporting_roles` 标记本稿的三个用途。
- 双语稿件中次要比较的 p 值呈现六位小数，K/M 的原始 p 值呈现三位小数。作者档案另有生成展示值的脚本及其逐项精确输出。
