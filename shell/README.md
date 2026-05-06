# Shared Flagship Demo Shell

This folder is the tracked source for the recruiter-safe shell used by flagship demo projects.

## Purpose

The shell owns shared identity and review flow:

- applied ML / data systems positioning
- project hero frame
- technical focus sidebar
- review links
- related systems links
- footer and minimal interaction behavior

Project-specific repositories keep ownership of:

- the project body content
- API routes and app behavior
- repo-specific architecture notes
- demo-specific limitations and links

## Files

- `index.html`: HTML template with placeholders
- `shell.css`: shared shell layout and identity styling
- `demo-content.css`: shared body-content defaults
- `shell.js`: sidebar toggle and small shell behavior
- `profile.json`: recruiter-default compatibility profile
- `profiles/*.json`: named shell profiles such as recruiter and commercial
- `projects/*.json`: per-project config examples
- `render-shell.mjs`: renders one project shell to a target directory

## Recommended consumption model

Use a copy-and-render strategy.

Why this is the safest option:

- current demo repos already deploy local static shell folders
- no repo currently exposes a stable shared package/build system
- submodules add maintenance overhead for small independent repos
- a tracked source + render script keeps the shell centralized without forcing a monorepo

## Render flow

1. Keep this folder tracked in one source repo.
2. Copy `shell/` into a flagship demo repo.
3. Add a repo-specific body HTML partial.
4. Run:

Recruiter render:

```bash
node shell/render-shell.mjs \
  --project shell/projects/rag.json \
  --body shell/body/rag.html \
  --out layout-shell \
  --profile recruiter
```

Commercial render:

```bash
node shell/render-shell.mjs \
  --project shell/projects/rag.json \
  --body shell/body/rag.html \
  --out layout-shell-commercial \
  --profile commercial
```

The command writes:

- `layout-shell/index.html`
- `layout-shell/shell.css`
- `layout-shell/demo-content.css`
- `layout-shell/shell.js`
- `layout-shell/profile.json`

The selected profile controls:

- identity line
- home/portfolio URL
- technical-focus sidebar
- review section title
- footer identity

The selected project config can also carry profile-specific overrides under `profiles.<name>` for:

- page title
- eyebrow
- summary
- project CTA links
- sidebar links: `relatedMlSystems` and `relatedDataTools` (rendered under headings **ML systems** and **Data tools**), or legacy `relatedSystems` as a single **Related** list

For other projects, the same rendered output can be copied to any static web root (VPS, object storage, etc.).

## Pilot approach

RAG is the first multi-profile pilot because it has the clearest frontend/backend separation and the highest need for recruiter/commercial shell divergence.

Once the RAG pilot is stable, the same profile flow can be applied to:

1. Batch Scoring
2. Feature Store
3. Monitoring later

## Notes

- The template intentionally has no consulting, services, KPI, spreadsheet, or client-work language.
- Facebook / Vakasoft links are excluded from the shared identity layer.
- Project body content is intentionally left repo-specific so each artifact can keep its own technical narrative.
- README files in the project repos should stay technically neutral; domain-specific positioning belongs in the shell layer, not in the repo README.
