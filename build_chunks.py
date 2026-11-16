
import json, re, os, sys
SRC = r"D:\学年设计\sumai\kb_corpus.json"
OUT = r"D:\学年设计\sumai\kb_chunks.json"
MAXC, MINC, OVERLAP = 480, 120, 80

docs = json.load(open(SRC, encoding="utf-8"))
print("docs loaded:", len(docs))

CIT = re.compile(r"(第[一二三四五六七八九十百]+条|^[一二三四五六七八九十]+、|^（[一二三四五六七八九十]+）|^\d+[\.、])")

def split_long(text, maxc=MAXC, overlap=OVERLAP):
    if len(text) <= maxc:
        return [text]
    chunks, start = [], 0
    while start < len(text):
        end = min(start + maxc, len(text))
        if end < len(text):
            window = text[start:end]
            # prefer paragraph / sentence / clause boundaries in the last 120 chars
            for sep in ("\n", "。", "；", "，"):
                idx = window.rfind(sep, int(maxc * 0.6))
                if idx != -1:
                    end = start + idx + 1
                    break
        chunks.append(text[start:end].strip())
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return [c for c in chunks if c]

chunks = []
for d in docs:
    body = (d.get("body") or "").strip()
    if len(body) < MINC:
        continue
    title = d.get("title") or d.get("pageTitle") or ""
    for i, part in enumerate(split_long(body)):
        chunks.append({
            "id": "c%d" % len(chunks),
            "docId": d["url"],
            "column": d.get("column", ""),
            "title": title,
            "date": d.get("date", ""),
            "wenhao": d.get("wenhao", ""),
            "chunkIndex": i,
            "len": len(part),
            "text": ("【%s】%s\n%s" % (d.get("column", ""), title, part)) if i == 0 else part,
        })

json.dump(chunks, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
lens = [c["len"] for c in chunks]
print("docs used:", len({c['docId'] for c in chunks}))
print("chunks:", len(chunks), "avg len:", int(sum(lens)/len(lens)), "max:", max(lens))
print("total chars:", sum(lens))
from collections import Counter
print("by column:", Counter(c["column"] for c in chunks).most_common())
