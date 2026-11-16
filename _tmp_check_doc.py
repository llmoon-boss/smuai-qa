import os

HERE = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(os.path.dirname(HERE), "SMUAI学年设计论文.doc")
print("path:", path, "exists:", os.path.exists(path))

with open(path, "rb") as f:
    head = f.read(16)
print("sig:", head[:8].hex(" "))
print("bytes:", head)

if head[:4] == b"PK\x03\x04":
    print("=> ZIP 容器（可能是 docx 或 odt）")
    import zipfile

    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        print("entries:", len(names))
        for n in names[:30]:
            print(" ", n)
elif head[:4] == b"\xd0\xcf\x11\xe0":
    print("=> OLE2 复合文档（Word 97-2003 .doc 或同名格式）")
elif head[:5] == b"{\\rtf":
    print("=> RTF")
else:
    print("=> 未知格式")
