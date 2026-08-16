# 步骤06：Deduplicator 去重器实现

**完成时间**：2026-08-14  
**负责模块**：文件存储 - 去重器  
**状态**：✅ 已完成

---

## 一、实现目标

实现基于 MD5 哈希的去重器（Deduplicator），提供字符串和文档的 MD5 计算、持久化存储和查重功能，为 FileStore 和 Splitter 提供去重能力。

---

## 二、核心功能需求回顾

根据 `doc/实现思路（语雀）.md` 中的定义：

### 2.1 功能需求
- **核心功能**：
  1. 字符串转 MD5：计算任意字符串的 MD5 哈希值
  2. 文档转 MD5：计算 Document 内容的 MD5 哈希值
  3. 持久化存储：保存已见过的 MD5 值，支持查重
  4. 增删操作：添加和删除 MD5 记录

### 2.2 技术实现
- **哈希算法**：MD5（hashlib 库）
- **存储方式**：文本文件（每行一个 MD5）
- **编码方式**：UTF-8

---

## 三、实现内容

### 3.1 已实现的方法

#### ✅ MD5 计算（静态方法）
```python
@staticmethod
str_to_md5(text: str) -> str
    计算字符串的 MD5 哈希值

@staticmethod
document_to_md5(document: Document) -> str
    计算 Document 内容的 MD5 哈希值
```

#### ✅ 持久化管理
```python
__init__(md5_store_path: str)
    初始化去重器，加载已有的 MD5 记录

_load_md5_set() -> None
    从文件加载 MD5 集合

_save_md5_set() -> None
    保存 MD5 集合到文件
```

#### ✅ 去重操作
```python
save_str(text: str) -> bool
    保存字符串的 MD5（用于文件名去重）

delete_str(text: str) -> bool
    删除字符串的 MD5

check_duplicate(text: str) -> bool
    检查字符串是否重复
```

---

## 四、详细实现说明

### 4.1 str_to_md5() - 字符串转 MD5

**功能**：计算字符串的 MD5 哈希值

**实现要点**：
1. **编码处理**：字符串编码为 UTF-8 字节
2. **哈希计算**：使用 hashlib.md5() 计算哈希
3. **返回格式**：32 位十六进制字符串

**核心代码**：
```python
@staticmethod
def str_to_md5(text: str) -> str:
    if not text:
        return ""
    return hashlib.md5(text.encode('utf-8')).hexdigest()
```

**关键设计**：
- 静态方法，无需实例化即可调用
- 空字符串返回空串，避免异常
- 固定编码 UTF-8，确保跨平台一致性

---

### 4.2 document_to_md5() - 文档转 MD5

**功能**：计算 Document 内容的 MD5 哈希值

**实现要点**：
1. 提取 document.page_content
2. 复用 str_to_md5() 方法

**核心代码**：
```python
@staticmethod
def document_to_md5(document: Document) -> str:
    if not document or not document.page_content:
        return ""
    return Deduplicator.str_to_md5(document.page_content)
```

---

### 4.3 持久化机制

**文件格式**：
```
fe5820fe31ea71a0df868a0f120553dc
b7d23a93fb49160225fea7cd183442c8
c4970a2d42756155cea29cb1c14600f6
```

**加载逻辑**：
```python
def _load_md5_set(self):
    if os.path.exists(self.md5_store_path):
        with open(self.md5_store_path, 'r', encoding='utf-8') as f:
            self.md5_set = set(line.strip() for line in f if line.strip())
    else:
        self.md5_set = set()
```

**保存逻辑**：
```python
def _save_md5_set(self):
    os.makedirs(os.path.dirname(self.md5_store_path), exist_ok=True)
    with open(self.md5_store_path, 'w', encoding='utf-8') as f:
        for md5 in self.md5_set:
            f.write(md5 + '\n')
```

---

### 4.4 去重操作

**添加 MD5**：
```python
def save_str(self, text: str) -> bool:
    md5 = self.str_to_md5(text)
    if not md5:
        return False
    
    if md5 in self.md5_set:
        return False  # 已存在
    
    self.md5_set.add(md5)
    self._save_md5_set()
    return True
```

**删除 MD5**：
```python
def delete_str(self, text: str) -> bool:
    md5 = self.str_to_md5(text)
    if md5 in self.md5_set:
        self.md5_set.remove(md5)
        self._save_md5_set()
        return True
    return False
```

**查重**：
```python
def check_duplicate(self, text: str) -> bool:
    md5 = self.str_to_md5(text)
    return md5 in self.md5_set
```

---

## 五、测试验证

### 5.1 测试脚本
**文件位置**：`test_scripts/test_deduplicator.py`

### 5.2 测试内容
1. ✅ MD5 计算正确性
2. ✅ 文件名去重功能
3. ✅ 持久化存储和加载
4. ✅ 删除操作
5. ✅ 清理测试数据

### 5.3 测试结果
```
测试 1: MD5 计算
字符串 MD5: 5d41402abc4b2a76b9719d911017c592
Document MD5: 5d41402abc4b2a76b9719d911017c592

测试 2: 去重功能
第一次添加: True
第二次添加: False (已存在)
查重结果: True

测试 3: 删除功能
删除后查重: False

[SUCCESS] Deduplicator 测试全部通过
```

---

## 六、关键技术点

### 6.1 MD5 哈希
- **算法**：MD5（128位哈希）
- **碰撞概率**：对于文本去重场景，碰撞概率极低
- **性能**：计算速度快，适合实时去重

### 6.2 内存 + 持久化
- **内存**：使用 set 存储 MD5，O(1) 查重速度
- **持久化**：每次增删立即保存，确保数据安全
- **权衡**：牺牲少量性能换取数据一致性

### 6.3 应用场景
1. **FileStore**：文件名去重（避免重复存储同名文件）
2. **Splitter**：文档块去重（计算切分后文档的 MD5）
3. **KnowledgeBase**：避免重复导入相同内容

---

## 七、遇到的问题和解决

### 问题1：MD5 碰撞风险
**现象**：不同内容可能产生相同的 MD5（理论上）

**解决方案**：
- 对于文本去重场景，MD5 已足够安全
- 如需更高安全性，可升级为 SHA-256
- 当前实现：保持 MD5（性能优先）

### 问题2：大量 MD5 的内存占用
**现象**：10万个文件 → 10万个 MD5 → 约 3.2MB 内存

**解决方案**：
- 当前规模下内存占用可接受
- 未来可优化：使用布隆过滤器（允许小概率误判）
- 当前实现：直接使用 set（精确去重）

---

## 八、完成标志

✅ 所有方法实现完成  
✅ 测试脚本运行成功  
✅ MD5 计算准确  
✅ 去重功能正常  
✅ 持久化存储可靠  
✅ 与 FileStore、Splitter 集成成功

---

**文档版本**：v1.0  
**最后更新**：2026-08-15
