# Shared static demo shell (`shell/`)

Templates and assets for **RAG Document QA** landing pages. **Do not edit generated folders by hand** — change `shell/` and re-run Node.

**Profiles:** Sidebar identity comes from **`shell/profiles/<name>.json`**. The build writes that object to **`profile.json`** in the output folder.

## Render

From the **repository root**:

**Recruiter** (`shell/body/rag.html`) → `layout-shell/`:

```bash
node shell/render-shell.mjs --project shell/projects/rag.json --body shell/body/rag.html --out layout-shell --profile recruiter --demo-body shell/body/interactive-demo.html
```

**Commercial** (`shell/body/rag-commercial.html`) → `layout-shell-commercial/`:

```bash
node shell/render-shell.mjs --project shell/projects/rag.json --body shell/body/rag-commercial.html --out layout-shell-commercial --profile commercial --demo-body shell/body/interactive-demo.html
```

Outputs include `index.html`, **`portfolio-demo.html`**, `shell.css`, `demo-content.css`, `rag-portfolio-demo.css`, `shell.js`, `favicon.svg`, and `profile.json`.

## Deploy

| Build | Host |
|--------|------|
| `layout-shell/` | **rag.vahdetkaratas.com** |
| `layout-shell-commercial/` | **rag.vahdetlabs.com** |
| API (same backend) | **rag-qa.vahdetkaratas.com** / **rag-qa.vahdetlabs.com** |

**Brand separation:** the **commercial** render uses **VahdetLabs** links only in sidebar CTAs and related lists — no `vahdetkaratas.com` navigation in that build.

**CORS:** add static origins to `CORS_ORIGINS` on the API (e.g. `https://rag.vahdetkaratas.com`, `https://rag.vahdetlabs.com`).

## Commit policy

`layout-shell/` and `layout-shell-commercial/` are tracked. Re-render and commit after any change under `shell/`.
