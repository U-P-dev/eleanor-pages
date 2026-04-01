# Screencraft インフラ構成

> **概要**: 自然言語 AI による App Store / Google Play スクリーンショットデザイン作成 SaaS
> **リポジトリ**: `U-P-dev/screencraft`（pnpm モノレポ、コードは `screencraft/` 配下）
> **ステータス**: 開発中（本番環境デプロイ済み）
> **最終更新**: 2026-04-01

---

## 本番 URL

| サービス | URL |
|---------|-----|
| フロントエンド | https://screenshot-craft.app |
| フロントエンド (Cloudflare) | https://screencraft-web.pages.dev |
| API | https://api.screenshot-craft.app |
| API (Cloudflare) | https://screencraft-api.yusuke-p-development.workers.dev |

---

## アーキテクチャ概要

```
ユーザー
  ↓ HTTPS
Cloudflare Pages（Next.js 15 / apps/web）  ← GitHub 連携で自動デプロイ
  ↓ API リクエスト
Cloudflare Workers（Hono / apps/api）      ← wrangler deploy で手動デプロイ
  ├── Supabase（認証 + PostgreSQL）
  ├── Cloudflare R2（書き出し画像）
  ├── Anthropic Claude Haiku（AI 操作変換）
  ├── Stripe（課金）
  └── Resend（メール）
```

---

## ホスティング

### フロントエンド — Cloudflare Pages (screencraft-web)

| 項目 | 値 |
|---|---|
| プロジェクト名 | `screencraft-web` |
| フレームワーク | Next.js 15（App Router、Edge Runtime） |
| Production branch | `main` |
| デプロイ方式 | GitHub 連携（main push で自動デプロイ） |
| ビルドツール | `@cloudflare/next-on-pages`（`vercel build` 経由） |
| ビルドコマンド | `pnpm pages:build`（apps/web 配下） |

> ビルド設定（Root directory / Build command / Build output directory）は Cloudflare ダッシュボードの UI 上から確認・編集不可。プロジェクト作成時に設定済み。

### API — Cloudflare Workers (screencraft-api)

| 項目 | 値 |
|---|---|
| プロジェクト名 | `screencraft-api` |
| フレームワーク | Hono |
| デプロイツール | Wrangler |
| デプロイ | `wrangler deploy`（apps/api 配下） |

---

## screencraft-web 環境変数（Cloudflare Pages Production）

ダッシュボード: Settings > Variables and Secrets

| 変数名 | Type | 値 |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | Text | `https://api.screenshot-craft.app` |
| `NEXT_PUBLIC_POSTHOG_HOST` | Text | `https://us.i.posthog.com` |
| `NEXT_PUBLIC_POSTHOG_KEY` | Text | `phc_jDi1vzdwrSqV6czofmBD3sS7xjuec5K1Nn83qcD6tkJ` |
| `NEXT_PUBLIC_SENTRY_DSN` | Text | `https://2b44c8e7f2f881c0258bdc177535bb03@o4511098219528192.ingest.us.sentry.io/4511098231717888` |
| `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` | Secret | 暗号化済み（値確認不可） |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Text | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |
| `NEXT_PUBLIC_SUPABASE_URL` | Text | `https://tkgcahfeqwmjajsougdw.supabase.co` |
| `NODE_VERSION` | Text | `20` |

### Runtime 設定

| 項目 | 値 |
|---|---|
| Compatibility date | 2026-03-23 |
| Compatibility flags | `nodejs_compat` |
| Fail open/closed | Fail open |

### Bindings

現在なし（未設定）

---

## screencraft-api 環境変数（Cloudflare Workers Secrets）

Wrangler CLI で設定:

```bash
export CLOUDFLARE_API_TOKEN="..."
cd screencraft/apps/api
echo "<値>" | npx wrangler secret put SUPABASE_URL
echo "<値>" | npx wrangler secret put SUPABASE_SERVICE_ROLE_KEY
echo "<値>" | npx wrangler secret put ANTHROPIC_API_KEY
echo "<値>" | npx wrangler secret put STRIPE_SECRET_KEY
echo "<値>" | npx wrangler secret put STRIPE_WEBHOOK_SECRET
echo "<値>" | npx wrangler secret put RESEND_API_KEY
echo "<値>" | npx wrangler secret put SENTRY_DSN
```

### Bindings（wrangler.toml）

| Type | Name | Value |
|---|---|---|
| R2 Bucket | `R2` | `screencraft-exports` |
| Var | `ENVIRONMENT` | `production` |

---

## ローカル開発環境の環境変数

### apps/web/.env.local

Next.js は `apps/web/.env.local` から読む（モノレポルートの `.env` は読まない）。

```
NEXT_PUBLIC_SUPABASE_URL=https://tkgcahfeqwmjajsougdw.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<Supabase ダッシュボードから取得>
NEXT_PUBLIC_API_URL=https://api.screenshot-craft.app
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=
NEXT_PUBLIC_POSTHOG_KEY=phc_jDi1vzdwrSqV6czofmBD3sS7xjuec5K1Nn83qcD6tkJ
NEXT_PUBLIC_POSTHOG_HOST=https://us.i.posthog.com
NEXT_PUBLIC_SENTRY_DSN=https://2b44c8e7f2f881c0258bdc177535bb03@o4511098219528192.ingest.us.sentry.io/4511098231717888
```

> **重要**: `.env.local` はモノレポルートではなく `apps/web/` に配置すること。

---

## Cloudflare API トークン（M8 デプロイ用）

| 項目 | 値 |
|---|---|
| トークン名 | `screencraft-deploy` |
| Account ID | `4397f5ef54372634d9d2b5ead948d7a9` |
| 用途 | M8 サーバーからの wrangler deploy（SSH 環境、ブラウザなし） |
| 認証方法 | `export CLOUDFLARE_API_TOKEN=...` |

### Permissions

| カテゴリ | Permission | アクセス |
|---|---|---|
| Account | Workers Scripts | Edit |
| Account | Cloudflare Pages | Edit |
| Account | Workers R2 Storage | Edit |
| User | Memberships | Read |

> トークン値は `.env` やリポジトリに保存しないこと。

---

## データベース・認証 — Supabase

| 項目 | 値 |
|---|---|
| Project ID | `tkgcahfeqwmjajsougdw` |
| URL | `https://tkgcahfeqwmjajsougdw.supabase.co` |
| ダッシュボード | https://supabase.com/dashboard/project/tkgcahfeqwmjajsougdw |
| 認証方式 | Email + Google SSO |
| マイグレーション | `supabase/migrations/001〜005` |

### カスタム RPC 関数

| 関数 | 定義場所 | 用途 |
|---|---|---|
| `increment_usage()` | `003_usage.sql` | 使用量インクリメント |
| `reset_monthly_usage()` | `003_usage.sql` | 月次使用量リセット |

---

## ストレージ — Cloudflare R2

| 項目 | 値 |
|---|---|
| バケット名 | `screencraft-exports` |
| 用途 | 書き出し画像の一時保存 |

---

## AI — Anthropic Claude Haiku

| 項目 | 値 |
|---|---|
| モデル | `claude-haiku-4-5-20251001` |
| 用途 | 自然言語 → キャンバス操作 JSON 変換 |
| API キー格納 | Workers Secret: `ANTHROPIC_API_KEY` |

---

## 決済 — Stripe

| 項目 | 値 |
|---|---|
| 課金モデル | 月額サブスク（4プラン） |
| PPP | 国別動的価格設定あり |
| Webhook | `POST /stripe/webhook`（Stripe 署名検証） |

---

## Cron ジョブ

| スケジュール | 処理 | 定義ファイル |
|---|---|---|
| 毎月 1 日 02:00 UTC | 月次使用量リセット | `apps/api/src/cron/staleUsers.ts` |
| 毎週月曜 09:00 UTC | 90 日未使用ユーザーへのリエンゲージメントメール | `apps/api/src/cron/staleUsers.ts` |

---

## デプロイ手順

### フロントエンド（自動）

`main` ブランチに push するだけで Cloudflare Pages が自動ビルド・デプロイ。

### API（手動）

```bash
export CLOUDFLARE_API_TOKEN="..."
cd screencraft/apps/api
npx wrangler deploy
```

---

## 開発環境

| 環境 | アクセス方法 | 成果物確認 URL |
|------|-------------|---------------|
| 本番確認 | ブラウザ | https://screenshot-craft.app |
| ローカル開発（自宅） | VS Code Remote-SSH | `localhost:3000`（自動ポートフォワード） |
| ローカル開発（職場） | Tailscale 経由 | `http://100.83.181.125:3000` |

> ローカル dev server 起動時は `apps/web/.env.local` の存在を確認すること。
> 詳細 → `screencraft/docs/environment-switching.md`, `screencraft/docs/remote-dev-setup-log.md`

---

## プラン制限（参考）

| 操作 | Free | Lite | Pro | Agency |
|---|---|---|---|---|
| スクショ書き出し | 2 回/月 | 15 回/月 | 50 回/月 | 無制限 |
| AI インタラクション | 5 回/月 | 50 回/月 | 200 回/月 | 無制限 |
| 月額（JPY） | 無料 | ¥580 | ¥980 | ¥3,900 |
