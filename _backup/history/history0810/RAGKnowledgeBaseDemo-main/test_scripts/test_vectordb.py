#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：VectorDB 向量数据库功能测试
功能：测试 VectorDB 的增删查功能
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from VectorDB import VectorDB
from test_data_loader import MedicalDataLoader
import config


def test_vectordb():
    """测试 VectorDB 的完整功能"""

    print("=" * 60)
    print("VectorDB 向量数据库功能测试")
    print("=" * 60 + "\n")

    # 检查环境变量
    if 'DASHSCOPE_API_KEY' not in os.environ:
        print("⚠️  警告：未设置 DASHSCOPE_API_KEY 环境变量")
        print("请先设置环境变量：")
        print("  Windows: set DASHSCOPE_API_KEY=your_api_key")
        print("  Linux/Mac: export DASHSCOPE_API_KEY=your_api_key")
        print("\n或在代码中设置：")
        print("  import os")
        print("  os.environ['DASHSCOPE_API_KEY'] = 'your_api_key'")
        return False

    # 测试数据准备
    print("【步骤1】加载测试数据")
    print("-" * 60)

    try:
        data_loader = MedicalDataLoader("../MedicalDataset/triples.json")
        data_loader.load_data()

        # 使用三元组模式，取前100条数据进行测试
        all_documents = data_loader.convert_to_documents(format_type='triple')
        test_documents = all_documents[:100]  # 取前100条用于测试
        print(f"✓ 准备测试数据: {len(test_documents)} 条\n")

    except Exception as e:
        print(f"✗ 加载测试数据失败: {str(e)}")
        return False

    # 初始化 VectorDB
    print("【步骤2】初始化 VectorDB")
    print("-" * 60)

    test_db_path = "./test_vector_db"

    try:
        vectordb = VectorDB(
            vector_db_store_path=test_db_path,
            embedding_model_name=config.EMBEDDING_MODEL_NAME
        )
        print(f"✓ VectorDB 初始化成功")
        print(f"  存储路径: {test_db_path}")
        print(f"  嵌入模型: {vectordb.get_embedding_model_name()}\n")

    except Exception as e:
        print(f"✗ VectorDB 初始化失败: {str(e)}")
        return False

    # 测试1：添加单个文档
    print("【测试1】添加单个文档")
    print("-" * 60)

    try:
        single_doc = test_documents[0]
        print(f"文档内容: {single_doc.page_content[:100]}...")
        print(f"文档 MD5: {single_doc.metadata['md5'][:16]}...")

        result = vectordb.add_document(single_doc)
        if result:
            print("✓ 单个文档添加成功\n")
        else:
            print("✗ 单个文档添加失败\n")
            return False

    except Exception as e:
        print(f"✗ 测试失败: {str(e)}\n")
        return False

    # 测试2：批量添加文档
    print("【测试2】批量添加文档")
    print("-" * 60)

    try:
        batch_docs = test_documents[1:50]  # 添加第2-50条
        print(f"批量添加 {len(batch_docs)} 条文档...")

        result = vectordb.add_documents(batch_docs)
        if result:
            print(f"✓ 批量添加成功\n")
        else:
            print("✗ 批量添加失败\n")
            return False

    except Exception as e:
        print(f"✗ 测试失败: {str(e)}\n")
        return False

    # 测试3：向量检索
    print("【测试3】向量检索")
    print("-" * 60)

    try:
        # 测试查询1：药品相关
        query1 = "人参有什么副作用？"
        print(f"查询1: {query1}")
        results1 = vectordb.search(query1, k=5)

        if results1:
            print(f"✓ 检索到 {len(results1)} 条相关文档")
            print("\n前3条结果:")
            for i, doc in enumerate(results1[:3], 1):
                print(f"  [{i}] {doc.page_content[:80]}...")
        else:
            print("✗ 检索失败或无结果")
            return False

        # 测试查询2：疾病相关
        print(f"\n查询2: 糖尿病的症状")
        results2 = vectordb.search("糖尿病的症状", k=5)

        if results2:
            print(f"✓ 检索到 {len(results2)} 条相关文档")
            print("\n前3条结果:")
            for i, doc in enumerate(results2[:3], 1):
                print(f"  [{i}] {doc.page_content[:80]}...")
        else:
            print("✗ 检索失败或无结果")

        print()

    except Exception as e:
        print(f"✗ 检索测试失败: {str(e)}\n")
        return False

    # 测试4：删除单个文档
    print("【测试4】删除单个文档")
    print("-" * 60)

    try:
        delete_md5 = test_documents[0].metadata['md5']
        print(f"删除文档 MD5: {delete_md5[:16]}...")

        result = vectordb.delete_document(delete_md5)
        if result:
            print("✓ 单个文档删除成功")

            # 验证删除
            verify_results = vectordb.search(test_documents[0].page_content, k=5)
            # 检查删除的文档是否还在结果中
            found = any(doc.metadata.get('md5') == delete_md5 for doc in verify_results)
            if not found:
                print("✓ 验证：文档已从数据库中删除\n")
            else:
                print("⚠️  警告：删除后仍能检索到该文档\n")
        else:
            print("✗ 单个文档删除失败\n")
            return False

    except Exception as e:
        print(f"✗ 删除测试失败: {str(e)}\n")
        return False

    # 测试5：批量删除文档
    print("【测试5】批量删除文档")
    print("-" * 60)

    try:
        delete_md5_list = [doc.metadata['md5'] for doc in test_documents[1:10]]
        print(f"批量删除 {len(delete_md5_list)} 条文档...")

        result = vectordb.delete_documents(delete_md5_list)
        if result:
            print("✓ 批量删除成功\n")
        else:
            print("✗ 批量删除失败\n")
            return False

    except Exception as e:
        print(f"✗ 批量删除测试失败: {str(e)}\n")
        return False

    # 测试6：删除数据库
    print("【测试6】清理测试数据")
    print("-" * 60)

    try:
        vectordb.delete_me()
        print("✓ 测试数据库已清理\n")

    except Exception as e:
        print(f"⚠️  清理失败: {str(e)}\n")

    # 测试总结
    print("=" * 60)
    print("✓ 所有测试通过！VectorDB 功能正常")
    print("=" * 60)
    print("\n测试涵盖的功能:")
    print("  ✓ 单个文档添加")
    print("  ✓ 批量文档添加")
    print("  ✓ 向量相似度检索")
    print("  ✓ 单个文档删除")
    print("  ✓ 批量文档删除")
    print("  ✓ 数据库清理")
    print("\n" + "=" * 60)

    return True


def main():
    """主函数"""
    try:
        success = test_vectordb()
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
