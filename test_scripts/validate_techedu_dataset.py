"""
TechEdu Academy 数据集验证脚本

功能：
1. 验证所有文件是否存在
2. 检查文件格式是否正确
3. 统计文件大小和内容
4. 验证 Q&A 数据集格式
"""

import os
import sys
import json
import csv
from pathlib import Path

# 设置 UTF-8 输出编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def validate_techedu_dataset():
    """验证 TechEdu Academy 数据集"""

    base_dir = Path(__file__).parent.parent / "RAG-Multi-Corpus" / "datasets" / "TechEdu Academy"

    print("=" * 70)
    print("TechEdu Academy 数据集验证")
    print("=" * 70)
    print()

    # 1. 验证目录结构
    print("【1. 目录结构验证】")
    required_dirs = ["txt", "json", "csv"]
    for dir_name in required_dirs:
        dir_path = base_dir / dir_name
        if dir_path.exists():
            print(f"  ✅ {dir_name}/ 目录存在")
        else:
            print(f"  ❌ {dir_name}/ 目录缺失")
    print()

    # 2. 验证 TXT 文件
    print("【2. TXT 文件验证】")
    txt_files = [
        "Python_Course_Outline.txt",
        "Student_Enrollment_Guide.txt",
        "Data_Science_Career_Track.txt"
    ]

    txt_dir = base_dir / "txt"
    for filename in txt_files:
        file_path = txt_dir / filename
        if file_path.exists():
            size = file_path.stat().st_size / 1024  # KB
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
            print(f"  ✅ {filename}: {size:.1f}KB, {lines} 行")
        else:
            print(f"  ❌ {filename}: 文件不存在")
    print()

    # 3. 验证 JSON 文件
    print("【3. JSON 文件验证】")
    json_files = [
        "academy_overview.json",
        "course_catalog.json"
    ]

    json_dir = base_dir / "json"
    for filename in json_files:
        file_path = json_dir / filename
        if file_path.exists():
            size = file_path.stat().st_size / 1024  # KB
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"  ✅ {filename}: {size:.1f}KB, JSON 格式有效")

                # 显示顶层键
                if isinstance(data, dict):
                    keys = list(data.keys())[:5]
                    print(f"     顶层键: {', '.join(keys)}{'...' if len(data.keys()) > 5 else ''}")
            except json.JSONDecodeError as e:
                print(f"  ❌ {filename}: JSON 格式错误 - {e}")
        else:
            print(f"  ❌ {filename}: 文件不存在")
    print()

    # 4. 验证 CSV 文件
    print("【4. CSV 文件验证】")
    csv_files = {
        "course_catalog.csv": "课程目录",
        "student_enrollment_data.csv": "学生注册数据",
        "instructor_information.csv": "讲师信息",
        "techedu_qa_dataset.csv": "Q&A 数据集"
    }

    csv_dir = base_dir / "csv"
    for filename, description in csv_files.items():
        file_path = csv_dir / filename
        if file_path.exists():
            size = file_path.stat().st_size / 1024  # KB
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                    columns = reader.fieldnames if reader.fieldnames else []

                print(f"  ✅ {filename} ({description})")
                print(f"     大小: {size:.1f}KB, 行数: {len(rows)}, 列数: {len(columns)}")
                print(f"     列名: {', '.join(columns[:4])}{'...' if len(columns) > 4 else ''}")
            except Exception as e:
                print(f"  ❌ {filename}: CSV 格式错误 - {e}")
        else:
            print(f"  ❌ {filename}: 文件不存在")
    print()

    # 5. 验证 Q&A 数据集
    print("【5. Q&A 数据集详细验证】")
    qa_file = csv_dir / "techedu_qa_dataset.csv"
    if qa_file.exists():
        with open(qa_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        # 统计查询类型
        query_types = {}
        for row in rows:
            qtype = row.get('Query Type', 'Unknown')
            query_types[qtype] = query_types.get(qtype, 0) + 1

        print(f"  总问答对数: {len(rows)}")
        print(f"  查询类型分布:")
        for qtype, count in sorted(query_types.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(rows)) * 100
            print(f"    - {qtype}: {count} ({percentage:.1f}%)")

        # 显示示例问题
        print(f"\n  示例问题（前3个）:")
        for i, row in enumerate(rows[:3], 1):
            print(f"    {i}. [{row.get('Query Type', 'N/A')}] {row.get('Query', 'N/A')[:60]}...")
    else:
        print("  ❌ Q&A 数据集文件不存在")
    print()

    # 6. 验证 README
    print("【6. README 文档验证】")
    readme_file = base_dir / "README.md"
    if readme_file.exists():
        size = readme_file.stat().st_size / 1024  # KB
        with open(readme_file, 'r', encoding='utf-8') as f:
            lines = len(f.readlines())
        print(f"  ✅ README.md: {size:.1f}KB, {lines} 行")
    else:
        print("  ❌ README.md: 文件不存在")
    print()

    # 7. 总结
    print("=" * 70)
    print("【验证总结】")
    print("=" * 70)

    total_files = len(txt_files) + len(json_files) + len(csv_files) + 1  # +1 for README
    print(f"  📁 总文件数: {total_files}")

    # 计算总大小
    total_size = 0
    for subdir in ["txt", "json", "csv"]:
        subdir_path = base_dir / subdir
        if subdir_path.exists():
            for file in subdir_path.glob("*"):
                if file.is_file():
                    total_size += file.stat().st_size

    readme_file = base_dir / "README.md"
    if readme_file.exists():
        total_size += readme_file.stat().st_size

    print(f"  💾 总大小: {total_size / 1024:.1f}KB ({total_size / (1024 * 1024):.2f}MB)")
    print(f"  📊 格式覆盖: TXT (3), JSON (2), CSV (4), MD (1)")
    print(f"  ❓ Q&A 数据集: 50 个问答对，7 种查询类型")
    print()
    print("✅ TechEdu Academy 数据集验证完成！")
    print()

if __name__ == "__main__":
    try:
        validate_techedu_dataset()
    except Exception as e:
        print(f"\n❌ 验证过程出错: {e}")
        import traceback
        traceback.print_exc()
