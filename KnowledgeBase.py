"""
知识库类
"""
import os
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
            self.file_store_path = os.path.join(self.knowledgebase_store_path, config.FILE_STORE_PATH)

        self.document_store_path = document_store_path
        if self.document_store_path is None:
            self.document_store_path = os.path.join(self.knowledgebase_store_path, config.DOCUMENT_STORE_PATH)

        self.md5_store_path = md5_store_path
        if self.md5_store_path is None:
            self.md5_store_path = os.path.join(self.knowledgebase_store_path, config.MD5_STORE_PATH)

        self.file_document_map_store_path = file_document_map_store_path
        if self.file_document_map_store_path is None:
            self.file_document_map_store_path = os.path.join(self.knowledgebase_store_path, config.FILE_DOCUMENT_MAP_STORE_PATH)

        self.RAG_store_path = RAG_store_path
        if self.RAG_store_path is None:
            self.RAG_store_path = os.path.join(self.knowledgebase_store_path, config.RAG_STORE_PATH)

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

    def add_file(self, file_path: str, file_name: str = None) -> bool:
        """
        添加文件到知识库
        流程：FileStore 存储文件 -> 切分为 Document -> RAGService 存储到向量库和关键词库
        Args:
            file_path: 待添加的文件路径
            file_name: 文件名称（可选，默认使用文件路径中的文件名）
        Returns:
            bool: 是否添加成功
        """
        try:
            # 1. FileStore 保存文件并切分为 Document
            split_docs = self.file_store.save_file(file_path, file_name)

            if not split_docs:
                print(f"错误[KnowledgeBase.add_file] 文件保存失败或被去重: {file_name or file_path}")
                return False

            # 2. 将切分后的文档添加到 RAGService
            success = self.rag_service.add_documents(split_docs)

            if not success:
                # 如果 RAG 存储失败，需要回滚 FileStore 的操作
                actual_file_name = file_name or os.path.basename(file_path)
                self.file_store.delete_file(actual_file_name)
                print(f"错误[KnowledgeBase.add_file] RAG 存储失败，已回滚文件存储: {actual_file_name}")
                return False

            print(f"信息[KnowledgeBase.add_file] 文件添加成功: {file_name or file_path}, {len(split_docs)} 个文档")
            return True

        except Exception as e:
            print(f"错误[KnowledgeBase.add_file] 文件添加失败: {e}")
            return False

    def add_files(self, file_paths: List[str]) -> bool:
        """
        批量添加文件到知识库
        Args:
            file_paths: 待添加的文件路径列表
        Returns:
            bool: 是否全部添加成功
        """
        success_count = 0
        fail_count = 0

        for file_path in file_paths:
            if self.add_file(file_path):
                success_count += 1
            else:
                fail_count += 1

        print(f"信息[KnowledgeBase.add_files] 批量添加完成: 成功 {success_count}, 失败 {fail_count}")
        return fail_count == 0

    def get_file(self, file_name: str) -> str:
        """
        获取文件存储中的文件路径
        Args:
            file_name: 文件名称
        Returns:
            str: 文件的完整路径，如果文件不存在则返回 None
        """
        return self.file_store.get_file(file_name)

    def get_all_files(self) -> List[str]:
        """
        获取文件存储中的所有文件名称
        Returns:
            List[str]: 所有文件名称列表
        """
        return self.file_store.get_all_file_name()

    def get_file_documents(self, file_name: str) -> List[Document]:
        """
        根据文件名获取该文件切分后的所有文档
        Args:
            file_name: 文件名称
        Returns:
            List[Document]: 该文件切分后的文档列表
        """
        return self.file_store.get_documents_by_file(file_name)

    def delete_file(self, file_name: str) -> bool:
        """
        删除文件及其关联的所有文档
        流程：FileStore 删除文件 -> 获取文档 MD5 列表 -> RAGService 批量删除文档
        Args:
            file_name: 文件名称
        Returns:
            bool: 是否删除成功
        """
        try:
            # 1. 从 FileStore 删除文件，返回被删除文档的 MD5 列表
            md5_list = self.file_store.delete_file(file_name)

            if not md5_list:
                print(f"错误[KnowledgeBase.delete_file] 文件不存在或无关联文档: {file_name}")
                return False

            # 2. 从 RAGService 批量删除所有文档
            success = self.rag_service.delete_documents(md5_list)

            if success:
                print(f"信息[KnowledgeBase.delete_file] 文件删除成功: {file_name}, 删除了 {len(md5_list)} 个文档")
                return True
            else:
                print(f"错误[KnowledgeBase.delete_file] RAG 文档删除失败: {file_name}")
                return False

        except Exception as e:
            print(f"错误[KnowledgeBase.delete_file] 文件删除失败: {e}")
            return False

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
        return self.rag_service.search(query, mod, k, vector_weight, keyword_weight)

    def search_as_strings(self, query: str, mod: str = "hybrid", k: int = config.RAG_SEARCH_DEFAULT_K,
                          vector_weight: float = 0.5,
                          keyword_weight: float = 0.5) -> List[str]:
        """
        检索并返回字符串列表
        Args:
            query: 检索的问题
            mod: 模型类型，vector、keyword、hybrid，默认hybrid
            k: 返回的文档数量，默认config.RAG_SEARCH_DEFAULT_K
            vector_weight: 向量权重，默认0.5
            keyword_weight: 关键词权重，默认0.5
        Returns:
            List[str]: 检索得到的文档内容字符串列表
        """
        docs = self.search(query, mod, k, vector_weight, keyword_weight)
        return [doc.page_content for doc in docs]

    def delete_me(self):
        """
        删除知识库的所有持久化存储
        """
        import shutil

        try:
            # 先删除 FileStore 和 RAGService 的内部数据
            try:
                self.rag_service.delete_me()
            except Exception as e:
                print(f"错误[KnowledgeBase.delete_me] 删除 RAG 服务失败: {e}")

            # 删除知识库根目录
            if os.path.exists(self.knowledgebase_store_path):
                shutil.rmtree(self.knowledgebase_store_path)
                print(f"信息[KnowledgeBase.delete_me] 知识库已删除: {self.name}")
            else:
                print(f"错误[KnowledgeBase.delete_me] 知识库路径不存在: {self.knowledgebase_store_path}")
        except Exception as e:
            print(f"错误[KnowledgeBase.delete_me] 删除知识库失败: {e}")

        # 清理对象引用，防止后续调用出错
        self.file_store = None
        self.rag_service = None
        print("信息[KnowledgeBase.delete_me] KnowledgeBase 对象引用已清理")