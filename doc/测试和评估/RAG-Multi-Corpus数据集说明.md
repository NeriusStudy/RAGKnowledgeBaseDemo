# RAG-Multi-Corpus 测试数据集说明

**数据集名称**：RAG-Multi-Corpus  
**数据集版本**：v1.0  
**文档创建日期**：2026-08-15

---

## 一、数据集概述

### 1.1 数据集简介

RAG-Multi-Corpus 是一个多领域企业知识库测试数据集，专为 RAG（检索增强生成）系统的开发和评估而设计。数据集模拟了6个不同行业的企业知识库，包含真实业务场景的文档和问答对。

**数据集特点**：
- ✅ 多领域覆盖（汽车、教育、航空、科技、金融）
- ✅ 多文件格式（TXT, MD, JSON, CSV）
- ✅ 真实业务场景（产品文档、政策手册、FAQ）
- ✅ 标准化QA评估集（1302个问答对）
- ✅ 支持多种查询类型（Single-hop, Multi-hop, Temporal, Comparison）

### 1.2 数据集来源

**项目路径**：`RAGKnowledgeBaseDemo-main/RAG-Multi-Corpus/`

**数据集结构**：
```
RAG-Multi-Corpus/
├── datasets/                      # 企业知识库原始数据
│   ├── Aventro Motors/           # 汽车制造企业
│   ├── Cendara University/       # 大学学术机构
│   ├── CloudWay-24/              # 航空旅游企业
│   ├── TechEdu Academy/          # 在线教育平台
│   ├── Velvera Technologies/     # 科技公司
│   └── ZX Bank/                  # 银行金融机构
├── qa_datasets/                   # QA 测试数据集
│   ├── merged_all_qa_dataset.csv # 完整QA数据集（1302条）
│   └── individual_qa_files/      # 各企业独立QA文件
└── README.md                      # 数据集说明文档
```

---

## 二、企业知识库详情

### 2.1 Aventro Motors（汽车制造）

**企业背景**：虚拟汽车制造企业，生产多款轿车和SUV车型

**知识库内容**：
- 产品规格文档（车型参数、配置、价格）
- 售后服务政策（保修、维修、召回）
- 经销商信息（门店位置、联系方式）
- 车主手册（使用指南、维护保养）

**文件统计**：
- 文件数：51 个
- 文件格式：TXT (35), MD (12), CSV (3), JSON (1)
- 主要文档：
  - `Aventro Motors.csv` - 车型完整数据表
  - `Sedan Models.md` - 轿车系列介绍
  - `SUV Models.md` - SUV系列介绍
  - `Warranty Policy.txt` - 保修政策

**典型问题**：
- "What are the features of Aventro sedan models?"
- "What is the warranty period for Aventro vehicles?"
- "Where can I find Aventro service centers in Mumbai?"

---

### 2.2 Cendara University（学术教育）

**企业背景**：虚拟大学机构，提供本科和研究生教育

**知识库内容**：
- 招生信息（入学要求、申请流程、奖学金）
- 课程目录（专业介绍、课程列表、学分要求）
- 学术政策（考试规则、成绩评定、学术诚信）
- 校园服务（图书馆、宿舍、体育设施）

**文件统计**：
- 文件数：40 个
- 文件格式：MD (28), TXT (10), JSON (2)
- 主要文档：
  - `Admission Requirements.md` - 招生要求
  - `Undergraduate Programs.md` - 本科项目
  - `Graduate Programs.md` - 研究生项目
  - `Scholarship Information.md` - 奖学金信息

**典型问题**：
- "What are the admission requirements for undergraduate programs?"
- "Which scholarships are available for international students?"
- "What is the credit requirement for a Bachelor's degree?"

---

### 2.3 CloudWay-24（航空旅游）

**企业背景**：虚拟航空公司，提供国内和国际航班服务

**知识库内容**：
- 航班信息（航线、时刻表、机型）
- 票务政策（预订、退改签、行李）
- 乘客服务（餐食、座位、特殊需求）
- 会员计划（里程累积、等级权益）

**文件统计**：
- 文件数：37 个
- 文件格式：MD (25), TXT (8), JSON (3), CSV (1)
- 主要文档：
  - `Mumbai Inbound & Outbound Flights.md` - 孟买航班
  - `Upgrade Policies.md` - 升舱政策
  - `Travelling with Pets.md` - 宠物托运
  - `Boeing 787 Dreamliner.md` - 机型介绍

**典型问题**：
- "What is the process for upgrading to premium economy?"
- "What are the baggage allowance rules for international flights?"
- "Can I travel with my pet on CloudWay-24 flights?"

---

### 2.4 TechEdu Academy（在线教育）

**企业背景**：虚拟在线教育平台，提供编程和技术课程

**知识库内容**：
- 课程大纲（Python、Java、Web开发、数据科学）
- 学习路径（初级到高级的学习规划）
- 项目案例（实战项目、作业要求）
- 技术文档（编程语言手册、工具使用）

**文件统计**：
- 文件数：10 个
- 文件格式：TXT (7), MD (2), JSON (1)
- 主要文档：
  - `Python_Course_Outline.txt` - Python课程大纲
  - `Java_Programming_Guide.txt` - Java编程指南
  - `Web_Development_Path.md` - Web开发路径
  - `Data_Science_Curriculum.txt` - 数据科学课程

**典型问题**：
- "What topics are covered in the Python programming course?"
- "What is the recommended learning path for web development?"
- "Are there any prerequisites for the Data Science course?"

---

### 2.5 Velvera Technologies（企业科技）

**企业背景**：虚拟科技公司，提供企业软件解决方案

**知识库内容**：
- 产品文档（功能介绍、技术规格、API文档）
- 用户手册（安装指南、配置说明、故障排除）
- 技术支持（FAQ、问题诊断、联系方式）
- 企业信息（公司简介、团队介绍、职位招聘）

**文件统计**：
- 文件数：38 个
- 文件格式：MD (20), TXT (12), JSON (4), CSV (2)
- 主要文档：
  - `Product Overview.md` - 产品概览
  - `Installation Guide.txt` - 安装指南
  - `API Documentation.md` - API文档
  - `Careers at Velvera.md` - 招聘信息

**典型问题**：
- "How do I install Velvera's enterprise software?"
- "What are the system requirements for the product?"
- "How can I contact technical support?"

---

### 2.6 ZX Bank（银行金融）

**企业背景**：虚拟银行机构，提供个人和企业金融服务

**知识库内容**：
- 账户服务（储蓄账户、信用卡、贷款）
- 网点信息（分行地址、ATM位置、营业时间）
- 金融产品（理财、保险、投资）
- 服务政策（费用标准、利率、条款）

**文件统计**：
- 文件数：73 个
- 文件格式：MD (45), TXT (20), JSON (5), CSV (3)
- 主要文档：
  - `ZX Bank ATM Network at Major Parks – India.md` - ATM网点（公园）
  - `ZX Bank ATMs at Major Bus Stands (India).md` - ATM网点（公交站）
  - `Savings Account.md` - 储蓄账户
  - `Credit Card Policies.md` - 信用卡政策

**典型问题**：
- "When were the ATMs installed in major parks of Surat?"
- "What are the interest rates for savings accounts?"
- "Where can I find ZX Bank branches in Delhi?"

---

## 三、QA测试数据集

### 3.1 数据集概览

**文件位置**：`qa_datasets/merged_all_qa_dataset.csv`

**数据规模**：
- 总问答对：1302 条
- 覆盖企业：6 个
- 查询类型：5 种
- 平均每企业：217 个问答对

### 3.2 数据格式

**CSV 字段说明**：
```csv
Query,Enterprise,Supporting Facts,Query Type
```

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| Query | String | 用户查询问题 | "What are the features of sedan models?" |
| Enterprise | String | 所属企业 | "Aventro Motors" |
| Supporting Facts | String | 包含答案的文档文件名（可能多个，用分号分隔） | "Aventro Motors Sedan.md; Vehicle Specs.txt" |
| Query Type | String | 查询类型 | "Single-hop" |

**示例记录**：
```csv
"What are the admission requirements for undergraduate programs?","Cendara University","Admission Requirements.md; Undergraduate Programs.md","Single-hop"
"Compare the baggage allowance between economy and business class","CloudWay-24","Economy Class.md; Business Class.md","Comparison"
```

### 3.3 查询类型分布

| 查询类型 | 数量 | 占比 | 说明 |
|---------|------|------|------|
| **Single-hop** | 520 | 40% | 单步查询，答案在单个文档中 |
| **Multi-hop** | 312 | 24% | 多步查询，需要综合多个文档 |
| **Temporal** | 195 | 15% | 时间相关查询（when, since, until） |
| **Comparison** | 156 | 12% | 对比查询（compare, difference, vs） |
| **Procedural** | 119 | 9% | 流程查询（how to, steps, process） |
| **总计** | 1302 | 100% | - |

### 3.4 查询类型详解

#### Single-hop（单步查询）
**特点**：答案直接存在于单个文档中，无需跨文档推理

**示例**：
```
Query: "What is the warranty period for Aventro vehicles?"
Supporting Facts: "Warranty Policy.txt"
Answer: 在 Warranty Policy.txt 中直接查找保修期限
```

**难度**：⭐⭐☆☆☆

---

#### Multi-hop（多步查询）
**特点**：需要从多个文档中提取信息并综合

**示例**：
```
Query: "What documents are required for international students applying for scholarships?"
Supporting Facts: "Admission Requirements.md; Scholarship Information.md"
Answer: 需要先从 Admission Requirements 了解国际学生申请要求，
       再从 Scholarship Information 了解奖学金所需文档
```

**难度**：⭐⭐⭐⭐☆

---

#### Temporal（时间查询）
**特点**：涉及时间信息的查询

**示例**：
```
Query: "When were the ATMs installed in major parks of Surat?"
Supporting Facts: "ZX Bank ATM Network at Major Parks – India.md"
Answer: 查找文档中关于Surat公园ATM的安装时间
```

**难度**：⭐⭐⭐☆☆

---

#### Comparison（对比查询）
**特点**：需要对比两个或多个实体的属性

**示例**：
```
Query: "Compare the features of sedan and SUV models"
Supporting Facts: "Sedan Models.md; SUV Models.md"
Answer: 需要分别提取两种车型的特性，然后进行对比
```

**难度**：⭐⭐⭐⭐☆

---

#### Procedural（流程查询）
**特点**：询问操作步骤或流程

**示例**：
```
Query: "What is the process for upgrading to premium economy?"
Supporting Facts: "Upgrade Policies.md"
Answer: 查找升舱的操作步骤和流程
```

**难度**：⭐⭐⭐☆☆

---

## 四、数据集使用方法

### 4.1 构建知识库

**脚本**：`build_complete_knowledge_base.py`

```bash
# 运行构建脚本
python build_complete_knowledge_base.py
```

**构建结果**：
- 生成6个企业知识库到 `data/knowledge/` 目录
- 生成元数据索引 `data/knowledge/knowledge_bases.json`
- 总计：242 文件，3116 文档

### 4.2 运行QA评估

**脚本**：`evaluate_qa_performance.py`

```bash
# 运行评估脚本
python evaluate_qa_performance.py
```

**评估流程**：
1. 从 1302 个问答对中随机抽取 20 个
2. 使用混合检索（hybrid mode）检索 Top-5
3. 对比检索结果与 Supporting Facts
4. 计算 Precision、Recall、F1 Score
5. 生成详细评估报告

**输出结果**：
- 终端输出：实时评估进度和结果
- 日志文件：`logs/qa_test/{timestamp}.log`
- 评估报告：`evaluation_results/qa_evaluation_report.json`

### 4.3 自定义评估

**修改抽样数量**：
```python
# 在 evaluate_qa_performance.py 中修改
SAMPLE_SIZE = 20  # 改为50或100
```

**修改检索配置**：
```python
results = kb.search(
    query=query,
    mode="hybrid",  # 可改为 "vector" 或 "keyword"
    k=5,            # 可改为 3 或 10
    vector_weight=0.7,
    keyword_weight=0.3
)
```

**筛选特定查询类型**：
```python
# 只评估 Single-hop 查询
filtered_df = qa_df[qa_df['Query Type'] == 'Single-hop']
sampled_qa = filtered_df.sample(n=20)
```

---

## 五、数据集统计分析

### 5.1 总体统计

**文件统计**：
```
总文件数：248
├── TXT: 92 (37%)
├── MD: 132 (53%)
├── JSON: 16 (7%)
└── CSV: 8 (3%)

成功导入：242 (97.6%)
导入失败：6 (2.4%)
```

**文档统计**（切分后）：
```
总文档块：3116
平均每文件：12.9 个文档块
最小：1 个文档块（短文件）
最大：63 个文档块（长文档）
```

### 5.2 按企业统计

| 企业 | 文件数 | 文档块数 | 平均文档/文件 | QA数量 |
|------|--------|----------|--------------|--------|
| Aventro Motors | 49 | 461 | 9.4 | 218 |
| Cendara University | 40 | 857 | 21.4 | 215 |
| CloudWay-24 | 35 | 272 | 7.8 | 220 |
| TechEdu Academy | 10 | 174 | 17.4 | 210 |
| Velvera Technologies | 37 | 557 | 15.1 | 223 |
| ZX Bank | 71 | 795 | 11.2 | 216 |

**分析**：
- Cendara University 文档最多（学术文档通常较长）
- TechEdu Academy 文件最少（但文档密度高）
- 各企业QA数量均衡（~215个/企业）

### 5.3 文档长度分布

| 文档块长度（字符） | 数量 | 占比 |
|------------------|------|------|
| < 200 | 312 | 10% |
| 200 - 400 | 935 | 30% |
| 400 - 600 | 1246 | 40% |
| 600 - 800 | 468 | 15% |
| > 800 | 155 | 5% |

**平均长度**：约 480 字符/文档块

---

## 六、数据集质量

### 6.1 优势

✅ **多样性**：
- 6个不同行业领域
- 4种文件格式
- 5种查询类型

✅ **真实性**：
- 模拟真实企业知识库结构
- 包含完整业务流程文档
- 问答对来自实际业务场景

✅ **标准化**：
- 统一的CSV格式
- 清晰的 Supporting Facts 标注
- 完整的元数据信息

✅ **规模适中**：
- 1302个问答对，适合快速评估
- 242个文件，适合本地测试
- 3116个文档块，覆盖多种长度

### 6.2 局限性

⚠️ **语言单一**：
- 仅包含英文文档
- 缺少中文或其他语言

⚠️ **领域覆盖有限**：
- 仅6个行业
- 缺少医疗、法律、制造等领域

⚠️ **文档重复问题**：
- 部分CSV文件包含重复行
- 导致6个文件添加失败（2.4%）

⚠️ **QA答案未提供**：
- 只提供 Supporting Facts（文档名）
- 未提供具体的答案文本

---

## 七、使用建议

### 7.1 适用场景

**✅ 推荐用于**：
1. RAG系统原型开发
2. 检索算法对比测试
3. 多领域知识库管理
4. 教学和研究项目

**⚠️ 不推荐用于**：
1. 生产环境部署（数据规模小）
2. 领域专用系统（缺少深度）
3. 多语言RAG测试（仅英文）

### 7.2 扩展建议

**添加更多领域**：
- 医疗健康（医学文献、诊疗指南）
- 法律法规（法律文书、条款解释）
- 制造业（工艺流程、质量标准）

**添加多语言支持**：
- 中文企业知识库
- 多语言问答对
- 跨语言检索评估

**提供标准答案**：
- 为每个问答对提供参考答案
- 支持生成质量评估（ROUGE、BLEU）
- 引入人工评分标准

---

## 八、数据集维护

### 8.1 版本历史

**v1.0（当前版本）**：
- 初始发布
- 6个企业，248个文件
- 1302个问答对

### 8.2 已知问题

1. **CSV文件重复数据**：
   - 影响文件：`Aventro Motors.csv` 等6个
   - 计划：下个版本清洗数据

2. **部分QA标注不完整**：
   - 少数 Supporting Facts 缺失
   - 计划：人工补充标注

### 8.3 更新计划

**短期（1-2月）**：
- 清洗重复数据
- 补充缺失标注
- 添加中文知识库

**长期（3-6月）**：
- 扩展到10+领域
- 增加到5000+问答对
- 提供标准答案和评分

---

## 九、引用和致谢

### 9.1 数据来源

本数据集为项目内部构建的测试数据，文档内容为虚拟企业知识库，不涉及真实企业信息。

### 9.2 使用许可

本数据集仅供学习和研究使用，不得用于商业用途。

---

**文档版本**：v1.0  
**最后更新**：2026-08-15
