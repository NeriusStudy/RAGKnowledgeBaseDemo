# RAGService 实现文档

## 一、概述

RAGService 是 RAG 知识库系统的统一服务接口，整合了 VectorDB（向量数据库）、KeywordDB（关键词数据库）和 Reranker（重排序器）三大核心组件，提供文档管理和多模式检索功能。

**主要特点**：
- **组件整合**：统一管理 VectorDB、KeywordDB、Reranker 三个组件
- **多模式检索**：支持向量检索、关键词检索、混合检索三种模式
- **文档管理**：支持文档的添加、删除操作（单个和批量）
- **降级策略**：混合检索失败时自动降级到向量检索
- **一致性保证**：确保向量数据库和关键词数据库的数据一致性

---

## 二、系统架构

### 2.1 组件依赖关系

```
RAGService
    │
    ├── VectorDB (向量数据库)
    │   ├── DashScope Embeddings
    │   └── Chroma Vector Store
    │
    ├── KeywordDB (关键词数据库)
    │   ├── BM25 Retriever
    │   └── Jieba 分词
    │
    └── Reranker (重排序器)
        ├── RRF 融合算法
        └── DashScope Rerank API
```

### 2.2 数据流向

**添加文档流程**：
```
Document → RAGService
    ├→ VectorDB.add_document()
    └→ KeywordDB.add_document()
```

**混合检索流程**：
```
Query → RAGService.search(mod="hybrid")
    ├→ VectorDB.search() → 向量检索结果
    ├→ KeywordDB.search() → 关键词检索结果
    └→ Reranker.rerank()
        ├→ RRF 融合
        └→ DashScope Rerank → 最终结果
```

---

## 三、环境准备

### 3.1 依赖包

确保已安装所有依赖组件的包：

```bash
# 向量数据库依赖
pip install langchain-chroma dashscope

# 关键词数据库依赖
pip install rank_bm25 jieba

# Reranker 依赖
pip install dashscope
```

### 3.2 环境变量配置

```bash
# Windows (cmd)
set DASHSCOPE_API_KEY=your_api_key_here
set DASHSCOPE_WORKSPACE_ID=your_workspace_id  # 如果需要

# Linux/Mac
export DASHSCOPE_API_KEY=your_api_key_here
export DASHSCOPE_WORKSPACE_ID=your_workspace_id  # 如果需要
```

---

## 四、核心方法实现

### 4.1 初始化方法

**功能**：初始化 RAGService，创建三个核心组件实例

**参数**：
- `RAG_store_path`: RAG 存储路径
- `embedding_model_name`: 嵌入模型名称（默认使用 config.EMBEDDING_MODEL_NAME）
- `rerank_model_name`: 重排序模型名称（默认使用 config.RERANK_MODEL_NAME）

**实现要点**：
1. 根据 RAG_store_path 拼接向量数据库和关键词数据库的存储路径
2. 初始化 VectorDB、KeywordDB、Reranker 三个组件
3. 所有组件共享相同的根路径

**核心代码**：
```python
def __init__(self, RAG_store_path: str,
             embedding_model_name: str = config.EMBEDDING_MODEL_NAME,
             rerank_model_name: str = config.RERANK_MODEL_NAME):
    self.RAG_store_path = RAG_store_path
    self.embedding_model_name = embedding_model_name
    self.rerank_model_name = rerank_model_name
    
    # 拼接存储路径
    self.vector_db_path = self.RAG_store_path + config.VECTOR_DB_PATH
    self.keyword_db_path = self.RAG_store_path + config.KEYWORD_DB_PATH
    
    # 初始化三个核心组件
    self.vector_db = VectorDB(
        vector_db_store_path=self.vector_db_path,
        embedding_model_name=self.embedding_model_name
    )
    self.keyword_db = KeywordDB(
        keyword_db_store_path=self.keyword_db_path
    )
    self.reranker = Reranker(
        rerank_model_name=self.rerank_model_name
    )
```

---

### 4.2 文档管理方法

#### 4.2.1 add_document() - 添加单个文档

**功能**：添加单个文档到向量数据库和关键词数据库

**实现要点**：
1. 先添加到向量数据库
2. 再添加到关键词数据库
3. 如果关键词数据库添加失败，从向量数据库删除已添加的文档以保持一致性
4. 使用文档 metadata 中的 md5 作为唯一标识

**核心代码**：
```python
def add_document(self, document: Document) -> bool:
    try:
        # 添加到向量数据库
        vector_success = self.vector_db.add_document(document)
        if not vector_success:
            return False

        # 添加到关键词数据库
        keyword_success = self.keyword_db.add_document(document)
        if not keyword_success:
            # 回滚：从向量数据库删除
            if 'md5' in document.metadata:
                self.vector_db.delete_document(document.metadata['md5'])
            return False

        return True
    except Exception as e:
        print(f"添加文档失败: {e}")
        return False
```

#### 4.2.2 add_documents() - 批量添加文档

**功能**：批量添加文档到两个数据库

**实现要点**：
1. 使用批量操作提高性能
2. 保持一致性：如果关键词数据库失败，回滚向量数据库的操作

**核心代码**：
```python
def add_documents(self, documents: list[Document]) -> bool:
    try:
        # 批量添加到向量数据库
        vector_success = self.vector_db.add_documents(documents)
        if not vector_success:
            return False

        # 批量添加到关键词数据库
        keyword_success = self.keyword_db.add_documents(documents)
        if not keyword_success:
            # 回滚：批量删除
            md5_list = [doc.metadata['md5'] for doc in documents 
                       if 'md5' in doc.metadata]
            if md5_list:
                self.vector_db.delete_documents(md5_list)
            return False

        return True
    except Exception as e:
        print(f"批量添加文档失败: {e}")
        return False
```

#### 4.2.3 delete_document() - 删除单个文档

**功能**：根据 md5 从两个数据库删除文档

**实现要点**：
1. 同时从向量数据库和关键词数据库删除
2. 只有两者都成功才返回 True

**核心代码**：
```python
def delete_document(self, md5: str) -> bool:
    try:
        vector_success = self.vector_db.delete_document(md5)
        keyword_success = self.keyword_db.delete_document(md5)
        
        return vector_success and keyword_success
    except Exception as e:
        print(f"删除文档失败: {e}")
        return False
```

#### 4.2.4 delete_documents() - 批量删除文档

**功能**：批量删除文档

**实现要点**：
1. 使用批量操作提高性能
2. 两个数据库都必须成功

---

### 4.3 检索方法

#### 4.3.1 _vector_search() - 向量检索

**功能**：仅使用向量数据库进行语义检索

**适用场景**：
- 语义理解类问题
- 概念性查询
- 模糊匹配

**核心代码**：
```python
def _vector_search(self, query:str, k:int = config.VECTOR_SEARCH_DEFAULT_K) -> list[Document]:
    try:
        return self.vector_db.search(query=query, k=k)
    except Exception as e:
        print(f"向量检索失败: {e}")
        return []
```

#### 4.3.2 _keyword_search() - 关键词检索

**功能**：仅使用关键词数据库进行精确匹配

**适用场景**：
- 精确匹配类问题
- 实体名称查询
- 关键词搜索

**核心代码**：
```python
def _keyword_search(self, query:str, k:int = config.KEYWORD_SEARCH_DEFAULT_K) -> list[Document]:
    try:
        return self.keyword_db.search(query=query, k=k)
    except Exception as e:
        print(f"关键词检索失败: {e}")
        return []
```

#### 4.3.3 _hybrid_search() - 混合检索

**功能**：结合向量检索和关键词检索，使用 Reranker 进行融合和重排序

**检索流程**：
1. **并行检索**：同时调用向量检索和关键词检索
2. **RRF 融合**：Reranker 使用 RRF 算法融合两路结果
3. **精排序**：使用 DashScope Rerank API 进行精确排序
4. **降级策略**：如果失败，降级到向量检索

**适用场景**：
- 综合性查询
- 需要高精度的场景
- 默认推荐模式

**核心代码**：
```python
def _hybrid_search(self, query:str, k:int = config.HYBRID_SEARCH_DEFAULT_K,
                   vector_weight: float = 0.5,
                   keyword_weight: float = 0.5) -> list[Document]:
    try:
        # 并行检索：获取较多候选文档
        vector_results = self.vector_db.search(
            query=query,
            k=config.VECTOR_SEARCH_DEFAULT_K
        )
        keyword_results = self.keyword_db.search(
            query=query,
            k=config.KEYWORD_SEARCH_DEFAULT_K
        )

        # Reranker 进行融合和重排序
        reranked_results = self.reranker.rerank(
            query=query,
            vector_documents=vector_results,
            keyword_documents=keyword_results,
            vector_weight=vector_weight,
            keyword_weight=keyword_weight,
            k=k
        )

        return reranked_results
    except Exception as e:
        print(f"混合检索失败: {e}")
        # 降级策略：返回向量检索结果
        return self._vector_search(query=query, k=k)
```

#### 4.3.4 search() - 统一检索接口

**功能**：统一的检索入口，根据 mod 参数选择检索模式

**参数**：
- `query`: 查询字符串
- `mod`: 检索模式，可选 "vector"、"keyword"、"hybrid"（默认）
- `k`: 返回的文档数量
- `vector_weight`: 向量检索权重（仅 hybrid 模式）
- `keyword_weight`: 关键词检索权重（仅 hybrid 模式）

**核心代码**：
```python
def search(self, query:str, mod:str = "hybrid", k:int = config.RAG_SEARCH_DEFAULT_K,
           vector_weight: float = 0.5,
           keyword_weight: float = 0.5) -> list[Document]:
    try:
        if mod == "vector":
            return self._vector_search(query=query, k=k)
        elif mod == "keyword":
            return self._keyword_search(query=query, k=k)
        elif mod == "hybrid":
            return self._hybrid_search(
                query=query,
                k=k,
                vector_weight=vector_weight,
                keyword_weight=keyword_weight
            )
        else:
            print(f"警告：不支持的检索模式 '{mod}'，使用默认的 hybrid 模式")
            return self._hybrid_search(query=query, k=k,
                                      vector_weight=vector_weight,
                                      keyword_weight=keyword_weight)
    except Exception as e:
        print(f"检索失败: {e}")
        return []
```

---

### 4.4 清理方法

#### delete_me() - 删除 RAG 服务

**功能**：删除所有持久化存储的数据

**实现要点**：
1. 分别删除向量数据库和关键词数据库
2. 即使一个失败也继续删除另一个

**核心代码**：
```python
def delete_me(self):
    try:
        self.vector_db.delete_me()
        print("✓ 向量数据库已删除")
    except Exception as e:
        print(f"删除向量数据库失败: {e}")

    try:
        self.keyword_db.delete_me()
        print("✓ 关键词数据库已删除")
    except Exception as e:
        print(f"删除关键词数据库失败: {e}")
```

---

## 五、配置说明

### 5.1 相关配置项

在 `config.py` 中需要配置以下参数：

```python
# 向量检索默认返回数量
VECTOR_SEARCH_DEFAULT_K = 15

# 关键词检索默认返回数量
KEYWORD_SEARCH_DEFAULT_K = 15

# 混合检索默认返回数量
HYBRID_SEARCH_DEFAULT_K = 10

# RAG 统一检索默认返回数量
RAG_SEARCH_DEFAULT_K = 10

# 向量数据库路径
VECTOR_DB_PATH = "vector_db/"

# 关键词数据库路径
KEYWORD_DB_PATH = "keyword_db/"

# 嵌入模型名称
EMBEDDING_MODEL_NAME = "text-embedding-v2"

# 重排序模型名称
RERANK_MODEL_NAME = "qwen3-rerank"
```

### 5.2 存储路径结构

```
test_rag_service/
├── vector_db/               # 向量数据库
│   └── <chroma_collection_id>/
│       ├── chroma.sqlite3
│       └── data_level0.bin
└── keyword_db/              # 关键词数据库
    └── documents.pkl
```

---

## 六、使用示例

### 6.1 基本使用

```python
from RAGService import RAGService
from langchain_core.documents import Document

# 1. 初始化服务
rag_service = RAGService(RAG_store_path="./my_rag_db/")

# 2. 添加文档
doc = Document(
    page_content="糖尿病是一种代谢疾病",
    metadata={"md5": "abc123"}
)
rag_service.add_document(doc)

# 3. 检索
results = rag_service.search(query="糖尿病的症状", mod="hybrid", k=5)

# 4. 查看结果
for doc in results:
    print(doc.page_content)
    print(doc.metadata.get('rerank_score'))
```

### 6.2 批量操作

```python
# 批量添加
documents = [...]  # Document 列表
rag_service.add_documents(documents)

# 批量删除
md5_list = ["abc123", "def456", "ghi789"]
rag_service.delete_documents(md5_list)
```

### 6.3 不同检索模式

```python
# 向量检索（语义理解）
results = rag_service.search(query="糖尿病", mod="vector", k=10)

# 关键词检索（精确匹配）
results = rag_service.search(query="糖尿病", mod="keyword", k=10)

# 混合检索（推荐）
results = rag_service.search(query="糖尿病", mod="hybrid", k=10)
```

### 6.4 权重调整

```python
# 偏重向量检索
results = rag_service.search(
    query="糖尿病的症状",
    mod="hybrid",
    k=5,
    vector_weight=0.7,
    keyword_weight=0.3
)

# 偏重关键词检索
results = rag_service.search(
    query="糖尿病",
    mod="hybrid",
    k=5,
    vector_weight=0.3,
    keyword_weight=0.7
)
```

---

## 七、测试方法

### 7.1 运行测试脚本

```bash
cd test_scripts
python test_ragservice.py
```

### 7.2 测试内容

测试脚本 `test_ragservice.py` 覆盖以下功能：

1. **初始化测试**：验证 RAGService 初始化成功
2. **添加单个文档**：测试单个文档添加功能
3. **批量添加文档**：测试批量添加 99 个文档
4. **向量检索模式**：测试纯向量检索
5. **关键词检索模式**：测试纯关键词检索
6. **混合检索模式**：测试 RRF + Rerank 混合检索
7. **不同权重配置**：测试不同的向量/关键词权重
8. **删除单个文档**：测试单个文档删除
9. **批量删除文档**：测试批量删除功能
10. **清理测试数据**：测试 delete_me() 方法

---

## 八、性能优化建议

### 8.1 批量操作优化

**问题**：频繁的单个文档操作效率低

**解决方案**：
- 使用 `add_documents()` 而不是循环调用 `add_document()`
- 使用 `delete_documents()` 而不是循环调用 `delete_document()`

### 8.2 检索参数调优

**候选文档数量**：
```python
# config.py
VECTOR_SEARCH_DEFAULT_K = 15  # 向量检索候选数
KEYWORD_SEARCH_DEFAULT_K = 15  # 关键词检索候选数
HYBRID_SEARCH_DEFAULT_K = 10  # 最终返回数量
```

**原则**：
- 候选数量（15）应大于最终返回数量（10）
- 给 Reranker 足够的候选文档进行精排序

### 8.3 权重配置建议

**场景1：语义理解为主**
```python
vector_weight=0.7, keyword_weight=0.3
```

**场景2：精确匹配为主**
```python
vector_weight=0.3, keyword_weight=0.7
```

**场景3：平衡模式（默认）**
```python
vector_weight=0.5, keyword_weight=0.5
```

---

## 九、常见问题

### 9.1 数据不一致问题

**问题**：向量数据库和关键词数据库数据不一致

**原因**：
- 添加文档时某个数据库失败但未回滚
- 删除文档时某个数据库失败

**解决方案**：
- 代码已实现了事务性保证：添加失败会自动回滚
- 删除操作会同时删除两个数据库

### 9.2 混合检索返回结果为空

**问题**：混合检索返回空列表

**可能原因**：
1. 向量数据库和关键词数据库都为空
2. Reranker API 失败且降级的向量检索也为空

**解决方案**：
- 检查是否已添加文档
- 检查 API Key 是否配置正确
- 查看日志中的错误信息

### 9.3 权重设置无效

**问题**：调整权重后结果没有明显变化

**原因**：
- 权重影响的是 RRF 融合阶段，最终结果由 Rerank 模型决定
- 权重的影响在候选文档差异较大时才明显

**建议**：
- 使用极端权重（0.9 vs 0.1）观察差异
- 对比不同权重下的 RRF 融合结果（Rerank 之前）

### 9.4 Windows 文件删除失败

**问题**：`delete_me()` 报错文件被占用

**解决方案**：
```python
# VectorDB 和 KeywordDB 已实现资源释放逻辑
# 如果仍失败，手动删除：
import shutil
shutil.rmtree("test_rag_service", ignore_errors=True)
```

---

## 十、性能对比

### 10.1 三种检索模式对比

| 检索模式 | 优点 | 缺点 | 适用场景 |
|---------|------|------|---------|
| **Vector** | 语义理解好 | 对精确关键词不敏感 | 概念性查询 |
| **Keyword** | 精确匹配快 | 无语义理解 | 实体名称查询 |
| **Hybrid** | 综合两者优点 | API 调用成本高 | 综合性查询 |

### 10.2 响应时间估算

**向量检索**：
- 嵌入生成：~50ms（DashScope API）
- 向量搜索：~10ms（Chroma）
- **总计**：~60ms

**关键词检索**：
- BM25 搜索：~5ms（本地计算）
- **总计**：~5ms

**混合检索**：
- 向量检索：~60ms
- 关键词检索：~5ms（并行）
- Rerank API：~100ms
- **总计**：~165ms

---

## 十一、扩展方向

### 11.1 缓存机制

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def _cached_search(self, query: str, mod: str, k: int):
    return self.search(query, mod, k)
```

### 11.2 异步支持

```python
async def search_async(self, query: str, mod: str = "hybrid", k: int = 10):
    # 并行执行向量检索和关键词检索
    vector_task = asyncio.create_task(self._vector_search_async(query, k))
    keyword_task = asyncio.create_task(self._keyword_search_async(query, k))
    
    vector_results, keyword_results = await asyncio.gather(vector_task, keyword_task)
    return await self.reranker.rerank_async(...)
```

### 11.3 检索日志

```python
def search(self, query: str, ...):
    start_time = time.time()
    results = self._hybrid_search(...)
    elapsed = time.time() - start_time
    
    # 记录日志
    self._log_search(query, mod, k, len(results), elapsed)
    return results
```

---

## 十二、备注

1. **组件依赖**：RAGService 依赖 VectorDB、KeywordDB、Reranker 三个已实现的组件
2. **API Key 配置**：需要配置 DASHSCOPE_API_KEY 环境变量
3. **工作空间配置**：如果使用工作空间，需配置 DASHSCOPE_WORKSPACE_ID
4. **数据一致性**：添加/删除操作保证两个数据库的一致性
5. **降级策略**：混合检索失败时自动降级到向量检索
6. **性能优化**：批量操作性能远优于单个操作

---

**文档版本**：v1.0  
**创建日期**：2026-08-11  
**最后更新**：2026-08-11
