
import json, re
docs = json.load(open(r"D:\学年设计\sumai\kb_docs.json", encoding="utf-8"))
def show(kw, n=6):
    hits = [(d["title"], d["body"].count(kw)) for d in docs if kw in d["body"]]
    hits.sort(key=lambda x: -x[1])
    print("\n[body 含 %s] %d 篇" % (kw, len(hits)))
    for t, c in hits[:n]:
        print("   %3d次  %s" % (c, t[:46]))
for kw in ["毕业设计", "调课", "停课", "教学信息员"]:
    show(kw)
