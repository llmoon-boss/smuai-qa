
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
for name,url in [("学校简介","https://www.smxy.cn/xxjj/list.htm"),
                 ("学校章程","https://www.smxy.cn/xxzc/list.htm"),
                 ("校园导航","https://www.smxy.cn/xydh/list.htm"),
                 ("校史沿革","https://www.smxy.cn/xsyg/list.htm"),
                 ("部门简介","https://www.smxy.cn/jwc/bmjj/list.htm")]:
    r=s.get(url,timeout=25); doc=LH.fromstring(decode(r))
    nodes=doc.xpath('//div[contains(@class,"wp_articlecontent")]')
    body = "\n".join(nodes[0].text_content().split()) if nodes else ""
    classes = doc.xpath('//div[@class]/@class')
    print(name, r.status_code, "| wp_article:", bool(nodes), "len:", len(body))
    if not nodes:
        cands = [c for c in classes if any(k in c for k in ("content","article","detail","main"))]
        print("   candidate divs:", list(dict.fromkeys(cands))[:8])
        # try largest text div
        best = ("", "")
        for d in doc.xpath('//div'):
            txt = (d.text_content() or "").strip()
            if len(txt) > len(best[1]):
                best = (d.get("class") or d.get("id") or "", txt)
        print("   largest div:", best[0], "len", len(best[1]), "|", best[1][:80].replace("\n"," "))
