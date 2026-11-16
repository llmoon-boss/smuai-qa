
import requests, re
from lxml import html as LH
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
s=requests.Session(); s.headers.update({"User-Agent":UA,"Accept-Language":"zh-CN,zh;q=0.9"})
r=s.get("https://tpass.fjsmu.edu.cn/cas/login?service=https%3A%2F%2Fwww.smxy.cn%2Fjwc%2F2024%2F1111%2Fc1379a160806%2Fpage.psp", timeout=25)
print("status", r.status_code, "len", len(r.text))
t=r.text
doc=LH.fromstring(t)
for f in doc.xpath('//form'):
    print("FORM", f.get("action"), f.get("method"), "id=", f.get("id"))
    for i in f.xpath('.//input'):
        print("   input name=%s id=%s type=%s value=%s" % (i.get("name"), i.get("id"), i.get("type"), (i.get("value") or "")[:40]))
print("captcha words:", [w for w in ("captcha","kaptcha","verifyCode","验证码") if w.lower() in t.lower()])
m=re.search(r'<title>(.*?)</title>', t, re.S); print("title:", m.group(1).strip() if m else "")
