# RAG 知识库管理系统

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3.13-green.svg)](https://github.com/langchain-ai/langchain)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> 基于 LangChain 的完整 RAG（检索增强生成）知识库管理系统，支持文件管理、文档切分和多模态检索

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

本项目实现了一个完整的 RAG（Retrieval-Augmented Generation）知识库管理系统，支持文件管理、文档切分、多模态检索（向量检索、关键词检索、混合检索），为 AI 应用提供完整的知识库管理和检索服务。

**设计目标**：
- 📚 支持多种文件格式的知识库构建（TXT、MD、JSON、CSV等）
- 🔍 提供多种检索模式（向量、关键词、混合）
- 🎯 高精度的语义检索和重排序
- 🚀 易于集成的统一服务接口
- 📊 完整的文件管理和文档切分能力
- ✅ 已构建 6 个企业知识库，包含 242 个文件、3116 个文档

---

## ✨ 核心特性

### 🔍 多模态检索
- **向量检索**：基于 DashScope text-embedding-v2 模型的语义检索
- **关键词检索**：基于 BM25 算法的精确匹配，支持中文分词（jieba）
- **混合检索**：RRF 融合 + DashScope Rerank 精排序（推荐）

### 📁 文件管理
- **多格式支持**：TXT、MD、JSON、CSV 等文本文件
- **文件去重**：基于 MD5 的文件名去重机制
- **文档切分**：RecursiveCharacterTextSplitter（chunk_size=500, overlap=50）
- **文件-文档映射**：完整的映射关系维护
- **级联删除**：删除文件时自动清理相关文档

### 📊 数据管理
- 文档增删操作（单个和批量）
- 数据一致性保证（事务性回滚机制）
- 基于 MD5 的文档去重
- 持久化存储（Chroma + Pickle + JSON）
- 文档 JSON 存储（便于查看和调试）

### 🎯 高可用性
- 多级降级策略（Rerank → RRF → Vector）
- 完整的异常处理
- 版本兼容性保证

### 🛠️ 易于使用
- 统一的 LangChain Document 接口
- 灵活的权重配置
- 完整的测试覆盖（100%）
- 详细的实现文档

---

## 🛠️ 技术栈

| 类别 | 技术 |
|------|------|
| **框架** | LangChain 0.3.13 |
| **向量数据库** | Chroma 0.5.23 |
| **嵌入模型** | DashScope text-embedding-v2 |
| **重排序模型** | DashScope qwen3-rerank |
| **关键词检索** | BM25 + jieba |
| **文件加载** | UnstructuredFileLoader |
| **文档切分** | RecursiveCharacterTextSplitter |
| **编程语言** | Python 3.8+ |

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────┐
│         KnowledgeBase（知识库）✅            │
│         （统一知识库管理接口）                │
├─────────────────┬───────────────────────────┤
│   FileStore ✅  │      RAGService ✅         │
│  （文件存储）    │    （RAG 服务）            │
├─────────────────┼───────────────────────────┤
│  - Deduplicator✅│  - VectorDB ✅            │
│  - Splitter ✅   │  - KeywordDB ✅           │
│  - FileLoader ✅ │  - Reranker ✅            │
└─────────────────┴───────────────────────────┘
```

### 完整架构说明

```
┌──────────────────────────────────────────────┐
│              KnowledgeBase ✅                 │
│         (统一知识库管理接口)                   │
└──────────┬─────────────────────────┬─────────┘
           │                         │
    ┌──────▼──────────┐      ┌──────▼──────────┐
    │   FileStore ✅   │      │  RAGService ✅   │
    │  (文件管理层)     │      │  (检索服务层)     │
    └──────┬──────────┘      └──────┬──────────┘
           │                         │
    ┌──────▼────┬────────┐   ┌──────▼──────────────────┐
    │Deduplicator│Splitter│   │VectorDB│KeywordDB│Reranker│
    │   ✅       │  ✅    │   │  ✅    │   ✅    │  ✅   │
    └───────────┴────────┘   └─────────────────────────┘
           │                         │
    ┌──────▼──────┐          ┌──────▼──────────────────┐
    │   MD5 去重   │          │ Chroma + DashScope      │
    │文件名/文档内容│          │ BM25 + jieba           │
    │             │          │ RRF + Rerank           │
    └─────────────┘          └────────────────────────┘
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

# 单组件测试
python test_vectordb.py       # 向量数据库
python test_keyworddb.py      # 关键词数据库
python test_reranker.py       # 重排序器
python test_ragservice.py     # RAG 服务
python test_deduplicator.py   # 去重器
python test_splitter.py       # 文档切分器
python test_filestore.py      # 文件存储

# 集成测试
python test_integration.py    # 完整流程测试
```

### 4. 构建知识库

```bash
# 返回项目根目录
cd ..

# 构建完整知识库（6个企业，242文件，3116文档）
python build_complete_knowledge_base.py
```

### 5. 评估性能

```bash
# QA 性能评估（20个测试问题）
python evaluate_qa_performance.py
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

### 5. Deduplicator（去重器）✅

**功能**：基于 MD5 的去重检测

**核心方法**：
- `str_to_md5(text)` - 字符串转 MD5（静态方法）
- `document_to_md5(document)` - 文档转 MD5（静态方法）
- `check_duplicate(text)` - 检查是否重复
- `save_str(text)` - 保存字符串 MD5

**详细文档**：[doc/项目实现过程/06_Deduplicator实现.md](doc/项目实现过程/06_Deduplicator实现.md)

---

### 6. Splitter（文档切分器）✅

**功能**：将长文档切分为小块，便于检索

**核心方法**：
- `split_document(document)` - 切分单个文档
- `split_documents(documents)` - 批量切分文档

**配置**：chunk_size=500, chunk_overlap=50

**详细文档**：[doc/项目实现过程/07_Splitter实现.md](doc/项目实现过程/07_Splitter实现.md)

---

### 7. FileStore（文件存储）✅

**功能**：文件存储、切分、去重和映射管理

**核心方法**：
- `save_file(file_path)` - 保存文件并切分
- `delete_file(filename)` - 删除文件及文档
- `get_all_files()` - 获取所有文件
- `get_documents_by_file(filename)` - 获取文件的文档块

**详细文档**：[doc/项目实现过程/08_FileStore实现.md](doc/项目实现过程/08_FileStore实现.md)

---

### 8. KnowledgeBase（知识库管理）✅

**功能**：应用层集成组件，提供完整的知识库管理服务

**核心方法**：
- `add_file(file_path)` - 添加单个文件
- `add_files(file_paths)` - 批量添加文件
- `delete_file(filename)` - 删除文件
- `search(query, mode, k)` - 统一检索接口
- `get_statistics()` - 获取统计信息

**详细文档**：[doc/项目实现过程/09_KnowledgeBase实现.md](doc/项目实现过程/09_KnowledgeBase实现.md)

---

## 💡 使用示例

### 基本使用（KnowledgeBase）

```python
from KnowledgeBase import KnowledgeBase

# 1. 初始化知识库
kb = KnowledgeBase(
    kb_name="my_knowledge_base",
    kb_path="./data/knowledge/my_kb",
    chunk_size=500,
    chunk_overlap=50
)

# 2. 添加文件
result = kb.add_file("./documents/medical_guide.txt")
print(f"添加成功: {result['success']}, 文档数: {result['document_count']}")

# 3. 批量添加文件
file_list = [
    "./documents/doc1.txt",
    "./documents/doc2.md",
    "./documents/doc3.json"
]
result = kb.add_files(file_list)
print(f"成功: {result['success']}/{result['total']}, 总文档: {result['total_documents']}")

# 4. 检索（三种模式）
# 向量检索（语义理解）
results = kb.search(query="糖尿病的症状", mode="vector", k=5)

# 关键词检索（精确匹配）
results = kb.search(query="糖尿病", mode="keyword", k=5)

# 混合检索（推荐）
results = kb.search(
    query="糖尿病的治疗方法",
    mode="hybrid",
    k=5,
    vector_weight=0.5,
    keyword_weight=0.5
)

# 5. 查看结果
for doc in results:
    print(f"内容: {doc.page_content}")
    print(f"来源: {doc.metadata.get('source', 'N/A')}")
    print(f"相关度: {doc.metadata.get('rerank_score', 'N/A')}")

# 6. 查看统计信息
stats = kb.get_statistics()
print(f"知识库: {stats['kb_name']}")
print(f"文件数: {stats['total_files']}")
print(f"文档数: {stats['total_documents']}")

# 7. 删除文件
result = kb.delete_file("medical_guide.txt")
print(f"删除成功: {result['success']}, 删除文档数: {result['deleted_documents']}")
```

### 高级使用（RAGService）

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
results = kb.search(
    query="糖尿病并发症",
    mode="hybrid",
    k=5,
    vector_weight=0.7,    # 语义权重更高
    keyword_weight=0.3
)

# 偏重精确匹配
results = kb.search(
    query="二甲双胍",
    mode="hybrid",
    k=5,
    vector_weight=0.3,
    keyword_weight=0.7    # 关键词权重更高
)
```

---

## 📊 开发进度

### 后端核心功能 ✅ 100%

| 模块 | 组件 | 状态 | 测试覆盖 |
|------|------|------|---------|
| **RAG 服务** | VectorDB | ✅ 已完成 | ✅ 100% |
| | KeywordDB | ✅ 已完成 | ✅ 100% |
| | Reranker | ✅ 已完成 | ✅ 100% |
| | RAGService | ✅ 已完成 | ✅ 100% |
| **文件存储** | Deduplicator | ✅ 已完成 | ✅ 100% |
| | Splitter | ✅ 已完成 | ✅ 100% |
| | FileStore | ✅ 已完成 | ✅ 100% |
| **应用层** | KnowledgeBase | ✅ 已完成 | ✅ 100% |

**总进度**：8/8 组件完成，测试覆盖率 100%

### 测试和评估 ✅ 100%

| 测试项目 | 状态 | 说明 |
|---------|------|------|
| 单组件测试 | ✅ 完成 | 8个组件全部测试通过 |
| 集成测试 | ✅ 完成 | 完整流程测试通过 |
| 大规模构建 | ✅ 完成 | 6个企业知识库，242文件，3116文档 |
| QA性能评估 | ✅ 完成 | Precision 28.58%, Recall 75.00%, F1 38.33% |

### 文档编写 ✅ 100%

| 文档类型 | 数量 | 状态 |
|---------|------|------|
| 实现过程文档 | 9篇 | ✅ 完成 |
| 测试评估文档 | 3篇 | ✅ 完成 |
| 配置说明文档 | 2篇 | ✅ 完成 |
| 进度总结文档 | 1篇 | ✅ 完成 |

### Web 接口 ⏸️ 0%

| 组件 | 状态 | 负责人 |
|------|------|--------|
| FastAPI 接口 | ⏸️ 待实现 | 前端负责人 |
| 前端界面 | ⏸️ 待实现 | 前端负责人 |

**项目当前状态**：后端核心功能开发完成，等待 API 和前端开发

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
- [06_Deduplicator实现](doc/项目实现过程/06_Deduplicator实现.md)
- [07_Splitter实现](doc/项目实现过程/07_Splitter实现.md)
- [08_FileStore实现](doc/项目实现过程/08_FileStore实现.md)
- [09_KnowledgeBase实现](doc/项目实现过程/09_KnowledgeBase实现.md)

### 测试和评估文档
- [完整知识库构建说明](doc/测试和评估/完整知识库构建说明.md) - 6个企业知识库构建过程
- [QA性能评估报告](doc/测试和评估/QA性能评估报告.md) - 检索性能评估和分析
- [RAG-Multi-Corpus数据集说明](doc/测试和评估/RAG-Multi-Corpus数据集说明.md) - 测试数据集详细说明

### 配置文档
- [环境变量配置说明](doc/环境变量配置说明.md)

### 任务清单
- [任务清单00](doc/各进度任务清单/任务清单00.md) - 完整的任务拆解和完成情况

### 进度总结
- [项目开发进度总结01](doc/项目开发进度总结/项目开发进度总结01.md) - 后端核心功能开发总结

---

## 👥 项目成果

### 代码实现
- ✅ 9 个核心组件类
- ✅ 13 个测试脚本
- ✅ 2 个构建/评估脚本
- ✅ 约 2500+ 行 Python 代码

### 文档产出
- ✅ 9 个实现过程文档
- ✅ 3 个测试评估文档
- ✅ 2 个配置说明文档
- ✅ 1 个进度总结文档

### 数据集构建
- ✅ 6 个企业知识库（汽车、教育、航空、科技、金融）
- ✅ 242 个文件（TXT、MD、JSON、CSV）
- ✅ 3116 个文档块
- ✅ 1302 个 QA 测试对

### 性能表现
- ✅ 测试覆盖率：100%
- ✅ 知识库构建成功率：97.6%
- ✅ QA 评估 Recall：75.00%
- ✅ 检索响应时间：50-300ms

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

**最后更新**：2026-08-15  
**项目状态**：后端核心功能开发完成（100%），等待 API 和前端开发
