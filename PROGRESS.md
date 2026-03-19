# エレノア 事業進捗ドキュメント

> **最終更新**: 2026-03-19
> **次の作業再開時は、このファイルと `tasks/todo.md` を参照すること**

---

## 事業概要

| 項目 | 内容 |
|------|------|
| 屋号 | エレノア（Eleanor） |
| 代表者 | 豊島 悠右（Yusuke Toyoshima） |
| 形態 | 個人事業主 |
| 事業内容 | スマートフォンアプリ開発・販売 |
| 主要アプリ | SONO-HINO（Flutterタスク管理アプリ） |
| 住所 | 〒160-0022 東京都新宿区新宿2丁目8番15号 パークフロント新宿 202号室 |
| メール | contact@eleanor-dev.com（Gmail転送設定済み） |
| ドメイン | eleanor-dev.com |
| サイト | https://eleanor-dev.com/ |

---

## インフラ構成

### GitHub Pages
- **リポジトリ**: https://github.com/U-P-dev/eleanor-pages
- **カスタムドメイン**: eleanor-dev.com（CNAME設定済み）
- **HTTPS**: Enforce HTTPS 有効（Let's Encrypt）
- **SSH認証**: `~/.ssh/id_ed25519`（U-P-dev として設定済み）

### Cloudflare DNS（eleanor-dev.com）
| タイプ | Name | Content | 用途 |
|--------|------|---------|------|
| A | @ | 185.199.108.153 ほか×4 | GitHub Pages |
| AAAA | @ | 2606:50c0:8000::153 ほか×4 | GitHub Pages（IPv6） |
| CNAME | www | u-p-dev.github.io | www リダイレクト |
| TXT | _github-pages-challenge-U-P-dev | （認証トークン） | ドメイン認証 |
- **Proxy**: DNS only（オレンジ雲OFF）にすること。オンにするとHTTPS証明書が競合する
- **Email Routing**: contact@eleanor-dev.com → yusuke.p.development@gmail.com（動作確認済み）

### ローカル開発環境
- **作業ディレクトリ**: `C:\Projects\00_eleanor\`（git管理外）
- **eleanor-pages clone先**: `C:\Projects\eleanor-pages\`
- **Flutterコード**: `C:\Projects\SONO-HINO\`

---

## 公開ページ一覧

| ページ | URL |
|--------|-----|
| トップ（事業者HP） | https://eleanor-dev.com/ |
| 会社情報 | https://eleanor-dev.com/company.html |
| プライバシーポリシー | https://eleanor-dev.com/privacy.html |
| サポート | https://eleanor-dev.com/support.html |
| アカウント削除 | https://eleanor-dev.com/account-deletion.html |

---

## 完了済みタスク

### 事業基盤
- [x] 開業届受理
- [x] バーチャルオフィス住所開設（2026-03-12）
- [x] 事業用口座開設完了（2026-03-17）
- [x] 事業用クレジットカード発行（配送待ち）
- [x] D-U-N-S 申請（2026-03-15、ケース #34349624）

### インフラ
- [x] 独自ドメイン `eleanor-dev.com` 取得（2026-03-17）
- [x] Cloudflare DNS 設定（A×4・AAAA×4・CNAME・TXT）
- [x] GitHub Pages ドメイン認証（TXTレコード）
- [x] Enforce HTTPS 有効化
- [x] 独自ドメインメール設定（contact@eleanor-dev.com → Gmail転送）

### サイト
- [x] 事業者HP 構築・公開（5ページ構成）
- [x] 全ページ統一ナビゲーション・フッター
- [x] ダーク・テック系デザインリニューアル（トップページ）
  - スマホモックアップ（純CSS、iPhone風）
  - スクロールアニメーション（Intersection Observer）
  - Coming Soonバッジ・開発者紹介セクション
  - グラデーションメッシュ・ノイズテクスチャ背景

### アプリ（SONO-HINO）
- [x] AdMob アカウント・広告ユニット・本番ID差し替え
- [x] AdMob 同意管理設定（EU規制・米国州規制・IDFA説明メッセージ）
- [x] Android Keystore 生成
- [x] コード実装（広告・IAP・ATT）完了
- [x] アプリアイコン自作完了
- [x] Google Play Console アプリ設定（グラフィック素材待ち）

---

## 未完了タスク（優先順）

### 1. D-U-N-S 受領待ち（2026-03-26〜04-02）
- ケース #34349624（D&B直接申請済み）
- 受領後 → Apple Developer Program 登録（Organization、$99/年）
- 受領後 → Google Play Developer 登録（$25）

### 2. AdMob 支払い情報登録
- 事業用口座カード・クレカ到着後に登録
- AdMob Console → お支払い → お支払いプロファイルを設定 → 銀行口座追加
- PIN レター受取待ち（数週間）→ 住所確認完了

### 3. スクリーンショット・フィーチャーグラフィック
- 外注中
- 入稿後 → Google Play Console のグラフィック素材を完了

### 4. HP表示確認
- Enforce HTTPS有効化後にページが開かない報告あり
- キャッシュクリア（Ctrl+Shift+R）またはシークレットモードで `https://eleanor-dev.com/` を確認

---

## 開発者アカウント登録手順（D-U-N-S受領後）

### Apple Developer Program
1. https://developer.apple.com/programs/enroll/ にアクセス
2. Organization として登録
3. D-U-N-S Number 入力
4. 法人情報・代表者情報を入力
5. $99/年 支払い

### Google Play Developer
1. https://play.google.com/console/ にアクセス
2. Organization として登録
3. D-U-N-S Number 入力
4. ドメイン（eleanor-dev.com）・メール（contact@eleanor-dev.com）を入力
5. $25 支払い

---

## ストア申請後のタスク（参考）

- [ ] IAP商品 `remove_ads` を各ストアに登録
- [ ] App Store・Google Play にプライバシーポリシーURL登録（https://eleanor-dev.com/privacy.html）
- [ ] iOS ビルド・Xcode アップロード（Mac環境必要）
- [ ] Android ビルド・Google Play 内部テストアップロード
- [ ] スクリーンショット・フィーチャーグラフィック登録
