
# -*- coding: utf-8 -*-
"""消融实验：四种召回/融合策略的 R@1 / R@3 / MRR。"""
import json, sys
sys.path.insert(0, r"D:\学年设计\sumai")
from kbsearch import KB

Q = json.load(open(r"D:\学年设计\sumai\eval_queries.json", encoding="utf-8"))
kb = KB()

def norm(vec):
    if not vec: return []
    mx = max(v for _, v in vec) or 1e-9
    mn = min(v for _, v in vec)
    rng = (mx - mn) or 1e-9
    return [(k, (v - mn) / rng) for k, v in vec]

def rank_chunk(q):
    return [d for d, _ in kb.rank_chunks(q)]

def rank_title(q):
    return [d for d, _ in kb.rank_docs_by_title(q)]

def rank_rrf(q, k=60):
    fused = {}
    for ranking in (rank_chunk(q), rank_title(q)):
        for r, did in enumerate(ranking[:50]):
            fused[did] = fused.get(did, 0.0) + 1.0 / (k + r + 1)
    return [d for d, _ in sorted(fused.items(), key=lambda kv: -kv[1])]

def rank_score(q, alpha=0.75):
    ch = norm([(d, s) for d, (s, _i) in [(x[0], x[1]) for x in kb.rank_chunks(q)]])
    ti = norm([(d, s) for d, s in kb.rank_docs_by_title(q)])
    fused = {}
    for d, s in ch: fused[d] = alpha * s
    for d, s in ti: fused[d] = fused.get(d, 0.0) + (1 - alpha) * s
    return [d for d, _ in sorted(fused.items(), key=lambda kv: -kv[1])]

STRATS = [("chunk-only", rank_chunk), ("title-only", rank_title),
          ("RRF(60)", rank_rrf), ("score a=0.75", lambda q: rank_score(q, 0.75)),
          ("score a=0.6", lambda q: rank_score(q, 0.6)), ("score a=0.9", lambda q: rank_score(q, 0.9))]

def hit_rank(order, gold, k=5):
    for i, did in enumerate(order[:k], 1):
        t = kb.doc_by_id[did]["title"]
        if any(g in t for g in gold):
            return i
    return None

print("%-14s %6s %6s %6s" % ("strategy", "R@1", "R@3", "MRR"))
for name, fn in STRATS:
    ranks = [hit_rank(fn(q), g) for q, g in Q]
    r1 = sum(1 for r in ranks if r == 1) / len(Q)
    r3 = sum(1 for r in ranks if r and r <= 3) / len(Q)
    mrr = sum((1.0 / r) for r in ranks if r) / len(Q)
    print("%-14s %6.3f %6.3f %6.3f" % (name, r1, r3, mrr))
