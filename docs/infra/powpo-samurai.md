# パワポ侍 インフラ構成

> **概要**: PowerPoint ショートカットキーを侍テーマのドリル形式で学習する Web サービス
> **リポジトリ**: `/home/dev/projects/powpo-samurai/`
> **ステータス**: 開発中（未デプロイ）

---

## ホスティング — Vercel（未デプロイ）

| 項目 | 値 |
|---|---|
| フレームワーク | Next.js 14（App Router / TypeScript Strict） |
| Node.js | v18 |
| デプロイ先 | Vercel（予定） |

---

## データベース・認証 — Supabase（未接続）

| 用途 | 内容 |
|---|---|
| プレイログ | ユーザーのドリル結果記録（予定） |
| ランキング | スコアランキング（予定） |
| Auth | ユーザー認証（予定） |

---

## アナリティクス — GA4（未導入）

| 項目 | 値 |
|---|---|
| 設定方法 | `NEXT_PUBLIC_GA_ID` を `.env.local` に設定するだけで有効化 |
| Cookie 同意 | 同意後のみ GA4 読み込み（実装済み） |

---

## 環境変数

```
NEXT_PUBLIC_GA_ID=           # GA4 測定ID（設定すると有効化）
NEXT_PUBLIC_SUPABASE_URL=    # Supabase URL（未使用）
NEXT_PUBLIC_SUPABASE_ANON_KEY=  # Supabase Anon Key（未使用）
```

---

## 未完了インフラタスク

- [ ] Vercel デプロイ・カスタムドメイン設定
- [ ] Supabase 接続（プレイログ・ランキング）
- [ ] GA4 有効化（`NEXT_PUBLIC_GA_ID` 設定）
- [ ] Google Search Console 登録
- [ ] AdSense 申請
