"""
Splitter 文档切分器测试脚本

测试内容：
1. 文本切分功能
2. 单个 Document 切分
3. 多个 Document 批量切分
4. 切分后 MD5 自动添加
5. 不同参数配置的切分效果
6. 中文文本切分优化
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Splitter import Splitter
from langchain_core.documents import Document
import config

def test_split_text():
    """测试文本切分功能"""
    print("=" * 70)
    print("测试 1: 文本切分功能")
    print("=" * 70)

    splitter = Splitter(chunk_size=100, chunk_overlap=20)

    # 测试短文本
    short_text = "这是一段短文本。"
    chunks = splitter.split_text(short_text)
    print(f"\n1. 短文本切分:")
    print(f"   原文本: {short_text}")
    print(f"   切分结果: {len(chunks)} 个块")
    for i, chunk in enumerate(chunks, 1):
        print(f"   块 {i}: {chunk}")

    # 测试长文本
    long_text = """
    Python 是一种广泛使用的高级编程语言，由 Guido van Rossum 创造并于 1991 年首次发布。
    Python 的设计哲学强调代码的可读性和简洁的语法（尤其是使用空格缩进划分代码块）。
    Python 支持多种编程范式，包括面向对象、命令式、函数式和过程式编程。
    Python 拥有动态类型系统和垃圾回收功能，能够自动管理内存使用。
    Python 的标准库非常庞大，提供了丰富的模块和工具。
    Python 社区非常活跃，有大量的第三方库可供使用。
    Python 被广泛应用于 Web 开发、数据分析、人工智能、科学计算等领域。
    """

    chunks = splitter.split_text(long_text)
    print(f"\n2. 长文本切分:")
    print(f"   原文本长度: {len(long_text)} 字符")
    print(f"   切分结果: {len(chunks)} 个块")
    for i, chunk in enumerate(chunks, 1):
        print(f"   块 {i} ({len(chunk)} 字符): {chunk[:50]}...")

    print()

def test_split_document():
    """测试单个 Document 切分"""
    print("=" * 70)
    print("测试 2: 单个 Document 切分")
    print("=" * 70)

    splitter = Splitter(chunk_size=150, chunk_overlap=30)

    # 创建测试 Document
    doc = Document(
        page_content="""
        机器学习是人工智能的一个分支，它使计算机能够在没有明确编程的情况下学习。
        机器学习的核心是从数据中学习模式和规律。常见的机器学习算法包括监督学习、
        无监督学习和强化学习。监督学习使用标记的训练数据来学习输入和输出之间的映射关系。
        无监督学习则从未标记的数据中发现隐藏的模式和结构。强化学习通过与环境交互来学习
        最优的行为策略。机器学习在图像识别、自然语言处理、推荐系统等领域有广泛应用。
        """,
        metadata={"source": "ml_intro.txt", "page": 1, "author": "AI Researcher"}
    )

    print(f"\n1. 原始 Document:")
    print(f"   内容长度: {len(doc.page_content)} 字符")
    print(f"   Metadata: {doc.metadata}")

    # 切分 Document
    split_docs = splitter.split_document(doc)

    print(f"\n2. 切分结果: {len(split_docs)} 个 Document")
    for i, split_doc in enumerate(split_docs, 1):
        print(f"\n   Document {i}:")
        print(f"     内容长度: {len(split_doc.page_content)} 字符")
        print(f"     内容预览: {split_doc.page_content[:60]}...")
        print(f"     MD5: {split_doc.metadata.get('md5', 'N/A')}")
        print(f"     原始 Metadata: source={split_doc.metadata.get('source')}, page={split_doc.metadata.get('page')}")

    print()

def test_split_documents_batch():
    """测试多个 Document 批量切分"""
    print("=" * 70)
    print("测试 3: 多个 Document 批量切分")
    print("=" * 70)

    splitter = Splitter(chunk_size=100, chunk_overlap=20)

    # 创建多个测试 Document
    docs = [
        Document(
            page_content="深度学习是机器学习的一个子领域，它使用多层神经网络来学习数据的表示。深度学习在计算机视觉、语音识别等领域取得了突破性进展。",
            metadata={"source": "dl_intro.txt", "topic": "deep_learning"}
        ),
        Document(
            page_content="自然语言处理（NLP）是人工智能的一个重要分支，致力于让计算机理解和生成人类语言。NLP 的应用包括机器翻译、情感分析、文本摘要等。",
            metadata={"source": "nlp_intro.txt", "topic": "nlp"}
        ),
        Document(
            page_content="计算机视觉是研究如何让计算机从图像或视频中获取信息的学科。常见任务包括图像分类、目标检测、图像分割等。",
            metadata={"source": "cv_intro.txt", "topic": "computer_vision"}
        )
    ]

    print(f"\n1. 原始 Document 数量: {len(docs)}")
    for i, doc in enumerate(docs, 1):
        print(f"   Document {i}: {len(doc.page_content)} 字符, source={doc.metadata['source']}")

    # 批量切分
    split_docs = splitter.split_documents(docs)

    print(f"\n2. 切分后 Document 数量: {len(split_docs)}")
    for i, split_doc in enumerate(split_docs, 1):
        print(f"   Document {i}: {len(split_doc.page_content)} 字符, source={split_doc.metadata.get('source')}, MD5={split_doc.metadata.get('md5', 'N/A')[:8]}...")

    print()

def test_different_chunk_sizes():
    """测试不同参数配置的切分效果"""
    print("=" * 70)
    print("测试 4: 不同参数配置的切分效果")
    print("=" * 70)

    test_text = """
    Python 编程语言具有简洁优雅的语法，强大的标准库，以及活跃的社区支持。
    Python 广泛应用于 Web 开发、数据科学、人工智能、自动化脚本等多个领域。
    学习 Python 是进入编程世界的绝佳选择。Python 的 Hello World 程序只需一行代码。
    """

    configs = [
        {"chunk_size": 50, "chunk_overlap": 10, "label": "小块（50字符，重叠10）"},
        {"chunk_size": 100, "chunk_overlap": 20, "label": "中块（100字符，重叠20）"},
        {"chunk_size": 200, "chunk_overlap": 50, "label": "大块（200字符，重叠50）"},
    ]

    for config_dict in configs:
        splitter = Splitter(
            chunk_size=config_dict["chunk_size"],
            chunk_overlap=config_dict["chunk_overlap"]
        )

        chunks = splitter.split_text(test_text)

        print(f"\n{config_dict['label']}:")
        print(f"  切分结果: {len(chunks)} 个块")
        for i, chunk in enumerate(chunks, 1):
            print(f"  块 {i} ({len(chunk)} 字符): {chunk.strip()[:40]}...")

    print()

def test_md5_generation():
    """测试切分后 MD5 自动添加"""
    print("=" * 70)
    print("测试 5: 切分后 MD5 自动添加")
    print("=" * 70)

    splitter = Splitter(chunk_size=100, chunk_overlap=20)

    doc = Document(
        page_content="测试文本内容，用于验证 MD5 是否正确添加到切分后的每个 Document 的 metadata 中。" * 3,
        metadata={"source": "test.txt"}
    )

    print(f"\n1. 原始 Document:")
    print(f"   内容长度: {len(doc.page_content)} 字符")
    print(f"   是否有 MD5: {'md5' in doc.metadata}")

    split_docs = splitter.split_document(doc)

    print(f"\n2. 切分后的 Document:")
    print(f"   切分数量: {len(split_docs)}")

    all_have_md5 = all('md5' in d.metadata for d in split_docs)
    print(f"   所有块都有 MD5: {all_have_md5}")

    print(f"\n3. MD5 详情:")
    for i, split_doc in enumerate(split_docs, 1):
        md5 = split_doc.metadata.get('md5', 'N/A')
        print(f"   块 {i}: MD5={md5}, 长度={len(md5) if md5 != 'N/A' else 0}")

    print()

def test_chinese_text_splitting():
    """测试中文文本切分优化"""
    print("=" * 70)
    print("测试 6: 中文文本切分优化")
    print("=" * 70)

    # 使用默认的中文优化分隔符
    splitter = Splitter(chunk_size=80, chunk_overlap=15)

    chinese_text = """
    人工智能（Artificial Intelligence，简称 AI）是计算机科学的一个分支。它企图了解智能的实质，
    并生产出一种新的能以人类智能相似的方式做出反应的智能机器。该领域的研究包括机器人、
    语言识别、图像识别、自然语言处理和专家系统等。人工智能从诞生以来，理论和技术日益成熟，
    应用领域也不断扩大，可以设想，未来人工智能带来的科技产品，将会是人类智慧的"容器"。
    """

    print(f"\n1. 中文文本切分:")
    print(f"   原文本长度: {len(chinese_text)} 字符")
    print(f"   使用分隔符: {splitter.get_separators()[:5]}...")  # 显示前5个分隔符

    chunks = splitter.split_text(chinese_text)

    print(f"\n2. 切分结果: {len(chunks)} 个块")
    for i, chunk in enumerate(chunks, 1):
        print(f"\n   块 {i} ({len(chunk)} 字符):")
        print(f"   {chunk.strip()}")

    print()

def test_config_parameters():
    """测试配置参数的获取"""
    print("=" * 70)
    print("测试 7: 配置参数的获取")
    print("=" * 70)

    splitter = Splitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", ","],
        length_function=len
    )

    print(f"\n配置参数:")
    print(f"  chunk_size: {splitter.get_chunk_size()}")
    print(f"  chunk_overlap: {splitter.get_chunk_overlap()}")
    print(f"  separators: {splitter.get_separators()}")
    print(f"  length_function: {splitter.get_length_function()}")

    print()

def main():
    """主测试函数"""
    print("\n")
    print("=" * 70)
    print("Splitter 文档切分器测试")
    print("=" * 70)
    print()

    try:
        # 运行所有测试
        test_split_text()
        test_split_document()
        test_split_documents_batch()
        test_different_chunk_sizes()
        test_md5_generation()
        test_chinese_text_splitting()
        test_config_parameters()

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
