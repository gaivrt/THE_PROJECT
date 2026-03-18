# Metis Continuum — TODO

> 基于代码审查和哲学评估整理，按优先级排列。
> 标记说明：`[x]` 已完成 · `[ ]` 待办 · `[~]` 进行中

---

## P0 — 紧急修复（系统当前无法正常运行）

### 修复 API 端点的 `ollama_api` 引用错误

- [ ] `core/main.py:177-205` — `/api/generate`、`/api/chat`、`/api/health` 均调用 `metis.ollama_api`，但 `MetisContinuum.__init__` 中从未初始化该属性
- [ ] 方案 A：在 `MetisContinuum.__init__` 中补充 `self.ollama_api = OllamaAPI(...)` 初始化
- [ ] 方案 B：将 API 端点改为通过 `self.thinking_engine.llm` 统一调用，避免重复实例

### 实现 `queue_expression`

- [ ] `core/main.py:142-145` — 当前为 `pass`，思维表达的唯一出口被堵死
- [ ] 维护一个表达队列（`asyncio.Queue`）
- [ ] 在 WebSocket 循环中消费队列，将"已决定表达的思维"推送给前端
- [ ] 考虑在无 WebSocket 连接时的缓冲策略

---

## P1 — 核心功能补全（架构已搭好但关节未接通）

### 替换评估系统的随机占位符

- [ ] `core/modules/evaluation_system.py:92-95` — `_evaluate_coherence`：返回随机数
  - 方案：用 LLM 二次评判，输入思维文本，输出连贯性分数
  - 备选：基于句间逻辑连接词密度的启发式评分
- [ ] `core/modules/evaluation_system.py:97-100` — `_evaluate_relevance`：返回随机数
  - 方案：计算当前思维与上下文窗口的语义相似度（embedding cosine）
- [ ] `core/modules/evaluation_system.py:102-105` — `_evaluate_novelty`：返回随机数
  - 方案：计算当前思维与 `recent_evaluations` 中历史思维的平均语义距离
- [ ] `core/modules/evaluation_system.py:131-134` — `_is_urgent`：始终返回 `False`
  - 方案：检测思维中是否包含时间敏感关键词或用户交互触发的上下文

### 使用 `ThinkingLoop` 替代硬编码循环

- [ ] `core/main.py:107-140` — `start_continuous_thinking` 直接 `while True` + `sleep(5)`
- [ ] 改为使用 `core/utils/thinking_loop.py` 中已实现的 `ThinkingLoop`
- [ ] 接入自适应节奏调整（高质量思维加速、低质量思维减速）

### 实现语义记忆检索

- [ ] `core/modules/memory_module.py:143-149` — `_calculate_relevance` 仅用时间衰减
- [ ] 引入向量嵌入（可使用 Ollama embedding API 或 sentence-transformers）
- [ ] 存储时对每条记忆生成向量
- [ ] 检索时用余弦相似度匹配，替代纯时间衰减
- [ ] 综合 `时间衰减 × 语义相似度 × 重要性` 三因子排序

### 实现欲望—思维的语义关联

- [ ] `core/modules/desire_system.py:96-100` — `_calculate_relevance` 返回随机数
- [ ] 方案 A：关键词匹配（为每个欲望维护关键词表）
- [ ] 方案 B：embedding 相似度（将欲望描述与思维内容做向量匹配）
- [ ] 确保欲望满足度更新反映真实的思维—欲望关联

---

## P2 — 哲学层面升级（让系统更像"心灵"）

### 涌现式欲望生成

- [ ] 当思维内容反复涉及某一主题（超过阈值次数），自动提炼为新欲望
- [ ] 使用 LLM 从近期思维链中提取潜在动机
- [ ] 新欲望的初始优先级根据出现频率和情感强度计算
- [ ] 添加欲望消亡机制：长期未被激活的欲望降低优先级直至移除

### 动态情感衰减

- [ ] `core/modules/emotion_module.py` — 当前 `decay_rate = 0.1` 全局固定
- [ ] 基于情感事件历史调整衰减率：
  - 反复正面体验 → 降低正面衰减率（情感韧性）
  - 反复负面体验 → 可配置为"脱敏"（加速衰减）或"创伤"（减缓衰减）
- [ ] 为 VAD 三个维度设置独立衰减率

### 记忆再巩固（Reconsolidation）

- [ ] 每次检索长期记忆时，用 LLM 对旧记忆做"重新诠释"
- [ ] 将当前情感状态融入重新诠释过程（情绪依赖性记忆）
- [ ] 更新记忆内容而非仅更新访问元数据
- [ ] 模拟记忆的建构性本质：记忆不是播放录像，而是每次重构

### 记忆重要性评估改进

- [ ] `core/modules/memory_module.py:109-115` — `_calculate_importance` 仅用情感强度
- [ ] 增加"认知重要性"维度：与活跃欲望的关联度、思维链中的因果地位
- [ ] 防止"平静的深刻洞见被遗忘，肤浅的情绪反应被保留"

---

## P3 — 工程质量与可观测性

### 测试补全

- [ ] 模块间集成测试：情感状态实际影响思维生成的端到端路径
- [ ] 思维循环端到端测试（mock LLM 响应，验证完整循环）
- [ ] WebSocket 交互测试（连接、状态推送、断开）
- [ ] 评估系统实现真实评估后的回归测试
- [ ] 记忆模块的巩固/检索/清理流程测试

### 可观测性

- [ ] 为每轮思维循环添加结构化日志（思维摘要、评估分数、是否表达、情感快照）
- [ ] 添加 `/api/state` 端点，返回当前系统完整内部状态（调试用）
- [ ] 考虑添加 Prometheus metrics：思维生成延迟、表达率、情感维度时序

### 配置与健壮性

- [ ] `core/utils/config.py` 的 `MetisConfig` 已定义但 `main.py` 未使用，改为统一走 Pydantic 配置
- [ ] 为 LLM 调用添加超时控制（当前无超时，Ollama 不响应时会永久阻塞）
- [ ] CORS `allow_origins=["*"]` 需在生产环境中收紧

---

## P4 — 长期演进方向

### 多模态感知

- [ ] 接入视觉输入（图像理解），让思维不仅基于文本
- [ ] 探索音频情感分析作为情感模块的外部输入

### 多 Agent 交互

- [ ] 支持多个 Metis 实例间通过欲望和情感状态互相影响
- [ ] 模拟社会认知：他者模型（Theory of Mind）

### 元学习

- [ ] 系统通过回顾自身思维历史，调整评估权重和欲望优先级
- [ ] 实现"性格演化"：长期运行后系统展现出稳定的个性特征
