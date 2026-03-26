# コーポレートサイト インフラ構成

> **URL**: https://eleanor-dev.com/
> **リポジトリ**: https://github.com/U-P-dev/eleanor-pages
> **ローカルパス**: `C:\Projects\eleanor-pages\`（git管理）

---

## ホスティング — GitHub Pages

| 項目 | 値 |
|---|---|
| リポジトリ | `U-P-dev/eleanor-pages` |
| ブランチ | `main` |
| カスタムドメイン | `eleanor-dev.com`（CNAME ファイルで設定済み） |
| HTTPS | Enforce HTTPS 有効（Let's Encrypt 自動発行） |
| SSH認証 | `~/.ssh/id_ed25519`（U-P-dev として設定済み） |

### デプロイ手順

```bash
# C:\Projects\eleanor-pages\ で操作
git add <files>
git commit -m "feat|fix|chore: description"
git push origin main

# デプロイ確認（SHA が最新コミットと一致すること）
gh api repos/U-P-dev/eleanor-pages/deployments --jq '.[0] | {sha, created_at}'
```

---

## DNS — Cloudflare（eleanor-dev.com）

> **Proxy 設定**: 必ず **DNS only（オレンジ雲 OFF）** にすること。
> Proxy ON にすると GitHub Pages の HTTPS 証明書と競合してサイトが開かなくなる。

| タイプ | Name | Content | 用途 |
|--------|------|---------|------|
| A | `@` | `185.199.108.153` | GitHub Pages（IPv4） |
| A | `@` | `185.199.109.153` | GitHub Pages（IPv4） |
| A | `@` | `185.199.110.153` | GitHub Pages（IPv4） |
| A | `@` | `185.199.111.153` | GitHub Pages（IPv4） |
| AAAA | `@` | `2606:50c0:8000::153` | GitHub Pages（IPv6） |
| AAAA | `@` | `2606:50c0:8001::153` | GitHub Pages（IPv6） |
| AAAA | `@` | `2606:50c0:8002::153` | GitHub Pages（IPv6） |
| AAAA | `@` | `2606:50c0:8003::153` | GitHub Pages（IPv6） |
| CNAME | `www` | `u-p-dev.github.io` | www リダイレクト |
| TXT | `_github-pages-challenge-U-P-dev` | （認証トークン） | GitHub ドメイン認証 |

---

## メール — Cloudflare Email Routing

| 項目 | 値 |
|---|---|
| 受信アドレス | `contact@eleanor-dev.com` |
| 転送先 | `yusuke.p.development@gmail.com` |
| ステータス | 動作確認済み |

---

## AdSense

| 項目 | 値 |
|---|---|
| パブリッシャーID | `ca-pub-6133561595210589` |
| 登録サイト | `eleanor-dev.com`（プロトコル・末尾スラッシュなし） |
| 実装 | 全ページに `google-adsense-account` メタタグ・`ads.txt` 配置済み |

詳細: [../adsense-setup.md](../adsense-setup.md)

---

## 公開ページ一覧

| ファイル | URL |
|--------|-----|
| `index.html` | https://eleanor-dev.com/ |
| `company.html` | https://eleanor-dev.com/company.html |
| `privacy.html` | https://eleanor-dev.com/privacy.html |
| `support.html` | https://eleanor-dev.com/support.html |
| `account-deletion.html` | https://eleanor-dev.com/account-deletion.html |

---

## 注意事項

- `CNAME` ファイルを削除するとカスタムドメイン設定が消えるため **絶対に削除しない**
- Cloudflare の Proxy は **OFF のまま維持**（GitHub Pages との証明書競合を防ぐため）
- 表示不具合時は Ctrl+Shift+R（キャッシュクリア）またはシークレットモードで確認
