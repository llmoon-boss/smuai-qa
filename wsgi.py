"""WSGI 入口：给 gunicorn / Render 使用。

启动命令（Render）：
    gunicorn -w 1 -k gthread --threads 4 -b 0.0.0.0:$PORT wsgi:app --timeout 120

首次启动会建表并写入 105 条种子问答与管理员账号，失败不阻塞服务启动（便于看日志）。
"""
import os

from app import app
from db import init_db

if os.getenv("SMU_SKIP_DB_INIT", "0") != "1":
    try:
        init_db()
        print("[db] 初始化完成", flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"[db] 初始化失败：{e}", flush=True)
