"""
构建完整知识库脚本

遍历 RAG-Multi-Corpus/datasets/ 目录下的所有企业数据，
为每个企业创建独立的知识库，存储到 data/knowledge/ 目录。

支持的企业：
1. Aventro Motors - 汽车
2. Cendara University - 学术教育
3. CloudWay-24 - 云服务/航空
4. TechEdu Academy - 在线教育
5. Velvera Technologies - 企业技术
6. ZX Bank - 银行金融
"""

import os
import sys
import json
from pathlib import Path
from KnowledgeBase import KnowledgeBase
import config

# 企业数据映射
ENTERPRISES = {
    "aventro_motors": {
        "name": "aventro_motors",
        "display_name": "Aventro Motors",
        "source_dir": "RAG-Multi-Corpus/datasets/Aventro Motors",
        "industry": "汽车",
    },
    "cendara_university": {
        "name": "cendara_university",
        "display_name": "Cendara University",
        "source_dir": "RAG-Multi-Corpus/datasets/Cendara University",
        "industry": "学术教育",
    },
    "cloudway_24": {
        "name": "cloudway_24",
        "display_name": "CloudWay-24",
        "source_dir": "RAG-Multi-Corpus/datasets/CloudWay-24",
        "industry": "云服务/航空",
    },
    "techedu_academy": {
        "name": "techedu_academy",
        "display_name": "TechEdu Academy",
        "source_dir": "RAG-Multi-Corpus/datasets/TechEdu Academy",
        "industry": "在线教育",
    },
    "velvera_technologies": {
        "name": "velvera_technologies",
        "display_name": "Velvera Technologies",
        "source_dir": "RAG-Multi-Corpus/datasets/Velvera Technologies",
        "industry": "企业技术",
    },
    "zx_bank": {
        "name": "zx_bank",
        "display_name": "ZX Bank",
        "source_dir": "RAG-Multi-Corpus/datasets/ZX Bank",
        "industry": "银行金融",
    },
}

def collect_files(source_dir: str) -> list[str]:
    """
    收集目录下的所有文本文件（txt, json, csv, md）
    Args:
        source_dir: 源目录路径
    Returns:
        文件路径列表
    """
    supported_extensions = ['.txt', '.json', '.csv', '.md']
    files = []

    source_path = Path(source_dir)
    if not source_path.exists():
        print(f"[警告] 目录不存在: {source_dir}")
        return []

    for root, dirs, filenames in os.walk(source_dir):
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext in supported_extensions:
                file_path = os.path.join(root, filename)
                files.append(file_path)

    return files

def build_knowledge_base(enterprise_key: str, enterprise_info: dict) -> dict:
    """
    为单个企业构建知识库
    Args:
        enterprise_key: 企业键名
        enterprise_info: 企业信息字典
    Returns:
        构建结果字典
    """
    print(f"\n{'='*70}")
    print(f"开始构建知识库: {enterprise_info['display_name']} ({enterprise_info['industry']})")
    print(f"{'='*70}\n")

    # 收集文件
    files = collect_files(enterprise_info['source_dir'])
    if not files:
        print(f"[错误] 未找到任何文件: {enterprise_info['source_dir']}")
        return {
            "success": False,
            "enterprise": enterprise_info['display_name'],
            "file_count": 0,
            "error": "未找到文件"
        }

    print(f"找到 {len(files)} 个文件")

    # 创建知识库
    kb_name = enterprise_info['name']
    kb_store_path = f"data/knowledge/{kb_name}/"

    # 删除旧的知识库（如果存在）
    import shutil
    if os.path.exists(kb_store_path):
        print(f"删除旧的知识库: {kb_store_path}")
        shutil.rmtree(kb_store_path)

    try:
        # 初始化知识库
        kb = KnowledgeBase(
            name=kb_name,
            knowledgebase_store_path=kb_store_path,
            file_store_path=None,
            document_store_path=None,
            md5_store_path=None,
            file_document_map_store_path=None,
            RAG_store_path=None,
            embedding_model_name=config.EMBEDDING_MODEL_NAME,
            rerank_model_name=config.RERANK_MODEL_NAME,
            splitter_chunk_size=config.SPLITTER_CHUNK_SIZE,
            splitter_chunk_overlap=config.SPLITTER_CHUNK_OVERLAP,
        )

        print(f"[成功] 知识库初始化完成")
        print(f"  存储路径: {kb_store_path}")
        print(f"  Embedding 模型: {config.EMBEDDING_MODEL_NAME}")
        print(f"  Rerank 模型: {config.RERANK_MODEL_NAME}")
        print(f"  切分大小: {config.SPLITTER_CHUNK_SIZE}")
        print(f"  切分重叠: {config.SPLITTER_CHUNK_OVERLAP}\n")

        # 批量添加文件
        print(f"开始添加文件到知识库...")
        success_count = 0
        fail_count = 0

        for i, file_path in enumerate(files, 1):
            file_name = os.path.basename(file_path)
            print(f"[{i}/{len(files)}] 添加文件: {file_name}")

            if kb.add_file(file_path):
                success_count += 1
            else:
                fail_count += 1

        # 统计信息
        total_files = len(kb.get_all_files())
        total_docs = kb.file_store.get_total_document_count()

        print(f"\n{'='*70}")
        print(f"知识库构建完成: {enterprise_info['display_name']}")
        print(f"{'='*70}")
        print(f"  添加成功: {success_count} 个文件")
        print(f"  添加失败: {fail_count} 个文件")
        print(f"  文件总数: {total_files}")
        print(f"  文档总数: {total_docs}")
        print(f"{'='*70}\n")

        return {
            "success": True,
            "enterprise": enterprise_info['display_name'],
            "enterprise_key": enterprise_key,
            "industry": enterprise_info['industry'],
            "kb_path": kb_store_path,
            "file_count": total_files,
            "document_count": total_docs,
            "success_files": success_count,
            "failed_files": fail_count,
        }

    except Exception as e:
        print(f"[错误] 知识库构建失败: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "enterprise": enterprise_info['display_name'],
            "error": str(e)
        }

def save_metadata(results: list[dict]):
    """
    保存知识库元数据到 JSON 文件
    Args:
        results: 构建结果列表
    """
    metadata_path = "../data/knowledge/knowledge_bases.json"

    # 确保目录存在
    os.makedirs(os.path.dirname(metadata_path), exist_ok=True)

    metadata = {
        "total_knowledge_bases": len([r for r in results if r['success']]),
        "created_at": "2026-08-15",
        "knowledge_bases": {}
    }

    for result in results:
        if result['success']:
            metadata['knowledge_bases'][result['enterprise_key']] = {
                "name": result['enterprise'],
                "industry": result['industry'],
                "kb_path": result['kb_path'],
                "file_count": result['file_count'],
                "document_count": result['document_count'],
            }

    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"\n[成功] 元数据已保存: {metadata_path}")

def main():
    """主函数"""
    print("\n" + "="*70)
    print("RAG-Multi-Corpus 完整知识库构建")
    print("="*70 + "\n")

    print(f"将为以下 {len(ENTERPRISES)} 个企业构建知识库：")
    for key, info in ENTERPRISES.items():
        print(f"  - {info['display_name']} ({info['industry']})")

    input("\n按 Enter 键开始构建...")

    results = []

    # 为每个企业构建知识库
    for enterprise_key, enterprise_info in ENTERPRISES.items():
        result = build_knowledge_base(enterprise_key, enterprise_info)
        results.append(result)

    # 保存元数据
    save_metadata(results)

    # 打印总结
    print("\n" + "="*70)
    print("所有知识库构建完成")
    print("="*70 + "\n")

    success_count = len([r for r in results if r['success']])
    fail_count = len([r for r in results if not r['success']])

    print(f"构建成功: {success_count} 个知识库")
    print(f"构建失败: {fail_count} 个知识库\n")

    if success_count > 0:
        print("成功构建的知识库：")
        for result in results:
            if result['success']:
                print(f"  ✓ {result['enterprise']}: {result['file_count']} 个文件, {result['document_count']} 个文档")

    if fail_count > 0:
        print("\n失败的知识库：")
        for result in results:
            if not result['success']:
                print(f"  ✗ {result['enterprise']}: {result.get('error', '未知错误')}")

    print("\n" + "="*70)
    print("知识库路径: data/knowledge/")
    print("元数据文件: data/knowledge/knowledge_bases.json")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
