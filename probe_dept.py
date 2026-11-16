
import requests, re
from urllib.parse import urljoin, urlparse
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
r=s.get("https://www.smxy.cn/zzjg/list.htm", timeout=25)
print("status", r.status_code)
doc=LH.fromstring(decode(r))
hosts={}
for a in doc.xpath('//a[@href]'):
    t=(a.text_content() or '').strip(); h=(a.get('href') or '').strip()
    if not h or h.startswith('#') or h.startswith('javascript'): continue
    full=urljoin("https://www.smxy.cn/zzjg/list.htm", h)
    host=urlparse(full).netloc
    if host and host not in ('www.smxy.cn','smxy.cn'):
        hosts.setdefault(host, []).append((t, full))
for host, items in hosts.items():
    print("==", host, len(items))
    for t,f in items[:4]:
        print("   ", t, f)
