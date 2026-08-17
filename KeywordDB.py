"""
实现人：

关键词数据库
基于 LangChain 的 BM25Retriever 实现关键词检索，
集成文档持久化存储、关键词相似度检索等功能。
文档的 MD5 由上层统一管理，KeywordDB 不再包含内部去重逻辑。
"""
import config
import pickle
import os
from pathlib import Path
from typing import Dict, Optional, List
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
        self.keyword_db_store_path = Path(keyword_db_store_path)
        # 持久化文件路径
        self.documents_file = self.keyword_db_store_path / "documents.pkl"

        # 创建存储目录
        self.keyword_db_store_path.mkdir(parents=True, exist_ok=True)

        # 加载文档，从存储路径中读取所有文档
        # 文档的metadata中的md5作为索引，文档作为值
        self._documents: Dict[str, Document] = self._load_documents()
        # 初始化BM25Retriever，用于关键词检索
        self._retriever: Optional[BM25Retriever] = self._build_retriever()

    def _load_documents(self) -> Dict[str, Document]:
        """
        从持久化目录中读入持久化存储的文档
        """
        try:
            if self.documents_file.exists():
                with open(self.documents_file, 'rb') as f:
                    documents_dict = pickle.load(f)
                print(f"信息[KeywordDB._load_documents] 成功加载 {len(documents_dict)} 条文档")
                return documents_dict
            else:
                print("信息[KeywordDB._load_documents] 未找到持久化文档，初始化空数据库")
                return {}
        except Exception as e:
            print(f"错误[KeywordDB._load_documents] 加载文档失败: {str(e)}，初始化空数据库")
            return {}

    def _save_documents(self) -> bool:
        """
        保存文档到持久化存储
        """
        try:
            with open(self.documents_file, 'wb') as f:
                pickle.dump(self._documents, f, protocol=pickle.HIGHEST_PROTOCOL)
            return True
        except Exception as e:
            print(f"错误[KeywordDB._save_documents] 保存文档失败: {str(e)}")
            return False

    def _build_retriever(self) -> Optional[BM25Retriever]:
        """
        初始化BM25Retriever
        """
        try:
            if not self._documents:
                # 空数据库，返回 None
                return None

            # 从字典中提取所有文档
            doc_list = list(self._documents.values())

            # 创建 BM25Retriever
            retriever = BM25Retriever.from_documents(doc_list)

            return retriever

        except Exception as e:
            print(f"错误[KeywordDB._build_retriever] 构建 BM25Retriever 失败: {str(e)}")
            return None

    def add_document(self, document: Document) -> bool:
        """
        添加文档到关键词数据库
        Args:
            document: 待添加的文档
        Returns:
            bool: 是否添加成功
        """
        try:
            # 检查文档是否包含 md5
            if 'md5' not in document.metadata:
                print("错误[KeywordDB.add_document]：文档 metadata 中缺少 md5 字段")
                return False

            md5 = document.metadata['md5']

            # 添加文档到内存字典
            self._documents[md5] = document

            # 重建 BM25Retriever
            self._retriever = self._build_retriever()

            # 持久化保存
            return self._save_documents()

        except Exception as e:
            print(f"错误[KeywordDB.add_document] 添加文档失败: {str(e)}")
            return False

    def add_documents(self, documents: List[Document]) -> bool:
        """
        批量添加文档到关键词数据库
        Args:
            documents: 待添加的文档列表
        Returns:
            bool: 是否添加成功
        """
        try:
            if not documents:
                print("警告[KeywordDB.add_documents]：文档列表为空")
                return True

            # 检查所有文档是否都包含 md5
            for doc in documents:
                if 'md5' not in doc.metadata:
                    print(f"错误[KeywordDB.add_documents]：文档 metadata 中缺少 md5 字段")
                    return False

            # 批量添加到内存字典
            for doc in documents:
                md5 = doc.metadata['md5']
                self._documents[md5] = doc

            # 重建 BM25Retriever
            self._retriever = self._build_retriever()

            # 持久化保存
            return self._save_documents()

        except Exception as e:
            print(f"错误[KeywordDB.add_documents] 批量添加文档失败: {str(e)}")
            return False

    def delete_document(self, md5: str) -> bool:
        """
        删除关键词数据库中的文档
        Args:
            md5: 文档的md5值
        Returns:
            bool: 是否删除成功
        """
        try:
            # 从内存字典中删除
            if md5 in self._documents:
                del self._documents[md5]
            else:
                print(f"警告[KeywordDB.delete_document]：文档 md5={md5} 不存在")

            # 重建 BM25Retriever
            self._retriever = self._build_retriever()

            # 持久化保存
            return self._save_documents()

        except Exception as e:
            print(f"错误[KeywordDB.delete_document] 删除文档失败 (md5={md5}): {str(e)}")
            return False

    def delete_documents(self, md5_list: List[str]) -> bool:
        """
        批量删除关键词数据库中的文档
        Args:
            md5_list: 文档的md5值列表
        Returns:
            bool: 是否删除成功
        """
        try:
            if not md5_list:
                print("警告[KeywordDB.delete_documents]：md5列表为空")
                return True

            # 批量删除
            for md5 in md5_list:
                if md5 in self._documents:
                    del self._documents[md5]

            # 重建 BM25Retriever
            self._retriever = self._build_retriever()

            # 持久化保存
            return self._save_documents()

        except Exception as e:
            print(f"错误[KeywordDB.delete_documents] 批量删除文档失败: {str(e)}")
            return False

    def search(self, query: str, k: int = config.KEYWORD_SEARCH_DEFAULT_K) -> List[Document]:
        """
        进行关键词检索
        Args:
            query: 检索关键词
            k: （可选）返回的文档数量，默认值为 config.KEYWORD_SEARCH_DEFAULT_K
        Returns:
            list[Document]: 检索到的文档列表，失败返回空列表
        """
        try:
            if not self._retriever:
                print("警告[KeywordDB.search]：BM25Retriever 未初始化，数据库为空")
                return []

            # 使用 BM25Retriever 进行检索
            # 设置返回的文档数量
            self._retriever.k = k

            # 尝试不同的调用方式（兼容不同版本的LangChain）
            try:
                # 方法1：invoke (新版本)
                results = self._retriever.invoke(query)
            except AttributeError:
                try:
                    # 方法2：get_relevant_documents (旧版本)
                    results = self._retriever.get_relevant_documents(query)
                except AttributeError:
                    # 方法3：直接调用 (最基础的方式)
                    results = self._retriever(query)

            return results

        except Exception as e:
            print(f"错误[KeywordDB.search] 关键词检索失败: {str(e)}")
            return []

    def delete_me(self):
        """
        删除关键词数据库，包括所有持久化存储
        """
        try:
            import shutil

            # 删除持久化存储目录
            if self.keyword_db_store_path.exists():
                shutil.rmtree(self.keyword_db_store_path)
                print(f"成功[KeywordDB.delete_me] 成功删除关键词数据库: {self.keyword_db_store_path}")
            else:
                print(f"警告[KeywordDB.delete_me]：关键词数据库目录不存在: {self.keyword_db_store_path}")

        except Exception as e:
            print(f"错误[KeywordDB.delete_me] 删除关键词数据库失败: {str(e)}")
            raise
