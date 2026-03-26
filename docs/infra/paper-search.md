# paper-search インフラ構成

> **概要**: 日本語クエリで PubMed を検索する AI 論文検索 Web アプリ
> **リポジトリ**: `C:\Projects\paper-search\`
> **URL**: `paper-search.eleanor-dev.com`（`eleanor-dev.com` のサブドメイン）

---

## ホスティング

| 項目 | 値 |
|---|---|
| フレームワーク | Next.js 16（App Router / TypeScript） |
| Node.js | v20 必須（Next.js 16 要件） |
| デプロイ先 | 未定 |

---

## 外部サービス

| サービス | 用途 | 認証 |
|---|---|---|
| Anthropic Claude Haiku | キーワード候補生成・PubMed クエリ変換 | API キー |
| Anthropic Claude Sonnet | 論文日本語要約 | API キー（同上） |
| PubMed E-utilities | 論文検索 | NCBI API キー（任意・制限緩和用） |
| Semantic Scholar | 類似論文取得 | API キー（任意） |
| Supabase | レート制限 RPC / キャッシュ | URL + Service Role Key |
| Google AdSense | 広告 | パブリッシャー ID（`ca-pub-6133561595210589`） |

---

## 環境変数

`.env.local`（`.env.example` をコピーして設定）:

```
# 必須
ANTHROPIC_API_KEY=

# 推奨（レート制限緩和）
NCBI_API_KEY=
NCBI_EMAIL=

# 任意
SEMANTIC_SCHOLAR_API_KEY=
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
NEXT_PUBLIC_ADSENSE_CLIENT_ID=ca-pub-6133561595210589
```

> Supabase 未設定時はインメモリキャッシュ / レート制限にフォールバック。

---

## レート制限

| エンドポイント | 制限 | バックエンド |
|---|---|---|
| `/api/search` | 10 回/分 | Supabase RPC / インメモリ（デュアルモード） |
| `/api/suggest` | 15 回/分 | Supabase RPC / インメモリ（デュアルモード） |

---

## AdSense

`eleanor-dev.com` 単位で審査・管理（サブドメインは審査通過後に自動カバー）。
詳細: [eleanor-website.md](./eleanor-website.md)
