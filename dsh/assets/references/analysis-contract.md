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

Use a narrower profile when it creates a clearer report:

- `agent-evaluation`: task validity, graders, contamination, variance, cost,
  human baselines, and failure attribution;
- `harness`: runtime, tools, permissions, state, recovery, observability, and
  model–Harness interaction;
- `memory`: memory formation, retrieval, update, forgetting, temporal validity,
  and long-horizon evaluation;
- `continual-learning`: feedback loops, skill or policy updates, regression,
  catastrophic forgetting, and reward hacking;
- `multi-agent`: role design, coordination, communication cost, conflict, and
  credit assignment;
- `tool-use`: tool selection, interfaces, execution feedback, error recovery,
  and cost;
- `reasoning-planning`: decomposition, search, verification, replanning, and
  long-horizon reliability;
- `embodied-agent`: perception–action loops, simulation-to-real transfer,
  safety, and physical evaluation.

`data-agent` examines data discovery, semantic layers, SQL/code generation,
pipeline orchestration, data quality, lineage, metadata, governance, human
review, benchmark realism, and operational integration with data engineering.

`custom` follows the user's focus questions without deleting the core questions.

Profile insights belong in `profile_analysis`; do not hardcode them into the
paper identity or generic evidence model.

## Reader-facing narrative

The executive summary has three distinct jobs that must not collapse into one:

1. `core_conclusion` reconstructs the paper itself for a curious reader who may
   lack specialist background: problem or gap, named approach or study object,
   and strongest supported result. It is descriptive synthesis and a reading
   hook, not a review verdict. For Chinese, use two short sentences, normally
   90-160 characters and never more than 220. Exclude formulas, complexity
   notation, LaTeX, unexplained abbreviations, and nonessential setup details.
2. `why_it_matters` explains why the result deserves the target reader's time.
3. `analyst_verdict` evaluates transfer value and limitations. `evidence_summary`
   states what the inspected evidence does and does not support.

For a benchmark or systems paper, the core conclusion should normally identify
the evaluated task/system, the evaluation design, and the discriminating result
rather than merely saying a benchmark was introduced. For a method paper,
identify the prior gap, the mechanism, and the strongest comparison or finding.
For a survey or position paper, replace experimental language with its organizing
framework and central argument. Never begin the core conclusion with a generic
quality judgment such as "this paper is valuable but limited."

Keep scientific precision by preserving the scope of the supported finding, not
by copying the paper's densest notation. Put exact equations, model sizes,
benchmark lists, ablation details, and caveats in Method, Evidence, key metrics,
or the analyst verdict where readers can interpret them with context.

Before listing contributions, reconstruct the paper's argument in the order a
good Introduction establishes it: research context, prior-work gap, why the gap
matters, proposed solution, and main findings. This narrative should let a
technical reader understand the paper before encountering the report's critique.

For evidence, prefer concrete experiment descriptions and a prose synthesis to
qualitative score graphics. For criticism, explain the reasoning in complete
paragraphs or ordered points and place grouped source locations after that unit
of thought.
