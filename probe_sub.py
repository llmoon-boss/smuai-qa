
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
for u in ["https://zjc.fjsmu.edu.cn/main.htm","https://cwc.fjsmu.edu.cn/","https://www.fjsmu.edu.cn/jwc/"]:
    try:
        r=s.get(u,timeout=25); doc=LH.fromstring(decode(r))
        wp=doc.xpath('//div[contains(@class,"wp_articlecontent")]')
        title=doc.xpath('string(//title)').strip()
        links=[a.get('href') for a in doc.xpath('//a[@href]') if 'page.htm' in (a.get('href') or '')][:3]
        print(u, r.status_code, "|", title[:30], "| wp_article:", bool(wp), "| sample links:", links)
    except Exception as e:
        print(u, "ERR", e)
