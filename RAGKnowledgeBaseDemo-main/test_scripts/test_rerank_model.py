import os
import dashscope
from http import HTTPStatus

# 设置 API Key
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

# 设置业务空间 ID（请替换为真实值）
WORKSPACE_ID = "llm-fq43z9u2tnoy3m7o"
dashscope.base_http_api_url = f'https://{WORKSPACE_ID}.cn-beijing.maas.aliyuncs.com/api/v1'

documents = [
    "重排序模型广泛应用于搜索引擎和推荐系统，按相关性对候选文本进行排序",
    "量子计算是计算科学的前沿领域",
    "预训练语言模型的发展为重排序模型带来了新的进展"
]

# 正确调用：直接传入 query 和 documents，不包裹 input
resp = dashscope.TextReRank.call(
    model="qwen3-rerank",
    query="什么是重排序模型",
    documents=documents,
    top_n=2
)

if resp.status_code == HTTPStatus.OK:
    print("✅ 调用成功！")
    for result in resp.output.results:
        # 通过 index 从原始列表中获取文档内容
        doc_text = documents[result.index] if result.index < len(documents) else "未知文档"
        print(f"得分: {result.relevance_score:.4f} - {doc_text[:50]}...")
else:
    print(f"❌ 调用失败: {resp.code} - {resp.message}")

# WORKSPACE_ID ="llm-fq43z9u2tnoy3m7o"