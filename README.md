# Paper Deep Analysis Skill

An evidence-grounded Agent Skill that turns a local paper PDF, a public PDF URL,
or an arXiv identifier into two complementary artifacts:

- a self-contained HTML report designed for human reading; and
- a schema-validated JSONL dataset designed for downstream Agent retrieval,
  reflection, comparison, and continual-learning experiments.

The host Agent performs the semantic reading. Deterministic Python tools handle
source acquisition, PDF extraction, schema checks, HTML escaping/rendering,
dataset export, and provenance. No external model API is required.

## Status

This repository contains the public `0.1.0` release of the Skill. No
reliability, scientific-analysis accuracy, or benchmark claim is made.

## Skill compatibility

The canonical Skill lives at
`.agents/skills/paper-deep-analysis/` and follows the open
[Agent Skills specification](https://agentskills.io/specification). Its
`SKILL.md`, `scripts/`, `references/`, and `assets/` are shared by both hosts.

- **OpenAI Codex:** discovers the canonical project Skill under
  `.agents/skills/` and can use `agents/openai.yaml` for Codex UI metadata.
- **Claude Code:** discovers the project entry under
  `.claude/skills/paper-deep-analysis/`. That entry is a repository-local
  symlink to the canonical Skill, a layout supported by
  [Claude Code skills](https://code.claude.com/docs/en/skills).

There is one implementation, not two copied trees. This avoids host-specific
versions drifting apart. If a filesystem cannot preserve symlinks, copy the
canonical `paper-deep-analysis` directory into `.claude/skills/` instead.

## Supported inputs

| Input | v0.1 behavior |
|---|---|
| Local PDF path | Supported; the absolute path is not copied into public artifacts |
| arXiv ID or arXiv URL | Supported; metadata and PDF are retrieved from public arXiv endpoints |
| Direct public PDF URL | Supported over HTTPS |
| Paper landing page | Best effort only when a public PDF link is explicitly discoverable |
| Login/paywalled/private-network source | Refused; provide an authorized local PDF instead |
| Scanned/image-only PDF | Detected and reported; OCR is intentionally out of scope in v0.1 |

## Repository quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'

python .agents/skills/paper-deep-analysis/scripts/prepare_source.py \
  "2607.28033" --output-dir .work/data-claw
```

Then ask the Agent to use `paper-deep-analysis` on the input. The Skill guides
the Agent through source preparation, evidence-grounded analysis, deterministic
rendering, dataset export, and validation.

Expected public-safe artifacts:

```text
analysis.json
report.html
agent-learning.jsonl
source-manifest.json
run.json
validation.json
```

The downloaded PDF and page-level extracted text stay under `.work/` and are
ignored by Git by default.

## Build the standalone Skill package

Create a deterministic runtime-only directory and ZIP. The package excludes
tests, repository documentation, examples, caches, local PDFs, extracted text,
and evaluation workspaces.

```bash
python scripts/build_release.py
```

Outputs under ignored `dist/`:

```text
dist/
├── paper-deep-analysis/          # installable Skill directory
├── paper-deep-analysis-v0.1.0.zip
├── release-manifest.json         # per-file hashes and compatibility metadata
└── SHA256SUMS
```

Install the generated directory at one of these locations:

```text
# Codex, per project
<project>/.agents/skills/paper-deep-analysis/

# Claude Code, per project
<project>/.claude/skills/paper-deep-analysis/

# Claude Code, personal
~/.claude/skills/paper-deep-analysis/
```

The ZIP intentionally does not vendor Python packages. Install its runtime
dependencies in the host environment before use:

```bash
python -m pip install 'jsonschema>=4.21,<5' 'pypdf>=5,<7' 'requests>=2.31,<3'
```

For a cloned copy of this repository, the two project entries are already
wired to the same canonical Skill.

## Non-goals

- bypassing paywalls, authentication, robots controls, or publisher access rules;
- silently running OCR or trusting extraction from image-only PDFs;
- claiming peer-review status, correctness, reproducibility, or model accuracy;
- publishing paper full text as an “Agent dataset”;
- replacing domain-expert review for high-stakes scientific decisions.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Quality and validation](docs/QUALITY.md)
- [Evaluation results and honest limits](docs/EVAL_RESULTS.md)
- [Report design-density review](docs/DESIGN_DENSITY_REVIEW.md)
- [Security and copyright](docs/SECURITY_AND_COPYRIGHT.md)
- [Publication checklist](docs/PUBLICATION_CHECKLIST.md)

The [DataClawEval example](examples/data-claw/report.html) demonstrates the
`data-agent` profile. Its source was resolved from an arXiv ID; the paper PDF
and extracted full text are not included. The example validates the artifact
pipeline, not the paper's benchmark results or scientific correctness.

The report renderer follows a dense editorial reading model: scroll progress,
CSS current-section navigation, a paper-centered core conclusion separated from
the analyst verdict, anchored key metrics, Introduction narrative, method flow,
experiment evidence, multi-dimensional criticism, a paper-specific directed
perspective, concepts, and no external runtime dependency. It does not turn
qualitative evidence status into a visual score.

## Attribution and disclosure

This project was developed with AI-assisted analysis and code generation under
human direction and review. Generated reports must record the model/product used
and distinguish paper claims from analyst inference.

For arXiv-powered inputs: Thank you to arXiv for use of its open access
interoperability. This project is independent and is not endorsed by arXiv.

## Local release gate

Before creating a GitHub release, run:

```bash
pytest --cov --cov-report=term
skills-ref validate .agents/skills/paper-deep-analysis
skills-ref validate .claude/skills/paper-deep-analysis
python scripts/release_audit.py
python scripts/build_release.py --force
```

Inspect the example report and `dist/SHA256SUMS`, then obtain owner confirmation
before committing, pushing, tagging, or publishing a release.

## License

Code and original templates are MIT licensed. Papers, metadata, and source
materials retain their original rights and licenses; this repository's license
does not relicense them.
