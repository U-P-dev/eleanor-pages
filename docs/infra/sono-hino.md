# SONO-HINO インフラ構成

> **概要**: Flutter タスク管理アプリ（Timeline + Someday 2 ゾーン）
> **プラットフ���ーム**: iOS / Android
> **リポジトリ**: `/home/dev/projects/sono-hino/`
> **ステータ���**: リリース準備中（Organization 移行 → ストア申請）
> **最終更新**: 2026-04-03

---

## 技術スタック

| 項目 | ��� |
|---|---|
| フレームワーク | Flutter 3.41.4 |
| 状態管理 | Supabase + Riverpod 2.x（手書き） |
| UI | Freezed 2.x / go_router（pubspec 宣言のみ・Navigator 使用） |

---

## Supabase（バックエンド）

| 項目 | 値 |
|---|---|
| プロジェクト名 | `sono-hino` |
| リージョン | Northeast Asia / Tokyo |
| 認証 | Email + Password（最小8文字） |
| Realtime | `public.tasks` テーブルを監視 |

### テーブル: `public.tasks`

| カラム | 型 | 説明 |
|--------|-----|------|
| id | uuid (PK) | gen_random_uuid() |
| user_id | uuid (FK → auth.users) | 所有者 |
| parent_id | uuid (FK → self, CASCADE) | null = ルート |
| title | text | タスク名 |
| memo | text | メモ |
| is_completed | boolean | 完了フラグ |
| scheduled_date | date | null = Someday |
| rank | double precision | Lexorank 並び順 |
| reminder_at | timestamptz | リマインダー日時 |
| created_at / updated_at | timestamptz | タイムスタンプ |

**インデックス**: `idx_tasks_user_date`, `idx_tasks_parent`, `idx_tasks_rank`

### RLS ポリシー

全CRUD操作に `auth.uid() = user_id` チェック + クライアント側二重フィルタ。

### トリガー

| 名前 | 説明 |
|------|------|
| `set_updated_at` | UPDATE時に `updated_at` を自動更新 |
| `check_child_user_id` | 子の user_id が親と一致することを検証 |
| `trg_set_child_date` | サブタスク挿入時に親の日付を自動設定 |
| `trg_sync_children_date` | 親の日付変更時に子も連動更新 |

### RPC 関数（デプロイ済み 2026-03-01）

| 関数 | 説明 |
|------|------|
| `auto_reschedule_overdue(p_user_id)` | 過去日の未完了ルートタスクを今日に移動 |
| `rebalance_ranks(p_task_ids, p_new_ranks)` | ランク等間隔再設定 |
| `complete_descendants(p_task_id, p_user_id)` | 全子孫を一括完了 |
| `auto_complete_parent_chain(p_task_id, p_user_id)` | 兄弟全完了時に親を自動完了 |
| `uncheck_parent_chain(p_task_id, p_user_id)` | 完了解除時に親チェーンも解除 |
| `uncheck_descendants(p_task_id, p_user_id)` | 全子孫の完了を解除 |
| `repair_completion_consistency(p_user_id)` | 起動時の不整合修復 |

> SQL定義: sono-hino リポジトリ `docs/references/rpc_cascade_completion.sql`

---

## 収益化

### AdMob（アプリ内広告）

| 項目 | 値 |
|---|---|
| 広告ユニット | 設定済み・本番 ID 差し替え済み |
| 同意管理 | EU 規制・米国州規制・IDFA 説明メッセージ 設定済み |

> お支払い → [google-payments.md](./google-payments.md) を参照。

### IAP（アプリ内課金）

| 商品ID | 種別 | 内容 |
|---|---|---|
| `remove_ads` | 買い切り | 広告非表示（各ストア未登録） |

---

## ストア登録状況

| ストア | 状況 | 備考 |
|---|---|---|
| Google Play Console | アプリ設定済み | グラフィック素材待ち（外注中） |
| App Store | 未登録 | Organization 移行後に登録 → [移行ガイド](../guides/apple-developer-organization-migration.md) |

### ストア申請タスク

- [ ] `remove_ads` を各ストアに IAP 商品登録
- [ ] プライバシーポリシー URL 登録（https://eleanor-dev.com/privacy.html）
- [ ] Android ビルド → Google Play 内部テストアップロード
- [ ] iOS ビルド → Xcode アップロード（**Mac 環境必要**）
- [ ] スクリーンショット・フィーチャーグラフィック登録（外注品入稿後）

---

## プロジェクト内ドキュメント（sono-hino リポジトリ docs/）

| ファイル | スコープ |
|---|---|
| `architecture.md` | 構造・プロバイダー・テーマ・広告/IAP・L10n |
| `business-rules.md` | ビジネスロジック（Rule A/C/D） |
| `ui-structure.md` | UI・D&D・テーマ |
| `database.md` | スキーマ・RLS・トリガー・RPC リファレンス |
| `critical-patterns.md` | 致命的パターン・コーディングルール |
| `security-rules.md` | ゼロトラスト・OWASP |
