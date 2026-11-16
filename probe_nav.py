
import requests, re
from urllib.parse import urljoin
from lxml import html as LH
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
s = requests.Session(); s.headers.update({"User-Agent": UA, "Accept-Language":"zh-CN,zh;q=0.9"})
def decode(r):
    raw=r.content; m=re.search(rb'charset=["\']?\s*([\w-]+)', raw[:3000], re.I)
    enc=(m.group(1).decode('ascii','ignore').lower() if m else 'utf-8')
    if enc in ('gb2312','gbk','gb18030'): enc='gb18030'
    for c in (enc,'utf-8','gb18030'):
        try: return raw.decode(c)
        except Exception: pass
    return raw.decode('utf-8','replace')

for site in ["https://www.smxy.cn/jwc/", "https://www.smxy.cn/"]:
    r = s.get(site, timeout=20); doc = LH.fromstring(decode(r))
    print("=====", site, r.status_code, len(decode(r)))
    seen=set()
    for a in doc.xpath('//a[@href]'):
        t=(a.text_content() or '').strip(); h=(a.get('href') or '').strip()
        if not t or not h or len(t)>12: continue
        if h.startswith('#') or h.startswith('javascript'): continue
        full=urljoin(site,h)
        if full in seen: continue
        if re.search(r'/(list|index)[\w]*\.htm$', full) or full.rstrip('/').endswith(site.rstrip('/')):
            seen.add(full); print("  ", t, "->", full)
