
import requests, re, json, time, os, sys
from urllib.parse import urljoin
from lxml import html as LH

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
OUT = r"D:\学年设计\sumai\kb_corpus.json"
PROG = r"D:\学年设计\sumai\kb_crawl_progress.log"
s = requests.Session()
s.headers.update({"User-Agent": UA,
                  "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                  "Accept-Language": "zh-CN,zh;q=0.9"})

COLUMNS = [
    ("教务处-规章制度", "https://www.smxy.cn/jwc/gzzd/list.htm"),
    ("教务处-教务管理", "https://www.smxy.cn/jwc/jwgl/list.htm"),
    ("教务处-课务管理", "https://www.smxy.cn/jwc/kwgl/list.htm"),
    ("教务处-学务管理", "https://www.smxy.cn/jwc/xwgl/list.htm"),
    ("教务处-考试管理", "https://www.smxy.cn/jwc/ksgl/list.htm"),
    ("教务处-实验实践", "https://www.smxy.cn/jwc/sysj/list.htm"),
    ("教务处-质量监控", "https://www.smxy.cn/jwc/zljk/list.htm"),
    ("教务处-教学改革", "https://www.smxy.cn/jwc/jxtz/list.htm"),
    ("教务处-教材建设", "https://www.smxy.cn/jwc/xkjs/list.htm"),
    ("教务处-服务指南", "https://www.smxy.cn/jwc/fwzn/list.htm"),
    ("教务处-信息公开", "https://www.smxy.cn/jwc/xxgk/list.htm"),
    ("教务处-工作动态", "https://www.smxy.cn/jwc/gzdt/list.htm"),
    ("教务处-部门简介", "https://www.smxy.cn/jwc/bmjj/list.htm"),
    ("教务处-机构设置", "https://www.smxy.cn/jwc/jgsz/list.htm"),
    ("学校-学校简介", "https://www.smxy.cn/xxjj/list.htm"),
    ("学校-学校章程", "https://www.smxy.cn/xxzc/list.htm"),
    ("学校-校园导航", "https://www.smxy.cn/xydh/list.htm"),
    ("学校-现任领导", "https://www.smxy.cn/xrld/list.htm"),
    ("学校-组织机构", "https://www.smxy.cn/zzjg/list.htm"),
    ("学校-校史沿革", "https://www.smxy.cn/xsyg/list.htm"),
]

def log(msg):
    line = time.strftime("%H:%M:%S ") + msg
    print(line, flush=True)
    with open(PROG, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def decode(resp):
    raw = resp.content
    m = re.search(rb'charset=["\']?\s*([\w-]+)', raw[:3000], re.I)
    enc = (m.group(1).decode("ascii", "ignore").lower() if m else "utf-8")
    if enc in ("gb2312", "gbk", "gb18030"):
        enc = "gb18030"
    for c in (enc, "utf-8", "gb18030"):
        try:
            return raw.decode(c)
        except Exception:
            pass
    return raw.decode("utf-8", "replace")

def list_entries(column_name, list_url):
    entries, seen = [], set()
    base = list_url.rsplit("/", 1)[0] + "/"
    for idx in range(1, 7):
        url = urljoin(base, "list.htm" if idx == 1 else "list%d.htm" % idx)
        try:
            r = s.get(url, timeout=25)
        except Exception as e:
            log("LIST ERR %s %s" % (url, e)); break
        if r.status_code != 200:
            break
        doc = LH.fromstring(decode(r))
        links = doc.xpath('//table[contains(@class,"wp_article_list_table")]//a[@href]')
        if not links:
            links = [a for a in doc.xpath('//a[@href]') if "page.htm" in (a.get("href") or "")]
        got = 0
        for a in links:
            href = a.get("href") or ""
            title = (a.text_content() or "").strip()
            if "page.htm" not in href or not title:
                continue
            full = urljoin(url, href)
            if full in seen:
                continue
            seen.add(full)
            row = a.xpath("ancestor::tr[1]")
            date = ""
            if row:
                m = re.search(r"\d{4}-\d{2}-\d{2}", row[0].text_content())
                date = m.group(0) if m else ""
            entries.append({"column": column_name, "title": title, "url": full, "date": date})
            got += 1
        if got == 0:
            break
        time.sleep(0.2)
    return entries

def extract(doc):
    nodes = doc.xpath('//div[contains(@class,"wp_articlecontent")]')
    body, atts = "", []
    if nodes:
        body = "\n".join(p.strip() for p in nodes[0].text_content().split("\n") if p.strip())
        atts = [a.get("href") for a in nodes[0].xpath(".//a[@href]")
                if re.search(r"\.(pdf|docx?|xlsx?|zip|rar)$", a.get("href"), re.I)]
    return body, atts

def fetch(e):
    r = s.get(e["url"], timeout=30)
    if "tpass.fjsmu.edu.cn" in r.url:
        return dict(e, gated=True, body="", length=0)
    doc = LH.fromstring(decode(r))
    body, atts = extract(doc)
    wenhao = ""
    m = re.search(r"[\u4e00-\u9fa5]{2,10}〔\d{4}〕\d+号", body[:400])
    if m:
        wenhao = m.group(0)
    return dict(e, gated=False, pageTitle=doc.xpath("string(//title)").strip(),
                body=body, length=len(body), wenhao=wenhao, attachments=atts)

existing = {}
if os.path.exists(OUT):
    for d in json.load(open(OUT, encoding="utf-8")):
        existing[d["url"]] = d
log("start, existing docs=%d" % len(existing))

queue = []
for cname, curl in COLUMNS:
    try:
        es = list_entries(cname, curl)
    except Exception as ex:
        log("COL ERR %s %s" % (cname, ex)); continue
    new = [e for e in es if e["url"] not in existing]
    log("column %s: entries=%d new=%d" % (cname, len(es), len(new)))
    queue.extend(new)

docs = list(existing.values())
done = 0
for e in queue:
    if e["url"] in existing:
        continue
    try:
        d = fetch(e)
    except Exception as ex:
        d = dict(e, error=str(ex)[:120], body="", length=0)
    docs.append(d)
    existing[d["url"]] = d
    done += 1
    if done % 10 == 0 or d.get("length", 0) > 500:
        json.dump(docs, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if done % 20 == 0:
        log("progress %d/%d" % (done, len(queue)))
    time.sleep(0.25)

json.dump(docs, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
ok = [d for d in docs if d.get("length", 0) > 200]
log("DONE total=%d ok=%d gated=%d short=%d chars=%d" % (
    len(docs), len(ok), sum(1 for d in docs if d.get("gated")),
    sum(1 for d in docs if not d.get("gated") and d.get("length", 0) <= 200),
    sum(d.get("length", 0) for d in docs)))
