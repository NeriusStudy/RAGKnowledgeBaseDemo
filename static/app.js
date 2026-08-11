const state = {
    currentKB: null,
};

const $ = (id) => document.getElementById(id);

function showToast(message, type = "") {
    const toast = $("toast");
    toast.textContent = message;
    toast.className = "toast " + type;
    toast.classList.remove("hidden");
    setTimeout(() => {
        toast.classList.add("hidden");
    }, 2000);
}

function showView(viewId) {
    document.querySelectorAll(".view").forEach((v) => v.classList.remove("active"));
    $(viewId).classList.add("active");
}

async function api(method, path, body = null) {
    const opts = {
        method,
        headers: {},
    };
    if (body !== null) {
        if (body instanceof FormData) {
            opts.body = body;
        } else {
            opts.headers["Content-Type"] = "application/json";
            opts.body = JSON.stringify(body);
        }
    }
    const res = await fetch(path, opts);
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
        throw new Error(data.detail || "请求失败");
    }
    return data;
}

// ============ 知识库列表 ============

async function loadKnowledgeBases() {
    try {
        const data = await api("GET", "/api/knowledgebases");
        const list = data.knowledge_bases || [];
        renderKBList(list);
    } catch (err) {
        showToast(err.message || "加载知识库失败", "error");
        renderKBList([]);
    }
}

function renderKBList(list) {
    const container = $("kb-list");
    const empty = $("kb-empty");

    if (list.length === 0) {
        container.innerHTML = "";
        empty.classList.remove("hidden");
        return;
    }

    empty.classList.add("hidden");
    container.innerHTML = list
        .map(
            (kb) => `
        <div class="kb-card" data-name="${escapeHtml(kb.name)}">
            <div class="kb-card-header">
                <div class="kb-card-icon">&#128218;</div>
                <button class="kb-card-delete" data-action="delete-kb" data-name="${escapeHtml(kb.name)}" title="删除">
                    &#128465;
                </button>
            </div>
            <div class="kb-card-name">${escapeHtml(kb.name)}</div>
            <div class="kb-card-desc">点击进入管理</div>
        </div>
    `
        )
        .join("");

    container.querySelectorAll(".kb-card").forEach((card) => {
        card.addEventListener("click", (e) => {
            if (e.target.closest("[data-action='delete-kb']")) return;
            const name = card.dataset.name;
            enterKnowledgeBase(name);
        });
    });

    container.querySelectorAll("[data-action='delete-kb']").forEach((btn) => {
        btn.addEventListener("click", (e) => {
            e.stopPropagation();
            const name = btn.dataset.name;
            confirmDeleteKB(name);
        });
    });
}

function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}

// ============ 知识库列表 ============

$("btn-add-kb").addEventListener("click", () => {
    $("kb-name-input").value = "";
    $("kb-modal").classList.remove("hidden");
    setTimeout(() => $("kb-name-input").focus(), 50);
});

$("kb-modal-cancel").addEventListener("click", () => {
    $("kb-modal").classList.add("hidden");
});

$("kb-modal-confirm").addEventListener("click", async () => {
    const input = $("kb-name-input");
    const name = input.value.trim();
    if (!name) {
        showToast("请输入知识库名称", "error");
        return;
    }
    try {
        await api("POST", "/api/knowledgebases", { name });
        $("kb-modal").classList.add("hidden");
        showToast("创建成功", "success");
        loadKnowledgeBases();
    } catch (err) {
        showToast(err.message || "创建失败", "error");
    }
});

$("kb-name-input").addEventListener("keydown", (e) => {
    if (e.key === "Enter") $("kb-modal-confirm").click();
    if (e.key === "Escape") $("kb-modal-cancel").click();
});

// ============ 知识库列表 ============

function confirmDeleteKB(name) {
    showConfirm({
        title: "确认删除知识库",
        message: `确定要删除知识库 "${name}" 吗？此操作不可恢复。`,
        onConfirm: async () => {
            try {
                await api("DELETE", `/api/knowledgebases/${encodeURIComponent(name)}`);
                showToast("删除成功", "success");
                loadKnowledgeBases();
            } catch (err) {
                showToast(err.message || "删除失败", "error");
            }
        },
    });
}

// ============ 确认对话框 ============

function showConfirm({ title, message, onConfirm }) {
    $("confirm-title").textContent = title || "确认";
    $("confirm-message").textContent = message || "";
    $("confirm-modal").classList.remove("hidden");

    const confirmBtn = $("confirm-confirm");
    const cancelBtn = $("confirm-cancel");

    const cleanup = () => {
        $("confirm-modal").classList.add("hidden");
        confirmBtn.removeEventListener("click", handleConfirm);
        cancelBtn.removeEventListener("click", handleCancel);
    };

    const handleConfirm = () => {
        cleanup();
        onConfirm && onConfirm();
    };

    const handleCancel = () => {
        cleanup();
    };

    confirmBtn.addEventListener("click", handleConfirm);
    cancelBtn.addEventListener("click", handleCancel);
}

// ============ 确认对话框 ============

function enterKnowledgeBase(name) {
    state.currentKB = name;
    $("current-kb-name").textContent = name;
    showView("file-view");
    loadFiles(name);
}

$("btn-back").addEventListener("click", () => {
    state.currentKB = null;
    showView("kb-view");
    loadKnowledgeBases();
});

async function loadFiles(name) {
    try {
        const data = await api("GET", `/api/knowledgebases/${encodeURIComponent(name)}/files`);
        const files = data.files || [];
        renderFileList(files);
    } catch (err) {
        showToast(err.message || "加载文件失败", "error");
        renderFileList([]);
    }
}

function renderFileList(files) {
    const container = $("file-list");
    const empty = $("file-empty");

    if (files.length === 0) {
        container.innerHTML = "";
        empty.classList.remove("hidden");
        return;
    }

    empty.classList.add("hidden");
    container.innerHTML = files
        .map(
            (f) => `
        <div class="file-item">
            <div class="file-info">
                <div class="file-icon">&#128196;</div>
                <div class="file-name">${escapeHtml(f.name)}</div>
            </div>
            <button class="file-delete" data-name="${escapeHtml(f.name)}" title="删除">
                &#128465;
            </button>
        </div>
    `
        )
        .join("");

    container.querySelectorAll(".file-delete").forEach((btn) => {
        btn.addEventListener("click", () => {
            const fileName = btn.dataset.name;
            confirmDeleteFile(fileName);
        });
    });
}

// ============ 确认对话框 ============

$("btn-add-file").addEventListener("click", () => {
    $("file-input").value = "";
    $("file-input").click();
});

$("file-input").addEventListener("change", async (e) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    const kbName = state.currentKB;
    if (!kbName) return;

    let successCount = 0;
    let failCount = 0;

    for (const file of files) {
        const formData = new FormData();
        formData.append("file", file);
        try {
            await api("POST", `/api/knowledgebases/${encodeURIComponent(kbName)}/files`, formData);
            successCount++;
        } catch (err) {
            failCount++;
        }
    }

    if (successCount > 0) {
        showToast(`成功 ${successCount} 个文件`, "success");
    }
    if (failCount > 0) {
        showToast(`${failCount} 个文件上传失败`, "error");
    }

    loadFiles(kbName);
});

// ============ 确认对话框 ============

function confirmDeleteFile(fileName) {
    showConfirm({
        title: "确认删除",
        message: `确定要删除文件 "${fileName}" 吗？`,
        onConfirm: async () => {
            try {
                await api(
                    "DELETE",
                    `/api/knowledgebases/${encodeURIComponent(state.currentKB)}/files/${encodeURIComponent(fileName)}`
                );
                showToast("删除成功", "success");
                loadFiles(state.currentKB);
            } catch (err) {
                showToast(err.message || "删除失败", "error");
            }
        },
    });
}

// ============ 初始化 ============

document.addEventListener("DOMContentLoaded", () => {
    loadKnowledgeBases();
});
