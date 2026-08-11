分工：
1：文件存储类负责人：
负责人：
实现Deduplicator，FileStore，KnowledgeBase，Splitter
有一个问题是支持哪些文件格式，并以什么类型传输，比如接口中的file参数需要一个类
或许可能还需要新建一个文件实现一个文件类型转换器，将前端传入的不同的文件类型
转换为一个通用的文件类型，可能在FileStore这个类里依赖文件类型转换器

2：RAG服务负责人：
负责人：
实现RAGService，KeywordDB，KnowledgeBase，Reranker

3：前端负责人：
负责人：
实现main，以及搭建前端界面，前后端交互用fastapi框架
# 测试一下能不能写入 
