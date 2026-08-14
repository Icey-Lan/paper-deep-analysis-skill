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

This repository is a local pre-release (`0.1.0`). The implementation and tests
are being completed and audited before any GitHub publication. No reliability,
accuracy, or benchmark claim is made.

## Supported inputs

| Input | v0.1 behavior |
|---|---|
| Local PDF path | Supported; the absolute path is not copied into public artifacts |
| arXiv ID or arXiv URL | Supported; metadata and PDF are retrieved from public arXiv endpoints |
| Direct public PDF URL | Supported over HTTPS |
| Paper landing page | Best effort only when a public PDF link is explicitly discoverable |
| Login/paywalled/private-network source | Refused; provide an authorized local PDF instead |
| Scanned/image-only PDF | Detected and reported; OCR is intentionally out of scope in v0.1 |

## Quick start

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
- [Security and copyright](docs/SECURITY_AND_COPYRIGHT.md)
- [Publication checklist](docs/PUBLICATION_CHECKLIST.md)

The [DataClawEval example](examples/data-claw/report.html) demonstrates the
`data-agent` profile. Its source was resolved from an arXiv ID; the paper PDF
and extracted full text are not included. The example validates the artifact
pipeline, not the paper's benchmark results or scientific correctness.

## Attribution and disclosure

This project was developed with AI-assisted analysis and code generation under
human direction and review. Generated reports must record the model/product used
and distinguish paper claims from analyst inference.

For arXiv-powered inputs: Thank you to arXiv for use of its open access
interoperability. This project is independent and is not endorsed by arXiv.

## License

Code and original templates are MIT licensed. Papers, metadata, and source
materials retain their original rights and licenses; this repository's license
does not relicense them.
