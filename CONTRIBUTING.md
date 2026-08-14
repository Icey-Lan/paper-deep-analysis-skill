# Contributing

Contributions are welcome after the initial public release.

1. Do not commit papers, extracted full text, private URLs, credentials, or
   customer data. Use synthetic fixtures.
2. Keep semantic model output in `analysis.json`; generated HTML and JSONL must
   remain deterministic views.
3. Add a regression test for behavior changes and a trigger/failure eval when
   Skill routing changes.
4. Run `pytest`, `scripts/release_audit.py`, and `skills-ref validate`.
5. Describe AI assistance honestly in the pull request when it materially
   contributed to code or analysis.

Changes to safety limits, URL policy, evidence requirements, output schemas, or
copyright handling need explicit rationale and migration notes.
