# デザインの正本 — eleanor-dev.com

> **最終更新**: 2026-09-24（「AI が作ったように見える型」を出典つきで調べて外した日）
> 見た目・部品を変えるときは、ここを先に読む。変えたらここを直す。
> 値の正本は `src/styles/tokens.css`、見た目は `src/styles/global.css`、部品は `src/components/`。

---

## 1. 方針（4つ）

1. **デジタル庁デザインシステム（DADS）の値と部品の作り方に沿う。**
   参照した版: デザイントークン npm 2.0.1（2026-05-28）／HTML コードスニペット v20260909／ドキュメント v2.18.0（2026-09-09）。
   トークンとコードは MIT。流用部分の著作権表示を `tokens.css` の先頭に残している。
   サイト上の表記は「デジタル庁デザインシステムを参考に作成」まで（「準拠」「公式」とは書かない）。デジタル庁のロゴは使わない。
2. **生成 AI が作ったページによくある型を使わない。** 次の型は、出典で「AI っぽさの目印」として挙がっている。
   出力に入ると `scripts/check_site.py` が公開を止める（§6）。
   - 紫から青へのグラデーションで面を塗る（最も多く挙がる目印。925 Studios 2026・Anthropic の frontend-design・Qiita 2026）
   - すべての見出しの上に、字間を広げた英字の小見出しを置く（Anthropic の frontend-design）
   - 同じ大きさ・同じ角丸のカードを並べ、全部の節を同じ重さ・同じ余白で続ける（Qiita・サロンシード 2026）
   - 実物（画面・写真・数字）を見せずに主張だけを書く（NN/g・Stanford の信頼性の指針・Utsubo 2026）
   - 三つ並べ・「〜ではなく」の対句・ダッシュの多い文章（Wikipedia「Signs of AI writing」）
   - 別の流行りの型へ乗り換えること（生成り色＋明朝＋テラコッタ、黒地＋蛍光色、新聞風の太い罫）も同じく避ける
3. **ブランドの紫は「押すところ」と「今いる場所」と「ロゴ」だけ。** バイオレット `#7c3aed` は Tailwind CSS の既定色（violet-600）と
   同じ値なので、面に広げると既定のままの見た目になる。「赤と青が混ざって紫」はロゴの印だけで表す。
4. **JIS X 8341-3:2016 の適合レベル AA を目標にする。** 方針と試験結果は `/site-policy.html`。

## 2. 色（正本は `src/styles/tokens.css`・組み合わせは `scripts/check_site.py` の `CONTRAST` が毎回計算）

| 用途 | 値 | 備考 |
|---|---|---|
| 本文／見出し | Gray-800 `#333` ／ Gray-900 `#1a1a1a` | |
| リード文・注記・画面の説明／日付・補足 | Gray-700 `#4d4d4d` ／ Gray-600 `#666` | |
| ブランド（塗りのボタン・メニューの今いるページの下線） | Violet `#7c3aed` | 白い文字との比 5.70。ホバー Purple-900・押下 Purple-1000 |
| ロゴの印 | 赤 `#d7263d`・青 `#1f4fd1`・重なり Violet | ロゴだけに使う。文字には使わない |
| アウトラインのボタン・時系列の印・手順の番号 | Gray-900（墨） | 紫を飾りに増やさない |
| 灰の地（お問い合わせ・フッターだけ） | Gray-50 `#f2f2f2` | 節ごとに地の色を交互に変えない |
| 罫線・枠・画面の枠（白の地） | Gray-420 `#949494` | 3.03 |
| 罫線・枠（灰の地） | Gray-536 `#767676` | Gray-420 では 3:1 に届かない（2.7）ので地ごとに変数を上書き |
| リンク／ホバー／訪問済み／押下 | Blue-1000 ／ Blue-900 ／ Magenta-900 ／ Orange-800 | DADS 標準 |
| 「※必須」・エラー | Error-2 `#ce0000` | |
| フォーカス | Yellow-300 `#ffd43d` と黒の二重 | DADS は変更を禁止 |

- **文字は大きさに関係なく 4.5:1 以上**（DADS は大きい文字の 3:1 の例外を使わない）。
- **グラデーションは使わない。** 例外は表の横スクロールを知らせる端の影だけ（機能で、飾りではない）。
- **ダークモードは作らない**（DADS に定義が無く、フォーカス表示もライト前提）。`color-scheme: light`。

## 3. 文字と配置

- **書体**: 本文は OS の和文フォント（`'Noto Sans JP'` → ヒラギノ → BIZ UDPGothic → メイリオ）。
  **見出しとロゴだけ Zen Kaku Gothic New 700**（SIL OFL 1.1・`public/fonts/OFL.txt`）。OS の書体だけでは、Windows 11 の既定
  （Noto Sans JP）と同じ顔になるため。使っている字だけを Google Fonts から切り出し、このサイトから配る（`scripts/headings.mjs`。
  外部送信なし。約 350 字・約 40KB）。取れなければ見出しは本文と同じ書体で出る。
- **組み方**: 本文も見出しもベタ組み（見出しの書体に字詰めの情報が無い）。看板の約物だけ `.kern-open`／`.kern-close` で手で詰める。
  見出しは文節の区切りに `<wbr>`（`scripts/headings.mjs`）＋ `word-break: keep-all`。iPhone の Safari は `auto-phrase` が効かないため。
  本文は `line-break: strict`。ソースで文の途中で改行しない（HTML で空白になる。検査が止める）。
- **大きさ**: 本文 16px（768px 以上は 17px）・行の高さ 1.7（記事は 1.8）・字間 0.02em。
  H1 28/36px、H2 26/32px（従の節は 22/24px）、H3 19/20px（768px 未満／以上）。
  看板は 2 行（「「つくって終わり」。」／「に、しない。」）で、行が途中で折れないよう `white-space: nowrap` と画面幅に比例する大きさ。
- **角丸は 3 段だけ**: 0（節・表・画像・囲み）／4px（文中のコード・フォーカスの輪）／8px（ボタン・入力欄）。丸い札は作らない。
- **余白**: 主の節（看板・頼めること・つくったもの・お問い合わせ）は広く、従の節は狭くして上の罫だけで区切る。リード文は主の節だけ。
- **幅**: ページの最大幅 72rem、文章の幅 43rem（17px で約 40 字）。
- **段組みの切り替え**: 48rem（768px）の 1 本。ヘッダーの水平メニューだけは 5 項目＋問い合わせが収まる 60rem から出す。

## 4. 部品

| 部品 | 置き場 | DADS の部品 | 約束 |
|---|---|---|---|
| ロゴの印 | `components/LogoMark.astro` | — | 赤と青の四角が重なり、重なりが紫。`public/favicon.svg` と `tools/preview/icons.mjs` のアイコン類は同じ形 |
| ヘッダー | `layouts/Base.astro` | ヘッダーコンテナ・水平メニュー・ハンバーガーメニューボタン | メニューはページ名そのままの 5 つ。狭い画面は「メニュー」と書いたボタン。階層は 1 段 |
| パンくず | `components/Breadcrumb.astro` | パンくずナビゲーション | H1 の上。`aria-current` |
| ボタン | `global.css` `.button` | ボタン | **塗り（primary・紫）は 1 画面に 1 つ**。もう一つの行き先は文中リンク（`.button-row__link`）かアウトライン（墨） |
| 看板 | `pages/index.astro` `.hero` | — | 白地。H1 に「何の店か」を含める。右に実物の画面（撮影日つき） |
| 頼めること | `.offer` | — | 主力の LP を大きく、残りを右に小さく。同じ形のカードを並べない |
| 時系列 | `.timeline` | —（番号付きリスト） | `<ol>` を使わず番号を文字で書く。日数は料金データから |
| 事例 | `.work`・`.facts` | 説明リスト | 画面・公開日・担当・技術。載せるのは動いているものだけ |
| 実物の画面 | `.shot`・`.hero__shots` | — | 1px の枠だけ（影・傾き・偽のブラウザ枠は付けない）。キャプションに何の画面か・出どころ・撮影日 |
| 代表の紹介 | `components/Person.astro` | — | 写真は `src/assets/person/` に 1 枚（撮影データを消してから）。無ければ文章だけ |
| 料金表 | `components/PriceTables.astro` | テーブル | 横スクロールの枠に名前と `tabindex="0"`。金額は右寄せ |
| よくある質問 | `.qa`（`src/data/faq.mjs`） | — | **答えを折りたたまない**（検索と AI の回答に拾われるように）。画面と構造化データを同じデータから作る |
| ページの終わり | `.page-end` | — | 罫で区切った一言とボタン 1 つ。帯で塗らない |
| 問い合わせ | `components/ContactForm.astro` | インプットテキスト・ラベル | ラベルは上・「※必須」「※任意」・プレースホルダーは使わない |
| 仕組みの図 | `components/Flow.astro` | — | 画像にせず HTML のリストで描く |
| 移したページ | `layouts/Legal.astro` | — | 旧サイトの本文（`src/legal/*.html`）をそのまま差し込む（意図して直した箇所は `check_legal_text.py` の `INTENDED`） |

使わないと決めたもの: グラデーションの面、見出しの上の英字の小見出し、同じ形のカードの並び、紫の飾り（上帯・下線・左の帯・薄紫の地）、
丸い札、飾りの影、カルーセル、ページトップへ戻るボタン、文字サイズ変更ボタン、ダークモード、装飾だけのアニメーション。

## 5. DADS から意図して外した点

| 点 | DADS | このサイト | 理由 |
|---|---|---|---|
| キーカラー | Blue | Violet（使う場所を 3 か所に限る） | §1-3 |
| 見出しの書体 | Noto Sans JP | Zen Kaku Gothic New | §3。OS の既定と同じ顔にしない |
| よくある質問 | アコーディオン | 開いたまま | 答えを検索と AI の回答に拾わせる（Microsoft の案内） |
| ヘッダーのメニューの出し方 | 768px で切り替え | 60rem（960px）で切り替え | 5 項目＋問い合わせが 768px では収まらない |
| ロゴのリンク | リンクは下線 | 下線なし | 位置と慣習で分かる |
| 移したページの `<ol>`・表 | 番号は文字で／表は名前つきの枠 | 旧サイトのまま | 本文を変えない約束が優先 |

## 6. 機械で止まるもの（`npm run build`）

- `scripts/copy_generated.mjs`: LP 事業が直下に書き込む 3 枚が無い
- `scripts/headings.mjs`: 止めない（見出しの書体が取れなければ WARN）
- `scripts/check_site.py`:
  - 守る URL・`#lp` `#contact` `#apps`・リンク切れ・H1 の数・名前の無い `<nav>`・表の枠・`<ol>`・外部送信の表・色のコントラスト比
  - **型の再発**: グラデーション・やめたクラス・見出しの上の英字・3 段以外の角丸・飾りの影・0.08em を超える字間・大文字変換・
    3 か所以外の紫・本文のダッシュ・句読点のあとの空白（「〜ではなく」と三つ並べは WARN）
  - **SEO と AIO**: 構造化データ（JSON・`@id` のつながり・電話の +81・日時の +09:00・FAQ と画面の一致・トップの WebSite・ロゴ）、
    title と description の重複、title の書き方、画像の alt と幅と高さ、`llms.txt`・`favicon.ico`・`logo.png`、robots.txt、lastmod
  - **持ち込み**: 出力と追跡中のファイルに、サブドメインのホスト名や IP アドレスがない
- ビルドの外で回すもの: `scripts/check_legal_text.py`（移したページの本文）・`scripts/check_prices.py`（料金の元データ）・非公開の検査

## 7. 変えるとき

- **色を変える** → `tokens.css` → `npm run build`（`CONTRAST` が落ちたら値を戻す）→ この §2
- **ロゴの形を変える** → `LogoMark.astro` と `public/favicon.svg` → `node tools/preview/icons.mjs` → OGP（`tools/preview/og.html?auto=1`）
- **部品を足す** → `src/components/` → `global.css` → この §4
- **ページを足す** → `src/pages/<名前>.astro` → `NAV` → フッター → `src/data/updated.json` に最終更新日
- **中身を変えた** → `src/data/updated.json` の日付（見た目だけの変更では変えない）
- **料金が変わった** → `python3 scripts/check_prices.py --write` → 差分を見てコミット（金額を `.astro` に直書きしない）
- **画面を撮り直す** → `tools/preview/shoot.ps1`（スマートフォンの幅は `-Mobile`）→ `src/assets/shots/` → `WORKS.*.shotAt`
- **見た目を変えた** → アクセシビリティの再試験（`/site-policy.html` の試験結果を更新）

## 8. 出典

- デジタル庁デザインシステム: https://design.digital.go.jp/dads/
- 利用上の注意（ライセンス）: https://design.digital.go.jp/dads/introduction/notices/
- Anthropic「Improving frontend design through skills」: https://claude.com/blog/improving-frontend-design-through-skills
- Anthropic `frontend-design` スキル: https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md
- 925 Studios（AI っぽさの目印）: https://www.925studios.co/blog/ai-slop-design-tells
- Qiita（AI っぽいデザインの特徴）: https://qiita.com/kenimo49/items/8aaa2bf0d25c704637ae
- NN/g（人の写真）: https://www.nngroup.com/articles/photos-as-web-content/
- W3C JLREQ（日本語組版処理の要件）: https://www.w3.org/TR/jlreq/
- Wikipedia「Signs of AI writing」: https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing
