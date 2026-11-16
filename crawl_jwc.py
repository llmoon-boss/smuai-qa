
import requests, re, json, time
from urllib.parse import urljoin
from lxml import html as LH

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
BASE = "https://www.smxy.cn/jwc/gzzd/"
s = requests.Session()
s.headers.update({"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                  "Accept-Language": "zh-CN,zh;q=0.9"})

def decode(resp):
    raw = resp.content
    m = re.search(rb'charset=["\']?\s*([\w-]+)', raw[:3000], re.I)
    enc = (m.group(1).decode("ascii", "ignore").lower() if m else "utf-8")
    if enc in ("gb2312", "gbk", "gb18030"): enc = "gb18030"
    for cand in (enc, "utf-8", "gb18030"):
        try: return raw.decode(cand)
        except Exception: pass
    return raw.decode("utf-8", "replace")

def list_entries():
    entries, seen = [], set()
    for idx in range(1, 9):
        url = urljoin(BASE, "list.htm" if idx == 1 else "list%d.htm" % idx)
        try: r = s.get(url, timeout=20)
        except Exception as e:
            print("LIST ERR", url, e); break
        if r.status_code != 200: break
        doc = LH.fromstring(decode(r))
        links = doc.xpath('//table[contains(@class,"wp_article_list_table")]//a[@href]')
        if not links: links = [a for a in doc.xpath('//a[@href]') if "page.htm" in (a.get("href") or "")]
        got = 0
        for a in links:
            href = a.get("href") or ""; title = (a.text_content() or "").strip()
            if "page.htm" not in href or not title: continue
            full = urljoin(url, href)
            if full in seen: continue
            seen.add(full)
            row = a.xpath('ancestor::tr[1]')
            date = ""
            if row:
                m = re.search(r"\d{4}-\d{2}-\d{2}", row[0].text_content())
                date = m.group(0) if m else ""
            entries.append({"title": title, "url": full, "date": date})
            got += 1
        print("list", idx, "+", got, "total", len(entries))
        if got == 0: break
        time.sleep(0.2)
    return entries

def body_text(doc):
    nodes = doc.xpath('//div[contains(@class,"wp_articlecontent")]')
    if not nodes: return "", []
    body = "\n".join(p.strip() for p in nodes[0].text_content().split("\n") if p.strip())
    atts = [a.get("href") for a in nodes[0].xpath('.//a[@href]') if re.search(r"\.(pdf|docx?|xlsx?|zip|rar)$", a.get("href"), re.I)]
    return body, atts

def fetch(url):
    r = s.get(url, timeout=25)
    if "tpass.fjsmu.edu.cn" in r.url:
        return {"gated": True, "status": r.status_code}
    t = decode(r); doc = LH.fromstring(t)
    body, atts = body_text(doc)
    wenhao = ""
    m = re.search(r"[\u4e00-\u9fa5]{2,8}〔\d{4}〕\d+号", body[:400])
    if m: wenhao = m.group(0)
    return {"status": r.status_code, "title": doc.xpath('string(//title)').strip(),
            "body": body, "len": len(body), "wenhao": wenhao, "attachments": atts}

entries = list_entries()
out = []
for i, e in enumerate(entries, 1):
    try: info = fetch(e["url"])
    except Exception as ex: info = {"error": str(ex)[:100]}
    info.update(e)
    out.append(info)
    print("%2d/%d %-8s %s" % (i, len(entries), ("GATED" if info.get("gated") else "OK %d" % info.get("len",0)), e["title"][:34]))
    time.sleep(0.25)

json.dump(out, open(r"D:\学年设计\sumai\kb_crawl.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
ok = [o for o in out if o.get("len", 0) > 200]
print("TOTAL", len(out), "OK", len(ok), "GATED", sum(1 for o in out if o.get("gated")))
print("avg len", int(sum(o.get("len",0) for o in ok)/max(1,len(ok))))
