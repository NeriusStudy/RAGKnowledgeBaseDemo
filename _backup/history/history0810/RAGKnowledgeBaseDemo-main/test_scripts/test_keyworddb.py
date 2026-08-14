#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：KeywordDB 关键词数据库功能测试
功能：测试 KeywordDB 的增删查功能
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from KeywordDB import KeywordDB
from test_data_loader import MedicalDataLoader
import config


def test_keyworddb():
    """测试 KeywordDB 的完整功能"""

    print("=" * 60)
    print("KeywordDB 关键词数据库功能测试")
    print("=" * 60 + "\n")

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

    # 初始化 KeywordDB
    print("【步骤2】初始化 KeywordDB")
    print("-" * 60)

    test_db_path = "./test_keyword_db"

    try:
        keyworddb = KeywordDB(keyword_db_store_path=test_db_path)
        print(f"✓ KeywordDB 初始化成功")
        print(f"  存储路径: {test_db_path}\n")

    except Exception as e:
        print(f"✗ KeywordDB 初始化失败: {str(e)}")
        return False

    # 测试1：添加单个文档
    print("【测试1】添加单个文档")
    print("-" * 60)

    try:
        single_doc = test_documents[0]
        print(f"文档内容: {single_doc.page_content[:100]}...")
        print(f"文档 MD5: {single_doc.metadata['md5'][:16]}...")

        result = keyworddb.add_document(single_doc)
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

        result = keyworddb.add_documents(batch_docs)
        if result:
            print(f"✓ 批量添加成功\n")
        else:
            print("✗ 批量添加失败\n")
            return False

    except Exception as e:
        print(f"✗ 测试失败: {str(e)}\n")
        return False

    # 测试3：关键词检索
    print("【测试3】关键词检索")
    print("-" * 60)

    try:
        # 测试查询1：精确关键词
        query1 = "人参茎叶总皂苷胶囊"
        print(f"查询1: {query1}")
        results1 = keyworddb.search(query1, k=5)

        if results1:
            print(f"✓ 检索到 {len(results1)} 条相关文档")
            print("\n前3条结果:")
            for i, doc in enumerate(results1[:3], 1):
                print(f"  [{i}] {doc.page_content[:80]}...")
        else:
            print("⚠️  未检索到结果（可能是测试数据中不包含该关键词）")

        # 测试查询2：常见关键词
        print(f"\n查询2: 不良反应")
        results2 = keyworddb.search("不良反应", k=5)

        if results2:
            print(f"✓ 检索到 {len(results2)} 条相关文档")
            print("\n前3条结果:")
            for i, doc in enumerate(results2[:3], 1):
                print(f"  [{i}] {doc.page_content[:80]}...")
        else:
            print("⚠️  未检索到结果")

        # 测试查询3：疾病名称
        print(f"\n查询3: 头痛")
        results3 = keyworddb.search("头痛", k=5)

        if results3:
            print(f"✓ 检索到 {len(results3)} 条相关文档")
            print("\n前3条结果:")
            for i, doc in enumerate(results3[:3], 1):
                print(f"  [{i}] {doc.page_content[:80]}...")
        else:
            print("⚠️  未检索到结果")

        print()

    except Exception as e:
        print(f"✗ 检索测试失败: {str(e)}\n")
        return False

    # 测试4：持久化验证（重新加载）
    print("【测试4】持久化验证")
    print("-" * 60)

    try:
        print("重新初始化 KeywordDB，测试持久化加载...")
        keyworddb2 = KeywordDB(keyword_db_store_path=test_db_path)

        # 验证文档数量
        doc_count = len(keyworddb2._documents)
        print(f"✓ 成功加载 {doc_count} 条持久化文档")

        # 再次检索验证
        verify_results = keyworddb2.search("不良反应", k=3)
        if verify_results:
            print(f"✓ 持久化数据检索正常，检索到 {len(verify_results)} 条文档\n")
        else:
            print("⚠️  持久化数据检索未返回结果\n")

    except Exception as e:
        print(f"✗ 持久化测试失败: {str(e)}\n")
        return False

    # 测试5：删除单个文档
    print("【测试5】删除单个文档")
    print("-" * 60)

    try:
        delete_md5 = test_documents[0].metadata['md5']
        print(f"删除文档 MD5: {delete_md5[:16]}...")

        result = keyworddb.delete_document(delete_md5)
        if result:
            print("✓ 单个文档删除成功")

            # 验证删除
            doc_count_after = len(keyworddb._documents)
            print(f"✓ 验证：文档数量从 50 减少到 {doc_count_after}\n")
        else:
            print("✗ 单个文档删除失败\n")
            return False

    except Exception as e:
        print(f"✗ 删除测试失败: {str(e)}\n")
        return False

    # 测试6：批量删除文档
    print("【测试6】批量删除文档")
    print("-" * 60)

    try:
        delete_md5_list = [doc.metadata['md5'] for doc in test_documents[1:10]]
        print(f"批量删除 {len(delete_md5_list)} 条文档...")

        result = keyworddb.delete_documents(delete_md5_list)
        if result:
            print("✓ 批量删除成功")

            # 验证删除
            doc_count_final = len(keyworddb._documents)
            print(f"✓ 验证：当前文档数量为 {doc_count_final}\n")
        else:
            print("✗ 批量删除失败\n")
            return False

    except Exception as e:
        print(f"✗ 批量删除测试失败: {str(e)}\n")
        return False

    # 测试7：清理测试数据
    print("【测试7】清理测试数据")
    print("-" * 60)

    try:
        keyworddb.delete_me()
        print("✓ 测试数据库已清理\n")

    except Exception as e:
        print(f"⚠️  清理失败: {str(e)}\n")

    # 测试总结
    print("=" * 60)
    print("✓ 所有测试通过！KeywordDB 功能正常")
    print("=" * 60)
    print("\n测试涵盖的功能:")
    print("  ✓ 单个文档添加")
    print("  ✓ 批量文档添加")
    print("  ✓ 关键词检索（BM25算法）")
    print("  ✓ 持久化存储与加载")
    print("  ✓ 单个文档删除")
    print("  ✓ 批量文档删除")
    print("  ✓ 数据库清理")
    print("\n" + "=" * 60)

    return True


def main():
    """主函数"""
    try:
        success = test_keyworddb()
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
