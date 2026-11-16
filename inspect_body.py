
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
doc = Document(r"D:\学年设计\SMUAI毕业设计项目设计报告.docx")
body = doc.element.body
out = []
for i, child in enumerate(body.iterchildren()):
    tag = child.tag.split('}')[-1]
    if tag == 'p':
        p = Paragraph(child, doc)
        style = p.style.name if p.style else ''
        txt = p.text.strip()
        out.append(f"#{i} <p> style={style} text={txt[:40]}")
    elif tag == 'tbl':
        out.append(f"#{i} <tbl>")
    else:
        out.append(f"#{i} <{tag}>")
open(r"D:\学年设计\sumai\docx_body.txt","w",encoding="utf-8").write("\n".join(out))
print("ok")
