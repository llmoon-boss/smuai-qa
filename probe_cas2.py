
import requests, re
from lxml import html as LH
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
s=requests.Session(); s.headers.update({"User-Agent":UA,"Accept-Language":"zh-CN,zh;q=0.9"})
r=s.get("https://tpass.fjsmu.edu.cn/cas/login?service=https%3A%2F%2Fwww.smxy.cn%2Fjwc%2F2024%2F1111%2Fc1379a160806%2Fpage.psp", timeout=25)
doc=LH.fromstring(r.text)
print("TEXT:", re.sub(r"\s+"," ", doc.text_content())[:1200])
print("\nSCRIPTS:", [ (s0.get("src") or (s0.text or "")[:80]) for s0 in doc.xpath('//script')][:6])
