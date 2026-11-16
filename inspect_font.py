
from docx import Document
from docx.oxml.ns import qn
doc = Document(r"D:\学年设计\SMUAI毕业设计项目设计报告.docx")
# inspect fonts of a heading1, heading2, and normal paragraph
def dump_font(p, label):
    print(f"--- {label}: style={p.style.name}")
    for r in p.runs[:2]:
        rf = r.font
        rPr = r._r.rPr
        ea = None
        if rPr is not None:
            rf_el = rPr.find(qn('w:rFonts'))
            if rf_el is not None:
                ea = rf_el.get(qn('w:eastAsia'))
                print(f"  run '{r.text[:20]}' font.name={rf.name} eastAsia={ea} size={rf.size} bold={rf.bold}")
for i,p in enumerate(doc.paragraphs):
    if p.style.name == 'Heading 1' and '项目开发背景' in p.text:
        dump_font(p,'H1'); break
for i,p in enumerate(doc.paragraphs):
    if p.style.name == 'Heading 2' and p.text.startswith('1.2'):
        dump_font(p,'H2'); break
for i,p in enumerate(doc.paragraphs):
    if p.style.name == 'Normal' and len(p.text) > 50:
        dump_font(p,'Normal'); break
# also check default style font
st = doc.styles['Normal']
print('Normal style font:', st.font.name)
rpr = st.element.find(qn('w:rPr'))
if rpr is not None:
    rf = rpr.find(qn('w:rFonts'))
    if rf is not None:
        print('  Normal style eastAsia:', rf.get(qn('w:eastAsia')), ' ascii:', rf.get(qn('w:ascii')))
