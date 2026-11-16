
import sys
from docx import Document
doc = Document(r"D:\学年设计\SMUAI毕业设计项目设计报告.docx")
out = []
for i, p in enumerate(doc.paragraphs):
    t = p.text.strip()
    if t:
        out.append(f"[P{i}] ({p.style.name}) {t}")
out.append("")
for ti, tb in enumerate(doc.tables):
    out.append(f"=== TABLE {ti} ===")
    for row in tb.rows:
        cells = [c.text.strip().replace('\n',' / ') for c in row.cells]
        out.append(" | ".join(cells))
open(r"D:\学年设计\sumai\docx_text.txt", "w", encoding="utf-8").write("\n".join(out))
print("ok", len(out))
