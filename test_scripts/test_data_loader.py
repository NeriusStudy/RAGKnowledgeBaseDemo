#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：医疗知识库数据加载器
功能：从 triples.json 加载医疗知识图谱数据，并转换为 LangChain Document 格式
"""

import json
import hashlib
from pathlib import Path
from typing import List
from langchain_core.documents import Document


class MedicalDataLoader:
    """医疗知识库数据加载器"""

    def __init__(self, json_path: str):
        """
        初始化数据加载器
        Args:
            json_path: triples.json 文件路径
        """
        self.json_path = Path(json_path)
        if not self.json_path.exists():
            raise FileNotFoundError(f"数据文件不存在: {json_path}")

        self.triples = []
        self.entities = {}  # 存储所有实体信息
        self.statistics = {
            'total_triples': 0,
            'diseases': set(),
            'symptoms': set(),
            'drugs': set(),
            'operations': set(),
            'relations': set()
        }

    def load_data(self):
        """加载 JSON 数据"""
        print(f"正在加载数据文件: {self.json_path}")
        with open(self.json_path, 'r', encoding='utf-8') as f:
            self.triples = json.load(f)

        print(f"✓ 成功加载 {len(self.triples)} 条三元组数据")
        self._analyze_data()

    def _analyze_data(self):
        """分析数据统计信息"""
        print("\n正在分析数据...")

        for triple in self.triples:
            # 统计三元组
            self.statistics['total_triples'] += 1

            # 统计实体
            subject_type = triple['subject_entity_type']
            object_type = triple['object_entity_type']
            relation = triple['relation_name']

            # 记录实体
            subject_id = triple['subject_entity_id']
            object_id = triple['object_entity_id']

            self.entities[subject_id] = {
                'name': triple['subject_entity_name'],
                'type': subject_type
            }
            self.entities[object_id] = {
                'name': triple['object_entity_name'],
                'type': object_type
            }

            # 按类型统计
            if subject_type == '疾病':
                self.statistics['diseases'].add(triple['subject_entity_name'])
            elif subject_type == '症状':
                self.statistics['symptoms'].add(triple['subject_entity_name'])
            elif subject_type == '药品':
                self.statistics['drugs'].add(triple['subject_entity_name'])
            elif subject_type == '手术':
                self.statistics['operations'].add(triple['subject_entity_name'])

            if object_type == '疾病':
                self.statistics['diseases'].add(triple['object_entity_name'])
            elif object_type == '症状':
                self.statistics['symptoms'].add(triple['object_entity_name'])
            elif object_type == '药品':
                self.statistics['drugs'].add(triple['object_entity_name'])
            elif object_type == '手术':
                self.statistics['operations'].add(triple['object_entity_name'])

            # 统计关系类型
            self.statistics['relations'].add(relation)

        # 打印统计信息
        print("\n" + "="*60)
        print("数据统计信息")
        print("="*60)
        print(f"三元组总数: {self.statistics['total_triples']}")
        print(f"实体总数: {len(self.entities)}")
        print(f"  - 疾病实体: {len(self.statistics['diseases'])}")
        print(f"  - 症状实体: {len(self.statistics['symptoms'])}")
        print(f"  - 药品实体: {len(self.statistics['drugs'])}")
        print(f"  - 手术实体: {len(self.statistics['operations'])}")
        print(f"关系类型数: {len(self.statistics['relations'])}")
        print(f"关系类型: {', '.join(sorted(self.statistics['relations']))}")
        print("="*60 + "\n")

    def convert_to_documents(self, format_type: str = 'triple') -> List[Document]:
        """
        将数据转换为 LangChain Document 格式

        Args:
            format_type: 转换格式类型
                - 'triple': 每条三元组转换为一个Document
                - 'entity': 每个实体及其关系转换为一个Document

        Returns:
            List[Document]: 转换后的文档列表
        """
        if format_type == 'triple':
            return self._convert_triples_to_documents()
        elif format_type == 'entity':
            return self._convert_entities_to_documents()
        else:
            raise ValueError(f"不支持的格式类型: {format_type}")

    def _convert_triples_to_documents(self) -> List[Document]:
        """将三元组转换为Document（每条三元组一个Document）"""
        print("正在转换数据为 Document 格式（三元组模式）...")

        documents = []
        for triple in self.triples:
            # 构建文档内容
            content = self._format_triple_content(triple)

            # 生成 md5
            md5_hash = hashlib.md5(content.encode('utf-8')).hexdigest()

            # 创建 Document
            doc = Document(
                page_content=content,
                metadata={
                    'md5': md5_hash,
                    'source': 'medical_triples.json',
                    'data_type': 'triple',
                    'subject_entity_id': triple['subject_entity_id'],
                    'subject_entity_name': triple['subject_entity_name'],
                    'subject_entity_type': triple['subject_entity_type'],
                    'relation_name': triple['relation_name'],
                    'object_entity_id': triple['object_entity_id'],
                    'object_entity_name': triple['object_entity_name'],
                    'object_entity_type': triple['object_entity_type']
                }
            )
            documents.append(doc)

        print(f"✓ 成功转换 {len(documents)} 个 Document\n")
        return documents

    def _format_triple_content(self, triple: dict) -> str:
        """格式化三元组内容"""
        return (
            f"{triple['subject_entity_name']}（{triple['subject_entity_type']}）"
            f" {triple['relation_name']} "
            f"{triple['object_entity_name']}（{triple['object_entity_type']}）"
        )

    def _convert_entities_to_documents(self) -> List[Document]:
        """将实体转换为Document（每个实体及其所有关系为一个Document）"""
        print("正在转换数据为 Document 格式（实体模式）...")

        # 构建实体关系索引
        entity_relations = {}
        for triple in self.triples:
            subject_id = triple['subject_entity_id']
            if subject_id not in entity_relations:
                entity_relations[subject_id] = {
                    'entity_name': triple['subject_entity_name'],
                    'entity_type': triple['subject_entity_type'],
                    'outgoing_relations': []
                }
            entity_relations[subject_id]['outgoing_relations'].append({
                'relation': triple['relation_name'],
                'target_name': triple['object_entity_name'],
                'target_type': triple['object_entity_type']
            })

        # 转换为 Document
        documents = []
        for entity_id, entity_info in entity_relations.items():
            content = self._format_entity_content(entity_info)
            md5_hash = hashlib.md5(content.encode('utf-8')).hexdigest()

            doc = Document(
                page_content=content,
                metadata={
                    'md5': md5_hash,
                    'source': 'medical_entities.json',
                    'data_type': 'entity',
                    'entity_id': entity_id,
                    'entity_name': entity_info['entity_name'],
                    'entity_type': entity_info['entity_type'],
                    'relation_count': len(entity_info['outgoing_relations'])
                }
            )
            documents.append(doc)

        print(f"✓ 成功转换 {len(documents)} 个 Document\n")
        return documents

    def _format_entity_content(self, entity_info: dict) -> str:
        """格式化实体内容"""
        content_lines = [
            f"实体名称: {entity_info['entity_name']}",
            f"实体类型: {entity_info['entity_type']}",
            f"关系数量: {len(entity_info['outgoing_relations'])}",
            "\n相关关系:"
        ]

        for rel in entity_info['outgoing_relations']:
            content_lines.append(
                f"  - {rel['relation']}: {rel['target_name']}（{rel['target_type']}）"
            )

        return "\n".join(content_lines)

    def get_statistics(self) -> dict:
        """获取统计信息"""
        return {
            'total_triples': self.statistics['total_triples'],
            'total_entities': len(self.entities),
            'disease_count': len(self.statistics['diseases']),
            'symptom_count': len(self.statistics['symptoms']),
            'drug_count': len(self.statistics['drugs']),
            'operation_count': len(self.statistics['operations']),
            'relation_types': list(self.statistics['relations'])
        }


def main():
    """主函数：测试数据加载"""

    # 数据文件路径
    data_path = "../MedicalDataset/triples.json"

    print("="*60)
    print("医疗知识库数据加载测试")
    print("="*60 + "\n")

    try:
        # 1. 创建数据加载器
        loader = MedicalDataLoader(data_path)

        # 2. 加载数据
        loader.load_data()

        # 3. 测试转换为 Document（三元组模式）
        print("\n【测试1】三元组模式转换")
        print("-"*60)
        triple_docs = loader.convert_to_documents(format_type='triple')

        # 显示前3个样例
        print("样例 Document（前3个）:")
        for i, doc in enumerate(triple_docs[:3], 1):
            print(f"\n[Document {i}]")
            print(f"Content: {doc.page_content}")
            print(f"Metadata: ")
            for key, value in doc.metadata.items():
                if key != 'md5':
                    print(f"  {key}: {value}")
            print(f"  md5: {doc.metadata['md5'][:16]}...")

        # 4. 测试转换为 Document（实体模式）
        print("\n\n【测试2】实体模式转换")
        print("-"*60)
        entity_docs = loader.convert_to_documents(format_type='entity')

        # 显示前2个样例
        print("样例 Document（前2个）:")
        for i, doc in enumerate(entity_docs[:2], 1):
            print(f"\n[Document {i}]")
            print(f"Content:\n{doc.page_content}")
            print(f"\nMetadata:")
            for key, value in doc.metadata.items():
                if key != 'md5':
                    print(f"  {key}: {value}")

        # 5. 输出统计信息
        print("\n\n【测试3】数据统计")
        print("-"*60)
        stats = loader.get_statistics()
        print(f"转换结果:")
        print(f"  - 三元组模式: {len(triple_docs)} 个 Document")
        print(f"  - 实体模式: {len(entity_docs)} 个 Document")

        print("\n" + "="*60)
        print("✓ 测试完成！数据加载和转换功能正常")
        print("="*60)

        return True

    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
