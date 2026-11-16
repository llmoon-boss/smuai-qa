// 知识库管理后台脚本（简版）
let editingId = null;   //正在编辑的问答 ID（null 表示新增）
let rowsCache = [];     //当前页数据缓存（供编辑回填）
let page = 1;
const PAGE_SIZE = 5;

const $ = (id) => document.getElementById(id);

// 登录/退出
$("login-btn").addEventListener("click", async () => {
  const resp = await fetch("/api/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      username: $("login-username").value.trim(),
      password: $("login-password").value,
    }),
  });
  const data = await resp.json();
  if (data.ok) {
    $("login-view").classList.add("hidden");
    $("panel-view").classList.remove("hidden");
    loadQa();
    loadLogs();
    loadFeedbacks();
  } else {
    alert(data.error || "登录失败");
  }
});

$("logout-btn").addEventListener("click", async () => {
  await fetch("/api/logout", { method: "POST" });
  location.reload();
});

//标签页切换
document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
    tab.classList.add("active");
    const name = tab.dataset.tab;
    document.querySelectorAll("[id^='tab-']").forEach((p) => p.classList.add("hidden"));
    $("tab-" + name).classList.remove("hidden");
  });
});

//知识库列表
async function loadQa() {
  const kw = $("kw-input").value.trim();
  const resp = await fetch(`/api/qa?page=${page}&kw=${encodeURIComponent(kw)}`);
  if (resp.status === 401) { location.reload(); return; }
  const data = await resp.json();
  rowsCache = data.rows;
  $("qa-tbody").innerHTML = data.rows.map((r) => `
    <tr>
      <td>${r.id}</td>
      <td>${escapeHtml(r.question)}</td>
      <td class="answer-cell">${escapeHtml(r.answer)}</td>
      <td>${escapeHtml(r.keywords)}</td>
      <td>${escapeHtml(r.category)}</td>
      <td>
        <button class="mini-btn" onclick="editRow(${r.id})">编辑</button>
        <button class="mini-btn danger" onclick="deleteRow(${r.id})">删除</button>
      </td>
    </tr>`).join("");
  const totalPages = Math.max(1, Math.ceil(data.total / PAGE_SIZE));
  $("page-info").textContent = `第 ${data.page} / ${totalPages} 页（共 ${data.total} 条）`;
  $("prev-btn").disabled = data.page <= 1;
  $("next-btn").disabled = data.page >= totalPages;
}

// 编辑：回填表单，提交按钮切换为"保存修改"
function editRow(id) {
  const r = rowsCache.find((x) => x.id === id);
  if (!r) return;
  editingId = id;
  $("f-question").value = r.question;
  $("f-answer").value = r.answer;
  $("f-keywords").value = r.keywords || "";
  $("f-category").value = r.category || "";
  $("qa-submit-btn").textContent = "保存修改";
  $("qa-cancel-btn").classList.remove("hidden");
}

async function deleteRow(id) {
  if (!confirm("确定删除这条问答吗？")) return;
  await fetch(`/api/qa/${id}`, { method: "DELETE" });
  loadQa();
}

function cancelEdit() {
  editingId = null;
  $("qa-form").reset();
  $("qa-submit-btn").textContent = "新增问答";
  $("qa-cancel-btn").classList.add("hidden");
}

// ---------- 新增 / 修改提交 ----------
$("qa-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const payload = {
    question: $("f-question").value.trim(),
    answer: $("f-answer").value.trim(),
    keywords: $("f-keywords").value.trim(),
    category: $("f-category").value.trim(),
  };
  if (!payload.question || !payload.answer) { alert("问题和答案不能为空"); return; }
  if (editingId) {
    await fetch(`/api/qa/${editingId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } else {
    await fetch("/api/qa", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  }
  cancelEdit();
  loadQa();
});

//分页/搜索/取消
$("prev-btn").addEventListener("click", () => { page--; loadQa(); });
$("next-btn").addEventListener("click", () => { page++; loadQa(); });
$("kw-search-btn").addEventListener("click", () => { page = 1; loadQa(); });
$("qa-cancel-btn").addEventListener("click", cancelEdit);

//聊天记录
async function loadLogs() {
  const resp = await fetch("/api/logs");
  const data = await resp.json();
  $("logs-tbody").innerHTML = data.rows.map((r) => `
    <tr>
      <td>${r.id}</td>
      <td>${escapeHtml(r.user_question)}</td>
      <td>${r.reply_source === "kb" ? "知识库" : "AI"}</td>
      <td class="answer-cell">${escapeHtml(r.answer)}</td>
      <td>${r.create_time}</td>
    </tr>`).join("");
}

//用户反馈
async function loadFeedbacks() {
  const resp = await fetch("/api/feedbacks");
  if (resp.status === 401) { location.reload(); return; }
  const data = await resp.json();
  const rows = (data.rows || []).map((r) => `
    <tr>
      <td>${r.id}</td>
      <td>${escapeHtml(r.nickname || "（未填写）")}</td>
      <td>${escapeHtml(r.username || String(r.user_id))}</td>
      <td class="answer-cell">${escapeHtml(r.content)}</td>
      <td>${r.status === 1 ? "已处理" : "待处理"}</td>
      <td>${r.create_time}</td>
      <td>
        <button class="mini-btn" onclick="toggleFeedback(${r.id}, ${r.status})">
          ${r.status === 1 ? "设为待处理" : "标记已处理"}
        </button>
      </td>
    </tr>`).join("");
  $("feedbacks-tbody").innerHTML = rows || `<tr><td colspan="7" class="hint">暂无用户反馈</td></tr>`;
}

async function toggleFeedback(id, status) {
  const resp = await fetch(`/api/feedbacks/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status: status === 1 ? 0 : 1 }),
  });
  if (resp.status === 401) { location.reload(); return; }
  loadFeedbacks();
}

//工具
function escapeHtml(s) {
  return String(s ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
