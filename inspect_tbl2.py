# -*- coding: utf-8 -*-
import docx, io
from lxml import etree
p = r"D:\学年设计\开题报告.docx"
d = docx.Document(p)
tb = d.tables[0]
buf = io.StringIO()
# dump each row: cell count, gridSpan info, and for each cell first paragraph style/font
from docx.oxml.ns import qn
for ri, row in enumerate(tb.rows):
    buf.write(f"===== ROW {ri} ({len(row.cells)} cells) =====\n")
    # unique cells by tc element
    seen = set()
    for tc in row._tr.findall(qn('w:tc')):
        tcPr = tc.find(qn('w:tcPr'))
        gs = tcPr.find(qn('w:gridSpan')) if tcPr is not None else None
        vm = tcPr.find(qn('w:vMerge')) if tcPr is not None else None
        gsval = gs.get(qn('w:val')) if gs is not None else '1'
        vmval = 'merge' if vm is None else (vm.get(qn('w:val')) or 'continue')
        # paragraphs in this tc
        paras = tc.findall(qn('w:p'))
        ptexts = []
        for pp in paras:
            txt = ''.join(t.text or '' for t in pp.findall('.//'+qn('w:t')))
            ptexts.append(txt[:30])
        buf.write(f"  tc gridSpan={gsval} vMerge={vmval} paras={len(paras)} first={ptexts[:2]}\n")
open(r"D:\学年设计\sumai\tbl_xml.txt","w",encoding="utf-8").write(buf.getvalue())
print("ok")