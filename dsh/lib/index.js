import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { BUNDLED_SKILL_RANK } from "@deepseek-ai/dsh-skill";

/**
 * Bundled `paper-deep-analysis` skill provider.
 *
 * Ships the SKILL.md body plus its references/, scripts/, and assets/
 * directories as the skill's resource base, so the deterministic Python
 * tooling (preflight, source preparation, validation, rendering, dataset
 * export) resolves relative to the packaged assets directory.
 *
 * @module dsh-plugin-paper-deep-analysis
 */
const PROVIDER_NAME = "paper-deep-analysis";
const DESCRIPTION =
  "Deeply analyzes a research paper from a local PDF, public PDF URL, paper link, arXiv URL, or arXiv ID. Use when the user asks to read, critique, explain, or learn from one paper and wants an evidence-grounded human-readable HTML report plus structured Agent-learning JSONL. Selects a paper-specific research perspective such as Agent evaluation, Harness, Memory, continual learning, or Data Agent. Refuses paywall bypass, private-network fetching, and unsupported image-only PDFs.";
const SKILL_BODY_URL = new URL("../assets/SKILL.md", import.meta.url);
const RESOURCE_BASE = {
  kind: "directory",
  path: fileURLToPath(new URL("../assets/", import.meta.url))
};

const CANDIDATE = {
  name: "paper-deep-analysis",
  description: DESCRIPTION,
  invocation: {
    modelInvocable: true,
    userInvocable: true
  },
  provider: PROVIDER_NAME,
  source: "dsh-plugin",
  resourceBase: RESOURCE_BASE,
  rank: BUNDLED_SKILL_RANK,
  locator: SKILL_BODY_URL
};

const provider = {
  name: PROVIDER_NAME,
  list: () => Promise.resolve([CANDIDATE]),
  async get(_candidate) {
    return {
      name: CANDIDATE.name,
      description: CANDIDATE.description,
      invocation: CANDIDATE.invocation,
      provider: CANDIDATE.provider,
      source: CANDIDATE.source,
      resourceBase: RESOURCE_BASE,
      content: await readFile(SKILL_BODY_URL, "utf8")
    };
  }
};

/** Cordis plugin name. */
const name = "paper-deep-analysis";
/** Service required by the bundled provider. */
const inject = ["skills"];
/** Register the bundled `paper-deep-analysis` provider on `ctx.skills`. */
function apply(ctx) {
  ctx.skills.registerProvider(() => provider);
}

export { apply, inject, name };
