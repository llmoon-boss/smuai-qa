# -*- coding: utf-8 -*-
import docx, io
p = r"D:\学年设计\开题报告.docx"
d = docx.Document(p)
buf = io.StringIO()
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph
body = d.element.body
paras = [Paragraph(el, d) for el in body if el.tag == qn('w:p')]
for i in [3,4,5,6,8,16]:
    par = paras[i]
    buf.write(f"--- PARA {i} style={par.style.name} align={par.alignment} ---\n")
    for r in par.runs:
        u = r.underline
        buf.write(f"  run underline={u} text={repr(r.text)}\n")
open(r"D:\学年设计\sumai\cover_runs.txt","w",encoding="utf-8").write(buf.getvalue())
print("ok")