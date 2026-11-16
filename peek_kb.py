
import json
d = json.load(open(r"D:\学年设计\sumai\kb_sample.json", encoding="utf-8"))
print(type(d), len(d))
if isinstance(d, dict): print(list(d.keys())[:10])
items = d if isinstance(d, list) else d.get("items") or d.get("docs") or []
print("items", len(items))
if items: print(json.dumps(items[0], ensure_ascii=False)[:600])
for it in items:
    if isinstance(it, dict):
        print("-", it.get("url"), "|len", len(it.get("text") or it.get("content") or ""), "|", (it.get("title") or "")[:40])
