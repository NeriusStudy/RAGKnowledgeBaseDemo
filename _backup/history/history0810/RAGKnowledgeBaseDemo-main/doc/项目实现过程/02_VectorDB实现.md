# 步骤02：VectorDB 向量数据库实现

**完成时间**：2026-08-10  
**负责模块**：RAG服务 - 向量数据库  
**状态**：✅ 已完成

---

## 一、实现目标

实现基于 Chroma + DashScopeEmbeddings 的向量数据库（VectorDB），提供文档的向量化存储、相似度检索和增删管理功能，为 RAGService 混合检索提供语义检索能力。

---

## 二、核心功能需求回顾

根据 `doc/需求分析和架构现状.md` 中的定义：

### 2.1 功能需求
- **输入**：Document 类或 Document 列表（已切分好的文档）
- **存储索引**：Document.metadata 中的 md5 作为唯一标识
- **核心功能**：
  1. 向量存储：将文档转换为向量并持久化存储
  2. 向量检索：基于语义相似度检索文档，可自定义检索数量 k
  3. 文档增删：支持单个和批量操作

### 2.2 技术实现
- **嵌入模型**：DashScopeEmbeddings（阿里云百炼）
- **模型名称**：text-embedding-2
- **持久化方案**：Chroma 本地存储
- **相似度算法**：余弦相似度（Chroma 内置）

---

## 三、实现内容

### 3.1 已实现的方法

#### ✅ 初始化相关（已有）
```python
__init__(vector_db_store_path, embedding_model_name)
get_embedding_model_name() -> str
str_to_vector(text: str) -> list[float]
document_to_vector(document: Document) -> list[float]
```

#### ✅ 文档添加（新实现）
```python
add_document(document: Document) -> bool
add_documents(documents: list[Document]) -> bool
```

#### ✅ 文档删除（新实现）
```python
delete_document(md5: str) -> bool
delete_documents(md5_list: list[str]) -> bool
```

#### ✅ 向量检索（新实现）
```python
search(query: str, k: int) -> list[Document]
```

#### ✅ 数据库清理（新实现）
```python
delete_me() -> None
```

---

## 四、详细实现说明

### 4.1 add_document() - 添加单个文档

**功能**：将单个 Document 添加到向量数据库

**实现要点**：
1. **MD5 校验**：检查 document.metadata 中是否包含 'md5' 字段
2. **ID 映射**：使用 md5 作为 Chroma 的文档 ID
3. **向量化**：Chroma 自动调用 embedding_function 进行向量化
4. **持久化**：Chroma 自动持久化到指定目录

**核心代码**：
```python
md5 = document.metadata['md5']
self.vector_db.add_documents(
    documents=[document],
    ids=[md5]
)
```

**关键设计**：
- 使用 md5 作为 Chroma ID，确保文档唯一性
- Chroma 内部会自动处理向量化和存储
- 返回 bool 表示操作成功与否

---

### 4.2 add_documents() - 批量添加文档

**功能**：批量添加多个 Document 到向量数据库

**实现要点**：
1. **空列表处理**：如果列表为空，直接返回 True
2. **批量校验**：遍历所有文档检查 md5 字段
3. **批量操作**：一次性提交所有文档，提高效率
4. **ID 列表**：提取所有 md5 组成 ID 列表

**核心代码**：
```python
md5_list = [doc.metadata['md5'] for doc in documents]
self.vector_db.add_documents(
    documents=documents,
    ids=md5_list
)
```

**性能优化**：
- 批量操作比单个添加效率高
- Chroma 内部会批量处理向量化
- 适合大规模文档导入

---

### 4.3 delete_document() - 删除单个文档

**功能**：根据 md5 删除指定文档

**实现要点**：
1. **直接删除**：使用 md5 作为 ID 直接调用 Chroma 删除接口
2. **无需查询**：不需要先查询文档是否存在
3. **异常处理**：捕获删除异常并返回失败状态

**核心代码**：
```python
self.vector_db.delete(ids=[md5])
```

**设计说明**：
- Chroma 的 delete 方法支持 ID 列表
- 如果 ID 不存在，Chroma 不会报错
- 简单高效，无额外查询开销

---

### 4.4 delete_documents() - 批量删除文档

**功能**：批量删除多个文档

**实现要点**：
1. **空列表检查**：如果列表为空，直接返回 True
2. **批量删除**：一次性删除所有指定的文档
3. **ID 列表传递**：直接使用 md5 列表作为 ID 列表

**核心代码**：
```python
self.vector_db.delete(ids=md5_list)
```

**使用场景**：
- 删除某个文件对应的所有文档切片
- 批量清理过期文档
- 知识库更新时的批量替换

---

### 4.5 search() - 向量相似度检索

**功能**：基于查询字符串进行语义相似度检索

**实现要点**：
1. **查询向量化**：Chroma 自动将 query 转换为向量
2. **相似度计算**：使用余弦相似度计算相似度
3. **Top-K 返回**：返回相似度最高的 k 个文档
4. **失败处理**：异常时返回空列表

**核心代码**：
```python
results = self.vector_db.similarity_search(
    query=query,
    k=k
)
```

**检索特点**：
- **语义理解**：能理解同义词、近义词
- **上下文感知**：考虑词语在句子中的上下文
- **多语言支持**：支持中文和英文混合查询

**示例**：
```python
# 查询："人参的副作用"
# 能匹配到：
#   - "人参茎叶总皂苷胶囊 不良反应 头痛"
#   - "人参有什么不良反应"
#   - "服用人参可能导致的问题"
```

---

### 4.6 delete_me() - 删除整个数据库

**功能**：删除向量数据库的所有持久化存储文件

**实现要点**：
1. **目录删除**：使用 shutil.rmtree 删除整个存储目录
2. **路径检查**：先检查目录是否存在
3. **彻底清理**：删除所有向量、索引和元数据文件

**核心代码**：
```python
db_path = Path(self.vector_db_store_path)
if db_path.exists():
    shutil.rmtree(db_path)
```

**使用场景**：
- 知识库删除
- 测试环境清理
- 重建索引前的清理

---

## 五、技术要点

### 5.1 Chroma 的 ID 管理

**设计决策**：使用 md5 作为 Chroma 的文档 ID

**优点**：
1. **唯一性**：md5 确保文档唯一标识
2. **直接映射**：md5 → Chroma ID，无需额外映射表
3. **简化删除**：根据 md5 直接删除，无需查询
4. **去重天然**：相同 md5 的文档会自动覆盖（Chroma 行为）

**Chroma ID 机制**：
```python
# 添加文档时指定 ID
vectordb.add_documents(
    documents=[doc1, doc2],
    ids=['md5_1', 'md5_2']
)

# 删除时使用相同的 ID
vectordb.delete(ids=['md5_1'])
```

---

### 5.2 嵌入模型配置

#### 5.2.1 当前使用的模型：DashScope text-embedding-2

**模型信息**：
- **提供商**：阿里云百炼（DashScope）
- **模型名称**：text-embedding-2
- **向量维度**：1536 维（标准维度）
- **支持语言**：中文、英文
- **最大输入**：约 8000 tokens
- **费用**：免费额度每月 100 万 tokens

**API 调用流程**：
```
用户查询 "人参的副作用"
    ↓
DashScopeEmbeddings.embed_query()
    ↓
调用阿里云 API
    ↓
返回 1536 维向量 [0.123, -0.456, ...]
    ↓
Chroma 进行相似度计算
    ↓
返回最相似的文档
```

**环境变量配置**：
```python
# 必须设置
os.environ['DASHSCOPE_API_KEY'] = 'your_api_key'
```

**获取 API Key**：
1. 访问：https://dashscope.console.aliyun.com/
2. 注册/登录阿里云账号
3. 开通百炼服务（有免费额度）
4. 在控制台获取 API Key

---

#### 5.2.2 如何更换嵌入模型

如果需要更换嵌入模型（例如使用 OpenAI、本地模型等），按照以下步骤操作：

**方案1：使用 OpenAI 嵌入模型**

**优点**：效果最好，稳定性高  
**缺点**：需要付费，需要外网访问  
**适用场景**：生产环境，预算充足

**步骤**：

1. 安装依赖：
```bash
pip install langchain-openai
```

2. 修改 `config.py`：
```python
# 原配置
EMBEDDING_MODEL_NAME = "text-embedding-2"

# 改为
EMBEDDING_MODEL_NAME = "text-embedding-3-small"  # 或 text-embedding-3-large
```

3. 修改 `VectorDB.py` 的第 12 行导入：
```python
# 原代码
from langchain_community.embeddings import DashScopeEmbeddings

# 改为
from langchain_openai import OpenAIEmbeddings
```

4. 修改 `VectorDB.py` 的第 30-32 行初始化：
```python
# 原代码
self.embedding_mode = DashScopeEmbeddings(
    model=self.embedding_model_name
)

# 改为
self.embedding_mode = OpenAIEmbeddings(
    model=self.embedding_model_name,
    openai_api_key=os.environ.get('OPENAI_API_KEY')
)
```

5. 设置环境变量：
```bash
# Windows
set OPENAI_API_KEY=sk-your_openai_key

# Linux/Mac
export OPENAI_API_KEY=sk-your_openai_key
```

---

**方案2：使用本地开源模型（HuggingFace）**

**优点**：完全免费，无调用限制，数据隐私好  
**缺点**：需要 GPU，首次加载较慢  
**适用场景**：大规模生产，有 GPU 服务器

**步骤**：

1. 安装依赖：
```bash
pip install sentence-transformers
```

2. 修改 `config.py`：
```python
# 改为本地模型名称
EMBEDDING_MODEL_NAME = "BAAI/bge-large-zh-v1.5"  # 中文效果好
# 或使用多语言模型
# EMBEDDING_MODEL_NAME = "BAAI/bge-m3"
```

3. 修改 `VectorDB.py` 的第 12 行导入：
```python
# 改为
from langchain_community.embeddings import HuggingFaceEmbeddings
```

4. 修改 `VectorDB.py` 的第 30-32 行初始化：
```python
# 改为
self.embedding_mode = HuggingFaceEmbeddings(
    model_name=self.embedding_model_name,
    model_kwargs={'device': 'cuda'},  # 有GPU用cuda，否则用cpu
    encode_kwargs={'normalize_embeddings': True}
)
```

5. 首次运行会自动下载模型（约 1-2GB）

**推荐的中文开源模型**：
- `BAAI/bge-large-zh-v1.5`：中文效果最好（1GB）
- `BAAI/bge-base-zh-v1.5`：中等效果，速度快（400MB）
- `BAAI/bge-small-zh-v1.5`：轻量级（100MB）

---

**方案3：使用 Ollama 本地部署**

**优点**：本地部署，易于安装，免费  
**缺点**：效果略差于云端模型  
**适用场景**：离线环境，对效果要求不高

**步骤**：

1. 安装 Ollama：
   - 访问：https://ollama.ai/download
   - 下载并安装 Ollama

2. 下载嵌入模型：
```bash
ollama pull bge-m3
```

3. 修改 `config.py`：
```python
EMBEDDING_MODEL_NAME = "bge-m3"
```

4. 修改 `VectorDB.py` 的第 12 行导入：
```python
from langchain_community.embeddings import OllamaEmbeddings
```

5. 修改 `VectorDB.py` 的第 30-32 行初始化：
```python
self.embedding_mode = OllamaEmbeddings(
    model=self.embedding_model_name,
    base_url="http://localhost:11434"
)
```

---

#### 5.2.3 模型选择对比

| 模型方案 | 向量维度 | 中文效果 | 费用 | 部署难度 | 推荐场景 |
|---------|---------|---------|------|---------|---------|
| **DashScope** | 1536 | ⭐⭐⭐⭐⭐ | 免费额度充足 | ⭐ 极简 | **开发测试** ✅ |
| OpenAI | 1536/3072 | ⭐⭐⭐⭐ | 较高 | ⭐ 极简 | 生产环境（预算充足） |
| HuggingFace本地 | 1024 | ⭐⭐⭐⭐⭐ | 完全免费 | ⭐⭐⭐ 中等 | 大规模生产（有GPU） |
| Ollama本地 | 1024 | ⭐⭐⭐ | 完全免费 | ⭐⭐ 简单 | 离线场景 |

**推荐**：
- **开发测试阶段**：使用 DashScope（当前方案）
- **生产环境**：根据预算和硬件条件选择 OpenAI 或 HuggingFace
- **离线场景**：使用 Ollama

---

#### 5.2.4 模型更换注意事项

⚠️ **重要提示**：

1. **向量维度不兼容**：
   - 不同模型的向量维度可能不同
   - 更换模型后需要重新构建整个向量数据库
   - 旧的向量数据无法直接使用

2. **重建数据库流程**：
```python
# 1. 删除旧数据库
vectordb.delete_me()

# 2. 使用新模型初始化
vectordb = VectorDB(
    vector_db_store_path="./vector_db",
    embedding_model_name="new_model_name"
)

# 3. 重新添加所有文档
vectordb.add_documents(all_documents)
```

3. **检索效果差异**：
   - 不同模型对同一查询的检索结果可能不同
   - 建议在切换模型后进行效果测试

4. **性能差异**：
   - 云端 API：响应快，但有网络延迟
   - 本地模型：首次加载慢，后续推理快

---

### 5.3 Chroma 持久化机制

**存储结构**：
```
test_vector_db/                    # vector_db_store_path
├── chroma.sqlite3                 # 元数据数据库
└── [其他 Chroma 内部文件]
```

**持久化特点**：
1. **自动持久化**：每次操作后自动保存
2. **增量更新**：只保存变更部分
3. **加载恢复**：下次初始化时自动加载已有数据

**重启恢复**：
```python
# 第一次创建
vectordb = VectorDB("./my_db")
vectordb.add_documents(docs)

# 程序重启后
vectordb = VectorDB("./my_db")  # 自动加载已有数据
results = vectordb.search("query")  # 可以直接检索
```

---

### 5.4 相似度计算

**算法**：余弦相似度（Cosine Similarity）

**公式**：
```
similarity = (A · B) / (||A|| × ||B||)
```

**取值范围**：[-1, 1]
- 1：完全相同
- 0：无关
- -1：完全相反

**Chroma 默认行为**：
- 使用余弦相似度
- 返回相似度从高到低的文档
- 不返回相似度分数（但可以通过 similarity_search_with_score 获取）

---

## 六、测试脚本说明

### 6.1 测试文件

**文件路径**：`test_scripts/test_vectordb.py`

**测试覆盖**：
1. ✅ 环境变量检查（DASHSCOPE_API_KEY）
2. ✅ 数据加载（使用医疗知识图谱前100条）
3. ✅ VectorDB 初始化
4. ✅ 单个文档添加
5. ✅ 批量文档添加（49条）
6. ✅ 向量检索（两个不同查询）
7. ✅ 单个文档删除并验证
8. ✅ 批量文档删除
9. ✅ 数据库清理

### 6.2 运行测试

**前置条件**：
```bash
# 1. 激活 conda 环境
conda activate your_env_name

# 2. 安装依赖（如果还未安装）
pip install langchain langchain-community langchain-dashscope chromadb

# 3. 设置环境变量
set DASHSCOPE_API_KEY=your_api_key_here
```

**执行测试**：
```bash
cd F:\SE_works\application\dify\RAGKnowledgeBaseDemo-main\RAGKnowledgeBaseDemo-main\test_scripts
python test_vectordb.py
```

### 6.3 预期输出

```
============================================================
VectorDB 向量数据库功能测试
============================================================

【步骤1】加载测试数据
------------------------------------------------------------
正在加载数据文件: ..\MedicalDataset\triples.json
✓ 成功加载 82478 条三元组数据
...
✓ 准备测试数据: 100 条

【步骤2】初始化 VectorDB
------------------------------------------------------------
✓ VectorDB 初始化成功
  存储路径: ./test_vector_db
  嵌入模型: text-embedding-2

【测试1】添加单个文档
------------------------------------------------------------
文档内容: 人参茎叶总皂苷胶囊（药品） 不良反应 头痛（疾病）...
文档 MD5: a1b2c3d4e5f6g7h8...
✓ 单个文档添加成功

【测试2】批量添加文档
------------------------------------------------------------
批量添加 49 条文档...
✓ 批量添加成功

【测试3】向量检索
------------------------------------------------------------
查询1: 人参有什么副作用？
✓ 检索到 5 条相关文档

前3条结果:
  [1] 人参茎叶总皂苷胶囊（药品） 不良反应 头痛（疾病）...
  [2] 人参茎叶总皂苷胶囊（药品） 不良反应 腹泻（疾病）...
  [3] 人参茎叶总皂苷胶囊（药品） 不良反应 心悸（症状）...

查询2: 糖尿病的症状
✓ 检索到 5 条相关文档
...

【测试4】删除单个文档
------------------------------------------------------------
删除文档 MD5: a1b2c3d4e5f6g7h8...
✓ 单个文档删除成功
✓ 验证：文档已从数据库中删除

【测试5】批量删除文档
------------------------------------------------------------
批量删除 9 条文档...
✓ 批量删除成功

【测试6】清理测试数据
------------------------------------------------------------
成功删除向量数据库: ./test_vector_db
✓ 测试数据库已清理

============================================================
✓ 所有测试通过！VectorDB 功能正常
============================================================
```

---

## 七、使用示例

### 7.1 基本使用流程

```python
from VectorDB import VectorDB
from langchain_core.documents import Document
import hashlib

# 1. 初始化 VectorDB
vectordb = VectorDB(
    vector_db_store_path="./my_knowledge_base/vector_db",
    embedding_model_name="text-embedding-2"
)

# 2. 准备文档
doc = Document(
    page_content="人参茎叶总皂苷胶囊用于治疗糖尿病",
    metadata={
        'md5': hashlib.md5("...".encode()).hexdigest(),
        'source': 'medical_kb.json',
        'entity_type': '药品'
    }
)

# 3. 添加文档
vectordb.add_document(doc)

# 4. 检索
results = vectordb.search("糖尿病的治疗药物", k=5)
for doc in results:
    print(doc.page_content)

# 5. 删除文档
vectordb.delete_document(doc.metadata['md5'])
```

### 7.2 批量导入场景

```python
# 批量导入医疗数据
from test_data_loader import MedicalDataLoader

# 加载数据
loader = MedicalDataLoader("./data/medical.json")
loader.load_data()
documents = loader.convert_to_documents(format_type='triple')

# 分批添加（避免一次性加载过多）
batch_size = 1000
for i in range(0, len(documents), batch_size):
    batch = documents[i:i+batch_size]
    vectordb.add_documents(batch)
    print(f"已添加 {i+len(batch)}/{len(documents)} 条文档")
```

---

## 八、性能考虑

### 8.1 向量化性能

**DashScope API 限制**：
- QPS 限制：根据套餐不同（免费版约 10 QPS）
- 单次请求：建议不超过 100 条文档
- 响应时间：平均 100-300ms

**优化建议**：
```python
# 分批添加，避免超时
batch_size = 50  # 每批50条
for i in range(0, len(docs), batch_size):
    vectordb.add_documents(docs[i:i+batch_size])
    time.sleep(0.1)  # 避免触发限流
```

### 8.2 检索性能

**Chroma 检索性能**：
- 10,000 文档：<50ms
- 100,000 文档：<200ms
- 1,000,000 文档：<1s

**规模建议**：
- 小型知识库（<10万文档）：单个 Chroma 实例
- 中型知识库（10-100万）：考虑分片或索引优化
- 大型知识库（>100万）：考虑专业向量数据库（Milvus, Weaviate）

### 8.3 存储空间

**存储估算**：
- 每个文档向量：1536 维 × 4 字节 = 6KB
- 元数据：约 1KB
- 索引开销：约 20%
- **总计**：约 8-9KB/文档

**示例**：
- 10,000 文档 ≈ 80-90MB
- 100,000 文档 ≈ 800MB-900MB
- 1,000,000 文档 ≈ 8-9GB

---

## 九、常见问题

### 9.1 API Key 配置

**Q1：如何获取 DASHSCOPE_API_KEY？**

A：访问 https://dashscope.console.aliyun.com/
1. 注册/登录阿里云账号
2. 开通百炼服务（有免费额度）
3. 在控制台获取 API Key

**Q2：环境变量没生效？**

A：确保在运行 Python 之前设置
```bash
# Windows CMD
set DASHSCOPE_API_KEY=sk-xxx
python test_vectordb.py

# Windows PowerShell
$env:DASHSCOPE_API_KEY="sk-xxx"
python test_vectordb.py

# 或在代码中设置
import os
os.environ['DASHSCOPE_API_KEY'] = 'sk-xxx'
```

### 9.2 Chroma 相关

**Q3：如何清空数据库重新开始？**

A：
```python
vectordb.delete_me()  # 删除整个数据库
vectordb = VectorDB(same_path)  # 重新初始化
```

**Q4：数据库文件可以移动吗？**

A：可以，但需要：
1. 移动整个目录
2. 更新 vector_db_store_path 参数

### 9.3 检索效果

**Q5：检索结果不相关？**

A：可能原因：
1. 文档数量太少（建议 >100 条）
2. 查询词与文档内容差异大
3. 需要调整 k 值（增加返回数量）

**Q6：如何提高检索准确度？**

A：
1. 增加文档数量
2. 优化文档切分粒度
3. 使用混合检索（向量+关键词）
4. 添加重排序（下一步实现）

---

## 十、文件清单

本步骤创建/修改的文件：

```
RAGKnowledgeBaseDemo-main/
├── VectorDB.py                              ✅ 修改（实现所有方法）
├── test_scripts/
│   └── test_vectordb.py                     ✅ 新建（VectorDB测试脚本）
└── doc/
    └── 项目实现过程/
        └── 02_VectorDB实现.md               ✅ 新建（本文档）
```

---

## 十一、下一步计划

### 下一步：实现 KeywordDB（关键词数据库）

**目标**：实现基于 BM25 算法的关键词检索数据库

**主要任务**：
1. 实现 KeywordDB 类的核心方法
2. 基于 LangChain 的 BM25Retriever
3. 实现文档持久化存储
4. 实现关键词检索功能
5. 编写单元测试验证功能

**待实现的方法**：
```python
KeywordDB._load_documents() -> Dict[str, Document]
KeywordDB._build_retriever() -> BM25Retriever
KeywordDB.add_document(document: Document) -> bool
KeywordDB.add_documents(documents: List[Document]) -> bool
KeywordDB.delete_document(md5: str) -> bool
KeywordDB.delete_documents(md5_list: List[str]) -> bool
KeywordDB.search(query: str, k: int) -> List[Document]
KeywordDB.delete_me() -> None
```

**技术栈**：
- 检索算法：BM25（Best Matching 25）
- 实现方式：LangChain BM25Retriever
- 持久化：pickle + JSON

---

## 十二、备注

1. **API 成本**：DashScope 免费额度有限，大规模测试建议使用付费套餐
2. **版本兼容**：基于 langchain-community 0.2.x 开发
3. **线程安全**：当前实现不保证线程安全，多线程场景需要加锁
4. **向量维度**：text-embedding-2 固定 1536 维，不可更改

---

**文档版本**：v1.0  
**创建日期**：2026-08-10  
**最后更新**：2026-08-10
