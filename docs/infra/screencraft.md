# Screencraft インフラ構成

> **概要**: AIスクリーンショットデザイン SaaS
> **リポジトリ**: `C:\Projects\screencraft\screencraft\`（pnpm モノレポ）
> **ステータス**: 開発中

---

## アーキテクチャ概要

```
ユーザー
  ↓ HTTPS
Cloudflare Pages（Next.js 15 / apps/web）
  ↓ API リクエスト
Cloudflare Workers（Hono / apps/api）
  ├── Supabase（認証 + PostgreSQL）
  ├── Cloudflare R2（書き出し画像）
  ├── Anthropic Claude Haiku（AI 操作変換）
  ├── Stripe（課金）
  └── Resend（メール）
```

---

## ホスティング

### フロントエンド — Cloudflare Pages

| 項目 | 値 |
|---|---|
| フレームワーク | Next.js 15（App Router） |
| ビルドコマンド | `pnpm pages:build`（apps/web 配下） |
| デプロイ | `pnpm pages:deploy` |

### API — Cloudflare Workers

| 項目 | 値 |
|---|---|
| フレームワーク | Hono |
| デプロイツール | Wrangler |
| デプロイ | `wrangler deploy`（apps/api 配下） |

---

## データベース・認証 — Supabase

| 項目 | 値 |
|---|---|
| 種別 | PostgreSQL + Auth |
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
| API キー格納 | Wrangler secret: `ANTHROPIC_API_KEY` |

---

## 決済 — Stripe

| 項目 | 値 |
|---|---|
| 課金モデル | 月額サブスク（4プラン: Free / Lite ¥580 / Pro ¥980 / Agency ¥3,900） |
| PPP | 国別動的価格設定あり |
| Webhook | `POST /stripe/webhook`（Stripe 署名検証） |

---

## 外部サービス一覧

| サービス | 用途 | Wrangler Secret |
|---|---|---|
| Supabase | DB・認証 | `SUPABASE_URL` / `SUPABASE_SERVICE_ROLE_KEY` |
| Anthropic | Claude Haiku API | `ANTHROPIC_API_KEY` |
| Stripe | 課金・Webhook | `STRIPE_SECRET_KEY` / `STRIPE_WEBHOOK_SECRET` |
| Resend | トランザクションメール | `RESEND_API_KEY` |
| Sentry | エラー監視 | `SENTRY_DSN` |
| PostHog | アナリティクス | `NEXT_PUBLIC_POSTHOG_KEY`（Web 環境変数） |

---

## 環境変数

### apps/web/.env.local（Next.js）

```
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
NEXT_PUBLIC_API_URL=http://localhost:8787
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=
NEXT_PUBLIC_POSTHOG_KEY=
NEXT_PUBLIC_POSTHOG_HOST=https://app.posthog.com
NEXT_PUBLIC_SENTRY_DSN=
```

### apps/api（Wrangler Secrets）

```bash
wrangler secret put SUPABASE_URL
wrangler secret put SUPABASE_SERVICE_ROLE_KEY
wrangler secret put ANTHROPIC_API_KEY
wrangler secret put STRIPE_SECRET_KEY
wrangler secret put STRIPE_WEBHOOK_SECRET
wrangler secret put RESEND_API_KEY
wrangler secret put SENTRY_DSN
```

---

## Cron ジョブ

| スケジュール | 処理 | 定義ファイル |
|---|---|---|
| 毎月 1 日 02:00 UTC | 月次リセット通知メール | `apps/api/src/cron/staleUsers.ts` |
| 毎週月曜 09:00 UTC | 90日塩漬けユーザーへのリエンゲージメントメール | `apps/api/src/cron/staleUsers.ts` |

---

## 初期セットアップ手順

1. Supabase プロジェクト作成 → `supabase/migrations/001〜005` を順番に実行
2. Cloudflare R2 バケット `screencraft-exports` を作成
3. Stripe で月払い・年払いの Price ID を作成
4. `.env.local` と Wrangler secrets に各値を設定
5. `cd screencraft && pnpm install && pnpm dev`

---

## 開発環境の切り替え（自宅PC ↔ 社用PC SSH）

| 環境 | アクセス方法 | ブラウザURL |
|------|-------------|------------|
| 自宅PC（直接） | ターミナルで `pnpm dev` | `http://localhost:3000` |
| 社用PC → 自宅PC | VS Code Remote SSH + Dev Tunnels | `https://{tunnel-id}-3000.jpe1.devtunnels.ms` |

**詳細手順・トラブルシューティング** → `screencraft/docs/environment-switching.md`

---

## プラン制限（参考）

| 操作 | Free | Lite | Pro | Agency |
|---|---|---|---|---|
| スクショ書き出し | 2回/月 | 15回/月 | 50回/月 | 無制限 |
| AI インタラクション | 5回/月 | 50回/月 | 200回/月 | 無制限 |
| 月額（JPY） | 無料 | ¥580 | ¥980 | ¥3,900 |
