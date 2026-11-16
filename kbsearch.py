
# -*- coding: utf-8 -*-
"""三明学院校园知识库：分块 BM25 + 标题 BM25 的混合检索（RRF 融合）。"""
import json, os, re
import jieba
from rank_bm25 import BM25Okapi

jieba.setLogLevel(20)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_P = os.path.join(BASE_DIR, "kb_docs.json")
CHUNKS_P = os.path.join(BASE_DIR, "kb_chunks.json")

EXTRA = ["学分", "重修", "辅修", "学籍", "学位", "选课", "评教", "绩点", "补考", "缓考", "免修",
         "转专业", "退学", "休学", "复学", "毕业设计", "毕业论文", "开题报告", "毕业实习",
         "实践教育基地", "实验室", "危险化学品", "教学大纲", "培养方案", "教材", "征订",
         "考试作弊", "学位论文作假", "推免", "考研", "国家奖学金", "助学金", "勤工助学",
         "通识教育", "选修课", "专业选修", "教学成果奖", "教改项目", "教学信息员", "教学档案",
         "学业预警", "双语教学", "应征入伍", "入学资格复查", "教室借用", "调课", "停课"]
for w in EXTRA:
    jieba.add_word(w, freq=200000)

def tokenize(text):
    return [t.lower() for t in jieba.lcut(text) if t.strip()]

class KB:
    def __init__(self):
        self.docs = json.load(open(DOCS_P, encoding="utf-8"))
        self.chunks = json.load(open(CHUNKS_P, encoding="utf-8"))
        self.doc_by_id = {d["docId"]: d for d in self.docs}
        self.chunk_toks = [tokenize(c["text"]) for c in self.chunks]
        self.title_toks = [tokenize(d["title"] + " " + d["column"]) for d in self.docs]
        self.bm25_chunk = BM25Okapi(self.chunk_toks)
        self.bm25_title = BM25Okapi(self.title_toks)

    # --- 单路召回 ---
    def rank_chunks(self, q):
        scores = self.bm25_chunk.get_scores(tokenize(q))
        best = {}
        for i, s in enumerate(scores):
            did = self.chunks[i]["docId"]
            if did not in best or s > best[did][0]:
                best[did] = (s, i)
        return sorted(best.items(), key=lambda kv: -kv[1][0])

    def rank_docs_by_title(self, q):
        scores = self.bm25_title.get_scores(tokenize(q))
        order = sorted(range(len(self.docs)), key=lambda i: -scores[i])
        return [(self.docs[i]["docId"], scores[i]) for i in order]

    # --- 混合检索：归一化加权融合（chunk 0.75 + 标题 0.25） ---
    @staticmethod
    def _norm(ranking):
        """把一路排名的分数做 min-max 归一化。"""
        if not ranking:
            return {}
        flat = [(d, sc[0] if isinstance(sc, tuple) else sc) for d, sc in ranking]
        vals = [v for _d, v in flat]
        mx, mn = max(vals), min(vals)
        rng = (mx - mn) or 1e-9
        return {d: (v - mn) / rng for d, v in flat}

    def search(self, q, topk=3, alpha=0.75, rrf_k=None):
        ch = self.rank_chunks(q)
        ti = self.rank_docs_by_title(q)
        if rrf_k:  # 兼容旧实验：RRF 融合
            fused = {}
            for ranking in (ch, ti):
                for r, (did, _s) in enumerate(ranking[:50]):
                    fused[did] = fused.get(did, 0.0) + 1.0 / (rrf_k + r + 1)
            order = sorted(fused.items(), key=lambda kv: -kv[1])
            best_chunk = dict((d, (sc, i)) for d, (sc, i) in ch)
            out = []
            for did, sc in order[:topk]:
                i = best_chunk.get(did, (0, 0))[1]
                out.append(self._pack(did, sc, i))
            return out
        nc, nt = self._norm(ch), self._norm(ti)
        fused = {}
        for d, sc in nc.items():
            fused[d] = alpha * sc
        for d, sc in nt.items():
            fused[d] = fused.get(d, 0.0) + (1 - alpha) * sc
        best_chunk = dict((d, i) for d, (_sc, i) in ch)
        order = sorted(fused.items(), key=lambda kv: -kv[1])
        return [self._pack(d, sc, best_chunk.get(d, 0)) for d, sc in order[:topk]]

    def _pack(self, did, score, cidx):
        d = self.doc_by_id[did]
        c = self.chunks[cidx]
        return {"docId": did, "score": round(score, 4), "title": d["title"], "column": d["column"],
                "date": d["date"], "wenhao": d["wenhao"], "url": did,
                "snippet": c["text"][:180], "chunkIndex": c["chunkIndex"], "nChunks": c["nChunks"]}

    def build_context(self, q, topk=3, max_chars=1400):
        hits = self.search(q, topk)
        parts, used = [], 0
        for i, h in enumerate(hits, 1):
            chs = [c for c in self.chunks if c["docId"] == h["docId"]]
            chs.sort(key=lambda c: c["chunkIndex"])
            start = max(h["chunkIndex"] - 0, 0)
            body = ""
            for c in chs[start:start + 3]:
                body += c["text"]
                if len(body) > 600:
                    break
            block = "[%d]《%s》（%s，%s）%s\n%s" % (
                i, h["title"], h["column"], h["date"], (" " + h["wenhao"] if h["wenhao"] else ""), body[:600])
            if used + len(block) > max_chars:
                break
            parts.append(block)
            used += len(block)
        return "\n\n".join(parts), hits

if __name__ == "__main__":
    import sys
    kb = KB()
    q = sys.argv[1] if len(sys.argv) > 1 else "重修怎么申请"
    ctx, hits = kb.build_context(q, 3)
    print("QUERY:", q)
    for h in hits:
        print("  %.4f %s | %s | %s" % (h["score"], h["column"], h["title"][:40], h["url"]))
    print("\n--- CONTEXT ---\n" + ctx)
