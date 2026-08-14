"""
实现人：

重排序器（Reranker）
直接使用 DashScope SDK 实现，
用于在混合检索（Hybrid Search）场景中对召回的文档进行重排序，
提升最终结果的相关性。
"""
import config
import os
import dashscope
from http import HTTPStatus
from langchain_core.documents import Document

class Reranker:
    def __init__(self, rerank_model_name: str = config.RERANK_MODEL_NAME):
        """
        初始化重排序器
        Args:
            rerank_model_name: 重排序模型名称，默认使用config.RERANK_MODEL_NAME
        """
        self.rerank_model_name = rerank_model_name

        # 从环境变量获取 API Key
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            print("警告：DASHSCOPE_API_KEY 环境变量未设置")

        dashscope.api_key = api_key

        # 如果有工作空间 ID，设置 base_url
        workspace_id = os.getenv("DASHSCOPE_WORKSPACE_ID")
        if workspace_id:
            dashscope.base_http_api_url = f'https://{workspace_id}.cn-beijing.maas.aliyuncs.com/api/v1'
            print(f"使用工作空间: {workspace_id}")

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
        try:
            # RRF (Reciprocal Rank Fusion) 常数，用于平滑排名
            RRF_K = 60

            # 存储每个文档的 RRF 分数
            # key: md5, value: (Document, rrf_score)
            doc_scores = {}

            # 处理向量检索结果
            for rank, doc in enumerate(vector_documents, start=1):
                md5 = doc.metadata.get('md5', '')
                if not md5:
                    continue

                # RRF 公式: score = weight / (K + rank)
                rrf_score = vector_weight / (RRF_K + rank)

                if md5 in doc_scores:
                    doc_scores[md5] = (doc, doc_scores[md5][1] + rrf_score)
                else:
                    doc_scores[md5] = (doc, rrf_score)

            # 处理关键词检索结果
            for rank, doc in enumerate(keyword_documents, start=1):
                md5 = doc.metadata.get('md5', '')
                if not md5:
                    continue

                rrf_score = keyword_weight / (RRF_K + rank)

                if md5 in doc_scores:
                    doc_scores[md5] = (doc_scores[md5][0], doc_scores[md5][1] + rrf_score)
                else:
                    doc_scores[md5] = (doc, rrf_score)

            # 按分数降序排序
            sorted_docs = sorted(doc_scores.values(), key=lambda x: x[1], reverse=True)

            # 返回前 k 个文档
            result = [doc for doc, score in sorted_docs[:k]]

            return result

        except Exception as e:
            print(f"RRF融合失败: {str(e)}")
            # 失败时返回向量检索结果（作为降级策略）
            return vector_documents[:k] if vector_documents else []

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
        try:
            # 步骤1：使用 RRF 算法进行初步融合
            # 融合时使用较大的 k 值，获取更多候选文档
            fusion_k = config.RRF_REFUSION_K
            fused_documents = self._rrf_fusion(
                vector_documents=vector_documents,
                keyword_documents=keyword_documents,
                vector_weight=vector_weight,
                keyword_weight=keyword_weight,
                k=fusion_k
            )

            # 如果融合后没有文档，直接返回空列表
            if not fused_documents:
                print("警告：RRF融合后没有文档")
                return []

            # 步骤2：使用 DashScope Rerank 模型进行精排
            try:
                # 准备文档列表
                documents_text = [doc.page_content for doc in fused_documents]

                # 调用 DashScope Rerank API
                response = dashscope.TextReRank.call(
                    model=self.rerank_model_name,
                    query=query,
                    documents=documents_text,
                    top_n=min(k, len(fused_documents))
                )

                # 检查返回结果
                if response.status_code == HTTPStatus.OK:
                    # 根据重排序结果重新组织文档
                    reranked_documents = []
                    for result in response.output.results:
                        if result.index < len(fused_documents):
                            doc = fused_documents[result.index]
                            # 将相关性得分添加到 metadata
                            doc.metadata['rerank_score'] = result.relevance_score
                            reranked_documents.append(doc)

                    return reranked_documents[:k]

                else:
                    print(f"Rerank API 调用失败: {response.code} - {response.message}")
                    print("降级到 RRF 融合结果")
                    return fused_documents[:k]

            except Exception as rerank_error:
                print(f"Rerank 模型调用失败: {str(rerank_error)}")
                print(f"错误类型: {type(rerank_error).__name__}")
                # 降级到 RRF 融合结果
                return fused_documents[:k]

        except Exception as e:
            print(f"重排序失败: {str(e)}")
            print(f"错误类型: {type(e).__name__}")
            # 失败时返回 RRF 融合结果作为降级策略
            try:
                fused_documents = self._rrf_fusion(
                    vector_documents=vector_documents,
                    keyword_documents=keyword_documents,
                    vector_weight=vector_weight,
                    keyword_weight=keyword_weight,
                    k=k
                )
                return fused_documents
            except Exception as e2:
                print(f"RRF融合降级也失败: {str(e2)}")
                # 最终降级：返回向量检索结果
                return vector_documents[:k] if vector_documents else []