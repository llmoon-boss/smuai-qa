# -*- coding: utf-8 -*-
import docx, io, zipfile, re
p = r"D:\学年设计\开题报告.docx"
z = zipfile.ZipFile(p)
st = z.read("word/styles.xml").decode("utf-8")
buf = io.StringIO()
# find style with w:styleId="3"
m = re.search(r'<w:style [^>]*w:styleId="3"[^>]*>.*?</w:style>', st, re.S)
buf.write("styleId=3: " + (m.group(0) if m else "NOT FOUND") + "\n\n")
# also list default and any styles referencing 仿宋
open(r"D:\学年设计\sumai\style3.txt","w",encoding="utf-8").write(buf.getvalue())
# check document defaults
m2 = re.search(r'<w:docDefaults>.*?</w:docDefaults>', st, re.S)
open(r"D:\学年设计\sumai\docdefaults.txt","w",encoding="utf-8").write(m2.group(0) if m2 else "none")
print("ok")