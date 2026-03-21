# Eleanor デザイン & 開発ガイドライン

> **対象**: eleanor-pages（コーポレートサイト）の開発・保守担当者
> **最終更新**: 2026-03-21

---

## 1. ブランド概要

| 項目 | 内容 |
|------|------|
| 屋号 | エレノア（Eleanor） |
| コンセプト | プロダクトスタジオ & AI アジャイル開発 |
| ターゲット | 小規模企業・スタートアップ |
| ポジショニング | 圧倒的な低価格・高速開発（≠ SI の上位互換） |

---

## 2. コーポレートカラー

### プライマリ（トライカラー）

| 変数 | HEX | 用途 |
|------|-----|------|
| `--blue` | `#2563EB` | プライマリアクション、リンク |
| `--purple` | `#7C3AED` | ブランドコア、グロー |
| `--red` | `#E11D48` | アクセント、CTA |

### ライト（テキスト・グラデーション用）

| 変数 | HEX | 用途 |
|------|------|------|
| `--blue-l` | `#93C5FD` | グラデーションテキスト |
| `--purple-l` | `#C4B5FD` | グラデーションテキスト |
| `--red-l` | `#FDA4AF` | グラデーションテキスト |

### バックグラウンド

| 変数 | HEX | 用途 |
|------|------|------|
| `--bg` | `#04040E` | ページ背景（最暗） |
| `--bg2` | `#07071A` | セクション背景 |
| `--bg3` | `#0A0A22` | カード背景 |

### テキスト（コントラスト設計）

| 変数 | 値 | 用途 | 目標コントラスト |
|------|----|------|----------------|
| `--text` | `#FFFFFF` | 見出し | AA/AAA |
| `--body` | `rgba(255,255,255,0.84)` | 本文 | AA |
| `--muted` | `rgba(255,255,255,0.60)` | 補助テキスト | 最低限 |
| `--muted2` | `rgba(255,255,255,0.38)` | プレースホルダ等 | 装飾用のみ |

### ボーダー

| 変数 | 値 | 用途 |
|------|----|------|
| `--border` | `rgba(255,255,255,0.09)` | 通常の区切り |
| `--border2` | `rgba(255,255,255,0.15)` | ホバー時・強調 |

---

## 3. シグネチャグラデーション

```css
/* ボタン・バー・アイコン等に使うメイングラデーション */
--grad: linear-gradient(135deg, #2563EB 0%, #7C3AED 50%, #E11D48 100%);

/* テキストに使うパステルグラデーション（視認性確保） */
--grad-text: linear-gradient(125deg, #93C5FD 0%, #C4B5FD 48%, #FDA4AF 100%);

/* カード背景・ホバー等の微細なグラデーション */
--grad-subtle: linear-gradient(135deg,
  rgba(37,99,235,.18) 0%,
  rgba(124,58,237,.14) 50%,
  rgba(225,29,72,.12) 100%);
```

### グラデーションテキストの適用方法

```css
.gradient-text {
  background: var(--grad-text);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
```

---

## 4. タイポグラフィ

| 用途 | フォント | ウェイト |
|------|---------|---------|
| 全文 | Inter（Google Fonts） | 300〜900 |
| フォールバック | -apple-system, BlinkMacSystemFont, Hiragino Sans, Yu Gothic, sans-serif |
| 見出し H1 | 56–64px | 900 |
| 見出し H2 | 38–42px | 800 |
| 見出し H3 | 20–24px | 700 |
| 本文 | 16–17px | 400–500 |
| 小テキスト | 13–14px | 400–500 |
| letter-spacing | 見出し: -0.03〜-0.05em、本文: 0 |

---

## 5. コンポーネント設計

### トップアクセントバー

```html
<div class="top-bar"></div>
```
- 高さ: 3px、幅: 100%
- 背景: `var(--grad)`
- position: fixed, z-index: 300

### ナビゲーション

- height: 60px、top: 3px（アクセントバー分）
- 背景: `rgba(4,4,14,0.82)` + backdrop-filter: blur(28px) saturate(160%)
- ロゴ: 白テキスト + 「Eleanor」部分に `--grad-text`
- CTA ボタン: `--grad` 背景、shadow: `0 0 24px rgba(124,58,237,.45)`

### カード

- 背景: `var(--bg3)` または `var(--grad-subtle)`
- border: `1px solid var(--border)`
- border-radius: 14–16px（コーポレート感のある丸み）
- hover: border-color → `var(--border2)` + translateY(-4px)

### ボタン（プライマリ）

```css
background: var(--grad);
color: #fff;
border-radius: 8px;
font-weight: 700;
box-shadow: 0 0 24px rgba(124,58,237,.45);
```

---

## 6. アニメーション

### スクロールアニメーション

- `[data-a]` 属性を持つ要素が Intersection Observer で `.visible` クラスを受け取る
- デフォルト: `opacity: 0; transform: translateY(28px)`
- `.visible`: `opacity: 1; transform: none; transition: 0.6s cubic-bezier(.22,1,.36,1)`
- 遅延: `[data-d="1"]` → `transition-delay: 0.1s`（数字 × 0.1s）

### ホバー

- ボタン: `translateY(-1px)` + shadow 強調
- カード: `translateY(-4px)` + border-color 変化
- transition: 0.15〜0.25s ease

---

## 7. レスポンシブ

| ブレークポイント | 対象 |
|----------------|------|
| `max-width: 960px` | ナビ折りたたみ（ハンバーガー） |
| `max-width: 768px` | カードグリッド 1列化、パディング縮小 |
| `max-width: 480px` | H1 フォントサイズ縮小 |

---

## 8. 開発方針

### 技術スタック

- **静的HTML + CSS + Vanilla JS**（ビルドツール不使用）
- **ホスティング**: GitHub Pages（`U-P-dev/eleanor-pages`）
- **ドメイン**: `eleanor-dev.com`（Cloudflare DNS → GitHub Pages）
- **フォント**: Google Fonts CDN（Inter）

### コーディングルール

1. CSSカスタムプロパティ（変数）を必ず使用し、ハードコードの色値を避ける
2. テキストコントラストは WCAG AA 基準（4.5:1 以上）を維持すること
3. `rgba(255,255,255,0.42)` 以下のテキストは本文に使用しない
4. JavaScript は最小限。アニメーションは CSS + Intersection Observer のみ
5. 外部依存はフォントのみ（CDN 1本）

### デザイン原則

- **Accenture Song スタイル**: 鮮烈なトライカラーグラデーション、モノクロ暗背景
- **情報の誠実さ**: 誇大表現を避け、強み・弱みを正直に提示する
- **コントラスト優先**: 見た目の美しさよりも可読性を優先する

### デプロイフロー

```bash
# 変更後
git add <files>
git commit -m "description"
git push origin main

# デプロイ確認（SHA が一致すれば完了）
gh api repos/U-P-dev/eleanor-pages/deployments --jq '.[0] | {sha, created_at}'
```

---

## 9. ページ構成

| ファイル | URL | 内容 |
|---------|-----|------|
| `index.html` | `/` | トップ（事業者HP） |
| `company.html` | `/company.html` | 会社情報 |
| `privacy.html` | `/privacy.html` | プライバシーポリシー |
| `support.html` | `/support.html` | サポート |
| `account-deletion.html` | `/account-deletion.html` | アカウント削除 |

---

## 10. 注意事項

- Cloudflare の Proxy（オレンジ雲）は **OFF** にすること（HTTPS証明書が競合する）
- `CNAME` ファイルは削除しないこと（GitHub Pages のカスタムドメイン設定）
- `PROGRESS.md` は事業進捗の記録。コミット対象だが公開ページではない
