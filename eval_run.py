
# -*- coding: utf-8 -*-
"""检索评测：分块 BM25（单路） vs 分块+标题 RRF 混合。"""
import json, time, sys
sys.path.insert(0, r"D:\学年设计\sumai")
from kbsearch import KB

QUERIES = [
    ("重修怎么申请", ["重修"]),
    ("辅修专业怎么报名", ["辅修"]),
    ("学业预警是怎么处理的", ["学业预警"]),
    ("教室可以借用吗", ["教室"]),
    ("教学档案怎么归档", ["教学档案"]),
    ("双语教学课程怎么开", ["双语教学"]),
    ("教学信息员做什么", ["教学信息员"]),
    ("应征入伍学籍怎么保留", ["应征入伍"]),
    ("新生入学资格复查", ["入学资格复查"]),
    ("学位论文作假怎么处理", ["学位论文作假"]),
    ("考研有什么奖励", ["考研"]),
    ("教学成果奖怎么评", ["教学成果奖"]),
    ("教改项目怎么申报", ["教育教学改革研究项目"]),
    ("通识教育选修课要修多少学分", ["通识教育选修课"]),
    ("调课停课怎么办手续", ["课程运行管理"]),
    ("实验室安全怎么管理", ["实验室"]),
    ("毕业论文抽检怎么安排", ["毕业论文"]),
    ("补考怎么报名", ["补考"]),
    ("实践教育基地怎么建设", ["实践教育基地"]),
    ("学生评教怎么操作", ["评教", "教学质量评价"]),
]

def rank_of(hits_titles, gold):
    for i, t in enumerate(hits_titles, 1):
        if any(g in t for g in gold):
            return i
    return None

kb = KB()

def hybrid_titles(q, k=5):
    return [h["title"] for h in kb.search(q, topk=k, rrf_k=60)][:k]

def chunk_only_titles(q, k=5):
    return [kb.doc_by_id[did]["title"] for did, _ in kb.rank_chunks(q)[:k]]

res = []
for q, gold in QUERIES:
    hr = rank_of(hybrid_titles(q), gold)
    cr = rank_of(chunk_only_titles(q), gold)
    n_gold = sum(1 for d in kb.docs if any(g in d["title"] for g in gold))
    res.append((q, gold, cr, hr, n_gold))

def agg(idx, k):
    hit = sum(1 for r in res if r[idx] and r[idx] <= k)
    return hit / len(res)

def mrr(idx):
    s = 0.0
    for r in res:
        if r[idx]:
            s += 1.0 / r[idx]
    return s / len(res)

print("%-28s %-14s %5s %5s %5s" % ("query", "gold", "chunk", "hyb", "#gold"))
for q, gold, cr, hr, n in res:
    print("%-28s %-14s %5s %5s %5d" % (q, "/".join(gold)[:14], cr or "-", hr or "-", n))

print("\n单路 chunk-BM25:  R@1=%.3f  R@3=%.3f  MRR=%.3f" % (agg(2,1), agg(2,3), mrr(2)))
print("混合 RRF(chunk+title): R@1=%.3f  R@3=%.3f  MRR=%.3f" % (agg(3,1), agg(3,3), mrr(3)))
print("gold 文档不存在(语料缺)=%d 条" % sum(1 for r in res if r[4] == 0))
json.dump([{"q": q, "gold": g, "chunkRank": c, "hybridRank": h, "nGoldInCorpus": n} for q, g, c, h, n in res],
          open(r"D:\学年设计\sumai\eval_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
