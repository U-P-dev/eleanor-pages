# Apple Developer Program: Individual → Organization 移行ガイド（個人事業主向け）

> **概要**: 個人事業主が Apple Developer Program を Individual から Organization に切り替え、App Store の販売者名を屋号にする手順
> **対象**: 日本の個人事業主（法人格なし）
> **作成日**: 2026-04-03
> **ステータス**: 移行準備中

---

## なぜ移行するのか

Individual アカウントでは App Store の「販売者（Seller）」欄に**本名が公開**される。Organization に移行すると屋号（例: Eleanor）が表示され、個人の氏名・住所を非公開にできる。

---

## 前提条件

| # | 条件 | 当事業の状況 |
|---|------|-------------|
| 1 | Apple Developer Program（Individual）に加入済み | ✅ 2026-03-31 登録済み |
| 2 | D-U-N-S 番号を取得済み | ✅ 698839776 |
| 3 | 開業届を税務署に提出済み | 要確認 |
| 4 | e-Tax の電子申請等証明データシート | 要取得（後述） |
| 5 | 独自ドメイン + Web サイト | ✅ eleanor-dev.com |
| 6 | 独自ドメインのメールアドレス | ✅ contact@eleanor-dev.com |
| 7 | 写真付き本人確認書類（運転免許証 両面） | 要準備 |

---

## 移行手順

### Step 1: 開業届の確認・提出

個人事業主であることを証明するために**開業届の控え**が必要。

- 未提出の場合: e-Tax または税務署窓口で提出（即日完了）
- freee開業・マネーフォワード・弥生 等で書類生成可能

### Step 2: 電子申請等証明データシートの取得

> ⚠️ **重要**: 開業届の控えだけでは不十分。e-Tax から「電子申請等証明データシート」を別途ダウンロードし、開業届の控えと**1つの PDF に結合**して提出する必要がある。

取得手順:
1. e-Tax にログイン
2. 「送信結果・お知らせ」→「メッセージボックス一覧」
3. 開業届の送信結果を開く
4. 「電子申請等証明データシート」をダウンロード
5. 開業届控えと結合して 1 PDF にまとめる

### Step 3: 就労証明書の準備

Apple は在籍証明書・名刺の提出を求める場合がある。個人事業主の場合:

- **就労証明書**: こども家庭庁のテンプレートを使い自己作成で可
- **名刺がない場合**: Apple に「名刺はありません」とメールで説明すれば免除される

### Step 4: Apple Developer Support に移行リクエスト

**方法 A: Developer ポータルから（推奨）**

1. https://developer.apple.com/account にサインイン
2. 「Membership Details」→「Update your information」
3. 「Switch to organization membership」を選択
4. 組織名・Web サイト URL・D-U-N-S 番号を入力
5. 送信

**方法 B: お問い合わせフォームから**

1. https://developer.apple.com/contact/ にアクセス
2. 「Account Updates and Renewals」を選択
3. Individual → Organization への移行を希望する旨を記載
4. CEO 名・組織名・D-U-N-S 番号・住所・電話番号を記載

### Step 5: 自動拒否への対処（高確率で発生）

> ⚠️ **個人事業主の場合、以下のエラーが高確率で返される:**
>
> 「この組織が法人であることを確認できませんでした。個人事業主/個人経営者の場合は個人として登録してください」

**これは想定内であり、突破可能。** 対処法:

1. Apple Developer Support にメールで連絡
2. 「個人事業主だが Organization への移行を希望する」旨を伝える
3. Apple 側で**手動の D-U-N-S 検証バイパス**が行われる
4. 組織情報入力フォームへのアクセスが許可される

複数の日本人開発者が同じ手順で成功を報告している。

### Step 6: 書類アップロード

Apple から指定されたポータルに以下をアップロード:

| # | 書類 | 備考 |
|---|------|------|
| 1 | 写真付き本人確認書類 | 運転免許証（両面）。健康保険証は不可 |
| 2 | 開業届控え + 電子申請等証明データシート | 1 PDF に結合 |
| 3 | 就労証明書（該当する場合） | 自己作成可 |

> アップロード時に、代替書類を使っている旨をメールで Apple に説明するとスムーズ。

### Step 7: 電話認証

- Apple から**カリフォルニアの番号**で確認電話がかかってくる場合がある
- 提出から 2 週間以内
- 英語対応の可能性あり（日本語サポートを希望する旨を事前に伝えておくとよい）

### Step 8: 承認・反映

- 承認後、App Store の販売者名・開発者名が屋号に変更される
- Paid Applications Agreement の再署名が求められる
- 税務フォームの再提出が必要（後述）

---

## 所要期間

| フェーズ | 期間 |
|---------|------|
| 開業届提出（e-Tax） | 即日 |
| D-U-N-S 取得（Apple 経由） | 2〜3 営業日（取得済み） |
| D-U-N-S データの Apple 同期待ち | 2 営業日以上 |
| Apple 初回レビュー | 2〜3 営業日 |
| 自動拒否 → サポート介入 | 1〜5 営業日 |
| 書類審査 | 1〜3 週間 |
| **合計目安** | **2〜6 週間** |

> 実績例: D-U-N-S 取得から 12 日で承認完了（note.com/ai_to_neko 報告）

---

## 移行後の変更点

### 変わるもの

| 項目 | 変更内容 |
|------|---------|
| App Store 販売者名 | 本名 → 屋号（全アプリに適用） |
| App Store 開発者名 | 屋号に変更 |
| 税務フォーム | W-8BEN（個人）→ W-8BEN-E（法人） |
| チーム管理 | 無制限のメンバー招待・ロール管理が可能に |
| Paid Applications Agreement | 再署名が必要 |

### 変わらないもの

| 項目 | 備考 |
|------|------|
| Team ID | そのまま |
| Apple ID | そのまま |
| 既存アプリ | 再提出不要・公開状態維持 |
| Bundle ID / App ID | そのまま |
| 証明書・プロビジョニングプロファイル | 基本的に継続（一時的に使用不可になる場合あり） |
| 年会費 | $99/年（12,980 円）のまま |

---

## IAP（アプリ内課金）がある場合の注意

sono-hino は `remove_ads`（買い切り IAP）を予定しているため、以下に注意:

- **IAP 商品はそのまま引き継がれる**（再作成不要）
- Paid Applications Agreement の再署名が完了するまで、新規 IAP 作成・価格変更は不可
- 税務フォーム再提出が完了するまで、**支払いが一時停止**する可能性あり
- 移行開始時点のアクティブな銀行口座に、移行前の収益が振り込まれる

> **推奨**: IAP 商品登録は Organization 移行が完了してから行う（sono-hino はまだ未登録なので問題なし）

---

## 税務フォームの変更

| 移行前（Individual） | 移行後（Organization） |
|---------------------|----------------------|
| W-8BEN（個人向け） | W-8BEN-E（法人向け） |

- 日米租税条約により、どちらの場合もロイヤルティの源泉徴収率は **0%**
- 税務フォームは App Store Connect で再提出
- 自分では変更できない場合、Apple Support に連絡して更新を依頼

---

## トラブルシューティング

### D-U-N-S 情報の不一致

D-U-N-S に登録された組織名・住所と Apple に入力する情報が**完全一致**していないと審査に落ちる。D-U-N-S 発行後、Apple のシステムに反映されるまで最低 2 営業日待つこと。

### メール認証のロックアウト

独自ドメインメールのワンタイムパスコード認証には**リトライ回数制限**がある。事前にメール受信が正常に動作することを確認してから認証に進むこと。ロックアウトされた場合は Apple にメールで解除を依頼。

### 証明書の一時利用不可

移行中にチームメンバーの Certificates, Identifiers & Profiles へのアクセスが一時的に失われる報告あり。移行前に有効な配布証明書があることを確認し、移行中にアプリ更新が必要にならないよう計画すること。

---

## 当事業での実行計画

| # | タスク | 状態 |
|---|--------|------|
| 1 | 開業届の提出状況を確認 | ⬜ |
| 2 | e-Tax から電子申請等証明データシートを取得 | ⬜ |
| 3 | 運転免許証を準備（両面スキャン） | ⬜ |
| 4 | Apple Developer ポータルから移行リクエスト送信 | ⬜ |
| 5 | 自動拒否された場合、Apple Support に連絡 | ⬜ |
| 6 | 書類アップロード | ⬜ |
| 7 | 電話認証に対応 | ⬜ |
| 8 | 承認後: Paid Applications Agreement 再署名 | ⬜ |
| 9 | 承認後: W-8BEN-E 税務フォーム提出 | ⬜ |
| 10 | App Store で販売者名が屋号に変更されたことを確認 | ⬜ |

---

## 参照

- [App Store を個人名→屋号にした話（Zenn: ASHIMOTO）](https://zenn.dev/ashimoto/books/1_appleprogram)
- [Apple Developer Program アカウントを個人から組織に変更（Qiita: GoHiromi, 2025-02）](https://qiita.com/GoHiromi/items/890de3fe5811d357e4bc)
- [身バレ防止＆テスター不要：組織アカウント取得ガイド（Zenn: yukapero）](https://zenn.dev/yukapero/articles/3b2bac9b576e93)
- [App Store の開発者名表示を屋号に変えた話（note: ギガビット）](https://note.com/gigabit_million/n/n8acc6f98d4f9)
- [Apple Developer Program を個人から法人に切り替える方法（AppSeed）](https://develop.hateblo.jp/entry/apple-dev-corporation)
- [Apple 公式: Program Enrollment](https://developer.apple.com/help/account/membership/program-enrollment/)
- [Apple 公式: Tax Information](https://developer.apple.com/help/app-store-connect/manage-tax-information/provide-tax-information/)
