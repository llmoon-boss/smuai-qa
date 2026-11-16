
# -*- coding: utf-8 -*-
import json, sys, time
sys.path.insert(0, r"D:\学年设计\sumai")
from kbsearch import KB
Q = json.load(open(r"D:\学年设计\sumai\eval_queries.json", encoding="utf-8"))
kb = KB()
print("%-26s %-12s %5s %s" % ("query", "gold", "rank", "top1 命中?"))
ok = 0; lat = []
for q, gold in Q:
    t0 = time.time(); hits = kb.search(q, topk=3); lat.append((time.time()-t0)*1000)
    rank = None
    for i, h in enumerate(hits, 1):
        if any(g in h["title"] for g in gold):
            rank = i; break
    exists = any(any(g in d["title"] for g in gold) for d in kb.docs)
    if rank: ok += 1
    print("%-26s %-12s %5s %s" % (q, "/".join(gold)[:12], rank or "-", "gold在语料中:%s" % ("是" if exists else "否")))
print("\n命中率(top3, 全20条)=%d/20" % ok)
import statistics
print("单次检索耗时: 中位 %.0f ms, 最大 %.0f ms (含标题+分块两路 BM25 与 1792 块打分)" % (statistics.median(lat), max(lat)))
