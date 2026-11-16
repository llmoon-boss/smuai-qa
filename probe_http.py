
import requests, re
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
urls = [
 "https://www.smxy.cn/jwc/2024/1111/c1379a160806/page.htm",
 "https://www.smxy.cn/jwc/2024/0425/c1379a152680/page.htm",
 "https://www.smxy.cn/jwc/2026/0714/c1379a184703/page.htm",
]
s = requests.Session()
s.headers.update({"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                  "Accept-Language": "zh-CN,zh;q=0.9", "Referer": "https://www.smxy.cn/jwc/gzzd/list.htm"})
for u in urls:
    try:
        r = s.get(u, timeout=20, allow_redirects=False)
        print(u.split("/")[-2], "->", r.status_code, "loc:", (r.headers.get("Location") or "")[:120], "len", len(r.content))
        if r.status_code == 200:
            txt = r.text
            m = re.search(r'<div class="wp_articlecontent">(.*?)</div>\s*</div>', txt, re.S)
            print("   article block found:", bool(m))
            body = re.sub(r"<[^>]+>", "", (m.group(1) if m else txt))
            print("   textlen:", len(re.sub(r"\s+", "", body)))
    except Exception as e:
        print(u, "ERR", e)
