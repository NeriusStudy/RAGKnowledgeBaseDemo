"""
实现人：

向量数据库（VectorDB）
基于 LangChain 的 DashScopeEmbeddings + Chroma 实现，
集成向量化、向量存储、向量检索等功能，嵌入模型在类内配置，上层不感知，
APIKEY配置在环境变量中。
文档的 MD5 由上层统一管理，默认传入的文档Document类的metadata中有md5作为存储索引，
VectorDB 不再包含内部去重逻辑。
"""
import config
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

class VectorDB:
    def __init__(self, vector_db_store_path: str, embedding_model_name: str = config.EMBEDDING_MODEL_NAME):
        """
        初始化向量数据库（VectorDB）
        Args:
            vector_db_store_path: Chroma 向量数据库持久化存储路径，由于每个知识库都单独列一个目录存储，
            所以这里的路径需要上层封装好传入否则可能会和其他知识库的路径重复，所以这里没有默认值

            embedding_model_name: （可选）嵌入模型名称，默认值为 config.EMBEDDING_MODEL_NAME
        """
        # 存储路径，上层必须传入
        self.vector_db_store_path = vector_db_store_path
        # 初始化嵌入模型，默认使用的阿里云百炼模型名称在config中定义
        self.embedding_model_name = embedding_model_name
        self.embedding_mode = DashScopeEmbeddings(
            model=self.embedding_model_name
        )
        # 初始化向量数据库，嵌入模型需要统一
        self.vector_db = Chroma(
            embedding_function=self.embedding_mode,
            persist_directory=vector_db_store_path,
        )

    def get_embedding_model_name(self) -> str:
        """
        获取当前使用的嵌入模型名称
        Returns:
            str: 当前使用的嵌入模型名称
        """
        return self.embedding_model_name

    def str_to_vector(self, text: str) -> list[float]:
        """
        将字符串转换为向量
        Args:
            text: 待转换的字符串
        Returns:
            list[float]: 转换后的向量，失败返回None
        """
        return self.embedding_mode.embed_query(text)

    def document_to_vector(self, document: Document) -> list[float]:
        """
        将文档转换为向量
        Args:
            document: 待转换的文档，文档内容在document.page_content中
        Returns:
            list[float]: 转换后的向量，失败返回None
        """
        return self.embedding_mode.embed_query(document.page_content)

    def add_document(self, document: Document) -> bool:
        """
        添加文档到向量数据库
        Args:
            document: 待添加的文档，文档内容在document.page_content中，文档存储索引在document.metadata.md5中,
            上层保证传入的文档无重复，使用Chroma存储
        Returns:
            bool: 是否添加成功
        """
        pass

    def add_documents(self, document: list[Document]) -> bool:
        """
        批量添加文档到向量数据库
        Args:
            document: 待添加的文档，文档内容在document.page_content中，文档存储索引在document.metadata.md5中,
            上层保证传入的文档无重复，使用Chroma存储
        Returns:
            bool: 是否添加成功
        """
        pass

    def delete_document(self, md5: str) -> bool:
        """
        删除文档
        Args:
            md5: 文档的md5值，用于唯一标识文档
        Returns:
            bool: 是否删除成功
        """
        pass

    def delete_documents(self, md5: list[str]) -> bool:
        """
        批量删除文档
        Args:
            md5: 文档的md5值，用于唯一标识文档
        Returns:
            bool: 是否删除成功
        """
        pass

    def search(self, query: str, k: int = config.VECTOR_SEARCH_DEFAULT_K) -> list[Document]:
        """
        搜索向量数据库
        Args:
            query: 搜索查询的字符串
            k: （可选）返回的文档数量，默认值为 config.VECTOR_SEARCH_DEFAULT_K
        Returns:
            list[Document]: 搜索到的文档列表，失败返回None
        """
        pass

    def delete_me(self):
        """
        删除当前向量数据库，包括所有的持久化存储文件
        """
        pass