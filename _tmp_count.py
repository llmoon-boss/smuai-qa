import csv
from collections import Counter

import os

csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "问答数据.csv")
with open(csv_path, encoding="utf-8-sig") as f:
    rows = [r for r in csv.reader(f) if r and r[0] and r[0] != "类别"]
print("有效记录:", len(rows))
print("列数一致:", all(len(r) == len(rows[0]) for r in rows))
print("列头:", rows[0] if len(rows[0]) != 5 else "5列(类别,问题,答案,关键词,来源)")
print("分类统计:", dict(Counter(r[0] for r in rows)))
