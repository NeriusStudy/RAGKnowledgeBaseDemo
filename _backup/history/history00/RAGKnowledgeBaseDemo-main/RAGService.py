"""
实现人：

RAG 服务（RAGService）
基于 LangChain 的检索增强生成服务封装，
整合 VectorDB、KeywordDB、Reranker 三大组件，
提供文档管理、向量检索、关键词检索、混合检索（RRF + Rerank）等能力。
"""
import config
from langchain_core.documents import Document
from VectorDB import VectorDB
from KeywordDB import KeywordDB
from Reranker import Reranker

class RAGService:
    def __init__(self, RAG_store_path: str,
                 embedding_model_name: str = config.EMBEDDING_MODEL_NAME,
                 rerank_model_name: str = config.RERANK_MODEL_NAME):
        """
        初始化RAG服务
        Args:
            RAG_store_path: RAG存储路径
            embedding_model_name: 嵌入模型名称，默认使用config.EMBEDDING_MODEL_NAME
            rerank_model_name: 重排序模型名称，默认使用config.RERANK_MODEL_NAME
        """
        self.RAG_store_path = RAG_store_path
        self.embedding_model_name = embedding_model_name
        self.rerank_model_name = rerank_model_name
        # 拼接向量数据库存储位置
        self.vector_db_path = self.RAG_store_path + config.VECTOR_DB_PATH
        # 拼接关键词库存储位置
        self.keyword_db_path = self.RAG_store_path + config.KEYWORD_DB_PATH
        # 初始化向量库
        self.vector_db = VectorDB(
            vector_db_store_path=self.vector_db_path,
            embedding_model_name=self.embedding_model_name
        )
        # 初始化关键词库
        self.keyword_db = KeywordDB(
            keyword_db_store_path=self.keyword_db_path,
        )
        # 初始化重排序器
        self.reranker = Reranker(
            rerank_model_name=self.rerank_model_name
        )

    def get_embedding_model_name(self) -> str:
        """
        获取嵌入模型名称
        Returns:
            str: 嵌入模型名称
        """
        return self.vector_db.get_embedding_model_name()

    def get_rerank_model_name(self) -> str:
        """
        获取重排序模型名称
        Returns:
            str: 重排序模型名称
        """
        return self.reranker.get_rerank_model_name()

    def add_document(self, document: Document) -> bool:
        """
        添加文档，默认传入的文档的md5信息保存在metadata中作为文档索引，内部不用去重
        分别向向量库和关键词库添加文档
        Args:
            document: 要添加的文档
        Returns:
            bool: 是否添加成功
        """
        pass

    def add_documents(self, document: list[Document]) -> bool:
        """
        批量添加文档，默认传入的文档的md5信息保存在metadata中作为文档索引，内部不用去重
        分别向向量库和关键词库添加文档
        Args:
            document: 要添加的文档
        Returns:
            bool: 是否添加成功
        """
        pass

    def delete_document(self, md5: str) -> bool:
        """
        删除文档，传入文档的md5索引，分别从向量数据库和关键词库中删除文档
        Args:
            md5: 文档的md5值
        Returns:
            bool: 是否删除成功
        """
        pass

    def delete_documents(self, md5: list[str]) -> bool:
        """
        批量删除文档，传入文档的md5索引，分别从向量数据库和关键词库中删除文档
        Args:
            md5: 文档的md5值
        Returns:
            bool: 是否删除成功
        """
        pass

    def _vector_search(self, query:str, k:int = config.VECTOR_SEARCH_DEFAULT_K) -> list[Document]:
        """
        向量检索
        Args:
            query: 检索的问题
            k: 返回的文档数量，默认config.VECTOR_SEARCH_DEFAULT_K
        Returns:
            list[Document]: 检索得到的文档
        """
        pass

    def _keyword_search(self, query:str, k:int = config.KEYWORD_SEARCH_DEFAULT_K) -> list[Document]:
        """
        关键词检索
        Args:
            query: 检索的问题
            k: 返回的文档数量，默认config.KEYWORD_SEARCH_DEFAULT_K
        Returns:
            list[Document]: 检索得到的文档
        """
        pass

    def _hybrid_search(self, query:str, k:int = config.HYBRID_SEARCH_DEFAULT_K,
                       vector_weight: float = 0.5,
                       keyword_weight: float = 0.5) -> list[Document]:
        """
        混合检索
        Args:
            query: 检索的问题
            k: 返回的文档数量，默认config.HYBRID_SEARCH_DEFAULT_K
            vector_weight: 向量权重，默认0.5
            keyword_weight: 关键词权重，默认0.5
        Returns:
            list[Document]: 检索得到的文档
        """
        pass

    def search(self, query:str, mod:str = "hybrid", k:int = config.RAG_SEARCH_DEFAULT_K,
               vector_weight: float = 0.5,
               keyword_weight: float = 0.5) -> list[Document]:
        """
        检索
        Args:
            query: 检索的问题
            mod: 模型类型，vector、keyword、hybrid，默认hybrid
            k: 返回的文档数量，默认config.RAG_SEARCH_DEFAULT_K
            vector_weight: 向量权重，默认0.5
            keyword_weight: 关键词权重，默认0.5
        Returns:
            list[Document]: 检索得到的文档
        """
        pass

    def delete_me(self):
        """
        删除RAG服务，包括向量库和关键词库的持久化存储
        """
        pass