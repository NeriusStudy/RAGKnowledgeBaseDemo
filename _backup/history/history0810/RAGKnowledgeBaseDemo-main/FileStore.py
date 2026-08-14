"""
实现人：

文件存储类
用于存储文件内容
利用deduplicator实现文件去重，对文件名进行去重，避免重复存储相同文件
利用splitter将文件内容分割为文档，每个文档对应一个md5值，用于唯一标识文档
存储文件和切分的文档的对应关系
"""
from typing import List, Optional
from langchain_core.documents import Document
from Splitter import Splitter
from Deduplicator import Deduplicator
import config

class FileStore:
    def __init__(self,
                 file_store_path: str,
                 document_store_path: str,
                 md5_store_path: str,
                 file_document_map_store_path: str,
                 splitter_chunk_size: int = config.SPLITTER_CHUNK_SIZE,
                 splitter_chunk_overlap: int = config.SPLITTER_CHUNK_OVERLAP,
                 splitter_separaters: List[str] = config.SEPLITTER_SEPARATERS,
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
        pass

    def _file_to_document(self, file) -> Document:
        """
        解析文件成为Document
        """
        pass

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

    def save_file(file) -> List[Document]:
        """
        保存文件内容到存储路径，需要对传入的文件根据文件名称进行去重处理，如果重复则不再保存
        切分文件内容为文档，每个文档对应一个md5值，用于唯一标识文档
        保存文件和文档的对应关系
        Args:
            file: 待保存的文件
        Returns:
            List[Document]: 切分后的文档列表，其中每个文档的md5保存在Document的metadata中
        """

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
        pass

    def get_document_md5_from_file_name(self, file_name: str) -> List[str]:
        """
        根据文件名称获取文件的所有对应的文档的md5列表
        Args:
            file_name: 文件名称
        Returns:
            List[str]: 文件的所有对应的文档的md5列表
        """
        pass

    def get_file(self, file_name: str):
        """
        根据文件名称获取文件内容
        Args:
            file_name: 文件名称
        Returns:
            文件
            !!!!!!!!!!!!!!!!!!!!! to think: 如何传回一个文件类，以及支持哪些文件类型，这些文件类型以什么格式传输
        """
        pass

    def get_all_file_name(self) -> List[str]:
        """
        获取所有文件名称
        Returns:
            List[str]: 所有文件名称列表
        """
        pass

    def delete_me(self):
        """
        删除所有持久化存储
        """