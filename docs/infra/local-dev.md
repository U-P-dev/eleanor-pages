# ローカル・リモート開発環境

---

## 作業ディレクトリ構成

| パス（Linux / M8） | 内容 |
|---|---|
| `/home/dev/projects/eleanor-pages/` | GitHub Pages リポジトリ（`U-P-dev/eleanor-pages`） |
| `/home/dev/projects/sono-hino/` | SONO-HINO Flutter コード |
| `/home/dev/projects/screencraft/` | Screencraft モノレポ |
| `/home/dev/projects/KEIBA_MatchFixing_Detection/` | KEIBA-YARAZU |
| `/home/dev/projects/invoice-validator-pro/` | インボイスバリデーター Pro |
| `/home/dev/projects/Memoria/` | Memoria モノレポ |
| `/home/dev/projects/paper-search/` | AI 論文検索 |
| `/home/dev/projects/jido-lp-sales/` | LP 制作自動化 |
| `/home/dev/projects/powpo-samurai/` | パワポ侍 |
| `/home/dev/projects/fx-tool-platform/` | FX ツール |
| `/home/dev/projects/kindle-auto-summary/` | Kindle スクショ→PDF |

> Dev Server プレビュー方法（LAN / Tailscale / Funnel）→ [localhost-preview-guide.md](../guides/localhost-preview-guide.md)

---

## リモート開発 — VS Code Remote Tunnels

### 構成

```
外出先 PC ──（HTTPS port 443）──▶ Microsoft リレー ──▶ 自宅 PC（全処理はここ）
```

- コード実行・ファイル操作・git・Claude Code の API 通信など **すべて自宅 PC で処理**
- 外出先 PC は画面表示とキー入力の転送のみ
- 外出先 PC の通信制限は関係ない（Microsoft リレーへの port 443 が通れば接続できる）
- **設定済み・稼働中**

### セットアップ手順（再セットアップ時）

WSL2 ではなく **Windows の VS Code** から操作すること（Windows Credential Manager が keyring として機能するため、WSL2 の gnome-keyring 不要）:

1. 自宅 PC の Windows VS Code を開く
2. 左下のアカウントアイコン → **「Turn on Remote Tunnel Access...」**
3. GitHub でサインイン・トンネル名を設定

### 外出先からの接続

外出先 PC の VS Code で:

1. リモートエクスプローラー → ドロップダウンで **「Tunnels」**
2. 同じ GitHub アカウントでサインイン → トンネル名をクリック

### 注意事項

- **自宅 PC は電源 ON のまま・スリープなしにすること**
  - Windows 設定 → システム → 電源とスリープ → スリープ: **なし**
- 自宅 PC の電源が切れた・スリープに入った時点で接続が切れる

---

---

## 開発サーバーのポートフォワーディング（VSCode Remote Tunnels 経由作業時）

### ⚠️ 絶対に覚えること：localhost は使えない

VSCode Remote Tunnels 経由でリモート作業している場合、**社用PCのブラウザで `localhost:3000` を開いても自宅PCの開発サーバーには届かない**。

```
社用PCブラウザ → localhost:3000  → ❌ 社用PC自身のポート（何も動いていない）
社用PCブラウザ → https://{tunnel-name}-3000.jpe1.devtunnels.ms → ✅ Microsoft リレー → 自宅PCのポート3000
```

### 開発サーバーへのアクセス手順

1. **VSCode Ports タブでポートを転送**
   - 自宅PCで開発サーバーを起動（`pnpm dev` 等）
   - VSCode 下部「Ports」タブ → 「Forward a Port」
   - 使用するポート番号を追加（例: `3000`, `8787`）
   - 転送後、`https://{tunnel-name}-{port}.jpe1.devtunnels.ms` の URL が発行される

2. **ポートの可視性を Public に設定**（必須）
   - Ports タブで該当ポートを右クリック →「Port Visibility」→ **Public**
   - **Private のままだと Microsoft 認証が要求され、ブラウザから API 呼び出しがすべてブロックされる**

3. **アプリの URL 設定をトンネル URL に変更**
   - 環境変数・CORS・OAuth リダイレクト URL など、`localhost` を参照している設定をすべてトンネル URL に変更する
   - 詳細は各プロジェクトの `docs/environment-switching.md` 参照

### 現在のトンネル名

| プロジェクト | トンネル名 | フロント URL | API URL |
|---|---|---|---|
| Screencraft | `fkpkwtft` | `https://fkpkwtft-3000.jpe1.devtunnels.ms` | `https://fkpkwtft-8787.jpe1.devtunnels.ms` |

> トンネル名は自宅PCで「Turn on Remote Tunnel Access」を設定した際に決まる。
> 変更した場合は上の表を更新すること。

### next-intl 使用プロジェクトの注意点

`localePrefix: 'as-needed'` の設定では、英語ブラウザでアクセスすると `/en/` へリダイレクトされる。
App Router に `[locale]` ディレクトリがない場合、`/en/` は 404 になる。

→ **`localePrefix: 'never'` に設定すること**（`i18n/routing.ts`）。ロケールはURLではなくブラウザヘッダー・Cookieで検出される。

### 初回アクセス時の警告について

トンネル URL に初めてアクセスすると以下の警告が表示される。これは **正常な Microsoft のセキュリティ確認**。

> "You are about to connect to a developer tunnel at: ..."

→ **「Continue」をクリックするだけ**。同じブラウザ・同じトンネルでは以降表示されない。

---

## SSH 認証

| 鍵 | 用途 |
|---|---|
| `~/.ssh/id_ed25519` | GitHub（`U-P-dev`）への SSH push |
