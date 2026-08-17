"""
去重器（Deduplicator）
对文件标题内容进行 MD5 去重，
避免重复文本被重复写入数据库。
"""
from typing import Optional
import hashlib
import os
from langchain_core.documents import Document

class Deduplicator:
    def __init__(self, md5_store_path: str):
        """
        初始化去重器
        Args:
            md5_store_path: 存储 MD5 数据的文件路径（.txt 格式），
                            文件中每一行存储一个 MD5 哈希值
        """
        self.md5_store_path = md5_store_path

    def _load_md5_set(self) -> set:
        """
        从存储文件中加载所有 MD5 值到集合中
        Returns:
            包含所有已存储 MD5 的集合
        """
        md5_set = set()
        if os.path.exists(self.md5_store_path):
            try:
                with open(self.md5_store_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            md5_set.add(line)
            except Exception as e:
                print(f"错误[Deduplicator._load_md5_set] 读取 MD5 文件失败: {e}")
        return md5_set

    @staticmethod
    def str_to_md5(text: str) -> Optional[str]:
        """
        将字符串转换为 MD5 哈希值
        Args:
            text: 需要转换的字符串
        Returns:
            MD5 格式的字符串（32位十六进制），失败时返回 None
        """
        try:
            return hashlib.md5(text.encode("utf-8")).hexdigest()
        except Exception as e:
            print(f"错误[Deduplicator.str_to_md5] 字符串转 MD5 失败: {e}")
            return None

    def check_if_deduplicate_md5(self, md5: str) -> bool:
        """
        判断传入的 MD5 是否在存储文件中已存在
        Args:
            md5: 要检查的 MD5 哈希值
        Returns:
            如果 MD5 已存在返回 True，否则返回 False
        """
        return md5 in self._load_md5_set()

    def check_if_deduplicate_str(self, text: str) -> bool:
        """
        判断传入字符串对应的 MD5 是否已在存储文件中
        Args:
            text: 要检查的字符串
        Returns:
            如果字符串对应的 MD5 已存在返回 True，否则返回 False
        """
        md5 = self.str_to_md5(text)
        if md5 is None:
            return False
        return self.check_if_deduplicate_md5(md5)

    def save_md5(self, md5: str) -> bool:
        """
        将 MD5 存入存储文件
        Args:
            md5: 要存储的 MD5 哈希值
        Returns:
            成功返回 True，失败返回 False 并输出错误信息
            如果 MD5 已存在，返回 True 并输出提示
        """
        if self.check_if_deduplicate_md5(md5):
            print(f"警告[Deduplicator.save_md5] MD5 {md5} 已存在，跳过存储")
            return True

        try:
            os.makedirs(os.path.dirname(self.md5_store_path), exist_ok=True)
            with open(self.md5_store_path, "a", encoding="utf-8") as f:
                f.write(md5 + "\n")
            return True
        except Exception as e:
            print(f"错误[Deduplicator.save_md5] 保存 MD5 失败: {e}")
            return False

    def save_str(self, text: str) -> bool:
        """
        保存字符串对应的 MD5（去重存储）
        将字符串转为 MD5，检查是否已存在，若不存在则写入文件。
        Args:
            text: 要保存的字符串
        Returns:
            成功存入或已存在返回 True，失败返回 False
        """
        md5 = self.str_to_md5(text)
        if md5 is None:
            return False
        return self.save_md5(md5)

    def delete_md5(self, md5: str) -> bool:
        """
        从存储文件中删除指定的 MD5
        Args:
            md5: 要删除的 MD5 哈希值
        Returns:
            成功删除返回 True；如果文件中不存在该 MD5 返回 True 并输出提示；
            其他失败情况返回 False
        """
        md5_set = self._load_md5_set()
        if md5 not in md5_set:
            print(f"警告[Deduplicator.delete_md5] MD5 {md5} 不存在，无需删除")
            return True

        md5_set.discard(md5)
        try:
            os.makedirs(os.path.dirname(self.md5_store_path), exist_ok=True)
            with open(self.md5_store_path, "w", encoding="utf-8") as f:
                for m in md5_set:
                    f.write(m + "\n")
            return True
        except Exception as e:
            print(f"错误[Deduplicator.delete_md5] 删除 MD5 失败: {e}")
            return False

    def delete_str(self, text: str) -> bool:
        """
        删除字符串对应的 MD5
        Args:
            text: 要删除的字符串
        Returns:
            成功返回 True，失败返回 False
        """
        md5 = self.str_to_md5(text)
        if md5 is None:
            return False
        return self.delete_md5(md5)

    # ========== Document 级别方法 ==========

    @staticmethod
    def document_to_md5(document: Document) -> Optional[str]:
        """
        将 Document 对象转为 MD5
        使用 document 的 page_content 计算 MD5 哈希值。
        Args:
            document: 待转换的 LangChain Document 对象
        Returns:
            MD5 格式的字符串，失败返回 None
        """
        return Deduplicator.str_to_md5(document.page_content)

    def check_if_deduplicate_document(self, document: Document) -> bool:
        """
        检查 Document 是否已被记录（其 MD5 是否已存在）
        Args:
            document: 要检查的 LangChain Document 对象
        Returns:
            已存在返回 True，否则返回 False
        """
        md5 = self.document_to_md5(document)
        if md5 is None:
            return False
        return self.check_if_deduplicate_md5(md5)

    def save_document(self, document: Document) -> bool:
        """
        保存 Document 的 MD5 到持久化存储
        将 Document 的 page_content 转为 MD5，
        若该 MD5 已存在则跳过，否则写入存储文件。
        Args:
            document: 要保存的 LangChain Document 对象
        Returns:
            成功（或已存在）返回 True，失败返回 False
        """
        md5 = self.document_to_md5(document)
        if md5 is None:
            return False
        return self.save_md5(md5)

    def delete_document(self, document: Document) -> bool:
        """
        从持久化存储中删除 Document 对应的 MD5
        Args:
            document: 要删除的 LangChain Document 对象
        Returns:
            成功返回 True，失败返回 False
        """
        md5 = self.document_to_md5(document)
        if md5 is None:
            return False
        return self.delete_md5(md5)
