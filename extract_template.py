# -*- coding: utf-8 -*-
import docx, io
p = r"D:\学年设计\开题报告.docx"
d = docx.Document(p)
buf = io.StringIO()
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph
body = d.element.body
def is_p(el): return el.tag == qn('w:p')
def is_t(el): return el.tag == qn('w:tbl')
ti = 0
for el in body:
    if is_p(el):
        par = Paragraph(el, d)
        t = par.text
        st = par.style.name
        # mark empty lines too
        buf.write(f"[{st}] {repr(t)}\n")
    elif is_t(el):
        tb = Table(el, d)
        rows = len(tb.rows); cols = len(tb.columns)
        buf.write(f"=== TABLE rows={rows} cols={cols} ===\n")
        for r in tb.rows:
            buf.write(" || ".join(c.text.replace("\n","⏎") for c in r.cells) + "\n")
        buf.write("=== /TABLE ===\n")
open(r"D:\学年设计\sumai\proposal_template.txt","w",encoding="utf-8").write(buf.getvalue())
print("ok", len(d.paragraphs), "paras,", len(d.tables), "tables")