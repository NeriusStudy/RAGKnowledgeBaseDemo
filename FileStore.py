"""
文件存储类
用于存储文件内容
利用deduplicator实现文件去重，对文件名进行去重，避免重复存储相同文件
利用splitter将文件内容分割为文档，每个文档对应一个md5值，用于唯一标识文档
存储文件和切分的文档的对应关系
"""
from typing import List, Optional, Dict
from langchain_core.documents import Document
from Splitter import Splitter
from Deduplicator import Deduplicator
import config
import os
import json
import shutil

class FileStore:
    def __init__(self,
                 file_store_path: str,
                 document_store_path: str,
                 md5_store_path: str,
                 file_document_map_store_path: str,
                 splitter_chunk_size: int = config.SPLITTER_CHUNK_SIZE,
                 splitter_chunk_overlap: int = config.SPLITTER_CHUNK_OVERLAP,
                 splitter_separaters: List[str] = config.SPLITTER_SEPARATERS,
                 splitter_length_function = config.SPLITTER_LENGTH_FUNCTION,
                 ):
        """
        初始化文件存储类
        Args:
            file_store_path: 文件存储路径目录
            document_store_path: 文档存储路径目录
            md5_store_path: md5存储路径文件
            file_document_map_store_path: 文件和文档对应关系存储路径文件
        """
        # 初始化文件存储路径
        self.file_store_path = file_store_path
        # 初始化文档存储路径
        self.document_store_path = document_store_path
        # 初始化md5存储路径
        self.md5_store_path = md5_store_path
        # 初始化文件和文档对应关系存储路径
        self.file_document_map_store_path = file_document_map_store_path

        # 初始化文档分割器参数
        self.splitter_chunk_size = splitter_chunk_size
        self.splitter_chunk_overlap = splitter_chunk_overlap
        self.splitter_separaters = splitter_separaters
        self.splitter_length_function = splitter_length_function
        # 初始化文档分割器
        self.splitter = Splitter(
            chunk_size=self.splitter_chunk_size,
            chunk_overlap=self.splitter_chunk_overlap,
            separators=self.splitter_separaters,
            length_function=self.splitter_length_function,
        )
        # 初始化去重器
        self.deduplicator = Deduplicator(md5_store_path)
        # 初始化文件和文档对应关系映射
        self.file_document_map = {}
        # 加载文件和文档对应关系映射
        self._load_file_document_map()

    def _load_file_document_map(self):
        """
        加载文件和文档对应关系映射
        """
        if not os.path.exists(self.file_document_map_store_path):
            self.file_document_map = {}
            return

        try:
            with open(self.file_document_map_store_path, 'r', encoding='utf-8') as f:
                self.file_document_map = json.load(f)
        except Exception as e:
            print(f"错误[FileStore._load_file_document_map] 加载文件-文档映射失败: {e}")
            self.file_document_map = {}

    def _save_file_document_map(self):
        """
        保存文件和文档对应关系映射
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.file_document_map_store_path), exist_ok=True)

            with open(self.file_document_map_store_path, 'w', encoding='utf-8') as f:
                json.dump(self.file_document_map, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[FileStore] 保存文件-文档映射失败: {e}")

    def _file_to_document(self, file_path: str, file_name: str) -> Document:
        """
        解析文件成为Document
        Args:
            file_path: 文件路径
            file_name: 文件名称
        Returns:
            Document 对象
        """
        try:
            # 读取文件内容（支持 TXT, JSON, CSV, MD 等文本文件）
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 创建 Document
            doc = Document(
                page_content=content,
                metadata={
                    "source": file_name,
                    "file_path": file_path,
                    "file_type": os.path.splitext(file_name)[1]
                }
            )

            return doc

        except Exception as e:
            print(f"错误[FileStore._file_to_document] 文件解析失败 {file_name}: {e}")
            raise

    def get_splitter_chunk_size(self) -> int:
        """
        获取当前使用的文本块最大字符数
        Returns:
            int: 当前使用的文本块最大字符数
        """
        return self.splitter.get_chunk_size()

    def get_splitter_chunk_overlap(self) -> int:
        """
        获取当前使用的文本块重叠字符数
        Returns:
            int: 当前使用的文本块重叠字符数
        """
        return self.splitter.get_chunk_overlap()

    def get_splitter_separaters(self) -> List[str]:
        """
        获取当前使用的切分分隔符列表
        Returns:
            List[str]: 当前使用的切分分隔符列表
        """
        return self.splitter.get_separators()

    def get_splitter_length_function(self):
        """
        获取当前使用的计算文本长度的函数
        Returns:
            计算文本长度的函数
        """
        return self.splitter.get_length_function()

    def save_file(self, file_path: str, file_name: Optional[str] = None) -> List[Document]:
        """
        保存文件内容到存储路径，需要对传入的文件根据文件名称进行去重处理，如果重复则不再保存
        切分文件内容为文档，每个文档对应一个md5值，用于唯一标识文档
        保存文件和文档的对应关系
        Args:
            file_path: 待保存的文件路径
            file_name: 文件名称（可选，默认使用文件路径中的文件名）
        Returns:
            List[Document]: 切分后的文档列表，其中每个文档的md5保存在Document的metadata中
        """
        # 获取文件名
        if file_name is None:
            file_name = os.path.basename(file_path)

        # 1. 检查文件是否已存在（去重）
        if file_name in self.file_document_map:
            print(f"警告[FileStore.save_file] 文件已存在，跳过: {file_name}")
            return []

        # 2. 确保文件存储目录存在
        os.makedirs(self.file_store_path, exist_ok=True)

        # 3. 复制文件到存储目录
        target_file_path = os.path.join(self.file_store_path, file_name)
        try:
            shutil.copy2(file_path, target_file_path)
        except Exception as e:
            print(f"[FileStore] 文件复制失败: {e}")
            return []

        # 4. 解析文件为 Document
        try:
            doc = self._file_to_document(target_file_path, file_name)
        except Exception as e:
            # 解析失败，删除已复制的文件
            os.remove(target_file_path)
            print(f"[FileStore] 文件解析失败，已删除: {file_name}")
            return []

        # 5. 切分 Document
        split_docs = self.splitter.split_document(doc)

        # 6. 提取所有文档的 MD5
        doc_md5_list = [d.metadata.get('md5') for d in split_docs if 'md5' in d.metadata]

        # 7. 保存每个文档到 document_store_path（以 MD5 命名的 JSON 文件）
        os.makedirs(self.document_store_path, exist_ok=True)
        for split_doc in split_docs:
            doc_md5 = split_doc.metadata.get('md5')
            if doc_md5:
                doc_file_path = os.path.join(self.document_store_path, f"{doc_md5}.json")
                try:
                    with open(doc_file_path, 'w', encoding='utf-8') as f:
                        json.dump({
                            "page_content": split_doc.page_content,
                            "metadata": split_doc.metadata
                        }, f, ensure_ascii=False, indent=2)
                except Exception as e:
                    print(f"错误[FileStore.save_file] 文档保存失败 {doc_md5}: {e}")

        # 8. 保存文件-文档映射关系
        self.file_document_map[file_name] = {
            "file_path": target_file_path,
            "document_md5_list": doc_md5_list,
            "document_count": len(split_docs)
        }

        # 9. 持久化映射关系
        self._save_file_document_map()

        # 10. 保存文件名到去重器（用于文件名去重）
        self.deduplicator.save_str(file_name)

        print(f"成功[FileStore.save_file] 文件保存成功: {file_name}, 切分为 {len(split_docs)} 个文档")

        return split_docs

    def delete_file(self, file_name: str) -> List[str]:
        """
        删除文件，以及在deduplicator中删除，以及删除所有对应的文档
        返回删除的文件所对应的所有文档的md5信息，方便后续对向量库和关键词库的删除
        删除文件和文档的对应关系
        Args:
            file_name: 待删除的文件名称
        Returns:
            List[str]: 删除的文件的所有对应的文档的md5列表
        """
        # 1. 检查文件是否存在
        if file_name not in self.file_document_map:
            print(f"警告[FileStore.delete_file] 文件不存在: {file_name}")
            return []

        # 2. 获取文档 MD5 列表
        file_info = self.file_document_map[file_name]
        doc_md5_list = file_info.get("document_md5_list", [])
        file_path = file_info.get("file_path")

        # 3. 删除物理文件
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"错误[FileStore.delete_file] 删除文件失败: {e}")

        # 4. 删除所有文档 JSON 文件
        for doc_md5 in doc_md5_list:
            doc_file_path = os.path.join(self.document_store_path, f"{doc_md5}.json")
            if os.path.exists(doc_file_path):
                try:
                    os.remove(doc_file_path)
                except Exception as e:
                    print(f"错误[FileStore.delete_file] 删除文档文件失败 {doc_md5}: {e}")

        # 5. 从映射中删除
        del self.file_document_map[file_name]

        # 6. 持久化映射关系
        self._save_file_document_map()

        # 7. 从去重器中删除文件名
        self.deduplicator.delete_str(file_name)

        print(f"成功[FileStore.delete_file] 文件删除成功: {file_name}, 返回 {len(doc_md5_list)} 个文档 MD5")

        return doc_md5_list

    def get_document_md5_from_file_name(self, file_name: str) -> List[str]:
        """
        根据文件名称获取文件的所有对应的文档的md5列表
        Args:
            file_name: 文件名称
        Returns:
            List[str]: 文件的所有对应的文档的md5列表
        """
        if file_name not in self.file_document_map:
            return []

        return self.file_document_map[file_name].get("document_md5_list", [])

    def get_file(self, file_name: str) -> Optional[str]:
        """
        根据文件名称获取文件路径
        Args:
            file_name: 文件名称
        Returns:
            文件的存储路径，如果文件不存在则返回 None
        """
        if file_name not in self.file_document_map:
            return None

        return self.file_document_map[file_name].get("file_path")

    def get_all_file_name(self) -> List[str]:
        """
        获取所有文件名称
        Returns:
            List[str]: 所有文件名称列表
        """
        return list(self.file_document_map.keys())

    def get_file_count(self) -> int:
        """
        获取已存储的文件总数
        Returns:
            int: 文件总数
        """
        return len(self.file_document_map)

    def get_total_document_count(self) -> int:
        """
        获取所有文件切分后的文档总数
        Returns:
            int: 文档总数
        """
        total = 0
        for file_info in self.file_document_map.values():
            total += file_info.get("document_count", 0)
        return total

    def get_file_document_map(self) -> Dict[str, Dict]:
        """
        获取文件和文档的对应关系
        Returns:
            Dict: 文件和文档的对应关系字典
                  格式: {file_name: {"file_path": str, "document_md5_list": List[str], "document_count": int}}
        """
        return self.file_document_map.copy()

    def get_file_md5s(self, file_name: str) -> List[str]:
        """
        根据文件名获取该文件所有文档的 MD5 列表（KnowledgeBase 使用）
        Args:
            file_name: 文件名称
        Returns:
            List[str]: 文档 MD5 列表
        """
        return self.get_document_md5_from_file_name(file_name)

    def get_documents_by_file(self, file_name: str) -> List[Document]:
        """
        根据文件名获取该文件切分后的所有文档
        Args:
            file_name: 文件名称
        Returns:
            List[Document]: 文档列表
        """
        md5_list = self.get_document_md5_from_file_name(file_name)
        documents = []

        for md5 in md5_list:
            doc_path = os.path.join(self.document_store_path, f"{md5}.json")
            if os.path.exists(doc_path):
                try:
                    with open(doc_path, 'r', encoding='utf-8') as f:
                        doc_data = json.load(f)
                        doc = Document(
                            page_content=doc_data.get("page_content", ""),
                            metadata=doc_data.get("metadata", {})
                        )
                        documents.append(doc)
                except Exception as e:
                    print(f"错误[FileStore.get_documents_by_file] 读取文档失败: {md5}.json, 错误: {e}")

        return documents

    def delete_me(self):
        """
        删除所有持久化存储，清理文件、文档、MD5、映射数据
        """
        import gc
        import time
        from pathlib import Path

        try:
            # 1. 删除文件存储目录
            self._delete_path(self.file_store_path, "文件存储目录")

            # 2. 删除文档存储目录
            self._delete_path(self.document_store_path, "文档存储目录")

            # 3. 删除 MD5 存储文件
            self._delete_file(self.md5_store_path, "MD5存储文件")

            # 4. 删除文件-文档映射文件
            self._delete_file(self.file_document_map_store_path, "文件-文档映射文件")

            # 5. 清理内部状态
            self.file_document_map.clear()
            self.splitter = None
            self.deduplicator = None

            gc.collect()
            print("信息[FileStore.delete_me]：FileStore 所有数据已清理")

        except Exception as e:
            print(f"错误[FileStore.delete_me]：删除持久化存储时出错: {str(e)}")

    @staticmethod
    def _delete_path(path: str, description: str):
        """
        删除目录，支持 Windows 文件锁定重试
        """
        import gc
        import time
        from pathlib import Path

        target = Path(path)
        if not target.exists():
            print(f"警告[FileStore._delete_path]：{description}不存在: {path}")
            return

        max_retries = 3
        for i in range(max_retries):
            try:
                shutil.rmtree(target)
                print(f"信息[FileStore._delete_path]：成功删除{description}: {path}")
                return
            except (PermissionError, OSError) as e:
                if i < max_retries - 1:
                    print(f"警告[FileStore._delete_path]：删除{description}失败，1秒后重试... ({i+1}/{max_retries})")
                    time.sleep(1)
                    gc.collect()
                else:
                    print(f"错误[FileStore._delete_path]：删除{description}失败（文件被占用）: {path}")
                    print("提示：请手动删除该目录，或稍后删除")

    @staticmethod
    def _delete_file(path: str, description: str):
        """
        删除单个文件，支持 Windows 文件锁定重试
        """
        import gc
        import time
        from pathlib import Path

        target = Path(path)
        if not target.exists():
            print(f"警告[FileStore._delete_file]：{description}不存在: {path}")
            return

        max_retries = 3
        for i in range(max_retries):
            try:
                target.unlink()
                print(f"信息[FileStore._delete_file]：成功删除{description}: {path}")
                return
            except (PermissionError, OSError) as e:
                if i < max_retries - 1:
                    print(f"警告[FileStore._delete_file]：删除{description}失败，1秒后重试... ({i+1}/{max_retries})")
                    time.sleep(1)
                    gc.collect()
                else:
                    print(f"错误[FileStore._delete_file]：删除{description}失败（文件被占用）: {path}")
                    print("提示：请手动删除该文件，或稍后删除")