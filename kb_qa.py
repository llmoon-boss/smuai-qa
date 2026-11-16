
# -*- coding: utf-8 -*-
"""问答层：检索 → 置信度门控 → 生成（LLM 或抽取式）→ 带引用输出。"""
import os, re, sys, json, math
sys.path.insert(0, r"D:\学年设计\sumai")
from kbsearch import KB, tokenize

STOP = set("怎么 什么 如何 可以 吗 呢 要 应该 哪些 哪个 怎么办 注意 怎样 是不是 有没有 哪 我 你 请问 一下 介绍 简单 说 办 手续 需要 要求 具体 相关 规定 政策 制度 流程".split())

PROMPT = """你是三明学院的校园智能问答助手，回答对象是在校学生。请严格依据下面给出的【资料】回答，不要使用资料之外的知识。

【资料】
{context}

【问题】{question}

【回答要求】
1. 只使用【资料】中的信息；资料不足时直接说明“知识库中暂未收录该信息”，不要猜测或编造。
2. 每条事实性陈述后标注来源编号，如 [1]、[2]；编号必须与【资料】中的编号一致。
3. 先给结论，再给办理流程/条件/时间等要点，用短句和分点。
4. 使用简体中文，语气平实，不夸大，不承诺资料中不存在的服务。
"""

class QA:
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

    # ---------- 置信度：查询词在候选文档中的覆盖率 ----------
    @staticmethod
    def _content_tokens(q):
        out, seen = [], set()
        for t in tokenize(q):
            if t in STOP or len(t) < 2 or re.fullmatch(r"\W+", t):
                continue
            if t not in seen:
                seen.add(t); out.append(t)
        return out

    def coverage(self, q, doc):
        toks = self._content_tokens(q)
        if not toks:
            return 0.0
        dt = set(tokenize(doc["title"] + " " + doc["body"]))
        return sum(1 for t in toks if t in dt) / len(toks)

    def confidence(self, q, hits):
        vals = []
        for h in hits[:2]:
            vals.append(self.coverage(q, self.kb.doc_by_id[h["docId"]]))
        return max(vals) if vals else 0.0

    # ---------- 抽取式答案（无 LLM 时的降级模式） ----------
    def _sentences(self, text):
        return [s.strip() for s in re.split(r"[。；\n]", text) if len(s.strip()) > 8]

    ACTION = ["申请", "报名", "办理", "提交", "审核", "流程", "材料", "时间", "条件",
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
        return "\n".join("- " + p for p in picks)

    # ---------- 主入口 ----------
    def answer(self, q, topk=3, threshold=0.6, llm=None):
        hits = self.kb.search(q, topk=topk)
        if not hits:
            return {"question": q, "refused": True, "confidence": 0.0, "answer": "知识库中暂未收录与「%s」相关的内容。" % q, "sources": []}
        conf = self.confidence(q, hits)
        if conf < threshold:
            return {"question": q, "refused": True, "confidence": round(conf, 3),
                    "answer": "知识库中暂未收录与「%s」相关的明确规定。当前收录范围为三明学院官网教务处规章制度、教务/学务/考试/实践等栏目的公开文件，建议咨询所在学院教学秘书或教务处。" % q,
                    "sources": [{"n": i, "title": h["title"], "column": h["column"], "date": h["date"],
                                "wenhao": h["wenhao"], "url": h["url"], "score": h["score"]}
                               for i, h in enumerate(hits, 1)]}
        ctx, _ = self.kb.build_context(q, topk=topk, max_chars=1400)
        if llm:
            text = llm(PROMPT.format(context=ctx, question=q))
        else:
            text = self.extractive(q, hits, limit=3)
        return {"question": q, "refused": False, "confidence": round(conf, 3), "answer": text,
                "sources": [{"n": i, "title": h["title"], "column": h["column"], "date": h["date"],
                             "wenhao": h["wenhao"], "url": h["url"], "score": h["score"]}
                            for i, h in enumerate(hits, 1)],
                "context": ctx}

def llm_from_env():
    """可选：OpenAI 兼容接口（DeepSeek / 通义 / 本地 vLLM 均可）。"""
    key = os.environ.get("DSH_LLM_KEY") or os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not key:
        return None
    base = os.environ.get("DSH_LLM_BASE", "https://api.deepseek.com/v1")
    model = os.environ.get("DSH_LLM_MODEL", "deepseek-chat")
    import urllib.request
    def call(prompt):
        body = json.dumps({"model": model, "temperature": 0.1,
                           "messages": [{"role": "user", "content": prompt}]}).encode()
        req = urllib.request.Request(base.rstrip("/") + "/chat/completions", data=body,
                                     headers={"Content-Type": "application/json", "Authorization": "Bearer " + key})
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())["choices"][0]["message"]["content"].strip()
    return call

if __name__ == "__main__":
    qa = QA()
    for q in (sys.argv[1:] or ["重修怎么申请", "辅修专业怎么报名", "红烧肉怎么做才好吃"]):
        r = qa.answer(q)
        print("=" * 70)
        print("Q:", q, "| 置信度", r["confidence"], "| 拒答" if r["refused"] else "| 作答")
        print(r["answer"])
        if not r["refused"]:
            for s in r["sources"]:
                print("  [%d] %s（%s，%s）%s" % (s["n"], s["title"], s["column"], s["date"], s["url"]))
