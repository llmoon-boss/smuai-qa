
# -*- coding: utf-8 -*-
"""置信度标定 v2：用查询词覆盖率（而非 min-max 相对分）判定是否可答。"""
import json, sys, re, statistics
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
STOP |= set("的 了 和 与 在 是 有 也 就 都 很 最 更 还 又 把 被 让 给 对 从 到 为 以 及 或 而 并且 所以 因为 但是 如果 这样 那样".split())

def content_tokens(q):
    ts = [t for t in tokenize(q) if t not in STOP and len(t) >= 2 and not re.fullmatch(r"\W+", t)]
    seen, out = set(), []
    for t in ts:
        if t not in seen:
            seen.add(t); out.append(t)
    return out

def confidence(q, topk=3):
    hits = kb.search(q, topk=topk)
    if not hits: return 0.0, 0.0, hits
    toks = content_tokens(q)
    if not toks: return 0.0, 0.0, hits
    best = 0.0
    for h in hits[:1]:
        doc = kb.doc_by_id[h["docId"]]
        doc_toks = set(tokenize(doc["title"] + " " + doc["body"]))
        cov = sum(1 for t in toks if t in doc_toks) / len(toks)
        title_hit = sum(1 for t in toks if t in set(tokenize(doc["title"]))) / len(toks)
        best = max(best, cov)
    return best, title_hit, hits

def collect(qs):
    return sorted(confidence(q)[0] for q in qs)

ins, offs = collect(IN), collect(OFF)
print("域内覆盖率: min=%.2f median=%.2f max=%.2f" % (ins[0], statistics.median(ins), ins[-1]))
print("域外覆盖率: min=%.2f median=%.2f max=%.2f" % (offs[0], statistics.median(offs), offs[-1]))
print("\n域内:")
for q in IN: print("  %.2f  %s  ->  %s" % (confidence(q)[0], q, confidence(q)[2][0]["title"][:34]))
print("\n域外:")
for q in OFF: print("  %.2f  %s  ->  %s" % (confidence(q)[0], q, confidence(q)[2][0]["title"][:34]))

best = None
for i in range(20, 100):
    t = i / 100
    tp = sum(1 for v in ins if v >= t) / len(ins)
    tn = sum(1 for v in offs if v < t) / len(offs)
    acc = (tp + tn) / 2
    if best is None or acc > best[1]:
        best = (t, acc, tp, tn)
print("\n最佳阈值 t=%.2f  域内接受=%.3f  域外拒绝=%.3f  平均=%.3f" % best)
