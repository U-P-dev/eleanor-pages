# リモート開発環境 Dev Server プレビューガイド

## 環境構成

| 項目 | 値 |
|------|-----|
| リモートサーバー | GMKtec M8 / Ubuntu Server 24.04 LTS |
| ローカルIP（自宅LAN） | 192.168.3.100 |
| Tailscale IP | 100.83.181.125 |
| Tailscale Funnel URL | https://m8.tailea005c.ts.net |
| code-server | ポート8080 で稼働中（Funnel経由で公開） |

## なぜ localhost:3000 にアクセスできないのか

dev server は M8 上で動作しているため、社用PC やスマホのブラウザで `localhost:3000` にアクセスしても何も表示されない。`localhost` はアクセス元のデバイス自身を指すためである。M8 上のサーバーに到達するには、以下いずれかの方法でポートを転送・公開する必要がある。

---

## 1. VS Code Remote-SSH 接続時（自宅LAN内）

社用PCとM8が同一LANにある場合の方法。

### 1-1. VS Code の自動ポートフォワード（推奨）

VS Code Remote-SSH は、ターミナルで dev server を起動すると自動的にポートフォワードを検出する。

1. VS Code で M8 に Remote-SSH 接続する
2. ターミナルで dev server を起動（例: `pnpm dev`）
3. 「ポート転送」パネルに自動でポートが表示される
4. 社用PCのブラウザで `localhost:3000` にアクセスできる

**ポート転送パネルの開き方:**
- `Ctrl + Shift + P` → 「Ports: Focus on Ports View」
- または下部パネルの「ポート」タブ

### 1-2. 手動でポートフォワードを追加

自動検出されない場合:

1. VS Code の「ポート」タブを開く
2. 「ポートの転送」ボタンをクリック
3. ポート番号（例: `3000`）を入力して Enter
4. 社用PCのブラウザで `localhost:3000` にアクセス

複数ポートが必要な場合（フロント + API など）は、それぞれ追加する。

### 1-3. ssh -L コマンドによるトンネリング

VS Code を使わず、ターミナルから直接トンネルを張る方法。

```bash
# 社用PC（Windows）の PowerShell / コマンドプロンプトで実行
# ローカルの3000番ポートを M8 の3000番ポートに転送
ssh -L 3000:localhost:3000 dev@192.168.3.100

# 複数ポートを同時に転送（フロント3000 + API 8787）
ssh -L 3000:localhost:3000 -L 8787:localhost:8787 dev@192.168.3.100
```

接続後、社用PCのブラウザで `localhost:3000` にアクセスできる。

**バックグラウンドで張る場合（接続だけしてシェルは不要）:**

```bash
ssh -N -L 3000:localhost:3000 -L 8787:localhost:8787 dev@192.168.3.100
```

`-N` はリモートコマンドを実行しない（トンネルだけ維持する）オプション。

### 1-4. LAN内直接アクセス

dev server を `0.0.0.0` にバインドしていれば、ポートフォワード無しでも直接アクセスできる。

```
http://192.168.3.100:3000
```

ただしフレームワークによってはデフォルトで `127.0.0.1` にしかバインドしないため、起動オプションの変更が必要（後述の「フレームワーク別設定」参照）。

---

## 2. code-server（ブラウザ）接続時（職場・外出先）

ブラウザで `https://m8.tailea005c.ts.net` にアクセスして code-server を使っている場合。

### 2-1. code-server 内蔵のポートフォワード機能

code-server は VS Code ベースのため、同等のポートフォワード機能がある。

1. code-server のターミナルで dev server を起動
2. 下部パネルの「ポート」タブに自動検出される
3. 表示されたローカルアドレス（例: `localhost:3000`）のリンクをクリック

**注意:** code-server 経由でのポートフォワードは、code-server 自体がブラウザ上で動作しているため、転送先は code-server のプロキシ URL になる。URL は以下の形式:

```
https://m8.tailea005c.ts.net/proxy/3000/
```

これが機能しない場合は、次の Tailscale Serve / Funnel を使う。

### 2-2. Tailscale Serve で追加ポートを公開

Tailscale ネットワーク内のデバイスからアクセスできるようにする方法。

```bash
# M8 上で実行 — ポート3000を Tailscale 経由で公開
sudo tailscale serve --bg https+insecure://localhost:3000

# 確認
tailscale serve status
```

公開後、社用PCのブラウザで以下にアクセス:

```
https://m8.tailea005c.ts.net:443   → code-server（既存）
https://m8.tailea005c.ts.net:3000  → dev server（追加）
```

**注意:** Tailscale Serve はデフォルトで Tailscale ネットワーク内のみアクセス可能。社用PC に Tailscale がインストールされている必要がある。

### 2-3. Tailscale Funnel で外部公開

社用PC に Tailscale が入っていない場合や、完全に外部からアクセスしたい場合。

```bash
# M8 上で実行 — ポート3000を Funnel（インターネット公開）で追加
sudo tailscale funnel --bg --set-path /app https+insecure://localhost:3000
```

**注意:**
- 現在 Funnel は `/` が code-server（ポート8080）に割り当て済み
- パスベースで分ける場合は `--set-path` を使う
- Funnel で公開するとインターネット上の誰でもアクセス可能になるため、認証がないページの公開には注意

### 2-4. 別ポートで Funnel を追加

パスベースではなくポートベースで分ける方法:

```bash
# ポート3000を Funnel で公開
sudo tailscale funnel --bg 3000 http://localhost:3000

# 状態確認
tailscale funnel status
```

アクセスURL: `https://m8.tailea005c.ts.net:3000`

### 2-5. Funnel / Serve の解除

```bash
# Serve / Funnel の設定をリセット
sudo tailscale serve reset

# 個別に解除する場合
sudo tailscale serve --remove /app
sudo tailscale funnel --remove 3000
```

---

## 3. スマホからのプレビュー

### 3-1. Tailscale 経由（推奨）

スマホに Tailscale アプリをインストール済みの場合、M8 の Tailscale IP に直接アクセスできる。

**前提:** dev server を `0.0.0.0` にバインドして起動すること。

```
http://100.83.181.125:3000
```

### 3-2. Tailscale Funnel 経由

dev server を Funnel で公開済みであれば、Tailscale アプリ不要でブラウザからアクセスできる。

```
https://m8.tailea005c.ts.net:3000
```

### 3-3. Termux + SSH からの確認

Termux で SSH 接続している場合は、ターミナルベースの確認のみ可能。

```bash
# Termux から M8 に SSH
ssh dev@100.83.181.125

# curl でレスポンス確認
curl -s http://localhost:3000 | head -20
```

ブラウザでのプレビューが必要な場合は、3-1 または 3-2 を使う。

---

## 4. フレームワーク別 0.0.0.0 バインド設定

LAN 内直接アクセスや Tailscale IP でのアクセスには、dev server を `0.0.0.0`（全インターフェース）にバインドする必要がある。

### Next.js

```bash
# package.json の scripts で設定
next dev --hostname 0.0.0.0 --port 3000

# または環境変数
HOSTNAME=0.0.0.0 next dev
```

### Vite (React, Vue, Svelte 等)

```bash
# コマンドライン
vite --host 0.0.0.0

# または vite.config.ts で設定
# server: { host: '0.0.0.0' }
```

### Expo (React Native)

```bash
# トンネルモード（外部アクセス用）
npx expo start --tunnel

# LAN モード（同一ネットワーク内）
npx expo start --lan
```

### Hono (Cloudflare Workers / Wrangler)

```bash
# wrangler dev はデフォルトで localhost のみ
# 0.0.0.0 バインドするには:
wrangler dev --ip 0.0.0.0
```

### Django

```bash
python manage.py runserver 0.0.0.0:8000
```

### Flask

```bash
flask run --host=0.0.0.0
```

### Rails

```bash
rails server -b 0.0.0.0
```

---

## 5. 接続パターン早見表

| 状況 | dev server の確認方法 | URL例 |
|------|----------------------|-------|
| 自宅 + VS Code Remote-SSH | 自動ポートフォワード | `localhost:3000` |
| 自宅 + LAN直接 | 0.0.0.0 バインド | `192.168.3.100:3000` |
| 職場 + code-server | code-server プロキシ | `m8.tailea005c.ts.net/proxy/3000/` |
| 職場 + Tailscale | Tailscale Serve | `https://m8.tailea005c.ts.net:3000` |
| 職場 + Funnel | Tailscale Funnel | `https://m8.tailea005c.ts.net:3000` |
| スマホ + Tailscale | Tailscale IP 直接 | `http://100.83.181.125:3000` |
| スマホ + Funnel | Funnel URL | `https://m8.tailea005c.ts.net:3000` |

---

## 6. Claude Code 開発時の注意事項

Claude Code でdev serverを起動する際は以下に注意:

1. **ポートフォワードの案内を忘れない** — `pnpm dev` 等でサーバーを起動した後、ユーザーの接続方法に応じたアクセスURLを案内する
2. **0.0.0.0 バインドが必要な場面を把握する** — VS Code Remote-SSH の自動フォワード以外では、基本的に `0.0.0.0` バインドが必要
3. **Tailscale Funnel の既存設定を壊さない** — `/` は code-server に割り当て済み。追加する場合はパスまたはポートで分ける
4. **screencraft の場合** — フロント（:3000）と API（:8787）の2ポートが必要。両方フォワードまたは公開すること
