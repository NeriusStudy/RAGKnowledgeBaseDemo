"""
KnowledgeBase 集成测试
测试 FileStore + Splitter + Deduplicator + RAGService 的完整流程
使用 RAG-Multi-Corpus 数据集进行真实场景测试
"""
import os
import sys

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from KnowledgeBase import KnowledgeBase
import config

def print_separator(title: str):
    """打印分隔线"""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70 + "\n")

def test_create_knowledgebase():
    """测试 1: 创建知识库"""
    print_separator("测试 1: 创建知识库")

    kb_name = "test_rag_corpus"
    kb_path = f"data/knowledge/{kb_name}/"

    # 如果已存在则删除
    import shutil
    if os.path.exists(kb_path):
        shutil.rmtree(kb_path)
        print(f"已删除旧的知识库: {kb_path}")

    # 创建知识库
    kb = KnowledgeBase(
        name=kb_name,
        knowledgebase_store_path=kb_path,
        file_store_path=None,  # 使用默认路径
        document_store_path=None,
        md5_store_path=None,
        file_document_map_store_path=None,
        RAG_store_path=None,
    )

    print(f"[SUCCESS] 知识库创建成功: {kb.get_name()}")
    print(f"  存储路径: {kb_path}")
    print(f"  Embedding 模型: {kb.get_RAG_service_embedding_model_name()}")
    print(f"  Rerank 模型: {kb.get_RAG_service_rerank_model_name()}")
    print(f"  切分大小: {kb.get_file_store_splitter_chunk_size()}")
    print(f"  切分重叠: {kb.get_file_store_splitter_chunk_overlap()}")

    return kb

def test_add_single_file(kb: KnowledgeBase):
    """测试 2: 添加单个文件"""
    print_separator("测试 2: 添加单个文件")

    # 使用 TechEdu Academy 的 TXT 文件
    file_path = os.path.join(project_root, "RAG-Multi-Corpus/datasets/TechEdu Academy/txt/Python_Course_Outline.txt")

    if not os.path.exists(file_path):
        print(f"[ERROR] 测试文件不存在: {file_path}")
        return False

    print(f"添加文件: {os.path.basename(file_path)}")
    success = kb.add_file(file_path)

    if success:
        print(f"[SUCCESS] 文件添加成功")

        # 查看文件列表
        files = kb.get_all_files()
        print(f"\n当前文件列表 ({len(files)} 个):")
        for f in files:
            print(f"  - {f}")

        # 查看文档切分情况
        docs = kb.get_file_documents("Python_Course_Outline.txt")
        print(f"\n文档切分情况:")
        print(f"  文档数量: {len(docs)}")
        if docs:
            print(f"  第一个文档预览: {docs[0].page_content[:100]}...")
    else:
        print(f"[FAILED] 文件添加失败")
        return False

    return True

def test_add_multiple_files(kb: KnowledgeBase):
    """测试 3: 批量添加文件"""
    print_separator("测试 3: 批量添加多个文件")

    # 添加 TechEdu Academy 的多个文件
    base_path = os.path.join(project_root, "RAG-Multi-Corpus/datasets/TechEdu Academy")

    file_paths = [
        os.path.join(base_path, "txt/Student_Enrollment_Guide.txt"),
        os.path.join(base_path, "txt/Data_Science_Career_Track.txt"),
        os.path.join(base_path, "json/academy_overview.json"),
        os.path.join(base_path, "json/course_catalog.json"),
    ]

    # 过滤存在的文件
    existing_files = [f for f in file_paths if os.path.exists(f)]

    print(f"准备添加 {len(existing_files)} 个文件:")
    for f in existing_files:
        print(f"  - {os.path.basename(f)}")

    success = kb.add_files(existing_files)

    if success:
        print(f"\n[SUCCESS] 批量添加成功")
    else:
        print(f"\n[WARNING] 部分文件添加失败")

    # 查看文件列表
    files = kb.get_all_files()
    print(f"\n当前文件列表 ({len(files)} 个):")
    for f in files:
        docs = kb.get_file_documents(f)
        print(f"  - {f} ({len(docs)} 个文档)")

    return True

def test_deduplication(kb: KnowledgeBase):
    """测试 4: 文件去重"""
    print_separator("测试 4: 文件去重测试")

    # 尝试添加已存在的文件
    file_path = os.path.join(project_root, "RAG-Multi-Corpus/datasets/TechEdu Academy/txt/Python_Course_Outline.txt")

    print(f"尝试重复添加文件: {os.path.basename(file_path)}")

    files_before = kb.get_all_files()
    print(f"添加前文件数: {len(files_before)}")

    success = kb.add_file(file_path)

    files_after = kb.get_all_files()
    print(f"添加后文件数: {len(files_after)}")

    if len(files_before) == len(files_after):
        print(f"[SUCCESS] 去重成功，重复文件未添加")
    else:
        print(f"[FAILED] 去重失败，重复文件被添加")

    return True

def test_search_vector(kb: KnowledgeBase):
    """测试 5: 向量检索"""
    print_separator("测试 5: 向量检索")

    query = "What are the main topics covered in the Python course?"
    print(f"查询问题: {query}")
    print(f"检索模式: vector")

    results = kb.search(query, mod="vector", k=3)

    print(f"\n检索结果 ({len(results)} 个):")
    for i, doc in enumerate(results, 1):
        print(f"\n结果 {i}:")
        print(f"  内容: {doc.page_content[:150]}...")
        print(f"  元数据: {doc.metadata}")

    return True

def test_search_keyword(kb: KnowledgeBase):
    """测试 6: 关键词检索"""
    print_separator("测试 6: 关键词检索")

    query = "Python programming modules"
    print(f"查询问题: {query}")
    print(f"检索模式: keyword")

    results = kb.search(query, mod="keyword", k=3)

    print(f"\n检索结果 ({len(results)} 个):")
    for i, doc in enumerate(results, 1):
        print(f"\n结果 {i}:")
        print(f"  内容: {doc.page_content[:150]}...")
        print(f"  元数据: {doc.metadata}")

    return True

def test_search_hybrid(kb: KnowledgeBase):
    """测试 7: 混合检索"""
    print_separator("测试 7: 混合检索 (Vector + Keyword + Rerank)")

    query = "How long is the Data Science bootcamp?"
    print(f"查询问题: {query}")
    print(f"检索模式: hybrid")

    results = kb.search(query, mod="hybrid", k=5, vector_weight=0.6, keyword_weight=0.4)

    print(f"\n检索结果 ({len(results)} 个):")
    for i, doc in enumerate(results, 1):
        print(f"\n结果 {i}:")
        print(f"  内容: {doc.page_content[:150]}...")
        print(f"  元数据: {doc.metadata}")

    # 测试字符串返回格式
    print(f"\n\n测试字符串返回格式:")
    string_results = kb.search_as_strings(query, mod="hybrid", k=3)
    print(f"返回 {len(string_results)} 个字符串:")
    for i, text in enumerate(string_results, 1):
        print(f"\n字符串 {i}: {text[:100]}...")

    return True

def test_delete_file(kb: KnowledgeBase):
    """测试 8: 删除文件"""
    print_separator("测试 8: 删除文件")

    file_name = "Python_Course_Outline.txt"

    files_before = kb.get_all_files()
    print(f"删除前文件数: {len(files_before)}")
    print(f"删除文件: {file_name}")

    success = kb.delete_file(file_name)

    files_after = kb.get_all_files()
    print(f"删除后文件数: {len(files_after)}")

    if success and len(files_after) == len(files_before) - 1:
        print(f"[SUCCESS] 文件删除成功")

        # 验证检索结果中是否还有该文件的文档
        results = kb.search("Python course", mod="vector", k=10)
        has_deleted_file = any("Python_Course_Outline.txt" in doc.metadata.get("source", "") for doc in results)

        if not has_deleted_file:
            print(f"[SUCCESS] 检索结果中已无该文件的文档")
        else:
            print(f"[WARNING] 检索结果中仍有该文件的文档")
    else:
        print(f"[FAILED] 文件删除失败")

    return True

def test_statistics(kb: KnowledgeBase):
    """测试 9: 统计信息"""
    print_separator("测试 9: 知识库统计信息")

    files = kb.get_all_files()
    print(f"文件总数: {len(files)}")

    total_docs = 0
    print(f"\n文件详情:")
    for f in files:
        docs = kb.get_file_documents(f)
        total_docs += len(docs)
        print(f"  - {f}: {len(docs)} 个文档")

    print(f"\n文档总数: {total_docs}")

    return True

def main():
    """主测试流程"""
    print("=" * 70)
    print("KnowledgeBase 集成测试")
    print("测试 FileStore + Splitter + Deduplicator + RAGService")
    print("=" * 70)

    try:
        # 测试 1: 创建知识库
        kb = test_create_knowledgebase()

        # 测试 2: 添加单个文件
        if not test_add_single_file(kb):
            print("\n[ERROR] 测试中断")
            return

        # 测试 3: 批量添加文件
        test_add_multiple_files(kb)

        # 测试 4: 去重测试
        test_deduplication(kb)

        # 测试 5-7: 检索测试
        test_search_vector(kb)
        test_search_keyword(kb)
        test_search_hybrid(kb)

        # 测试 8: 删除文件
        test_delete_file(kb)

        # 测试 9: 统计信息
        test_statistics(kb)

        print_separator("所有测试完成")
        print("[SUCCESS] 集成测试全部通过！")

        # 询问是否删除测试数据
        print(f"\n知识库路径: {kb.knowledgebase_store_path}")
        print(f"提示: 可以手动检查生成的文件，或运行以下代码删除测试数据:")
        print(f"  kb.delete_me()")

    except Exception as e:
        print(f"\n[ERROR] 测试过程中出现异常")
        print(f"异常信息: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
