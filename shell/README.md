# Multi-profile shell (source)

Templates and assets for **RAG Document QA** landing pages. **Do not edit generated folders by hand** — change `shell/` and re-run Node.

**One technical project, two presentations:**

| Profile | Output folder | Static host | API host |
|---------|---------------|-------------|----------|
| `recruiter` | `layout-shell/` | **rag.vahdetkaratas.com** | **rag-qa.vahdetkaratas.com** |
| `commercial` | `layout-shell-commercial/` | **rag.vahdetlabs.com** | **rag-qa.vahdetlabs.com** |

Sidebar identity comes from **`shell/profiles/<name>.json`**. Project copy and links come from **`shell/projects/rag.json`** (`profiles.recruiter` / `profiles.commercial` overrides).

## Render

From the **repository root**:

```bash
node shell/render-shell.mjs --project shell/projects/rag.json --body shell/body/rag.html --out layout-shell --profile recruiter --demo-body shell/body/interactive-demo.html

node shell/render-shell.mjs --project shell/projects/rag.json --body shell/body/rag-commercial.html --out layout-shell-commercial --profile commercial --demo-body shell/body/interactive-demo.html
```

Outputs: `index.html`, **`portfolio-demo.html`**, `shell.css`, `demo-content.css`, `rag-portfolio-demo.css`, `shell.js`, `favicon.svg`, `profile.json`.

## Deploy

- **Static pages** — deploy `layout-shell/` or `layout-shell-commercial/` to the matching `rag.*` hostname (Caddy/Nginx web root). **Not** the Docker API container alone.
- **API** — `docker compose` / VPS runs FastAPI on `rag-qa.*`. Same backend; only the static shell framing differs.
- **CORS** — on the API, set `CORS_ORIGINS` to include `https://rag.vahdetkaratas.com` and/or `https://rag.vahdetlabs.com`.

**Brand separation:** the **commercial** build uses VahdetLabs links only in navigation (no `vahdetkaratas.com` in sidebar CTAs or related lists).

**Commit policy:** `layout-shell/` and `layout-shell-commercial/` are **committed** (see repo `.gitignore` note). Re-render and commit after any change under `shell/`.
