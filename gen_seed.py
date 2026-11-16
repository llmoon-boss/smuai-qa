# -*- coding: utf-8 -*-
"""从 问答数据.csv 生成 db.py 的 SEED_QA 种子数据（数据改了重跑本脚本即可）"""
import csv

CSV_PATH = "问答数据.csv"
DB_PATH = "db.py"

with open(CSV_PATH, encoding="utf-8-sig") as f:
    rows = [r for r in csv.reader(f) if r and r[0] and r[0] != "类别"]
    # 列顺序：类别, 问题, 答案, 关键词, 核实来源
    data = [(r[0], r[1], r[2], r[3]) for r in rows]


def py_str(s):
    """转成 Python 单引号字符串字面量"""
    return "'" + s.replace("\\", "\\\\").replace("'", "\\'") + "'"


lines = [
    "# 校园问答对（数据来源：问答数据.csv，依据三明学院官方文件整理；",
    "# 修改数据请改 CSV 后重跑 gen_seed.py）",
    "SEED_QA = [",
]
for cat, q, a, kw in data:
    lines.append(f"    ({py_str(q)},\n     {py_str(a)},\n     {py_str(kw)}, {py_str(cat)}),")
lines.append("]")
seed_code = "\n".join(lines) + "\n"

with open(DB_PATH, encoding="utf-8") as f:
    src = f.read()

# 找到种子区起点（SEED_QA 赋值语句），替换其后全部内容（幂等，可重复运行）
marker = "SEED_QA = ["
idx = src.index(marker)
new_src = src[:idx] + seed_code

with open(DB_PATH, "w", encoding="utf-8") as f:
    f.write(new_src)

print(f"OK：已生成 {len(data)} 条种子数据写入 {DB_PATH}")
