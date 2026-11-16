
import ctypes, base64, json, sqlite3, shutil, os, tempfile
from ctypes import wintypes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ROAM = r"C:\Users\刘亮\AppData\Roaming\@deepseek-ai\dsh-desktop"
PART = os.path.join(ROAM, "Partitions", "dsh-platform-57b2c69601e4be422397b72dbe780ff4274f790994882e876f74db4432fccb6a")
COOKIES = os.path.join(PART, "Network", "Cookies")

class DATA_BLOB(ctypes.Structure):
    _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_char))]

def dpapi_unprotect(data):
    buf = ctypes.create_string_buffer(data, len(data))
    blobin = DATA_BLOB(len(data), ctypes.cast(buf, ctypes.POINTER(ctypes.c_char)))
    blobout = DATA_BLOB()
    ok = ctypes.windll.crypt32.CryptUnprotectData(ctypes.byref(blobin), None, None, None, None, 0, ctypes.byref(blobout))
    if not ok:
        raise OSError("CryptUnprotectData failed: %d" % ctypes.get_last_error())
    n = blobout.cbData
    out = ctypes.create_string_buffer(n)
    ctypes.memmove(out, blobout.pbData, n)
    ctypes.windll.kernel32.LocalFree(blobout.pbData)
    return out.raw[:n]

ls = json.load(open(os.path.join(ROAM, "Local State"), encoding="utf-8"))
enc_key = base64.b64decode(ls["os_crypt"]["encrypted_key"])
assert enc_key[:5] == b"DPAPI", enc_key[:5]
key = dpapi_unprotect(enc_key[5:])
print("master key len:", len(key))

tmp = os.path.join(tempfile.gettempdir(), "dsh_cookies.db")
shutil.copy2(COOKIES, tmp)
for suf in ("-wal", "-shm"):
    if os.path.exists(COOKIES + suf):
        shutil.copy2(COOKIES + suf, tmp + suf)
con = sqlite3.connect(tmp)
rows = con.execute("SELECT host_key, name, value, encrypted_value, path, expires_utc, is_secure, is_httponly FROM cookies").fetchall()
print("total cookies:", len(rows))
aes = AESGCM(key)
def dec(val):
    if not val:
        return ""
    if val[:3] in (b"v10", b"v11"):
        return aes.decrypt(val[3:15], val[15:], None).decode("utf-8", "replace")
    if val[:3] == b"v20":
        return "<<v20-appbound>>"
    return val.decode("utf-8", "replace")

out = []
for host, name, value, enc, path, exp, sec, httponly in rows:
    try:
        v = dec(enc) if (enc and not value) else value
    except Exception as e:
        v = "<<ERR %s>>" % type(e).__name__
    out.append({"domain": host, "name": name, "value": v, "path": path, "secure": sec})
    if "fjsmu" in host or "smxy" in host:
        print("HOST", host, "|", name, "|", (v[:40] + "...") if len(v) > 40 else v)
print("hosts:", sorted({o["domain"] for o in out})[:40])
json.dump(out, open(r"D:\学年设计\sumai\kb_cookies.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved")
