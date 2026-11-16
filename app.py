import os
import re
import threading
import time
from functools import wraps

from flask import Flask, jsonify, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from config import COOKIE_SECURE, SECRET_KEY
from db import db_conn, init_db
from llm import chat_once
from matcher import search_kb

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=COOKIE_SECURE,  # 线上 HTTPS 时开启
    MAX_CONTENT_LENGTH=1 * 1024 * 1024,  # 请求体上限 1MB
)
PAGE_SIZE = 5  # 后台列表每页条数

#简单限流：同一 IP 每分钟最多 N 次问答，防止公网被刷爆大模型额度
RATE_PER_MIN = int(os.getenv("SMU_RATE_PER_MIN", "30"))
_rate_lock = threading.Lock()
_rate_hits = {}


def _rate_ok(ip):
    now = time.time()
    with _rate_lock:
        hits = [t for t in _rate_hits.get(ip, []) if now - t < 60]
        if len(hits) >= RATE_PER_MIN:
            _rate_hits[ip] = hits
            return False
        hits.append(now)
        _rate_hits[ip] = hits
        if len(_rate_hits) > 5000:  # 粗粒度清理，避免字典无限增长
            for k in [k for k, v in _rate_hits.items() if not v]:
                _rate_hits.pop(k, None)
        return True


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("is_admin"):
            return jsonify({"ok": False, "error": "未登录"}), 401
        return fn(*args, **kwargs)
    return wrapper


def user_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({"ok": False, "error": "请先登录"}), 401
        return fn(*args, **kwargs)
    return wrapper


def _json_rows(rows):
    for r in rows:
        for k, v in list(r.items()):
            if hasattr(v, "strftime"):
                r[k] = v.strftime("%Y-%m-%d %H:%M:%S")
    return rows


#页面
@app.route("/")
def page_index():
    return render_template("index.html")


@app.route("/admin")
def page_admin():
    return render_template("admin.html")


#问答接口
@app.route("/api/chat", methods=["POST"])
def api_chat():
    """用户问答知识库返回标准答案，调用大模型兜底。"""
    data = request.get_json(silent=True) or {}
    question = str(data.get("question") or "").strip()
    if not question:
        return jsonify({"ok": False, "error": "问题不能为空"}), 400
    if len(question) > 500:
        return jsonify({"ok": False, "error": "问题过长（最多 500 字）"}), 400
    # 反向代理（Render/Nginx）后真实客户端 IP 在 X-Forwarded-For 首位
    fwd = request.headers.get("X-Forwarded-For", "")
    ip = (fwd.split(",")[0].strip() or request.headers.get("X-Real-IP")
          or request.remote_addr or "-")
    if not _rate_ok(ip):
        return jsonify({"ok": False, "error": "提问过于频繁，请稍后再试"}), 429

    matched = search_kb(question)
    if matched:
        answer, source = matched["answer"], "kb"
    else:
        answer, _ = chat_once(question)  # 大模型兜底；内部已处理异常降级
        source = "llm"

    try:  # 记录聊天日志；日志失败不影响问答
        with db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO chat_logs (user_question, reply_source, answer) "
                    "VALUES (%s, %s, %s)",
                    (question, source, answer),
                )
    except Exception:
        pass
    return jsonify({"ok": True, "answer": answer, "source": source})


# 知识库管理接口
@app.route("/api/qa", methods=["GET"])
@admin_required
def api_qa_list():
    page = max(1, request.args.get("page", 1, type=int))
    kw = request.args.get("kw", "").strip()
    like = f"%{kw}%"
    with db_conn() as conn:
        with conn.cursor() as cur:
            if kw:
                cur.execute(
                    "SELECT * FROM qa_pairs "
                    "WHERE question LIKE %s OR keywords LIKE %s "
                    "ORDER BY id DESC LIMIT %s OFFSET %s",
                    (like, like, PAGE_SIZE, (page - 1) * PAGE_SIZE),
                )
                rows = cur.fetchall()
                cur.execute(
                    "SELECT COUNT(*) AS c FROM qa_pairs "
                    "WHERE question LIKE %s OR keywords LIKE %s",
                    (like, like),
                )
            else:
                cur.execute(
                    "SELECT * FROM qa_pairs ORDER BY id DESC LIMIT %s OFFSET %s",
                    (PAGE_SIZE, (page - 1) * PAGE_SIZE),
                )
                rows = cur.fetchall()
                cur.execute("SELECT COUNT(*) AS c FROM qa_pairs")
            total = cur.fetchone()["c"]
    return jsonify({"ok": True, "rows": _json_rows(rows), "total": total,
                    "page": page, "page_size": PAGE_SIZE})


@app.route("/api/qa", methods=["POST"])
@admin_required
def api_qa_add():
    """新增问答"""
    data = request.get_json(silent=True) or {}
    question = str(data.get("question") or "").strip()
    answer = str(data.get("answer") or "").strip()
    if not question or not answer:
        return jsonify({"ok": False, "error": "问题与答案不能为空"}), 400
    keywords = str(data.get("keywords") or "").strip()
    category = str(data.get("category") or "其他").strip()
    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO qa_pairs (question, answer, keywords, category) "
                "VALUES (%s, %s, %s, %s)",
                (question, answer, keywords, category),
            )
    return jsonify({"ok": True})


@app.route("/api/qa/<int:qa_id>", methods=["PUT"])
@admin_required
def api_qa_update(qa_id):
    """修改问答"""
    data = request.get_json(silent=True) or {}
    question = str(data.get("question") or "").strip()
    answer = str(data.get("answer") or "").strip()
    if not question or not answer:
        return jsonify({"ok": False, "error": "问题与答案不能为空"}), 400
    keywords = str(data.get("keywords") or "").strip()
    category = str(data.get("category") or "其他").strip()
    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE qa_pairs SET question=%s, answer=%s, keywords=%s, "
                "category=%s WHERE id=%s",
                (question, answer, keywords, category, qa_id),
            )
    return jsonify({"ok": True})


@app.route("/api/qa/<int:qa_id>", methods=["DELETE"])
@admin_required
def api_qa_delete(qa_id):
    """删除问答对。"""
    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM qa_pairs WHERE id=%s", (qa_id,))
    return jsonify({"ok": True})

#聊天记录
@app.route("/api/logs", methods=["GET"])
@admin_required
def api_logs():
    """最近 50 条聊天记录"""
    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM chat_logs ORDER BY id DESC LIMIT 50")
            rows = cur.fetchall()
    return jsonify({"ok": True, "rows": _json_rows(rows)})


#登录/退出
@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username") or "").strip()
    password = str(data.get("password") or "")
    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT password_hash FROM admin WHERE username=%s",
                        (username,))
            row = cur.fetchone()
    if row and check_password_hash(row["password_hash"], password):
        session["is_admin"] = True
        return jsonify({"ok": True})
    return jsonify({"ok": False, "error": "用户名或密码错误"}), 401


@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"ok": True})


#用户注册/登录/反馈（用户端）
@app.route("/api/user/register", methods=["POST"])
def api_user_register():
    """用户注册：成功即自动登录。"""
    data = request.get_json(silent=True) or {}
    username = str(data.get("username") or "").strip()
    nickname = str(data.get("nickname") or "").strip()
    password = str(data.get("password") or "")
    if not re.fullmatch(r"[A-Za-z0-9_]{3,20}", username):
        return jsonify({"ok": False, "error": "用户名需为 3-20 位字母、数字或下划线"}), 400
    if not nickname or len(nickname) > 20:
        return jsonify({"ok": False, "error": "请填写昵称/姓名（20 字以内）"}), 400
    if len(password) < 6 or len(password) > 64:
        return jsonify({"ok": False, "error": "密码长度需为6-64位"}), 400
    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE username=%s", (username,))
            if cur.fetchone():
                return jsonify({"ok": False, "error": "用户名已被注册"}), 400
            cur.execute(
                "INSERT INTO users (username, password_hash, nickname) VALUES (%s, %s, %s)",
                (username, generate_password_hash(password), nickname))
            cur.execute("SELECT id FROM users WHERE username=%s", (username,))
            uid = cur.fetchone()["id"]
    session["user_id"], session["username"], session["nickname"] = uid, username, nickname
    return jsonify({"ok": True, "nickname": nickname})


@app.route("/api/user/login", methods=["POST"])
def api_user_login():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username") or "").strip()
    password = str(data.get("password") or "")
    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, username, nickname, password_hash FROM users WHERE username=%s",
                (username,))
            row = cur.fetchone()
    if row and check_password_hash(row["password_hash"], password):
        session["user_id"] = row["id"]
        session["username"] = row["username"]
        session["nickname"] = row["nickname"]
        return jsonify({"ok": True, "nickname": row["nickname"]})
    return jsonify({"ok": False, "error": "用户名或密码错误"}), 401


@app.route("/api/user/logout", methods=["POST"])
def api_user_logout():
    for k in ("user_id", "username", "nickname"):
        session.pop(k, None)
    return jsonify({"ok": True})


@app.route("/api/user/me")
def api_user_me():
    """当前登录用户信息"""
    uid = session.get("user_id")
    if not uid:
        return jsonify({"ok": False})
    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT username, nickname, create_time FROM users WHERE id=%s", (uid,))
            row = cur.fetchone()
    if not row:
        return jsonify({"ok": False})
    return jsonify({"ok": True, **_json_rows([row])[0]})

@app.route("/api/feedback", methods=["POST"])
@user_required
def api_feedback_add():
    data = request.get_json(silent=True) or {}
    content = str(data.get("content") or "").strip()
    if not content:
        return jsonify({"ok": False, "error": "反馈内容不能为空"}), 400
    if len(content) > 1000:
        return jsonify({"ok": False, "error": "反馈内容过长"}), 400
    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO feedbacks (user_id, content) VALUES (%s, %s)",
                        (session["user_id"], content))
    return jsonify({"ok": True})
#用户反馈管理
@app.route("/api/feedbacks", methods=["GET"])
@admin_required
def api_feedback_list():
    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT f.id, f.user_id, f.content, f.status, f.create_time, "
                "u.username, u.nickname FROM feedbacks f "
                "LEFT JOIN users u ON f.user_id = u.id "
                "ORDER BY f.id DESC LIMIT 200")
            rows = cur.fetchall()
    return jsonify({"ok": True, "rows": _json_rows(rows)})


@app.route("/api/feedbacks/<int:fid>", methods=["PUT"])
@admin_required
def api_feedback_update(fid):
    data = request.get_json(silent=True) or {}
    status = 1 if str(data.get("status") or "0") == "1" else 0
    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE feedbacks SET status=%s WHERE id=%s", (status, fid))
    return jsonify({"ok": True})


if __name__ == "__main__":
    try:
        init_db()
    except Exception as e:
        print(f"数据库初始化失败：{e}")
        # print("请检查 config.py 的 DB_CONFIG，并确认MySQL已启动")
    app.run(
        host=os.getenv("SMU_HOST", "0.0.0.0"),
        port=int(os.getenv("SMU_PORT", "5000")),
        debug=False,
    )
