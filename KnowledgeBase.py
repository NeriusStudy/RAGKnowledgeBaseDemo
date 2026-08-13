"""
实现人：

知识库类
"""
import config
from FileStore import FileStore
from RAGService import RAGService
from typing import List
from langchain_core.documents import Document

class KnowledgeBase:
    def __init__(self, name: str,
                 knowledgebase_store_path: str,
                 file_store_path: str,
                 document_store_path: str,
                 md5_store_path: str,
                 file_document_map_store_path: str,
                 RAG_store_path: str,
                 embedding_model_name: str = config.EMBEDDING_MODEL_NAME,
                 rerank_model_name: str = config.RERANK_MODEL_NAME,
                 splitter_chunk_size: int = config.SPLITTER_CHUNK_SIZE,
                 splitter_chunk_overlap: int = config.SPLITTER_CHUNK_OVERLAP,
                 splitter_separaters: List[str] = config.SEPLITTER_SEPARATERS,
                 splitter_length_function=config.SPLITTER_LENGTH_FUNCTION,
                 ):
        """
        初始化知识库（KnowledgeBase）
        Args:
            name: （必填）知识库名称
            knowledgebase_store_path: （选填，默认data/name/）知识库持久化存储路径，由于每个知识库都单独列一个目录存储，
            所以这里的路径需要上层封装好传入否则可能会和其他知识库的路径重复，所以这里没有默认值
            file_store_path: （选填，默认data/name/file_store/files/）文件存储路径，用于存储文件内容
            document_store_path: （选填，默认data/name/file_store/documents/）文档存储路径，用于存储切分后的文档
            md5_store_path: （选填，默认data/name/file_store/md5.txt）md5存储路径，用于存储文档的md5值
            file_document_map_store_path: （选填，默认data/name/file_store/file_document_map.txt）文件文档映射存储路径，用于存储文件和文档的对应关系
            RAG_store_path: （选填，默认data/name/RAG_store）RAG存储路径，用于存储RAG模型的参数
            embedding_model_name: （选填，默认config.EMBEDDING_MODEL_NAME）嵌入模型名称，用于将文档转换为向量
            rerank_model_name: （选填，默认config.RERANK_MODEL_NAME）重排模型名称，用于对文档进行重排
            splitter_chunk_size: （选填，默认config.SPLITTER_CHUNK_SIZE）切分器大小，用于将文件内容切分为文档
            splitter_chunk_overlap: （选填，默认config.SPLITTER_CHUNK_OVERLAP）切分器重叠大小，用于将文件内容切分为文档
            splitter_separaters: （选填，默认config.SEPLITTER_SEPARATERS）切分器分隔符，用于将文件内容切分为文档
            splitter_length_function: （选填，默认config.SPLITTER_LENGTH_FUNCTION）切分器长度函数，用于将文件内容切分为文档
        """
        self.name = name

        self.knowledgebase_store_path = knowledgebase_store_path
        if self.knowledgebase_store_path is None:
            self.knowledgebase_store_path = f"data/{self.name}/"

        self.file_store_path = file_store_path
        if self.file_store_path is None:
            self.file_store_path = self.knowledgebase_store_path + config.FILE_STORE_PATH

        self.document_store_path = document_store_path
        if self.document_store_path is None:
            self.document_store_path = self.knowledgebase_store_path + config.DOCUMENT_STORE_PATH

        self.md5_store_path = md5_store_path
        if self.md5_store_path is None:
            self.md5_store_path = self.knowledgebase_store_path + config.MD5_STORE_PATH

        self.file_document_map_store_path = file_document_map_store_path
        if self.file_document_map_store_path is None:
            self.file_document_map_store_path = self.knowledgebase_store_path + config.FILE_DOCUMENT_MAP_STORE_PATH

        self.RAG_store_path = RAG_store_path
        if self.RAG_store_path is None:
            self.RAG_store_path = self.knowledgebase_store_path + config.RAG_STORE_PATH

        self.embedding_model_name = embedding_model_name
        self.rerank_model_name = rerank_model_name
        self.splitter_chunk_size = splitter_chunk_size
        self.splitter_chunk_overlap = splitter_chunk_overlap
        self.splitter_separaters = splitter_separaters
        self.splitter_length_function = splitter_length_function
        # 初始化文件存储
        self.file_store = FileStore(self.file_store_path, self.document_store_path, self.md5_store_path, self.file_document_map_store_path,
                                self.splitter_chunk_size, self.splitter_chunk_overlap, self.splitter_separaters, self.splitter_length_function)
        # 初始化RAG服务
        self.rag_service = RAGService(self.RAG_store_path, self.embedding_model_name, self.rerank_model_name)

    def get_name(self) -> str:
        """
        获取知识库名称
        Returns:
            str: 知识库名称
        """
        return self.name

    def get_file_store_splitter_chunk_size(self) -> int:
        """
        获取文件存储中的切分器文本块最大字符数
        Returns:
            int: 文件存储中的切分器文本块最大字符数
        """
        return self.file_store.get_splitter_chunk_size()

    def get_file_store_splitter_chunk_overlap(self) -> int:
        """
        获取文件存储中的切分器文本块重叠字符数
        Returns:
            int: 文件存储中的切分器文本块重叠字符数
        """
        return self.file_store.get_splitter_chunk_overlap()

    def get_file_store_splitter_separaters(self) -> List[str]:
        """
        获取文件存储中的切分器分隔符列表
        Returns:
            List[str]: 文件存储中的切分器分隔符列表
        """
        return self.file_store.get_splitter_separaters()

    def get_file_store_splitter_length_function(self):
        """
        获取文件存储中的切分器长度函数
        Returns:
            计算文本长度的函数
        """
        return self.file_store.get_splitter_length_function()

    def get_RAG_service_embedding_model_name(self) -> str:
        """
        获取RAG服务中的嵌入模型名称
        Returns:
            str: RAG服务中的嵌入模型名称
        """
        return self.rag_service.get_embedding_model_name()

    def get_RAG_service_rerank_model_name(self) -> str:
        """
        获取RAG服务中的重排模型名称
        Returns:
            str: RAG服务中的重排模型名称
        """
        return self.rag_service.get_rerank_model_name()

    def add_file(self, file) -> bool:
        """
        添加文件到文件存储
        Args:
            file: 待添加的文件
        Returns:
            bool: 是否添加成功
        """
        # 保存文件到文件存储，获取切分后的文档列表
        documents = self.file_store.save_file(file)
        if not documents:
            return False
        # 将文档添加到 RAG 服务（向量库和关键词库）
        return self.rag_service.add_documents(documents)

    def add_files(self, files) -> bool:
        """
        批量添加文件到文件存储
        Args:
            files: 待添加的文件列表
        Returns:
            bool: 是否添加成功
        """
        for file in files:
            if not self.add_file(file):
                return False
        return True

    def get_file(self, file_name: str):
        """
        获取文件存储中的文件
        Args:
            file_name: 文件名称
        Returns:
            !!!!!!!!!!!!!!!! todo:文件类型处理在FileStore类中实现
        """
        return self.file_store.get_file(file_name)

    def get_all_files(self) -> List[str]:
        """
        获取文件存储中的所有文件名称
        Returns:
            List[str]: 所有文件名称列表
        """
        return self.file_store.get_all_file_name()

    def delete_file(self, file_name: str) -> bool:
        """
        删除文件存储中的文件
        Args:
            file_name: 文件名称
        Returns:
            bool: 是否删除成功
        """
        # 从文件存储中删除文件，获取被删除文档的 md5 列表
        md5_list = self.file_store.delete_file(file_name)
        if md5_list is None:
            return False
        # 从 RAG 服务中删除对应的文档
        if md5_list:
            self.rag_service.delete_documents(md5_list)
        return True

    def search(self, query: str, mod: str = "hybrid", k: int = config.RAG_SEARCH_DEFAULT_K,
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
        return self.rag_service.search(
            query=query, mod=mod, k=k,
            vector_weight=vector_weight,
            keyword_weight=keyword_weight,
        )

    def delete_me(self):
        """
        删除所有持久化存储
        """
        self.file_store.delete_me()
        self.rag_service.delete_me()
