# Google AdSense 設定手順

> 作成日: 2026-03-22
> 対象サイト: paper-search.eleanor-dev.com（ルートドメイン: eleanor-dev.com）
> Publisher ID: ca-pub-6133561595210589

---

## 概要

Google AdSense を Next.js (App Router) サイトに組み込み、サイト審査を通過するための手順。
本ドキュメントは実際に躓いたポイントを含めて記録したもの。

---

## 実装済みコード

### ads.txt

`public/ads.txt`:
```
google.com, pub-6133561595210589, DIRECT, f08c47fec0942fa0
```

### サイト所有権確認メタタグ（SSR出力）

`src/app/layout.tsx`:
```typescript
export const metadata: Metadata = {
  other: {
    "google-adsense-account": process.env.NEXT_PUBLIC_ADSENSE_CLIENT_ID ?? "",
  },
};
```

→ `<meta name="google-adsense-account" content="ca-pub-XXXX">` としてSSR出力される。
**Googleクローラーが同意なしで読める唯一の方法。**

### AdSenseスクリプト（Cookieあり時のみ）

`src/components/ads/AdSenseScript.tsx`:
```typescript
// Cookie同意がないと return null になる
if (!clientId || !hasConsent) return null;
```

⚠️ Googleのクローラーは Cookie 同意をしないため、このスクリプトはクロール時に出力されない。
→ **AdSense所有権確認には使えない。**

---

## Step 1: Vercel 環境変数の設定（必須）

1. Vercel ダッシュボード → プロジェクト → Settings → Environment Variables
2. 追加:
   - Name: `NEXT_PUBLIC_ADSENSE_CLIENT_ID`
   - Value: `ca-pub-6133561595210589`
   - Environments: Production / Preview / Development すべてチェック
3. Save → Deployments → 最新デプロイの「...」→ Redeploy

環境変数未設定のままだと `google-adsense-account` メタタグの content が空になり、確認失敗する。

---

## Step 2: AdSense サイト登録

### 2-1. サインアップ

`https://adsense.google.com/start` にアクセス。

### 2-2. サイト URL 入力時の注意点

> ⚠️ **躓きポイント**: AdSense は**ルートドメイン単位**でサイトを登録する。
>
> - ❌ `paper-search.eleanor-dev.com`（サブドメインは「URLには有効なトップレベル ドメインを指定してください」エラー）
> - ❌ `https://eleanor-dev.com`（プロトコルを含めるとエラー）
> - ✅ `eleanor-dev.com`（プロトコルなし、サブドメインなし、末尾スラッシュなし）

サブドメイン `paper-search.eleanor-dev.com` は審査通過後に自動カバーされる。

---

## Step 3: サイト所有権の確認

サイト登録後、「サイトの所有権を確認してください」画面が表示される。
3つの確認方法が提示されるが、**「メタタグ」を選択すること。**

| 方法 | 可否 | 理由 |
|------|------|------|
| AdSense コード スニペット | ❌ 不可 | Cookie同意後のみスクリプト出力のため、Googleクローラーが検出できない |
| ads.txt スニペット | △ 条件次第 | ルートドメイン `eleanor-dev.com/ads.txt` が解決できる場合のみ有効 |
| **メタタグ** | ✅ **推奨** | SSRで常に出力されるため、クローラーが確実に検出できる |

### メタタグ選択後の手順

1. 「メタタグ」ラジオボタンを選択
2. AdSenseが表示するメタタグの内容を確認（`ca-pub-6133561595210589` が含まれるはず）
3. 「コードを配置しました」チェックボックスをオン
4. 「確認」ボタンをクリック

Vercelへの環境変数設定とRedeployが完了していれば、Googleクローラーがメタタグを検出して確認完了になる。

---

## Step 4: 審査リクエスト

所有権確認後、「審査をリクエスト」セクションが有効になる。
リクエストを送信すると審査開始（通常 1〜14 日）。

---

## Step 5: 審査通過後の広告設定

1. AdSense → 「広告」→「サマリー」→ サイトを選択
2. 自動広告をオン → 保存

自動広告は AdSense が最適な位置に自動配置する。追加のコード変更は不要。

---

## トラブルシューティング

### メタタグ確認が通らない

```bash
# デプロイ後にメタタグが出力されているか確認
curl https://paper-search.eleanor-dev.com | grep google-adsense-account
```

出力例（正常）:
```html
<meta name="google-adsense-account" content="ca-pub-6133561595210589"/>
```

content が空または出力されない → Vercel の環境変数 `NEXT_PUBLIC_ADSENSE_CLIENT_ID` を確認・Redeploy。

### CSP エラーで広告が表示されない（審査通過後）

ブラウザ DevTools → Console に以下が出る場合:
```
Refused to load script from 'https://pagead2.googlesyndication.com/...'
```

→ `src/middleware.ts` の CSP に AdSense ドメインが含まれているか確認。
現在の実装では `script-src` に `https://pagead2.googlesyndication.com` が含まれている。

---

## 関連ファイル

| ファイル | 役割 |
|----------|------|
| `public/ads.txt` | AdSense 認定ファイル |
| `src/components/ads/AdSenseScript.tsx` | AdSense スクリプト（Cookie同意後のみ出力） |
| `src/app/layout.tsx` | `google-adsense-account` メタタグ・nonce受け渡し |
| `src/middleware.ts` | nonce生成・CSP設定（AdSenseドメイン許可含む） |
| `.env.example` | 環境変数テンプレート |
