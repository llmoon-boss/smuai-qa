
from docx import Document
doc = Document(r"D:\学年设计\SMUAI毕业设计项目设计报告.docx")
lines = []
for i, tb in enumerate(doc.tables):
    lines.append(f"table{i} style={tb.style.name if tb.style else None} rows={len(tb.rows)} cols={len(tb.columns)}")
    # header row font
    if tb.rows:
        c = tb.rows[0].cells[0]
        for p in c.paragraphs[:1]:
            for r in p.runs[:1]:
                lines.append(f"  hdr run font={r.font.name} size={r.font.size} bold={r.font.bold}")
open(r"D:\学年设计\sumai\tblstyle.txt","w",encoding="utf-8").write("\n".join(lines))
print("ok")
