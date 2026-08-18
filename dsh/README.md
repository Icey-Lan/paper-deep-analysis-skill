# dsh-plugin-paper-deep-analysis

A [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness) (dsh)
plugin bundle that packages the **`paper-deep-analysis`** skill. The skill turns
a local paper PDF, a public PDF URL, or an arXiv identifier into:

- a self-contained, evidence-grounded HTML report for human reading; and
- a schema-validated JSONL dataset for downstream Agent retrieval, reflection,
  comparison, and continual-learning experiments.

The host Agent performs the semantic reading. Deterministic Python tools handle
source acquisition, PDF extraction, schema checks, HTML rendering, dataset
export, and provenance. No external model API is required.

## Install

From this repository (local / private use):

```sh
dsh plugin --profile web add <path-to-this-repo>/dsh
```

The package declares `dsh.bundle.patch`, so `dsh plugin` adds it to the
profile's bundle stack automatically. When published, install by name instead:

```sh
dsh plugin --profile web add dsh-plugin-paper-deep-analysis
```

## Python runtime

The skill's deterministic tooling is Python and requires Python 3.10+ plus
`pypdf`, `requests`, and `jsonschema`. Rather than touching the host's Python
environment (which on modern distros refuses bare `pip install` under PEP 668),
the skill bootstraps a self-contained virtualenv on first use:

```sh
python3 dsh/assets/bootstrap.py --dir .work/venv
```

The script is idempotent and prints the virtualenv's Python binary; the skill's
instructions use it for every command. Manually installing the same
dependencies is also fine (`python -m pip install -r requirements.txt`).
`preflight` still detects a missing dependency and fails with a `runtime.*`
code, and the instructions tell the agent to re-run the bootstrap step.

## Release gate

Before publishing the plugin package, run:

```sh
python dsh/sync-assets.py --check   # dsh/assets must match canonical byte-for-byte
python dsh/sync-assets.py           # re-sync if it reports drift
python dsh/assets/bootstrap.py --dir .work/venv
.work/venv/bin/python dsh/assets/scripts/preflight.py "2607.26637" --output-dir .work/gate
cd dsh && npm pack --dry-run         # inspect publish contents
```

The repository CI runs the sync check, the bootstrap, and a preflight smoke
automatically. The one check CI cannot run (the npm `@deepseek-ai/dsh-skill`
published version is stale) is the plugin registration smoke — run it locally
with a dsh runtime present. The end-user check is simplest: install the plugin
into a profile, restart dsh, and confirm `paper-deep-analysis` appears in
`<available_skills>` and a `skill paper-deep-analysis` call returns the body.
For a scripted check, load the plugin with the dsh runtime's `node_modules` on
the resolution path (e.g. from the npx dsh checkout, as in the repo's
verification notes) and assert the provider registers and serves content:

```sh
node --input-type=module -e '
import { apply, inject, name } from "<plugin>/lib/index.js";
const registered = [];
const ctx = { skills: { registerProvider: (create) => { registered.push(create({ signal: new AbortController().signal, invalidate() {} })); return () => {}; } } };
apply(ctx);
const p = registered[0];
const c = (await p.list())[0];
const d = await p.get(c);
console.log("plugin:", name, "| provider:", p.name, "| content bytes:", d.content.length);
if (!d.content.includes("Paper deep analysis")) process.exit(1);
'
```

## Inputs and deliverables

Supported inputs: local PDF, public HTTPS PDF URL, arXiv ID/URL, or a paper
landing page that exposes a public PDF link. Login/paywalled/private-network
sources are refused; scanned/image-only PDFs are detected and reported.

Expected public-safe artifacts:

```text
analysis.json
report.html
agent-learning.jsonl
source-manifest.json
run.json
validation.json
```

## Layout and single source of truth

The canonical skill lives at
`.agents/skills/paper-deep-analysis/`. `dsh/assets/` ships `references/`,
`scripts/`, and `assets/` as deterministic copies; regenerate them after a
canonical change with:

```sh
python dsh/sync-assets.py
```

`dsh/assets/SKILL.md` is the DSH-adapted entry point (resource-base relative
paths instead of the canonical `$PAPER_SKILL_DIR` convention). Two DSH-only
helpers sit beside it and are never overwritten by the sync:

- `bootstrap.py` — creates the self-contained runtime virtualenv (see above);
- `render_page.py` — renders source-PDF pages to PNG so an image-capable host
  model can inspect figures with `read_image` (optional `pymupdf` dependency,
  installed on first use).

## License

MIT. Papers, metadata, and source materials retain their original rights.
