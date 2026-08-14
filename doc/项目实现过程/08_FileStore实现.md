# 步骤08：FileStore 文件存储实现

**完成时间**：2026-08-15  
**负责模块**：文件存储 - 文件管理  
**状态**：✅ 已完成

---

## 一、实现目标

实现文件存储管理器（FileStore），负责文件的持久化存储、文档切分、去重管理和文件-文档映射关系维护，为 KnowledgeBase 提供完整的文件管理能力。

---

## 二、核心功能需求回顾

根据 `doc/实现思路（语雀）.md` 中的定义：

### 2.1 功能需求
- **核心功能**：
  1. 文件存储：复制文件到知识库目录
  2. 文件去重：避免重复存储同名文件
  3. 文档切分：调用 Splitter 切分文件为文档块
  4. 文档持久化：保存切分后的文档为 JSON 文件
  5. 映射管理：维护文件与文档的对应关系
  6. 文件删除：级联删除文件、文档和映射关系

### 2.2 技术实现
- **文件加载器**：UnstructuredFileLoader（LangChain）
- **依赖组件**：Deduplicator（去重）、Splitter（切分）
- **存储结构**：
  ```
  /file_store/
    files/           # 原始文件
    documents/       # 切分后的文档JSON
    file_document_map.json  # 文件-文档映射
  ```

---

## 三、实现内容

### 3.1 已实现的方法

#### ✅ 初始化
```python
__init__(file_store_path, document_store_path, splitter, rag_service)
    初始化文件存储，加载映射关系
```

#### ✅ 文件管理
```python
save_file(file_path: str) -> tuple[bool, int]
    保存文件并切分为文档

delete_file(filename: str) -> tuple[bool, list[str]]
    删除文件及其关联的文档

get_all_files() -> list[str]
    获取所有已存储的文件列表
```

#### ✅ 文档查询
```python
get_documents_by_file(filename: str) -> list[Document]
    根据文件名获取其切分后的所有文档块
```

#### ✅ 映射管理（内部方法）
```python
_load_file_document_map() -> None
    加载文件-文档映射关系

_save_file_document_map() -> None
    保存文件-文档映射关系
```

---

## 四、详细实现说明

### 4.1 初始化和目录结构

**功能**：创建必要的目录和加载映射关系

**目录结构**：
```
data/knowledge/test_kb/file_store/
├── files/                          # 原始文件存储
│   ├── document1.txt
│   ├── document2.pdf
│   └── ...
├── documents/                      # 切分后的文档JSON
│   ├── fe5820fe31ea71a0df868a0f120553dc.json
│   ├── b7d23a93fb49160225fea7cd183442c8.json
│   └── ...
└── file_document_map.json         # 映射关系文件
```

**映射文件格式**：
```json
{
  "document1.txt": [
    "fe5820fe31ea71a0df868a0f120553dc",
    "b7d23a93fb49160225fea7cd183442c8",
    "c4970a2d42756155cea29cb1c14600f6"
  ],
  "document2.pdf": [
    "d8e9f2a1b3c4d5e6f7a8b9c0d1e2f3a4"
  ]
}
```

**核心代码**：
```python
def __init__(self, file_store_path, document_store_path, splitter, rag_service):
    self.file_store_path = file_store_path
    self.document_store_path = document_store_path
    self.splitter = splitter
    self.rag_service = rag_service
    
    # 创建目录
    os.makedirs(self.file_store_path, exist_ok=True)
    os.makedirs(self.document_store_path, exist_ok=True)
    
    # 初始化去重器和加载器
    self.deduplicator = Deduplicator(
        md5_store_path=os.path.join(file_store_path, "file_md5.txt")
    )
    self.file_loader = UnstructuredFileLoader
    
    # 加载映射关系
    self._load_file_document_map()
```

---

### 4.2 save_file() - 保存文件

**功能**：将文件复制到知识库，切分为文档块，并存储到 RAGService

**完整流程**（7步）：

```python
def save_file(self, file_path: str) -> tuple[bool, int]:
    filename = os.path.basename(file_path)
    
    # 1. 文件名去重
    if self.deduplicator.check_duplicate(filename):
        return False, 0
    
    # 2. 复制文件到 file_store_path
    target_path = os.path.join(self.file_store_path, filename)
    shutil.copy(file_path, target_path)
    
    # 3. 加载文件为 Document
    loader = self.file_loader(target_path)
    document = loader.load()[0]
    document.metadata['file_path'] = target_path
    
    # 4. 切分文档
    split_docs = self.splitter.split_document(document)
    
    # 5. 添加到 RAGService（会自动存储到 VectorDB 和 KeywordDB）
    success = self.rag_service.add_documents(split_docs)
    if not success:
        os.remove(target_path)  # 回滚
        return False, 0
    
    # 6. 记录文件名到去重器
    self.deduplicator.save_str(filename)
    
    # 7. 保存每个文档到 document_store_path（以 MD5 命名的 JSON 文件）
    doc_md5_list = []
    for split_doc in split_docs:
        doc_md5 = split_doc.metadata.get('md5')
        if doc_md5:
            doc_md5_list.append(doc_md5)
            doc_file_path = os.path.join(self.document_store_path, f"{doc_md5}.json")
            with open(doc_file_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "page_content": split_doc.page_content,
                    "metadata": split_doc.metadata
                }, f, ensure_ascii=False, indent=2)
    
    # 8. 更新文件-文档映射
    self.file_document_map[filename] = doc_md5_list
    self._save_file_document_map()
    
    return True, len(split_docs)
```

**关键设计**：
1. **原子性保证**：RAGService 失败时自动回滚文件复制
2. **双重存储**：文档既存储在 VectorDB/KeywordDB（检索），也存储为 JSON（查看）
3. **映射维护**：实时更新文件-文档映射关系

---

### 4.3 delete_file() - 删除文件

**功能**：级联删除文件、文档和映射关系

**完整流程**（5步）：

```python
def delete_file(self, filename: str) -> tuple[bool, list[str]]:
    # 1. 检查文件是否存在
    if filename not in self.file_document_map:
        return False, []
    
    # 2. 获取文档 MD5 列表
    doc_md5_list = self.file_document_map[filename]
    
    # 3. 从 RAGService 删除所有文档
    for doc_md5 in doc_md5_list:
        self.rag_service.delete_document(doc_md5)
    
    # 4. 删除所有文档 JSON 文件
    for doc_md5 in doc_md5_list:
        doc_file_path = os.path.join(self.document_store_path, f"{doc_md5}.json")
        if os.path.exists(doc_file_path):
            os.remove(doc_file_path)
    
    # 5. 删除原始文件
    file_path = os.path.join(self.file_store_path, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # 6. 从去重器删除
    self.deduplicator.delete_str(filename)
    
    # 7. 删除映射关系
    del self.file_document_map[filename]
    self._save_file_document_map()
    
    return True, doc_md5_list
```

**关键设计**：
- **级联删除**：确保所有相关数据都被清理
- **顺序重要**：先删检索数据库，再删文件，最后删映射

---

### 4.4 get_documents_by_file() - 查看文档

**功能**：根据文件名读取其切分后的所有文档块

**实现要点**：
1. 从映射关系获取 MD5 列表
2. 读取每个 MD5 对应的 JSON 文件
3. 重建 Document 对象

**核心代码**：
```python
def get_documents_by_file(self, filename: str) -> list[Document]:
    if filename not in self.file_document_map:
        return []
    
    doc_md5_list = self.file_document_map[filename]
    documents = []
    
    for doc_md5 in doc_md5_list:
        doc_file_path = os.path.join(self.document_store_path, f"{doc_md5}.json")
        if os.path.exists(doc_file_path):
            with open(doc_file_path, 'r', encoding='utf-8') as f:
                doc_data = json.load(f)
                doc = Document(
                    page_content=doc_data["page_content"],
                    metadata=doc_data["metadata"]
                )
                documents.append(doc)
    
    return documents
```

**应用场景**：
- 用户查看某个文件被切分成了哪些文档块
- 调试检索问题（查看文档内容是否正确）

---

## 五、测试验证

### 5.1 测试脚本
**文件位置**：`test_scripts/test_filestore.py`

### 5.2 测试内容
1. ✅ 文件保存（单个文件）
2. ✅ 文件去重（重复保存失败）
3. ✅ 批量添加多个文件
4. ✅ 查看文件的文档列表
5. ✅ 文件删除（级联删除）
6. ✅ 清理测试数据

### 5.3 测试结果
```
测试 1: 保存文件
文件: test_document.txt
切分结果: 5 个文档块
映射关系已保存

测试 2: 文件去重
第一次保存: 成功
第二次保存: 失败（文件名重复）

测试 3: 查看文档
文件: test_document.txt
文档数量: 5
文档1预览: "这是测试文档的第一段..."
文档2预览: "这是测试文档的第二段..."

测试 4: 删除文件
删除文件: test_document.txt
删除文档数: 5
映射关系已更新

[SUCCESS] FileStore 测试全部通过
```

---

## 六、关键技术点

### 6.1 文件-文档映射

**为什么需要映射？**
- RAGService 只存储文档，不知道文档来自哪个文件
- 删除文件时需要知道要删除哪些文档
- 用户查看文档时需要按文件聚合

**映射维护时机**：
- **添加时**：save_file() 最后保存映射
- **删除时**：delete_file() 最后删除映射
- **加载时**：__init__() 从 JSON 文件加载

### 6.2 双重存储设计

**为什么文档要存两份？**

| 存储位置 | 格式 | 用途 | 优势 |
|---------|------|------|------|
| VectorDB/KeywordDB | 向量+倒排索引 | 检索 | 检索速度快 |
| document_store_path | JSON 文件 | 查看原文 | 可读性好，易调试 |

**示例**：
```
fe5820fe31ea71a0df868a0f120553dc.json:
{
  "page_content": "糖尿病是一种慢性代谢性疾病...",
  "metadata": {
    "md5": "fe5820fe31ea71a0df868a0f120553dc",
    "source": "diabetes.txt",
    "file_path": "data/knowledge/test_kb/file_store/files/diabetes.txt"
  }
}
```

### 6.3 原子性保证

**场景**：添加文件时 RAGService 失败

**问题**：
- 文件已复制到 file_store_path
- 但文档未成功存储到检索数据库
- 导致不一致状态

**解决方案**：
```python
success = self.rag_service.add_documents(split_docs)
if not success:
    os.remove(target_path)  # 回滚文件复制
    return False, 0
```

---

## 七、与其他组件的集成

### 7.1 依赖关系图

```
FileStore
  ├─→ Deduplicator（文件名去重）
  ├─→ Splitter（文档切分）
  ├─→ RAGService（文档存储和检索）
  └─→ UnstructuredFileLoader（文件加载）
```

### 7.2 与 KnowledgeBase 的集成

**调用流程**：
```python
# KnowledgeBase.add_file()
def add_file(self, file_path: str) -> dict:
    success, doc_count = self.file_store.save_file(file_path)  # ← 调用 FileStore
    return {
        "success": success,
        "document_count": doc_count
    }
```

---

## 八、遇到的问题和解决

### 问题1：文档持久化缺失
**现象**：`get_documents_by_file()` 返回空列表

**原因**：
- 初始实现只存储到 VectorDB/KeywordDB
- 没有保存文档 JSON 文件

**解决方案**：
- 在 `save_file()` 添加步骤7：保存文档 JSON
- 格式：`{md5}.json`

### 问题2：删除不完整
**现象**：删除文件后，文档 JSON 文件残留

**原因**：
- `delete_file()` 只删除了原始文件和 RAGService 中的文档
- 忘记删除 document_store_path 中的 JSON 文件

**解决方案**：
- 添加步骤4：删除所有文档 JSON 文件

### 问题3：映射关系不一致
**现象**：重启后文件列表错误

**原因**：
- 增删操作后没有立即保存映射文件
- 程序崩溃导致映射丢失

**解决方案**：
- 每次增删后立即调用 `_save_file_document_map()`
- 确保映射持久化

---

## 九、完成标志

✅ 所有方法实现完成  
✅ 测试脚本运行成功  
✅ 文件存储功能正常  
✅ 文档切分和持久化成功  
✅ 映射关系维护正确  
✅ 级联删除功能完整  
✅ 与 KnowledgeBase 集成成功

---

**文档版本**：v1.0  
**最后更新**：2026-08-15
