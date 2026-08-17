"""
QA评估脚本

从 merged_all_qa_dataset.csv 中随机抽取20个问题，
使用我们构建的知识库系统回答，并与官方的 Supporting Facts 对比。

评估指标：
1. 检索准确率：检索结果是否包含 Supporting Facts 中的文档
2. 内容相似度：检索内容与 Supporting Facts 的文本相似度
3. 企业匹配度：是否从正确的企业知识库检索
"""

import os
import csv
import json
import random
import sys
from datetime import datetime
from typing import List, Dict
from KnowledgeBase import KnowledgeBase
import config

class TeeOutput:
    """
    同时输出到终端和日志文件的类
    """
    def __init__(self, log_file_path):
        self.terminal = sys.stdout
        self.log_file = open(log_file_path, 'w', encoding='utf-8')

    def write(self, message):
        self.terminal.write(message)
        self.log_file.write(message)
        self.log_file.flush()  # 实时写入

    def flush(self):
        self.terminal.flush()
        self.log_file.flush()

    def close(self):
        self.log_file.close()
        sys.stdout = self.terminal

def load_qa_dataset(csv_path: str) -> List[Dict]:
    """
    加载QA数据集
    Args:
        csv_path: CSV文件路径
    Returns:
        QA数据列表
    """
    qa_data = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            qa_data.append(row)
    return qa_data

def load_knowledge_bases() -> Dict[str, KnowledgeBase]:
    """
    加载所有知识库
    Returns:
        知识库字典 {enterprise_key: KnowledgeBase}
    """
    metadata_path = "../data/knowledge/knowledge_bases.json"

    if not os.path.exists(metadata_path):
        print(f"[错误] 元数据文件不存在: {metadata_path}")
        print("请先运行 build_complete_knowledge_base.py 构建知识库")
        return {}

    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    knowledge_bases = {}

    print("正在加载知识库...")
    for kb_key, kb_info in metadata['knowledge_bases'].items():
        try:
            kb = KnowledgeBase(
                name=kb_key,
                knowledgebase_store_path=kb_info['kb_path'],
                file_store_path=None,
                document_store_path=None,
                md5_store_path=None,
                file_document_map_store_path=None,
                RAG_store_path=None,
            )
            knowledge_bases[kb_key] = kb
            print(f"  ✓ {kb_info['name']}: {kb_info['file_count']} 个文件, {kb_info['document_count']} 个文档")
        except Exception as e:
            print(f"  ✗ {kb_info['name']}: 加载失败 - {e}")

    return knowledge_bases

def map_enterprise_name_to_key(enterprise_name: str) -> str:
    """
    将企业显示名称映射到知识库键名
    Args:
        enterprise_name: 企业显示名称
    Returns:
        知识库键名
    """
    mapping = {
        "Aventro Motors": "aventro_motors",
        "Cendara University": "cendara_university",
        "CloudWay-24": "cloudway_24",
        "Cloudway 24": "cloudway_24",
        "TechEdu Academy": "techedu_academy",
        "Velvera Technologies": "velvera_technologies",
        "ZX Bank": "zx_bank",
    }
    return mapping.get(enterprise_name, enterprise_name.lower().replace(" ", "_"))

def evaluate_single_qa(qa: Dict, knowledge_bases: Dict[str, KnowledgeBase],
                       search_mode: str = "hybrid", top_k: int = 5) -> Dict:
    """
    评估单个QA问题
    Args:
        qa: QA数据字典
        knowledge_bases: 知识库字典
        search_mode: 检索模式 (vector/keyword/hybrid)
        top_k: 返回的文档数量
    Returns:
        评估结果字典
    """
    query = qa['Query']
    enterprise_name = qa['Enterprise Name']
    query_type = qa['Query Type']

    # 解析 Supporting Facts
    try:
        supporting_facts = json.loads(qa['Supporting Facts'])
    except:
        supporting_facts = []

    # 获取对应的知识库
    kb_key = map_enterprise_name_to_key(enterprise_name)

    if kb_key not in knowledge_bases:
        return {
            "query": query,
            "enterprise": enterprise_name,
            "query_type": query_type,
            "error": f"知识库不存在: {kb_key}",
            "success": False
        }

    kb = knowledge_bases[kb_key]

    # 执行检索
    try:
        retrieved_docs = kb.search(query, mod=search_mode, k=top_k)

        # 提取检索到的文档文件名
        retrieved_filenames = set()
        retrieved_contents = []

        for doc in retrieved_docs:
            source = doc.metadata.get('source', '')
            if source:
                retrieved_filenames.add(source)
            retrieved_contents.append({
                "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                "source": source,
                "metadata": doc.metadata
            })

        # 提取 Supporting Facts 中的文件名
        expected_filenames = set()
        for fact in supporting_facts:
            filename = fact.get('filename', '')
            if filename:
                # 处理文件名（可能带路径）
                expected_filenames.add(os.path.basename(filename))

        # 计算检索准确率：检索到的文档是否包含期望的文件
        matched_files = retrieved_filenames.intersection(expected_filenames)
        precision = len(matched_files) / len(retrieved_filenames) if retrieved_filenames else 0
        recall = len(matched_files) / len(expected_filenames) if expected_filenames else 0
        f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

        return {
            "query": query,
            "enterprise": enterprise_name,
            "query_type": query_type,
            "search_mode": search_mode,
            "top_k": top_k,
            "expected_files": list(expected_filenames),
            "retrieved_files": list(retrieved_filenames),
            "matched_files": list(matched_files),
            "retrieved_contents": retrieved_contents,
            "supporting_facts": supporting_facts,
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
            "success": True
        }

    except Exception as e:
        import traceback
        return {
            "query": query,
            "enterprise": enterprise_name,
            "query_type": query_type,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "success": False
        }

def print_evaluation_result(result: Dict, index: int):
    """
    打印单个评估结果
    Args:
        result: 评估结果字典
        index: 问题序号
    """
    print(f"\n{'='*80}")
    print(f"问题 {index}")
    print(f"{'='*80}")
    print(f"企业: {result['enterprise']}")
    print(f"查询类型: {result['query_type']}")
    print(f"问题: {result['query']}")

    if not result['success']:
        print(f"\n[错误] {result.get('error', '未知错误')}")
        return

    print(f"\n检索模式: {result['search_mode']}, Top-{result['top_k']}")
    print(f"\n期望文件 ({len(result['expected_files'])} 个):")
    for filename in result['expected_files']:
        print(f"  - {filename}")

    print(f"\n检索到的文件 ({len(result['retrieved_files'])} 个):")
    for filename in result['retrieved_files']:
        matched = "✓" if filename in result['matched_files'] else "✗"
        print(f"  {matched} {filename}")

    print(f"\n匹配文件 ({len(result['matched_files'])} 个):")
    for filename in result['matched_files']:
        print(f"  ✓ {filename}")

    print(f"\n评估指标:")
    print(f"  Precision: {result['precision']:.2%}")
    print(f"  Recall: {result['recall']:.2%}")
    print(f"  F1 Score: {result['f1_score']:.2%}")

    print(f"\n检索内容预览 (前3个):")
    for i, content in enumerate(result['retrieved_contents'][:3], 1):
        print(f"\n  [{i}] 来源: {content['source']}")
        print(f"      内容: {content['content']}")

def save_evaluation_report(results: List[Dict], output_path: str):
    """
    保存评估报告到JSON文件
    Args:
        results: 评估结果列表
        output_path: 输出文件路径
    """
    # 计算总体统计
    successful_results = [r for r in results if r['success']]

    if not successful_results:
        print("[警告] 没有成功的评估结果")
        return

    avg_precision = sum(r['precision'] for r in successful_results) / len(successful_results)
    avg_recall = sum(r['recall'] for r in successful_results) / len(successful_results)
    avg_f1 = sum(r['f1_score'] for r in successful_results) / len(successful_results)

    report = {
        "summary": {
            "total_questions": len(results),
            "successful_evaluations": len(successful_results),
            "failed_evaluations": len(results) - len(successful_results),
            "average_precision": avg_precision,
            "average_recall": avg_recall,
            "average_f1_score": avg_f1,
        },
        "results": results
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n[成功] 评估报告已保存: {output_path}")

def main():
    """主函数"""
    # 创建日志目录
    log_dir = "logs/qa_test"
    os.makedirs(log_dir, exist_ok=True)

    # 生成日志文件名
    timestamp = datetime.now().strftime("%y%m%d%H%M")
    log_file_path = os.path.join(log_dir, f"{timestamp}.log")

    # 启动日志输出
    tee = TeeOutput(log_file_path)
    sys.stdout = tee

    print(f"日志文件: {log_file_path}\n")
    print("\n" + "="*80)
    print("RAG-Multi-Corpus QA 性能评估")
    print("="*80 + "\n")

    # 加载QA数据集
    qa_csv_path = "RAG-Multi-Corpus/qa_datasets/merged_all_qa_dataset.csv"
    print(f"加载QA数据集: {qa_csv_path}")
    qa_data = load_qa_dataset(qa_csv_path)
    print(f"  总问答对: {len(qa_data)} 条\n")

    # 随机抽取20个问题
    sample_size = 20
    random.seed(42)  # 固定随机种子，保证结果可复现
    sampled_qa = random.sample(qa_data, min(sample_size, len(qa_data)))
    print(f"随机抽取 {len(sampled_qa)} 个问题进行评估\n")

    # 加载知识库
    knowledge_bases = load_knowledge_bases()

    if not knowledge_bases:
        print("[错误] 未能加载任何知识库，请先运行 build_complete_knowledge_base.py")
        tee.close()
        return

    print(f"\n成功加载 {len(knowledge_bases)} 个知识库\n")

    input("按 Enter 键开始评估...")

    # 评估每个问题
    results = []
    for i, qa in enumerate(sampled_qa, 1):
        print(f"\n评估问题 {i}/{len(sampled_qa)}...")
        result = evaluate_single_qa(qa, knowledge_bases, search_mode="hybrid", top_k=5)
        results.append(result)
        print_evaluation_result(result, i)

    # 保存评估报告
    output_path = "../evaluation_results/qa_evaluation_report.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    save_evaluation_report(results, output_path)

    # 打印总结
    print("\n" + "="*80)
    print("评估总结")
    print("="*80 + "\n")

    successful_results = [r for r in results if r['success']]

    if successful_results:
        avg_precision = sum(r['precision'] for r in successful_results) / len(successful_results)
        avg_recall = sum(r['recall'] for r in successful_results) / len(successful_results)
        avg_f1 = sum(r['f1_score'] for r in successful_results) / len(successful_results)

        print(f"成功评估: {len(successful_results)}/{len(results)} 个问题")
        print(f"\n平均评估指标:")
        print(f"  Average Precision: {avg_precision:.2%}")
        print(f"  Average Recall: {avg_recall:.2%}")
        print(f"  Average F1 Score: {avg_f1:.2%}")

    failed_results = [r for r in results if not r['success']]
    if failed_results:
        print(f"\n失败评估: {len(failed_results)} 个问题")
        for result in failed_results:
            print(f"  ✗ {result['query'][:50]}... - {result.get('error', '未知错误')}")

    print("\n" + "="*80)
    print(f"详细报告: {output_path}")
    print(f"日志文件: {log_file_path}")
    print("="*80 + "\n")

    # 关闭日志输出
    tee.close()

if __name__ == "__main__":
    main()
