#!/usr/bin/env python3
"""ビルド出力（dist/）の検査。`npm run build` の最後に走り、FAIL が1件でもあれば exit 1（= 公開されない）。

解約手帳（kaiyaku-navi）の scripts/check_site.py を土台に、このサイト固有の約束を足した:

  - 守る URL: Stripe・アプリストア・アプリ内・Search Console・AdSense が参照している URL が全部 dist/ にあるか。
    index.html に #lp（Stripe 審査＝サイトの商品と請求商品の一致）・#contact・#apps があるか
  - 表記の約束: 古い看板の言葉（「会議なし」「0 meetings」）を出さない
  - title / description / canonical・H1 が1つ・id の重複・サイト内リンク切れ（相対リンクを含む）
  - デジタル庁デザインシステム（DADS）の約束: <ol> を使わない／表は名前つきの枠に入れる／<nav> に名前を付ける
    （旧サイトから本文をそのまま移したページは、本文を変えない約束が優先するので <ol> と表の枠は見ない）
  - 外部から自動で読み込むものの送信先が、サイトポリシーの外部送信の表に載っているか（電気通信事業法 27条の12）
  - 色のコントラスト比（src/styles/tokens.css の値で、文字 4.5:1・枠やアイコン 3:1）
  - 生成 AI が作ったページの目印として挙がる型を戻さない（DESIGN.md §1）: 面のグラデーション・見出しの上の英字・
    同じ形のカード・一律の角丸・飾りの影・紫の飾り使い・本文のダッシュ
  - 見た目の決まり（DESIGN.md §3・§4）: 文字の大きさは段の値だけ・表に縦の罫を引かない・灰の地はお問い合わせだけ・
    見出しは字詰め（palt）・旧ブランド色を使わない
  - SEO と AIO: 構造化データ（JSON として読めるか・@id のつながり・電話の国番号・日時の時差・FAQ と画面の一致）、
    title と description の重複、画像の代替テキストと大きさ、llms.txt、robots.txt、サイトマップの最終更新日
  - 公開リポジトリと出力に、サブドメインのホスト名や IP アドレスを持ち込まない

このほかの言葉づかいの検査は、非公開の運用リポジトリから dist/ を調べる。

使い方: python3 scripts/check_site.py [dist ディレクトリ]
"""
from __future__ import annotations

import datetime
import glob
import json
import os
import struct
import subprocess
import posixpath
import re
import sys
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

SITE_URL = "https://eleanor-dev.com"
SITE_HOST = "eleanor-dev.com"
BEACON_SRC = "https://static.cloudflareinsights.com/beacon.min.js"

# 外部から参照されているので、無くなったら公開しない URL（dist/ からの相対パス）
PROTECTED = [
    "index.html", "company.html", "404.html",
    # Stripe の遷移先と「公開情報」の3つ（LP 事業が自動生成して直下に書き込む）
    "thanks.html", "cancel.html", "tokusho.html", "privacy-lp.html", "terms-lp.html",
    # アプリストアの掲載情報・アプリ内に固定されたリンク
    "privacy.html", "support.html", "account-deletion.html",
    "privacy-hitomoyou.html", "terms-hitomoyou.html", "tokusho-hitomoyou.html", "support-hitomoyou.html",
    # AdSense・Search Console・セキュリティ窓口・検索エンジン
    "ads.txt", "googlef3142e0a3a00e599.html", ".well-known/security.txt", "robots.txt", "sitemap-index.xml",
    "favicon.svg", "apple-touch-icon.png", "og.jpg",
]
# index.html に無ければならないページ内の行き先（外部・自動生成ページのナビから張られている）
PROTECTED_IDS = ["lp", "contact", "apps"]
# LP 事業が自動生成するページ。このサイトの検査の対象外（存在だけ確かめる）
GENERATED = {"/tokusho.html", "/privacy-lp.html", "/terms-lp.html"}
# ページではないファイル（Search Console の所有確認）
NOT_PAGES = {"/googlef3142e0a3a00e599.html"}
# 旧サイトから本文をそのまま移したページ（scripts/check_legal_text.py が本文を照合する）
MIGRATED = {"/privacy.html", "/support.html", "/account-deletion.html", "/privacy-hitomoyou.html", "/terms-hitomoyou.html",
            "/tokusho-hitomoyou.html", "/support-hitomoyou.html", "/thanks.html", "/cancel.html"}

LEAKS = ["-->", "**", "CLAUDE.md", "undefined", "NaN", "[object Object]"]
# 古い看板の言葉（2026-09-24 に看板を「つくって終わり」に、しない。へ変えた）
BANNED = ["会議なし", "0 meetings"]

# 自動で読み込まれる外部の送信先 → サイトポリシーの外部送信の表に書く事業者名
SENDERS = {
    "static.cloudflareinsights.com": "Cloudflare, Inc.",
    "challenges.cloudflare.com": "Cloudflare, Inc.",
    "fonts.googleapis.com": "Google LLC",
    "fonts.gstatic.com": "Google LLC",
}
POLICY_PATH = "/site-policy.html"

# 色の組み合わせ（前景, 背景, 最低比, どこで使っているか）。値は src/styles/tokens.css の変数名で引く
WHITE, GRAY50 = "color-neutral-white", "color-neutral-solid-gray-50"
CONTRAST = [
    ("color-neutral-solid-gray-800", WHITE, 4.5, "本文"),
    ("color-neutral-solid-gray-800", GRAY50, 4.5, "灰の地の本文・フッター"),
    ("color-neutral-solid-gray-900", WHITE, 4.5, "見出し・アウトラインのボタン"),
    ("color-neutral-solid-gray-900", GRAY50, 4.5, "灰の地の見出し・アウトラインのボタン（ホバー）"),
    ("color-neutral-solid-gray-700", WHITE, 4.5, "リード文・表の注記・画面の説明"),
    ("color-neutral-solid-gray-700", GRAY50, 4.5, "灰の地の表の注記"),
    ("color-neutral-solid-gray-600", WHITE, 4.5, "日付・フォームの補足"),
    ("color-neutral-solid-gray-600", GRAY50, 4.5, "灰の地のフォームの補足・©"),
    (WHITE, "color-brand", 4.5, "塗りのボタン"),
    (WHITE, "color-brand-hover", 4.5, "塗りのボタン（ホバー）"),
    (WHITE, "color-brand-press", 4.5, "塗りのボタン（押下）"),
    (WHITE, "color-neutral-solid-gray-900", 4.5, "手順の番号（移したページ）"),
    ("color-brand", WHITE, 3.0, "今いるページの下線・ロゴの重なり"),
    ("color-logo-red", WHITE, 3.0, "ロゴの赤"),
    ("color-logo-blue", WHITE, 3.0, "ロゴの青"),
    ("color-error-2", WHITE, 4.5, "「※必須」・エラー"),
    ("color-error-2", GRAY50, 4.5, "灰の地の「※必須」・エラー"),
    ("color-primitive-blue-1000", WHITE, 4.5, "リンク"),
    ("color-primitive-blue-1000", GRAY50, 4.5, "灰の地のリンク"),
    ("color-primitive-magenta-900", WHITE, 4.5, "訪問済みのリンク"),
    ("color-primitive-magenta-900", GRAY50, 4.5, "灰の地の訪問済みリンク"),
    ("color-primitive-blue-900", WHITE, 4.5, "ホバー中のリンク"),
    ("color-primitive-orange-800", WHITE, 4.5, "押している間のリンク"),
    ("color-primitive-blue-900", GRAY50, 4.5, "灰の地でホバー中のリンク"),
    ("color-primitive-orange-900", GRAY50, 4.5, "灰の地で押している間のリンク"),
    ("color-primitive-blue-1000", "color-primitive-yellow-300", 4.5, "フォーカス中のリンク（黄色の地）"),
    ("color-primitive-magenta-900", "color-primitive-yellow-300", 4.5, "フォーカス中の訪問済みリンク"),
    ("color-neutral-solid-gray-420", WHITE, 3.0, "白の地の罫線・画面の枠"),
    ("color-neutral-solid-gray-536", GRAY50, 3.0, "灰の地の枠"),
    ("color-neutral-solid-gray-600", WHITE, 3.0, "入力欄の枠"),
    ("color-primitive-yellow-900", WHITE, 3.0, "注意の枠"),
    ("color-neutral-black", WHITE, 3.0, "フォーカスの黒線"),
]

# ── 生成 AI が作ったページの目印として挙がる型（DESIGN.md §1。出典は同じ節）を戻さない ──
# 見た目の型をやめたときに消したクラス。出力に残っていたら、どこかの部品が古い書き方のまま
RETIRED_CLASSES = ["section__eyebrow", "hero__eyebrow", "card--accent", "section--tint", "cta-band", "on-dark", "tag-list",
                   # 2026-09-25: 問い合わせを専用ページとラジオボタンにした（会社名の欄と種類の選択肢の箱をやめた）
                   "form-error",
                   # 2026-09-25: 見出しの字詰めを palt に任せた・節の余白をそろえた
                   "kern-open", "kern-close", "section--flush"]
# 角丸は 3 段だけ（0・4px・8px）。全部に同じ角丸を付けない・丸い札を作らない
RADIUS_OK = {"0", "0px", "var(--border-radius-4)", "var(--border-radius-8)", ".25rem", "0.25rem", ".5rem", "0.5rem", "4px", "8px"}
# ブランドの紫を使ってよいのは「塗りのボタン」「今いるページ」「ロゴ」だけ（ロゴは SVG なので CSS には出ない）
BRAND = ["#7b3a87", "#622e6c", "#4a2351"]
VIOLET = ["var(--key)", "var(--key-hover)", "var(--key-press)", "var(--color-brand)", "var(--color-brand-hover)",
          "var(--color-brand-press)", *BRAND]
VIOLET_OK = ("button--primary", "aria-current", ":root")
# 旧ブランド色（Tailwind の既定色 violet-600 と同じ値。2026-09-25 に #7b3a87 へ替えた）。CSS にも HTML の属性にも書かない
RETIRED_COLORS = ["#7c3aed"]
# 文字の大きさは段の値だけ（DADS の Std-16/17/20/24/32/45 と看板。DESIGN.md §3）。14px はメニューのボタンとロゴの英字だけ
FONT_OK = {"1rem", "1.0625rem", "1.25rem", "1.5rem", "2rem", "2.8125rem", "3.5625rem", "inherit", "1em"}
FONT_14 = (".875rem", ("menu-button", "site-logo__en", ":root"))
HERO_OK = {"min(8.8vw,2.5rem)", "clamp(2.5rem,5.2vw,3.5625rem)"}
# グラデーションを使ってよいのは、表の横スクロールを知らせる端の影だけ（機能で、飾りではない）
GRADIENT_OK = (".table-region",)
LOGO_SVG = re.compile(r'<svg class="site-logo__mark"[\s\S]*?</svg>')
EYEBROW = re.compile(r"<p[^>]*>\s*[A-Za-z][A-Za-z0-9 &'’.\-]{0,30}\s*</p>\s*<h[1-4]\b")
DASHES = ("—", "―")
# ホスト名と IP アドレス（公開リポジトリと出力に持ち込まない。www は本体への転送なので許す）
SUBDOMAIN = re.compile(r"\b(?!www\.)[a-z0-9-]+(?:\.[a-z0-9-]+)*\.eleanor-dev\.com\b", re.I)
# 問い合わせフォームの受け口は、公開の HTML に載る前提の値。置いてよいのは定数の 1 か所と、フォームのあるページだけ
FORM_HOST = "form." + SITE_HOST
HOST_OK = {FORM_HOST: {"src/site.mjs", "contact.html"}}
# 受け口（LP 事業の Worker）が保存する欄。これ以外の欄は受け取られずに捨てられる
FORM_FIELDS = {"name", "email", "subject", "message", "_hp", "cf-turnstile-response"}
FORM_ACTION = re.compile(r"https://" + re.escape(FORM_HOST) + r"/f/[0-9a-f]{16}")
# 「Chrome/140.0.0.0」のような製品名/版番号は IP アドレスとして扱わない（2026-09-24 に誤検出した）
IPV4 = re.compile(r"(?<![\d.])(?<![A-Za-z]/)(?:\d{1,3}\.){3}\d{1,3}(?![\d.])")
IP_OK = {"0.0.0.0", "127.0.0.1"}
# 新しいページに無ければならないファイル（構造化データのロゴ・検索結果のアイコン・書体のライセンス・AI 向けの案内）
REQUIRED = ["favicon.ico", "logo.png", "fonts/OFL.txt", "llms.txt"]
JP_GAP = re.compile(r"[。、」）]\s+(?=[\u3040-\u30ff\u4e00-\u9fff「（])")
JP_GAP_TAIL = re.compile(r"[。、」）]\s+$")
INLINE = {"a", "strong", "em", "span", "time", "code", "small", "b", "i", "abbr"}
VOID = {"meta", "link", "br", "img", "hr", "input", "source", "wbr", "area", "base", "col", "embed", "track"}


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.comments: list[str] = []
        self.links: list[str] = []
        self.ids: list[str] = []
        self.h1 = 0
        self.ol = 0
        self.title = ""
        self.meta: dict[str, str] = {}
        self.canonical = ""
        self.scripts: list[str] = []
        self.loads: list[str] = []
        self.text: list[str] = []
        self.tables: list[bool] = []
        self.regions: list[dict[str, str]] = []
        self.navs: list[dict[str, str]] = []
        self.imgs: list[dict[str, str]] = []
        self.jsonld: list[str] = []
        self._ld = False
        # 句読点のあとの空白（ソースの改行が HTML で空白になったもの）。同じ文字のまとまりの中か、文中の要素の直前だけを見る
        self.jp_gaps: list[str] = []
        self._gap_tail = ""
        self._stack: list[tuple[str, set[str]]] = []

    def _inside(self, cls: str) -> bool:
        return any(cls in classes for _, classes in self._stack)

    def handle_starttag(self, tag, attrs):
        if self._gap_tail and tag in INLINE:
            self.jp_gaps.append(repr(self._gap_tail[-20:]) + f" <{tag}>")
        self._gap_tail = ""
        a = {k: v or "" for k, v in attrs}
        classes = set(a.get("class", "").split())
        if a.get("id"):
            self.ids.append(a["id"])
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag == "h1":
            self.h1 += 1
        if tag == "ol":
            self.ol += 1
        if tag == "meta" and a.get("name"):
            self.meta[a["name"]] = a.get("content", "")
        if tag == "link":
            rel = a.get("rel", "")
            if rel == "canonical":
                self.canonical = a.get("href", "")
            elif rel in ("stylesheet", "preload", "modulepreload", "icon", "apple-touch-icon", "manifest", "preconnect"):
                self.loads.append(a.get("href", ""))
        if tag == "script" and a.get("src"):
            self.scripts.append(a["src"])
            self.loads.append(a["src"])
        if tag in ("img", "iframe", "audio", "video", "source", "embed") and a.get("src"):
            self.loads.append(a["src"])
        if tag == "img":
            self.imgs.append({**a, "_in_figure": "1" if any(t == "figure" for t, _ in self._stack) else ""})
        if tag == "script" and a.get("type") == "application/ld+json":
            self._ld = True
            self.jsonld.append("")
        if tag == "table":
            self.tables.append(self._inside("table-region"))
        if "table-region" in classes:
            self.regions.append(a)
        if tag == "nav":
            self.navs.append(a)
        if tag not in VOID:
            self._stack.append((tag, classes))

    def handle_endtag(self, tag):
        self._gap_tail = ""
        if tag == "script":
            self._ld = False
        if any(t == tag for t, _ in self._stack):
            while self._stack and self._stack.pop()[0] != tag:
                pass

    def handle_data(self, data):
        if self._ld:
            self.jsonld[-1] += data
            return
        if not self._stack:
            return
        tags = [t for t, _ in self._stack]
        if tags[-1] == "title":
            self.title += data
        elif "script" not in tags and "style" not in tags:
            self.text.append(data)
            if "pre" not in tags and "code" not in tags:
                m = JP_GAP.search(data)
                if m:
                    self.jp_gaps.append(repr(data[max(0, m.start() - 15):m.end() + 15]))
                self._gap_tail = data if JP_GAP_TAIL.search(data) else ""

    def handle_comment(self, data):
        self.comments.append(data)


def url_path(dist: str, html_path: str) -> str:
    rel = os.path.relpath(html_path, dist).replace(os.sep, "/")
    return "/" if rel == "index.html" else "/" + rel


def resolves(dist: str, page_path: str, href_path: str) -> bool:
    """サイト内の href（絶対・相対）が dist/ の実在のファイルに当たるか。"/" は index.html"""
    base = "/" if page_path == "/" else posixpath.dirname(page_path) + "/"
    path = posixpath.normpath(posixpath.join(base, unquote(href_path))) if not href_path.startswith("/") else unquote(href_path)
    if path.endswith("/"):
        path += "index.html"
    return os.path.isfile(os.path.join(dist, path.lstrip("/")))


def host_of(url: str) -> str:
    return (urlsplit(url).hostname or "").lower()


def host_matches(host: str, domain: str) -> bool:
    return host == domain or host.endswith("." + domain)


def luminance(hex_color: str) -> float:
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    rgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a: str, b: str) -> float:
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def check_colors(root: str) -> list[str]:
    path = os.path.join(root, "src/styles/tokens.css")
    tokens = dict(re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{3,6})\s*;", open(path, encoding="utf-8").read()))
    fails = []
    for fg, bg, minimum, where in CONTRAST:
        if fg not in tokens or bg not in tokens:
            fails.append(f"  ✗ 色 {where}: tokens.css に --{fg if fg not in tokens else bg} が無い")
            continue
        r = contrast(tokens[fg], tokens[bg])
        if r < minimum:
            fails.append(f"  ✗ 色 {where}: {tokens[fg]} / {tokens[bg]} のコントラスト比 {r:.2f}（{minimum} 以上にする）")
    return fails


def beacon_token(root: str) -> str:
    m = re.search(r"cloudflareBeaconToken:\s*'([^']*)'", open(os.path.join(root, "src/site.mjs"), encoding="utf-8").read())
    return m.group(1) if m else ""


def banned_in(text: str) -> list[str]:
    return [w for w in BANNED if w in text]


def css_rules(css: str):
    """最小化された CSS から (セレクタ, 宣言) を取り出す（@media・@supports の中の規則も拾う）"""
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        yield m.group(1).strip(), m.group(2)


def check_css(dist: str, inline_css: list[str]) -> list[str]:
    """生成 AI が作ったページの目印として挙がる見た目の型を、出力の CSS から探す（DESIGN.md §1）"""
    fails: list[str] = []
    heading_palt: list[bool] = []
    sources = [(os.path.relpath(p, dist), open(p, encoding="utf-8").read()) for p in sorted(glob.glob(os.path.join(dist, "_astro", "*.css")))]
    sources += [("<style>", c) for c in inline_css]
    for name, css in sources:
        for sel, decl in css_rules(css):
            if sel.startswith("@font-face"):
                continue
            low = decl.lower()
            where = f"{name} の「{sel[:70]}」"
            if re.search(r"(?:repeating-)?(?:linear|radial|conic)-gradient\(", low) and not any(ok in sel for ok in GRADIENT_OK):
                fails.append(f"  ✗ CSS {where}: グラデーションを使っている（使ってよいのは表の横スクロールの影だけ）")
            for v in re.findall(r"border-radius:([^;]+)", low):
                v = v.replace("!important", "").strip()
                if v not in RADIUS_OK:
                    fails.append(f"  ✗ CSS {where}: 角丸 {v}（0・4px・8px の 3 段だけ）")
            if re.search(r"(?:^|;)\s*(?:box-shadow|text-shadow|filter|backdrop-filter):", low) and ":focus-visible" not in sel:
                fails.append(f"  ✗ CSS {where}: 影・ぼかしを飾りに使っている（使ってよいのはフォーカスの輪だけ）")
            for v in re.findall(r"letter-spacing:\s*(-?[\d.]+)em", low):
                if float(v) > 0.08:
                    fails.append(f"  ✗ CSS {where}: 字間 {v}em（0.08em まで。字間を広げた英字の小見出しは型の目印）")
            if "text-transform:uppercase" in low.replace(" ", ""):
                fails.append(f"  ✗ CSS {where}: 大文字への変換を使っている")
            for token in VIOLET:
                if token in low and not any(ok in sel for ok in VIOLET_OK):
                    fails.append(f"  ✗ CSS {where}: ブランドの紫（{token}）を飾りに使っている（塗りのボタン・今いるページ・ロゴだけ）")
            for token in RETIRED_COLORS:
                if token in low:
                    fails.append(f"  ✗ CSS {where}: 旧ブランド色 {token} を使っている（ブランド色は {BRAND[0]}）")
            for prop, v in re.findall(r"(?:^|;)\s*(font-size|--font-size-[\w-]+|--fs-[\w-]+)\s*:\s*([^;]+)", low):
                v = re.sub(r"(?<![\d.])0\.", ".", v.replace(" ", "").replace("!important", ""))
                ok = (v.startswith(("var(--font-size-", "var(--fs-")) or v.replace(".", "0.", 1) in FONT_OK or v in FONT_OK
                      or (prop == "--fs-hero" and v in HERO_OK)
                      or (v == FONT_14[0] and any(w in sel for w in FONT_14[1])))
                if not ok:
                    fails.append(f"  ✗ CSS {where}: 文字の大きさ {v}（段の値だけ。DESIGN.md §3）")
            # 表は行の横罫だけで区切る（縦の罫・四方の枠を引かない。DADS のテーブル・Refactoring UI「罫を減らす」）
            if re.search(r"table-region|table--stack|\btable\b|data-table", sel):
                for m in re.finditer(r"(?:^|;)\s*(border|border-left|border-right|border-inline(?:-start|-end)?)\s*:\s*([^;]+)", low):
                    if m.group(2).strip() not in ("0", "none", "0 none", "none 0"):
                        fails.append(f"  ✗ CSS {where}: 表に縦の罫・四方の枠（{m.group(1)}: {m.group(2).strip()}）。行の横罫だけにする")
            # 見出しは字詰め（palt）を効かせる
            if re.search(r"(?:^|,)h1(?:,|$)", sel) and "font-feature-settings" in low:
                heading_palt.append("palt" in low)
    if heading_palt and not any(heading_palt):
        fails.append("  ✗ CSS: 見出し（h1〜h4）の規則に font-feature-settings: 'palt' が無い（見出しは字詰めする。DESIGN.md §3）")
    elif not heading_palt:
        fails.append("  ✗ CSS: 見出し（h1〜h4）の書体の設定が見つからない")
    return fails


def refs_in(node, out: set[str]) -> set[str]:
    """構造化データの中の参照（{"@id": …} だけの辞書）を集める"""
    if isinstance(node, dict):
        if set(node) == {"@id"}:
            out.add(node["@id"])
        for v in node.values():
            refs_in(v, out)
    elif isinstance(node, list):
        for v in node:
            refs_in(v, out)
    return out


def png_size(path: str) -> tuple[int, int]:
    with open(path, "rb") as f:
        head = f.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        return (0, 0)
    return struct.unpack(">II", head[16:24])


def draft_slugs(root: str) -> list[str]:
    out = []
    for p in glob.glob(os.path.join(root, "content", "blog", "*.md")):
        fm = re.match(r"^---\n([\s\S]*?)\n---", open(p, encoding="utf-8").read())
        if fm and re.search(r"^draft:\s*true\s*$", fm.group(1), re.M):
            slug = re.search(r"^slug:\s*(\S+)", fm.group(1), re.M)
            if slug:
                out.append(slug.group(1))
    return out


def leak_findings(text: str, where: str = "") -> list[str]:
    found = [m.group(0) for m in SUBDOMAIN.finditer(text) if where not in HOST_OK.get(m.group(0).lower(), set())]
    found += [ip for ip in IPV4.findall(text) if ip not in IP_OK and all(0 <= int(x) <= 255 for x in ip.split("."))]
    return found


def check_leaks(dist: str, root: str) -> tuple[list[str], list[str]]:
    """公開リポジトリ（追跡中のファイル）と出力に、サブドメインのホスト名・IP アドレスが無いか"""
    fails: list[str] = []
    notes: list[str] = []
    for p in glob.glob(os.path.join(dist, "**", "*"), recursive=True):
        if os.path.isfile(p) and p.endswith((".html", ".css", ".js", ".txt", ".xml", ".json")):
            for hit in leak_findings(open(p, encoding="utf-8", errors="ignore").read(), os.path.relpath(p, dist))[:1]:
                fails.append(f"  ✗ 出力 {os.path.relpath(p, dist)} にホスト名か IP アドレス「{hit}」がある")
    try:
        # まだコミットしていない新しいファイルも見る（手元で通って Cloudflare のビルドで落ちる、を防ぐ。2026-09-24）
        tracked = subprocess.run(["git", "-C", root, "ls-files", "--cached", "--others", "--exclude-standard"],
                                 capture_output=True, text=True, check=True).stdout.split()
    except (OSError, subprocess.CalledProcessError):
        notes.append("  · git が使えないので、追跡中のファイルのホスト名の検査は省いた")
        return fails, notes
    for rel in tracked:
        if rel in ("package-lock.json",) or rel.startswith("public/fonts/") or not rel.endswith(
            (".astro", ".mjs", ".js", ".ts", ".css", ".md", ".py", ".json", ".jsonc", ".html", ".txt", ".xml", ".ps1", ".toml", ".yml")
        ):
            continue
        path = os.path.join(root, rel)
        if os.path.isfile(path):
            for hit in leak_findings(open(path, encoding="utf-8", errors="ignore").read(), rel)[:1]:
                fails.append(f"  ✗ 公開リポジトリの {rel} にホスト名か IP アドレス「{hit}」がある")
    return fails, notes


def check(dist: str, root: str) -> tuple[list[str], list[str]]:
    fails: list[str] = []
    notes: list[str] = []
    for rel in PROTECTED:
        if not os.path.isfile(os.path.join(dist, rel)):
            fails.append(f"  ✗ 守る URL /{rel} が dist/ に無い（外部から参照されている）")
    pages = sorted(glob.glob(os.path.join(dist, "**/*.html"), recursive=True))
    if not pages:
        return fails + [f"  ✗ {dist} に HTML が無い（ビルドされていない）"], notes

    parsed: dict[str, Page] = {}
    raws: dict[str, str] = {}
    for html_path in pages:
        if url_path(dist, html_path) in NOT_PAGES:
            continue
        raw = open(html_path, encoding="utf-8").read()
        page = Page()
        page.feed(raw)
        parsed[url_path(dist, html_path)] = page
        raws[url_path(dist, html_path)] = raw
    inline_css: list[str] = []
    titles: dict[str, list[str]] = {}
    descriptions: dict[str, list[str]] = {}
    policy = parsed.get(POLICY_PATH)
    policy_text = "".join(policy.text) if policy else ""
    want_beacon = 1 if beacon_token(root) else 0

    home = parsed.get("/")
    for i in PROTECTED_IDS:
        if home and i not in home.ids:
            fails.append(f"  ✗ / にページ内の行き先 #{i} が無い（外部・自動生成ページのナビから張られている）")

    for path, page in parsed.items():
        def fail(msg: str) -> None:
            fails.append(f"  ✗ {path} {msg}")

        # --- 外部送信（自動生成ページも含めて見る） ---
        for url in page.loads:
            host = host_of(url)
            if not host or host_matches(host, SITE_HOST):
                continue
            sender = next((name for d, name in SENDERS.items() if host_matches(host, d)), None)
            if sender is None:
                fail(f"外部から自動で読み込むものがあるが、送信先 {host} が SENDERS とサイトポリシーに無い")
            elif sender not in policy_text:
                fail(f"送信先 {host}（{sender}）がサイトポリシーの外部送信の表に載っていない")
        if path in GENERATED:
            continue

        text = "".join(page.text)
        visible = text + page.title + page.meta.get("description", "")
        if page.comments:
            fail(f"HTML コメントが {len(page.comments)} 件残っている: {page.comments[0].strip()[:50]!r}")
        for leak in LEAKS:
            if leak in text:
                i = text.find(leak)
                fail(f"本文に「{leak}」が見えている: …{text[max(0, i - 25):i + 25]!r}…")
        for word in banned_in(visible):
            i = visible.find(word)
            fail(f"表記の約束に反する語「{word}」: …{visible[max(0, i - 25):i + 25]!r}…")

        # --- 生成 AI が作ったページの目印として挙がる型（DESIGN.md §1） ---
        raw = raws[path]
        inline_css += re.findall(r"<style[^>]*>([\s\S]*?)</style>", raw)
        for cls in RETIRED_CLASSES:
            if re.search(r'class="[^"]*(?<![\w-])' + re.escape(cls) + r'(?![\w-])', raw):
                fail(f"やめた型のクラス {cls} が残っている")
        markup = LOGO_SVG.sub("", re.sub(r'<script type="application/ld\+json">[\s\S]*?</script>', "", raw))
        # 本文で色の値を文字として書くのはよい（記事で説明するため）。属性（fill・style など）に書いたものを見る
        if re.search(r'=\s*"[^"]*#7b3a87', markup, re.I):
            fail("ブランドの紫を HTML の属性に直接書いている（使ってよいのはロゴの印だけ）")
        for token in RETIRED_COLORS:
            if re.search(r'=\s*"[^"]*' + token, raw, re.I):
                fail(f"旧ブランド色 {token} が HTML の属性に残っている（ロゴを含む）")
        for tag in re.findall(r"<[a-z]+\b[^>]*\bclass=\"[^\"]*\bsection--sub\b[^\"]*\"[^>]*>", raw):
            if 'id="contact"' not in tag:
                fail(f"灰の地（section--sub）はお問い合わせの節だけ: {tag[:70]!r}")
        if re.search(r"linear-?gradient|radial-?gradient|conic-gradient", markup, re.I):
            fail("HTML にグラデーションがある")
        if path not in MIGRATED:
            if re.search(r'\bstyle="[^"]*font-size', raw):
                fail("HTML の style 属性で文字の大きさを指定している（段の値は CSS で決める）")
            m = EYEBROW.search(raw)
            if m:
                fail(f"見出しの直前に英字だけの小見出しがある: {m.group(0)[:60]!r}")
            for d in DASHES:
                if d in text:
                    i = text.find(d)
                    fail(f"本文にダッシュ「{d}」がある（文章の型の目印。句点や読点で書く）: …{text[max(0, i - 20):i + 20]!r}…")
            for gap in page.jp_gaps[:1]:
                fail(f"句読点のあとに空白がある（ソースの改行が空白になっている）: …{gap}…")
            if "ではなく" in text:
                i = text.find("ではなく")
                notes.append(f"  ⚠ {path} 「〜ではなく」の対句（文章の型の目印になりやすい）: …{text[max(0, i - 20):i + 20]!r}…")
            if re.search(r"[^。]*?も、[^。]*?も、[^。]*?も[、。]", text):
                notes.append(f"  ⚠ {path} 「〜も、〜も、〜も」の三つ並べ（文章の型の目印になりやすい）")
        for url in page.loads:
            if host_matches(host_of(url), "googleapis.com") or host_matches(host_of(url), "gstatic.com"):
                fail(f"閲覧者のブラウザが Google Fonts を直接読みにいく（書体はこのサイトから配る）: {url[:60]}")

        # --- 問い合わせフォーム（受け口へ送る・受け口が保存する欄だけ・送る前に利用目的・迷惑送信の対策） ---
        if re.search(r'<form\b[^>]*\baction="mailto:', raw, re.I):
            fail("フォームの送り先が mailto（メールソフトが無い人は送れない。受け口へ送る）")
        for form in re.findall(r"<form\b[\s\S]*?</form>", raw):
            act = re.search(r'\baction="([^"]+)"', form)
            if not act or not FORM_ACTION.fullmatch(act.group(1)):
                fail(f"フォームの送り先が受け口の形でない: {act.group(1)[:40] if act else '(action が無い)'}")
                continue
            extra = set(re.findall(r'<(?:input|textarea|select)\b[^>]*\bname="([^"]+)"', form)) - FORM_FIELDS
            if extra:
                fail(f"受け口が保存しない欄がある（送っても捨てられる）: {sorted(extra)}")
            if 'name="_hp"' not in form:
                fail("フォームに迷惑送信の罠（_hp）が無い")
            if 'data-sitekey="' not in form or "challenges.cloudflare.com/turnstile" not in raw:
                fail("フォームに迷惑送信の確認（Turnstile）が無い")
            submit_at = form.find('type="submit"')
            privacy_at = form.find('href="/privacy-lp.html"')
            if privacy_at == -1 or (submit_at != -1 and privacy_at > submit_at):
                fail("送信ボタンの前に、利用目的とプライバシーポリシーへのリンクが無い（個人情報保護法 21 条 2 項）")
        header = re.search(r'<header class="site-header"[\s\S]*?</header>', raw)
        if header and 'href="/#lp"' in header.group(0):
            fail("ヘッダーのメニューがトップの料金表（/#lp）を指している（料金は「サービスと料金」のページ）")
        if path != "/" and re.search(r'href="/(?:index\.html)?#contact"', raw):
            fail("お問い合わせへのリンクがトップの節（/#contact）を指している（/contact.html へ）")

        # --- 画像: 代替テキスト・大きさ・ファイルの実在 ---
        for img in page.imgs:
            alt = img.get("alt")
            src = img.get("src", "")
            if alt is None:
                fail(f"代替テキスト（alt）の無い画像: {src[:50]}")
            elif not alt.strip() and img.get("_in_figure"):
                fail(f"図の中の画像の代替テキストが空: {src[:50]}")
            if not (img.get("width", "").isdigit() and img.get("height", "").isdigit()):
                fail(f"画像に幅と高さ（数字）が無い（読み込み中に表示がずれる）: {src[:50]}")
            sp = urlsplit(src)
            if src and not sp.scheme and not src.startswith("data:") and not resolves(dist, path, sp.path):
                fail(f"画像のファイルが無い: {src}")

        # --- 構造化データ ---
        graph_nodes: list[dict] = []
        for raw_ld in page.jsonld:
            try:
                data = json.loads(raw_ld)
            except ValueError as e:
                fail(f"構造化データが JSON として読めない: {e}")
                continue
            nodes = [n for n in (data.get("@graph") or [data]) if isinstance(n, dict)]
            graph_nodes += nodes
            known = {n.get("@id") for n in nodes}
            for ref in sorted(refs_in(data, set()) - known):
                fail(f"構造化データの参照先 {ref} がページの中に無い")
        flat = re.sub(r"\s+", "", text)
        for n in graph_nodes:
            kind = n.get("@type")
            if kind == "ProfessionalService":
                fail("構造化データに ProfessionalService がある（schema.org で非推奨。Organization にする）")
            if kind == "Organization":
                if not str(n.get("telephone", "")).startswith("+81"):
                    fail("構造化データの電話番号に国番号（+81）が無い")
                logo = (n.get("logo") or {}).get("url", "") if isinstance(n.get("logo"), dict) else str(n.get("logo", ""))
                if not logo.endswith("/logo.png"):
                    fail("構造化データのロゴが /logo.png でない")
            for key in ("datePublished", "dateModified"):
                if key in n and not str(n[key]).endswith("+09:00"):
                    fail(f"構造化データの {key} に時差（+09:00）が無い: {n[key]}")
            if kind == "FAQPage":
                for q in n.get("mainEntity", []):
                    for label, value in (("質問", q.get("name", "")), ("答え", (q.get("acceptedAnswer") or {}).get("text", ""))):
                        if re.sub(r"\s+", "", value) not in flat:
                            fail(f"構造化データの FAQ の{label}が画面の文字と一致しない: {value[:40]!r}")
        if path == "/" and not any(n.get("@type") == "WebSite" for n in graph_nodes):
            fail("トップの構造化データに WebSite が無い（検索結果のサイト名）")
        if path == "/contact.html":
            if not any(n.get("@type") == "ContactPage" for n in graph_nodes):
                fail("お問い合わせのページの構造化データに ContactPage が無い")
            points = [n.get("contactPoint") for n in graph_nodes if n.get("contactPoint")]
            if not points or not str(points[0].get("telephone", "")).startswith("+81"):
                fail("構造化データの ContactPoint が無いか、電話番号に国番号（+81）が無い")
        if path == "/contact-thanks.html" and "noindex" not in page.meta.get("robots", ""):
            fail("送信のあとの画面が検索に出る設定になっている（noindex にする）")

        # --- 題名と説明文 ---
        if "エレノア" not in page.title:
            fail(f"<title> に「エレノア」が無い: {page.title!r}")
        if re.search(r"[|｜]\s*Eleanor|[—―–]", page.title):
            fail(f"<title> に古い書き方（| Eleanor）かダッシュがある: {page.title!r}")
        if not ("noindex" in page.meta.get("robots", "")):
            titles.setdefault(page.title.strip(), []).append(path)
            descriptions.setdefault(page.meta.get("description", "").strip(), []).append(path)

        if not page.title.strip():
            fail("<title> が空")
        if len(page.meta.get("description", "")) < 20:
            fail("meta description が無いか短すぎる")
        if page.h1 != 1:
            fail(f"H1 が {page.h1} 個（1個にする）")
        dup = sorted({i for i in page.ids if page.ids.count(i) > 1})
        if dup:
            fail(f"id が重複している: {dup[:3]}")
        beacons = page.scripts.count(BEACON_SRC)
        if beacons != want_beacon and "noindex" not in page.meta.get("robots", ""):
            fail(f"アクセス解析のスクリプトが {beacons} 個（{want_beacon} 個にする）")

        noindex = "noindex" in page.meta.get("robots", "")
        if not noindex and page.canonical != SITE_URL + path:
            fail(f"canonical が {page.canonical!r}（期待値 {SITE_URL + path!r}）")

        ids = set(page.ids)
        for href in page.links:
            parts = urlsplit(href)
            if parts.scheme or href.startswith("//"):
                continue
            if href.startswith("#"):
                if unquote(parts.fragment) not in ids:
                    fail(f"ページ内リンク {href[:40]!r} の行き先（id）が無い")
                continue
            if parts.path and not resolves(dist, path, parts.path):
                fail(f"サイト内リンク切れ: {href}")
            elif parts.path in ("/", "/index.html") and parts.fragment and home and parts.fragment not in home.ids:
                fail(f"トップのページ内リンク {href} の行き先が無い")

        for nav in page.navs:
            names = nav.get("aria-labelledby", "").split()
            if not names and not nav.get("aria-label"):
                fail("名前の無い <nav> がある")
            elif any(n not in ids for n in names):
                fail(f"<nav> の名前（aria-labelledby={' '.join(names)}）の行き先が無い")
        for region in page.regions:
            names = region.get("aria-labelledby", "").split()
            if region.get("role") != "region" or region.get("tabindex") != "0" or not (names or region.get("aria-label")):
                fail("表の枠に role=region / tabindex=0 / 名前（aria-labelledby か aria-label）が揃っていない")
            elif any(n not in ids for n in names):
                fail(f"表の枠の名前（aria-labelledby={' '.join(names)}）の行き先が無い")
        if path in MIGRATED:
            continue
        # --- DADS の約束（新しくつくったページ） ---
        if page.ol:
            fail(f"<ol> が {page.ol} 個ある（DADS: 番号は文字で書く）")
        if not all(page.tables):
            fail(f"横スクロールの枠に入っていない表がある（{page.tables.count(False)} 個）")

    sitemap = "".join(open(p, encoding="utf-8").read() for p in glob.glob(os.path.join(dist, "sitemap-*.xml")))
    for p in ("/", "/services.html", "/company.html", "/products.html", "/blog.html", "/site-policy.html", "/contact.html"):
        if f"<loc>{SITE_URL}{p}</loc>" not in sitemap:
            fails.append(f"  ✗ sitemap に {p} が無い")
    if "/contact-thanks" in sitemap:
        fails.append("  ✗ sitemap に送信のあとの画面（/contact-thanks.html）が載っている")

    for label, table in (("title", titles), ("description", descriptions)):
        for value, where in table.items():
            if len(where) > 1:
                fails.append(f"  ✗ {label} が {len(where)} ページで同じ: {', '.join(where[:4])}（{value[:30]!r}）")

    fails += check_css(dist, inline_css)

    # --- 必要なファイル・ロゴ・llms.txt・robots.txt ---
    for rel in REQUIRED:
        if not os.path.isfile(os.path.join(dist, rel)):
            fails.append(f"  ✗ /{rel} が dist/ に無い")
    logo = os.path.join(dist, "logo.png")
    if os.path.isfile(logo) and min(png_size(logo)) < 112:
        fails.append(f"  ✗ /logo.png が {png_size(logo)}（構造化データのロゴは 112px 以上）")
    ico = os.path.join(dist, "favicon.ico")
    if os.path.isfile(ico) and open(ico, "rb").read(4) != b"\x00\x00\x01\x00":
        fails.append("  ✗ /favicon.ico が ICO の形でない")
    llms = os.path.join(dist, "llms.txt")
    if os.path.isfile(llms):
        body = open(llms, encoding="utf-8").read()
        for slug in draft_slugs(root):
            if f"/blog/{slug}.html" in body:
                fails.append(f"  ✗ /llms.txt に下書きの記事（{slug}）が載っている")
    robots = os.path.join(dist, "robots.txt")
    if os.path.isfile(robots) and re.search(r"^\s*Disallow:\s*/\s*$", open(robots, encoding="utf-8").read(), re.M):
        fails.append("  ✗ robots.txt が全体を拒んでいる（Disallow: /）")

    # --- サイトマップの最終更新日（正しい日付だけ。未来の日付は書かない） ---
    today = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)).date().isoformat()
    for lastmod in re.findall(r"<lastmod>([^<]+)</lastmod>", sitemap):
        if not re.match(r"^\d{4}-\d{2}-\d{2}", lastmod) or lastmod[:10] > today:
            fails.append(f"  ✗ sitemap の lastmod が正しくない: {lastmod}")

    # --- ホスト名・IP アドレスの持ち込み ---
    leak_fails, leak_notes = check_leaks(dist, root)
    fails += leak_fails
    notes += leak_notes

    # --- 見出しの書体（取れなくても公開は止めない。本文と同じ書体で出る） ---
    report_path = os.path.join(root, ".astro", "heading-font.json")
    report = json.load(open(report_path, encoding="utf-8")) if os.path.isfile(report_path) else {}
    if report.get("file"):
        notes.append(f"  · 見出しの書体 {report.get('family')} {report['file']}（{report['bytes'] / 1024:.1f}KB・{report['glyphs']} 字・palt {report.get('palt')}）")
        if report.get("palt") is False:
            fails.append(f"  ✗ 見出しの書体（{report.get('family')}）に字詰め（palt）が無い。見出しは palt を前提に組んでいる")
    else:
        notes.append(f"  ⚠ 見出しの書体を作れなかった（{report.get('error', 'scripts/headings.mjs が走っていない')}）。見出しは本文と同じ書体で出る")

    fails += check_colors(root)
    notes.append(f"  · HTML {len(pages)} ページ・守る URL {len(PROTECTED)} 件・色の組み合わせ {len(CONTRAST)} 通り")
    return fails, notes


def main() -> int:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dist = sys.argv[1] if len(sys.argv) > 1 else os.path.join(root, "dist")
    fails, notes = check(dist, root)
    print("\n=== ビルド出力の検査（dist/） — " + ("❌ 公開しない" if fails else "✅ 合格") + " ===")
    for line in fails + notes:
        print(line)
    print(f"FAIL {len(fails)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
