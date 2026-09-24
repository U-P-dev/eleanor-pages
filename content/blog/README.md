# ブログ記事の書き方（このファイルは公開されない）

- 1 記事 1 ファイル。ファイル名は `slug` と同じにする（`content/blog/<slug>.md` → `/blog/<slug>.html`）
- frontmatter: `title`（10字以上）・`slug`（英小文字・数字・ハイフン）・`description`（50字以上）・
  `category`（`集客` か `つくったもの`）・`published_at`・`updated_at`・`draft`
- **公開前は `draft: true`**。本番のビルドには出ない。確認用のビルド（`SHOW_DRAFTS=1`）でだけ見える。
  代表が読んで OK を出したら `draft` を外し、`published_at` を公開日にする
- 本文の最初に `# 見出し` を1つ（ページの H1 になる）。段落は1行で書く（段落の中の改行は改行として表示される）
- 囲み: `> [!NOTE]`（補足）・`> [!WARNING] 題`（注意）。番号付きリストは自動で DADS の形になる
- 書く前に、非公開の運用リポジトリにある記事の約束を読む（書かないことの一覧がある）
