# Memoria インフラ構成

> **概要**: 参考書・問題集写真を AI 解析→間隔反復復習通知する学習支援アプリ
> **プラットフォーム**: iOS / Android（Expo）+ Web（Next.js）
> **リポジトリ**: `/home/dev/projects/Memoria/`（GitHub: `U-P-dev/Memoria`）
> **ステータス**: Phase 4/7/8 進行中

---

## アーキテクチャ概要

```
Mobile（Expo SDK 52）
Web（Next.js 14 App Router）
  ↓ Supabase Auth
Supabase（PostgreSQL + Storage + Edge Functions）
  ├── analyze-image Edge Function → OpenAI GPT-4o Vision
  ├── send-notifications Edge Function（Cron）
  └── stripe-webhook Edge Function
```

---

## BaaS — Supabase

| 機能 | 内容 |
|---|---|
| Auth | Email + ソーシャル |
| PostgreSQL | 9テーブル（全 RLS 有効） |
| Storage | バケット `problem-images`（ユーザーフォルダスコープ RLS） |
| Edge Functions | analyze-image / send-notifications / stripe-webhook |

### データベーステーブル

| テーブル | 用途 |
|---|---|
| `folders` | 問題集フォルダ |
| `problems` | 問題本体（LaTeX 形式） |
| `tags` | タグ |
| `problem_tags` | 問題↔タグ中間テーブル |
| `review_logs` | FSRS 復習ログ |
| `subscriptions` | サブスク・AI 使用量管理 |
| `notification_preferences` | 通知設定 |
| `push_tokens` | Expo Push トークン |
| `notification_logs` | 通知送信ログ |

### マイグレーション

| ファイル | 内容 |
|---|---|
| `00001_initial_schema.sql` | コアスキーマ + `handle_new_user()` + `reset_monthly_ai_usage()` |
| `00002_notifications.sql` | 通知テーブル |

### Edge Functions

| 関数 | トリガー | 用途 |
|---|---|---|
| `analyze-image` | HTTP POST（認証必須） | GPT-4o Vision で問題画像解析・使用量チェック |
| `send-notifications` | Cron | 復習通知スケジューラー |
| `stripe-webhook` | Stripe Webhook | サブスク更新処理 |

---

## AI — OpenAI GPT-4o Vision

| 項目 | 値 |
|---|---|
| モデル | `gpt-4o`（Vision） |
| 用途 | 問題画像 → 問題文・解説の構造化抽出 |
| API キー格納 | Edge Function の環境変数のみ（クライアント非公開） |
| 抽象化 | `AIProvider` インターフェースで切り替え可能 |

---

## 決済

| プラットフォーム | 用途 |
|---|---|
| Stripe | Web サブスク（月額・checkout・portal） |
| App Store IAP | iOS 課金 |
| Google Play IAP | Android 課金 |

---

## Cron ジョブ

| 関数 | スケジュール | 用途 |
|---|---|---|
| `send-notifications` | 日次（復習期日ベース） | 復習リマインダー Push 通知 |
| `reset_monthly_ai_usage()` | 毎月 1 日 | AI 使用量リセット |

---

## 環境変数

### Web（apps/web/.env.local）

```
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
VAPID_PUBLIC_KEY=
VAPID_PRIVATE_KEY=
NEXT_PUBLIC_SENTRY_DSN=
```

### Mobile（apps/mobile/.env.local）

```
EXPO_PUBLIC_SUPABASE_URL=
EXPO_PUBLIC_SUPABASE_ANON_KEY=
EXPO_PUBLIC_SENTRY_DSN=
```

---

## 許可された外部通信先

Supabase / OpenAI / Stripe / Expo Push / Sentry のみ（それ以外は禁止）

---

## CI/CD

| 項目 | 値 |
|---|---|
| ツール | GitHub Actions |
| ファイル | `.github/workflows/ci.yml` |
| 実行条件 | push / PR to main |
| ステップ | pnpm install → typecheck → lint → build（Node.js 18） |
