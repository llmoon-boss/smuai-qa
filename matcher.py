import re

from db import db_conn


def _normalize(text):
    # 去除空白与中英文标点并转小写
    return re.sub(r"[\s，。！？、,.!?；;：:（）()《》\"'‘’“”]+", "", str(text)).lower()


def search_kb(question):
    #在 qa_pairs中检索最匹配的问答对
    q = _normalize(question)
    if not q:
        return None

    best, best_score = None, 0
    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, question, answer, keywords, category FROM qa_pairs")
            rows = cur.fetchall()

    for row in rows:
        score = 0
        # 规则 1：关键词命中
        for kw in re.split(r"[,，、\s]+", row["keywords"] or ""):
            if kw and _normalize(kw) in q:
                score += 1
        # 规则 2：问题文本互相包含（模糊匹配）
        qq = _normalize(row["question"])
        if qq and (q in qq or qq in q):
            score += 3
        if score > best_score:
            best, best_score = row, score
    return best if best_score >= 2 else None
