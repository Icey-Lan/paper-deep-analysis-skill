# Contributing

Contributions are welcome after the initial public release.

1. Do not commit papers, extracted full text, private URLs, credentials, or
   customer data. Use synthetic fixtures.
2. Keep semantic model output in `analysis.json`; generated HTML and JSONL must
   remain deterministic views.
3. Add a regression test for behavior changes and a trigger/failure eval when
   Skill routing changes.
4. Run `pytest`, `scripts/release_audit.py`, `scripts/build_release.py`, and
   `skills-ref validate` against both project Skill entries.
5. Describe AI assistance honestly in the pull request when it materially
   contributed to code or analysis.

Changes to safety limits, URL policy, evidence requirements, output schemas, or
copyright handling need explicit rationale and migration notes.

Edit only `.agents/skills/paper-deep-analysis/`. The Claude Code project entry
is a symlink to that canonical directory; do not create a second maintained copy.
