"""
实现人：

RAG 服务（RAGService）
基于 LangChain 的检索增强生成服务封装，
整合 VectorDB、KeywordDB、Reranker 三大组件，
提供文档管理、向量检索、关键词检索、混合检索（RRF + Rerank）等能力。
"""
import os
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
        self.vector_db_path = os.path.join(self.RAG_store_path, config.VECTOR_DB_PATH)
        # 拼接关键词库存储位置
        self.keyword_db_path = os.path.join(self.RAG_store_path, config.KEYWORD_DB_PATH)
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
        try:
            # 添加到向量数据库
            vector_success = self.vector_db.add_document(document)
            if not vector_success:
                print(f"警告[RAGService.add_document]：文档添加到向量数据库失败")
                return False

            # 添加到关键词数据库
            keyword_success = self.keyword_db.add_document(document)
            if not keyword_success:
                print(f"警告[RAGService.add_document]：文档添加到关键词数据库失败")
                # 尝试从向量数据库中删除已添加的文档以保持一致性
                if 'md5' in document.metadata:
                    self.vector_db.delete_document(document.metadata['md5'])
                return False

            return True
        except Exception as e:
            print(f"错误[RAGService.add_document]：文档添加文档失败: {e}")
            return False

    def add_documents(self, documents: list[Document]) -> bool:
        """
        批量添加文档，默认传入的文档的md5信息保存在metadata中作为文档索引，内部不用去重
        分别向向量库和关键词库添加文档
        Args:
            documents: 要添加的文档列表
        Returns:
            bool: 是否添加成功
        """
        try:
            # 批量添加到向量数据库
            vector_success = self.vector_db.add_documents(documents)
            if not vector_success:
                print(f"警告[RAGService.add_documents]：文档批量添加到向量数据库失败")
                return False

            # 批量添加到关键词数据库
            keyword_success = self.keyword_db.add_documents(documents)
            if not keyword_success:
                print(f"警告[RAGService.add_documents]：文档批量添加到关键词数据库失败")
                # 尝试从向量数据库中删除已添加的文档以保持一致性
                md5_list = [doc.metadata['md5'] for doc in documents if 'md5' in doc.metadata]
                if md5_list:
                    self.vector_db.delete_documents(md5_list)
                return False

            return True
        except Exception as e:
            print(f"错误[RAGService.add_documents]：文档批量添加文档失败: {e}")
            return False

    def delete_document(self, md5: str) -> bool:
        """
        删除文档，传入文档的md5索引，分别从向量数据库和关键词库中删除文档
        Args:
            md5: 文档的md5值
        Returns:
            bool: 是否删除成功
        """
        try:
            # 从向量数据库删除
            vector_success = self.vector_db.delete_document(md5)

            # 从关键词数据库删除
            keyword_success = self.keyword_db.delete_document(md5)

            # 只有两者都成功才返回True
            if vector_success and keyword_success:
                return True
            else:
                if not vector_success:
                    print(f"警告[RAGService.delete_document]：从向量数据库删除文档 {md5} 失败")
                if not keyword_success:
                    print(f"警告[RAGService.delete_document]：从关键词数据库删除文档 {md5} 失败")
                return False
        except Exception as e:
            print(f"错误[RAGService.delete_document]：文档批量删除文档失败: {e}")
            return False

    def delete_documents(self, md5_list: list[str]) -> bool:
        """
        批量删除文档，传入文档的md5索引，分别从向量数据库和关键词库中删除文档
        Args:
            md5_list: 文档的md5值列表
        Returns:
            bool: 是否删除成功
        """
        try:
            # 从向量数据库批量删除
            vector_success = self.vector_db.delete_documents(md5_list)

            # 从关键词数据库批量删除
            keyword_success = self.keyword_db.delete_documents(md5_list)

            # 只有两者都成功才返回True
            if vector_success and keyword_success:
                return True
            else:
                if not vector_success:
                    print(f"警告[RAGService.delete_documents]：从向量数据库批量删除文档失败")
                if not keyword_success:
                    print(f"警告[RAGService.delete_documents]：从关键词数据库批量删除文档失败")
                return False
        except Exception as e:
            print(f"错误[RAGService.delete_documents]：文档批量删除文档失败: {e}")
            return False

    def _vector_search(self, query:str, k:int = config.VECTOR_SEARCH_DEFAULT_K) -> list[Document]:
        """
        向量检索
        Args:
            query: 检索的问题
            k: 返回的文档数量，默认config.VECTOR_SEARCH_DEFAULT_K
        Returns:
            list[Document]: 检索得到的文档
        """
        try:
            return self.vector_db.search(query=query, k=k)
        except Exception as e:
            print(f"向量检索失败: {e}")
            return []

    def _keyword_search(self, query:str, k:int = config.KEYWORD_SEARCH_DEFAULT_K) -> list[Document]:
        """
        关键词检索
        Args:
            query: 检索的问题
            k: 返回的文档数量，默认config.KEYWORD_SEARCH_DEFAULT_K
        Returns:
            list[Document]: 检索得到的文档
        """
        try:
            return self.keyword_db.search(query=query, k=k)
        except Exception as e:
            print(f"错误[RAGService._keyword_search]：关键词检索失败: {e}")
            return []

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
        try:
            # 调用向量检索和关键词检索，获取较多的候选文档用于重排序
            # 获取的文档数量使用配置中的值
            vector_results = self.vector_db.search(
                query=query,
                k=config.VECTOR_SEARCH_DEFAULT_K
            )
            keyword_results = self.keyword_db.search(
                query=query,
                k=config.KEYWORD_SEARCH_DEFAULT_K
            )

            # 使用 Reranker 进行混合检索（RRF融合 + 重排序）
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
            print(f"错误[RAGService._hybrid_search]：混合检索失败: {e}")
            # 降级策略：如果混合检索失败，返回向量检索结果
            return self._vector_search(query=query, k=k)

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
                print(f"警告[RAGService.search]：不支持的检索模式 '{mod}'，使用默认的 hybrid 模式")
                return self._hybrid_search(
                    query=query,
                    k=k,
                    vector_weight=vector_weight,
                    keyword_weight=keyword_weight
                )
        except Exception as e:
            print(f"错误[RAGService.search]：检索失败: {e}")
            return []

    def delete_me(self):
        """
        删除RAG服务，包括向量库和关键词库的持久化存储
        """
        try:
            # 删除向量数据库
            self.vector_db.delete_me()
            print("信息[RAGService.delete_me]：向量数据库已删除")
        except Exception as e:
            print(f"错误[RAGService.delete_me]：删除向量数据库失败: {e}")

        try:
            # 删除关键词数据库
            self.keyword_db.delete_me()
            print("信息[RAGService.delete_me]：关键词数据库已删除")
        except Exception as e:
            print(f"错误[RAGService.delete_me]：删除关键词数据库失败: {e}")

        # 清理对象引用，防止后续调用出错
        self.vector_db = None
        self.keyword_db = None
        self.reranker = None
        print("信息[RAGService.delete_me]：RAGService 对象引用已清理")