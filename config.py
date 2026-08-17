# 配置文件

# ============================================================
# 依赖清单（统一使用 pip install -r requirements.txt 安装）
# ============================================================
#
# 【LangChain 核心生态】
#   langchain>=1.3
#   langchain-core>=0.3
#   langchain-community>=0.3
#   langchain-text-splitters>=1.1
#
# 【Web 框架】
#   fastapi>=0.115
#   uvicorn>=0.34
#   python-multipart>=0.0.9   (FastAPI 文件上传必需)
#   pydantic>=2.0
#
# 【向量数据库】
#   langchain-chroma>=0.1
#   chromadb>=0.5
#
# 【关键词检索】
#   rank-bm25>=0.2
#   jieba>=0.42              (中文分词)
#
# 【阿里云 DashScope】
#   dashscope>=1.20           (Embedding + Rerank)
#
# 【文档解析】
#   olefile>=0.47             (.doc 旧版 Word)
#   python-docx>=1.1          (.docx 新版 Word)
#   pypdf>=5.0                (.pdf)
#
# 【数据处理】
#   numpy>=1.24
#   pandas>=2.0
#   python-dotenv>=1.0        (.env 环境变量加载)
#
# 【测试工具】（可选）
#   pytest>=8.0
#
# ============================================================

# 环境变量（必需）
# DASHSCOPE_API_KEY          (阿里云百炼 API Key)
# 可选:
#   DASHSCOPE_WORKSPACE_ID   (阿里云百炼工作空间 ID)

# VectorDB
EMBEDDING_MODEL_NAME = "text-embedding-v2"
VECTOR_SEARCH_DEFAULT_K = 10

# KeywordDB
KEYWORD_SEARCH_DEFAULT_K = 10

# Reranker
RERANK_MODEL_NAME = "qwen3-rerank"
RRF_REFUSION_K = 20
RERANK_K = 10

# RAGService
HYBRID_SEARCH_DEFAULT_K = 10
RAG_SEARCH_DEFAULT_K = 10
# 存储路径
VECTOR_DB_PATH = "vector_db"
KEYWORD_DB_PATH = "keyword_db"

# Splitter
SPLITTER_CHUNK_SIZE = 500
SPLITTER_CHUNK_OVERLAP = 50
SPLITTER_SEPARATERS = ["\n\n", "\n", "。", "！", "？", "；", "，", "、", " ", "", ".", ",", "!", "?"]
SPLITTER_LENGTH_FUNCTION = len

# KnowledgeBase
# 存储路径
FILE_STORE_PATH = "file_store/files/"
DOCUMENT_STORE_PATH = "file_store/documents/"
MD5_STORE_PATH = "file_store/md5.txt"
FILE_DOCUMENT_MAP_STORE_PATH = "file_store/file_document_map.txt"
RAG_STORE_PATH = "RAG_store"

# main
KNOWLEDGE_BASE_STORE_PATH = "data/knowledge"
KNOWLEDGE_BASE_STORE_FILE = "knowledge_bases.json"