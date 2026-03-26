# インボイスバリデーター Pro インフラ構成

> **概要**: 適格請求書発行事業者番号（T+13桁）リアルタイム照合 Web ツール
> **事業ID**: `B-FN-002`
> **リポジトリ**: `C:\Projects\invoice-validator-pro\`
> **ステータス**: 開発中（Phase 1: MVP）

---

## アーキテクチャ概要

```
Vercel（Next.js / フロントエンド + API Routes）
  ├── 国税庁インボイス公表サイト API（外部 / 無料・認証不要）
  ├── Supabase（認証・利用回数管理）
  └── Stripe Checkout（課金）
```

---

## ホスティング — Vercel

| 項目 | 値 |
|---|---|
| フレームワーク | Next.js + Tailwind CSS |
| リージョン | `nrt1`（東京） |
| API キャッシュ | `/api/*` は `no-store`（vercel.json で設定済み） |
| インフラコスト | ¥0〜3,000/月（初期） |

---

## データベース・認証 — Supabase

| 用途 | 内容 |
|---|---|
| 認証 | ユーザー管理 |
| 利用回数管理 | API コール数・プラン別制限 |

---

## 外部 API

| API | 用途 | コスト | 認証 |
|---|---|---|---|
| 国税庁インボイス公表サイト API | T番号リアルタイム照合 | 無料 | 不要 |

---

## 決済 — Stripe Checkout

| プラン | 月額 | 用途 |
|---|---|---|
| 個人プラン | ¥980 | 単件・CSV照合 |
| 法人CSVプラン | ¥4,980 | CSV一括処理 |
| API連携プラン | ¥9,800 | API エンドポイント提供 |

---

## 環境変数

`.env.local` に設定（`.env.local.example` を参照）:

```
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=
```

---

## 開発フェーズ

| フェーズ | 内容 |
|---|---|
| Phase 1 | 単件照合 MVP（国税庁 API 連携・LP 公開） |
| Phase 2 | CSV 一括照合（有料機能）+ Stripe 課金 |
| Phase 3 | SEO 記事 5 本 + コンテンツ SEO 本格化 |
| Phase 4 | API 提供 + 法人向けダッシュボード |
