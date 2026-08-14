from __future__ import annotations

import html
from pathlib import Path
from typing import Any, Iterable

from .common import read_json, write_text


CSS = r"""
:root {
  color-scheme: light;
  --bg: #f5f3ed;
  --paper: #faf9f5;
  --panel: #ebe7de;
  --ink: #191919;
  --body: #474747;
  --muted: #77736c;
  --line: #d5d0c7;
  --accent: #2c3e8c;
  --green: #2f6b46;
  --ochre: #8b6914;
  --rust: #98523a;
  --blue-soft: #e9ecf5;
  --green-soft: #e8efe8;
  --ochre-soft: #f1ebda;
  --toc: 11.5rem;
  --content: 49rem;
  --title-font: "Noto Serif SC", "Songti SC", "STSong", Georgia, serif;
  --body-font: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans SC", "PingFang SC", sans-serif;
  --number-font: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--body);
  font: 16.5px/1.78 var(--body-font);
  -webkit-font-smoothing: antialiased;
  overflow-wrap: anywhere;
}
a { color: var(--accent); text-underline-offset: .2em; }
a:focus-visible, summary:focus-visible { outline: 3px solid var(--accent); outline-offset: 3px; }
.skip { position: fixed; left: .5rem; top: .5rem; transform: translateY(-180%); z-index: 30; background: var(--ink); color: white; padding: .55rem .8rem; }
.skip:focus { transform: none; }
.reading-progress { position: fixed; inset: 0 auto auto 0; z-index: 25; width: 100%; height: 3px; background: var(--accent); transform: scaleX(0); transform-origin: left center; }
@supports (animation-timeline: scroll()) {
  .reading-progress { animation: reading-progress linear; animation-timeline: scroll(root block); }
  @keyframes reading-progress { to { transform: scaleX(1); } }
}
.layout { display: grid; grid-template-columns: var(--toc) minmax(0,var(--content)); justify-content: center; gap: 3rem; max-width: calc(var(--toc) + var(--content) + 3rem); margin: 0 auto; padding: 3rem 1.5rem 6rem; timeline-scope: --summary, --narrative, --method, --evidence, --claims, --critique, --profile, --concepts, --reproducibility, --questions; }
.toc { position: sticky; top: 2rem; align-self: start; max-height: calc(100vh - 4rem); overflow-y: auto; }
.toc strong { display: block; margin-bottom: .5rem; padding: 0 0 .65rem; border-bottom: 1px solid var(--line); color: var(--muted); font-size: .72rem; letter-spacing: .12em; text-transform: uppercase; }
.toc a { position: relative; display: block; margin: .06rem 0; padding: .4rem .6rem .4rem .78rem; border-radius: .28rem; color: var(--muted); font-size: .8rem; line-height: 1.45; text-decoration: none; transition: color .16s ease, background-color .16s ease; }
.toc a::before { content: ""; position: absolute; inset: .58rem auto .58rem 0; width: 2px; border-radius: 2px; background: transparent; }
.toc a:hover, .toc a:focus-visible { color: var(--accent); background: rgb(44 62 140 / .045); }
.toc a:hover::before, .toc a:focus-visible::before { background: var(--accent); }
@supports (animation-timeline: view()) {
  .toc a { animation: toc-follow 1ms linear both; animation-range: entry 70% exit 30%; }
  .toc a[href="#summary"] { animation-timeline: --summary; }
  .toc a[href="#narrative"] { animation-timeline: --narrative; }
  .toc a[href="#method"] { animation-timeline: --method; }
  .toc a[href="#evidence"] { animation-timeline: --evidence; }
  .toc a[href="#claims"] { animation-timeline: --claims; }
  .toc a[href="#critique"] { animation-timeline: --critique; }
  .toc a[href="#profile"] { animation-timeline: --profile; }
  .toc a[href="#concepts"] { animation-timeline: --concepts; }
  .toc a[href="#reproducibility"] { animation-timeline: --reproducibility; }
  .toc a[href="#questions"] { animation-timeline: --questions; }
  @keyframes toc-follow {
    0%, 100% { color: var(--muted); background: transparent; box-shadow: inset 2px 0 transparent; }
    12%, 88% { color: var(--accent); background: rgb(44 62 140 / .055); box-shadow: inset 2px 0 var(--accent); }
  }
}
main { min-width: 0; }
.article-header { margin-bottom: 2.7rem; padding-bottom: 2.35rem; border-bottom: 1px solid var(--line); }
.meta-line { display: flex; flex-wrap: wrap; gap: .9rem; margin-bottom: 1.45rem; color: var(--muted); font-size: .79rem; letter-spacing: .03em; }
h1 { margin: 0 0 1.2rem; color: var(--ink); font: 900 clamp(2.2rem, 5vw, 2.8rem)/1.22 var(--title-font); letter-spacing: .005em; }
.paper-title { margin: 0; color: var(--body); font-size: .94rem; font-style: italic; line-height: 1.55; }
.paper-title b { margin-right: .35rem; color: var(--muted); font-size: .72rem; font-style: normal; letter-spacing: .08em; text-transform: uppercase; }
.authors { margin: .5rem 0 0; color: var(--muted); font-size: .84rem; }
.tag-row { display: flex; flex-wrap: wrap; gap: .38rem; margin-top: 1rem; }
.tag { border: 1px solid var(--line); padding: .18rem .5rem; color: var(--muted); font-size: .72rem; line-height: 1.4; }
.analysis-boundary { margin-bottom: 1.35rem; padding: 1rem 1.05rem; border: 1px solid var(--line); background: var(--paper); }
.analysis-boundary dl { display: grid; grid-template-columns: repeat(3,minmax(0,1fr)); gap: 1.1rem; margin: 0; }
.analysis-boundary dt { color: var(--muted); font-size: .71rem; letter-spacing: .08em; text-transform: uppercase; }
.analysis-boundary dd { margin: .22rem 0 0; color: var(--ink); font-size: .84rem; line-height: 1.55; }
.reading-limits { margin-top: .85rem; padding-top: .7rem; border-top: 1px solid var(--line); }
.reading-limits summary { cursor: pointer; color: var(--accent); font-size: .82rem; font-weight: 650; }
.reading-limits ul { margin: .55rem 0 0; padding-left: 1.2rem; font-size: .82rem; }
.evidence-summary { margin: 0 0 1.8rem; padding: .9rem 1rem; border-left: 4px solid var(--green); background: var(--green-soft); }
.evidence-summary b { display: block; margin-bottom: .2rem; color: var(--green); font-size: .73rem; letter-spacing: .08em; text-transform: uppercase; }
.evidence-summary p { margin: 0; color: var(--ink); font-size: .95rem; line-height: 1.65; }
.metrics-figure { margin: 0 0 2.2rem; }
.metrics-figure figcaption { margin-bottom: .7rem; color: var(--muted); font-size: .72rem; letter-spacing: .08em; text-transform: uppercase; }
.metrics-strip { display: grid; grid-template-columns: repeat(var(--metric-columns),minmax(0,1fr)); gap: 0; padding: 0; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }
.metric { min-width: 0; padding: 1.15rem 1rem 1.2rem; border-top: 1px solid var(--line); border-left: 1px solid var(--line); text-align: center; }
.metrics-columns-1 .metric, .metrics-columns-2 .metric:nth-child(2n+1), .metrics-columns-3 .metric:nth-child(3n+1), .metrics-columns-4 .metric:nth-child(4n+1) { border-left: 0; }
.metrics-columns-1 .metric:first-child, .metrics-columns-2 .metric:nth-child(-n+2), .metrics-columns-3 .metric:nth-child(-n+3), .metrics-columns-4 .metric:nth-child(-n+4) { border-top: 0; }
.metric-value { display: block; color: var(--ink); font: 750 clamp(1.75rem,4vw,2.25rem)/1 var(--number-font); font-variant-numeric: tabular-nums; letter-spacing: -.035em; white-space: nowrap; }
.metric-value-long { font-size: clamp(1.3rem,2.5vw,1.52rem); letter-spacing: -.025em; }
.metric-label { display: block; margin-top: .42rem; color: var(--muted); font-size: .76rem; line-height: 1.45; }
section { scroll-margin-top: 1.6rem; margin-bottom: 4.4rem; view-timeline-axis: block; }
#summary { view-timeline-name: --summary; }
#narrative { view-timeline-name: --narrative; }
#method { view-timeline-name: --method; }
#evidence { view-timeline-name: --evidence; }
#claims { view-timeline-name: --claims; }
#critique { view-timeline-name: --critique; }
#profile { view-timeline-name: --profile; }
#concepts { view-timeline-name: --concepts; }
#reproducibility { view-timeline-name: --reproducibility; }
#questions { view-timeline-name: --questions; }
h2 { display: flex; align-items: baseline; gap: 1rem; margin: 0 0 1.5rem; color: var(--ink); font: 800 1.68rem/1.28 var(--title-font); }
h2::after { content: ""; flex: 1; border-top: 1px solid var(--line); }
h3 { margin: 1.6rem 0 .62rem; color: var(--ink); font-size: 1rem; line-height: 1.45; }
p { margin: 0 0 1rem; }
.exec-summary { padding: 1.8rem 1.9rem 1.9rem; background: var(--panel); }
.exec-summary h2 { border: 0; margin-bottom: .65rem; padding: 0; color: var(--muted); font: 700 .73rem/1.2 var(--body-font); letter-spacing: .1em; text-transform: uppercase; }
.exec-summary h2::after { display: none; }
.core-conclusion { max-width: 43rem; margin: 0 0 1.4rem; color: var(--ink); font: 900 1.44rem/1.56 var(--title-font); letter-spacing: .005em; }
.summary-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.35rem; padding-top: 1rem; border-top: 1px solid var(--line); }
.summary-grid h3, .focus h3 { margin: 0 0 .42rem; color: var(--accent); font-size: .77rem; letter-spacing: .06em; }
.summary-grid p { margin: 0; }
.focus { margin-top: 1.15rem; padding-top: .9rem; border-top: 1px solid var(--line); }
.focus ol { margin: .4rem 0 0; padding-left: 1.3rem; }
.narrative { counter-reset: narrative; }
.narrative-block { display: grid; grid-template-columns: 8.5rem minmax(0,1fr); align-items: start; gap: 1.15rem; padding: 1rem 0; border-bottom: 1px solid var(--line); counter-increment: narrative; }
.narrative-block h3 { margin: 0; color: var(--accent); font-size: .82rem; line-height: 1.78; letter-spacing: .03em; }
.narrative-block h3::before { content: "0" counter(narrative) "  "; color: var(--muted); }
.narrative-block p { margin: 0; color: var(--ink); }
.contribution-list, .claim-list, .insight-list { margin: .65rem 0 0; padding-left: 1.35rem; }
.contribution-list li, .insight-list li { margin: .65rem 0; padding-left: .25rem; }
.source-line { margin-top: .8rem; color: var(--muted); font-size: .79rem; line-height: 1.6; }
.source-line b { color: var(--body); }
.prose-block { margin-bottom: 1.2rem; }
.prose-block p { color: var(--ink); }
.method-flow { margin: 1.3rem 0; padding: 1.15rem 1.2rem; border: 1px solid var(--line); background: var(--paper); }
.method-flow figcaption { margin-bottom: .85rem; color: var(--ink); font-weight: 700; }
.process-flow { display: grid; grid-template-columns: repeat(auto-fit,minmax(8rem,1fr)); gap: 0; margin: 0; padding: 0; list-style: none; }
.process-flow li { padding: .8rem .85rem; border-top: 3px solid var(--accent); border-right: 1px solid var(--line); }
.process-flow li:nth-child(2n) { border-top-color: var(--green); }
.process-flow li:nth-child(3n) { border-top-color: var(--ochre); }
.process-flow li:last-child { border-right: 0; }
.step-index { display: block; margin-bottom: .35rem; color: var(--muted); font-size: .73rem; font-weight: 700; }
.process-flow p { margin: 0; font-size: .82rem; line-height: 1.55; }
.assumption-list { margin: 0; padding-left: 1.35rem; }
.assumption-list li { margin: .55rem 0; }
.evidence-table { width: 100%; margin: 1rem 0 1.5rem; border-collapse: collapse; font-size: .86rem; line-height: 1.55; }
.evidence-table th { padding: .65rem .7rem; border-bottom: 2px solid var(--line); color: var(--muted); font-size: .7rem; letter-spacing: .06em; text-align: left; text-transform: uppercase; }
.evidence-table td { padding: .75rem .7rem; border-bottom: 1px solid var(--line); vertical-align: top; }
.evidence-table td:first-child { color: var(--ink); font-weight: 650; }
.evidence-synthesis { display: grid; grid-template-columns: repeat(3,minmax(0,1fr)); gap: 1rem; margin-top: 1.4rem; }
.evidence-synthesis article { padding-top: .75rem; border-top: 3px solid var(--green); }
.evidence-synthesis article:nth-child(2) { border-top-color: var(--rust); }
.evidence-synthesis article:nth-child(3) { border-top-color: var(--ochre); }
.evidence-synthesis h3 { margin: 0 0 .4rem; font-size: .83rem; }
.evidence-synthesis p { margin: 0; font-size: .88rem; line-height: 1.65; }
.claim-list { list-style: decimal-leading-zero; }
.claim-list li { margin: 0 0 1.15rem; padding: 0 0 1rem .35rem; border-bottom: 1px solid var(--line); }
.claim-text { color: var(--ink); font-weight: 650; }
.claim-support { margin: .35rem 0 0; color: var(--body); }
.claim-support b { color: var(--muted); font-size: .78rem; letter-spacing: .04em; }
.critical-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.8rem 2.2rem; counter-reset: critical; }
.critical-block { position: relative; padding: 1.05rem 0 0 2.4rem; border-top: 1px solid var(--line); counter-increment: critical; }
.critical-block::before { content: counter(critical, decimal-leading-zero); position: absolute; left: 0; top: 1.08rem; color: var(--rust); font: 700 .76rem/1 var(--number-font); letter-spacing: .04em; }
.critical-block h3 { margin: 0 0 .62rem; font: 750 1.03rem/1.38 var(--title-font); }
.critical-block ol { margin: 0; padding-left: 1.25rem; }
.critical-block li { margin: .5rem 0; }
.overall-judgment { margin-top: 1.5rem; padding: 1.1rem 1.2rem; background: var(--ochre-soft); border-left: 4px solid var(--ochre); }
.overall-judgment h3 { margin: 0 0 .4rem; color: var(--ochre); }
.overall-judgment p { margin: 0; color: var(--ink); }
.profile-summary { padding: 1.2rem 1.3rem; background: var(--blue-soft); }
.profile-verdicts { display: flex; gap: 2rem; margin-bottom: .8rem; }
.profile-verdicts span { color: var(--muted); font-size: .72rem; letter-spacing: .07em; text-transform: uppercase; }
.profile-verdicts strong { display: block; margin-top: .2rem; color: var(--ink); font: 800 1.25rem/1.25 var(--title-font); letter-spacing: 0; text-transform: none; }
.profile-summary p { margin: 0; color: var(--ink); }
.concept-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0 2.2rem; counter-reset: concept; }
.concept { position: relative; padding: 1.25rem 0 1.35rem 2.4rem; border-top: 1px solid var(--line); counter-increment: concept; }
.concept::before { content: counter(concept, decimal-leading-zero); position: absolute; left: 0; top: 1.42rem; color: var(--accent); font: 700 .76rem/1 var(--number-font); letter-spacing: .04em; }
.concept h3 { margin: 0 0 .12rem; color: var(--ink); font: 800 1.08rem/1.35 var(--title-font); }
.concept .term-en { color: var(--muted); font-size: .75rem; }
.concept p { margin: .62rem 0 0; font-size: .9rem; line-height: 1.7; }
.concept b { color: var(--body); }
dl.repro { display: grid; grid-template-columns: max-content 1fr; gap: .4rem 1rem; padding: 1rem 1.1rem; background: var(--panel); }
dl.repro dt { color: var(--muted); }
dl.repro dd { margin: 0; color: var(--ink); }
.clean { list-style: none; padding: 0; }
.clean li { margin: .4rem 0; }
footer { padding: 1.4rem 1.5rem; border-top: 1px solid var(--line); color: var(--muted); font-size: .76rem; text-align: center; }
footer .top-link { display: inline-block; margin-top: .4rem; }
@media (max-width: 760px) {
  body { font-size: 16px; }
  .layout { display: block; padding: 1rem .9rem 3rem; }
  .toc { position: static; display: flex; gap: .4rem; overflow-x: auto; padding: .2rem 0 .85rem; border-bottom: 1px solid var(--line); }
  .toc strong { display: none; }
  .toc a { flex: 0 0 auto; padding: .32rem .46rem; border-left: 0; border-bottom: 2px solid transparent; }
  .article-header { margin-top: 1.5rem; margin-bottom: 1.8rem; }
  h1 { font-size: 2.05rem; }
  .analysis-boundary dl, .summary-grid, .evidence-synthesis, .critical-grid, .concept-grid { grid-template-columns: 1fr; }
  .analysis-boundary dl { gap: .8rem; }
  .metrics-strip { grid-template-columns: repeat(2,minmax(0,1fr)); }
  .metrics-strip .metric { padding: .9rem .8rem; border-top: 1px solid var(--line); border-left: 0; }
  .metrics-strip .metric:nth-child(-n+2) { border-top: 0; }
  .metrics-strip .metric:nth-child(even) { border-left: 1px solid var(--line); }
  .narrative-block { grid-template-columns: 1fr; gap: .25rem; }
  .process-flow { grid-template-columns: 1fr; }
  .process-flow li { border-right: 0; border-bottom: 1px solid var(--line); }
  .evidence-table thead { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); }
  .evidence-table, .evidence-table tbody, .evidence-table tr, .evidence-table td { display: block; width: 100%; }
  .evidence-table tr { padding: .7rem 0; border-bottom: 1px solid var(--line); }
  .evidence-table td { padding: .18rem 0; border: 0; }
  .profile-verdicts { gap: 1rem; }
}
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  .toc a { transition: none; }
}
@media print {
  :root { --bg: white; --paper: white; }
  body { font-size: 10.5pt; }
  .reading-progress, .toc, .skip { display: none; }
  .layout { display: block; max-width: none; padding: 0; }
  h1 { font-size: 25pt; }
  section { break-inside: auto; }
  .concept, .critical-block, .method-flow, .profile-summary { break-inside: avoid; }
  a { color: inherit; text-decoration: none; }
  footer { padding-inline: 0; }
}
"""


ZH = {
    "toc": "目录", "summary": "执行摘要", "narrative": "论文如何建立问题与贡献", "method": "方法",
    "evidence": "证据", "claims": "核心主张与支持", "critique": "批判", "profile": "定向视角",
    "concepts": "概念", "repro": "可复现性", "questions": "开放问题", "paper": "原文", "paper_source": "查看论文来源",
    "analysis_basis": "阅读依据", "judgment_source": "判断来源", "generation": "生成说明",
    "evidence_overview": "证据概况", "reading_limits": "阅读限制", "key_metrics": "关键指标",
    "why": "为什么重要", "bottom": "分析判断", "focus": "关注问题", "research_context": "研究背景",
    "prior_work_gap": "前人工作的遗漏", "problem_importance": "为什么这个问题重要", "proposed_solution": "论文采用的方法",
    "main_findings": "主要发现", "contribution_list": "作者列出的主要贡献", "problem": "问题定义",
    "approach": "方法框架", "workflow": "方法流程", "assumptions": "关键假设", "experiment": "实验",
    "scope": "范围与规模", "measures": "观察指标", "finding": "主要结果", "evidence_strengths": "证据特点",
    "evidence_weaknesses": "证据缺陷", "evidence_reuse": "可复用性", "support": "论文如何支持",
    "strengths": "方法与证据优势", "claim_gaps": "主张与证据之间的差距", "prior_comparison": "与既有工作及 SOTA 的关系",
    "limitations": "研究范围与方法局限", "threats": "有效性与泛化风险", "missing": "缺失证据与后续验证",
    "judgment": "总体判断", "applicability": "直接适用性", "difficulty": "集成难度", "plain": "通俗理解",
    "concept_value": "为什么重要", "code": "代码", "data": "数据", "environment": "环境", "references": "参考链接",
    "sources": "来源位置", "generated": "由已验证的 analysis.json 确定性生成", "back_top": "返回顶部", "skip": "跳至正文",
    "model": "模型", "host": "运行环境", "license": "论文许可", "unknown_date": "日期未知", "unknown_venue": "发表信息未知",
    "full_text": "PDF 全文", "partial_text": "部分正文", "abstract_only": "仅摘要", "general": "通用",
    "agent-systems": "Agent 系统", "agent-evaluation": "Agent 评测", "harness": "Harness", "memory": "Memory",
    "continual-learning": "持续学习", "multi-agent": "多 Agent", "tool-use": "工具使用",
    "reasoning-planning": "推理与规划", "data-agent": "Data Agent", "embodied-agent": "具身 Agent", "custom": "自定义",
    "high": "高", "medium": "中", "low": "低", "unknown": "未知", "not_applicable": "不适用",
    "available": "可用", "partial": "部分可用", "unavailable": "不可用", "not_reported": "未报告", "specified": "已说明",
}

EN = {
    "toc": "On this page", "summary": "Executive summary", "narrative": "How the paper builds its case", "method": "Method",
    "evidence": "Evidence", "claims": "Core claims and support", "critique": "Critical assessment", "profile": "Directed perspective",
    "concepts": "Concepts", "repro": "Reproducibility", "questions": "Open questions", "paper": "Paper", "paper_source": "Paper source",
    "analysis_basis": "Reading basis", "judgment_source": "Judgment source", "generation": "Generation disclosure",
    "evidence_overview": "Evidence overview", "reading_limits": "Reading limits", "key_metrics": "Key metrics",
    "why": "Why it matters", "bottom": "Analyst verdict", "focus": "Focus questions", "research_context": "Research context",
    "prior_work_gap": "Prior-work gap", "problem_importance": "Why the problem matters", "proposed_solution": "Proposed solution",
    "main_findings": "Main findings", "contribution_list": "Author-stated contributions", "problem": "Problem",
    "approach": "Approach", "workflow": "Method flow", "assumptions": "Assumptions", "experiment": "Experiment",
    "scope": "Scope", "measures": "Measures", "finding": "Finding", "evidence_strengths": "Evidence strengths",
    "evidence_weaknesses": "Evidence weaknesses", "evidence_reuse": "Reusability", "support": "How the paper supports it",
    "strengths": "Method and evidence strengths", "claim_gaps": "Claim-evidence gaps", "prior_comparison": "Relationship to prior work and SOTA",
    "limitations": "Scope and method limitations", "threats": "Validity and generalization risks", "missing": "Missing evidence and follow-up",
    "judgment": "Overall judgment", "applicability": "Direct applicability", "difficulty": "Integration difficulty", "plain": "Plain language",
    "concept_value": "Why it matters", "code": "Code", "data": "Data", "environment": "Environment", "references": "References",
    "sources": "Source locations", "generated": "Deterministically rendered from validated analysis.json", "back_top": "Back to top", "skip": "Skip to analysis",
    "model": "Model", "host": "Host", "license": "Paper license", "unknown_date": "date unknown", "unknown_venue": "venue unknown",
}


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def enum_text(value: str, labels: dict[str, str]) -> str:
    return labels.get(value, value.replace("_", " "))


def anchor_label(anchor: dict[str, Any]) -> str:
    parts = []
    if anchor.get("page"):
        parts.append(f"p. {anchor['page']}")
    for field, prefix in (("section", "§"), ("figure", ""), ("table", "")):
        if anchor.get(field):
            parts.append(f"{prefix}{anchor[field]}")
    return " · ".join(parts) or "source context"


def collect_anchors(items: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    anchors: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in items:
        for anchor in item.get("anchors", []):
            key = repr(tuple(anchor.get(field) for field in ("page", "section", "figure", "table")))
            if key not in seen:
                seen.add(key)
                anchors.append(anchor)
    return anchors


def source_line(items: Iterable[dict[str, Any]], labels: dict[str, str]) -> str:
    anchors = collect_anchors(items)
    if not anchors:
        return ""
    values = "；".join(esc(anchor_label(anchor)) for anchor in anchors)
    return f'<p class="source-line"><b>{labels["sources"]}：</b>{values}</p>'


def render_metrics(metrics: list[dict[str, Any]], labels: dict[str, str]) -> str:
    if not metrics:
        return ""
    column_count = 3 if len(metrics) >= 5 else len(metrics)
    cells = "".join(
        f'<div class="metric"><span class="metric-value{" metric-value-long" if len(str(item["value"])) >= 7 else ""}">{esc(item["value"])}</span>'
        f'<span class="metric-label">{esc(item["label"])}</span></div>' for item in metrics
    )
    return f'<figure class="metrics-figure"><figcaption>{labels["key_metrics"]}</figcaption><div class="metrics-strip metrics-columns-{column_count}" style="--metric-columns:{column_count}">{cells}</div></figure>'


def render_narrative(narrative: dict[str, Any], contributions: list[dict[str, Any]], labels: dict[str, str]) -> str:
    order = ("research_context", "prior_work_gap", "problem_importance", "proposed_solution", "main_findings")
    blocks = "".join(
        f'<article class="narrative-block"><h3>{labels[key]}</h3><p>{esc(narrative[key]["text"])}</p></article>' for key in order
    )
    contribution_items = "".join(f'<li>{esc(item["text"])}</li>' for item in contributions)
    all_items = [narrative[key] for key in order] + contributions
    return f'<div class="narrative">{blocks}</div><h3>{labels["contribution_list"]}</h3><ol class="contribution-list">{contribution_items}</ol>{source_line(all_items, labels)}'


def render_method_flow(items: list[dict[str, Any]], labels: dict[str, str]) -> str:
    steps = "".join(
        f'<li><span class="step-index">{index:02d}</span><p>{esc(item["text"])}</p></li>' for index, item in enumerate(items, 1)
    )
    return f'<figure class="method-flow"><figcaption>{labels["workflow"]}</figcaption><ol class="process-flow">{steps}</ol>{source_line(items, labels)}</figure>'


def render_evidence(synthesis: dict[str, Any], labels: dict[str, str]) -> str:
    rows = "".join(
        f'<tr><td>{esc(item["name"])}</td><td>{esc(item["scope"])}</td><td>{esc(item["measures"])}</td><td>{esc(item["finding"])}</td></tr>'
        for item in synthesis["experiments"]
    )
    summary_items = (("evidence_strengths", synthesis["strengths"]), ("evidence_weaknesses", synthesis["weaknesses"]), ("evidence_reuse", synthesis["reusability"]))
    summaries = "".join(f'<article><h3>{labels[key]}</h3><p>{esc(item["text"])}</p></article>' for key, item in summary_items)
    all_items = list(synthesis["experiments"]) + [item for _, item in summary_items]
    return (
        f'<table class="evidence-table"><thead><tr><th>{labels["experiment"]}</th><th>{labels["scope"]}</th>'
        f'<th>{labels["measures"]}</th><th>{labels["finding"]}</th></tr></thead><tbody>{rows}</tbody></table>'
        f'<div class="evidence-synthesis">{summaries}</div>{source_line(all_items, labels)}'
    )


def render_claims(claims: list[dict[str, Any]], labels: dict[str, str]) -> str:
    items = "".join(
        f'<li><p class="claim-text">{esc(item["text"])}</p><p class="claim-support"><b>{labels["support"]}：</b>{esc(item["support"])}</p>'
        f'{source_line([item], labels)}</li>' for item in claims
    )
    return f'<ol class="claim-list">{items}</ol>'


def render_critical_block(title: str, items: list[dict[str, Any]], labels: dict[str, str]) -> str:
    points = "".join(f'<li>{esc(item["text"])}</li>' for item in items)
    return f'<article class="critical-block"><h3>{esc(title)}</h3><ol>{points}</ol>{source_line(items, labels)}</article>'


def render_concepts(concepts: list[dict[str, Any]], labels: dict[str, str]) -> str:
    cards = "".join(
        f'<article class="concept"><h3>{esc(item["term"])}</h3><div class="term-en">{esc(item.get("term_en") or "")}</div>'
        f'<p>{esc(item["definition"])}</p><p><b>{labels["plain"]}：</b>{esc(item["plain_language"])}</p>'
        f'<p><b>{labels["concept_value"]}：</b>{esc(item["why_it_matters"])}</p></article>' for item in concepts
    )
    return f'<div class="concept-grid">{cards}</div>{source_line(concepts, labels)}'


def render_report(analysis: dict[str, Any]) -> str:
    paper = analysis["paper"]
    context = analysis["analysis_context"]
    boundary = analysis["analysis_boundary"]
    summary = analysis["executive_summary"]
    narrative = analysis["paper_narrative"]
    method = analysis["method"]
    critical = analysis["critical_assessment"]
    profile = analysis["profile_analysis"]
    reproduction = analysis["reproducibility"]
    is_zh = context["language"].lower().startswith("zh")
    labels = ZH if is_zh else EN
    lang = "zh-CN" if is_zh else context["language"]
    source_link = f'<a href="{esc(paper["source_url"])}" rel="noreferrer">{labels["paper_source"]}</a>' if paper.get("source_url") else ""
    focus = "".join(f'<li>{esc(question)}</li>' for question in context["focus_questions"])
    warnings = ""
    if boundary["extraction_warnings"]:
        warning_items = "".join(f'<li>{esc(item)}</li>' for item in boundary["extraction_warnings"])
        warnings = f'<details class="reading-limits"><summary>{labels["reading_limits"]}</summary><ul>{warning_items}</ul></details>'
    basis_text = (
        f'{enum_text(boundary["basis"], labels)}；已核查 {len(boundary["visuals_inspected"])} 处关键图表或表格。'
        if is_zh else f'{enum_text(boundary["basis"], labels)}; {len(boundary["visuals_inspected"])} key figures or tables inspected.'
    )
    judgment_text = (
        "不设置自定义总分；论文主张、分析推断和迁移启示分别记录，所有重要判断都需要证据锚点。"
        if is_zh else "No custom overall score; paper claims, analyst inferences, and derived lessons are separated and anchored."
    )
    generation_text = (
        f'由 {boundary["model"]} 在 {boundary["host"]} 中辅助生成；未声称已完成人工逐条核验。'
        if is_zh else f'Assisted by {boundary["model"]} in {boundary["host"]}; no claim of completed line-by-line human verification.'
    )
    critical_grid = "".join((
        render_critical_block(labels["strengths"], critical["strengths"], labels),
        render_critical_block(labels["claim_gaps"], critical["claim_evidence_gaps"], labels),
        render_critical_block(labels["prior_comparison"], critical["comparison_to_prior_work"], labels),
        render_critical_block(labels["limitations"], critical["limitations"], labels),
        render_critical_block(labels["threats"], critical["threats_to_validity"], labels),
        render_critical_block(labels["missing"], critical["missing_evidence"], labels),
    ))
    refs = "".join(
        f'<li><a href="{esc(ref["url"])}" rel="noreferrer">{esc(ref["label"])}</a> · {esc(ref["kind"])}</li>' for ref in analysis["references"]
    ) or "<li>—</li>"
    insight_items = "".join(f'<li>{esc(item["text"])}</li>' for item in profile["insights"])
    return f'''<!doctype html>
<html lang="{esc(lang)}">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="color-scheme" content="light"><title>{esc(summary["headline"])} — Deep analysis</title><style>{CSS}</style></head>
<body>
<div class="reading-progress" aria-hidden="true"></div>
<a class="skip" href="#main">{labels["skip"]}</a>
<div class="layout">
  <nav class="toc" aria-label="{labels["toc"]}"><strong>{labels["toc"]}</strong><a href="#summary">{labels["summary"]}</a><a href="#narrative">{labels["narrative"]}</a><a href="#method">{labels["method"]}</a><a href="#evidence">{labels["evidence"]}</a><a href="#claims">{labels["claims"]}</a><a href="#critique">{labels["critique"]}</a><a href="#profile">{labels["profile"]}</a><a href="#concepts">{labels["concepts"]}</a><a href="#reproducibility">{labels["repro"]}</a><a href="#questions">{labels["questions"]}</a></nav>
  <main id="main">
    <header class="article-header"><div class="meta-line"><span>{paper.get("published") or labels["unknown_date"]}</span><span>{esc(paper.get("venue") or labels["unknown_venue"])}</span><span>{esc(paper["stable_id"])}</span></div><h1>{esc(summary["headline"])}</h1><p class="paper-title"><b>{labels["paper"]}</b>{esc(paper["title"])} {source_link}</p><p class="authors">{esc(" · ".join(paper["authors"]))}</p><div class="tag-row"><span class="tag">{esc(enum_text(context["profile"], labels))}</span><span class="tag">{esc(enum_text(boundary["basis"], labels))}</span><span class="tag">{esc(paper["license"])}</span></div></header>
    <aside class="analysis-boundary" aria-label="分析边界与生成说明"><dl><div><dt>{labels["analysis_basis"]}</dt><dd>{esc(basis_text)}</dd></div><div><dt>{labels["judgment_source"]}</dt><dd>{esc(judgment_text)}</dd></div><div><dt>{labels["generation"]}</dt><dd>{esc(generation_text)}</dd></div></dl>{warnings}</aside>
    <aside class="evidence-summary"><b>{labels["evidence_overview"]}</b><p>{esc(summary["evidence_summary"])}</p></aside>
    {render_metrics(analysis.get("key_metrics", []), labels)}
    <section id="summary" class="exec-summary"><h2>{labels["summary"]}</h2><p class="core-conclusion">{esc(summary["core_conclusion"])}</p><div class="summary-grid"><div><h3>{labels["why"]}</h3><p>{esc(summary["why_it_matters"])}</p></div><div><h3>{labels["bottom"]}</h3><p>{esc(summary["analyst_verdict"])}</p></div></div><div class="focus"><h3>{labels["focus"]}</h3><ol>{focus}</ol></div></section>
    <section id="narrative"><h2>{labels["narrative"]}</h2>{render_narrative(narrative, analysis["contributions"], labels)}</section>
    <section id="method"><h2>{labels["method"]}</h2><div class="prose-block"><h3>{labels["problem"]}</h3><p>{esc(method["problem"]["text"])}</p>{source_line([method["problem"]], labels)}</div><div class="prose-block"><h3>{labels["approach"]}</h3><p>{esc(method["approach"]["text"])}</p>{source_line([method["approach"]], labels)}</div>{render_method_flow(method["workflow"], labels)}<h3>{labels["assumptions"]}</h3><ol class="assumption-list">{"".join(f'<li>{esc(item["text"])}</li>' for item in method["assumptions"])}</ol>{source_line(method["assumptions"], labels)}</section>
    <section id="evidence"><h2>{labels["evidence"]}</h2>{render_evidence(analysis["evidence_synthesis"], labels)}</section>
    <section id="claims"><h2>{labels["claims"]}</h2>{render_claims(analysis["claims"], labels)}</section>
    <section id="critique"><h2>{labels["critique"]}</h2><div class="critical-grid">{critical_grid}</div><article class="overall-judgment"><h3>{labels["judgment"]}</h3><p>{esc(critical["overall_judgment"]["text"])}</p>{source_line([critical["overall_judgment"]], labels)}</article></section>
    <section id="profile"><h2>{esc(enum_text(profile["profile"], labels))} · {labels["profile"]}</h2><div class="profile-summary"><div class="profile-verdicts"><span>{labels["applicability"]}<strong>{esc(enum_text(profile["applicability"], labels))}</strong></span><span>{labels["difficulty"]}<strong>{esc(enum_text(profile["integration_difficulty"], labels))}</strong></span></div><p>{esc(profile["summary"]["text"])}</p>{source_line([profile["summary"]], labels)}</div><ol class="insight-list">{insight_items}</ol>{source_line(profile["insights"], labels)}</section>
    <section id="concepts"><h2>{labels["concepts"]}</h2>{render_concepts(analysis["concepts"], labels)}</section>
    <section id="reproducibility"><h2>{labels["repro"]}</h2><dl class="repro"><dt>{labels["code"]}</dt><dd>{esc(enum_text(reproduction["code"], labels))}</dd><dt>{labels["data"]}</dt><dd>{esc(enum_text(reproduction["data"], labels))}</dd><dt>{labels["environment"]}</dt><dd>{esc(enum_text(reproduction["environment"], labels))}</dd></dl><p>{esc(reproduction["replication_notes"]["text"])}</p>{source_line([reproduction["replication_notes"]], labels)}</section>
    <section id="questions"><h2>{labels["questions"]}</h2><ol class="insight-list">{"".join(f'<li>{esc(item["text"])}</li>' for item in analysis["open_questions"])}</ol>{source_line(analysis["open_questions"], labels)}<h3>{labels["references"]}</h3><ul class="clean">{refs}</ul></section>
  </main>
</div>
<footer>{labels["generated"]}。{labels["model"]}：{esc(boundary["model"])} · {labels["host"]}：{esc(boundary["host"])} · {labels["license"]}：{esc(paper["license"])}<br><a class="top-link" href="#main">{labels["back_top"]}</a></footer>
</body></html>'''


def render_file(analysis_path: Path, output_path: Path) -> None:
    write_text(output_path, render_report(read_json(analysis_path)))
