
import re
p = r"D:\学年设计\sumai\kb_qa.py"
s = open(p, encoding="utf-8").read()

s = s.replace('''class QA:
    def __init__(self):
        self.kb = KB()
''', '''class QA:
    def __init__(self):
        self.kb = KB()
        # 文档频次 → IDF，用于句子打分（避免“学生/学院”这类通用词霸榜）
        self._df = {}
        for d in self.kb.docs:
            for t in set(tokenize(d["title"] + " " + d["body"])):
                self._df[t] = self._df.get(t, 0) + 1
        self._N = len(self.kb.docs)

    def _idf(self, t):
        return math.log((self._N + 1) / (self._df.get(t, 0) + 1)) + 1.0
''')

s = s.replace('''    def extractive(self, q, hits, limit=3):
        toks = self._content_tokens(q)
        picks = []
        for i, h in enumerate(hits, 1):
            doc = self.kb.doc_by_id[h["docId"]]
            chunk = self.kb.chunks[h["chunkIndex"]]["text"]
            best, best_s = None, -1
            for s in self._sentences(chunk):
                sc = sum(1 for t in toks if t in s)
                # 处罚过长句子，避免整段照搬
                sc -= len(s) / 400.0
                if sc > best_s:
                    best, best_s = s, sc
            if best:
                picks.append("根据《%s》：%s [%d]" % (doc["title"], best[:180], i))
            if len(picks) >= limit:
                break
        return "\\n".join("- " + p for p in picks)''', '''    ACTION = ["申请", "报名", "办理", "提交", "审核", "流程", "材料", "时间", "条件",
              "不得", "应当", "须", "可以", "学分", "比例", "期限"]

    def extractive(self, q, hits, limit=3):
        toks = self._content_tokens(q)
        wants_action = any(w in q for w in ("怎么", "如何", "流程", "办理", "申请", "报名", "手续"))
        picks, used = [], set()
        for i, h in enumerate(hits, 1):
            doc = self.kb.doc_by_id[h["docId"]]
            # 用该文档全部块里最能回答问题的句子，而不只是命中的那一块
            cand = []
            for c in self.kb.chunks:
                if c["docId"] != h["docId"]:
                    continue
                cand.extend(self._sentences(c["text"]))
            best, best_s = None, -1
            for s in cand:
                if s in used:
                    continue
                sc = sum(self._idf(t) for t in toks if t in s) / math.sqrt(max(len(s), 20))
                if wants_action:
                    sc *= 1.15 if any(a in s for a in self.ACTION) else 1.0
                if sc > best_s:
                    best, best_s = s, sc
            if best and best_s > 0:
                used.add(best)
                picks.append("根据《%s》：%s [%d]" % (doc["title"], best[:200], i))
            if len(picks) >= limit:
                break
        return "\\n".join("- " + p for p in picks)''')
open(p, "w", encoding="utf-8").write(s)
print("patched extractive scorer")
