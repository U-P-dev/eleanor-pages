# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Eleanor (エレノア) is a static corporate website for a sole proprietorship (個人事業主) run by Yusuke Toyoshima. The site promotes the business and its flagship app, SONO-HINO (Flutter task management app).

- **Live site**: https://eleanor-dev.com/
- **Repo**: `U-P-dev/eleanor-pages` on GitHub
- **Hosting**: GitHub Pages with custom domain via Cloudflare DNS

## Deployment

No build step — this is pure static HTML/CSS/JS.

```bash
# Deploy
git add <files>
git commit -m "feat|fix|chore: description"
git push origin main

# Verify deployment (SHA should match latest commit)
gh api repos/U-P-dev/eleanor-pages/deployments --jq '.[0] | {sha, created_at}'
```

## Pages

| File | URL | Purpose |
|------|-----|---------|
| `index.html` | `/` | Homepage (main showcase) |
| `company.html` | `/company.html` | Company information |
| `privacy.html` | `/privacy.html` | Privacy policy |
| `support.html` | `/support.html` | Support |
| `account-deletion.html` | `/account-deletion.html` | GDPR account deletion |

## Architecture

**No frameworks, no build tools.** Each HTML file is self-contained with inline `<style>` and `<script>` tags. All CSS uses custom properties defined in `:root`.

Shared structure across all pages:
1. Fixed 3px gradient accent bar (`.top-bar`)
2. Fixed nav (60px, `top: 3px`) with frosted glass effect
3. Hamburger menu for mobile (toggles `.open` class via `document.getElementById('m')`)
4. Page content sections
5. Footer

Scroll animations work via Intersection Observer: add `data-a` to any element to make it fade-in on scroll. Use `data-d="N"` (number) for stagger delay (N × 0.1s).

## Design System

All design decisions are documented in `DESIGN.md`. Key points:

**Color variables** (always use these, never hardcode hex values):
```css
--blue: #2563EB    /* primary actions */
--purple: #7C3AED  /* brand core */
--red: #E11D48     /* accent, CTA */
--bg: #04040E      /* page background */
--bg2: #07071A     /* section background */
--bg3: #0A0A22     /* card background */
--text: #FFFFFF
--body: rgba(255,255,255,0.84)
--muted: rgba(255,255,255,0.60)
--grad: linear-gradient(135deg, #2563EB 0%, #7C3AED 50%, #E11D48 100%)
--grad-text: linear-gradient(125deg, #93C5FD 0%, #C4B5FD 48%, #FDA4AF 100%)
```

**Responsive breakpoints**: 960px (nav collapse), 768px (grid), 480px (font sizes)

**Text contrast**: Never use `rgba(255,255,255,0.42)` or lower for body text (WCAG AA minimum).

## Coding Rules

1. Use CSS custom properties — never hardcode color hex values
2. Keep JS minimal; only Intersection Observer animations and mobile menu toggle are acceptable
3. No external dependencies beyond Google Fonts CDN
4. Maintain WCAG AA contrast (4.5:1+) for all body text

## Infrastructure Notes

- **Cloudflare Proxy must be OFF** (DNS only mode) — enabling it causes HTTPS certificate conflicts with GitHub Pages
- **Do not delete `CNAME`** — it's required for the custom domain to work
- `PROGRESS.md` tracks business progress (D-U-N-S, app store registration, etc.) — commit it but it's not a public page
- **全プロジェクトのインフラ情報**: `docs/infra/` に集約（`docs/infra/README.md` がインデックス）
- **リモート開発環境**: [docs/infra/local-dev.md](./docs/infra/local-dev.md) 参照
