# Metis Continuum (持续思维AI系统)

一个具有情感和欲望驱动机制的持续思维AI系统。

## 系统特点

- 使用本地Ollama运行DeepSeek R1 7B模型进行持续思维
- 基于VAD（效价-唤醒度-支配度）模型的情感状态管理
- 具有动态满足度的欲望驱动行为系统
- 短期和长期记忆系统
- 实时思维评估和过滤
- 基于React的现代化前端，支持实时更新

## 环境要求

1. 安装 [Ollama](https://ollama.ai/)
2. 拉取 DeepSeek R1 7B 模型：
```bash
ollama pull deepseek-r1-7b
```
3. Python 3.9 或更高版本

## 安装步骤

1. 克隆仓库：
```bash
git clone <仓库地址>
cd metis-continuum
```

2. 创建并激活虚拟环境：
```bash
python -m venv venv
# Windows系统:
venv\Scripts\activate
# Linux/Mac系统:
source venv/bin/activate
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

## 配置说明

在项目根目录创建 `.env` 文件，包含以下配置：

```env
# 模型设置
MODEL_NAME=deepseek-r1-7b
OLLAMA_API_URL=http://localhost:11434/api

# 服务器设置
HOST=localhost
PORT=8000

# 思维循环设置
THOUGHT_INTERVAL=5.0          # 思维生成间隔（秒）
MEMORY_CLEANUP_INTERVAL=300.0 # 记忆清理间隔（秒）

# 记忆设置
SHORT_TERM_MEMORY_SIZE=100    # 短期记忆容量
CONTEXT_WINDOW_SIZE=10        # 上下文窗口大小
LONG_TERM_MEMORY_THRESHOLD=0.7 # 长期记忆阈值

# 情感设置
EMOTION_DECAY_RATE=0.1        # 情感衰减率
EMOTION_UPDATE_WEIGHT=0.3     # 情感更新权重

# 欲望设置
DESIRE_DECAY_RATE=0.05        # 欲望衰减率
SATISFACTION_THRESHOLD=0.7    # 满足度阈值

# 评估设置
MIN_CONFIDENCE_THRESHOLD=0.6  # 最小置信度阈值
MIN_EMOTIONAL_IMPACT=0.3      # 最小情感影响
```

## 项目结构

```
metis-continuum/
├── core/                    # 核心代码
│   ├── models/             # 模型相关
│   │   └── deepseek_wrapper.py  # DeepSeek模型封装
│   ├── modules/            # 功能模块
│   │   ├── emotion_module.py    # 情感模块
│   │   ├── desire_system.py     # 欲望系统
│   │   ├── memory_module.py     # 记忆模块
│   │   └── evaluation_system.py # 评估系统
│   └── utils/              # 工具类
│       ├── thinking_loop.py     # 思维循环
│       └── config.py            # 配置工具
├── frontend/               # 前端代码
│   └── src/
│       ├── components/     # React组件
│       │   ├── ThinkingDisplay.tsx  # 思维显示
│       │   ├── EmotionDisplay.tsx   # 情感显示
│       │   └── DesireDisplay.tsx    # 欲望显示
│       └── types/         # 类型定义
│           └── index.ts
├── tests/                 # 测试代码
├── .env                   # 环境配置
├── main.py               # 主程序
└── requirements.txt      # Python依赖
```

## 运行测试

```bash
python -m pytest tests/ -v
```

## 运行应用

1. 启动后端服务器：
```bash
python main.py
```

2. 启动前端开发服务器：
```bash
cd frontend
npm install
npm start
```

3. 访问 `http://localhost:3000` 查看应用

## 主要功能模块说明

### 1. 思维引擎 (DeepSeek Wrapper)
- 使用本地Ollama运行DeepSeek R1 7B模型
- 支持上下文感知的思维生成
- 集成情感和欲望因素

### 2. 情感系统
- 基于VAD模型管理情感状态
- 情感状态动态更新和衰减
- 影响思维生成和决策

### 3. 欲望系统
- 管理基本和自定义欲望
- 动态调整满足度
- 优先级影响行为决策

### 4. 记忆系统
- 短期记忆用于即时思维
- 长期记忆存储重要信息
- 上下文窗口管理最近思维

### 5. 评估系统
- 评估思维的质量和相关性
- 过滤低质量思维
- 影响记忆存储决策

## 参与贡献

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m '添加某个特性'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 开源协议

本项目采用 MIT 协议 - 详见 LICENSE 文件
