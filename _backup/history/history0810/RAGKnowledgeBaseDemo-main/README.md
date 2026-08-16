# RAG 知识库管理系统

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3.13-green.svg)](https://github.com/langchain-ai/langchain)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> 基于 LangChain 的多模态检索增强生成（RAG）知识库管理系统

## 📋 目录

- [项目简介](#项目简介)
- [核心特性](#核心特性)
- [技术栈](#技术栈)
- [系统架构](#系统架构)
- [快速开始](#快速开始)
- [组件说明](#组件说明)
- [使用示例](#使用示例)
- [开发进度](#开发进度)
- [文档导航](#文档导航)
- [团队分工](#团队分工)
- [贡献指南](#贡献指南)

---

## 📖 项目简介

本项目实现了一个完整的 RAG（Retrieval-Augmented Generation）知识库管理系统，支持多模态检索（向量检索、关键词检索、混合检索），为 AI 应用提供高质量的知识检索服务。

**设计目标**：
- 📚 支持多种文件格式的知识库构建
- 🔍 提供多种检索模式（向量、关键词、混合）
- 🎯 高精度的语义检索和重排序
- 🚀 易于集成的统一服务接口
- 📊 完整的文档管理能力

---

## ✨ 核心特性

### 🔍 多模态检索
- **向量检索**：基于 DashScope text-embedding-v2 模型的语义检索
- **关键词检索**：基于 BM25 算法的精确匹配，支持中文分词
- **混合检索**：RRF 融合 + DashScope Rerank 精排序（推荐）

### 📊 数据管理
- 文档增删操作（单个和批量）
- 数据一致性保证（事务性回滚机制）
- 基于 md5 的文档去重
- 持久化存储（Chroma + Pickle）

### 🎯 高可用性
- 多级降级策略（Rerank → RRF → Vector）
- 完整的异常处理
- 版本兼容性保证

### 🛠️ 易于使用
- 统一的 LangChain Document 接口
- 灵活的权重配置
- 完整的测试覆盖

---

## 🛠️ 技术栈

| 类别 | 技术 |
|------|------|
| **框架** | LangChain 0.3.13 |
| **向量数据库** | Chroma 0.5.23 |
| **嵌入模型** | DashScope text-embedding-v2 |
| **重排序模型** | DashScope qwen3-rerank |
| **关键词检索** | BM25 + jieba |
| **编程语言** | Python 3.8+ |

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────┐
│         KnowledgeBase（知识库）              │
│              [待集成]                         │
├─────────────────┬───────────────────────────┤
│   FileStore     │      RAGService           │
│  （文件存储）    │    （RAG 服务）✅          │
│   [待实现]      │                           │
├─────────────────┼───────────────────────────┤
│  - FileStore    │  - VectorDB ✅             │
│  - Splitter     │  - KeywordDB ✅            │
│  - Deduplicator │  - Reranker ✅             │
└─────────────────┴───────────────────────────┘
```

### RAG 服务架构（已完成）

```
┌──────────────────────────────────────────────┐
│              RAGService                      │
│  (统一检索接口 + 文档管理)                     │
└──────────┬─────────────┬──────────────┬─────┘
           │             │              │
    ┌──────▼──────┐ ┌───▼────────┐ ┌──▼─────────┐
    │  VectorDB   │ │ KeywordDB  │ │  Reranker  │
    │ (语义检索)   │ │ (精确匹配)  │ │ (重排序)    │
    └──────┬──────┘ └───┬────────┘ └──┬─────────┘
           │             │              │
    ┌──────▼──────┐ ┌───▼────────┐ ┌──▼─────────┐
    │  Chroma +   │ │ BM25 +     │ │ RRF +      │
    │  DashScope  │ │ jieba      │ │ DashScope  │
    │  Embedding  │ │            │ │ Rerank     │
    └─────────────┘ └────────────┘ └────────────┘
```

---

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <your-repo-url>
cd RAGKnowledgeBaseDemo-main

# 创建虚拟环境（推荐）
conda create -n rag_kb python=3.8
conda activate rag_kb

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件或设置环境变量：

```bash
# Windows (cmd)
set DASHSCOPE_API_KEY=your_api_key_here
set DASHSCOPE_WORKSPACE_ID=your_workspace_id  # 可选

# Linux/Mac
export DASHSCOPE_API_KEY=your_api_key_here
export DASHSCOPE_WORKSPACE_ID=your_workspace_id  # 可选
```

详细配置说明：[doc/环境变量配置说明.md](doc/环境变量配置说明.md)

### 3. 运行测试

```bash
cd test_scripts

# 测试数据加载器
python test_data_loader.py

# 测试向量数据库
python test_vectordb.py

# 测试关键词数据库
python test_keyworddb.py

# 测试重排序器
python test_reranker.py

# 测试 RAG 统一服务（推荐）
python test_ragservice.py
```

---

## 📦 组件说明

### 1. VectorDB（向量数据库）✅

**功能**：基于语义理解的向量检索

**核心方法**：
- `add_document(document)` - 添加单个文档
- `add_documents(documents)` - 批量添加文档
- `search(query, k)` - 向量检索
- `delete_document(md5)` - 删除文档

**详细文档**：[doc/项目实现过程/02_VectorDB实现.md](doc/项目实现过程/02_VectorDB实现.md)

---

### 2. KeywordDB（关键词数据库）✅

**功能**：基于 BM25 算法的关键词检索

**核心方法**：
- `add_document(document)` - 添加单个文档
- `add_documents(documents)` - 批量添加文档
- `search(query, k)` - 关键词检索
- `delete_document(md5)` - 删除文档

**详细文档**：[doc/项目实现过程/03_KeywordDB实现.md](doc/项目实现过程/03_KeywordDB实现.md)

---

### 3. Reranker（重排序器）✅

**功能**：两阶段重排序（RRF 融合 + DashScope Rerank）

**核心方法**：
- `rerank(query, vector_docs, keyword_docs, weights, k)` - 混合检索重排序

**详细文档**：[doc/项目实现过程/04_Reranker实现.md](doc/项目实现过程/04_Reranker实现.md)

---

### 4. RAGService（RAG 统一服务）✅

**功能**：整合 VectorDB、KeywordDB、Reranker，提供统一接口

**核心方法**：
- `add_document(document)` - 添加文档（保证一致性）
- `search(query, mod, k, weights)` - 统一检索接口
- `delete_document(md5)` - 删除文档

**详细文档**：[doc/项目实现过程/05_RAGService实现.md](doc/项目实现过程/05_RAGService实现.md)

---

## 💡 使用示例

### 基本使用

```python
from RAGService import RAGService
from langchain_core.documents import Document

# 1. 初始化服务
rag_service = RAGService(RAG_store_path="./my_rag_db/")

# 2. 添加文档
doc = Document(
    page_content="糖尿病是一种代谢性疾病，主要特征是血糖水平持续升高。",
    metadata={
        "md5": "abc123...",
        "source": "medical_knowledge.pdf"
    }
)
rag_service.add_document(doc)

# 3. 检索（三种模式）
# 向量检索（语义理解）
results = rag_service.search(query="糖尿病的症状", mod="vector", k=5)

# 关键词检索（精确匹配）
results = rag_service.search(query="糖尿病", mod="keyword", k=5)

# 混合检索（推荐）
results = rag_service.search(
    query="糖尿病的治疗方法",
    mod="hybrid",
    k=5,
    vector_weight=0.5,
    keyword_weight=0.5
)

# 4. 查看结果
for doc in results:
    print(f"内容: {doc.page_content}")
    print(f"相关度: {doc.metadata.get('rerank_score', 'N/A')}")
```

### 批量操作

```python
# 批量添加文档
documents = [
    Document(page_content="...", metadata={"md5": "..."}),
    Document(page_content="...", metadata={"md5": "..."}),
    # ...
]
rag_service.add_documents(documents)

# 批量删除文档
md5_list = ["abc123", "def456", "ghi789"]
rag_service.delete_documents(md5_list)
```

### 权重调整

```python
# 偏重语义检索
results = rag_service.search(
    query="糖尿病并发症",
    mod="hybrid",
    k=5,
    vector_weight=0.7,    # 语义权重更高
    keyword_weight=0.3
)

# 偏重精确匹配
results = rag_service.search(
    query="二甲双胍",
    mod="hybrid",
    k=5,
    vector_weight=0.3,
    keyword_weight=0.7    # 关键词权重更高
)
```

---

## 📊 开发进度

### RAG 核心组件（RAG 服务负责人）✅

| 组件 | 状态 | 完成度 | 测试覆盖 |
|------|------|--------|---------|
| 数据加载器 | ✅ 已完成 | 100% | ✅ |
| VectorDB | ✅ 已完成 | 100% | ✅ |
| KeywordDB | ✅ 已完成 | 100% | ✅ |
| Reranker | ✅ 已完成 | 100% | ✅ |
| RAGService | ✅ 已完成 | 100% | ✅ |

**总进度**：5/5 组件完成，测试覆盖率 100%

### 文件存储组件（文件存储负责人）⏸️

| 组件 | 状态 | 负责人 |
|------|------|--------|
| FileStore | ⏸️ 待实现 | 文件存储负责人 |
| Splitter | ⏸️ 待实现 | 文件存储负责人 |
| Deduplicator | ⏸️ 待实现 | 文件存储负责人 |

### 知识库集成（共同完成）⏸️

| 组件 | 状态 | 依赖 |
|------|------|------|
| KnowledgeBase | ⏸️ 待集成 | FileStore + RAGService |

### Web 接口（前端负责人）⏸️

| 组件 | 状态 | 负责人 |
|------|------|--------|
| FastAPI 接口 | ⏸️ 待实现 | 前端负责人 |
| 前端界面 | ⏸️ 待实现 | 前端负责人 |

---

## 📚 文档导航

### 需求与架构
- [需求分析和架构现状](doc/需求分析和架构现状.md) - 项目需求、架构设计、接口规范

### 实现过程文档
- [01_数据加载器实现](doc/项目实现过程/01_数据加载器实现.md)
- [02_VectorDB实现](doc/项目实现过程/02_VectorDB实现.md)
- [03_KeywordDB实现](doc/项目实现过程/03_KeywordDB实现.md)
- [04_Reranker实现](doc/项目实现过程/04_Reranker实现.md)
- [05_RAGService实现](doc/项目实现过程/05_RAGService实现.md)

### 配置文档
- [环境变量配置说明](doc/环境变量配置说明.md)

### 任务清单
- [任务清单00](doc/各进度任务清单/任务清单00.md) - 完整的任务拆解和完成情况

### 进度总结
- [项目开发进度总结01](doc/项目开发进度总结/项目开发进度总结01.md) - 已完成工作的详细总结

---

## 👥 团队分工

### 1. RAG 服务负责人 ✅
**负责组件**：
- ✅ VectorDB（向量数据库）
- ✅ KeywordDB（关键词数据库）
- ✅ Reranker（重排序器）
- ✅ RAGService（RAG 统一服务）
- ✅ 测试数据加载器

**完成情况**：100% 完成，所有组件已实现并测试通过

---

### 2. 文件存储负责人 ⏸️
**负责组件**：
- ⏸️ FileStore（文件存储管理）
- ⏸️ Splitter（文档切分器）
- ⏸️ Deduplicator（文档去重器）

**待解决问题**：
- 支持的文件格式（PDF、DOCX、TXT、Markdown 等）
- 文件类型转换器的实现
- Document 类的接口适配

---

### 3. 前端负责人 ⏸️
**负责组件**：
- ⏸️ main.py（主入口）
- ⏸️ FastAPI 接口
- ⏸️ 前端界面

**技术栈**：FastAPI + 前端框架

---

## 🎯 性能指标

| 检索模式 | 平均响应时间 | 准确率 | 适用场景 |
|---------|------------|--------|---------|
| Vector | ~100ms | 高（语义相关） | 概念查询、模糊搜索 |
| Keyword | ~50ms | 高（精确匹配） | 关键词查询、实体查找 |
| Hybrid | ~300ms | 最高 | 复杂查询、综合检索 |

**测试数据规模**：82,478 条医疗知识三元组

---

## 🔧 技术亮点

1. ✅ **两阶段重排序**：RRF 融合 + DashScope Rerank
2. ✅ **数据一致性保证**：添加失败自动回滚机制
3. ✅ **多级降级策略**：确保服务高可用
4. ✅ **版本兼容性**：支持新旧 LangChain API
5. ✅ **中文优化**：jieba 分词 + 中文嵌入模型

---

## 🐛 已知问题

1. **Windows 文件删除**：Chroma 数据库在 Windows 上可能出现文件占用问题
   - 解决方案：已实现资源释放逻辑，如仍失败可手动删除目录

2. **API 调用限制**：DashScope API 有调用频率限制
   - 解决方案：已实现降级策略，API 失败时自动降级

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

**开发流程**：
1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

---

## 📄 许可证

MIT License

---

## 📮 联系方式

如有问题或建议，欢迎通过以下方式联系：
- 提交 Issue
- 发送邮件

---

**最后更新**：2026-08-11  
**项目状态**：RAG 核心组件开发完成，等待文件存储组件集成
