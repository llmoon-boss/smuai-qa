
import json
from collections import Counter
docs = json.load(open(r"D:\学年设计\sumai\kb_corpus.json", encoding="utf-8"))
ok = [d for d in docs if d.get("length",0) > 200]
print("ok docs", len(ok))
# duplicates by normalized title
t = Counter((d.get("title") or "").strip() for d in ok)
print("dup titles:", [(k, v) for k, v in t.most_common(8)])
for col in ["教务处-教学改革", "教务处-教材建设", "教务处-考试管理"]:
    sub = [d for d in ok if d["column"] == col]
    print("\n==", col, len(sub), "docs, avg len", int(sum(d["length"] for d in sub)/max(1,len(sub))))
    for d in sorted(sub, key=lambda x: -x["length"])[:4]:
        print("   %5d %s | %s" % (d["length"], d["title"][:34], d["body"][:80].replace("\n"," ")))
print("\nGATED sample:")
for d in [x for x in docs if x.get("gated")][:6]:
    print("  ", d["column"], d["title"][:40])
print("\nSHORT sample:")
for d in [x for x in ok if False][:1]: pass
short = [d for d in docs if not d.get("gated") and d.get("length",0) <= 200]
for d in short[:6]:
    print("  ", d["column"], d["title"][:36], "len", d.get("length"))
