"""
实现人：

关键词数据库
基于 LangChain 的 BM25Retriever 实现关键词检索，
集成文档持久化存储、关键词相似度检索等功能。
文档的 MD5 由上层统一管理，KeywordDB 不再包含内部去重逻辑。
"""
import config
from typing import Dict, Optional
from langchain_community.retrievers.bm25 import BM25Retriever
from langchain_core.documents import Document

class KeywordDB:
    def __init__(self, keyword_db_store_path: str):
        """
        初始化关键词数据库（KeywordDB）
        Args:
            keyword_db_store_path: BM25Retriever 关键词数据库持久化存储路径，由于每个知识库都单独列一个目录存储，
            所以这里的路径需要上层封装好传入否则可能会和其他知识库的路径重复，所以这里没有默认值
        """
        # 存储路径，上层必须传入
        self.keyword_db_store_path = keyword_db_store_path
        # 加载文档，从存储路径中读取所有文档
        # 文档的metadata中的md5作为索引，文档作为值
        self._documents: Dict[str, Document] = self._load_documents()
        # 初始化BM25Retriever，用于关键词检索
        self._retriever: Optional[BM25Retriever] = self._build_retriever()

    def _load_documents(self) -> Dict[str, Document]:
        """
        从持久化目录中读入持久化存储的文档
        """
        pass

    def _build_retriever(self) -> BM25Retriever:
        """
        初始化BM25Retriever
        """
        pass

    def add_document(self, document: Document) -> bool:
        """
        添加文档到关键词数据库
        Args:
            document: 待添加的文档
        Returns:
            bool: 是否添加成功
        """
        pass

    def add_documents(self, document: list[Document]) -> bool:
        """
        批量添加文档到关键词数据库
        Args:
            document: 待添加的文档
        Returns:
            bool: 是否添加成功
        """
        pass

    def delete_document(self, md5: str) -> bool:
        """
        删除关键词数据库中的文档
        Args:
            md5: 文档的md5值
        Returns:
            bool: 是否删除成功
        """
        pass

    def delete_documents(self, md5: list[str]) -> bool:
        """
        批量删除关键词数据库中的文档
        Args:
            md5: 文档的md5值
        Returns:
            bool: 是否删除成功
        """
        pass

    def search(self, query: str, k: int = config.KEYWORD_SEARCH_DEFAULT_K) -> list[Document]:
        """
        进行关键词检索
        Args:
            query: 检索关键词
            k: （可选）返回的文档数量，默认值为 config.KEYWORD_SEARCH_DEFAULT_K
        Returns:
            list[Document]: 检索到的文档列表，失败返回None
        """
        pass

    def delete_me(self):
        """
        删除关键词数据库，包括所有持久化存储
        """
        pass
