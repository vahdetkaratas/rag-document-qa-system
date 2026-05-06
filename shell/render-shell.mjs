import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.dirname(fileURLToPath(import.meta.url));
const DEFAULT_PROFILE = "recruiter";

function usage() {
  console.error(
    "Usage: node shell/render-shell.mjs --project <project.json> --body <body.html> --out <output-dir> [--profile <profile-name>]"
  );
  process.exit(1);
}

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i += 1) {
    const key = argv[i];
    const value = argv[i + 1];
    if (!key.startsWith("--") || !value) usage();
    args[key.slice(2)] = value;
    i += 1;
  }
  return args;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function listItems(items) {
  return items.map((item) => `<li>${escapeHtml(item)}</li>`).join("\n");
}

function linkItems(items) {
  return items
    .map(
      (item) =>
        `<li><a href="${escapeHtml(item.href)}"${item.external ? ' target="_blank" rel="noopener noreferrer"' : ""}>${escapeHtml(item.label)}</a></li>`
    )
    .join("\n");
}

function socialItems(items) {
  return items
    .map(
      (item) =>
        `<a href="${escapeHtml(item.href)}" target="_blank" rel="noopener noreferrer" aria-label="${escapeHtml(item.label)}"><i class="${escapeHtml(item.iconClass)}" aria-hidden="true"></i></a>`
    )
    .join("\n");
}

function tagItems(items) {
  return items.map((item) => `<li>${escapeHtml(item)}</li>`).join("\n");
}

function buttonItems(items) {
  return items
    .map((item, index) => {
      const klass =
        index === 0
          ? "shell-link-button shell-link-button--primary"
          : "shell-link-button";
      return `<a class="${klass}" href="${escapeHtml(item.href)}"${item.external ? ' target="_blank" rel="noopener noreferrer"' : ""}>${escapeHtml(item.label)}</a>`;
    })
    .join("\n");
}

function mergeProject(baseProject, profileName) {
  const variant = baseProject.profiles?.[profileName] || {};
  return {
    ...baseProject,
    ...variant,
  };
}

async function readJson(filePath) {
  return JSON.parse(await fs.readFile(filePath, "utf8"));
}

async function readProfile(profileName) {
  const profilePath = path.join(ROOT, "profiles", `${profileName}.json`);
  try {
    return await readJson(profilePath);
  } catch (error) {
    if (profileName !== DEFAULT_PROFILE) {
      throw new Error(
        `Profile '${profileName}' was not found at ${profilePath}.`
      );
    }

    return readJson(path.join(ROOT, "profile.json"));
  }
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const projectPath = args.project ? path.resolve(args.project) : null;
  const bodyPath = args.body ? path.resolve(args.body) : null;
  const outDir = args.out ? path.resolve(args.out) : null;
  const profileName = args.profile || DEFAULT_PROFILE;

  if (!projectPath || !bodyPath || !outDir) usage();

  const profile = await readProfile(profileName);
  const projectBase = await readJson(projectPath);
  const project = mergeProject(projectBase, profileName);
  const template = await fs.readFile(path.join(ROOT, "index.html"), "utf8");
  const bodyHtml = await fs.readFile(bodyPath, "utf8");

  const rendered = template
    .replaceAll(
      "{{PAGE_TITLE}}",
      escapeHtml(project.pageTitle || `${project.title} - ${profile.name}`)
    )
    .replaceAll(
      "{{META_DESCRIPTION}}",
      escapeHtml(project.metaDescription || project.summary)
    )
    .replaceAll("{{PORTFOLIO_URL}}", escapeHtml(profile.portfolioUrl))
    .replaceAll("{{AVATAR_URL}}", escapeHtml(profile.avatarUrl))
    .replaceAll("{{PROFILE_NAME}}", escapeHtml(profile.name))
    .replaceAll("{{PROFILE_IDENTITY}}", escapeHtml(profile.identity))
    .replaceAll("{{PROFILE_LOCATION}}", escapeHtml(profile.location))
    .replaceAll(
      "{{TECHNICAL_FOCUS_ITEMS}}",
      listItems(profile.technicalFocus || [])
    )
    .replaceAll(
      "{{REVIEW_SECTION_TITLE}}",
      escapeHtml(profile.reviewSectionTitle || "Review this artifact")
    )
    .replaceAll(
      "{{RELATED_SECTION_TITLE}}",
      escapeHtml(profile.relatedSectionTitle || "Related systems")
    )
    .replaceAll(
      "{{REVIEW_LINK_ITEMS}}",
      linkItems(project.reviewLinks || [])
    )
    .replaceAll(
      "{{RELATED_SYSTEM_ITEMS}}",
      linkItems(project.relatedSystems || [])
    )
    .replaceAll(
      "{{SOCIAL_LINK_ITEMS}}",
      socialItems(profile.socialLinks || [])
    )
    .replaceAll(
      "{{PROJECT_EYEBROW}}",
      escapeHtml(project.eyebrow || "Portfolio artifact")
    )
    .replaceAll("{{PROJECT_TITLE}}", escapeHtml(project.title))
    .replaceAll("{{PROJECT_SUMMARY}}", escapeHtml(project.summary))
    .replaceAll("{{STACK_TAG_ITEMS}}", tagItems(project.stack || []))
    .replaceAll(
      "{{PROJECT_LINK_BUTTONS}}",
      buttonItems(project.projectLinks || [])
    )
    .replaceAll("{{LIMITATION_ITEMS}}", listItems(project.limitations || []))
    .replaceAll(
      "{{FOOTER_LABEL}}",
      escapeHtml(
        profile.footerLabel || "Applied ML / Data Systems portfolio artifact"
      )
    )
    .replaceAll("{{CONTENT_HTML}}", bodyHtml);

  await fs.rm(outDir, { recursive: true, force: true });
  await fs.mkdir(outDir, { recursive: true });
  await fs.writeFile(path.join(outDir, "index.html"), rendered, "utf8");

  for (const file of ["shell.css", "demo-content.css", "shell.js"]) {
    await fs.copyFile(path.join(ROOT, file), path.join(outDir, file));
  }

  await fs.writeFile(
    path.join(outDir, "profile.json"),
    `${JSON.stringify(profile, null, 2)}\n`,
    "utf8"
  );

  console.log(`Rendered shell to ${outDir} using profile '${profileName}'`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
