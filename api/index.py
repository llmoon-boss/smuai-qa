import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import app  # noqa: E402,F401
from db import init_db  # noqa: E402

if os.getenv("SMU_SKIP_DB_INIT", "0") != "1":
    try:
        init_db()
        print("[db] 初始化完成", flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"[db] 初始化失败：{e}", flush=True)
