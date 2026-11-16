
import sqlite3, os, json, base64, ctypes
from urllib.parse import quote
from ctypes import wintypes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ROAM = r"C:\Users\刘亮\AppData\Roaming\@deepseek-ai\dsh-desktop"
COOKIES = os.path.join(ROAM, "Network", "Cookies")
uri = "file:" + quote(COOKIES.replace("\\", "/")) + "?immutable=1"
con = sqlite3.connect(uri, uri=True, timeout=5)
rows = con.execute("select host_key,name,value,encrypted_value,path from cookies").fetchall()
print("rows:", len(rows))
from collections import Counter
for h, n in Counter([r[0] for r in rows]).most_common(40):
    print("HOSTN", h, n)

class DATA_BLOB(ctypes.Structure):
    _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_char))]
def dpapi_unprotect(data):
    buf = ctypes.create_string_buffer(data, len(data))
    bi = DATA_BLOB(len(data), ctypes.cast(buf, ctypes.POINTER(ctypes.c_char)))
    bo = DATA_BLOB()
    if not ctypes.windll.crypt32.CryptUnprotectData(ctypes.byref(bi), None, None, None, None, 0, ctypes.byref(bo)):
        raise OSError("dpapi fail %d" % ctypes.get_last_error())
    n = bo.cbData; out = ctypes.create_string_buffer(n)
    ctypes.memmove(out, bo.pbData, n); ctypes.windll.kernel32.LocalFree(bo.pbData)
    return out.raw[:n]

ls = json.load(open(os.path.join(ROAM, "Local State"), encoding="utf-8"))
key = dpapi_unprotect(base64.b64decode(ls["os_crypt"]["encrypted_key"])[5:])
aes = AESGCM(key)
def dec(v):
    if not v: return ""
    if v[:3] in (b"v10", b"v11"): return aes.decrypt(v[3:15], v[15:], None).decode("utf-8","replace")
    if v[:3] == b"v20": return "<<v20>>"
    return v.decode("utf-8","replace")

out=[]
for host,name,value,enc,path in rows:
    try: v = dec(enc) if (enc and not value) else value
    except Exception as e: v = "<<ERR %s>>" % type(e).__name__
    out.append({"domain":host,"name":name,"value":v,"path":path})
    if "fjsmu" in host:
        print("CK", host, name, "=", (v[:60]+"...") if len(v)>60 else v)
json.dump(out, open(r"D:\学年设计\sumai\kb_cookies.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved total", len(out))
