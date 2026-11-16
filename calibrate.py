
# -*- coding: utf-8 -*-
"""拒答阈值标定：域内问题 vs 域外问题的 top-1 融合分分布。"""
import json, sys, statistics
sys.path.insert(0, r"D:\学年设计\sumai")
from kbsearch import KB
kb = KB()
Q = json.load(open(r"D:\学年设计\sumai\eval_queries.json", encoding="utf-8"))
IN = [q for q, _g in Q]
OFF = ["红烧肉怎么做才好吃", "今天上海天气怎么样", "最近股票行情如何", "怎么快速减肥",
       "推荐一部好看的电影", "汽车保养要注意什么", "王者荣耀怎么上分", "手机电池不耐用怎么办",
       "火锅底料哪个牌子好", "离婚财产怎么分割", "信用卡逾期会怎样", "成都旅游攻略推荐",
       "怎么写一首现代诗", "钢琴入门要练多久", "猫咪为什么总掉毛", "比特币还能买吗",
       "篮球鞋怎么选", "英语四级怎么复习", "租房要注意哪些坑", "如何提高睡眠质量"]

def scores(q):
    h = kb.search(q, topk=2)
    return [x["score"] for x in h] + [0.0, 0.0]

ins = sorted(scores(q)[0] for q in IN)
offs = sorted(scores(q)[0] for q in OFF)
print("域内 top1 分: min=%.3f  median=%.3f  max=%.3f" % (ins[0], statistics.median(ins), ins[-1]))
print("域外 top1 分: min=%.3f  median=%.3f  max=%.3f" % (offs[0], statistics.median(offs), offs[-1]))
print("\n域内明细:")
for q in IN: print("  %.3f  %s" % (scores(q)[0], q))
print("\n域外明细:")
for q in OFF: print("  %.3f  %s" % (scores(q)[0], q))

# 在候选阈值上扫描，最大化 (域内召回 + 域外拒绝)/2
best = None
for t in [i/100 for i in range(10, 80)]:
    tp = sum(1 for v in ins if v >= t) / len(ins)
    tn = sum(1 for v in offs if v < t) / len(offs)
    acc = (tp + tn) / 2
    if best is None or acc > best[1]:
        best = (t, acc, tp, tn)
print("\n最佳阈值 t=%.2f  域内召回=%.3f  域外拒绝=%.3f  平均=%.3f" % best)
json.dump({"in": ins, "off": offs, "threshold": best[0]}, open(r"D:\学年设计\sumai\calib.json", "w"), indent=1)
