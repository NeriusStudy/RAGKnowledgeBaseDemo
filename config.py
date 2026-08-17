# 配置文件

# 依赖：后续安装的依赖请写在这里，统一用pip安装
# LangChain核心生态:
# pip install langchain langchain-core langchain-community
# Web框架依赖
# pip install fastapi uvicorn python-multipart
# Chroma数据库:
# pip install langchain-chroma
# dashscope:
# pip install dashscope
# 解析doc:
# pip install olefile
# 解析docx:
# pip install python-docx
# 解析pdf:
# pip install pypdf
# rank bm25:
# pip install rank_bm25

# 环境变量
# DASHSCOPE_API_KEY

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