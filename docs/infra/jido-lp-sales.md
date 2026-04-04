# jido-lp-sales インフラ構成

> **概要**: LP/HP を持たない都内事業者への LP 制作営業〜納品〜保守を全自動化するシステム
> **リポジトリ**: `/home/dev/projects/jido-lp-sales/`
> **ステータス**: 開発中（ローカル Python スクリプト）
> **最終更新**: 2026-04-03

---

## 実行環境

| 項目 | 値 |
|---|---|
| 言語 | Python |
| 実行方式 | ローカルスクリプト（クラウドデプロイなし） |
| 仮想環境 | `.venv/` |
| 設定ファイル | `config/config.json`（.gitignore 必須） |

---

## 起動方法

```bash
python scripts/main.py          # 通常起動
python scripts/health_check.py  # ヘルスチェックのみ
python scripts/setup_gmail_auth.py  # Gmail OAuth2 初回認証
```

---

## 外部サービス一覧（11サービス）

| # | サービス | 用途 | 月額コスト | 認証方式 |
|---|---------|------|-----------|---------|
| 1 | **Anthropic Claude** | LP コンテンツ生成・メール分類・Vision QA | 数十〜数百円 | API キー |
| 2 | **Google Places API** | 事業者検索 | 無料（月1万件） | API キー |
| 3 | **Google Custom Search** | 事業者 Web 情報収集 | 無料（月100件） | API キー + CX ID |
| 4 | **Gmail OAuth2** | メール送受信 | 無料 | OAuth2（`credentials.json` → `token.json`） |
| 5 | **GitHub** | LP ホスティング（Pages） | 無料 | PAT（有効期限管理必須） |
| 6 | **Stripe** | 決済 | 取引額の 3.6% | Secret キー + Webhook Secret |
| 7 | **LINE Bot (Messaging API)** | 緊急通知・日次サマリー | 無料 | Channel Access Token |
| 8 | **Formspree** | LP お問合せフォーム受信 | 無料（月50件） | API キー |
| 9 | **Unsplash** | LP 画像取得 | 無料（月5000件） | Access Key |
| 10 | **reCAPTCHA v3** | LP スパム防止 | 無料 | Site Key + Secret Key |
| 11 | **Microsoft Clarity** | LP アクセス解析 | 無料 | Tracking ID |

> 詳細なセットアップ手順（API キー取得〜config.json記入）: プロジェクト内 `docs/setup.md`

---

## config.json 構成（概要）

| セクション | 主要キー | 必須/任意 |
|-----------|---------|----------|
| `api_keys` | anthropic, google_places, google_custom_search, github_token, stripe_secret, line_channel_access_token | 必須 |
| `github` | username, token_expires | 必須 |
| `sender` | name, company, address, phone, email（特商法表記用） | 必須 |
| `models` | lp_generation, email_classification, vision_qa | 任意 |
| `limits` | daily_email_limit(30), max_lps_per_run(10), max_retries(3) | 任意 |
| `search` | target_areas, target_industries, places_radius_meters | 必須 |
| `notifications` | line_emergency_threshold, line_daily_summary_hour | 任意 |

> 本番運用では `config.json` を `.env` に移行推奨。`config/config.json` と `.env` は `.gitignore` に追加必須。

---

## AI モデル

| 用途 | デフォルトモデル |
|------|----------------|
| LP 生成 | claude-sonnet-4-6 |
| メール分類 | claude-haiku-4-5-20251001 |
| Vision QA | claude-sonnet-4-6 |

---

## プロジェクト内ドキュメント（jido-lp-sales リポジトリ docs/）

| ファイル | スコープ |
|---|---|
| `setup.md` | API キー取得〜初回認証の完全手順（1,069行） |
| `architecture.md` | システム設計 |
| `flows.md` | 営業〜納品の業務フロー |
| `data-schema.md` | DB スキーマ |
| `business.md` | ビジネス戦略・ユニットエコノミクス |
| `legal.md` | 法的コンプライアンス |
| `ops.md` | 運用手順 |
| `marketing.md` | マーケティング戦略 |
| `risks.md` | リスク管理 |
