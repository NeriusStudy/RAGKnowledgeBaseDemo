"""
向量数据库（VectorDB）
基于 LangChain 的 DashScopeEmbeddings + Chroma 实现，
集成向量化、向量存储、向量检索等功能，嵌入模型在类内配置，上层不感知，
APIKEY配置在环境变量中。
文档的 MD5 由上层统一管理，默认传入的文档Document类的metadata中有md5作为存储索引，
VectorDB 不再包含内部去重逻辑。
"""
import config
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

class VectorDB:
    def __init__(self, vector_db_store_path: str, embedding_model_name: str = config.EMBEDDING_MODEL_NAME):
        """
        初始化向量数据库（VectorDB）
        Args:
            vector_db_store_path: Chroma 向量数据库持久化存储路径，由于每个知识库都单独列一个目录存储，
            所以这里的路径需要上层封装好传入否则可能会和其他知识库的路径重复，所以这里没有默认值

            embedding_model_name: （可选）嵌入模型名称，默认值为 config.EMBEDDING_MODEL_NAME
        """
        # 存储路径，上层必须传入
        self.vector_db_store_path = vector_db_store_path
        # 初始化嵌入模型，默认使用的阿里云百炼模型名称在config中定义
        self.embedding_model_name = embedding_model_name
        self.embedding_mode = DashScopeEmbeddings(
            model=self.embedding_model_name
        )
        # 初始化向量数据库，嵌入模型需要统一
        self.vector_db = Chroma(
            embedding_function=self.embedding_mode,
            persist_directory=vector_db_store_path,
        )

    def get_embedding_model_name(self) -> str:
        """
        获取当前使用的嵌入模型名称
        Returns:
            str: 当前使用的嵌入模型名称
        """
        return self.embedding_model_name

    def str_to_vector(self, text: str) -> list[float]:
        """
        将字符串转换为向量
        Args:
            text: 待转换的字符串
        Returns:
            list[float]: 转换后的向量，失败返回None
        """
        return self.embedding_mode.embed_query(text)

    def document_to_vector(self, document: Document) -> list[float]:
        """
        将文档转换为向量
        Args:
            document: 待转换的文档，文档内容在document.page_content中
        Returns:
            list[float]: 转换后的向量，失败返回None
        """
        return self.embedding_mode.embed_query(document.page_content)

    def add_document(self, document: Document) -> bool:
        """
        添加文档到向量数据库
        Args:
            document: 待添加的文档，文档内容在document.page_content中，文档存储索引在document.metadata.md5中,
            上层保证传入的文档无重复，使用Chroma存储
        Returns:
            bool: 是否添加成功
        """
        try:
            # 检查文档是否包含 md5
            if 'md5' not in document.metadata:
                print("错误：文档 metadata 中缺少 md5 字段")
                return False

            # 使用 md5 作为 Chroma 的 ID
            md5 = document.metadata['md5']

            # 添加文档到 Chroma，使用 md5 作为唯一 ID
            self.vector_db.add_documents(
                documents=[document],
                ids=[md5]
            )

            return True

        except Exception as e:
            print(f"添加文档失败: {str(e)}")
            return False

    def add_documents(self, documents: list[Document]) -> bool:
        """
        批量添加文档到向量数据库
        Args:
            documents: 待添加的文档列表，文档内容在document.page_content中，文档存储索引在document.metadata.md5中,
            上层保证传入的文档无重复，使用Chroma存储
        Returns:
            bool: 是否添加成功
        """
        try:
            if not documents:
                print("警告：文档列表为空")
                return True

            # 检查所有文档是否都包含 md5
            md5_list = []
            for doc in documents:
                if 'md5' not in doc.metadata:
                    print(f"错误：文档 metadata 中缺少 md5 字段")
                    return False
                md5_list.append(doc.metadata['md5'])

            # 批量添加文档到 Chroma
            self.vector_db.add_documents(
                documents=documents,
                ids=md5_list
            )

            return True

        except Exception as e:
            print(f"批量添加文档失败: {str(e)}")
            return False

    def delete_document(self, md5: str) -> bool:
        """
        删除文档
        Args:
            md5: 文档的md5值，用于唯一标识文档
        Returns:
            bool: 是否删除成功
        """
        try:
            # Chroma 使用 md5 作为 ID，直接通过 ID 删除
            self.vector_db.delete(ids=[md5])
            return True

        except Exception as e:
            print(f"删除文档失败 (md5={md5}): {str(e)}")
            return False

    def delete_documents(self, md5_list: list[str]) -> bool:
        """
        批量删除文档
        Args:
            md5_list: 文档的md5值列表，用于唯一标识文档
        Returns:
            bool: 是否删除成功
        """
        try:
            if not md5_list:
                print("警告：md5列表为空")
                return True

            # 批量删除文档
            self.vector_db.delete(ids=md5_list)
            return True

        except Exception as e:
            print(f"批量删除文档失败: {str(e)}")
            return False

    def search(self, query: str, k: int = config.VECTOR_SEARCH_DEFAULT_K) -> list[Document]:
        """
        搜索向量数据库
        Args:
            query: 搜索查询的字符串
            k: （可选）返回的文档数量，默认值为 config.VECTOR_SEARCH_DEFAULT_K
        Returns:
            list[Document]: 搜索到的文档列表，失败返回空列表
        """
        try:
            # 使用 Chroma 的相似度搜索
            results = self.vector_db.similarity_search(
                query=query,
                k=k
            )
            return results

        except Exception as e:
            print(f"向量检索失败: {str(e)}")
            return []

    def delete_me(self):
        """
        删除当前向量数据库，包括所有的持久化存储文件
        """
        try:
            import shutil
            import gc
            from pathlib import Path

            # 关闭 Chroma 客户端（如果有的话）
            if hasattr(self.vector_db, '_client'):
                try:
                    # 尝试关闭 Chroma 客户端
                    if hasattr(self.vector_db._client, 'clear_system_cache'):
                        self.vector_db._client.clear_system_cache()
                except:
                    pass

            # 删除数据库对象，释放文件句柄
            self.vector_db = None
            self.embedding_mode = None

            # 强制垃圾回收，释放资源
            gc.collect()

            # 短暂延迟，确保文件句柄释放
            import time
            time.sleep(1.0)  # 增加延迟时间

            # 删除 Chroma 持久化存储目录
            db_path = Path(self.vector_db_store_path)
            if db_path.exists():
                # Windows 下可能需要多次尝试
                max_retries = 3
                for i in range(max_retries):
                    try:
                        shutil.rmtree(db_path)
                        print(f"成功删除向量数据库: {self.vector_db_store_path}")
                        break
                    except (PermissionError, OSError) as e:
                        if i < max_retries - 1:
                            print(f"删除失败，1秒后重试... ({i+1}/{max_retries})")
                            time.sleep(1)
                            gc.collect()
                        else:
                            print(f"删除向量数据库失败（文件被占用）: {self.vector_db_store_path}")
                            print("提示：请手动删除该目录，或稍后删除")
                            # 不抛出异常，允许程序继续执行
            else:
                print(f"向量数据库目录不存在: {self.vector_db_store_path}")

        except Exception as e:
            print(f"删除向量数据库时出错: {str(e)}")
            print("提示：可以忽略此错误，稍后手动删除测试目录")
            # 不抛出异常，允许测试继续