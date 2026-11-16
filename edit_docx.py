
# -*- coding: utf-8 -*-
from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn

SRC = r"D:\学年设计\SMUAI毕业设计项目设计报告.docx"
doc = Document(SRC)

def set_run_font(run, size=None, bold=None, east='宋体', ascii_f='Times New Roman'):
    run.font.name = ascii_f
    rpr = run._r.get_or_add_rPr()
    rfonts = rpr.find(qn('w:rFonts'))
    if rfonts is None:
        rfonts = rpr.makeelement(qn('w:rFonts'), {})
        rpr.append(rfonts)
    rfonts.set(qn('w:eastAsia'), east)
    rfonts.set(qn('w:ascii'), ascii_f)
    rfonts.set(qn('w:hAnsi'), ascii_f)
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold

def make_para(text, style='Normal'):
    p = doc.add_paragraph()
    p.style = doc.styles[style]
    if text:
        r = p.add_run(text)
        if style == 'Normal':
            set_run_font(r, size=12, bold=False)
    return p

def make_table(rows_data, header_bold=True):
    nrows = len(rows_data); ncols = len(rows_data[0])
    t = doc.add_table(rows=nrows, cols=ncols)
    t.style = doc.styles['Table Grid']
    for i, row in enumerate(rows_data):
        for j, val in enumerate(row):
            cell = t.cell(i, j)
            p = cell.paragraphs[0]
            for r in list(p.runs):
                r.text = ''
            run = p.add_run(val)
            set_run_font(run, size=10.5, bold=(header_bold and i == 0))
    return t

def insert_after(anchor_el, new_el):
    if hasattr(new_el, '_p'):
        new_el = new_el._p
    elif hasattr(new_el, '_tbl'):
        new_el = new_el._tbl
    anchor_el.addnext(new_el)
    return new_el

body = doc.element.body
children = list(body.iterchildren())

# ---- locate anchors ----
def find_table_after(heading_text):
    # find the <w:tbl> that follows the heading paragraph
    for idx, ch in enumerate(children):
        if ch.tag == qn('w:p'):
            from docx.text.paragraph import Paragraph
            p = Paragraph(ch, doc)
            if p.text.strip() == heading_text:
                # scan forward for next tbl
                for j in range(idx+1, len(children)):
                    if children[j].tag == qn('w:tbl'):
                        return children[j]
    raise RuntimeError('table not found after: ' + heading_text)

anchor_tbl0 = find_table_after('1.2 可行性分析')

# last paragraph before sectPr
last_p = None
for ch in children:
    if ch.tag == qn('w:p'):
        last_p = ch
assert last_p is not None

# ============ Section 1.2 additions ============
sec12 = []

sec12.append(make_para('1.2.1 理论可行性（文献支撑）', 'Heading 3'))
sec12.append(make_para(
    '检索增强生成（Retrieval-Augmented Generation，RAG）由 Lewis 等人于 2020 年提出，通过在生成前引入外部知识检索，'
    '显著提升大语言模型在知识密集型任务上的表现，并有效抑制“幻觉”回答[1]。Gao 等人对 RAG 的系统综述将其归纳为'
    '“索引—检索—生成”三阶段范式，指出该技术无需重新训练模型即可将领域知识注入生成过程，已成为领域问答的主流技术路线[2]。'
    '本设计“文档级知识库＋混合检索＋带引用生成”的架构正遵循这一范式，具备坚实的理论基础。', 'Normal'))
sec12.append(make_para(
    '在检索环节，BEIR 基准的大规模零样本评测表明，稀疏检索（BM25）擅长精确术语匹配、稠密检索（向量）擅长语义泛化，'
    '二者能力互补、混合使用可显著提升召回质量[3]；Robertson 等人提出的 BM25 概率检索框架为关键词检索提供了成熟的概率模型依据[4]；'
    'Cormack 等人证明倒数排名融合（RRF）能稳定优于单一排序学习方法，为本设计“BM25＋向量双路召回、RRF 融合”的融合策略提供了方法学支撑[5]。', 'Normal'))
sec12.append(make_para(
    '在中文领域，Xiao 等人发布的 C-Pack 资源包及 BGE 系列中文嵌入与重排模型，在中文检索与重排基准上取得领先效果，'
    '且可在 CPU 环境本地运行[6]，验证了“轻量本地嵌入（bge-small-zh-v1.5）＋重排（bge-reranker-base）”路线在普通硬件上即可落地，'
    '保证本设计的技术可行性与经济可行性。', 'Normal'))
sec12.append(make_para(
    '综上，本设计采用的“BM25 稀疏检索＋稠密向量检索＋RRF 融合＋重排序＋带引用生成”技术路线，'
    '每一环节均有成熟理论或经同行评议的实证支撑，不存在原理性风险，理论层面完全可行。', 'Normal'))

lit_rows = [
    ['设计环节', '采用技术/方法', '支撑文献'],
    ['知识注入与降幻觉', 'RAG 检索增强生成', '[1] Lewis 2020；[2] Gao 2023'],
    ['稀疏检索', 'BM25 关键词检索', '[3] BEIR 评测；[4] Robertson 2009'],
    ['稠密检索', '向量余弦相似度', '[3] Thakur 2021'],
    ['结果融合', 'RRF 倒数排名融合', '[5] Cormack 2009'],
    ['中文嵌入与重排', 'BGE（bge-small-zh / bge-reranker）', '[6] Xiao 2023'],
    ['领域可行性', '校园问答 RAG 实证', '[7][8]'],
]
sec12.append(make_table(lit_rows))

sec12.append(make_para('1.2.2 领域实证与借鉴案例', 'Heading 3'))
sec12.append(make_para(
    '与本设计同领域的公开文献提供了直接实证。某高校基于大语言模型与 RAG 的校园问答平台，采用“知识库构建—混合检索—智能生成”'
    '三模块架构，对课程表、校园政策等高频咨询实现了 92.2% 的意图识别准确率与 89.9% 的答案准确率，并支持多角色服务与知识库动态更新[7]；'
    '另有基于大语言模型与 RAG 的高校知识库智能问答研究完成了系统构建与评价[8]。'
    '这表明“RAG 校园智能问答”在同类场景中已有可复现的成功先例，本设计具备明确的领域可行性。', 'Normal'))
sec12.append(make_para(
    '工程实践层面，CSDN《RAG 检索质量从 60% 到 90%：混合检索＋重排序》指出纯向量检索因语义鸿沟命中率仅约 60%，'
    '采用“向量＋BM25 双路召回＋RRF 融合＋重排序”后命中率提升至约 90%[9]；腾讯云开发者社区《混合检索 RAG：多路召回＋Reranker 重排模型实战》'
    '实测混合方案使 Top-5 召回率提升约 20%、MRR 提升约 40%[10]。这些量化结果与本设计“以混合检索替代关键词打分”的动机直接吻合，'
    '进一步印证了升级方向的正确性。', 'Normal'))

# ============ Chapter 5 + references ============
ch5 = []
ch5.append(make_para('5 项目完善方向与改进设想', 'Heading 1'))
ch5.append(make_para(
    '在既有设计基础上，结合文献成果、CSDN 工程实践与学年设计原型的实测短板（口语化命中率 16.7%、兜底率 27.7%），提出以下完善方向。', 'Normal'))

ch5.append(make_para('5.1 检索质量与召回增强', 'Heading 2'))
ch5.append(make_para(
    '（1）查询意图识别与路由：在检索前增加轻量意图分类（政策查询／流程咨询／闲聊／失效信息），闲聊类直达通用模型、政策类走知识库，'
    '从源头降低无效兜底，可参照领域文献 92.2% 意图识别的做法[7]。', 'Normal'))
ch5.append(make_para(
    '（2）口语化与同义归一：构建“咋／啥→怎么／什么”“国奖／绩点／挂科／学费／军训”等校园口语同义词典，'
    '缓解 BM25 精确词匹配对口语表达的不足。', 'Normal'))
ch5.append(make_para(
    '（3）多路召回扩展：在 BM25＋向量双路基础上，增加“标题／目录路”与“实体知识图谱路”，形成三至四路召回，'
    '提升低资源语料下的召回率（借鉴腾讯云社区三路并行召回实践[10]）。', 'Normal'))
ch5.append(make_para(
    '（4）重排阈值自适应：将固定阈值 θ=0.35 改为按检索得分分布动态校准，减少误拒答。', 'Normal'))

ch5.append(make_para('5.2 知识工程与多模态扩展', 'Heading 2'))
ch5.append(make_para(
    '（1）从文档切块到知识图谱：在 chunks 之上构建“校园业务知识图谱”（单位—事项—条件—材料—流程），'
    '支持“转专业需满足哪些条件→需准备哪些材料”这类多跳推理问答，作为进阶方向展开想象。', 'Normal'))
ch5.append(make_para(
    '（2）多模态问答：在 RapidOCR 公告识别基础上，扩展表格、流程图的结构化解析，支持“查某流程步骤”类图文问答。', 'Normal'))
ch5.append(make_para(
    '（3）知识时效管理：为文档增加有效期与失效标记，过期政策自动降权并提示“以最新通知为准”。', 'Normal'))

ch5.append(make_para('5.3 评测与持续优化闭环', 'Heading 2'))
ch5.append(make_para(
    '（1）离线评测集：以 104 条问答对与口语化改写样本为种子，按“类别／难度／标准答案”构建 eval_questions，'
    '采用 Recall@k、MRR、答案忠实度、兜底率作为验收指标（当前基线：口语化命中率 16.7%、兜底率 27.7%）。', 'Normal'))
ch5.append(make_para(
    '（2）在线闭环：未命中问题 → 大模型生成候选答案 → 人工审核入库 → 增量更新向量索引，形成半自动知识生长，逐步降低兜底率。', 'Normal'))
ch5.append(make_para(
    '（3）来源可追溯：回答附引用编号、文件名、章节；日志记录 user_id、matched_chunk_id、latency_ms，支持归因分析与 A/B 评测。', 'Normal'))

ch5.append(make_para('5.4 工程化与安全完善', 'Heading 2'))
ch5.append(make_para(
    '（1）配置外置：API Key、数据库口令、管理员默认口令改为环境变量／.env 注入，源码不落明文（修正学年设计原型的明文密钥风险）。', 'Normal'))
ch5.append(make_para(
    '（2）安全加固：登录与聊天接口限流、注册并发冲突处理、会话 Cookie 安全属性（HttpOnly／SameSite）、CSRF 防护。', 'Normal'))
ch5.append(make_para(
    '（3）可维护性：主机／端口配置化，纳入 Git 版本管理，补充单元测试与部署文档。', 'Normal'))

ch5.append(make_para('5.5 借鉴 CSDN 与开源工程实践', 'Heading 2'))
ch5.append(make_para(
    'CSDN《RAG 检索质量从 60% 到 90%：混合检索＋重排序》提出“向量＋BM25 双路召回＋RRF 融合＋重排序”四步法，'
    '将专业知识库命中率从约 60% 提升至约 90%[9]，是本设计 4.1 节混合检索算法的直接印证。', 'Normal'))
ch5.append(make_para(
    '腾讯云开发者社区《混合检索 RAG：多路召回＋Reranker 重排模型实战》给出“向量＋关键词＋知识图谱”三路召回与 BGE-Reranker 实测流程[10]，'
    '可作 5.1(3) 多路召回的落地参考。', 'Normal'))
ch5.append(make_para(
    '开源项目 CN_Literature_RAG（BGE-M3 双路召回＋bge-reranker 重排＋生成）[11] 与 Campus-AI-RAG[12] 提供了中文知识库问答的完整工程化样板，'
    '可在实现阶段参照其模块划分与接口设计。', 'Normal'))

ch5.append(make_para('参考文献', 'Heading 1'))
refs = [
    '[1] Lewis P, Perez E, Piktus A, et al. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks[C]// Advances in Neural Information Processing Systems (NeurIPS 33). 2020.',
    '[2] Gao Y, Xiong Y, Gao X, et al. Retrieval-Augmented Generation for Large Language Models: A Survey[J]. arXiv preprint arXiv:2312.10997, 2023.',
    '[3] Thakur N, Reimers N, Rücklé A, et al. BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models[C]// NeurIPS Datasets and Benchmarks Track. 2021.',
    '[4] Robertson S, Zaragoza H. The Probabilistic Relevance Framework: BM25 and Beyond[J]. Foundations and Trends in Information Retrieval, 2009, 3(4): 333-389.',
    '[5] Cormack G V, Clarke C L A, Buettcher S. Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods[C]// SIGIR. 2009: 758-759.',
    '[6] Xiao S, Liu Z, Zhang P, et al. C-Pack: Packaged Resources To Advance General Chinese Embedding[C]// SIGIR. 2024. (arXiv:2309.07597)',
    '[7] 大模型和RAG驱动的校园问答平台设计与实现[J]. 电脑与电信, 2025(4): 65.（作者姓名请按知网/万方收录补全）',
    '[8] 基于大语言模型和RAG技术的高校知识库智能问答系统构建与评价[J].（维普收录，作者与卷期页码请按数据库补全）',
    '[9] 大模型微调专家. RAG检索质量从60%到90%：混合检索+重排序[EB/OL]. CSDN, 2026-06-22. https://blog.csdn.net/weixin_55154866/article/details/162207801.',
    '[10] 混合检索RAG：多路召回+Reranker重排模型实战[EB/OL]. 腾讯云开发者社区, 2026-07-17. https://cloud.tencent.com.cn/developer/article/2710906.',
    '[11] kobewith24. CN_Literature_RAG: 中文文献检索问答系统[EB/OL]. GitHub. https://github.com/kobewith24/CN_Literature_RAG.',
    '[12] liweisi91010. Campus-AI-RAG[EB/OL]. GitHub. https://github.com/liweisi91010/Campus-AI-RAG.',
]
for r in refs:
    ch5.append(make_para(r, 'Normal'))

# ---- perform insertion (move elements into place) ----
tail = anchor_tbl0
for el in sec12:
    tail = insert_after(tail, el)

tail = last_p
for el in ch5:
    tail = insert_after(tail, el)

OUT = r"D:\学年设计\SMUAI毕业设计项目设计报告_升级版.docx"
doc.save(OUT)
print("saved", OUT)
