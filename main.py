"""
知识库管理系统 —— 后端主入口
===========================================

负责人：李嘉洲

本模块是整个系统的后端核心，基于 FastAPI 框架实现。
主要职责：
  1. 提供 RESTful API 供前端调用（知识库和文件的增删查改）
  2. 挂载静态资源目录，直接服务前端 HTML/CSS/JS 文件
  3. 管理内存中的知识库数据
  4. 将数据持久化到本地 JSON 文件，支持重启后恢复

数据流向：
  前端 (index.html / app.js)
      ↓ HTTP 请求
  FastAPI 路由层 (本文件)
      ↓ 调用
  KnowledgeBase 后端类 (KnowledgeBase.py)
      ↓ 回退
  内存字典 / JSON 文件持久化

启动方式：
  python main.py
  然后浏览器访问 http://localhost:8000
"""

# ============================================================
# 第一部分：依赖导入
# ============================================================

import config
from KnowledgeBase import KnowledgeBase

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

import os
import shutil
import json


# ============================================================
# 第二部分：持久化存储路径配置
# ============================================================

# 知识库数据的存储目录
STORE_DIR = config.KNOWLEDGE_BASE_STORE_PATH
# 知识库数据持久化 JSON 文件的完整路径
STORE_FILE = os.path.join(STORE_DIR, config.KNOWLEDGE_BASE_STORE_FILE)


# ============================================================
# 第三部分：知识库实例化辅助函数
# ============================================================

def create_kb_instance(name):
    """
    【功能】根据知识库名称创建 KnowledgeBase 实例。
    【调用时机】创建新知识库时、服务启动加载历史数据时。
    【参数】name: 知识库名称
    【返回】KnowledgeBase 实例（若创建失败返回 None）

    各存储路径由 KnowledgeBase 内部根据 name 自动生成默认路径，
    这里统一传 None，使用其默认行为：
      - knowledgebase_store_path -> "data/{name}/"
      - file_store_path          -> "data/{name}/file_store/files/"
      - document_store_path      -> "data/{name}/file_store/documents/"
      - md5_store_path           -> "data/{name}/file_store/md5.txt"
      - file_document_map_store_path -> "data/{name}/file_store/file_document_map.txt"
      - RAG_store_path           -> "data/{name}/RAG_store"
    """
    try:
        instance = KnowledgeBase(
            name=name,
            knowledgebase_store_path="",  # 使用默认路径
            file_store_path="",  # 使用默认路径
            document_store_path="",  # 使用默认路径
            md5_store_path="",  # 使用默认路径
            file_document_map_store_path="",  # 使用默认路径
            RAG_store_path="",  # 使用默认路径
        )
        return instance
    except Exception:
        return None


# ============================================================
# 第四部分：持久化工具函数
# ============================================================

def load_data():
    """
    【功能】从本地 JSON 文件加载历史知识库数据到内存，并实例化所有知识库对象。
    【调用时机】服务启动时（模块加载阶段）自动调用一次。
    【执行流程】
        1. 检查 JSON 文件是否存在
        2. 读取文件内容并解析为 Python 字典
        3. 恢复知识库的创建顺序（kb_order）
        4. 遍历每个知识库，调用 create_kb_instance() 实例化对象
        5. 若实例化成功，instance 字段保存 KnowledgeBase 对象
        6. 若实例化失败，instance 字段为 None（后续 API 会走回退逻辑）
        7. 如果文件不存在或解析失败，则初始化为空数据
    """
    global knowledge_bases, kb_order

    if os.path.exists(STORE_FILE):
        try:
            with open(STORE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            kb_order = data.get("kb_order", [])
            kb_data = data.get("knowledge_bases", {})

            knowledge_bases = {}
            for name in kb_order:
                if name in kb_data:
                    # 尝试实例化 KnowledgeBase 对象
                    instance = create_kb_instance(name)
                    knowledge_bases[name] = {
                        "instance": instance,   # 实例化成功则为 KnowledgeBase 对象，失败则为 None
                        "files": kb_data[name].get("files", []),
                    }
        except Exception:
            knowledge_bases = {}
            kb_order = []
    else:
        knowledge_bases = {}
        kb_order = []


def save_data():
    """
    【功能】将内存中的知识库数据持久化保存到 JSON 文件。
    【调用时机】每次增删操作（创建/删除知识库、上传/删除文件）后调用。
    【执行流程】
        1. 确保存储目录存在（不存在则自动创建）
        2. 将内存数据整理为可序列化的结构（不保存 instance 对象）
        3. 写入 JSON 文件（UTF-8 编码、保留中文、缩进 2 格便于阅读）
    """
    os.makedirs(STORE_DIR, exist_ok=True)

    data = {
        "kb_order": kb_order,
        "knowledge_bases": {},
    }

    for name in kb_order:
        if name in knowledge_bases:
            data["knowledge_bases"][name] = {
                "files": knowledge_bases[name]["files"],
            }

    with open(STORE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ============================================================
# 第五部分：应用初始化
# ============================================================

app = FastAPI()

# 内存中存储所有知识库的数据
# knowledge_bases: 字典，键为知识库名称，值为字典
#   值字典包含：
#     - "instance": KnowledgeBase 实例（由 create_kb_instance() 创建，可能为 None 表示实例化失败）
#     - "files":    文件名字符串列表
knowledge_bases = {}

# kb_order: 列表，记录知识库的创建顺序
kb_order = []

# 启动时立即从 JSON 文件加载历史数据并实例化所有知识库对象
load_data()


# ============================================================
# 第六部分：请求体数据模型
# ============================================================

class KBCreateRequest(BaseModel):
    """
    创建知识库的请求体模型。

    请求示例：
        { "name": "我的第一个知识库" }
    """
    name: str


# ============================================================
# 第七部分：静态资源挂载
# ============================================================

app.mount("/static", StaticFiles(directory="static"), name="static")


# ============================================================
# 第八部分：路由定义
# ============================================================

# ---------- 8.1 首页 ----------
@app.get("/")
async def read_index():
    """【GET /】返回前端首页 HTML 文件。"""
    return FileResponse("static/index.html")


# ---------- 8.2 获取知识库列表 ----------
@app.get("/api/knowledgebases")
async def list_knowledge_bases():
    """【GET /api/knowledgebases】获取所有知识库列表，按创建顺序返回。"""
    result = []
    for name in kb_order:
        if name in knowledge_bases:
            result.append({"name": name})
    return {"knowledge_bases": result}


# ---------- 8.3 创建知识库 ----------
@app.post("/api/knowledgebases")
async def create_knowledge_base(request: KBCreateRequest):
    """
    【POST /api/knowledgebases】创建新的知识库。

    执行流程：
        1. 接收前端提交的知识库名称
        2. 校验名称合法性（非空、不重复）
        3. 调用 create_kb_instance() 实例化 KnowledgeBase 对象
        4. 将知识库信息存入内存
        5. 调用 save_data() 持久化到 JSON 文件
        6. 返回成功响应
    """
    name = request.name.strip()

    if not name:
        raise HTTPException(status_code=400, detail="知识库名称不能为空")

    if name in knowledge_bases:
        raise HTTPException(status_code=400, detail="知识库已存在")

    # 使用辅助函数实例化 KnowledgeBase 对象
    kb = create_kb_instance(name)

    knowledge_bases[name] = {"instance": kb, "files": []}
    kb_order.append(name)

    save_data()

    return {"success": True, "name": name}


# ---------- 8.4 删除知识库 ----------
@app.delete("/api/knowledgebases/{name}")
async def delete_knowledge_base(name: str):
    """
    【DELETE /api/knowledgebases/{name}】删除指定知识库。

    执行流程：
        1. 检查知识库是否存在
        2. 调用后端 delete_me() 方法（若实例存在）
        3. 删除本地数据目录
        4. 从内存中移除
        5. 更新持久化文件
    """
    if name not in knowledge_bases:
        raise HTTPException(status_code=404, detail="知识库不存在")

    kb_data = knowledge_bases[name]

    if kb_data["instance"]:
        try:
            kb_data["instance"].delete_me()
        except Exception:
            pass

    kb_path = f"data/{name}"
    if os.path.exists(kb_path):
        try:
            shutil.rmtree(kb_path)
        except Exception:
            pass

    del knowledge_bases[name]
    kb_order.remove(name)

    save_data()

    return {"success": True}


# ---------- 8.5 获取文件列表 ----------
@app.get("/api/knowledgebases/{name}/files")
async def list_files(name: str):
    """
    【GET /api/knowledgebases/{name}/files】获取指定知识库的文件列表。
    优先从后端实例获取，若实例为 None 则使用内存中记录的文件列表。
    """
    if name not in knowledge_bases:
        raise HTTPException(status_code=404, detail="知识库不存在")

    kb_data = knowledge_bases[name]
    files = []

    if kb_data["instance"]:
        try:
            file_names = kb_data["instance"].get_all_files()
            if file_names:
                files = [{"name": f} for f in file_names]
        except Exception:
            pass

    if not files:
        files = [{"name": f} for f in kb_data["files"]]

    return {"files": files}


# ---------- 8.6 上传文件 ----------
@app.post("/api/knowledgebases/{name}/files")
async def upload_file(name: str, file: UploadFile = File(...)):
    """
    【POST /api/knowledgebases/{name}/files】向指定知识库上传文件。
    优先调用后端 add_file() 方法，若实例为 None 则仅在内存中记录文件名。
    """
    if name not in knowledge_bases:
        raise HTTPException(status_code=404, detail="知识库不存在")

    kb_data = knowledge_bases[name]
    success = False

    if kb_data["instance"]:
        try:
            success = kb_data["instance"].add_file(file)
        except Exception:
            pass

    if not success:
        file_name = file.filename
        if file_name and file_name not in kb_data["files"]:
            kb_data["files"].append(file_name)
        success = True

    save_data()

    return {"success": success}


# ---------- 8.7 删除文件 ----------
@app.delete("/api/knowledgebases/{name}/files/{filename}")
async def delete_file(name: str, filename: str):
    """
    【DELETE /api/knowledgebases/{name}/files/{filename}】删除指定文件。
    优先调用后端 delete_file() 方法，若实例为 None 则从内存记录中移除。
    """
    if name not in knowledge_bases:
        raise HTTPException(status_code=404, detail="知识库不存在")

    kb_data = knowledge_bases[name]
    success = False

    if kb_data["instance"]:
        try:
            success = kb_data["instance"].delete_file(filename)
        except Exception:
            pass

    if not success:
        if filename in kb_data["files"]:
            kb_data["files"].remove(filename)
            success = True

    save_data()

    return {"success": success}


# ============================================================
# 第九部分：服务启动入口
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
