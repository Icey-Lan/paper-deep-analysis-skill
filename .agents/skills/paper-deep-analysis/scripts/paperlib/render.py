from __future__ import annotations

import html
from pathlib import Path
from typing import Any

from .common import read_json, write_text


CSS = r"""
:root {
  color-scheme: light;
  --ink: #172033;
  --muted: #5d6678;
  --paper: #fbfaf7;
  --card: #ffffff;
  --line: #dfe3e8;
  --accent: #2f5f55;
  --accent-soft: #e7f0ed;
  --warm: #a4512c;
  --warning: #fff3d6;
  --max: 76rem;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  color: var(--ink);
  background: var(--paper);
  font: 16px/1.65 ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  overflow-wrap: anywhere;
}
a { color: var(--accent); text-underline-offset: .18em; }
a:focus-visible { outline: 3px solid #f0a15c; outline-offset: 3px; }
.skip { position: absolute; left: -9999px; top: 0; }
.skip:focus { left: 1rem; top: 1rem; z-index: 10; background: white; padding: .6rem .9rem; }
.hero { background: #18352f; color: #f7fbf9; padding: 3.5rem max(1.25rem, calc((100vw - var(--max))/2)); }
.eyebrow { margin: 0 0 .8rem; color: #b9d4cc; font-size: .78rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; }
h1 { max-width: 22ch; margin: 0; font: 700 clamp(2rem, 5vw, 4.3rem)/1.05 ui-serif, Georgia, serif; letter-spacing: -.025em; }
.authors { max-width: 70ch; margin: 1.2rem 0 .4rem; color: #d9e6e2; }
.hero-meta { display: flex; flex-wrap: wrap; gap: .55rem; margin-top: 1.5rem; }
.hero-meta span, .pill { border: 1px solid currentColor; border-radius: 999px; padding: .25rem .65rem; font-size: .78rem; }
.layout { width: min(var(--max), calc(100% - 2rem)); margin: 0 auto; display: grid; grid-template-columns: 15rem minmax(0,1fr); gap: 2.5rem; }
nav { position: sticky; top: 1rem; align-self: start; padding: 1.5rem 0; }
nav strong { display: block; margin-bottom: .6rem; }
nav a { display: block; padding: .3rem 0; color: var(--muted); text-decoration: none; }
main { min-width: 0; padding: 2.5rem 0 5rem; }
section { scroll-margin-top: 1rem; margin-bottom: 3.5rem; }
h2 { margin: 0 0 1rem; font: 700 clamp(1.55rem, 3vw, 2.2rem)/1.2 ui-serif, Georgia, serif; }
h3 { margin: 1.4rem 0 .6rem; font-size: 1rem; }
.lede { font-size: clamp(1.12rem, 2vw, 1.35rem); line-height: 1.55; }
.grid { display: grid; grid-template-columns: repeat(2,minmax(0,1fr)); gap: 1rem; }
.card { background: var(--card); border: 1px solid var(--line); border-radius: 14px; padding: 1.15rem; box-shadow: 0 10px 24px rgb(18 37 32 / .04); }
.card > :first-child { margin-top: 0; }
.card > :last-child { margin-bottom: 0; }
.statement { border-left: 4px solid var(--accent); }
.statement[data-strength="weak"], .statement[data-strength="not_reported"] { border-left-color: var(--warm); }
.meta { display: flex; flex-wrap: wrap; gap: .4rem; margin-top: .8rem; color: var(--muted); }
.anchor { background: var(--accent-soft); border-radius: 999px; padding: .2rem .5rem; font-size: .75rem; }
.warning { background: var(--warning); border: 1px solid #e5c875; border-radius: 12px; padding: 1rem; }
.status { font-weight: 700; color: var(--accent); }
dl { display: grid; grid-template-columns: max-content 1fr; gap: .4rem 1rem; }
dt { color: var(--muted); }
dd { margin: 0; }
ul.clean { list-style: none; padding: 0; }
ul.clean > li { margin-bottom: .85rem; }
footer { border-top: 1px solid var(--line); padding: 2rem max(1rem, calc((100vw - var(--max))/2)); color: var(--muted); }
@media (max-width: 760px) {
  .hero { padding-top: 2.5rem; padding-bottom: 2.5rem; }
  .layout { display: block; width: min(100% - 1.25rem, var(--max)); }
  nav { position: static; border-bottom: 1px solid var(--line); display: flex; gap: .8rem; overflow-x: auto; }
  nav strong { display: none; }
  nav a { white-space: nowrap; }
  .grid { grid-template-columns: 1fr; }
  main { padding-top: 1.5rem; }
}
@media print {
  :root { --paper: white; }
  body { font-size: 10.5pt; }
  .hero { background: white; color: black; padding: 0 0 1.5rem; border-bottom: 2px solid black; }
  .authors, .eyebrow { color: #333; }
  .layout { display: block; width: 100%; }
  nav, .skip { display: none; }
  main { padding: 1.5rem 0; }
  .card { box-shadow: none; break-inside: avoid; }
  section { break-before: auto; }
  a { color: inherit; text-decoration: none; }
}
"""


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def anchor_label(anchor: dict[str, Any]) -> str:
    parts = []
    if anchor.get("page"):
        parts.append(f"p. {anchor['page']}")
    for field, prefix in (("section", "§"), ("figure", ""), ("table", "")):
        if anchor.get(field):
            parts.append(f"{prefix}{anchor[field]}")
    return " · ".join(parts) or "source context"


def render_anchors(anchors: list[dict[str, Any]]) -> str:
    return "".join(
        f'<span class="anchor" title="{esc(anchor.get("note", ""))}">{esc(anchor_label(anchor))}</span>'
        for anchor in anchors
    )


def render_statement(item: dict[str, Any]) -> str:
    return (
        f'<article class="card statement" data-strength="{esc(item["evidence_strength"])}">'
        f'<p>{esc(item["text"])}</p>'
        '<div class="meta">'
        f'<span class="pill">{esc(item["attribution"])}</span>'
        f'<span class="pill">confidence: {esc(item["confidence"])}</span>'
        f'<span class="pill">evidence: {esc(item["evidence_strength"])}</span>'
        f'{render_anchors(item["anchors"])}'
        '</div></article>'
    )


def render_list(items: list[dict[str, Any]], empty: str = "No item reported.") -> str:
    if not items:
        return f'<p class="warning">{esc(empty)}</p>'
    return '<div class="grid">' + "".join(render_statement(item) for item in items) + "</div>"


def render_assessment(evidence: dict[str, Any]) -> str:
    cards = []
    for key, value in evidence.items():
        label = key.replace("_", " ").title()
        cards.append(
            '<article class="card">'
            f'<h3>{esc(label)}</h3><p class="status">{esc(value["status"])}</p>'
            f'<p>{esc(value["summary"])}</p><div class="meta">{render_anchors(value["anchors"])}</div>'
            '</article>'
        )
    return '<div class="grid">' + "".join(cards) + "</div>"


def render_report(analysis: dict[str, Any]) -> str:
    paper = analysis["paper"]
    context = analysis["analysis_context"]
    boundary = analysis["analysis_boundary"]
    summary = analysis["executive_summary"]
    method = analysis["method"]
    critical = analysis["critical_assessment"]
    reproduction = analysis["reproducibility"]
    lang = "zh-CN" if context["language"].lower().startswith("zh") else context["language"]
    source_link = ""
    if paper.get("source_url"):
        source_link = f'<a href="{esc(paper["source_url"])}" rel="noreferrer">Source</a>'
    warnings = ""
    if boundary["basis"] != "full_text" or boundary["extraction_warnings"]:
        warning_text = [f'Analysis basis: {boundary["basis"]}.'] + boundary["extraction_warnings"]
        warnings = '<div class="warning"><strong>Reading boundary</strong><ul>' + "".join(f'<li>{esc(item)}</li>' for item in warning_text) + '</ul></div>'
    refs = "".join(
        f'<li><a href="{esc(ref["url"])}" rel="noreferrer">{esc(ref["label"])}</a> <span class="pill">{esc(ref["kind"])}</span></li>'
        for ref in analysis["references"]
    ) or "<li>No external reference recorded.</li>"
    focus = "".join(f"<li>{esc(question)}</li>" for question in context["focus_questions"]) or "<li>General deep analysis.</li>"
    return f'''<!doctype html>
<html lang="{esc(lang)}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light">
  <title>{esc(paper["title"])} — Deep analysis</title>
  <style>{CSS}</style>
</head>
<body>
<a class="skip" href="#main">Skip to analysis</a>
<header class="hero">
  <p class="eyebrow">Evidence-grounded paper analysis</p>
  <h1>{esc(paper["title"])}</h1>
  <p class="authors">{esc(" · ".join(paper["authors"]))}</p>
  <div class="hero-meta"><span>{esc(context["profile"])}</span><span>{esc(boundary["basis"])}</span><span>{esc(paper["stable_id"])}</span>{source_link}</div>
</header>
<div class="layout">
  <nav aria-label="Report sections"><strong>On this page</strong><a href="#summary">Summary</a><a href="#contributions">Contributions</a><a href="#method">Method</a><a href="#evidence">Evidence</a><a href="#claims">Claims</a><a href="#critique">Critique</a><a href="#profile">Profile</a><a href="#reproducibility">Reproducibility</a><a href="#questions">Questions</a></nav>
  <main id="main">
    <section id="summary"><h2>Executive summary</h2>{warnings}<p class="lede">{esc(summary["one_sentence"])}</p><div class="grid"><article class="card"><h3>Why it matters</h3><p>{esc(summary["why_it_matters"])}</p></article><article class="card"><h3>Bottom line</h3><p>{esc(summary["bottom_line"])}</p></article></div><h3>Focus questions</h3><ul>{focus}</ul></section>
    <section id="contributions"><h2>Contributions</h2>{render_list(analysis["contributions"])}</section>
    <section id="method"><h2>Method and assumptions</h2><h3>Problem</h3>{render_statement(method["problem"])}<h3>Approach</h3>{render_statement(method["approach"])}<h3>Workflow</h3>{render_list(method["workflow"])}<h3>Assumptions</h3>{render_list(method["assumptions"], "No explicit assumption captured.")}</section>
    <section id="evidence"><h2>Evidence assessment</h2>{render_assessment(analysis["evidence_assessment"])}</section>
    <section id="claims"><h2>Claim ledger</h2>{render_list(analysis["claims"])}</section>
    <section id="critique"><h2>Critical assessment</h2><h3>Strengths</h3>{render_list(critical["strengths"], "No strength captured.")}<h3>Limitations</h3>{render_list(critical["limitations"])}<h3>Threats to validity</h3>{render_list(critical["threats_to_validity"], "No threat captured.")}<h3>Missing evidence</h3>{render_list(critical["missing_evidence"], "No missing evidence captured.")}<h3>Calibrated judgment</h3>{render_statement(critical["overall_judgment"])}</section>
    <section id="profile"><h2>{esc(analysis["profile_analysis"]["profile"])} perspective</h2>{render_list(analysis["profile_analysis"]["insights"], "No profile-specific insight captured.")}</section>
    <section id="reproducibility"><h2>Reproducibility</h2><dl><dt>Code</dt><dd>{esc(reproduction["code"])}</dd><dt>Data</dt><dd>{esc(reproduction["data"])}</dd><dt>Environment</dt><dd>{esc(reproduction["environment"])}</dd></dl>{render_statement(reproduction["replication_notes"])}</section>
    <section id="questions"><h2>Open questions</h2>{render_list(analysis["open_questions"], "No open question captured.")}<h3>References</h3><ul class="clean">{refs}</ul></section>
  </main>
</div>
<footer>Generated from validated analysis JSON. Model: {esc(boundary["model"])} · Host: {esc(boundary["host"])} · Paper license: {esc(paper["license"])}</footer>
</body>
</html>'''


def render_file(analysis_path: Path, output_path: Path) -> None:
    write_text(output_path, render_report(read_json(analysis_path)))
