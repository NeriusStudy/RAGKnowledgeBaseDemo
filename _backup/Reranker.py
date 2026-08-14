"""
实现人：

重排序器（Reranker）
基于 LangChain 的 DashScopeRerank 实现，
用于在混合检索（Hybrid Search）场景中对召回的文档进行重排序，
提升最终结果的相关性。
"""
import config
from langchain_community.document_compressors import DashScopeRerank
from langchain_core.documents import Document

class Reranker:
    def __init__(self, rerank_model_name: str = config.RERANK_MODEL_NAME):
        """
        初始化重排序器
        Args:
            rerank_model_name: 重排序模型名称，默认使用config.RERANK_MODEL_NAME
        """
        self.rerank_model_name = rerank_model_name
        # 初始化重排序模型
        self.rerank_model = DashScopeRerank(
            model=self.rerank_model_name
        )

    def get_rerank_model_name(self) -> str:
        """
        获取当前使用的重排序模型名称
        Returns:
            str: 当前使用的重排序模型名称
        """
        return self.rerank_model_name

    def _rrf_fusion(self, vector_documents: list[Document],
                keyword_documents: list[Document],
                vector_weight: float = 0.5,
                keyword_weight: float = 0.5,
                k: int = config.RRF_REFUSION_K) -> list[Document]:
        """
        对向量召回和关键词召回进行融合重排序, 使用RRF融合策略
        Args:
            vector_documents: 基于向量的召回文档
            keyword_documents: 基于关键词的召回文档
            vector_weight: 向量权重，默认0.5
            keyword_weight: 关键词权重，默认0.5
            k: 返回的文档数量，默认 config.RRF_REFUSION_K
        Returns:
            list[Document]: 融合重排序后的文档列表
        """
        pass

    def rerank(self, query:str,
               vector_documents: list[Document],
               keyword_documents: list[Document],
               vector_weight: float = 0.5,
               keyword_weight: float = 0.5,
               k: int = config.RERANK_K):
        """
        对召回的文档进行重排序
        Args:
            query: 查询字符串
            vector_documents: 基于向量的召回文档
            keyword_documents: 基于关键词的召回文档
            vector_weight: 向量权重，默认0.5
            keyword_weight: 关键词权重，默认0.5
            k: 返回的文档数量，默认 config.RERANK_K
        Returns:
            list[Document]: 重排序后的文档列表
        """
        pass