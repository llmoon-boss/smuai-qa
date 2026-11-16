
from docx import Document
from docx.oxml.ns import qn
doc = Document(r"D:\学年设计\SMUAI毕业设计项目设计报告.docx")
lines = []
def ea_of(style):
    el = style.element
    rpr = el.find(qn('w:rPr'))
    if rpr is not None:
        rf = rpr.find(qn('w:rFonts'))
        if rf is not None:
            return (rf.get(qn('w:eastAsia')), rf.get(qn('w:ascii')))
    return None
for sn in ['Normal','Heading 1','Heading 2','Heading 3','Title']:
    try:
        st = doc.styles[sn]
        lines.append(f"{sn}: font={st.font.name} eastAsia={ea_of(st)}")
    except Exception as e:
        lines.append(f"{sn}: MISSING {e}")
open(r"D:\学年设计\sumai\fonts.txt","w",encoding="utf-8").write("\n".join(lines))
print("ok")
