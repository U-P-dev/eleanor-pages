# デザインの正本 — eleanor-dev.com

> **最終更新**: 2026-09-25（国内外のベストプラクティスを調べ、その差を埋めた日。突き合わせの全項目は `docs/best-practice-audit.md`）
> 見た目・部品・中身の並びを変えるときは、ここを先に読む。変えたらここを直す。
> 値の正本は `src/styles/tokens.css`、見た目は `src/styles/global.css`、部品は `src/components/`。
> 決まりの行の末尾の `[ID]` は §10 の出典。**出典の無い決まりは足さない**（好みで変えない）。

---

## 1. 方針（5つ）

1. **デジタル庁デザインシステム（DADS）の値と部品の作り方に沿う** [DADS-TYPO][DADS-LAYOUT][DADS-TABLE][DADS-FORM]。
   参照した版: デザイントークン npm 2.0.1（2026-05-28）／HTML コードスニペット v20260909。トークンとコードは MIT（表示は `tokens.css` の先頭）。
   サイト上の表記は「デジタル庁デザインシステムを参考に作成」まで（「準拠」「公式」とは書かない）。デジタル庁のロゴは使わない。
2. **実物・数字・連絡先を先に見せる** [NNG-HOME][STAN][BAIGIE][SURVEY15]。主力の LP の見本の画面を看板に置き、価格の横に条件を書く。
3. **生成 AI の既定の型を使わない** [X1][925]。面のグラデーション、見出しの上の英字、同じ形のカードの並び、既定色で面を塗ること、
   細い罫で全部を囲むこと。別の流行りの型（生成り色＋明朝＋テラコッタ、黒地＋蛍光色）へ乗り換えることも同じく避ける。
4. **ブランド色は「押すところ」「今いる場所」「ロゴ」だけ** [HIG-BRAND][DADS-COLOR]。
5. **JIS X 8341-3:2016 の適合レベル AA を目標にする** [MIC-GL]。方針と試験結果は `/site-policy.html`。

## 2. 色（正本は `tokens.css`・組み合わせは `scripts/check_site.py` の `CONTRAST` が毎回計算）

| 用途 | 値 | 備考 |
|---|---|---|
| 本文／見出し | Gray-800 `#333` ／ Gray-900 `#1a1a1a` | |
| リード・注記・画面の説明／日付・補足 | Gray-700 `#4d4d4d` ／ Gray-600 `#666` | 補足は大きさではなく色で分ける [RUI] |
| ブランド（塗りのボタン・メニューの今いるページの下線・ロゴの重なり） | `#7b3a87`（ホバー `#622e6c`・押下 `#4a2351`） | ロゴの赤と青の平均（2026-09-25 👤）。白い文字との比 7.51。旧 `#7c3aed` は Tailwind の既定色と同じ値だったのでやめた |
| ロゴの印 | 赤 `#d7263d`・青 `#1f4fd1`・重なりはブランド色 | ロゴだけに使う。文字には使わない |
| 本文中のリンク／ホバー／訪問済み／押下 | Blue-1000 ／ Blue-900 ／ Magenta-900 ／ Orange-800（灰の地は Orange-900） | DADS 標準。訪問済みを見分けられるようにする [DADS-LINK] |
| ヘッダーのメニュー・フッターのリンク | 墨 | DADS のメニューとユーティリティリンク |
| 灰の地 | Gray-50 `#f2f2f2` | **トップの `#contact` とフッターだけ**（節ごとに地の色を変えない） |
| 罫・枠（白の地／灰の地） | Gray-420 `#949494` ／ Gray-536 `#767676` | 3:1 以上 [DADS-COLOR] |
| 「※必須」・エラー | Error-2 `#ce0000` | |
| フォーカス | Yellow-300 `#ffd43d` と黒の二重 | DADS は変更を禁止 |

- 文字は大きさに関係なく 4.5:1 以上（DADS は大きい文字の 3:1 の例外を使わない）。
- グラデーションは使わない。例外は表の横スクロールを知らせる端の影だけ（機能で、飾りではない）。
- ダークモードは作らない（DADS に定義が無く、フォーカス表示もライト前提）。

## 3. 文字

**大きさの段**（DADS の Std／Dsp から選ぶ。ほかの値は `check_site.py` が止める）[DADS-TYPO][NNG-HIER][M3][HIG-TYPE]

| 役割 | SP | PC | 行の高さ |
|---|---|---|---|
| 看板 | min(8.8vw, 40px) | 40〜57px | 1.4 |
| H1（下層ページ） | 32 | 45 | 1.4 |
| H2（主の節） | 24 | 32 | 1.5 |
| H2（従の節）・H2（記事） | 24 | 24 | 1.5 |
| H3・表の題・質問・見本の題 | 20 | 20 | 1.5 |
| 本文・リード・ラベル | 16 | 17 | 1.7（記事は 1.75） |
| 表・注記・画面の説明・フッター | 16 | 16 | |
| メニューのボタン・ロゴの英字 | 14 | 14 | DADS: 制約のある場所だけ |

**和文の組み方**
- 書体: 本文は OS の和文フォント。**見出しとロゴだけ Noto Sans JP 700**（SIL OFL 1.1）を、使っている字だけ切り出してこのサイトから配る
  （`scripts/headings.mjs`。外部送信なし。約 360 字・約 70KB。取れなければ OS の書体で出る）。
- **見出しだけ字詰め（`font-feature-settings: 'palt'`）、本文はベタ組み** [JLREQ][ICS-PALT]。約物の連続も palt で詰まるので、手で詰める指定は置かない
  （2026-09-25 まで使っていた Zen Kaku Gothic New には palt が無かった）。`headings.mjs` が書体の palt の有無を報告し、無ければビルドが止まる。
- 和文と欧文・数字の間は `text-autospace: normal` に任せる [W3C-SPACE]。原稿の半角空白はそのまま残してよい。
- 1 行の長さは本文の文字で 41 字まで（`--measure: 41ic`。`@property` で長さとして受け継がせる）[JLREQ][WCAG-148][BUTTERICK]。
- 行の中の数字だけを大きくしない（行送りが崩れる）[JLREQ]。強調は太字と桁そろえだけ。
- 見出しは文節の区切りに `<wbr>`（`headings.mjs`）＋ `word-break: keep-all`。iPhone の Safari は `auto-phrase` が効かないため。
- 本文は `line-break: strict`。ソースで文の途中で改行しない（HTML で空白になる。検査が止める）。

## 4. 格子・余白・罫

- **格子**: 12 列・列間 2rem。2 列の節は、左を 1〜7 列（`.grid__main`）、右を 8〜12 列（`.grid__side`）にそろえる [DADS-LAYOUT][M3][HIG-LAYOUT]。
- **余白の段**: 8／16／24／40／64（PC の主の節だけ 96）[DADS-SPACE][M3][RUI]。部品の中の微調整（押せる範囲・印の位置・下線の位置・枠の太さ）は段の外。
- **近さでまとめる**: 見出しと本文の間は 8、段と段の間は 40。画面の説明は画面のすぐ下 [NNG-PROX]。
- **節**: トップは主の節（余白だけで区切る）と従の節（罫で区切る）の 2 段。下層ページの節は同じ間隔で並べ、主役は見出しの大きさと中身で示す。
- **罫は減らす** [RUI][DADS-TABLE][X1]: 表は縦の罫を引かず、見出し行の下の黒い罫と行の横罫だけ。SP で行を積む表は枠で囲まず、罫と余白で区切る。
  罫の長さは 3 種（画面の幅＝ヘッダーの下とフッターの上／本文の幅＝節の区切り／文章の幅＝よくある質問・お知らせ・説明リストの中）。
- **角丸は 3 段だけ**: 0（節・表・画像・囲み）／4px（文中のコード・フォーカスの輪）／8px（ボタン・入力欄）。丸い札は作らない。
- **幅**: ページの最大幅 72rem。段組みの切り替えは 48rem（768px）の 1 本。ヘッダーの水平メニューだけは 60rem から出す。

## 5. 部品

| 部品 | 置き場 | 約束 |
|---|---|---|
| ロゴの印 | `components/LogoMark.astro` | 赤と青の四角が重なり、重なりがブランド色。`public/favicon.svg` とアイコン類は同じ形 |
| ヘッダー | `layouts/Base.astro` | メニューは「サービスと料金」「つくったもの」「ブログ」「会社概要」と、右に「お問い合わせ」（墨の枠のボタン）[NNG-CONTACT] |
| フッター | `layouts/Base.astro` | よくある質問・お問い合わせ・取引の条件・プライバシーポリシー（お問い合わせ・LP 制作・保守）へ [NNG-FAQ] |
| ボタン | `.button` | **塗り（ブランド色）は 1 画面に 1 つ**。もう一つの行き先は文中リンクかアウトライン（墨） |
| 看板の見本 | `components/HeroSample.astro` | 主力の LP の見本。PC は右の列いっぱい、SP は看板の文のすぐ後。1 つの `<picture>` で出し分け、遅延読み込みにしない [NNG-HOME][WEBDEV-LAZY] |
| 見本の棚 | `components/SampleShelf.astro`（データ `src/data/samples.mjs`） | 承認済みのテンプレートだけ。**架空の店であること・段・料金・撮影日を画面の横に必ず書く** [CAA-UCHIKESHI]。画像が無い見本は出さない |
| 料金表 | `components/PriceTables.astro` | LP の表だけ（保守・フルオーダーはサービスのページ）。表の下に納期の数え方と取引条件へのリンク |
| 時系列 | `components/Timeline.astro` | 予定表のように縦に並べる。番号は文字で書く（`<ol>` を使わない）。値は料金データから |
| お知らせ・沿革 | `components/News.astro`（データ `src/data/news.json`） | 日付と一文。確かめられる事実だけ。未来の日付は書かない [JNET21][SURVEY-JP] |
| 代表の紹介 | `components/Person.astro` | 写真は `src/assets/person/` に 1 枚（撮影データを消してから）。無ければ文章だけ [NNG-PHOTO][NNG-ABOUT] |
| 問い合わせ | `components/ContactForm.astro`（`/contact.html`） | 送り先は LP 事業の受け口（`src/site.mjs` の `CONTACT`）。受け口が保存する欄だけ（種類・名前・メール・内容）。ラジオボタン、欄ごとのエラーと要約、送信の前に利用目的とプライバシーポリシー、Turnstile とハニーポット、完了は `/contact-thanks.html` [DADS-FORM][NNG-ERR][PPC][GOVUK-ERR] |
| よくある質問 | `.qa`（`src/data/faq.mjs`） | 答えを折りたたまない。画面と構造化データを同じデータから作る。規約の要約は条文と照合する |
| 表 | `.table-region` | 横スクロールの枠に名前と `tabindex="0"`。金額は右寄せ。SP で積む表は `role` と `data-label` を持つ |
| 実物の画面 | `.shot`・`.sample` | 1px の枠だけ（影・傾き・偽の端末の枠は付けない）。キャプションに何の画面か・出どころ・撮影日 [NNG-PHOTO] |
| ページの終わり | `.page-end` | 従の節として罫で区切った一言とボタン 1 つ。帯で塗らない |

使わないと決めたもの: グラデーションの面、見出しの上の英字の小見出し、同じ形のカードの並び、紫の飾り、丸い札、飾りの影、カルーセル、
ページトップへ戻るボタン、文字サイズ変更ボタン、ダークモード、装飾だけのアニメーション、自分で描いた絵（SVG）。

## 6. 中身と構成

- **トップの並び** [NNG-HOME][BAIGIE][SURVEY15]: 看板（誰に・何を・いくらで・何日で＋見本の画面）→ LP の見本 → 頼めること → LP の料金 →
  ご依頼の流れ → つくったもの → つくる人 → お知らせ → お問い合わせの案内（`#lp` `#contact` `#apps` は外から張られているので残す）。
- **価格の横に条件** [CAA-UCHIKESHI][NNG-PRICE]: 保守とあわせてのお申し込みであること、1 年間の合計の例、「最短」が何を指すか
  （お支払いの確認から確認用の初稿まで）、営業日（土日祝を除く平日）、事業者向けであること（税抜表示の前提 [MOF-TAX]）。
- **サービスと料金**: 冒頭に目次。LP の節を主役に（見本・表・1 年間の合計・ちがい）。保守の内容は「＋」で箇条に分け、用語の説明を置く。
- **会社概要**: 代表の紹介、事業者情報（受付時間・営業日・来訪しないこと・事業者向け・インボイスの状態）、これまでの歩み。
- **連絡先** [NNG-CONTACT][TOKUSHO-GUIDE]: 電話の受付時間（平日 8:00〜23:00、土日祝 9:00〜18:00・留守番電話は 1 営業日以内に折り返し）と
  返信の目安は `src/site.mjs` の 1 か所から出す。特定商取引法に基づく表示（LP 事業が生成）と同じ時間にする。
- **書かないこと**: 「コンサル」「DX」「AX」（プロフィールの「外資系コンサル」だけは 👤 が許可）、本業の社名、運用の情報（ホスト名・IP）、
  確かめていない数字、お客様の声（まだ無い。載せるときはステマ規制に従う）。

## 7. DADS から意図して外した点

| 点 | DADS | このサイト | 理由 |
|---|---|---|---|
| キーカラー | Blue | `#7b3a87`（使う場所を 3 か所に限る） | ブランド（§1-4） |
| 表の見出しセルの地 | Gray-100 | 白 | 面を減らす（§4） |
| 狭い画面の表 | 枠の中で横スクロール | 料金の表は行ごとに積む | 列を細くすると単語の途中で切れる |
| よくある質問 | アコーディオン | 開いたまま | 答えを検索と AI の回答に拾わせる |
| ヘッダーのメニューの出し方 | 768px で切り替え | 60rem（960px）で切り替え | 4 項目＋問い合わせが 768px では収まらない |
| ロゴのリンク | リンクは下線 | 下線なし | 位置と慣習で分かる |
| 移したページの `<ol>` | 番号は文字で | 旧サイトのまま | 本文を変えない約束が優先（表の縦罫は CSS で外した） |

## 8. 機械で止まるもの（`npm run build`）

- `scripts/headings.mjs`: 止めない（書体が取れなければ WARN。取れて palt が無ければ `check_site.py` が止める）
- `scripts/check_site.py`:
  - 守る URL・`#lp` `#contact` `#apps`・リンク切れ・H1 の数・名前の無い `<nav>`・表の枠・`<ol>`・外部送信の表・色のコントラスト比
  - **見た目の決まり**: 段に無い文字の大きさ・表の縦罫・`#contact` 以外の灰の地・見出しの palt・旧ブランド色 `#7c3aed`
  - **型の再発**: グラデーション・やめたクラスと id・見出しの上の英字・3 段以外の角丸・飾りの影・広い字間・大文字変換・
    3 か所以外のブランド色・本文のダッシュ・句読点のあとの空白（「〜ではなく」と三つ並べは WARN）
  - **問い合わせ**: mailto のフォーム・受け口の形でない送り先・受け口が保存しない欄・ハニーポットと Turnstile の欠け・
    送信ボタンより後ろのプライバシーのリンク・ヘッダーの `/#lp`・トップ以外の `/#contact`・ContactPage・送信後の画面の noindex
  - **実物**: 見本の説明に「架空」が無い・看板の画像が遅延読み込み・`<time>` の未来の日付
  - **SEO と AIO**: 構造化データ（JSON・`@id` のつながり・電話の +81・日時の +09:00・FAQ と画面の一致）、title と description の重複、
    画像の alt と幅と高さ、`llms.txt`・`favicon.ico`・`logo.png`、robots.txt、lastmod
  - **持ち込み**: 出力と追跡中のファイルにホスト名や IP アドレスがない（問い合わせの受け口のホストは `src/site.mjs` と `contact.html` だけ）
- `src/data/faq.mjs`: 利用規約 第15条の要点が変わったらビルドが止まる
- ビルドの外で回すもの: `scripts/check_legal_text.py`・`scripts/check_prices.py`・非公開の検査・アクセシビリティの自己試験（下の §9）
- 🔴 **push の前に `STAGING=1 SHOW_DRAFTS=1 npm run build` も回す**（下書きの記事は確認用のビルドにだけ入る。2026-09-25 に確認用だけ止まった）

## 9. 変えるとき

- **色を変える** → `tokens.css` → `npm run build`（`CONTRAST` が落ちたら値を戻す）→ この §2
- **ロゴの形や色を変える** → `LogoMark.astro` と `public/favicon.svg` → `node tools/preview/icons.mjs` →
  `tools/preview/og.html?auto=1` を `tools/preview/evaluate.ps1` で開いて OGP を描き直す → `public/og.jpg`
- **見本を撮り直す・足す** → LP 事業の見本の HTML を `tools/preview/shoot.ps1` で撮る（PC 1280×800・SP 390×844・2 倍）→ WebP で
  `src/assets/samples/<id>-pc|sp.webp` → `src/data/samples.mjs`（承認済みのテンプレートだけ・撮影日）
- **お知らせを足す** → `src/data/news.json`（確かめられる事実と日付）
- **部品を足す** → `src/components/` → `global.css`（値は段から）→ この §5
- **ページを足す** → `src/pages/<名前>.astro` → `NAV` → フッター → `src/data/updated.json`
- **料金が変わった** → `python3 scripts/check_prices.py --write` → 差分を見てコミット（金額を `.astro` に直書きしない）
- **電話の受付時間を変える** → `src/site.mjs` の `operator.hours` と、LP 事業の `config.json` の `support_hours`（特商法の表示を作り直す）
- **見た目を変えた** → アクセシビリティの自己試験（`tools/preview/evaluate.ps1` で `/__preview/a11y.html` の `runAll()`）→ `/site-policy.html` の試験結果

## 10. 出典（ID）

| ID | 出典 |
|---|---|
| DADS-TYPO／LAYOUT／SPACE／LINK／COLOR | デジタル庁デザインシステム https://design.digital.go.jp/dads/foundations/ （typography・layout・spacing・link-text・color） |
| DADS-TABLE／DADS-FORM | 同 https://design.digital.go.jp/dads/components/table/usage/ ・ https://design.digital.go.jp/dads/components/input-text/usage/ |
| MIC-GL | 総務省「みんなの公共サイト運用ガイドライン」2024 年版 https://www.soumu.go.jp/info-accessibility-portal/webaccessibility/ |
| NNG-HOME | NN/g Homepage Design: 5 Fundamental Principles（2024）https://www.nngroup.com/articles/homepage-design-principles/ |
| NNG-ABOUT／NNG-PHOTO | NN/g About Us Information（2019）https://www.nngroup.com/articles/about-us-information-on-websites/ ・ Photos as Web Content https://www.nngroup.com/articles/photos-as-web-content/ |
| NNG-CONTACT／NNG-PRICE／NNG-FAQ | NN/g https://www.nngroup.com/articles/contact-us-pages/ ・ https://www.nngroup.com/articles/show-prices-for-common-scenarios/ ・ https://www.nngroup.com/articles/faqs-deliver-value/ |
| NNG-ERR | NN/g 10 Design Guidelines for Reporting Errors in Forms https://www.nngroup.com/articles/errors-forms-design-guidelines/ |
| NNG-HIER／NNG-PROX | NN/g https://www.nngroup.com/articles/visual-hierarchy-ux-definition/ ・ https://www.nngroup.com/articles/gestalt-proximity/ |
| STAN | Stanford Guidelines for Web Credibility https://credibility.stanford.edu/guidelines/index.html |
| WEBDEV-LAZY | web.dev Browser-level image lazy loading https://web.dev/articles/browser-level-image-lazy-loading |
| GOVUK-ERR | GOV.UK Design System Error summary https://design-system.service.gov.uk/components/error-summary/ |
| RUI | Refactoring UI（Wathan・Schoger）https://www.refactoringui.com/ |
| M3 | Material Design 3 の文字の段 https://github.com/material-components/material-web/blob/main/tokens/versions/latest/sass/_md-sys-typescale.scss |
| HIG-TYPE／HIG-LAYOUT／HIG-BRAND | Apple Human Interface Guidelines https://developer.apple.com/design/human-interface-guidelines/ （typography・layout・branding） |
| JLREQ | W3C 日本語組版処理の要件 https://www.w3.org/TR/jlreq/ |
| W3C-SPACE | W3C Inline spacing https://www.w3.org/International/articles/styling/inline-space |
| WCAG-148 | WCAG 2.2 Understanding 1.4.8 https://www.w3.org/WAI/WCAG22/Understanding/visual-presentation.html |
| BUTTERICK | Practical Typography, Line length https://practicaltypography.com/line-length.html |
| ICS-PALT | ICS MEDIA 見出しの字詰め https://ics.media/entry/14087/ |
| BAIGIE | ベイジ BtoB サイトの 180 のチェックリスト https://baigie.me/officialblog/2019/10/16/btob-checklist/ |
| JNET21 | 中小機構 J-Net21 https://j-net21.smrj.go.jp/solution/qa/pr/Q0403.html |
| SURVEY-JP | NEXER ほか（2026・n=500）https://prtimes.jp/main/html/rd/p/000003103.000044800.html |
| SURVEY15 | 国内の個人・小規模の制作事務所 15 件の実地調査（2026-09-25。一覧は `docs/best-practice-audit.md`） |
| CAA-UCHIKESHI | 消費者庁 打消し表示に関する表示方法及び表示内容に関する留意点 https://www.caa.go.jp/policies/policy/representation/fair_labeling/pdf/fair_labeling_180607_0004.pdf |
| TOKUSHO-GUIDE | 消費者庁 特商法ガイド 広告の表示 Q&A https://www.no-trouble.caa.go.jp/qa/advertising.html |
| PPC | 個人情報保護委員会 ガイドライン（通則編）3-3-4 https://www.ppc.go.jp/personalinfo/legal/guidelines_tsusoku/ |
| MOF-TAX | 財務省 総額表示に関する主な質問（Q3・Q6）https://www.mof.go.jp/tax_policy/summary/consumption/a_001.htm |
| X1 | Anthropic `frontend-design` スキル https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md |
| 925 | 925 Studios（AI っぽさの目印）https://www.925studios.co/blog/ai-slop-design-tells |
