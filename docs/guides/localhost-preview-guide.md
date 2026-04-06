# リモート開発環境 Dev Server プレビューガイド

## 環境構成

| 項目 | 値 |
|------|-----|
| リモートサーバー | GMKtec M8 / Ubuntu Server 24.04 LTS |
| ローカルIP（自宅LAN） | 192.168.3.100 |
| Tailscale IP | 100.83.181.125 |
| Tailscale Funnel URL | https://m8.tailea005c.ts.net |
| code-server | ポート8080（Funnel ポート443 で公開中） |
| Tailscale operator | `dev`（sudo 不要に設定済み） |

## なぜ localhost:3000 にアクセスできないのか

dev server は M8 上で動作しているため、社用PC やスマホのブラウザで `localhost:3000` にアクセスしても何も表示されない。`localhost` はアクセス元のデバイス自身を指すためである。

---

## 推奨: Tailscale Funnel でポート公開（全プロジェクト共通）

**SSH ポートフォワード不要。どのネットワークからでもブラウザでアクセス可能。**

### 前提（初回のみ・設定済み）

```bash
# sudo 不要にする（一度だけ実行すれば永続）
sudo tailscale set --operator=$USER
```

### Funnel ポート割り当て

| Funnel ポート | 用途 | ローカルポート | URL |
|--------------|------|---------------|-----|
| 443 | code-server | 8080 | https://m8.tailea005c.ts.net |
| 8443 | フロントエンド | 3000 | https://m8.tailea005c.ts.net:8443 |
| 10000 | API / バックエンド | 8787 | https://m8.tailea005c.ts.net:10000 |

> Tailscale Funnel が使えるポートは **443, 8443, 10000** の3つのみ。

### 公開コマンド

```bash
# フロントエンド（ポート3000）を公開
tailscale funnel --https 8443 --bg 3000

# API（ポート8787）を公開
tailscale funnel --https 10000 --bg 8787

# 状態確認
tailscale funnel status

# 解除
tailscale funnel --https 8443 off
tailscale funnel --https 10000 off

# 全解除（code-server 含む）
tailscale funnel reset
```

### プロジェクト側で必要な設定

#### 1. dev server を 0.0.0.0 にバインド

Funnel はサーバーの `127.0.0.1` に proxy するため、`0.0.0.0` バインドは必須ではないが、Tailscale IP 直接アクセスとの互換性のために推奨。

#### 2. API URL をFunnel URL に向ける

フロントエンドが別サービスの API を呼ぶ場合、環境変数を Funnel URL に設定する。

```bash
# 例: screencraft
NEXT_PUBLIC_API_URL=https://m8.tailea005c.ts.net:10000
```

#### 3. CORS に Funnel オリジンを追加

API 側の CORS 許可リストに Funnel のフロントエンド URL を追加する。

```
https://m8.tailea005c.ts.net:8443
```

#### 4. 認証サービス（Supabase 等）の Redirect URLs

OAuth リダイレクト先に Funnel URL を追加する。

```
https://m8.tailea005c.ts.net:8443/**
```

---

## 代替方法

### A. VS Code Remote-SSH 自動ポートフォワード（自宅LAN内）

VS Code Remote-SSH は、dev server 起動時に自動でポートフォワードを検出する。

1. VS Code で M8 に Remote-SSH 接続
2. ターミナルで dev server を起動
3. ブラウザで `localhost:3000` にアクセス

### B. SSH ポートフォワーディング（手動）

```bash
# 社用PCで実行
ssh -L 3000:localhost:3000 -L 8787:localhost:8787 dev@192.168.3.100

# バックグラウンド（シェル不要）
ssh -N -L 3000:localhost:3000 -L 8787:localhost:8787 dev@192.168.3.100
```

この場合、API URL は `http://localhost:8787` に設定する。

### C. LAN内直接アクセス

dev server を `0.0.0.0` にバインドして、LAN IP で直接アクセス。

```
http://192.168.3.100:3000
```

### D. Tailscale IP 直接アクセス（スマホ等、Tailscale インストール済みデバイス）

```
http://100.83.181.125:3000
```

---

## フレームワーク別 0.0.0.0 バインド設定

| フレームワーク | コマンド |
|--------------|---------|
| Next.js | `next dev --hostname 0.0.0.0` |
| Vite | `vite --host 0.0.0.0` |
| Wrangler (Hono) | `wrangler dev --ip 0.0.0.0` |
| Expo | `npx expo start --tunnel` |
| Django | `python manage.py runserver 0.0.0.0:8000` |
| Flask | `flask run --host=0.0.0.0` |
| Rails | `rails server -b 0.0.0.0` |

---

## 接続パターン早見表

| 状況 | 方法 | URL例 |
|------|------|-------|
| 職場 / 外出先 | **Tailscale Funnel（推奨）** | `https://m8.tailea005c.ts.net:8443` |
| 自宅 + VS Code | 自動ポートフォワード | `localhost:3000` |
| 自宅 + LAN | 0.0.0.0 バインド | `192.168.3.100:3000` |
| スマホ + Tailscale | Tailscale IP | `http://100.83.181.125:3000` |
| スマホ + Funnel | Tailscale Funnel | `https://m8.tailea005c.ts.net:8443` |
