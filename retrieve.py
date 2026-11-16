
import json, sys, re, os
import jieba
from rank_bm25 import BM25Okapi

jieba.setLogLevel(20)
CHUNKS = r"D:\学年设计\sumai\kb_chunks.json"
EXTRA = ["学分", "重修", "辅修", "学籍", "学位", "选课", "评教", "绩点", "补考", "缓考",
         "转专业", "退学", "休学", "复学", "毕业设计", "毕业论文", "文献综述", "开题报告",
         "实习", "实践教育基地", "实验室", "危险化学品", "教学大纲", "培养方案", "教材",
         "考试作弊", "学位论文作假", "推免", "考研", "国家奖学金", "助学金", "勤工助学",
         "一卡通", "校园网", "图书馆", "宿舍", "报到", "注册", "学号", "缴费", "学费"]
for w in EXTRA:
    jieba.add_word(w, freq=20000)

def tokenize(text):
    toks = [t.strip().lower() for t in jieba.lcut(text) if t.strip()]
    toks += [b for b in re.findall(r"[\u4e00-\u9fa5]{2,4}", text)][:0]
    return toks

def load():
    chunks = json.load(open(CHUNKS, encoding="utf-8"))
    corpus = [tokenize(c["text"]) for c in chunks]
    bm25 = BM25Okapi(corpus)
    return chunks, bm25

def search(chunks, bm25, query, topk=5):
    q = tokenize(query)
    scores = bm25.get_scores(q)
    idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:topk]
    return [(scores[i], chunks[i]) for i in idx]

if __name__ == "__main__":
    chunks, bm25 = load()
    print("chunks:", len(chunks))
    queries = sys.argv[1:] or ["重修怎么申请", "学士学位论文作假怎么处理", "考研有奖励吗", "辅修专业怎么报名"]
    for q in queries:
        print("\n=== %s" % q)
        for s, c in search(chunks, bm25, q):
            print("  %.2f [%s] %s | %s" % (s, c["column"], c["title"][:26], c["text"][:70].replace("\n", " ")))
