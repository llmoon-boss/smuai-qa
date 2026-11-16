
import re
p = r"D:\学年设计\sumai\kbsearch.py"
s = open(p, encoding="utf-8").read()

# 1) search(): 默认改为归一化加权融合（alpha=0.75），保留 use_rrf 开关
old_start = s.index("    # --- 混合检索（RRF） ---")
old_end = s.index("    def build_context")
new = '''    # --- 混合检索：归一化加权融合（chunk 0.75 + 标题 0.25） ---
    @staticmethod
    def _norm(ranking):
        """把一路排名的分数做 min-max 归一化。"""
        if not ranking:
            return {}
        vals = [sc for _d, sc in ranking]
        mx, mn = max(vals), min(vals)
        rng = (mx - mn) or 1e-9
        return {d: (sc - mn) / rng for d, sc in ranking}

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

'''
s = s[:old_start] + new + s[old_end:]
open(p, "w", encoding="utf-8").write(s)
print("patched kbsearch.search -> weighted score fusion (alpha=0.75)")
