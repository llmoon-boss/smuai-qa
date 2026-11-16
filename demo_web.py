
# -*- coding: utf-8 -*-
"""毕业设计演示服务：Flask + 单页问答界面（独立于学年设计 app.py）。"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
from flask import Flask, request, jsonify, render_template  # noqa: E402
from kb_qa import QA, llm_from_env  # noqa: E402

app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates_demo"))
qa = QA()
LLM = llm_from_env()   # 设 DSH_LLM_KEY / DEEPSEEK_API_KEY 后启用大模型生成，否则抽取式降级

SAMPLES = ["重修怎么申请", "辅修专业怎么报名", "学业预警怎么处理", "教室可以借用吗",
           "教学成果奖怎么评", "毕业论文抽检怎么安排", "实验室安全怎么管理", "红烧肉怎么做才好吃"]

@app.get("/")
def index():
    return render_template("index.html", samples=SAMPLES, n_docs=len(qa.kb.docs),
                           n_chunks=len(qa.kb.chunks), llm=("大模型生成" if LLM else "抽取式降级"))

@app.get("/api/ask")
def api_ask():
    q = (request.args.get("q") or "").strip()
    if not q:
        return jsonify({"error": "empty query"}), 400
    return jsonify(qa.answer(q, llm=LLM))

@app.get("/api/stats")
def api_stats():
    return jsonify({"docs": len(qa.kb.docs), "chunks": len(qa.kb.chunks),
                    "chars": sum(c["len"] for c in qa.kb.chunks)})

if __name__ == "__main__":
    app.run(
        host=os.getenv("SMU_DEMO_HOST", "0.0.0.0"),
        port=int(os.getenv("SMU_DEMO_PORT", "8010")),
        debug=False,
        use_reloader=False,
    )
