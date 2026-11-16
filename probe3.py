
import requests, re
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
s = requests.Session(); s.headers.update({"User-Agent": UA, "Accept-Language":"zh-CN,zh;q=0.9"})
r = s.get("https://www.smxy.cn/jwc/gzzd/list.htm", timeout=20)
raw = r.content
print("len", len(raw))
m = re.search(rb'charset=["\']?\s*([\w-]+)', raw[:2000], re.I); print("charset", m.group(1) if m else None)
t = raw.decode("gb18030", "replace")
idx = t.find("page.htm")
print("first page.htm at", idx)
print(t[max(0,idx-1500):idx+500])
