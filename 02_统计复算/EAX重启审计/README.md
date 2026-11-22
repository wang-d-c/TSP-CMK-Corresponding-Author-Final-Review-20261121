# EAX 原生进程与重启公开汇总

公开表来自对现有 200 项 EAX 正式终态、包装器和原生子进程输出的复核。正式成绩及 p 值沿用冻结结果。e0316 仍保留单进程证据失败和空分。

- [原生进程数量分布](replayed/native_process_distribution.csv)
- [20 张地图的重启和自然 trial 完成分布](replayed/native_restarts_by_map.csv)
- [M/EAX 和 K/EAX 的进程分组配对结果](replayed/descriptive_effects_by_process_count.csv)

180 项只启动一个原生子进程，其中 179 项有效。20 项各启动两个子进程，其中第一个自然完成一次 trial 后，工作流启动第二个。每项双进程运行实际发生一次重启。两张 VLSI 图 dga9698 与 xmc10150 各有 10 项重启，其余 18 张图均未出现重启。旧审计字段 `process_restarts` 来源于 `len(children)`，其值表示原生子进程数。

分组统计中的短／平／长以左侧方法 M 或 K 相对 EAX 的路线长度判定。ppm 为 `1,000,000 × (EAX 长度 − M 或 K 长度) / EAX 长度`，有效配对先在每图内平均，再按地图等权。分组与地图构成完全重合，因此结果仅描述这两个组的差异，不能据此识别重启的因果效应。

所有地图在本批次只出现在一个进程组。可将逐图重启表与[有效配对长度](../../08_独立补验与执行证据/EAX200/正式结果/supplemental_eax_valid_pairs.csv)按地图连接，用原整数长度复核两个组的胜平负及地图等权效果。

公开表支持核对已报告的汇总记录。逐槽终态、原生 stdout、控制账本和原始运行归档需经权利核准由作者提供。完整生命周期的外部独立重放仍需获得这些原件。[数据访问条件](../../Data_Access_and_Archiving.md)
