# CLAUDE.md — 毕设项目上下文

> 项目：融合 RAG 与提示工程的 AI 生成内容隐性广告识别测试方案研究
> 每次在新会话中继续时，Claude 会自动读取此文件恢复上下文

---

## 项目概况

面向 AI 生成内容（AIGC）的安全测试需求，研究并设计融合 RAG + 提示工程的隐性广告智能识别测试方案。

**核心链路**：用户输入文本 → ChromaDB 检索相关法规/案例 → 拼装 Prompt → DeepSeek LLM 推理 → 输出判定结果（是否广告 + 风险等级 + 法律依据）

---

## 已确认的技术栈（不可更改，除非讨论后决定）

| 组件 | 选择 | 备注 |
|------|------|------|
| 语言 | Python 3.10+ | 当前环境 3.13 |
| LLM | DeepSeek API (`deepseek-chat`) | 国内直连 |
| Embedding | `BAAI/bge-m3` 本地 | ChromaDB 内置加载，约 2GB，需梯子下载 |
| 向量数据库 | ChromaDB | 零配置 |
| RAG 实现 | **原生（不用 LangChain）** | ChromaDB + DeepSeek 原生 API |
| 后端 | FastAPI | 保留（用户熟悉前后端分离） |
| 前端 | Streamlit | 纯 Python |

**明确排除**：LangChain（版本迭代快，原生更简单）、本地 LLM（不需要 GPU）

---

## 当前进度

- [x] 需求分析完成
- [x] 技术选型完成
- [x] Phase 0：环境搭建（2026-09-14 完成 — venv + 全部依赖安装通过）
- [x] Phase 1：Python 基础（2026-09-14 完成）
- [x] Phase 2：DeepSeek API 调通（2026-09-14 完成）
- [x] Phase 3：ChromaDB + BGE-M3 跑通（2026-09-14 完成）
- [x] Phase 4：RAG 核心链路串联 ⭐（2026-09-14 完成）
- [ ] Phase 5：提示工程设计与调优（进行中 — 变体 + 话术库 + 小规模对比测试已完成，正式选优待 Phase 10）
- [ ] Phase 6-11：待完成

### Phase 0 实际安装版本

> 因 Python 3.13 兼容性，requirements.txt 中部分包版本已调整：

| 包 | 计划版本 | 实际版本 | 原因 |
|---|---------|---------|------|
| chromadb | 0.5.5 | **1.5.9** | 0.5.5 与 numpy 2.x 冲突 |
| scikit-learn | 1.5.0 | **1.9.0** | 无 cp313 wheel |
| pandas | 2.2.0 | **2.3.3** | 无 cp313 wheel |
| httpx | 0.28.1 | **0.27.2** | openai 1.55.0 与 httpx 0.28 冲突（proxies 参数） |
| sentence-transformers | 未计划 | **6.0.1** | 加载 BGE-M3 必需（带 torch 2.14.0+cpu） |

⚠️ **ChromaDB 1.x API 与 0.5.x 不同**，后续编码需参考 1.x 文档。

---

## 项目文件结构

```
thesis/
├── CLAUDE.md                    ← 本文件（项目上下文）
├── 文档/
│   ├── 01-项目规划/
│   │   ├── 毕设详细设计文档.md     ← 给导师看的设计方案
│   │   └── 学习与开发路线图.md     ← 操作手册（11 个 Phase）
│   ├── 02-技术调研/
│   │   └── 设计风险审查与简化方案.md ← 技术决策依据
│   ├── 03-会议与沟通/            ← 导师会议记录
│   ├── 04-知识库资料/            ← 法规原文、案例素材
│   ├── 05-实验数据/              ← 测试集、实验结果
│   ├── 06-参考资料/              ← 文献、教程
│   ├── 07-论文草稿/              ← 各章节草稿
│   ├── 08-答辩准备/              ← PPT、演讲稿
│   └── 开发与学习日志/
│       └── 开发日志.md           ← 每日开发记录
└── code/
    ├── requirements.txt          ← 依赖
    └── venv/                     ← 虚拟环境（待重建）
```

---

## 用户背景

- 零 AI/LLM 基础，不理解 Transformer、PyTorch 等底层
- 曾用 AI 辅助开发安卓小说阅读器
- 写过 JavaWeb 管理系统（CRUD），理解前后端分离
- 理解软件架构和实现逻辑，但**对底层数学和 AI 训练一无所知**
- 有梯子，可访问 HuggingFace
- 开发策略：边学边做，最小学习量原则

---

## 关键技术决策与原因

1. **不用 LangChain**：RAG 链路仅 3 步（检索→拼 Prompt→LLM），原生 API 总共 ~15 行，不需要框架。LangChain 版本迭代快（一年 3 个大版本），网上的教程大量过期，出问题新手无法 debug。

2. **保留 FastAPI**：用户熟悉前后端分离（JavaWeb Controller 经验），FastAPI 仅 ~30 行代码，但给论文增加"API 接口设计"章节，且自带 Swagger `/docs` 方便调试。

3. **本地 BGE-M3**：用户有梯子，一次下载 ~2GB 后离线可用，零费用、零延迟。论文可写"本地 Embedding 方案避免云端依赖"。

4. **DeepSeek API**：国内直连，¥1/百万 tokens，全流程实验费用 < ¥20。

---

## 最高风险提醒

1. **LLM 输出 JSON 不稳定**：已设计 5 层容错解析器（`parser.py`）
2. **提示工程效果不确定**：可能 RAG 组效果不如裸 LLM，论文可分析原因
3. **版本锁定**：requirements.txt 已锁定所有版本号

---

## 工作规则（用户约定）

- **每当有重大变化时，记录到开发日志**（`文档/开发与学习日志/开发日志.md`）：包括新增功能、重要决策、踩坑及解决方案。
- **每当有重大变化时，git commit**：记录到开发日志后，同步 `git add` + `git commit`，形成可回退的版本点。
- **进入对应 Phase 时，提醒用户处理相关风险**：开发日志里有一份「风险清单」（9 个缺陷），进入对应 Phase 前，先查清单里有没有该 Phase 要处理的风险，主动提醒用户。

### 风险清单速查（完整版在开发日志）

| # | 风险 | 处理时机 |
|---|------|---------|
| 1 | 数据泄露（测试集与知识库重叠） | Phase 9 构建测试集时 |
| 4 | ad_type vs violation_type 重叠 | Phase 10 前（与 #5 一起改 Prompt） |
| 5 | 评估维度不全 | Phase 10 前 |
| 6 | 消融组别对应关系 | Phase 10 前 |
| 7 | 可复现 vs LLM 随机性 | Phase 10 |
| 8 | 知识库字段统一 | Phase 8 扩数据前 |
| 9 | 案例库语义/法律错配 | Phase 10 实验设计时 |

## 下一步

Phase 5 开发部分已完成：7 套 Prompt 变体 + 话术库（三路召回）+ 小测试集（10 条）+ 对比测试 + 风险分级标准已写入 FULL_PROMPT/PE_PROMPT。

**关键结论**：is_ad 上 RAG 增益有限（simple=full=90%），RAG 价值在风险分级/法条引用（待 Phase 10 验证）。test_001（翻包）标注分歧已解决：看推销话术，不看品牌数量。

**下次继续**：按「8/9 尽早启动 + 6 顺手做 + 7 延后」的分层策略。建议从 Phase 6（FastAPI，1~2 天）或 Phase 8（知识库数据收集）开始。

### Prompt 变体（8 个 mode）

- simple / rag_only / cot / role / pe / fewshot / full / full_templates
- full（两库）vs full_templates（三库）用于验证话术库增益

### 代码结构

```
code/
├── core/                    ← RAG 核心模块
│   ├── config.py            ← 全局配置（API Key、路径、TOP_K）
│   ├── parser.py            ← 5 层容错 JSON 解析
│   ├── prompt_templates.py  ← 3 套 Prompt（full/simple/rag_only）
│   └── rag_pipeline.py      ← RAGPipeline 类（检索→Prompt→LLM→解析）
├── knowledge_base/
│   ├── data/laws.json       ← 5 条法规
│   ├── data/cases.json      ← 3 条案例
│   ├── data/templates.json  ← 18 条话术模板（可选增强）
│   ├── data/brands.json     ← 18 条品牌特征（关键词匹配，不进 ChromaDB）
│   ├── chroma_db/           ← ChromaDB 持久化目录
│   └── build_kb.py          ← 知识库构建脚本（三库向量检索）
└── phase4/test_rag_e2e.py   ← 端到端测试

### 运行提示

- Windows 终端运行 Python 加 `-X utf8` 避免中文乱码
- DeepSeek API Key 已填入 `code/phase2/config.py`（敏感信息，勿上传）
- 加载 BGE-M3 前设 `os.environ["HF_HUB_OFFLINE"]="1"`（模型已下载到本地，避免联网 SSL 错误）
- ChromaDB 1.x collection 名必须以字母开头（如 `ad_laws`）
