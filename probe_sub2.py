
import requests, re
from lxml import html as LH
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
s=requests.Session(); s.headers.update({"User-Agent":UA,"Accept-Language":"zh-CN,zh;q=0.9"})
def decode(r):
    raw=r.content; m=re.search(rb'charset=["\']?\s*([\w-]+)', raw[:3000], re.I)
    enc=(m.group(1).decode('ascii','ignore').lower() if m else 'utf-8')
    if enc in ('gb2312','gbk','gb18030'): enc='gb18030'
    for c in (enc,'utf-8','gb18030'):
        try: return raw.decode(c)
        except Exception: pass
    return raw.decode('utf-8','replace')
for u in ["https://zjc.fjsmu.edu.cn/2026/0624/c3328a183078/page.htm",
          "https://cwc.fjsmu.edu.cn/2026/1029/c848a186942/page.htm",
          "https://www.fjsmu.edu.cn/jwc/2026/1030/c1473a187007/page.htm"]:
    r=s.get(u,timeout=25); doc=LH.fromstring(decode(r))
    print("==",u, r.status_code, len(decode(r)))
    cands={}
    for d in doc.xpath('//div|//td|//article'):
        txt=(d.text_content() or "").strip()
        if len(txt) > 300:
            key=(d.tag, d.get("class") or d.get("id") or "")
            cands[key]=max(cands.get(key,0), len(txt))
    for k,v in sorted(cands.items(), key=lambda kv:-kv[1])[:6]:
        print("   ", k, v)
