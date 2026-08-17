"""
文档切分器（Splitter）
基于 LangChain 的 RecursiveCharacterTextSplitter 封装，
提供对文本或 Document 对象的切分能力，支持自定义分块大小、
重叠大小、分隔符等参数，适配中文场景优化。
"""
import config
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import Optional, List
from Deduplicator import Deduplicator

class Splitter:
    def __init__(
        self,
        chunk_size: int = config.SPLITTER_CHUNK_SIZE,
        chunk_overlap: int = config.SPLITTER_CHUNK_OVERLAP,
        separators: Optional[List[str]] = config.SPLITTER_SEPARATERS,
        length_function = config.SPLITTER_LENGTH_FUNCTION,
    ):
        """
        初始化文档切分器
        Args:
            chunk_size: 每个文本块的最大字符数，默认 config.SPLITTER_CHUNK_SIZE = 500
            chunk_overlap: 相邻文本块重叠的字符数，默认 config.SPLITTER_CHUNK_OVERLAP = 50
            separators: 切分分隔符列表，按优先级从高到低排列；
                        默认针对中文优化，优先在段落、换行、句号、感叹号等处切分
            length_function: 计算文本长度的函数，默认为 config.SPLITTER_LENGTH_FUNCTION = len()
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators
        self.length_function = length_function
        # 配置langchain的文本分割器
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
            length_function=length_function,
        )

    def get_chunk_size(self) -> int:
        """
        获取当前使用的文本块最大字符数
        Returns:
            int: 当前使用的文本块最大字符数
        """
        return self.chunk_size

    def get_chunk_overlap(self) -> int:
        """
        获取当前使用的文本块重叠字符数
        Returns:
            int: 当前使用的文本块重叠字符数
        """
        return self.chunk_overlap

    def get_separators(self) -> List[str]:
        """
        获取当前使用的切分分隔符列表
        Returns:
            List[str]: 当前使用的切分分隔符列表
        """
        return self.separators

    def get_length_function(self):
        """
        获取当前使用的计算文本长度的函数
        Returns:
            计算文本长度的函数
        """
        return self.length_function

    def split_text(self, text: str) -> List[str]:
        """
        将原始文本字符串切分为文本块列表
        Args:
            text: 待切分的原始文本字符串
        Returns:
            切分后的文本块列表（List[str]）
        """
        if not text:
            print("警告[Splitter.split_text]：文本为空")
            return []

        try:
            split_text = self._splitter.split_text(text)
        except Exception as e:
            print(f"错误[Splitter.split_text]：切分文本失败: {str(e)}")
            return []
        return split_text

    def split_document(self, document: Document) -> List[Document]:
        """
        将单个 LangChain Document 对象切分为多个 Document 块，切分后需要调用Deduplicator
        将每个块的内容计算成md5作为Document的索引保存在Document的metadata的md5中
        Args:
            document: 待切分的 LangChain Document 对象
        Returns:
            切分后的 Document 块列表，每个块保留原始 Document 的 metadata，并添加md5
        """
        if not document.page_content:
            print("警告[Splitter.split_document]：文档内容为空")
            return []

        # 使用 LangChain 的切分器切分文档
        try:
            split_docs = self._splitter.split_documents([document])
        except Exception as e:
            print(f"错误[Splitter.split_document]：切分文档失败: {str(e)}")
            return []

        # 为每个切分后的文档添加 MD5
        try:
            for doc in split_docs:
                md5 = Deduplicator.str_to_md5(doc.page_content)
                if md5:
                    doc.metadata['md5'] = md5
        except Exception as e:
            print(f"错误[Splitter.split_document]：计算文档 md5 失败: {str(e)}")
            return []

        return split_docs

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        将多个 LangChain Document 对象切分为多个 Document 块
        Args:
            documents: 待切分的 LangChain Document 对象列表
        Returns:
            切分后的 Document 块列表，每个块保留对应原始 Document 的 metadata
        """
        if not documents:
            print("警告[Splitter.split_documents]：文档列表为空")
            return []

        try:
            all_split_docs = []
            for document in documents:
                split_docs = self.split_document(document)
                all_split_docs.extend(split_docs)
        except Exception as e:
            print(f"错误[Splitter.split_documents]：切分文档失败: {str(e)}")
            return []
        return all_split_docs
