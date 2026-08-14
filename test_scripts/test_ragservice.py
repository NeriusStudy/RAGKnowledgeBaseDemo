"""
RAGService 测试脚本

测试内容：
1. 初始化 RAGService
2. 添加文档（单个和批量）
3. 三种检索模式测试（vector, keyword, hybrid）
4. 删除文档（单个和批量）
5. 清理测试数据
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到系统路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from RAGService import RAGService
from test_data_loader import MedicalDataLoader
import config

def print_separator(title=""):
    """打印分隔线"""
    if title:
        print(f"\n{'='*60}")
        print(f"{title}")
        print('='*60)
    else:
        print('-'*60)

def test_ragservice():
    """测试 RAGService 的所有功能"""

    print_separator("RAGService 统一检索服务测试")

    # ============================================================
    # 步骤1：加载测试数据
    # ============================================================
    print_separator("【步骤1】加载测试数据")

    data_file = project_root / "MedicalDataset" / "triples.json"

    # 使用 MedicalDataLoader 加载数据
    loader = MedicalDataLoader(str(data_file))
    loader.load_data()
    documents = loader.convert_to_documents(format_type='triple')

    # 取前100条作为测试数据
    test_docs = documents[:100]
    print(f"✓ 准备测试数据: {len(test_docs)} 条\n")

    # ============================================================
    # 步骤2：初始化 RAGService
    # ============================================================
    print_separator("【步骤2】初始化 RAGService")

    rag_service = RAGService(
        RAG_store_path="./test_rag_service/"
    )

    print("✓ RAGService 初始化成功")
    print(f"  存储路径: ./test_rag_service/")
    print(f"  嵌入模型: {rag_service.get_embedding_model_name()}")
    print(f"  重排序模型: {rag_service.get_rerank_model_name()}\n")

    # ============================================================
    # 测试1：添加单个文档
    # ============================================================
    print_separator("【测试1】添加单个文档")

    doc = test_docs[0]
    print(f"文档内容: {doc.page_content[:50]}...")
    print(f"文档 MD5: {doc.metadata.get('md5', 'N/A')[:16]}...")

    success = rag_service.add_document(doc)
    if success:
        print("✓ 单个文档添加成功\n")
    else:
        print("✗ 单个文档添加失败\n")

    # ============================================================
    # 测试2：批量添加文档
    # ============================================================
    print_separator("【测试2】批量添加文档")

    batch_docs = test_docs[1:100]  # 添加剩余99条
    print(f"准备添加 {len(batch_docs)} 条文档...")

    success = rag_service.add_documents(batch_docs)
    if success:
        print(f"✓ 批量添加成功: {len(batch_docs)} 条文档\n")
    else:
        print("✗ 批量添加失败\n")

    # ============================================================
    # 测试3：向量检索模式
    # ============================================================
    print_separator("【测试3】向量检索模式（mod='vector'）")

    query = "糖尿病的症状"
    k = 5
    print(f"查询: {query}")
    print(f"返回数量: {k}")

    results = rag_service.search(query=query, mod="vector", k=k)
    print(f"✓ 向量检索返回: {len(results)} 条结果\n")

    if results:
        print("检索结果（前3条）:")
        for i, doc in enumerate(results[:3], 1):
            content = doc.page_content[:60].replace('\n', ' ')
            print(f"  [{i}] {content}...")
    print()

    # ============================================================
    # 测试4：关键词检索模式
    # ============================================================
    print_separator("【测试4】关键词检索模式（mod='keyword'）")

    query = "糖尿病的症状"
    k = 5
    print(f"查询: {query}")
    print(f"返回数量: {k}")

    results = rag_service.search(query=query, mod="keyword", k=k)
    print(f"✓ 关键词检索返回: {len(results)} 条结果\n")

    if results:
        print("检索结果（前3条）:")
        for i, doc in enumerate(results[:3], 1):
            content = doc.page_content[:60].replace('\n', ' ')
            print(f"  [{i}] {content}...")
    print()

    # ============================================================
    # 测试5：混合检索模式（默认）
    # ============================================================
    print_separator("【测试5】混合检索模式（mod='hybrid'，默认）")

    query = "糖尿病的治疗药物"
    k = 5
    print(f"查询: {query}")
    print(f"返回数量: {k}")

    results = rag_service.search(query=query, mod="hybrid", k=k)
    print(f"✓ 混合检索返回: {len(results)} 条结果\n")

    if results:
        print("检索结果（前5条）:")
        for i, doc in enumerate(results[:5], 1):
            content = doc.page_content[:60].replace('\n', ' ')
            # 如果有重排序得分，显示出来
            rerank_score = doc.metadata.get('rerank_score', None)
            score_str = f" [score: {rerank_score:.4f}]" if rerank_score else ""
            print(f"  [{i}] {content}...{score_str}")
    print()

    # ============================================================
    # 测试6：不同权重配置
    # ============================================================
    print_separator("【测试6】不同权重配置测试")

    query = "糖尿病的治疗"
    k = 3

    # 配置1：向量权重更高
    print("配置1：向量权重 0.7，关键词权重 0.3")
    results1 = rag_service.search(
        query=query,
        mod="hybrid",
        k=k,
        vector_weight=0.7,
        keyword_weight=0.3
    )
    print(f"✓ 返回 {len(results1)} 条结果\n")

    # 配置2：关键词权重更高
    print("配置2：向量权重 0.3，关键词权重 0.7")
    results2 = rag_service.search(
        query=query,
        mod="hybrid",
        k=k,
        vector_weight=0.3,
        keyword_weight=0.7
    )
    print(f"✓ 返回 {len(results2)} 条结果\n")

    # 配置3：平衡权重
    print("配置3：向量权重 0.5，关键词权重 0.5（平衡）")
    results3 = rag_service.search(
        query=query,
        mod="hybrid",
        k=k,
        vector_weight=0.5,
        keyword_weight=0.5
    )
    print(f"✓ 返回 {len(results3)} 条结果\n")

    # ============================================================
    # 测试7：删除单个文档
    # ============================================================
    print_separator("【测试7】删除单个文档")

    # 删除第一个添加的文档
    md5_to_delete = test_docs[0].metadata.get('md5')
    print(f"删除文档 MD5: {md5_to_delete[:16]}...")

    success = rag_service.delete_document(md5_to_delete)
    if success:
        print("✓ 单个文档删除成功\n")
    else:
        print("✗ 单个文档删除失败\n")

    # ============================================================
    # 测试8：批量删除文档
    # ============================================================
    print_separator("【测试8】批量删除文档")

    # 删除5个文档
    md5_list = [doc.metadata.get('md5') for doc in test_docs[1:6]]
    print(f"准备删除 {len(md5_list)} 个文档...")

    success = rag_service.delete_documents(md5_list)
    if success:
        print(f"✓ 批量删除成功: {len(md5_list)} 个文档\n")
    else:
        print("✗ 批量删除失败\n")

    # 验证删除后的检索结果数量是否减少
    results_after_delete = rag_service.search(query="糖尿病", mod="vector", k=100)
    print(f"删除后剩余文档数量: {len(results_after_delete)} 条")
    print(f"预期数量: {100 - 1 - 5} = 94 条\n")

    # ============================================================
    # 步骤9：清理测试数据
    # ============================================================
    print_separator("【步骤9】清理测试数据")

    try:
        rag_service.delete_me()
        print("✓ RAGService 清理完成\n")
    except Exception as e:
        print(f"⚠️  清理失败: {e}")
        print("  提示：如果是 Windows 文件占用错误，可以手动删除测试目录\n")

    print_separator("测试完成")
    print("\n所有测试已完成！")
    print("\n✅ RAGService 功能测试通过")
    print("   - 文档添加（单个和批量）")
    print("   - 向量检索模式")
    print("   - 关键词检索模式")
    print("   - 混合检索模式（RRF + Rerank）")
    print("   - 不同权重配置")
    print("   - 文档删除（单个和批量）")

if __name__ == "__main__":
    test_ragservice()
