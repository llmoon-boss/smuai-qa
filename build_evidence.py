
# -*- coding: utf-8 -*-
"""生成《可行性论证与完善方案》补充材料 docx。"""
import os, shutil
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

OUT = r"D:\学年设计\SMUAI毕业设计可行性论证与完善方案.docx"
FIG = r"D:\学年设计\sumai\figs"
os.makedirs(FIG, exist_ok=True)
SRC = {
    "answer": r"C:\Users\刘亮\.dsh\attachments\v1\objects\eb\ebb765be7601f7377c8b17af298f46d01bb2ca894b2bec3169a1bc77ca0c7875",
    "refuse": r"C:\Users\刘亮\.dsh\attachments\v1\objects\85\85a9f52c76bf1607d31bf22ce27566ba9118641c252ae00c011e5b78bdaad7b2",
}
for k, v in SRC.items():
    dst = os.path.join(FIG, k + ".png")
    if os.path.exists(v):
        shutil.copyfile(v, dst)

doc = Document()
sec = doc.sections[0]
sec.top_margin = Cm(2.4); sec.bottom_margin = Cm(2.4)
sec.left_margin = Cm(2.8); sec.right_margin = Cm(2.6)

def set_font(run, size=12, bold=False, ascii_font="Times New Roman", ea="宋体", color=None):
    run.font.size = Pt(size); run.bold = bold
    run.font.name = ascii_font
    run._element.rPr.rFonts.set(qn("w:eastAsia"), ea)
    if color: run.font.color.rgb = RGBColor(*color)

st = doc.styles["Normal"]
st.font.name = "Times New Roman"; st.font.size = Pt(12)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
pf = st.paragraph_format
pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
pf.space_before = Pt(0); pf.space_after = Pt(0)

def title(text, size=18):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(6)
    set_font(p.add_run(text), size, True, ea="黑体")
    return p

def subtitle(text):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(14)
    set_font(p.add_run(text), 10.5, False, color=(0x55, 0x55, 0x55))
    return p

def h1(text):
    p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(14); p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    set_font(p.add_run(text), 14, True, ea="黑体")
    return p

def h2(text):
    p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(9); p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    set_font(p.add_run(text), 12, True, ea="黑体")
    return p

def para(text, indent=True, size=12, align=None):
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Pt(size * 2) if indent else Pt(0)
    if align == "center": p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    else: p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    set_font(p.add_run(text), size)
    return p

def bullet(text, size=12):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Pt(size * 2)
    p.paragraph_format.first_line_indent = Pt(-size)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    set_font(p.add_run("（%s）" % text.split("|")[0].strip() if "|" in text else "· "), size)
    if "|" in text:
        set_font(p.add_run(text.split("|", 1)[1]), size)
    return p

def caption(text):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4); p.paragraph_format.space_after = Pt(8)
    set_font(p.add_run(text), 10.5, True, color=(0x33, 0x33, 0x33))

def _fix_table(t, widths, header_repeat=True, keep_together=True):
    """固定列宽 + 表头重复 + 行不跨页 + 整表不拆页。"""
    from docx.oxml import OxmlElement
    tbl = t._tbl
    tblPr = tbl.tblPr
    layout = OxmlElement("w:tblLayout"); layout.set(qn("w:type"), "fixed"); tblPr.append(layout)
    t.autofit = False
    if widths:
        grid = tbl.find(qn("w:tblGrid"))
        if grid is not None:
            for gc, w in zip(grid.findall(qn("w:gridCol")), widths):
                gc.set(qn("w:w"), str(int(w * 567)))  # cm -> twips
        for row in t.rows:
            for cell, w in zip(row.cells, widths):
                cell.width = Cm(w)
    n = len(t.rows)
    for i, row in enumerate(t.rows):
        trPr = row._tr.get_or_add_trPr()
        trPr.append(OxmlElement("w:cantSplit"))
        if header_repeat and i == 0:
            trPr.append(OxmlElement("w:tblHeader"))
        for cell in row.cells:
            for p in cell.paragraphs:
                if keep_together:
                    p.paragraph_format.keep_with_next = True

def table(headers, rows, widths=None, fs=10.5):
    # 让表格前的引导段落与表格同页，避免出现“引导句留在页底、表格翻页”
    if doc.paragraphs:
        doc.paragraphs[-1].paragraph_format.keep_with_next = True
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]
        c.text = ""
        p = c.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_font(p.add_run(h), fs, True, ea="黑体")
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i == 0 or len(str(v)) <= 12 else WD_ALIGN_PARAGRAPH.LEFT
            set_font(p.add_run(str(v)), fs)
    _fix_table(t, widths)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t

# ============ 正文 ============
title("基于混合检索与大语言模型的校园智能问答系统")
subtitle("可行性论证与完善方案（毕业设计补充材料 · 2026 年 11 月）")

para("本材料用于支撑毕业设计（论文）的可行性分析与系统完善章节，由三部分构成：一是项目技术路线的文献证据；二是本项目自建语料上的实测证据（含检索消融、拒答门控标定与系统演示）；三是在此基础上提出的完善与升级方案。全部文献均可依据文中给出的 DOI、arXiv 编号或刊期检索核对，全部实验数据可由随附脚本复现。")

# 一
h1("一、可行性论证框架")
para("可行性不宜只以“能否跑通”论证。本项目按四个维度论证，每个维度均给出文献证据与自测证据两类支撑，二者相互印证：技术路线是否有据可依、语料是否可得且可用、工程实现是否有同类系统先例、使用侧是否有真实需求与政策依据。")
table(["维度", "核心问题", "证据类型", "结论"],
      [["技术可行性", "所用检索与生成方法在当前语料上是否有效", "文献 + 消融实验", "成立"],
       ["数据可行性", "校内制度文件能否公开、稳定地获取与清洗", "实测抓取统计", "成立（有边界）"],
       ["工程可行性", "同类高校问答系统是否已有落地实现", "文献 + 工程实践", "成立"],
       ["效益与政策可行性", "是否存在真实问询压力与信息化政策导向", "政策原文 + 场景分析", "成立"]],
      widths=[3.0, 6.4, 3.6, 2.2])
caption("表 1  可行性论证的四个维度与证据来源")

# 二
h1("二、技术可行性的文献证据")
h2("2.1 词面检索是稳健基线：选用 BM25 有文献依据")
para("BEIR 基准（Thakur 等，2021）在 18 个异构数据集上评测了 10 类检索系统，其核心结论是 BM25 依然是极为稳健的基线：在跨领域、零样本场景下，稠密检索与稀疏学习检索往往不及 BM25，重排序（re-ranking）效果最好但计算代价显著。本项目语料为中文校内制度文本，术语高度领域化、问句与文件表述的用词重合度高，正属于词面检索的优势区间。因此以 BM25 为检索底座并非能力妥协，而是与文献结论一致的稳妥选择；在此基础上再叠加标题路融合与后续可选的向量路，属于渐进式增强而非推倒重来。")
para("需要说明的是，该结论并不意味着稠密检索无价值。文献同时指出稠密检索在同领域有标注数据时优势明显，这也是本项目把“向量路与重排序”列入完善方案（见第七章）的原因：第一版以可复现、低算力为先，后续按数据与算力条件升级。")

h2("2.2 混合检索的融合函数：凸组合优于 RRF")
para("Bruch、Gai 与 Ingber 在《An Analysis of Fusion Functions for Hybrid Retrieval》（ACM TOIS，2023，doi: 10.1145/3596512）中系统比较了倒数排名融合（RRF）与凸组合（加权归一化）两类融合函数，结论是凸组合在域内与域外评测中均优于 RRF，且 RRF 对参数 k 较敏感。本项目在自建语料上的消融结果与该结论完全一致：单路分块 BM25 的 R@1 为 0.900，RRF(k=60) 反而降至 0.850，而采用 min-max 归一化后的加权融合（分块 0.75、标题 0.25）回升至 0.950（详见表 3）。")
para("RRF 在本项目上失效的机理可以解释：RRF 只使用名次、丢弃了分数的量级信息，当两路排序高度相似时大量文档被打成同分，排序被“是否在双路中出现”主导，反而把单路第一名挤出前列。这一“自测与文献互证”的结果，正是本项目选择加权融合的直接依据。")

h2("2.3 稠密检索与重排序的收益与代价")
para("Abirami 等在《Evaluating Lexical, Dense, and Hybrid Retrieval Pipelines for RAG》（IEEE PuneCon，2025，doi: 10.1109/punecon67554.2025.11379254）中给出量化对照：在 Natural Questions 上稠密检索 nDCG@10 达 0.916，而 BM25 为 0.799；混合 RRF 可将 Recall@100 提升至 0.997；交叉编码器重排可把 nDCG@10 提到 0.954，但耗时超过 50 倍。该结果说明：稠密检索与重排的收益确实存在，但代价同样明确。对毕业设计而言，把重排列为“可选增强”而非默认路径，是算力与效果之间的合理取舍。")

h2("2.4 检索增强生成范式：可溯源与可更新")
para("Lewis 等提出 RAG（arXiv:2005.11401，2020），将参数化记忆与非参数化外部索引结合，使模型输出可追溯至具体文档、知识可增量更新而无需重训。Gao 等的综述（arXiv:2312.10997，2023）进一步把大模型在垂直场景的三类问题归纳为幻觉、知识时效性不足与缺乏可溯源性，并把 RAG 视为主要解法范式。本项目“先检索校内文件、再据资料作答并标注来源编号”的整体架构，正是这一范式的直接应用。")

h2("2.5 引用忠实性风险：为什么必须做门控与拒答")
para("《Correctness is not Faithfulness in RAG Attributions》（ACM ICTIR，2025，doi: 10.1145/3731120.3744592）指出，引用的“正确”（答案与引文相关）不等于“忠实”（答案确实由引文支持），其实验中高达 57% 的引用存在事后合理化成因。中文高风险场景的评测（CnHallu-RAG，Zenodo 21190545）同样发现模型会忽略给定证据、编造引用、把不确定表述为事实。")
para("这两项结论直接决定了本项目的三项设计：一是答案只允许使用检索到的资料并逐句标注来源；二是引入“查询词覆盖率”置信度门控，覆盖率不足时明确拒答而不是勉强作答；三是在无大模型可用时降级为抽取式答案（直接取原文句子），以牺牲流畅度换取可核验性。换言之，拒答机制不是功能缺失，而是针对上述风险的主动设计。")

h2("2.6 政策依据")
para("教育部《关于加强新时代教育管理信息化工作的通知》（2021）明确提出要“有效解决系统整合不足、数据共享不畅、服务体验不佳、设施重复建设等突出问题”，推动“教育服务由被动响应向主动服务转变”，并把“一网通办”、服务个性化列入阶段目标。校内制度问询正是“被动响应”最集中的环节之一：同一问题被不同学生反复询问，答复依赖人工且口径不一。以问答系统承接高频、标准化的制度问询，与该政策导向一致。")

# 三
h1("三、同类系统与工程实践的可行性证据")
h2("3.1 高校学生信息服务问答系统已有落地先例")
para("LexaQuery 系统（《Mathematics and Informatics》，2026，doi: 10.53656/math2026-1-4-lhc）面向保加利亚普罗夫迪夫大学的学生信息服务，采用三层架构：规则化的自然语言到 SQL 转换、多源知识抽取、对话交互层。其报告的核心结论是：相较纯神经网络方案，该架构响应更快、可解释性更强、更易与既有校务系统集成。这为本项目“检索 + 受控生成 + 来源标注”的路线提供了同类场景的直接实证，也说明在校园制度问答中，结构化知识与词面检索的组合同样具备竞争力。")
para("此外，EduChat（arXiv:2308.02773）面向教育场景的对话能力评测，以及《University Chatbot System Using Generative AI with LLMs》（2025，doi: 10.1007/978-3-031-91235-1_21）等高校问答实践，均表明“高校 + 生成式问答”已是成熟的研究与工程方向，本项目不属于无人验证的设想。")

h2("3.2 工程实践中的可借鉴做法")
para("检索同类工程文章（CSDN 等技术社区）后，可归纳出若干具有共性的工程做法，本项目已采纳或列入计划：")
table(["实践要点", "来源要点", "本项目处理"],
      [["分阶段检索 + 重排序", "校园心理健康 RAG 实战（2026-07-01）采用“双阶段向量检索与重排序”", "第一版保留单阶段词面检索；重排列入完善方案"],
       ["多层安全护栏", "同上：危机语义分级 + 规则拦截", "已实现拒答门控与范围提示，可扩展为敏感词与紧急转人工"],
       ["文档切片策略", "RAG 落地实践（向量库、切片与检索优化）强调切片粒度对召回的影响", "已按 480/120 字、80 字重叠在句读处切分，并做去重"],
       ["混合检索而非单路", "混合检索策略、召回优化类文章普遍建议词面 + 向量并行", "已实现分块与标题双路加权融合，向量路待接入"],
       ["轻量化部署", "LangChain + FastAPI 封装、轻量部署", "Flask 单进程 + 本地索引，无 GPU 依赖，启动即用"]],
      widths=[3.2, 7.0, 5.0])
caption("表 2  同类工程实践要点与本项目对应处理")

h2("3.3 与已有工作的差异")
para("现有校园问答实践多依赖私有业务数据（成绩、课表）或人工整理问答对，复现门槛高、结论难以核验。本项目的差异在于：语料全部取自学校官网公开文件，采集与清洗过程可完全复现；评测给出可复算的指标而非主观描述；对“答不出”的情形做显式标定与拒答。这使本项目在毕业设计的评价语境下更具可检验性——这也是它相较同类文章的主要贡献点。")

# 四
h1("四、数据可行性的实测证据")
para("为验证“校内制度文件可公开获取且足以支撑问答”，本项目以学校官网教务处 20 个栏目为入口实际采集，结果如下。")
table(["采集环节", "数量", "说明"],
      [["抓取栏目", "20 个", "规章制度、教务/课务/学务/考试管理、实验实践、质量监控、教学改革、教材建设等"],
       ["抓取文章", "731 篇", "列表页翻页 + 详情页正文抽取（统一正文容器）"],
       ["正文完整", "615 篇", "抽取到正文容器且长度达标"],
       ["需登录（未入库）", "41 篇", "经统一身份认证跳转，匿名访问被拒，需登录态或申请授权"],
       ["去重入库", "526 篇", "按标题与正文指纹去重，过滤过短文本"],
       ["检索分块", "1792 块", "平均 394 字，共约 70.8 万字"]],
      widths=[4.2, 2.6, 8.4])
caption("表 3  校园官网语料采集与入库统计")
para("统计说明了两点：其一，公开制度文件的主体部分可以稳定获取，语料足以覆盖重修、辅修、学业预警、考试管理、实践教学、毕业设计等高频问询；其二，存在明确边界——41 篇需登录的文件（含部分实验室与实践基地管理办法）无法匿名获取，构成当前语料的已知缺口，也是评测中个别查询未命中的直接原因。这一边界应在论文中如实交代，而非回避。")

# 五
h1("五、本项目自测证据")
h2("5.1 检索策略消融")
para("在 20 条中文评测查询（覆盖重修、辅修、学业预警、教室借用、教学档案、双语教学、教学信息员、应征入伍、入学资格复查、学位论文作假、考研、教学成果奖、教改项目、通识选修、课程运行、实验室、毕业论文、补考、实践教育基地、评教）上比较六种策略，以人工设定的标准答案文档为基准计算 Recall@1、Recall@3 与 MRR：")
table(["检索策略", "R@1", "R@3", "MRR"],
      [["仅分块 BM25", "0.900", "0.950", "0.925"],
       ["仅标题 BM25", "0.750", "0.850", "0.800"],
       ["RRF 融合（k=60）", "0.850", "0.850", "0.863"],
       ["加权融合（α=0.60）", "0.900", "0.900", "0.900"],
       ["加权融合（α=0.75，采用）", "0.950", "0.950", "0.950"],
       ["加权融合（α=0.90）", "0.950", "0.950", "0.950"]],
      widths=[6.4, 2.6, 2.6, 2.6])
caption("表 4  检索策略消融结果（20 条查询）")
para("最终口径下，20 条查询中 19 条在首位命中标准文档；唯一未命中的“实践教育基地怎么建设”属语料缺口（相应文件在 41 篇需登录之列），在可用语料上首位命中率为 19/19。单次检索（1792 个分块、双路 BM25）耗时中位 3 毫秒、最大 6 毫秒，全部在 CPU 上完成，无需 GPU。")

h2("5.2 拒答门控标定")
para("早期尝试直接用融合分做门控失败：min-max 归一化使任何查询的首位得分都等于 1.0，域外问题同样如此，无法区分。改用“查询内容词在候选文档正文中的覆盖率”后区分度显著：")
table(["统计量", "域内查询（20 条）", "域外查询（10 条）"],
      [["覆盖率最小值", "0.50", "0.00"],
       ["覆盖率中位数", "1.00", "0.00"],
       ["覆盖率最大值", "1.00", "0.67"]],
      widths=[5.0, 5.0, 5.0])
caption("表 5  查询词覆盖率在域内/域外问题上的分布")
para("取阈值 0.60 时，域内查询接受率 0.950、域外查询拒绝率 0.900，构成一组可用的工作点。被拒的域内查询主要是语料缺口问题；被放行的域外查询“英语四级怎么复习”实际命中了考位通知，属真实相关而非误放。这一交叉验证说明门控依据的是文本覆盖而非表面相似度，与 2.5 节引用的引用忠实性结论相互支撑。")

h2("5.3 端到端问答与演示")
para("系统已实现为可运行的本地服务：检索、门控、答案组织与来源标注串联为单一接口，返回结构包含问题、是否拒答、置信度、答案正文与来源列表（标题、栏目、日期、文号、原文链接、融合分）。下图分别为作答与拒答的实际界面。")
if os.path.exists(os.path.join(FIG, "answer.png")):
    doc.add_picture(os.path.join(FIG, "answer.png"), width=Cm(15.2))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    caption("图 1  “辅修专业怎么报名”的作答界面：答案分句标注来源编号，下方列出三篇依据文件")
if os.path.exists(os.path.join(FIG, "refuse.png")):
    doc.add_picture(os.path.join(FIG, "refuse.png"), width=Cm(15.2))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    caption("图 2  域外问题“红烧肉怎么做才好吃”的拒答界面：明确说明未收录并给出求助渠道")

h2("5.4 证据的局限")
para("上述实验的局限必须写明：一是语料仅来自教务处一个来源，学工、财务、图书馆、招生就业尚未纳入；二是评测仅 20 条查询，标准答案由关键词匹配判定，未做多标注者一致性检验；三是拒答阈值在上述 20 + 10 条样本上标定，样本量偏小，存在过拟合风险；四是尚未接入向量检索与重排序，未与大模型生成模式做效果对照；五是没有真实用户的使用数据。这些局限正是第六章完善方案的出发点。")

# 六 (编号对齐：完善方案)
h1("六、完善与升级方案")
para("按“语料—检索—问答—评估—工程”五层推进，每层给出可交付物与验收标准，便于在毕业设计周期内分阶段完成。")
table(["层次", "改进内容", "验收标准"],
      [["语料层", "扩展学工、财务、图书馆、招生就业等子站；对 41 篇需登录文件申请授权或采用登录态采集；按栏目设置权重，降低政策长文类噪声", "入库文档 ≥ 1200 篇，覆盖高频问询 30 项以上"],
       ["检索层", "接入中文向量模型（如 bge-m3）形成第三路；与词面路做凸组合；对比语义分块与固定长度分块；引入同义词与口语到书面的查询改写", "在同一评测集上 R@1 不低于 0.95，且口语化问法提升 ≥ 5 个百分点"],
       ["问答层", "问题意图分类（办事流程 / 制度解释 / 时间节点 / 联系方式）并路由不同提示模板；答案结构化为步骤卡；引用粒度细化到段落", "流程类问题输出可执行步骤，人工抽检正确率 ≥ 90%"],
       ["评估层", "评测集扩至 100 条并双人标注；增加答案忠实性人工核验；给出拒答 ROC 曲线与最优阈值", "形成可复算的评测报告，指标可被第三方复现"],
       ["工程层", "统一身份认证接入与权限分级；检索缓存与限流；问答日志与未命中问题回流；隐私合规（不采集个人信息）", "服务连续运行 7 天无故障，未命中问题可回流分析"]],
      widths=[2.4, 8.6, 4.6])
caption("表 6  五层完善方案与验收标准")
para("论文层面的改进同样重要。建议把“语料构建—策略消融—门控标定—系统演示”组织为一条完整证据链：先说明数据从何而来、如何清洗，再用消融实验说明方法选择不是拍定，随后用标定实验说明拒答阈值可解释，最后以系统演示证明工程可用。这样“方法—实验—讨论”形成闭环，也正好回应评审最关心的“工作量与可验证性”问题。")

# 七 结论
h1("七、结论")
para("第一，技术路线可行且有文献支撑。词面检索作为底座符合 BEIR 的基线结论；加权融合优于 RRF 的判断与 TOIS 2023 的分析一致，并在本项目消融中复现；“引用必须可核验、不足则拒答”的设计对应 ICTIR 2025 关于引用忠实性的发现。")
para("第二，数据与工程可行且有实测支撑。526 篇、1792 块的语料足以覆盖主要问询，检索首位命中率 0.95、时延毫秒级，系统可本地启动演示；同时存在 41 篇需登录文件的语料缺口，这一边界已被明确记录。")
para("第三，改进路径清晰且可分期完成。向量路、重排、意图路由、评估扩样与工程化五项改进均有明确的验收标准，可在毕业设计周期内逐项落地。")
para("第四，风险与对策明确。主要风险是大模型幻觉与引用不忠实，对策是覆盖率门控、来源编号、抽取式降级与人工抽检；次要风险是语料覆盖不全与评测样本偏小，对策是扩展来源与扩样标注。")

h1("参考文献")
refs = [
 "Thakur N, Reimers N, Rücklé A, et al. BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models[C]//NeurIPS Datasets and Benchmarks Track, 2021. arXiv:2104.08663.",
 "Lewis P, Perez E, Piktus A, et al. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks[C]//NeurIPS, 2020. arXiv:2005.11401.",
 "Gao Y, Xiong Y, Gao X, et al. Retrieval-Augmented Generation for Large Language Models: A Survey, 2023. arXiv:2312.10997.",
 "Bruch S, Gai S, Ingber A. An Analysis of Fusion Functions for Hybrid Retrieval[J]. ACM Transactions on Information Systems, 2023. doi:10.1145/3596512.",
 "Abirami S, et al. Evaluating Lexical, Dense, and Hybrid Retrieval Pipelines for RAG[C]//IEEE PuneCon, 2025. doi:10.1109/punecon67554.2025.11379254.",
 "LexaQuery: A Hybrid Chatbot System for University Student Information Services[J]. Mathematics and Informatics, 2026. doi:10.53656/math2026-1-4-lhc.",
 "Correctness is not Faithfulness in RAG Attributions[C]//ACM ICTIR, 2025. doi:10.1145/3731120.3744592.",
 "Evaluation of Retrieval-Augmented Generation: A Survey, 2025. doi:10.1007/978-981-96-1024-2_8.",
 "Dan Y, Lei Z, Gu Y, et al. EduChat: A Large-Scale Language Model-based Chatbot System for Intelligent Education, 2023. arXiv:2308.02773.",
 "University Chatbot System Using Generative AI with Large Language Models, 2025. doi:10.1007/978-3-031-91235-1_21.",
 "CnHallu-RAG: 中文高风险场景下检索增强生成的事实性评测, 2025. Zenodo:21190545.",
 "教育部. 关于加强新时代教育管理信息化工作的通知[Z]. 2021. 福建省教育厅转载：http://jyt.fujian.gov.cn/jglb/cwc/zcfg/202103/t20210317_5550869.htm.",
 "范贵进, 孙颖颖. 大模型和RAG驱动的校园问答平台设计与实现[J]. 电脑与电信, 2025(4): 65.",
 "whwzzc. 垂直领域大模型RAG实战：构建校园心理健康知识库智能问答系统[EB/OL]. CSDN, 2026-07-01. https://blog.csdn.net/whwzzc/article/details/162407134.",
]
for i, r in enumerate(refs, 1):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Pt(24)
    p.paragraph_format.first_line_indent = Pt(-24)
    p.paragraph_format.space_after = Pt(3)
    set_font(p.add_run("[%d] " % i), 10.5)
    set_font(p.add_run(r), 10.5)

doc.save(OUT)
print("SAVED", OUT, os.path.getsize(OUT))
print("paras", len(doc.paragraphs), "tables", len(doc.tables))
