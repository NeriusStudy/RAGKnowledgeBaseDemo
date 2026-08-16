"""
FileStore 文件存储测试脚本

测试内容：
1. 保存单个文件
2. 文件去重功能
3. 获取文件信息
4. 文件-文档映射关系
5. 删除文件功能
6. 批量文件处理
7. 统计信息获取
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from FileStore import FileStore
import tempfile
import shutil

def create_filestore(temp_dir, kb_name):
    """创建 FileStore 实例的辅助函数"""
    kb_data_dir = os.path.join(temp_dir, "knowledge", kb_name)
    file_store_path = os.path.join(kb_data_dir, "file_store", "files")
    md5_store_path = os.path.join(kb_data_dir, "file_store", "md5.txt")
    file_doc_map_path = os.path.join(kb_data_dir, "file_store", "file_document_map.json")

    return FileStore(
        file_store_path=file_store_path,
        document_store_path=file_store_path,
        md5_store_path=md5_store_path,
        file_document_map_store_path=file_doc_map_path
    )

def create_test_files(test_dir):
    """创建测试文件"""
    test_files = []

    # 文件 1: Python 教程
    file1_path = os.path.join(test_dir, "python_tutorial.txt")
    with open(file1_path, 'w', encoding='utf-8') as f:
        f.write("""
Python 编程基础教程

第一章：Python 简介
Python 是一种高级编程语言，由 Guido van Rossum 创造。
它具有简洁优雅的语法，适合初学者学习。

第二章：变量和数据类型
Python 支持多种数据类型，包括整数、浮点数、字符串、列表、元组、字典等。
变量不需要声明类型，Python 会自动推断。

第三章：控制流程
Python 使用 if-elif-else 语句进行条件判断。
使用 for 和 while 循环进行迭代操作。

第四章：函数定义
使用 def 关键字定义函数。
函数可以接受参数并返回值。

第五章：面向对象编程
Python 支持类和对象的概念。
使用 class 关键字定义类。
        """)
    test_files.append(file1_path)

    # 文件 2: 机器学习概述
    file2_path = os.path.join(test_dir, "ml_overview.txt")
    with open(file2_path, 'w', encoding='utf-8') as f:
        f.write("""
机器学习基础概述

监督学习：
使用标记的训练数据学习输入和输出之间的映射关系。
常见算法：线性回归、逻辑回归、决策树、随机森林、支持向量机。

无监督学习：
从未标记的数据中发现隐藏的模式和结构。
常见算法：K-means 聚类、层次聚类、主成分分析（PCA）。

强化学习：
通过与环境交互来学习最优的行为策略。
应用场景：游戏 AI、机器人控制、推荐系统。

深度学习：
使用多层神经网络学习数据的复杂表示。
应用领域：图像识别、语音识别、自然语言处理。
        """)
    test_files.append(file2_path)

    # 文件 3: Web 开发指南
    file3_path = os.path.join(test_dir, "web_dev_guide.txt")
    with open(file3_path, 'w', encoding='utf-8') as f:
        f.write("""
Web 开发技术栈

前端技术：
HTML: 网页结构标记语言
CSS: 样式表语言，用于美化网页
JavaScript: 客户端脚本语言，实现交互功能

后端技术：
Python Flask/Django: Python Web 框架
Node.js Express: JavaScript 后端框架
数据库: MySQL, PostgreSQL, MongoDB

开发工具：
版本控制: Git
编辑器: VS Code, PyCharm
浏览器开发工具: Chrome DevTools
        """)
    test_files.append(file3_path)

    return test_files

def test_save_single_file():
    """测试保存单个文件"""
    print("=" * 70)
    print("测试 1: 保存单个文件")
    print("=" * 70)

    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    test_files_dir = os.path.join(temp_dir, "test_files")
    os.makedirs(test_files_dir)

    try:
        # 创建测试文件
        test_files = create_test_files(test_files_dir)

        # 创建 FileStore
        file_store = create_filestore(temp_dir, "test_kb_1")

        # 保存第一个文件
        print(f"\n1. 保存文件: python_tutorial.txt")
        split_docs = file_store.save_file(test_files[0])

        print(f"   切分结果: {len(split_docs)} 个文档")
        for i, doc in enumerate(split_docs[:3], 1):  # 只显示前3个
            print(f"   文档 {i}: {len(doc.page_content)} 字符, MD5={doc.metadata.get('md5', 'N/A')[:8]}...")

        # 检查文件是否保存成功
        all_files = file_store.get_all_file_name()
        print(f"\n2. 当前存储的文件: {all_files}")
        print(f"   文件总数: {file_store.get_file_count()}")
        print(f"   文档总数: {file_store.get_total_document_count()}")

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)

    print()

def test_file_deduplication():
    """测试文件去重功能"""
    print("=" * 70)
    print("测试 2: 文件去重功能")
    print("=" * 70)

    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    test_files_dir = os.path.join(temp_dir, "test_files")
    os.makedirs(test_files_dir)

    try:
        # 创建测试文件
        test_files = create_test_files(test_files_dir)

        # 创建 FileStore
        file_store = create_filestore(temp_dir, "test_kb_2")

        # 第一次保存文件
        print(f"\n1. 第一次保存文件: python_tutorial.txt")
        split_docs_1 = file_store.save_file(test_files[0])
        print(f"   切分结果: {len(split_docs_1)} 个文档")

        # 第二次保存相同文件（应该被去重）
        print(f"\n2. 第二次保存相同文件: python_tutorial.txt")
        split_docs_2 = file_store.save_file(test_files[0])
        print(f"   切分结果: {len(split_docs_2)} 个文档（去重后应为0）")

        # 检查文件数量
        print(f"\n3. 文件总数: {file_store.get_file_count()} （应为1）")

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)

    print()

def test_get_file_info():
    """测试获取文件信息"""
    print("=" * 70)
    print("测试 3: 获取文件信息")
    print("=" * 70)

    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    test_files_dir = os.path.join(temp_dir, "test_files")
    os.makedirs(test_files_dir)

    try:
        # 创建测试文件
        test_files = create_test_files(test_files_dir)

        # 创建 FileStore
        file_store = create_filestore(temp_dir, "test_kb_3")

        # 保存文件
        file_store.save_file(test_files[0])

        file_name = "python_tutorial.txt"

        # 获取文件路径
        print(f"\n1. 获取文件路径:")
        file_path = file_store.get_file(file_name)
        print(f"   文件路径: {file_path}")
        print(f"   文件存在: {os.path.exists(file_path) if file_path else False}")

        # 获取文档 MD5 列表
        print(f"\n2. 获取文档 MD5 列表:")
        md5_list = file_store.get_document_md5_from_file_name(file_name)
        print(f"   文档数量: {len(md5_list)}")
        for i, md5 in enumerate(md5_list[:5], 1):  # 只显示前5个
            print(f"   MD5 {i}: {md5}")

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)

    print()

def test_file_document_mapping():
    """测试文件-文档映射关系"""
    print("=" * 70)
    print("测试 4: 文件-文档映射关系")
    print("=" * 70)

    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    test_files_dir = os.path.join(temp_dir, "test_files")
    os.makedirs(test_files_dir)

    try:
        # 创建测试文件
        test_files = create_test_files(test_files_dir)

        # 创建 FileStore
        file_store = create_filestore(temp_dir, "test_kb_4")

        # 保存多个文件
        for test_file in test_files:
            file_store.save_file(test_file)

        # 获取映射关系
        print(f"\n1. 文件-文档映射关系:")
        file_doc_map = file_store.get_file_document_map()

        for file_name, file_info in file_doc_map.items():
            print(f"\n   文件: {file_name}")
            print(f"     路径: {file_info['file_path']}")
            print(f"     文档数量: {file_info['document_count']}")
            print(f"     MD5 列表: {len(file_info['document_md5_list'])} 个")

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)

    print()

def test_delete_file():
    """测试删除文件功能"""
    print("=" * 70)
    print("测试 5: 删除文件功能")
    print("=" * 70)

    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    test_files_dir = os.path.join(temp_dir, "test_files")
    os.makedirs(test_files_dir)

    try:
        # 创建测试文件
        test_files = create_test_files(test_files_dir)

        # 创建 FileStore
        file_store = create_filestore(temp_dir, "test_kb_5")

        # 保存文件
        file_store.save_file(test_files[0])
        file_store.save_file(test_files[1])

        print(f"\n1. 删除前的文件数量: {file_store.get_file_count()}")
        print(f"   文件列表: {file_store.get_all_file_name()}")

        # 删除文件
        file_name = "python_tutorial.txt"
        print(f"\n2. 删除文件: {file_name}")
        deleted_md5_list = file_store.delete_file(file_name)
        print(f"   返回的文档 MD5 数量: {len(deleted_md5_list)}")

        print(f"\n3. 删除后的文件数量: {file_store.get_file_count()}")
        print(f"   文件列表: {file_store.get_all_file_name()}")

        # 尝试删除不存在的文件
        print(f"\n4. 删除不存在的文件: non_existent.txt")
        deleted_md5_list = file_store.delete_file("non_existent.txt")
        print(f"   返回的文档 MD5 数量: {len(deleted_md5_list)}")

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)

    print()

def test_batch_processing():
    """测试批量文件处理"""
    print("=" * 70)
    print("测试 6: 批量文件处理")
    print("=" * 70)

    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    test_files_dir = os.path.join(temp_dir, "test_files")
    os.makedirs(test_files_dir)

    try:
        # 创建测试文件
        test_files = create_test_files(test_files_dir)

        # 创建 FileStore
        file_store = create_filestore(temp_dir, "test_kb_6")

        # 批量保存文件
        print(f"\n1. 批量保存 {len(test_files)} 个文件:")
        total_docs = 0
        for test_file in test_files:
            file_name = os.path.basename(test_file)
            split_docs = file_store.save_file(test_file)
            total_docs += len(split_docs)
            print(f"   {file_name}: {len(split_docs)} 个文档")

        print(f"\n2. 保存完成:")
        print(f"   文件总数: {file_store.get_file_count()}")
        print(f"   文档总数: {file_store.get_total_document_count()}")

        print(f"\n3. 所有文件列表:")
        for i, file_name in enumerate(file_store.get_all_file_name(), 1):
            doc_count = len(file_store.get_document_md5_from_file_name(file_name))
            print(f"   {i}. {file_name}: {doc_count} 个文档")

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)

    print()

def test_statistics():
    """测试统计信息获取"""
    print("=" * 70)
    print("测试 7: 统计信息获取")
    print("=" * 70)

    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    test_files_dir = os.path.join(temp_dir, "test_files")
    os.makedirs(test_files_dir)

    try:
        # 创建测试文件
        test_files = create_test_files(test_files_dir)

        # 创建 FileStore
        file_store = create_filestore(temp_dir, "test_kb_7")

        # 保存文件
        for test_file in test_files:
            file_store.save_file(test_file)

        # 获取统计信息
        print(f"\n统计信息:")
        print(f"  文件总数: {file_store.get_file_count()}")
        print(f"  文档总数: {file_store.get_total_document_count()}")

        print(f"\n  Splitter 配置:")
        print(f"    chunk_size: {file_store.get_splitter_chunk_size()}")
        print(f"    chunk_overlap: {file_store.get_splitter_chunk_overlap()}")
        print(f"    separators: {file_store.get_splitter_separaters()[:5]}...")

        print(f"\n  详细信息:")
        for file_name in file_store.get_all_file_name():
            doc_count = len(file_store.get_document_md5_from_file_name(file_name))
            file_path = file_store.get_file(file_name)
            file_size = os.path.getsize(file_path) if file_path and os.path.exists(file_path) else 0
            print(f"    {file_name}:")
            print(f"      文档数: {doc_count}")
            print(f"      文件大小: {file_size} 字节")

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)

    print()

def main():
    """主测试函数"""
    print("\n")
    print("=" * 70)
    print("FileStore 文件存储测试")
    print("=" * 70)
    print()

    try:
        # 运行所有测试
        test_save_single_file()
        test_file_deduplication()
        test_get_file_info()
        test_file_document_mapping()
        test_delete_file()
        test_batch_processing()
        test_statistics()

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
