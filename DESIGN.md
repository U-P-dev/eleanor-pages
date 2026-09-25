# デザインの正本 — eleanor-dev.com

> **最終更新**: 2026-09-25（「白と明朝」へ作り替えた日。突き合わせの全項目は `docs/best-practice-audit.md`）
> 見た目・部品・中身の並びを変えるときは、ここを先に読む。変えたらここを直す。
> 値の正本は `src/styles/tokens.css`、見た目は `src/styles/global.css`、部品は `src/components/`。
> 決まりの行の末尾の `[ID]` は §10 の出典。**出典の無い決まりは足さない**（好みで変えない）。

---

## 1. 方針（5つ）

1. **白と明朝**（2026-09-25 👤）：明るい地、明朝の見出し（標準の太さ）、実物の画面を大きく。罫と表を減らし、余白で区切る。
   - 行政向けの型（DADS の見た目）は「制作スタジオらしさ」を下げるのでやめた [TUCH12][DADS]。
   - 制作会社の自社サイトは「腕前の見本」として読まれる [SIGNAL][FOGG02][BAIGIE13]。
2. **大胆に見せるのは看板の 1 か所だけ** [ANTH][KLUGE13][BAIGIE-CL]。
   - 実物の LP の画面を窓の右端で裁ち落とし、スマートフォンの画面を手前に重ねる。
   - ほかは格子の中に静かに収める（画面の複雑さを低く保つ [REIN13][TUCH12]）。
3. **実物・数字・連絡先を先に見せる** [NNG-HOME][STAN][BAIGIE]。
   - 価格には、すぐ隣に条件を書く [CAA-UCHIKESHI]。
4. **生成 AI の既定の型を使わない** [ANTH][925]。
   - 使わないもの：色味のある黒、生成り＋明朝＋テラコッタ、同じ角丸と影のカード、英字の小見出し、「01 02 03」、リンクの「→」、節ごとのふわっとした登場、ピル型のボタン。
5. **WCAG 2.2 AA と JIS X 8341-3:2016 の AA を守る** [MIC-GL]。
   - 見た目を変えても、文字の濃さ・押せる大きさ・キーボード操作・フォーカスは下げない。方針と試験結果は `/site-policy.html`。

## 2. 色（正本は `tokens.css`・組み合わせは `scripts/check_site.py` の `CONTRAST` が毎回計算）

色味のない灰と墨に、差し色は紫の 1 色だけ。地と白が約 70%、墨が約 25%、紫は 5% 以下 [LIG22][LIG16]。

| 名前 | 値 | 用途 | 比（地／白） |
|---|---|---|---|
| 地 `--color-ground` | `#f4f4f4` | ページ全体（ヘッダー・フッターも） | ― |
| 面 `--color-surface` | `#ffffff` | お問い合わせの面・入力欄 | ― |
| 墨 `--color-ink` | `#2b2b2b` | 本文・見出し・線のボタン・フォーカスの輪 | 12.87／14.16 |
| 薄墨 `--color-ink-2` | `#5c5c5c` | 補足・日付・画面の説明 | 6.08／6.69 |
| 線 `--color-line` | `#767676` | 入力欄の枠・表の見出し行の罫・訪問済みのリンクの下線 | 4.13／4.54 |
| 細罫 `--color-hairline` | `#d9d9d9` | 表・説明リストの行の間だけ（飾り。意味を持たせない） | ― |
| 紫 `--color-brand` | `#7b3a87`（ホバー `#622e6c`・押下 `#4a2351`） | 塗りのボタン・今いるページ・ホバーの下線・ロゴの重なり | 6.83／7.51 |
| エラー `--color-error` | `#c01f33` | 「※必須」・エラー | 5.48／6.03 |
| ロゴの赤・青 | `#d7263d`・`#1f4fd1` | ロゴの印だけ（文字には使わない） | ― |

- 文字は大きさに関係なく 4.5:1 以上。部品の境界（入力欄の枠など）は 3:1 以上 [WCAG-1411]。
- 紫は文字の色に使わない。ホバーは色だけで示さず、下線の太さも変える（紫と墨の比は 1.89）[WCAG-141]。
- 使わないもの：グラデーション、ダークモード、色味のある黒（`#111` のような）[ANTH]。

## 3. 文字

**書体**
- **見出し**：Noto Serif JP（源ノ明朝）の太さ 500 だけ（SIL OFL 1.1）[SD-LEE2017][SD-HIRA2005][LIG16][SURVEY18]。
  - 使っている字だけを切り出して、このサイトから配る（`scripts/headings.mjs`。外部送信なし）。
  - preload し、`font-display: optional` で使う（途中で書体を切り替えない）。取れなければ端末の明朝で出る。
- **本文**：ヒラギノ角ゴ、游ゴシック Medium（Windows。`local()` で `'Eleanor Gothic'` として指す）、メイリオ。
  - 通信なし。BIZ UDPゴシックと Noto Sans JP は並びから外した [LIG21]。
- 書体は 2 つだけ。太さは、明朝 500、ゴシック 400、600（フォームのラベル・エラー・`<strong>` だけ）[NNG-GOOD][BUTT][SD-LEE2017]。

**約物**
- この明朝には字詰めの palt が無い（実測）。見出しは書体の `chws` と `text-spacing-trim: space-all` で組む。
  - 約物が続くところ（」。など）を、どのブラウザでも同じに詰める。
  - `headings.mjs` が書体の chws と halt の有無を報告し、無ければビルドが止まる。
- 看板の標語の行頭の「だけは `halt` で半角にし、左の余白へぶら下げる（`.hang`）。

**大きさの段**（ほかの値は `check_site.py` が止める）[NNG-VIS][M3][JLREQ]

| 役割 | SP | PC | 行送り・字間 |
|---|---|---|---|
| 看板の標語 | `min(9.2vw, 3rem)` | `clamp(2.5rem, 4vw, 3.25rem)` | 1.35・.02em |
| H1（下層ページ） | 30 | 40 | 1.4・.04em |
| H2 | 26 | 32 | 1.5・.04em |
| H3・段の名・見せる価格 | 20 | 24 | 1.55・.04em |
| 本文・価格の条件・表 | 16 | 16 | 1.8・.05em |
| 小（画面の説明・日付・©・パンくず・ロゴの英字だけ） | 14 | 14 | 1.7・.05em |

- 大きい見出しは詰めて組んでよい。本文はベタ組み [JLREQ]。字間は 0〜.08em の範囲だけ（.08em はメニューとボタンの文字）[LIG24]。
- 1 行は 40 字まで（`--measure: 40ic`）[JLREQ][WCAG-148]。
- 価格の条件は 14px にしない。本文と同じ大きさで、価格のすぐ隣に置く [CAA-UCHIKESHI]。
- 行の中の数字だけを大きくしない [JLREQ]。
- 見出しは文節の区切りに `<wbr>`（`headings.mjs`）＋ `word-break: keep-all`。
- 本文は `line-break: strict` と `text-autospace: normal` [W3C-SPACE]。ソースで文の途中で改行しない。

## 4. 格子・余白・角・影・動き

- **格子**：12 列・列間 32px・最大幅 72rem。外側の余白は 24／40（48rem 以上）／64（64rem 以上）[M3][HIG-LAYOUT]。
- **余白の段**：4／8／16／24／32／48／64／96／128／160 [M3][RUI]。
  - 節と節の間：SP 96、PC 160。見本と見本の間：96／128。展示は間を広くとるほど格が上がる [SEV16][WSPACE]。
  - 見出しと本文の間は、段と段の間より狭くする [NNG-PROX]。
- **罫**：表と説明リストの行の間だけ（細罫）。節の区切りには引かない [RUI][REIN13]。
- **角**：0 の 1 種類だけ。ロゴの四角と形をそろえる。ラジオボタンだけは OS の円のまま [REFU26]。
- **影**：実物の画面にだけ。奥の PC の画面は `--shadow-screen`、手前の SP の画面は `--shadow-screen-front`。
  - どちらも 2 層で、1 層目は画面の縁取りの代わり [RUI][NNG-FLAT]。カードや文字には付けない。
- **動き**（2026-09-25 👤：看板と操作への反応だけ）[NNG-ANIM][M3-MOT][WEB-RM][ANTH]
  - 看板だけ、ページを開いたときに 1 回：
    - PC の画面が 0ms から入る（LCP の要素なので遅らせない）。
    - 標語の 2 行が 120・220ms から。SP の画面が 360ms から。残りの文字が 520ms から。
    - 全体で 960ms 以内。同じタブで 2 回目は動かさない（`sessionStorage`）。
  - 操作への反応：ホバーは 150ms。メニューは開くとき 300ms、閉じるとき 200ms。
  - 動きの指定は、すべて `@media (prefers-reduced-motion: no-preference)` の中に書く。
    - 「動きを減らす」の設定や JS が無いときは、最初から全部見える。
  - 付けないもの：スクロールで現れる動き、パララックス、カルーセル、繰り返す動き [NNG-PARA][WCAG-222]。

## 5. 部品

| 部品 | 置き場 | 約束 |
|---|---|---|
| ロゴ | `components/LogoMark.astro` | 赤と青の四角が重なり、重なりが紫。「エレノア」は明朝、「Eleanor」は小さく添える。`public/favicon.svg` とアイコン類は同じ形 |
| ヘッダー | `layouts/Base.astro` | 固定しない。メニューはゴシックで、ホバーで紫の 1px の下線、今いるページは紫の 2px の下線。右に「お問い合わせ」（線のボタン）[NNG-CONTACT][SURVEY18] |
| SP のメニュー | `layouts/Base.astro` | 「メニュー」の文字つきのボタン。開くと全画面の `<dialog>`。項目は明朝。下に電話・受付時間・メール |
| フッター | `layouts/Base.astro` | 明るい地のまま、余白で区切る。よくある質問・お問い合わせ・取引の条件・プライバシーポリシーへ [NNG-FAQ] |
| ボタン | `.button` | 角 0。**塗り（紫・高さ 56）は 1 ページに 1 つ**。置くのはお問い合わせの面・送信・下層ページの終わりだけ。ほかは線（墨・高さ 48。ヘッダーは 40） |
| 文中のリンク | `a` | 墨の字に 1px の下線。ホバーで下線を紫の 2px に。訪問済みは下線を線の色に。「→」は付けない |
| フォーカス | `:focus-visible` | 墨の 2px の輪を 2px 離して描く（地との比 12.87）[WCAG-2413] |
| 画面の組 | `components/ShotPair.astro` | PC と SP の画面を同じ縮尺で重ねる。端末の枠は描かない。遅延読み込みにするかは呼ぶ側が決める |
| 看板の見本 | `components/HeroSample.astro` | 主力の LP の見本。PC の画面は 6 列目から窓の右端まで。`fetchpriority="high"` は PC の画面だけ。どれも遅延読み込みにしない [WEBDEV-LAZY][WEB-LCP] |
| 見本の展示 | `components/SampleShelf.astro`（データ `src/data/samples.mjs`） | 画面は 1〜8 列、説明は 9〜12 列。左右を入れ替えない [NNG-ZIGZAG]。**架空の店であること・段・料金と条件・撮影日を必ず書く** [CAA-UCHIKESHI]。画像にホバーの動きを付けず、リンクにもしない |
| 料金表 | `components/PriceTables.astro` | LP の表だけ。段の名前と価格は明朝。行の間は細罫、縦の罫は引かない。表の下に納期の数え方と取引条件へのリンク |
| 時系列 | `components/Timeline.astro` | 予定表のように並べる。番号は文字で書く（`<ol>` を使わない）。値は料金データから |
| お知らせ・沿革 | `components/News.astro`（データ `src/data/news.json`） | 日付と一文。確かめられる事実だけ。未来の日付は書かない [JNET21][SURVEY-JP] |
| 代表の紹介 | `components/Person.astro` | 写真は `src/assets/person/` に 1 枚（撮影データを消してから）。無ければ文章だけ [NNG-PHOTO][BAIGIE-CL] |
| お問い合わせ | `components/ContactForm.astro`（`/contact.html`） | 送り先は LP 事業の受け口（`src/site.mjs` の `CONTACT`）。欄・エラー・送る前の利用目的・Turnstile の作りは変えない [DADS-FORM][NNG-ERR][PPC][GOVUK-ERR] |
| お問い合わせの面 | `.panel`（トップの `#contact` だけ） | 白い面に、そのページで唯一の塗りのボタン |
| よくある質問 | `.qa`（`src/data/faq.mjs`） | 答えを折りたたまない。画面と構造化データを同じデータから作る |
| 表 | `.table-region` | 横スクロールの枠に名前と `tabindex="0"`。金額は右寄せ。SP で積む表は `role` と `data-label` を持つ |

使わないと決めたもの：グラデーションの面、見出しの上の英字の小見出し、同じ形のカードの並び、紫の飾り、角丸、飾りの影、
カルーセル、ページトップへ戻るボタン、文字サイズ変更ボタン、ダークモード、スクロールで現れる動き、自分で描いた絵（SVG）。

## 6. 中身と構成

- **トップの並び** [NNG-HOME][BAIGIE][SURVEY15]：
  - 並び：看板 → LP の見本 → 頼めること → LP の料金 → ご依頼の流れ → つくったもの → つくる人 → お知らせ → お問い合わせの面。
  - `#samples` `#lp` `#contact` `#apps` は外から張られているので残す。
- **看板**：標語と事業内容の行（2026-09-25 👤：今のまま）、線のボタン 1 つ、見本の画面。
  - 最初の画面の文字は 100 字まで（実在 18 件の中央値は約 70 字）[SURVEY18][REIN13]。料金は条件と一緒に下の節で出す。
- **価格の横に条件** [CAA-UCHIKESHI][NNG-PRICE]：
  - 保守とあわせてのお申し込みであること。
  - 1 年間の合計の例。
  - 「最短」が何を指すか（お支払いの確認から、確認用の初稿まで）。
  - 営業日の定義（土日祝を除く平日）。
  - 事業者向けであること（税抜表示の前提）[MOF-TAX]。
- **サービスと料金**：冒頭に目次。LP の節を主役にする（見本・表・1 年間の合計・ちがい）。保守の内容は「＋」で箇条に分け、用語の説明を置く。
- **会社概要**：代表の紹介、事業者情報（受付時間・営業日・来訪しないこと・事業者向け・インボイスの状態）、これまでの歩み。
- **連絡先** [NNG-CONTACT][TOKUSHO-GUIDE]：電話の受付時間と返信の目安は、`src/site.mjs` の 1 か所から出す。特定商取引法に基づく表示と同じ時間にする。
- **書かないこと**：
  - 「コンサル」「DX」「AX」（プロフィールの「外資系コンサル」だけは 👤 が許可）、本業の社名。
  - 運用の情報（ホスト名・IP）、確かめていない数字。
  - お客様の声（まだ無い。載せるときはステマ規制に従う）。

## 7. DADS から引き継ぐもの・変えたもの

参照した版：デザイントークン npm 2.0.1（2026-05-28）／HTML コードスニペット v20260909。
トークンとコードの一部は MIT（表示は `tokens.css` の先頭）。サイト上の表記は「参考に作成」まで。

| 引き継ぐもの | 変えたもの（2026-09-25 👤「DADS の見た目はやめ、読みやすさの決まりだけ残す」） |
|---|---|
| フォームの作り（ラベルは上・「※必須」「※任意」・入力例は補足文に・プレースホルダーなし・エラーの要約）[DADS-FORM] | リンクの色（青・マゼンタ → 墨の下線） |
| 表の作り（名前つきの横スクロールの枠・見出しセル・縦の罫なし）[DADS-TABLE] | フォーカスの輪（黄と黒の二重 → 墨の 2px を 2px 離す。WCAG 2.4.13 の面積と比を満たす） |
| 押せる範囲 44px 以上・「メニュー」の文字つきのボタン | 文字の段（DADS の Std／Dsp → §3 の段）と見出しの書体 |
| 番号は文字で書く（`<ol>` を使わない。移したページだけは旧サイトのまま） | ボタンの角（8px → 0）、表の見出しセルの地（灰 → なし）、ヘッダーのメニューの切り替え幅（60rem） |
| コントラストの考え方（文字は大きさに関係なく 4.5:1） | 地の色（白 → `#f4f4f4`） |

## 8. 機械で止まるもの（`npm run build`）

- `scripts/headings.mjs`：止めない（書体が取れなければ WARN）。取れた書体に chws か halt が無ければ、`check_site.py` が止める。
- `scripts/check_site.py`：
  - 守る URL・`#lp` `#contact` `#apps`・リンク切れ・H1 の数・名前の無い `<nav>`・表の枠・`<ol>`・外部送信の表・色のコントラスト比
  - **見た目の決まり**：
    - 段に無い文字の大きさ・字間（0〜.08em の外）・0 以外の角丸
    - 画面の部品以外の影・グラデーション・大文字変換
    - 見出しの chws・500 以外の明朝の太さ・書体のライセンス表示のずれ
    - 決めた場所以外の紫・旧色（`#7c3aed` と DADS のリンク色）
  - **動き**：`prefers-reduced-motion: no-preference` の外の動き・0.4 秒を超える transition・0.8 秒を超える animation・`infinite`・看板とメニュー以外の animation・スクロールで動かす仕組み
  - **型の再発**：やめたクラスと id・見出しの上の英字・本文のダッシュ・句読点のあとの空白（「〜ではなく」と三つ並べは WARN）
  - **お問い合わせ**：
    - mailto のフォーム・受け口の形でない送り先・受け口が保存しない欄・ハニーポットと Turnstile の欠け
    - 送信ボタンより後ろのプライバシーのリンク
    - ヘッダーの `/#lp`・トップ以外の `/#contact`
    - ContactPage・送信後の画面の noindex・白い面（`.panel`）は `#contact` だけ
  - **実物**：
    - 見本の説明に「架空」が無い
    - 看板の画像が遅延読み込み・`fetchpriority="high"` が 1 枚でない
    - 看板に塗りのボタンがある
    - `<time>` の未来の日付
  - **SEO と AIO**：構造化データ・title と description の重複・画像の alt と幅と高さ・`llms.txt`・`favicon.ico`・`logo.png`・robots.txt・lastmod
  - **持ち込み**：出力と追跡中のファイルにホスト名や IP アドレスがない（問い合わせの受け口のホストは `src/site.mjs` と `contact.html` だけ）
- `src/data/faq.mjs`：利用規約 第15条の要点が変わったらビルドが止まる。
- ビルドの外で回すもの：`scripts/check_legal_text.py`・`scripts/check_prices.py`・非公開の検査・アクセシビリティの自己試験（下の §9）。
- 🔴 **push の前に `STAGING=1 SHOW_DRAFTS=1 npm run build` も回す**（下書きの記事は確認用のビルドにだけ入る。2026-09-25 に確認用だけ止まった）。

## 9. 変えるとき

- **色を変える** → `tokens.css` → `npm run build`（`CONTRAST` が落ちたら値を戻す）→ この §2
- **ロゴの形や色を変える** →
  1. `LogoMark.astro` と `public/favicon.svg` を直す。
  2. `node tools/preview/icons.mjs` でアイコンを書き出す。
  3. `tools/preview/og.html?auto=1` を `tools/preview/evaluate.ps1` で開いて OGP を描き直し、`public/og.jpg` にする。
- **見本を撮り直す・足す** →
  1. LP 事業の見本の HTML を `tools/preview/shoot.ps1` で撮る（PC 1280×800・SP 390×844・2 倍）。
  2. WebP で `src/assets/samples/<id>-pc|sp.webp` に置く。
  3. `src/data/samples.mjs` に足す（承認済みのテンプレートだけ・撮影日を書く）。
- **お知らせを足す** → `src/data/news.json`（確かめられる事実と日付）
- **部品を足す** → `src/components/` → `global.css`（値は段から）→ この §5
- **ページを足す** → `src/pages/<名前>.astro` → `NAV` → フッター → `src/data/updated.json`
- **料金が変わった** → `python3 scripts/check_prices.py --write` → 差分を見てコミット（金額を `.astro` に直書きしない）
- **電話の受付時間を変える** → `src/site.mjs` の `operator.hours` と、LP 事業の `config.json` の `support_hours`（特商法の表示を作り直す）
- **見た目を変えた** →
  - アクセシビリティの自己試験：`tools/preview/evaluate.ps1` で `/__preview/a11y.html` の `runAll()`・`heroFit()`・`motionCheck()` を回す。
  - `shoot.ps1 -Tabs 3` でフォーカスの輪を撮り、`-ReducedMotion` で「動きを減らす」の見え方を撮る。
  - 結果を `/site-policy.html` の試験結果に反映する。

## 10. 出典（ID）

| ID | 出典 |
|---|---|
| TUCH12 | Tuch ほか（Google）2012 視覚的な複雑さと典型性 https://research.google/pubs/pub38315/ |
| REIN13 | Reinecke ほか CHI 2013 第一印象と複雑さ https://www.eecs.harvard.edu/~kgajos/papers/2013/reinecke13aesthetics.pdf |
| FOGG02 | Fogg ほか（Stanford）信頼性の評価で「見た目」が 46.1% https://credibility.stanford.edu/pdf/How_Do_People_Evaluate_a_Web_Site%27s_Credibility_v37.pdf |
| SIGNAL | Wells ほか 2011（MIS Quarterly）サイトの質が製品の質のシグナルになる https://aisel.aisnet.org/misq/vol35/iss2/8/ |
| SEV16 | Sevilla・Townsend 2016（JMR）展示の間隔と格 https://doi.org/10.1509/jmr.13.0601 |
| WSPACE | Pracejus・Olsen・O'Guinn 2006（JCR）余白と格 https://academic.oup.com/jcr/article-abstract/33/1/82/1795433 |
| KLUGE13 | Kluge ほか 2013 ラグジュアリーブランドのトップページ https://doi.org/10.1108/ijrdm-01-2013-0013 |
| SD-LEE2017 | 李ほか『デザイン学研究』2017 文字の太さと高級感 https://www.jstage.jst.go.jp/article/jssdj/63/5/63_5_101/_article/-char/ja/ |
| SD-HIRA2005 | 平・辻『奈良高専研究紀要』2005 書体の印象（明朝＝上品） https://www.nara-k.ac.jp/nnct-library/publication/pdf/h17kiyo4.pdf |
| LIG16／LIG21／LIG22／LIG24 | LIG の記事（高級感・Noto Sans の多用・配色・余白と字間） https://liginc.co.jp/303466 ・ https://liginc.co.jp/566546 ・ https://liginc.co.jp/568190 ・ https://liginc.co.jp/624584 |
| BAIGIE13／BAIGIE-CL／BAIGIE | ベイジ https://baigie.me/sogitani/2013/08/btob_tips/ ・ https://baigie.me/officialblog/2019/10/16/btob-checklist/ |
| REFU26 | 安っぽく見えるデザインの原因（そろっていないこと） https://refu.co.jp/column/avoid-cheap-design/ |
| SURVEY18 | 高級感・上品のタグが付いた国内 18 件の実地調査（2026-09-25。一覧は `docs/best-practice-audit.md`） |
| SURVEY15 | 国内の個人・小規模の制作事務所 15 件の実地調査（2026-09-25。一覧は同じ文書） |
| ANTH | Anthropic `frontend-design` スキル（生成 AI の既定の型） https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md |
| 925 | 925 Studios（AI っぽさの目印）https://www.925studios.co/blog/ai-slop-design-tells |
| NNG-VIS／NNG-GOOD／NNG-FLAT | NN/g https://www.nngroup.com/articles/principles-visual-design/ ・ https://www.nngroup.com/articles/why-does-design-look-good/ ・ https://www.nngroup.com/articles/flat-ui-less-attention-cause-uncertainty/ |
| NNG-ANIM／NNG-PARA／NNG-ZIGZAG | NN/g https://www.nngroup.com/articles/animation-duration/ ・ https://www.nngroup.com/articles/parallax-usability/ ・ https://www.nngroup.com/articles/zigzag-page-layout/ |
| NNG-HOME | NN/g Homepage Design: 5 Fundamental Principles（2024）https://www.nngroup.com/articles/homepage-design-principles/ |
| NNG-ABOUT／NNG-PHOTO | NN/g https://www.nngroup.com/articles/about-us-information-on-websites/ ・ https://www.nngroup.com/articles/photos-as-web-content/ |
| NNG-CONTACT／NNG-PRICE／NNG-FAQ | NN/g https://www.nngroup.com/articles/contact-us-pages/ ・ https://www.nngroup.com/articles/show-prices-for-common-scenarios/ ・ https://www.nngroup.com/articles/faqs-deliver-value/ |
| NNG-ERR／NNG-PROX | NN/g https://www.nngroup.com/articles/errors-forms-design-guidelines/ ・ https://www.nngroup.com/articles/gestalt-proximity/ |
| STAN | Stanford Guidelines for Web Credibility https://credibility.stanford.edu/guidelines/index.html |
| M3／M3-MOT | Material Design 3 の文字の段と動きの時間 https://github.com/material-components/material-web/blob/main/tokens/versions/latest/sass/_md-sys-typescale.scss ・ https://raw.githubusercontent.com/androidx/androidx/androidx-main/compose/material3/material3/src/commonMain/kotlin/androidx/compose/material3/tokens/MotionTokens.kt |
| HIG-LAYOUT | Apple Human Interface Guidelines https://developer.apple.com/design/human-interface-guidelines/layout |
| RUI | Refactoring UI（Wathan・Schoger）https://www.refactoringui.com/ |
| BUTT | Practical Typography https://practicaltypography.com/summary-of-key-rules.html |
| JLREQ | W3C 日本語組版処理の要件 https://www.w3.org/TR/jlreq/ |
| W3C-SPACE | W3C Inline spacing https://www.w3.org/International/articles/styling/inline-space |
| WEB-LCP／WEB-RM／WEBDEV-LAZY | web.dev https://web.dev/articles/optimize-lcp ・ https://web.dev/articles/prefers-reduced-motion ・ https://web.dev/articles/browser-level-image-lazy-loading |
| WCAG-141／1411／148／222／2413 | WCAG 2.2 Understanding https://www.w3.org/WAI/WCAG22/Understanding/ （use-of-color・non-text-contrast・visual-presentation・pause-stop-hide・focus-appearance） |
| DADS／DADS-FORM／DADS-TABLE | デジタル庁デザインシステム https://design.digital.go.jp/ ・ https://design.digital.go.jp/dads/components/input-text/usage/ ・ https://design.digital.go.jp/dads/components/table/usage/ |
| MIC-GL | 総務省「みんなの公共サイト運用ガイドライン」2024 年版 https://www.soumu.go.jp/info-accessibility-portal/webaccessibility/ |
| GOVUK-ERR | GOV.UK Design System Error summary https://design-system.service.gov.uk/components/error-summary/ |
| JNET21 | 中小機構 J-Net21 https://j-net21.smrj.go.jp/solution/qa/pr/Q0403.html |
| SURVEY-JP | NEXER ほか（2026・n=500）https://prtimes.jp/main/html/rd/p/000003103.000044800.html |
| CAA-UCHIKESHI | 消費者庁 打消し表示に関する表示方法及び表示内容に関する留意点 https://www.caa.go.jp/policies/policy/representation/fair_labeling/pdf/fair_labeling_180607_0004.pdf |
| TOKUSHO-GUIDE | 消費者庁 特商法ガイド 広告の表示 Q&A https://www.no-trouble.caa.go.jp/qa/advertising.html |
| PPC | 個人情報保護委員会 ガイドライン（通則編）3-3-4 https://www.ppc.go.jp/personalinfo/legal/guidelines_tsusoku/ |
| MOF-TAX | 財務省 総額表示に関する主な質問（Q3・Q6）https://www.mof.go.jp/tax_policy/summary/consumption/a_001.htm |
