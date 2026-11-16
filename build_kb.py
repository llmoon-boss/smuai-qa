
import json, re, hashlib, os
SRC = r"D:\学年设计\sumai\kb_corpus.json"
DOCS = r"D:\学年设计\sumai\kb_docs.json"
CHUNKS = r"D:\学年设计\sumai\kb_chunks.json"
MAXC, MINC, OVERLAP = 480, 120, 80

PRIORITY = ["教务处-规章制度", "教务处-教务管理", "教务处-课务管理", "教务处-学务管理",
            "教务处-考试管理", "教务处-服务指南", "教务处-实验实践", "教务处-质量监控"]

def norm_title(t):
    return re.sub(r"[\s\u3000（）()《》\-\—\.,，。：:、]", "", t or "")

def sig(d):
    body = re.sub(r"\s+", "", d.get("body") or "")
    return hashlib.md5((norm_title(d.get("title")) + "|" + body[:300] + "|" + str(len(body))).encode()).hexdigest()

raw = json.load(open(SRC, encoding="utf-8"))
docs, seen, dropped = [], {}, {"gated": 0, "short": 0, "dup": 0}
for d in raw:
    if d.get("gated"):
        dropped["gated"] += 1; continue
    if d.get("length", 0) < MINC:
        dropped["short"] += 1; continue
    s = sig(d)
    if s in seen:
        dropped["dup"] += 1
        continue
    seen[s] = d
    docs.append({
        "docId": d["url"], "column": d["column"], "title": (d.get("title") or "").strip(),
        "date": d.get("date", ""), "wenhao": d.get("wenhao", ""),
        "length": d["length"], "body": d["body"], "attachments": d.get("attachments", []),
    })

docs.sort(key=lambda d: (PRIORITY.index(d["column"]) if d["column"] in PRIORITY else 99, d["title"]))
json.dump(docs, open(DOCS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("docs kept:", len(docs), "dropped:", dropped)

def split_long(text):
    if len(text) <= MAXC: return [text]
    out, start = [], 0
    while start < len(text):
        end = min(start + MAXC, len(text))
        if end < len(text):
            w = text[start:end]
            for sep in ("\n", "。", "；", "，"):
                i = w.rfind(sep, int(MAXC * 0.6))
                if i != -1:
                    end = start + i + 1; break
        out.append(text[start:end].strip())
        if end >= len(text): break
        start = max(end - OVERLAP, start + 1)
    return [c for c in out if c]

chunks = []
for d in docs:
    for i, part in enumerate(split_long(d["body"].strip())):
        chunks.append({"id": "c%d" % len(chunks), "docId": d["docId"], "column": d["column"],
                       "title": d["title"], "date": d["date"], "wenhao": d["wenhao"],
                       "chunkIndex": i, "nChunks": 0, "len": len(part), "text": part})
for c in chunks:
    pass
cnt = {}
for c in chunks:
    cnt[c["docId"]] = cnt.get(c["docId"], 0) + 1
for c in chunks:
    c["nChunks"] = cnt[c["docId"]]
json.dump(chunks, open(CHUNKS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
lens = [c["len"] for c in chunks]
print("chunks:", len(chunks), "avg", int(sum(lens)/len(lens)), "chars", sum(lens))
from collections import Counter
print("by column:", Counter(c["column"] for c in chunks).most_common())
