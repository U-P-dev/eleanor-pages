# CLAUDE.md — eleanor-dev.com（エレノアのホームページ）

> **制約：このファイルは常に100行未満を維持すること。**
> 🔴 **このリポジトリは公開**（`U-P-dev/eleanor-pages`）。運用情報・秘密・事業の方針の理由は書かない。

## 運用・インフラ・設定情報の在処

- 配信先・DNS・切り戻し手順・HP の方針: 非公開の `eleanor-ops/docs/infra/eleanor-website.md`
- 公開前に回す非公開の検査: `python3 /mnt/c/Projects/eleanor-ops/bin/check_eleanor_site.py`
- 見た目の正本: `DESIGN.md`（色・文字・格子・部品・中身の並び・DADS から外した点。決まりは出典の ID つき）
- ベストプラクティスとの突き合わせ: `docs/best-practice-audit.md`（済・一部・待ち・対象外の一覧）

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
SHOW_DRAFTS=1 STAGING=1 npm run build  # 確認用（下書き記事を含め、全ページを検索に出さない）。🔴 push の前にこれも回す
python3 scripts/check_legal_text.py  # 移したページ 9 枚の本文が旧サイトと一字も違わないか
python3 scripts/check_prices.py      # 料金の元データが正本とずれていないか（正本が隣に無ければ省略）
python3 tools/preview/serve.py       # dist/ を http://localhost:4321/ で配る（/mnt/c では astro preview が起動しない）
HEADING_FONT=off npm run build       # 見出しの書体を取りに行かずに組む（取れないときの見え方を確かめる）
node tools/preview/icons.mjs         # ロゴの印（public/favicon.svg）からアイコン一式を書き出す
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\preview\shoot.ps1 -Url <URL> -Out <Windows のパス> -Width 390 -Height 844 -Mobile
                                     # 画面を撮る（Windows の Chrome。幅 500px 未満は -Mobile で端末を真似る）
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\preview\evaluate.ps1 -Url http://localhost:4321/__preview/a11y.html -Expr "runAll().then(r => JSON.stringify(r))" -Out <Windows のパス>
                                     # アクセシビリティの自己試験（裏で動く Chrome。拡張が無くても回る）。
                                     # -ReducedMotion・-ForcedColors・-Print で OS の設定や印刷を真似る（shoot.ps1 も同じ）
```

## どこに何があるか

| 場所 | 中身 |
|---|---|
| `src/pages/*.astro` | 1 ファイル＝1 ページ（`index`・`services`・`products`・`company`・`contact`・`contact-thanks`・`blog`・`site-policy`・`404`） |
| `src/pages/<アプリ用>.astro` ＋ `src/legal/*.html` | 旧サイトから移したアプリのサポート・規約と決済の完了・取消。本文は `src/legal/` をそのまま差し込む |
| `content/blog/*.md` | ブログ記事（書き方は `content/blog/README.md`）。公開前は `draft: true` |
| `src/components/` | 料金表・問い合わせフォーム・パンくず・仕組みの図 |
| `src/styles/` | `tokens.css`（値・MIT 表示）と `global.css`（見た目） |
| `src/site.mjs` | サイトの定数（事業者・電話の受付時間・対応地域・運営しているもの・問い合わせの受け口）とヘッダーのメニュー |
| `src/data/` | `prices.json`（料金・自動で写す）・`faq.mjs`（よくある質問）・`updated.json`（最終更新日）・`news.json`（お知らせと沿革）・`samples.mjs`（LP の見本）・`tiers.mjs`（デザインの段） |
| `src/lib/jsonld.mjs` | 構造化データ（`@id` でつないだ 1 つの `@graph`。組み立ては `layouts/Base.astro`） |
| `src/assets/` | 実物の画面（`shots/`）・LP の見本の画面（`samples/`）・記事の図（`blog/`）・代表の写真（`person/`・撮影データを消してから置く） |
| `public/` | そのまま配るもの（`ads.txt`・Search Console の確認ファイル・`.well-known/security.txt`・アイコン） |
| `scripts/` | 検査とビルドの補助 |

## するとき

- **ページを足す** → `src/pages/<名前>.astro` → メニューに載せるなら `src/site.mjs` の `NAV` → フッター（`layouts/Base.astro`）
- **記事を公開する** → 代表の OK を取ってから `draft` を外す（完全自動化はしない）
- **公開する（push）前** → `npm run build` と上の非公開の検査が両方とも合格。`hp-redesign` への push は確認用サイトに自動で出る
- **見た目を変える** → 先に `DESIGN.md`（「白と明朝」。出典の無い決まりは足さない）。段に無い文字の大きさ・角丸・画面以外の影・
  表の縦罫・グラデーション・見出しの上の英字・紫の飾り・看板とメニュー以外の動き・「動きを減らす」の外の動きはビルドが止める。
  直したら `a11y.html` の `runAll()`・`heroFit()`・`motionCheck()`（`-ReducedMotion` の有無で 2 回）を回す
- **お知らせを足す** → `src/data/news.json`（確かめられる事実と日付だけ）
- **LP の見本を撮り直す・足す** → `DESIGN.md` §9（承認済みのテンプレートだけ・架空の店と書く）
- **電話の受付時間を変える** → `src/site.mjs` の `operator.hours` と LP 事業の `config.json` の `support_hours`（特商法の表示を作り直す）
- **移したページの本文を直す** → アプリストアの掲載情報と食い違わないか先に確かめる。直したら `check_legal_text.py` の基準も更新する
