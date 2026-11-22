# 三批统计与绘图复算

从包根目录运行。`../cmk-replay` 是包外尚不存在的输出目录，可替换为其他空位置。统计模式只需 Python 3.10 或更新版本的标准库。绘图模式需 Matplotlib，已在 3.10.6 验证。两种模式只读取已保存数值。

```text
python -I -S -B -X utf8 "02_统计复算/replay_all.py" --output ../cmk-replay
python -B -X utf8 "02_统计复算/replay_all.py" --output ../cmk-figures --figures
```

| 入口 | 输入与参考 | 覆盖 |
| --- | --- | --- |
| [原 600 项 `reproduce.py`](../03_数据与复算/reproduce.py) | 原始逐次整数路线长度、终态和冻结参考 | 主比较、原四项次要 Holm、交付、分层、留一图、196 个完整三元组的敏感性分析。比较专属配对保留各自样本。 |
| [EAX 复算](eax/README.md) | 主批和独立 EAX 的逐次 CSV、原后补参考 | 独立的有效配对、地图重抽样、精确符号翻转、独立两项 Holm、Table 5A 和 Figure S2 数据。 |
| [条件续搜复算](r14/README.md) | 120 条终点、固定计划、原摘要与配对 | 60 对、3 池和 6 个顺序子组、原 9 组区间的精确重放、Table 5B 和全点 Figure 5。 |
| [主批 Figure 1–4](../assets/figures/redraw_main.py) | 随包冻结数表和逐图/逐对衍生分析表 | 重绘现有图。Figure 3/4 从随包逐对起点–终点及顺序衍生表读取。公开基础长度表不足以重新提取底层起点与时序事件。 |
| [Figure S2 脚本](../08_独立补验与执行证据/EAX200/本轮公平性审计/render_eax_effects.py) | EAX 新生成的 `eax_map_effects_40.csv` | 逐图 EAX 效果及近零区域。 |

各阶段产物写入 `core`、`eax` 和 `r14`。`byte_comparisons.json` 对账 8 个原主批 CSV、3 个 EAX CSV 和条件诊断完整配对 CSV。绘图追加 `figures`、`figure_s2`、`figure_5`。Figure 5 的数据从终点重算，旧图仍存于原条件续搜记录。历史图以及补充图 S1 的不变展示保留。向量 PDF 的创建时间等元数据可能随重绘而异。

统计复算、图形再生、路线验环及从坐标重跑的可用范围各自见 [数据访问说明](../Data_Access_and_Archiving.md)。
