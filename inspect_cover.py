# -*- coding: utf-8 -*-
import docx, io
from lxml import etree
p = r"D:\学年设计\开题报告.docx"
d = docx.Document(p)
buf = io.StringIO()
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph
body = d.element.body
for i, el in enumerate(body):
    if el.tag == qn('w:p'):
        par = Paragraph(el, d)
        t = par.text
        if t.strip():
            buf.write(f"=== PARA {i}: {repr(t[:40])} ===\n")
            buf.write(etree.tostring(el, pretty_print=True, encoding='unicode')[:2000] + "\n\n")
open(r"D:\学年设计\sumai\cover_xml.txt","w",encoding="utf-8").write(buf.getvalue())
print("ok")