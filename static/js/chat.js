// 用户端问答脚本
const chatBox = document.getElementById("chat-box");
const input = document.getElementById("question-input");
const sendBtn = document.getElementById("send-btn");

// 把纯文本排成段落：以 - 、· 、• 开头的行作条目，其余作正文段
function renderText(target, text) {
  const lines = String(text).split(/\r?\n/);
  lines.forEach((line) => {
    const t = line.trim();
    if (!t) return;
    const p = document.createElement("p");
    if (/^[-·•]\s+/.test(t)) {
      p.className = "li";
      p.textContent = t.replace(/^[-·•]\s+/, "");
    } else {
      p.className = "para";
      p.textContent = t;
    }
    target.appendChild(p);
  });
  if (!target.childNodes.length) target.textContent = String(text);
}

// 添加一条问答记录：who = 'user' | 'bot'
function addMsg(text, who, source) {
  const div = document.createElement("div");
  div.className = "msg " + who;

  const tag = document.createElement("span");
  tag.className = "msg-tag";
  tag.textContent = who === "user" ? "问" : "答";

  const body = document.createElement("div");
  body.className = "msg-body";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  renderText(bubble, text);
  body.appendChild(bubble);

  if (source) {
    const src = document.createElement("div");
    src.className = "source";
    src.textContent = source;
    body.appendChild(src);
  }

  div.appendChild(tag);
  div.appendChild(body);
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
  return div;
}

async function send() {
  const q = input.value.trim();
  if (!q) return;
  input.value = "";
  const empty = document.getElementById("chat-empty");
  if (empty) empty.remove();
  addMsg(q, "user");
  sendBtn.disabled = true;
  const typing = addMsg("正在检索知识库…", "bot", "");
  typing.classList.add("pending");
  try {
    const resp = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: q }),
    });
    const data = await resp.json();
    typing.remove();
    if (data.ok) {
      addMsg(data.answer, "bot",
        data.source === "kb" ? "来源｜校园知识库（附原文可核对）" : "来源｜大模型生成，未经知识库校验");
    } else {
      addMsg(data.error || "出错了，请稍后再试。", "bot", "状态｜请求未被处理");
    }
  } catch (err) {
    typing.remove();
    addMsg("网络错误，请稍后再试。", "bot", "状态｜网络请求失败");
  } finally {
    sendBtn.disabled = false;
  }
}

sendBtn.addEventListener("click", send);
input.addEventListener("keydown", (e) => { if (e.key === "Enter") send(); });

// 常见问题：点击后填入输入框并直接发送
document.querySelectorAll(".chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    input.value = chip.dataset.q;
    send();
  });
});

// ==================== 用户登录 / 注册 / 意见反馈 ====================
const $ = (id) => document.getElementById(id);
const userBar = {
  login: $("btn-login"),
  register: $("btn-register"),
  feedback: $("btn-feedback"),
  logout: $("btn-logout"),
  name: $("user-name"),
};

function showModal(id) { $(id).classList.remove("hidden"); }
function hideModal(id) { $(id).classList.add("hidden"); }

// 根据登录状态刷新右上方入口
function refreshUserBar() {
  fetch("/api/user/me")
    .then((r) => r.json())
    .then((d) => {
      const logged = !!d.ok;
      userBar.name.textContent = d.ok ? d.nickname : "";
      userBar.name.classList.toggle("hidden", !logged);
      userBar.login.classList.toggle("hidden", logged);
      userBar.register.classList.toggle("hidden", logged);
      userBar.feedback.classList.toggle("hidden", !logged);
      userBar.logout.classList.toggle("hidden", !logged);
    })
    .catch(() => {});
}

async function postJSON(url, body) {
  const resp = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return resp.json();
}

async function doLogin() {
  const data = await postJSON("/api/user/login", {
    username: $("login-user").value.trim(),
    password: $("login-pass").value,
  });
  if (data.ok) {
    hideModal("login-modal");
    $("login-user").value = $("login-pass").value = $("login-err").textContent = "";
    refreshUserBar();
  } else {
    $("login-err").textContent = data.error || "登录失败";
  }
}

async function doRegister() {
  const data = await postJSON("/api/user/register", {
    username: $("reg-user").value.trim(),
    nickname: $("reg-nick").value.trim(),
    password: $("reg-pass").value,
  });
  if (data.ok) {
    hideModal("register-modal");
    $("reg-user").value = $("reg-nick").value = $("reg-pass").value = "";
    $("reg-err").textContent = "";
    refreshUserBar();
  } else {
    $("reg-err").textContent = data.error || "注册失败";
  }
}

async function doFeedback() {
  const data = await postJSON("/api/feedback", { content: $("fb-content").value.trim() });
  if (data.ok) {
    hideModal("feedback-modal");
    $("fb-content").value = "";
    $("fb-err").textContent = "";
    alert("反馈已提交，管理员会尽快查看，感谢你的建议。");
  } else {
    $("fb-err").textContent = data.error || "提交失败";
  }
}

userBar.login.addEventListener("click", () => showModal("login-modal"));
userBar.register.addEventListener("click", () => showModal("register-modal"));
userBar.feedback.addEventListener("click", () => showModal("feedback-modal"));
userBar.logout.addEventListener("click", async () => {
  await postJSON("/api/user/logout", {});
  refreshUserBar();
});
$("login-ok").addEventListener("click", doLogin);
$("reg-ok").addEventListener("click", doRegister);
$("fb-ok").addEventListener("click", doFeedback);
$("login-cancel").addEventListener("click", () => hideModal("login-modal"));
$("reg-cancel").addEventListener("click", () => hideModal("register-modal"));
$("fb-cancel").addEventListener("click", () => hideModal("feedback-modal"));
$("go-register").addEventListener("click", () => {
  hideModal("login-modal");
  showModal("register-modal");
});
$("go-login").addEventListener("click", () => {
  hideModal("register-modal");
  showModal("login-modal");
});
// 回车提交
$("login-pass").addEventListener("keydown", (e) => { if (e.key === "Enter") doLogin(); });
$("reg-pass").addEventListener("keydown", (e) => { if (e.key === "Enter") doRegister(); });
// 点击遮罩层关闭
document.querySelectorAll(".modal-mask").forEach((m) => {
  m.addEventListener("click", (e) => { if (e.target === m) m.classList.add("hidden"); });
});

refreshUserBar();
