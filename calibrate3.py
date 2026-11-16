
# -*- coding: utf-8 -*-
"""置信度 v3：IDF 加权查询词覆盖率。"""
import json, sys, re, math, statistics
sys.path.insert(0, r"D:\学年设计\sumai")
from kbsearch import KB, tokenize
kb = KB()
Q = json.load(open(r"D:\学年设计\sumai\eval_queries.json", encoding="utf-8"))
IN = [q for q, _g in Q]
OFF = ["红烧肉怎么做才好吃", "今天上海天气怎么样", "最近股票行情如何", "怎么快速减肥",
       "推荐一部好看的电影", "汽车保养要注意什么", "王者荣耀怎么上分", "手机电池不耐用怎么办",
       "火锅底料哪个牌子好", "离婚财产怎么分割", "信用卡逾期会怎样", "成都旅游攻略推荐",
       "怎么写一首现代诗", "钢琴入门要练多久", "猫咪为什么总掉毛", "比特币还能买吗",
       "篮球鞋怎么选", "英语四级怎么复习", "租房要注意哪些坑", "如何提高睡眠质量"]
STOP = set("怎么 什么 如何 可以 吗 呢 要 应该 哪些 哪个 怎么办 注意 怎样 是不是 有没有 哪 我 你 请问 一下 介绍 简单 说 办 手续 需要 要求 具体 相关 规定 政策 制度 流程".split())

# 文档频次 → IDF（以 526 篇文档为统计单位）
N = len(kb.docs)
df = {}
doc_ts = []
for d in kb.docs:
    ts = set(tokenize(d["title"] + " " + d["body"]))
    doc_ts.append(ts)
    for t in ts:
        df[t] = df.get(t, 0) + 1
def idf(t):
    return math.log((N + 1) / (df.get(t, 0) + 1)) + 1.0

def weighted_cov(q, doc):
    toks = [t for t in tokenize(q) if t not in STOP and len(t) >= 2]
    seen, toks2 = set(), []
    for t in toks:
        if t not in seen:
            seen.add(t); toks2.append(t)
    if not toks2: return 0.0
    dts = set(tokenize(doc["title"] + " " + doc["body"]))
    num = sum(idf(t) for t in toks2 if t in dts)
    den = sum(idf(t) for t in toks2)
    return num / den if den else 0.0

def conf(q):
    hits = kb.search(q, topk=3)
    if not hits: return 0.0, None
    docs = [kb.doc_by_id[h["docId"]] for h in hits]
    # 取前两篇的最大值，避免单篇抽错导致误判
    v = max(weighted_cov(q, docs[0]), weighted_cov(q, docs[1]) if len(docs) > 1 else 0.0)
    return v, docs[0]["title"]

ins = sorted(conf(q)[0] for q in IN)
offs = sorted(conf(q)[0] for q in OFF)
print("域内: min=%.2f median=%.2f" % (ins[0], statistics.median(ins)))
print("域外: max=%.2f median=%.2f" % (offs[-1], statistics.median(offs)))
print("\n域内低分（需注意）:")
for q in IN:
    v, t = conf(q)
    if v < 0.8: print("  %.2f  %s -> %s" % (v, q, t[:32]))
print("\n域外高分:")
for q in OFF:
    v, t = conf(q)
    if v >= 0.4: print("  %.2f  %s -> %s" % (v, q, t[:32]))
best = None
for i in range(20, 100):
    t = i / 100
    tp = sum(1 for v in ins if v >= t) / len(ins)
    tn = sum(1 for v in offs if v < t) / len(offs)
    acc = (tp + tn) / 2
    if best is None or acc > best[1]: best = (t, acc, tp, tn)
print("\n最佳阈值 t=%.2f  域内接受=%.3f  域外拒绝=%.3f  平均=%.3f" % best)
