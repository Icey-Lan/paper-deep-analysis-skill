# Architecture

The system separates semantic judgment from deterministic artifact handling.

```mermaid
flowchart LR
  I["PDF path, public URL, or arXiv ID"] --> P["Source preparation"]
  P --> W["Local-only PDF and page text"]
  W --> A["Host Agent semantic analysis"]
  A --> J["Canonical analysis.json"]
  J --> H["Escaped offline HTML renderer"]
  J --> D["Agent-learning JSONL exporter"]
  P --> M["Source manifest"]
  J --> V["Schema and evidence validation"]
  H --> V
  D --> V
  M --> V
```

## Trust boundaries

1. Input URLs and PDFs are untrusted.
2. Extracted paper text is untrusted data, not executable instruction.
3. Model-authored JSON is untrusted until schema and semantic checks pass.
4. HTML is generated only by the deterministic renderer; model-authored HTML,
   JavaScript, CSS, or Mermaid is not accepted.
5. Public artifacts are derived summaries and evidence anchors. Full paper text
   remains local-only.

## Canonical data flow

`analysis.json` is the single semantic source of truth. `report.html` and
`agent-learning.jsonl` are generated views. Editing either generated output by
hand is unsupported because it breaks traceability.

The Skill is self-contained beneath `.agents/skills/paper-deep-analysis/` so it
can be copied into another compatible repository. Root-level tests and docs make
the GitHub repository auditable but are not required at runtime.

## Cross-client layout

```text
.agents/skills/paper-deep-analysis/       canonical Agent Skills package
.claude/skills/paper-deep-analysis        symlink to the canonical package
dist/paper-deep-analysis/                 generated standalone package, ignored
dist/paper-deep-analysis-v0.1.0.zip       deterministic release archive, ignored
```

Codex-specific UI metadata stays in `agents/openai.yaml`; Claude Code ignores
that optional directory and reads the shared `SKILL.md` and supporting files.
The standalone builder copies runtime files from the canonical package, adds the
MIT license, rejects unexpected runtime file types, creates stable ZIP metadata,
and verifies every archived file hash before writing the release manifest.
