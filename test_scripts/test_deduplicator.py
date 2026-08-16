"""
Deduplicator 去重器测试脚本

测试内容：
1. 字符串转 MD5
2. MD5 去重检查
3. 字符串去重检查
4. MD5 保存和删除
5. 字符串保存和删除
6. Document 对象的 MD5 转换
7. Document 去重检查
8. Document 保存和删除
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Deduplicator import Deduplicator
from langchain_core.documents import Document
import tempfile
import shutil

def test_str_to_md5():
    """测试字符串转 MD5"""
    print("=" * 70)
    print("测试 1: 字符串转 MD5")
    print("=" * 70)

    test_cases = [
        "Hello World",
        "这是一段中文测试文本",
        "123456",
        "",
    ]

    for text in test_cases:
        md5 = Deduplicator.str_to_md5(text)
        print(f"文本: '{text}' -> MD5: {md5}")

    print()

def test_md5_operations():
    """测试 MD5 的保存、检查和删除操作"""
    print("=" * 70)
    print("测试 2: MD5 保存、检查和删除")
    print("=" * 70)

    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    md5_file = os.path.join(temp_dir, "test_md5.txt")

    try:
        dedup = Deduplicator(md5_file)

        # 测试保存 MD5
        test_md5_1 = "abc123def456"
        test_md5_2 = "xyz789uvw012"

        print(f"\n1. 保存 MD5: {test_md5_1}")
        result = dedup.save_md5(test_md5_1)
        print(f"   结果: {'成功' if result else '失败'}")

        print(f"\n2. 检查 MD5 是否存在: {test_md5_1}")
        exists = dedup.check_if_deduplicate_md5(test_md5_1)
        print(f"   结果: {'存在' if exists else '不存在'}")

        print(f"\n3. 重复保存同一个 MD5: {test_md5_1}")
        result = dedup.save_md5(test_md5_1)
        print(f"   结果: {'成功（已存在）' if result else '失败'}")

        print(f"\n4. 保存第二个 MD5: {test_md5_2}")
        result = dedup.save_md5(test_md5_2)
        print(f"   结果: {'成功' if result else '失败'}")

        print(f"\n5. 删除 MD5: {test_md5_1}")
        result = dedup.delete_md5(test_md5_1)
        print(f"   结果: {'成功' if result else '失败'}")

        print(f"\n6. 检查已删除的 MD5: {test_md5_1}")
        exists = dedup.check_if_deduplicate_md5(test_md5_1)
        print(f"   结果: {'仍存在（错误）' if exists else '不存在（正确）'}")

        print(f"\n7. 检查未删除的 MD5: {test_md5_2}")
        exists = dedup.check_if_deduplicate_md5(test_md5_2)
        print(f"   结果: {'存在（正确）' if exists else '不存在（错误）'}")

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)

    print()

def test_str_operations():
    """测试字符串的保存、检查和删除操作"""
    print("=" * 70)
    print("测试 3: 字符串保存、检查和删除")
    print("=" * 70)

    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    md5_file = os.path.join(temp_dir, "test_md5.txt")

    try:
        dedup = Deduplicator(md5_file)

        test_str_1 = "这是第一段测试文本"
        test_str_2 = "这是第二段测试文本"

        print(f"\n1. 保存字符串: '{test_str_1}'")
        result = dedup.save_str(test_str_1)
        print(f"   结果: {'成功' if result else '失败'}")

        print(f"\n2. 检查字符串是否存在: '{test_str_1}'")
        exists = dedup.check_if_deduplicate_str(test_str_1)
        print(f"   结果: {'存在' if exists else '不存在'}")

        print(f"\n3. 保存第二个字符串: '{test_str_2}'")
        result = dedup.save_str(test_str_2)
        print(f"   结果: {'成功' if result else '失败'}")

        print(f"\n4. 删除字符串: '{test_str_1}'")
        result = dedup.delete_str(test_str_1)
        print(f"   结果: {'成功' if result else '失败'}")

        print(f"\n5. 检查已删除的字符串: '{test_str_1}'")
        exists = dedup.check_if_deduplicate_str(test_str_1)
        print(f"   结果: {'仍存在（错误）' if exists else '不存在（正确）'}")

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)

    print()

def test_document_operations():
    """测试 Document 对象的操作"""
    print("=" * 70)
    print("测试 4: Document 对象操作")
    print("=" * 70)

    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    md5_file = os.path.join(temp_dir, "test_md5.txt")

    try:
        dedup = Deduplicator(md5_file)

        # 创建测试 Document
        doc1 = Document(
            page_content="这是第一个文档的内容",
            metadata={"source": "test1.txt", "page": 1}
        )

        doc2 = Document(
            page_content="这是第二个文档的内容",
            metadata={"source": "test2.txt", "page": 1}
        )

        doc3 = Document(
            page_content="这是第一个文档的内容",  # 与 doc1 内容相同
            metadata={"source": "test3.txt", "page": 2}
        )

        print(f"\n1. Document 转 MD5:")
        md5_1 = Deduplicator.document_to_md5(doc1)
        md5_2 = Deduplicator.document_to_md5(doc2)
        md5_3 = Deduplicator.document_to_md5(doc3)
        print(f"   Doc1 MD5: {md5_1}")
        print(f"   Doc2 MD5: {md5_2}")
        print(f"   Doc3 MD5: {md5_3}")
        print(f"   Doc1 和 Doc3 MD5 相同: {md5_1 == md5_3}")

        print(f"\n2. 保存 Document1")
        result = dedup.save_document(doc1)
        print(f"   结果: {'成功' if result else '失败'}")

        print(f"\n3. 检查 Document1 是否存在")
        exists = dedup.check_if_deduplicate_document(doc1)
        print(f"   结果: {'存在' if exists else '不存在'}")

        print(f"\n4. 检查 Document3（内容与 Doc1 相同）")
        exists = dedup.check_if_deduplicate_document(doc3)
        print(f"   结果: {'存在（去重生效）' if exists else '不存在（去重失败）'}")

        print(f"\n5. 保存 Document2")
        result = dedup.save_document(doc2)
        print(f"   结果: {'成功' if result else '失败'}")

        print(f"\n6. 删除 Document1")
        result = dedup.delete_document(doc1)
        print(f"   结果: {'成功' if result else '失败'}")

        print(f"\n7. 检查已删除的 Document1")
        exists = dedup.check_if_deduplicate_document(doc1)
        print(f"   结果: {'仍存在（错误）' if exists else '不存在（正确）'}")

        print(f"\n8. 检查 Document2（未删除）")
        exists = dedup.check_if_deduplicate_document(doc2)
        print(f"   结果: {'存在（正确）' if exists else '不存在（错误）'}")

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)

    print()

def test_batch_operations():
    """测试批量操作性能"""
    print("=" * 70)
    print("测试 5: 批量操作性能测试")
    print("=" * 70)

    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    md5_file = os.path.join(temp_dir, "test_md5.txt")

    try:
        dedup = Deduplicator(md5_file)

        # 生成 100 个测试文档
        docs = []
        for i in range(100):
            doc = Document(
                page_content=f"这是第 {i} 个文档的内容，包含一些测试数据：{i * 123}",
                metadata={"source": f"test_{i}.txt"}
            )
            docs.append(doc)

        print(f"\n1. 批量保存 {len(docs)} 个 Document")
        success_count = 0
        for doc in docs:
            if dedup.save_document(doc):
                success_count += 1
        print(f"   成功保存: {success_count}/{len(docs)}")

        print(f"\n2. 批量检查 {len(docs)} 个 Document")
        exists_count = 0
        for doc in docs:
            if dedup.check_if_deduplicate_document(doc):
                exists_count += 1
        print(f"   存在: {exists_count}/{len(docs)}")

        print(f"\n3. 重复保存相同的 Document（测试去重）")
        duplicate_success = 0
        for doc in docs[:10]:  # 只测试前 10 个
            if dedup.save_document(doc):
                duplicate_success += 1
        print(f"   重复保存成功（已存在）: {duplicate_success}/10")

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)

    print()

def main():
    """主测试函数"""
    print("\n")
    print("=" * 70)
    print("Deduplicator 去重器测试")
    print("=" * 70)
    print()

    try:
        # 运行所有测试
        test_str_to_md5()
        test_md5_operations()
        test_str_operations()
        test_document_operations()
        test_batch_operations()

        print("=" * 70)
        print("所有测试完成！")
        print("=" * 70)
        print()

    except Exception as e:
        print(f"\n错误: 测试过程中出现异常")
        print(f"异常信息: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
