# RAG Multi-Profile Shell Pilot

This document is the handoff for the next execution phase in the flagship demo ecosystem.

It exists for one reason: the shared shell is now multi-profile in the `vkcom` source repo, but the real RAG repository and its public deployment still need to be updated separately.

## Why this exists

The main site repositioning is already in place on `vahdetkaratas.com`.

The remaining ecosystem problem is external demo consistency:

- the RAG system is a separate repository
- its live frontend shell still reflects the old consultant-era wrapper unless production is switched
- the same technical project may need two different public contexts:
  - recruiter-facing on `vahdetkaratas.com` domains
  - commercial-facing on `vahdetlabs.com` domains

The chosen strategy is:

- keep one technical project and one backend truth
- keep README technically neutral
- vary only the outer shell by profile/domain

## Current source of truth

The shared shell source now lives in:

- `shell/index.html`
- `shell/shell.css`
- `shell/demo-content.css`
- `shell/shell.js`
- `shell/render-shell.mjs`
- `shell/profiles/recruiter.json`
- `shell/profiles/commercial.json`
- `shell/projects/rag.json`

These files are in the `vkcom` repo, not in the real RAG repo yet.

## What was already implemented

The shared shell now supports named profiles:

- `recruiter`
- `commercial`

The render command supports:

```bash
node shell/render-shell.mjs --project shell/projects/rag.json --body shell/body/rag.html --out <target-dir> --profile recruiter
node shell/render-shell.mjs --project shell/projects/rag.json --body shell/body/rag.html --out <target-dir> --profile commercial
```

The RAG project config now contains profile-specific overrides in:

- `shell/projects/rag.json`

Those overrides change only the outer framing:

- page title
- eyebrow
- summary
- project CTA links
- related links

The technical body remains shared.

## Pilot goal

Apply the multi-profile shell system to the real RAG repository without changing the core RAG backend or pipeline logic.

## Real work to do in the RAG repo

### 1. Inspect the real repo structure

Before making changes, verify:

- where the current shell lives
- whether `layout-shell/` is tracked or gitignored
- whether the live frontend is served from the repo or from a separate static deployment
- whether the frontend shell calls a separate API host
- whether CORS currently allows only the recruiter-facing domain

Key files to inspect first:

- `.gitignore`
- `README.md`
- `src/api/app.py`
- any existing `layout-shell/` or static frontend directory
- deployment config files

### 2. Add the tracked shell source

Copy the shared `shell/` folder from `vkcom` into the real RAG repo.

Minimum expected files:

- `shell/index.html`
- `shell/shell.css`
- `shell/demo-content.css`
- `shell/shell.js`
- `shell/render-shell.mjs`
- `shell/profile.json`
- `shell/profiles/recruiter.json`
- `shell/profiles/commercial.json`
- `shell/projects/rag.json`
- `shell/body/rag.html`
- `shell/README.md`

### 3. Decide output strategy

Preferred pilot strategy:

- `layout-shell/` = recruiter shell output
- `layout-shell-commercial/` = commercial shell output

This is preferred over runtime host switching because it is easier to test, easier to deploy, and less error-prone.

### 4. Render both outputs

Expected commands inside the real RAG repo:

```bash
node shell/render-shell.mjs --project shell/projects/rag.json --body shell/body/rag.html --out layout-shell --profile recruiter
node shell/render-shell.mjs --project shell/projects/rag.json --body shell/body/rag.html --out layout-shell-commercial --profile commercial
```

### 5. Keep asset path compatibility

Do not break the existing frontend contract.

If the current live RAG shell expects root-level asset paths such as:

- `styles.css`
- `demo-content.css`
- `shell.js`

then the generated output may need a post-render path adjustment or a small wrapper change.

This is a deployment compatibility task, not a product redesign task.

### 6. Check CORS/origin rules

If the backend currently allows only the recruiter-facing frontend origin, add the commercial frontend origin as needed.

Likely file:

- `src/api/app.py`

The backend should not be refactored beyond origin safety unless a real blocker is found.

## What should not change

Do not change these unless a real integration blocker forces it:

- retrieval logic
- chunking logic
- FAISS/indexing logic
- answer generation flow
- API contract
- notebooks
- evaluation code
- project README into recruiter/commercial marketing copy

The README should stay technically neutral.

## Validation checklist

### Recruiter shell

- identity is recruiter-safe
- no consultant wording
- links point to recruiter ecosystem where intended
- related systems point to `vahdetkaratas.com` ecosystem

### Commercial shell

- identity is commercial-capability oriented, not recruiter-oriented
- no recruiter-specific portfolio framing
- related systems point to `vahdetlabs.com` ecosystem

### Shared technical truth

- body content stays technically the same
- API docs still work
- backend endpoints still work
- no frontend/API origin break

## Production switch model

Preferred model:

- recruiter domain serves recruiter shell output
- commercial domain serves commercial shell output
- both use the same backend/API

Do not rely on implicit memory for this. The deployment mapping must be written down in the real RAG repo once confirmed.

## Open questions to answer in the real RAG repo

1. Is the public frontend shell actually deployed from the repo, or from a separate static host workflow?
2. Does the current deployment use `layout-shell/` directly?
3. Are asset paths root-relative or folder-relative in production?
4. Which commercial domain is the real target?
5. Does CORS already support multiple frontend origins?

## Fastest safe execution order

1. Open the real RAG repo
2. Inspect its live shell/deploy contract
3. Copy in the multi-profile `shell/` source
4. Render recruiter and commercial outputs
5. Adjust asset path compatibility if needed
6. Patch CORS only if required
7. Smoke-test locally
8. Deploy recruiter shell first
9. Deploy commercial shell second
10. Verify public HTML, not just repo state

## Thread restart instruction

If this work continues in a new thread, provide:

1. the real RAG repo path
2. this document path
3. the instruction: "continue RAG multi-profile shell pilot from this handoff"

That is enough to resume without re-deriving the strategy.
