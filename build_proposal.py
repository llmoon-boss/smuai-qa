# -*- coding: utf-8 -*-
import copy
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.table import _Cell

SRC = r"D:\学年设计\开题报告.docx"
OUT = r"D:\学年设计\开题报告_最终版.docx"

doc = Document(SRC)

def _fs_run(text):
    r = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:hint'), 'eastAsia')
    rFonts.set(qn('w:ascii'), '仿宋')
    rFonts.set(qn('w:hAnsi'), '仿宋')
    rFonts.set(qn('w:eastAsia'), '仿宋')
    rFonts.set(qn('w:cs'), '仿宋')
    rPr.append(rFonts)
    color = OxmlElement('w:color'); color.set(qn('w:val'), '000000'); rPr.append(color)
    r.append(rPr)
    t = OxmlElement('w:t'); t.set(qn('xml:space'), 'preserve'); t.text = text
    r.append(t)
    return r

def _strip_paraids(el):
    el.attrib.pop(qn('w14:paraId'), None)
    el.attrib.pop(qn('w14:textId'), None)
    for child in el:
        _strip_paraids(child)

def fill_content_cell(cell, lines):
    paras = list(cell.paragraphs)
    heading_el = paras[0]._p
    template_el = copy.deepcopy(paras[-1]._p)
    _strip_paraids(template_el)
    for p in paras[1:]:
        p._p.getparent().remove(p._p)
    spacer = copy.deepcopy(template_el)
    heading_el.addnext(spacer)
    anchor = spacer
    for line in lines:
        newp = copy.deepcopy(template_el)
        for r in newp.findall(qn('w:r')):
            newp.remove(r)
        newp.append(_fs_run(line))
        anchor.addnext(newp)
        anchor = newp

def set_cell_text(cell, text, center=False):
    p = cell.paragraphs[0]
    for r in list(p.runs):
        r._r.getparent().remove(r._r)
    pPr = p._p.find(qn('w:pPr'))
    if pPr is not None:
        jc = pPr.find(qn('w:jc'))
        if jc is None:
            jc = OxmlElement('w:jc'); pPr.append(jc)
        jc.set(qn('w:val'), 'center' if center else 'both')
    p._p.append(_fs_run(text))

def set_body_para_text(par, new_text):
    ref_rPr = None
    for r in par.runs:
        rPr = r._r.find(qn('w:rPr'))
        if rPr is not None:
            ref_rPr = copy.deepcopy(rPr); break
    for r in list(par.runs):
        r._r.getparent().remove(r._r)
    r = OxmlElement('w:r')
    if ref_rPr is not None:
        r.append(ref_rPr)
    else:
        r.append(OxmlElement('w:rPr'))
    t = OxmlElement('w:t'); t.set(qn('xml:space'), 'preserve'); t.text = new_text
    r.append(t)
    par._p.append(r)

TITLE = "基于混合检索与大语言模型的校园智能问答系统设计与实现"

tb = doc.tables[0]

# 表头信息行
row1 = tb.rows[1]._tr.findall(qn('w:tc'))
vals = ["信息工程学院", "计算机科学与技术", "刘亮", "20230861234", "", ""]
for tc, v in zip(row1, vals):
    if v:
        set_cell_text(_Cell(tc, tb), v, center=True)

# 题目行
row2 = tb.rows[2]._tr.findall(qn('w:tc'))
set_cell_text(_Cell(row2[1], tb), TITLE)

sec1 = [
"三明学院日常教学与学生管理涉及的规章制度数量较多且时有修订，并分散发布在不同平台，学生办理事务时往往需要反复查阅文件或到各窗口咨询，信息获取成本较高。以检索增强生成（RAG）为代表的知识密集型问答技术，通过检索外部知识库约束大语言模型的输出，能够缓解通用模型缺乏领域知识、易产生事实性错误（即\u201c幻觉\u201d）的问题，为构建校园规章制度问答系统提供了可行路径。本课题将 BM25 稀疏检索与向量稠密检索相结合的混合检索策略应用于中文垂直领域问答，并面向三明学院真实制度语料构建问答原型，兼具考察检索方法适用性的理论意义与减轻重复答疑负担的实践价值。",
"检索增强生成由 Lewis 等人（2020）正式提出。检索环节中，Robertson 与 Zaragoza（2009）提出的 BM25 仍是稀疏检索的代表方法，Cormack 等人（2009）提出的倒数排名融合无需训练即可改善多路召回结果的排序质量。中文方面，Xiao 等人（2024）开源的 BGE 系列嵌入模型与重排序器在中文评测基准上表现良好；已有研究者将大模型与 RAG 结合构建校园问答平台（《电脑与电信》2025 年第 4 期），报道其答案准确率达 88.9%，初步验证了该技术路线在校园场景的可用性。",
"但现有研究多以通用或宽泛的校园信息为对象，针对单一高校内部规章制度的垂直知识库构建仍较薄弱。三明学院现有原型采用关键词打分匹配，实测知识库兜底率约 27.7%、口语化改写命中率仅约 16.7%，难以应对学生多样化的口语表达。本课题拟引入混合检索与重排序机制加以改进，并建立可复现的评测方案。",
]
sec2 = [
"本课题的研究内容如下。",
"（1）知识库构建。采集三明学院学籍、奖助、住宿、课程重修、图书馆入馆等 14 份制度文档及 4 份公告图片，经文本解析、OCR、按标题切块后向量化入库。",
"（2）混合检索与重排序。实现 BM25 稀疏检索与 BGE 稠密向量检索双路召回，经 RRF 融合后由 bge-reranker 重排序。",
"（3）生成与兜底。将重排序片段作为上下文输入大语言模型，生成附引用编号的回答；检索置信度不足或模型调用失败时回退为知识库高置信答案。",
"（4）系统实现与评测。基于 Flask 构建问答、后台管理与反馈功能；以召回率、平均倒数排名、兜底率等指标对比关键词基线与混合检索方案。",
"预期目标：实现覆盖教务、奖助、图书馆、学工、后勤、学校概况六类问答的可运行原型；知识库兜底率由约 27.7% 降至 10% 以下、口语化命中率由约 16.7% 提升至 80% 以上；回答附带来源出处，形成可追溯链路。",
]
sec3 = [
"（1）文献研究法。梳理检索增强生成与信息检索领域文献，确定技术路线与评测口径。",
"（2）软件工程方法。按需求分析、设计、编码、测试的流程，采用 Flask、MySQL、Chroma 完成开发。",
"（3）实验对比法。以关键词检索原型为基线，对 BM25、向量检索、混合检索与重排序进行消融对比，辅以人工抽测评估答案质量。",
]
sec4 = [
"本课题计划用 16 周完成。",
"第 1—2 周：选题论证与文献调研，完成开题报告。",
"第 3—4 周：需求分析与系统设计。",
"第 5—6 周：文档解析、OCR、切块入库，完成知识库构建。",
"第 7—8 周：实现 BM25 与向量双路检索及 RRF 融合。",
"第 9—10 周：接入重排序与大模型生成，完善兜底策略。",
"第 11—12 周：系统集成联调，实现后台与反馈功能。",
"第 13—14 周：构建评测集，开展消融实验与指标评测。",
"第 15—16 周：撰写毕业论文，整理材料并准备答辩。",
]
sec5 = [
"[1] Lewis P, Perez E, Piktus A, et al. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks[C]//Advances in Neural Information Processing Systems. 2020: 9459-9474.",
"[2] Robertson S, Zaragoza H. The Probabilistic Relevance Framework: BM25 and Beyond[J]. Foundations and Trends in Information Retrieval, 2009, 3(4): 333-389.",
"[3] Cormack G V, Clarke C L A, Buettcher S. Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods[C]//Proceedings of the 32nd International ACM SIGIR Conference. 2009: 758-759.",
"[4] Xiao S, Liu Z, Zhang P, et al. C-Pack: Packaged Resources To Advance General Chinese Embedding[C]//Proceedings of the 47th International ACM SIGIR Conference. 2024: 1504-1514.",
"[5] 范贵进, 孙颖颖. 大模型和RAG驱动的校园问答平台设计与实现[J]. 电脑与电信, 2025(4): 65.",
]

for i, sec in enumerate([sec1, sec2, sec3, sec4, sec5]):
    row = tb.rows[3 + i]._tr.findall(qn('w:tc'))
    fill_content_cell(_Cell(row[0], tb), sec)

# 封面字段
def find_para(pred):
    for p in doc.paragraphs:
        if pred(p.text):
            return p
    return None

p_name = find_para(lambda t: t.startswith("学生姓名"))
if p_name is not None:
    set_body_para_text(p_name, "学生姓名：刘亮        学号：20230861234")
p_college = find_para(lambda t: t.replace(" ", "").startswith("学院"))
if p_college is not None:
    set_body_para_text(p_college, "学   院：信息工程学院")
p_major = find_para(lambda t: t.replace(" ", "").startswith("专业"))
if p_major is not None:
    set_body_para_text(p_major, "专      业：计算机科学与技术")
p_title = find_para(lambda t: t.startswith("论文（设计）题目"))
if p_title is not None:
    set_body_para_text(p_title, "论文（设计）题目：" + TITLE)

doc.save(OUT)
print("saved:", OUT)
