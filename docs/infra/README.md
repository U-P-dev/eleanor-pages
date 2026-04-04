# インフラ構成 — 全体マップ

> **最終更新**: 2026-04-03
> 各プロジェクトの詳細は同フォルダ内の個別ファイルを参照。
> 機密情報（APIキー・パスワード等）は `tasks/secrets/` に格納（git管理外）。

---

## プロジェクト一覧

| プロジェクト | ファイル | ステータス |
|---|---|---|
| コーポレートサイト (eleanor-dev.com) | [eleanor-website.md](./eleanor-website.md) | 本番稼働中 |
| SONO-HINO（Flutterタスク管理） | [sono-hino.md](./sono-hino.md) | リリース準備中 |
| Screencraft（AIスクショSaaS） | [screencraft.md](./screencraft.md) | 開発中 |
| KEIBA-YARAZU（競馬自動投票） | [keiba-yarazu.md](./keiba-yarazu.md) | 開発中 |
| インボイスバリデーター Pro | [invoice-validator.md](./invoice-validator.md) | 開発中 |
| Memoria（学習支援アプリ） | [memoria.md](./memoria.md) | 開発中 |
| paper-search（AI論文検索） | [paper-search.md](./paper-search.md) | 開発中 |
| パワポ侍（PowerPointドリル） | [powpo-samurai.md](./powpo-samurai.md) | 未デプロイ |
| FX-tool-platform | [fx-tool-platform.md](./fx-tool-platform.md) | 企画段階 |
| jido-lp-sales（LP制作自動化） | [jido-lp-sales.md](./jido-lp-sales.md) | 開発中 |
| kindle-auto-summary（Kindle→PDF） | [kindle-auto-summary.md](./kindle-auto-summary.md) | ユーティリティ |

## 共通基盤

| リソース | ファイル |
|---|---|
| Google お支払い（AdMob/AdSense共通） | [google-payments.md](./google-payments.md) |
| ローカル・リモート開発環境 | [local-dev.md](./local-dev.md) |

---

## 横断ガイド（docs/guides/）

| ガイド | 概要 |
|---|---|
| [Apple Developer Organization 移行](../guides/apple-developer-organization-migration.md) | Individual → Organization 切替手順（個人事業主向け） |
| [AdSense セットアップ](../guides/adsense-setup.md) | Next.js App Router での AdSense 実装手順 |
| [Dev Server プレビューガイド](../guides/localhost-preview-guide.md) | リモート環境での開発サーバーアクセス方法 |

---

## サービス横断マップ

| サービス | 利用プロジェクト |
|---|---|
| **GitHub Pages** | コーポレートサイト |
| **Cloudflare DNS** | コーポレートサイト（DNS管理・メールルーティング） |
| **Cloudflare Pages / Workers / R2** | Screencraft |
| **AWS Lambda / DynamoDB / S3 / EventBridge** | KEIBA-YARAZU |
| **Supabase** | Screencraft / インボイスバリデーター / Memoria / SONO-HINO |
| **Vercel** | インボイスバリデーター |
| **Stripe** | Screencraft / インボイスバリデーター / Memoria |
| **AdMob** | SONO-HINO |
| **IAP (App Store / Google Play)** | SONO-HINO / Memoria |
| **Claude Haiku** | Screencraft |
| **OpenAI GPT-4o Vision** | Memoria |

---

## ドメイン・アカウント情報

| 項目 | 値 |
|---|---|
| 事業ドメイン | `eleanor-dev.com` |
| 事業メール | `contact@eleanor-dev.com` → Gmail転送 |
| GitHub アカウント | `U-P-dev` |
| AWS リージョン | `ap-northeast-1`（東京） |
| AdSense パブリッシャーID | `ca-pub-6133561595210589` |
