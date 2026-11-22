# R19 冻结参考配置核查

**完成。** 2026 年 11 月 20 日 11:33:44（北京时间）的正式准入把 C_ref、M_new、K_new 绑定到 `review20_common_lkh_85_r3`。重新读取 200/200 份 C_ref 实际 `run.par`，均与冻结设置及各自基础种子相符。198 个有效终态的终态、参数和引擎 SHA256 均与记录相符。其余两项终态仍分别为一次磁盘资源执行错误和一次分页监测中止。[准入、配置、历史映射和结果的哈希回执](R19_configuration_receipt.json)

## C_ref 的历史选择依据

11 月 20 日的 B2 参数映射记录以历史 P5/R4 为参照，保留其可见搜索设置和 C、三父环、M/K 续搜各角色的种子映射，改由一个重建且修改过的 Windows LKH 3.0.14 引擎运行三臂。源版本和 Windows 构建作为研究配置固定，三臂共用它以控制可执行实现的差异。B2 文档记录的是本轮沿用历史设置的理由。早期资料记录了历史 P5 作为项目冻结搜索配置，现有证据未建立最初选定 P5 的正式调优竞赛、全局最强或软件默认设置。历史 P5/P5-resume 与本轮共有 PE 是不同构建，历史 R4 中记录的 `TIME_LIMIT=86400` 也不代表本轮外层收费上限。[对应原始文件及调用链哈希](R19_configuration_receipt.json)

| 项目 | 本轮 C_ref 的实际绑定 |
| --- | --- |
| 初始状态 | 从坐标直接求解，使用组基础种子，不提供首环，`common_paid_s=0` |
| 候选构造 | `POPMUSIC`；邻居 5、样本 10、解数 25、试探 1；`POPMUSIC_INITIAL_TOUR=NO`，`MAX_CANDIDATES=5` |
| 搜索 | `SUBGRADIENT=NO`；两种移动类型均 5；`BACKTRACKING=NO`；`PATCHING_A=1`、`PATCHING_C=0`；`GAIN_CRITERION=YES` |
| 运行与算术 | `RUNS=1`、`MAX_TRIALS=100000`、`POPULATION_SIZE=0`、`SCALE=1`、`PRECISION=100`、`STOP_AT_OPTIMUM=NO` |
| 重组 | 公共参数 `RECOMBINATION=GPX2`，在满足条件时允许引擎内部重组。K 的额外三次外部重组单列，本文未逐次测量内部调用 |
| 计时 | 同一固定时间协议。85 秒请求停止，86 秒前证明停止，88 秒前认证交付，90 秒前完成清理 |

对 C_ref 的优势表述应限定在当前实例、配置、时间预算和有效配对。主比较 K/M 未检出稳定的正平均净收益，研究没有预设等价界值或做等价性检验。稿件由此定位为固定预算下的工作流实证评估，最优性和不同 LKH 配置的表现均未由这些比较建立。[LKH 作者入口](https://keldhelsgaun.github.io/)
