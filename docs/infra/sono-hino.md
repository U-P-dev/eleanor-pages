# SONO-HINO インフラ構成

> **概要**: Flutter タスク管理アプリ（Timeline + Someday 2 ゾーン）
> **プラットフォーム**: iOS / Android
> **リポジトリ**: `C:\Projects\sono_hino\`
> **ステータス**: リリース準備中（D-U-N-S 受領後にストア申請）

---

## プラットフォーム・技術スタック

| 項目 | 値 |
|---|---|
| フレームワーク | Flutter 3.41.4 |
| 状態管理 | Supabase + Riverpod 2.x（手書き） |
| UI | Freezed 2.x / go_router（pubspec 宣言のみ・Navigator 使用） |

---

## 収益化

### AdMob（広告）

| 項目 | 値 |
|---|---|
| アカウント | 設定済み |
| 広告ユニット | 設定済み・本番 ID 差し替え済み |
| 同意管理 | EU 規制・米国州規制・IDFA 説明メッセージ 設定済み |
| AdSense パブリッシャーID | `ca-pub-6133561595210589` |
| 支払いプロファイル | 未設定（クレカ到着後に登録予定） |

### IAP（アプリ内課金）

| 商品ID | 種別 | 内容 |
|---|---|---|
| `remove_ads` | 買い切り | 広告非表示 |

---

## ストア登録状況

| ストア | 状況 | 備考 |
|---|---|---|
| Google Play Console | アプリ設定済み | グラフィック素材待ち（外注中） |
| App Store | 未登録 | Apple Developer Program 登録後（D-U-N-S 受領待ち） |

### ストア申請後のタスク

- [ ] `remove_ads` を各ストアに IAP 商品登録
- [ ] プライバシーポリシー URL 登録（https://eleanor-dev.com/privacy.html）
- [ ] Android ビルド → Google Play 内部テストアップロード
- [ ] iOS ビルド → Xcode アップロード（**Mac 環境必要**）
- [ ] スクリーンショット・フィーチャーグラフィック登録（外注品入稿後）

---

## ビルドコマンド

```bash
# 静的解析
flutter analyze

# テスト
flutter test

# コード生成（Freezed 等）
dart run build_runner build --delete-conflicting-outputs
```

---

## 関連ドキュメント（プロジェクト内 docs/）

| ファイル | 参照タイミング |
|---|---|
| `architecture.md` | 構造・プロバイダー・テーマ・広告/IAP・L10n |
| `database.md` | DB・RLS・RPC 関連 |
| `business-rules.md` | ビジネスロジック変更時（Rule A/C/D） |
| `known-issues.md` | バグ修正時（12 件の既知問題） |
| `security-rules.md` | パッケージ追加・外部通信時 |
