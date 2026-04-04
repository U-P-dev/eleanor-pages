# KEIBA-YARAZU インフラ構成

> **概要**: 地方競馬・競艇・競輪 D-Score 不正検知 & 自動投票システム
> **リポジトリ**: `/home/dev/projects/KEIBA_MatchFixing_Detection/`
> **IaC**: AWS CDK（Python）/ `cdk/stacks/yarazu_stack.py`
> **リージョン**: `ap-northeast-1`（東京）

---

## アーキテクチャ概要

```
EventBridge（5分毎 JST11-21時）
  → Lambda: yarazu-odds-monitor（オッズ取得・D-Score計算）
      → Lambda: yarazu-auto-bet（自動投票 / Playwright on ECR）
      → Lambda: yarazu-alert-handler（LINE/メール通知）

EventBridge（毎朝 9:00 JST）
  → Lambda: yarazu-session-refresh（楽天セッション更新 / Playwright on ECR）
```

---

## データ層

### DynamoDB テーブル

| テーブル名 | PK | SK | 用途 | 備考 |
|---|---|---|---|---|
| `yarazu-odds-history` | `race_id` | `timestamp` | オッズ時系列 | TTL 7日・RetainPolicy |
| `yarazu-bet-history` | `bet_id` | `race_id` | 投票記録 | PITR 有効・RetainPolicy |
| `yarazu-system-state` | `state_key` | — | Kill Switch / 連続不的中カウンタ | RetainPolicy |

### S3 バケット

| バケット名 | 用途 | 備考 |
|---|---|---|
| `yarazu-session-state-{account_id}` | Playwright `session_state.json` | 暗号化・全パブリックアクセスブロック |

---

## シークレット — AWS Secrets Manager

> **注意**: CDK デプロイ後に AWS コンソールまたは CLI で実際の値を入力すること

| シークレット名 | 内容 | 構造 |
|---|---|---|
| `yarazu/rakuten_credentials` | 楽天 ID ログイン情報・投票 PIN | `{"email": "", "password": "", "betting_pin": ""}` |
| `yarazu/line_token` | LINE Notify アクセストークン | `{"token": ""}` |
| `yarazu/imap_credentials` | MFA OTP 受信用 IMAP 設定 | `{"host": "imap.gmail.com", "user": "", "password": ""}` |

---

## Lambda 関数

| 関数名 | ランタイム | タイムアウト | メモリ | 用途 |
|---|---|---|---|---|
| `yarazu-odds-monitor` | Python 3.12（ZIP） | 9分 | 256 MB | オッズ取得・D-Score計算・AutoBet/Alert 起動 |
| `yarazu-auto-bet` | ECR コンテナ（Playwright） | 5分 | 1536 MB | 楽天競馬 自動投票 |
| `yarazu-session-refresh` | ECR コンテナ（Playwright） | 5分 | 1536 MB | ログインセッション更新 |
| `yarazu-alert-handler` | Python 3.12（ZIP） | 30秒 | 128 MB | LINE / メール通知送信 |

### Lambda 環境変数

**yarazu-odds-monitor:**

```
AUTOBET_LAMBDA_NAME=yarazu-auto-bet
ALERT_LAMBDA_NAME=yarazu-alert-handler
DYNAMODB_ODDS_TABLE=yarazu-odds-history
SYSTEM_STATE_TABLE=yarazu-system-state
ENABLED_SPORTS=keiba,kyotei,keirin
TZ=Asia/Tokyo
```

**yarazu-auto-bet:**

```
S3_BUCKET=yarazu-session-state-{account_id}
BET_HISTORY_TABLE=yarazu-bet-history
SYSTEM_STATE_TABLE=yarazu-system-state
TZ=Asia/Tokyo
```

**yarazu-session-refresh:**

```
S3_BUCKET=yarazu-session-state-{account_id}
SYSTEM_STATE_TABLE=yarazu-system-state
TZ=Asia/Tokyo
```

---

## スケジュール — EventBridge

| ルール名 | スケジュール | ターゲット | 用途 |
|---|---|---|---|
| `yarazu-odds-monitor-rule` | `*/5` 分 / UTC 02:00-12:00（JST 11:00-21:00） | OddsMonitor | 地方競馬開催時間帯の定期オッズ取得 |
| `yarazu-session-refresh-rule` | 毎日 00:00 UTC（JST 09:00） | SessionRefresh | ログインセッション事前更新 |

---

## 監視 — CloudWatch Alarms

| アラーム名 | メトリクス | 閾値 | 評価期間 |
|---|---|---|---|
| `yarazu-odds-monitor-errors` | OddsMonitor エラー数 | 3回以上 | 15分間 |
| `yarazu-auto-bet-errors` | AutoBet エラー数 | 1回以上 | 30分間 |

---

## 対応スポーツ

| スポーツ | フェッチャー | データソース | 単勝オッズ |
|---|---|---|---|
| 競馬（keiba） | `odds_fetcher.py` | `keiba.go.jp` API | あり |
| 競艇（kyotei） | `kyotei_fetcher.py` | `boatrace.jp` | あり |
| 競輪（keirin） | `keirin_fetcher.py` | `keirin.kdreams.jp` | なし（2連単から推定） |

---

## デプロイ手順

```bash
cd KEIBA_MatchFixing_Detection/cdk

# 初回のみ: cdk.json の "account" を実際のAWSアカウントIDに変更
pip install -r requirements.txt

# Bootstrap（初回のみ）
cdk bootstrap aws://YOUR_ACCOUNT_ID/ap-northeast-1

# デプロイ
cdk deploy
```

---

## セキュリティ注意事項

- **デプロイ後**: S3 バケットの公開設定を必ず確認すること
- **IMAP**: Gmail アプリパスワード使用。漏洩時は即ローテーション
- **CloudWatch ログ**: 認証情報・session token・PIN がログに出力されていないか確認
- **本番有効化前**: `DRY_RUN=true` でテストし `yarazu-system-state` の状態を確認
- **`--no-sandbox` Chromium**: Lambda 実行要件のためサンドボックス無効（仕様）
