
import requests, re
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
s = requests.Session()
s.headers.update({"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                  "Accept-Language": "zh-CN,zh;q=0.9", "Referer": "https://www.smxy.cn/jwc/gzzd/list.htm"})
r = s.get("https://www.smxy.cn/jwc/2024/0425/c1379a152680/page.htm", timeout=20)
t = r.text
print("status", r.status_code, "len", len(t), "enc", r.encoding)
# find candidate containers
for pat in ['wp_articlecontent', 'v_news_content', 'article-content', 'content', 'entry']:
    print(pat, t.count(pat))
i = t.find('wp_articlecontent')
print("--- around wp_articlecontent ---")
print(t[max(0,i-300):i+900].replace("\n"," ")[:1200])
print("=== psp test ===")
r2 = s.get("https://www.smxy.cn/jwc/2024/1111/c1379a160806/page.htm", timeout=20, allow_redirects=True)
print("psp final:", r2.status_code, r2.url, "len", len(r2.text))
j = r2.text.find('<title>')
print("title:", r2.text[j:j+120])
