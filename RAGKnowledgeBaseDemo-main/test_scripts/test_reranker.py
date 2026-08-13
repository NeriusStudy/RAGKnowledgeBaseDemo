#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：Reranker 重排序器功能测试
功能：测试 RRF 融合和 DashScope Rerank 重排序功能
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from Reranker import Reranker
from VectorDB import VectorDB
from KeywordDB import KeywordDB
from test_data_loader import MedicalDataLoader
import config


def test_reranker():
    """测试 Reranker 的完整功能"""

    print("=" * 60)
    print("Reranker 重排序器功能测试")
    print("=" * 60 + "\n")

    # 测试数据准备
    print("【步骤1】加载测试数据")
    print("-" * 60)

    try:
        data_loader = MedicalDataLoader("../MedicalDataset/triples.json")
        data_loader.load_data()

        # 使用三元组模式，取前200条数据进行测试
        all_documents = data_loader.convert_to_documents(format_type='triple')
        test_documents = all_documents[:200]
        print(f"✓ 准备测试数据: {len(test_documents)} 条\n")

    except Exception as e:
        print(f"✗ 加载测试数据失败: {str(e)}")
        return False

    # 初始化 VectorDB 和 KeywordDB
    print("【步骤2】初始化 VectorDB 和 KeywordDB")
    print("-" * 60)

    test_vector_db_path = "./test_reranker_vector_db"
    test_keyword_db_path = "./test_reranker_keyword_db"

    try:
        # 初始化向量数据库
        vectordb = VectorDB(vector_db_store_path=test_vector_db_path)
        print(f"✓ VectorDB 初始化成功")

        # 初始化关键词数据库
        keyworddb = KeywordDB(keyword_db_store_path=test_keyword_db_path)
        print(f"✓ KeywordDB 初始化成功\n")

    except Exception as e:
        print(f"✗ 数据库初始化失败: {str(e)}")
        return False

    # 添加测试数据到两个数据库
    print("【步骤3】添加测试数据到数据库")
    print("-" * 60)

    try:
        print("正在添加文档到 VectorDB...")
        vectordb.add_documents(test_documents)
        print("✓ VectorDB 数据添加完成")

        print("正在添加文档到 KeywordDB...")
        keyworddb.add_documents(test_documents)
        print("✓ KeywordDB 数据添加完成\n")

    except Exception as e:
        print(f"✗ 数据添加失败: {str(e)}")
        return False

    # 初始化 Reranker
    print("【步骤4】初始化 Reranker")
    print("-" * 60)

    try:
        reranker = Reranker()
        print(f"✓ Reranker 初始化成功")
        print(f"  使用模型: {reranker.get_rerank_model_name()}\n")

    except Exception as e:
        print(f"✗ Reranker 初始化失败: {str(e)}")
        return False

    # 测试1：RRF 融合
    print("【测试1】RRF 融合测试")
    print("-" * 60)

    try:
        query1 = "人参茎叶总皂苷胶囊的不良反应"

        # 分别进行向量检索和关键词检索
        print(f"查询: {query1}")
        vector_results = vectordb.search(query1, k=10)
        keyword_results = keyworddb.search(query1, k=10)

        print(f"✓ 向量检索结果: {len(vector_results)} 条")
        print(f"✓ 关键词检索结果: {len(keyword_results)} 条")

        # 使用 RRF 融合
        fused_results = reranker._rrf_fusion(
            vector_documents=vector_results,
            keyword_documents=keyword_results,
            vector_weight=0.5,
            keyword_weight=0.5,
            k=10
        )

        print(f"✓ RRF 融合结果: {len(fused_results)} 条")

        if fused_results:
            print("\n前3条融合结果:")
            for i, doc in enumerate(fused_results[:3], 1):
                print(f"  [{i}] {doc.page_content[:80]}...")
        print()

    except Exception as e:
        print(f"✗ RRF融合测试失败: {str(e)}\n")
        return False

    # 测试2：完整重排序流程
    print("【测试2】完整重排序测试（RRF + DashScope Rerank）")
    print("-" * 60)

    try:
        query2 = "糖尿病的治疗药物"

        print(f"查询: {query2}")

        # 分别进行向量检索和关键词检索
        vector_results2 = vectordb.search(query2, k=15)
        keyword_results2 = keyworddb.search(query2, k=15)

        print(f"✓ 向量检索结果: {len(vector_results2)} 条")
        print(f"✓ 关键词检索结果: {len(keyword_results2)} 条")

        # 使用完整重排序流程
        reranked_results = reranker.rerank(
            query=query2,
            vector_documents=vector_results2,
            keyword_documents=keyword_results2,
            vector_weight=0.6,
            keyword_weight=0.4,
            k=5
        )

        print(f"✓ 重排序后结果: {len(reranked_results)} 条")

        if reranked_results:
            print("\n重排序后的前5条结果:")
            for i, doc in enumerate(reranked_results, 1):
                print(f"  [{i}] {doc.page_content[:80]}...")
        print()

    except Exception as e:
        print(f"✗ 重排序测试失败: {str(e)}")
        print(f"  注意：如果是 API 调用失败，请检查 DASHSCOPE_API_KEY 环境变量\n")
        return False

    # 测试3：不同权重配置
    print("【测试3】不同权重配置测试")
    print("-" * 60)

    try:
        query3 = "头痛的症状"

        vector_results3 = vectordb.search(query3, k=10)
        keyword_results3 = keyworddb.search(query3, k=10)

        # 配置1：向量权重高
        print("配置1：向量权重 0.7，关键词权重 0.3")
        results_config1 = reranker.rerank(
            query=query3,
            vector_documents=vector_results3,
            keyword_documents=keyword_results3,
            vector_weight=0.7,
            keyword_weight=0.3,
            k=3
        )
        print(f"✓ 返回 {len(results_config1)} 条结果")

        # 配置2：关键词权重高
        print("\n配置2：向量权重 0.3，关键词权重 0.7")
        results_config2 = reranker.rerank(
            query=query3,
            vector_documents=vector_results3,
            keyword_documents=keyword_results3,
            vector_weight=0.3,
            keyword_weight=0.7,
            k=3
        )
        print(f"✓ 返回 {len(results_config2)} 条结果")

        # 配置3：平衡权重
        print("\n配置3：向量权重 0.5，关键词权重 0.5（平衡）")
        results_config3 = reranker.rerank(
            query=query3,
            vector_documents=vector_results3,
            keyword_documents=keyword_results3,
            vector_weight=0.5,
            keyword_weight=0.5,
            k=3
        )
        print(f"✓ 返回 {len(results_config3)} 条结果\n")

    except Exception as e:
        print(f"✗ 权重配置测试失败: {str(e)}\n")
        return False

    # 测试4：边界情况
    print("【测试4】边界情况测试")
    print("-" * 60)

    try:
        # 场景1：空结果
        print("场景1：空检索结果")
        empty_results = reranker.rerank(
            query="这是一个不存在的查询abcdefghijk123456",
            vector_documents=[],
            keyword_documents=[],
            k=5
        )
        print(f"✓ 空结果处理正常，返回 {len(empty_results)} 条")

        # 场景2：只有向量结果
        print("\n场景2：只有向量检索结果")
        vector_only_results = reranker.rerank(
            query="人参",
            vector_documents=vectordb.search("人参", k=5),
            keyword_documents=[],
            k=3
        )
        print(f"✓ 只有向量结果，返回 {len(vector_only_results)} 条")

        # 场景3：只有关键词结果
        print("\n场景3：只有关键词检索结果")
        keyword_only_results = reranker.rerank(
            query="人参",
            vector_documents=[],
            keyword_documents=keyworddb.search("人参", k=5),
            k=3
        )
        print(f"✓ 只有关键词结果，返回 {len(keyword_only_results)} 条\n")

    except Exception as e:
        print(f"✗ 边界情况测试失败: {str(e)}\n")
        return False

    # 清理测试数据
    print("【步骤5】清理测试数据")
    print("-" * 60)

    try:
        # 先删除对象引用，释放资源
        vectordb.delete_me()
        keyworddb.delete_me()

        # 删除对象引用
        del vectordb
        del keyworddb
        del reranker

        # 强制垃圾回收
        import gc
        gc.collect()

        print("✓ 测试数据库已清理\n")

    except Exception as e:
        print(f"⚠️  清理失败: {str(e)}")
        print(f"  提示：如果是 Windows 文件占用错误，可以手动删除测试目录\n")

    # 测试总结
    print("=" * 60)
    print("✓ 所有测试通过！Reranker 功能正常")
    print("=" * 60)
    print("\n测试涵盖的功能:")
    print("  ✓ RRF 融合算法")
    print("  ✓ DashScope Rerank 模型重排序")
    print("  ✓ 不同权重配置")
    print("  ✓ 边界情况处理")
    print("\n" + "=" * 60)

    return True


def main():
    """主函数"""
    try:
        success = test_reranker()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        return 1
    except Exception as e:
        print(f"\n\n测试过程中出现未预期的错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
