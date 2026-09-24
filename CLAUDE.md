# CLAUDE.md — eleanor-dev.com（エレノアのホームページ）

> **制約：このファイルは常に100行未満を維持すること。**
> 🔴 **このリポジトリは公開**（`U-P-dev/eleanor-pages`）。運用情報・秘密・事業の方針の理由は書かない。

## 運用・インフラ・設定情報の在処

- 配信先・DNS・切り戻し手順・HP の方針: 非公開の `eleanor-ops/docs/infra/eleanor-website.md`
- 公開前に回す非公開の検査: `python3 /mnt/c/Projects/eleanor-ops/bin/check_eleanor_site.py`
- 見た目の正本: `DESIGN.md`（色・文字・部品・DADS から外した点）

## 触る前に

- **Astro 7 の静的サイト**（Node 22・npm）。`src/` と `public/` から `dist/` をつくる。直下の `.html` は下の 3 枚だけ
- 🔴 **直下の `tokusho.html`・`privacy-lp.html`・`terms-lp.html` は LP 事業（jido-lp-sales）が GitHub API で書き込む自動生成物**。
  手で編集・移動・削除しない。ビルドが `dist/` へ写す（`scripts/copy_generated.mjs`）。見た目を変えるなら向こうのスクリプトを直す
- 🔴 **URL の形を変えない**（`/company.html` の形）。決済の遷移先・アプリストア・配布済みアプリ・Search Console が直接参照している。
  守る一覧は `scripts/check_site.py` の `PROTECTED`
- 料金を `.astro` に直書きしない。`src/data/prices.json`（`scripts/check_prices.py --write` で正本から抜き出す）を読む

## コマンド

```bash
npm run build                        # astro build → 自動生成 3 枚を写す → 出力の検査（FAIL があれば exit 1）
SHOW_DRAFTS=1 STAGING=1 npm run build  # 確認用（下書き記事を含め、全ページを検索に出さない）
python3 scripts/check_legal_text.py  # 移したページ 9 枚の本文が旧サイトと一字も違わないか
python3 scripts/check_prices.py      # 料金の元データが正本とずれていないか（正本が隣に無ければ省略）
python3 tools/preview/serve.py       # dist/ を http://localhost:4321/ で配る（/mnt/c では astro preview が起動しない）
```

## どこに何があるか

| 場所 | 中身 |
|---|---|
| `src/pages/*.astro` | 1 ファイル＝1 ページ（`index`・`services`・`products`・`company`・`blog`・`site-policy`・`404`） |
| `src/pages/<アプリ用>.astro` ＋ `src/legal/*.html` | 旧サイトから移したアプリのサポート・規約と決済の完了・取消。本文は `src/legal/` をそのまま差し込む |
| `content/blog/*.md` | ブログ記事（書き方は `content/blog/README.md`）。公開前は `draft: true` |
| `src/components/` | 料金表・問い合わせフォーム・パンくず・仕組みの図 |
| `src/styles/` | `tokens.css`（値・MIT 表示）と `global.css`（見た目） |
| `src/site.mjs` | サイトの定数とヘッダーのメニュー |
| `public/` | そのまま配るもの（`ads.txt`・Search Console の確認ファイル・`.well-known/security.txt`・アイコン） |
| `scripts/` | 検査とビルドの補助 |

## するとき

- **ページを足す** → `src/pages/<名前>.astro` → メニューに載せるなら `src/site.mjs` の `NAV` → フッター（`layouts/Base.astro`）
- **記事を公開する** → 代表の OK を取ってから `draft` を外す（完全自動化はしない）
- **公開する（push）前** → `npm run build` と上の非公開の検査が両方とも合格
- **移したページの本文を直す** → アプリストアの掲載情報と食い違わないか先に確かめる。直したら `check_legal_text.py` の基準も更新する
