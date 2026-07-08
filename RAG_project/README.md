# 🤖 RAG 智能问答系统

基于检索增强生成（Retrieval-Augmented Generation）技术的智能问答应用，支持知识库文档管理、多轮对话与多会话管理。

---

## 📌 项目简介

本项目是一个端到端的 **RAG 智能问答系统**，通过将本地文档知识向量化存储，结合大语言模型的生成能力，实现基于私有知识库的智能问答。系统采用 Streamlit 构建交互式 Web 界面，支持知识库上传、多会话管理和持久化对话历史。

### 核心特性

- 📚 **知识库管理** — 支持上传 TXT 文档，自动进行文本分割、去重（MD5 校验）和向量化存储
- 💬 **智能问答** — 基于检索增强生成（RAG），结合上下文与知识库进行精准回答
- 🗂️ **多会话支持** — 支持创建、切换、重命名和删除多个独立对话会话
- 📝 **对话历史持久化** — 会话历史自动保存至本地 JSON 文件，支持多轮上下文理解
- 🔍 **语义检索** — 基于向量相似度从知识库中检索最相关的文档片段
- 🎨 **精美 UI** — 采用现代化渐变主题，支持聊天消息气泡式展示

---

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                      前端层 (Streamlit)                   │
│  ┌──────────────┐  ┌──────────────┐                       │
│  │  智能问答页面 │  │ 知识库上传  │                       │
│  │  app_qa.py   │  │app_file_up.py│                       │
│  └──────┬───────┘  └──────┬───────┘                       │
│         └─────────────────┘                               │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────┐
│                      服务层 (LangChain)                  │
│  ┌──────────────────────┴──────────────────────┐          │
│  │            RagService (rag.py)             │          │
│  │  ┌──────────────┐  ┌────────────────────┐  │          │
│  │  │  向量检索    │  │  大模型对话生成    │  │          │
│  │  │  Retriever   │  │  ChatTongyi        │  │          │
│  │  └──────────────┘  └────────────────────┘  │          │
│  └────────────────────────────────────────────┘          │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────┐
│                      数据层                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  ChromaDB    │  │  对话历史    │  │  MD5 校验库  │   │
│  │  (向量数据库)  │  │  (JSON 文件) │  │  (文本文件)  │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 技术栈

| 层级 | 技术 |
|------|------|
| 前端框架 | [Streamlit](https://streamlit.io/) |
| LLM 模型 | 通义千问 Qwen3-max (via DashScope) |
| 嵌入模型 | text-embedding-v4 (DashScope) |
| 向量数据库 | [ChromaDB](https://www.trychroma.com/) |
| 应用框架 | [LangChain](https://www.langchain.com/) |
| 文本分割 | RecursiveCharacterTextSplitter |
| 消息历史 | FileChatMessageHistory (自定义) |

---

## 📁 项目结构

```
RAG_project/
├── app_qa.py              # 智能问答主页面（Streamlit 应用）
├── app_file_up.py         # 知识库上传页面（Streamlit 应用）
├── rag.py                 # RAG 核心服务（检索 + 生成链）
├── knowledge_base.py      # 知识库服务（文档处理、向量化）
├── vector_stores.py       # 向量存储服务（ChromaDB 封装）
├── file_histroy_store.py  # 对话历史持久化（自定义文件存储）
├── config_data.py         # 全局配置参数
├── data/                  # 示例文档目录
│   └── 尺码推荐.txt
├── chroma_db/             # ChromaDB 向量数据库持久化目录
├── md5.text               # 已处理文档的 MD5 校验记录
└── chat_history/            # 对话历史 JSON 文件存储目录
```

---

## ⚙️ 配置说明

主要配置项位于 `config_data.py`：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `collection_name` | ChromaDB 集合名称 | `rag` |
| `persist_directory` | 向量数据库持久化路径 | `./chroma_db` |
| `chunk_size` | 文本分割最大长度 | `1000` |
| `chunk_overlap` | 文本分割重叠字符数 | `100` |
| `separators` | 文本分割分隔符 | `\n\n`, `\n`, `.`, `!`, `?`, `。`, `？`, ` `, `` |
| `similarity_threshold` | 检索返回的文档数量 | `1` |
| `embedding_model_name` | 嵌入模型名称 | `text-embedding-v4` |
| `chat_model_name` | 大语言模型名称 | `qwen3-max` |

> **注意**：使用 DashScope 服务需要配置 `DASHSCOPE_API_KEY` 环境变量。

---

## 🚀 快速开始

### 环境准备

1. 确保 Python 版本 ≥ 3.9
2. 配置 DashScope API Key：
   ```bash
   export DASHSCOPE_API_KEY="your-api-key-here"
   ```

### 安装依赖

```bash
pip install streamlit langchain langchain-chroma langchain-community dashscope
```

### 启动服务

#### 1. 启动智能问答页面
```bash
streamlit run app_qa.py
```

#### 2. 启动知识库上传页面
```bash
streamlit run app_file_up.py
```

> 建议分别在两个终端中运行，以便同时操作知识库管理和智能问答。

---

## 📖 使用指南

### 上传知识库文档

1. 启动 `app_file_up.py`
2. 在页面上传 TXT 格式文档
3. 系统会自动进行：
   - MD5 去重校验（避免重复上传）
   - 智能文本分割（按段落、句子、字符多级分割）
   - 向量化存储至 ChromaDB

### 智能问答

1. 启动 `app_qa.py`
2. 在侧边栏管理会话：
   - ➕ 新建会话
   - 💬 切换会话
   - ✏️ 重命名会话
   - 🗑️ 删除会话
   - 🧹 清空当前对话
3. 在输入框中提问，AI 将基于知识库内容给出回答

---

## 🔧 核心模块详解

### `RagService` (rag.py)

RAG 核心服务，构建完整的检索-生成链：

```python
chain = (
    {"input": RunnablePassthrough(), 
     "context": retriever | format_document}
    | prompt_template 
    | ChatTongyi 
    | StrOutputParser()
)
```

- 接收用户输入 → 检索相关文档 → 格式化上下文 → 生成回答
- 通过 `RunnableWithMessageHistory` 实现多轮对话历史管理

### `KnowledgeBaseService` (knowledge_base.py)

知识库服务，负责文档处理：

- **MD5 去重**：通过 `md5.text` 记录已处理文档，避免重复上传
- **文本分割**：使用 `RecursiveCharacterTextSplitter` 进行多级语义分割
- **向量化存储**：调用 ChromaDB 存储文本片段及元数据（来源、时间、操作人）

### `FileChatMessageHistory` (file_histroy_store.py)

自定义文件式对话历史存储：

- 继承 `BaseChatMessageHistory`
- 将对话记录序列化为 JSON 存储于 `./chat_history/` 目录
- 支持消息追加、读取和清空操作

---

## 🎯 应用场景

- 📖 **企业知识库问答** — 基于内部文档的智能客服
- 📚 **学习辅导助手** — 基于教材、笔记的答疑系统
- 🏥 **医疗文档检索** — 基于医学文献的专业咨询
- 📋 **产品文档查询** — 基于产品手册的技术支持
- ⚖️ **法律法规检索** — 基于法律条文的智能咨询

---

## 📸 界面预览

### 智能问答页面
- 现代化渐变主题，支持深色模式
- 聊天消息气泡式展示（用户右对齐、AI 左对齐）
- 会话侧边栏管理

### 知识库上传页面
- 简洁的文件上传界面
- 实时显示文件信息（名称、格式、大小）
- 上传状态反馈

---

## 🛣️ 未来规划

- [ ] 支持更多文档格式（PDF、Word、Markdown）
- [ ] 集成多种 LLM 后端（OpenAI、Claude、本地模型）
- [ ] 支持多模态知识库（图片、表格）
- [ ] 添加用户认证与权限管理
- [ ] 支持知识库文档编辑与版本管理
- [ ] 引入重排序（Reranker）优化检索效果
- [ ] 添加引用溯源（显示回答来源文档）

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建你的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

---

## 📄 许可证

本项目基于 [MIT License](LICENSE) 开源。

---

## 🙏 致谢

- [LangChain](https://github.com/langchain-ai/langchain) — LLM 应用框架
- [Streamlit](https://github.com/streamlit/streamlit) — 数据应用前端框架
- [ChromaDB](https://github.com/chroma-core/chroma) — 向量数据库
- [DashScope](https://dashscope.aliyun.com/) — 阿里云模型服务平台
- [通义千问](https://tongyi.aliyun.com/) — 大语言模型

---

> **提示**：本项目为学习和演示用途，生产环境部署时建议添加错误处理、日志记录、API 限流等安全机制。
