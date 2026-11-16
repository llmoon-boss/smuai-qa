# -*- coding: utf-8 -*-
import docx, io
from lxml import etree
p = r"D:\学年设计\开题报告.docx"
d = docx.Document(p)
tb = d.tables[0]
buf = io.StringIO()
from docx.oxml.ns import qn
row = tb.rows[3]
tc = row._tr.find(qn('w:tc'))
buf.write(etree.tostring(tc, pretty_print=True, encoding='unicode'))
open(r"D:\学年设计\sumai\tbl_row3.xml","w",encoding="utf-8").write(buf.getvalue())
# also dump the title row (row2) and header info row (row1)
buf2 = io.StringIO()
buf2.write("=== ROW1 (info fill) ===\n")
for tc in tb.rows[1]._tr.findall(qn('w:tc')):
    buf2.write(etree.tostring(tc, pretty_print=True, encoding='unicode') + "\n")
buf2.write("=== ROW2 (title) ===\n")
for tc in tb.rows[2]._tr.findall(qn('w:tc')):
    buf2.write(etree.tostring(tc, pretty_print=True, encoding='unicode') + "\n")
open(r"D:\学年设计\sumai\tbl_row12.xml","w",encoding="utf-8").write(buf2.getvalue())
print("ok")