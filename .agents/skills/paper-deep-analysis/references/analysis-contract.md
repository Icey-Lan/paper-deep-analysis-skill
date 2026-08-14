# Analysis contract

The report should help a technically literate reader decide what the paper says,
how well it supports those claims, what transfers to practice, and what remains
uncertain.

## Core questions

1. What concrete problem is solved, for whom, under which assumptions?
2. What is genuinely new relative to the comparison set named by the paper?
3. How does the method or system work end to end?
4. Which experiments support each major claim, and which claims are unsupported?
5. Are baselines, metrics, ablations, and datasets adequate for the conclusion?
6. What failure modes, costs, safety issues, or external-validity limits matter?
7. What can a practitioner reuse now, and what needs independent verification?
8. Which questions should future research or a replication answer?

## Profile overlays

`general` adds no domain-specific required section.

`agent-systems` examines harness/runtime assumptions, tool use, memory, planning,
multi-agent coordination, evaluation realism, observability, safety, cost, and
self-improvement or continual-learning claims.

`data-agent` examines data discovery, semantic layers, SQL/code generation,
pipeline orchestration, data quality, lineage, metadata, governance, human
review, benchmark realism, and operational integration with data engineering.

`custom` follows the user's focus questions without deleting the core questions.

Profile insights belong in `profile_analysis`; do not hardcode them into the
paper identity or generic evidence model.
