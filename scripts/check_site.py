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

このほかの言葉づかいの検査は、非公開の運用リポジトリから dist/ を調べる。

使い方: python3 scripts/check_site.py [dist ディレクトリ]
"""
from __future__ import annotations

import glob
import os
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
    "fonts.googleapis.com": "Google LLC",
    "fonts.gstatic.com": "Google LLC",
}
POLICY_PATH = "/site-policy.html"

# 色の組み合わせ（前景, 背景, 最低比, どこで使っているか）。値は src/styles/tokens.css の変数名で引く
WHITE, GRAY50, TINT = "color-neutral-white", "color-neutral-solid-gray-50", "color-primitive-purple-50"
CONTRAST = [
    ("color-neutral-solid-gray-800", WHITE, 4.5, "本文"),
    ("color-neutral-solid-gray-800", GRAY50, 4.5, "灰の地の本文・フッター"),
    ("color-neutral-solid-gray-800", TINT, 4.5, "紫の地の本文"),
    ("color-neutral-solid-gray-900", WHITE, 4.5, "見出し"),
    ("color-neutral-solid-gray-900", GRAY50, 4.5, "灰の地の見出し"),
    ("color-neutral-solid-gray-900", TINT, 4.5, "紫の地の見出し"),
    ("color-neutral-solid-gray-700", WHITE, 4.5, "リード文・表の注記"),
    ("color-neutral-solid-gray-700", GRAY50, 4.5, "灰の地の表の注記"),
    ("color-neutral-solid-gray-600", WHITE, 4.5, "日付・フォームの補足"),
    ("color-neutral-solid-gray-600", GRAY50, 4.5, "灰の地のフォームの補足・©"),
    ("color-primitive-purple-900", WHITE, 4.5, "見出しの上の小見出し・アウトラインのボタン"),
    ("color-primitive-purple-900", GRAY50, 4.5, "灰の地の小見出し"),
    ("color-primitive-purple-900", TINT, 4.5, "紫の地の小見出し"),
    ("color-primitive-purple-1000", TINT, 4.5, "アウトラインのボタン（ホバー）"),
    (WHITE, "color-brand-violet", 4.5, "塗りのボタン"),
    (WHITE, "color-primitive-purple-900", 4.5, "塗りのボタン（ホバー）・手順の番号"),
    (WHITE, "color-primitive-purple-1000", 4.5, "塗りのボタン（押下）"),
    (WHITE, "color-primitive-magenta-900", 4.5, "ファーストビューの文字（グラデーションの赤側）"),
    (WHITE, "color-primitive-blue-1000", 4.5, "ファーストビューの文字（グラデーションの青側）"),
    ("color-primitive-purple-900", WHITE, 4.5, "ファーストビューの白いボタンの文字"),
    ("color-error-2", WHITE, 4.5, "「※必須」・エラー"),
    ("color-error-2", GRAY50, 4.5, "灰の地の「※必須」・エラー"),
    ("color-primitive-blue-1000", WHITE, 4.5, "リンク"),
    ("color-primitive-blue-1000", GRAY50, 4.5, "灰の地のリンク"),
    ("color-primitive-blue-1000", TINT, 4.5, "紫の地のリンク"),
    ("color-primitive-magenta-900", WHITE, 4.5, "訪問済みのリンク"),
    ("color-primitive-magenta-900", GRAY50, 4.5, "灰の地の訪問済みリンク"),
    ("color-primitive-magenta-900", TINT, 4.5, "紫の地の訪問済みリンク"),
    ("color-primitive-blue-900", WHITE, 4.5, "ホバー中のリンク"),
    ("color-primitive-orange-800", WHITE, 4.5, "押している間のリンク"),
    ("color-primitive-blue-1000", "color-primitive-yellow-300", 4.5, "フォーカス中のリンク（黄色の地）"),
    ("color-primitive-magenta-900", "color-primitive-yellow-300", 4.5, "フォーカス中の訪問済みリンク"),
    ("color-neutral-solid-gray-420", WHITE, 3.0, "白の地の罫線・カードの枠"),
    ("color-neutral-solid-gray-536", GRAY50, 3.0, "灰の地のカードの枠"),
    ("color-neutral-solid-gray-536", TINT, 3.0, "紫の地のカードの枠"),
    ("color-neutral-solid-gray-600", WHITE, 3.0, "入力欄の枠"),
    ("color-primitive-yellow-900", WHITE, 3.0, "注意の枠"),
    ("color-neutral-black", WHITE, 3.0, "フォーカスの黒線"),
]
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
        self._stack: list[tuple[str, set[str]]] = []

    def _inside(self, cls: str) -> bool:
        return any(cls in classes for _, classes in self._stack)

    def handle_starttag(self, tag, attrs):
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
        if tag == "table":
            self.tables.append(self._inside("table-region"))
        if "table-region" in classes:
            self.regions.append(a)
        if tag == "nav":
            self.navs.append(a)
        if tag not in VOID:
            self._stack.append((tag, classes))

    def handle_endtag(self, tag):
        if any(t == tag for t, _ in self._stack):
            while self._stack and self._stack.pop()[0] != tag:
                pass

    def handle_data(self, data):
        if not self._stack:
            return
        tags = [t for t, _ in self._stack]
        if tags[-1] == "title":
            self.title += data
        elif "script" not in tags and "style" not in tags:
            self.text.append(data)

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
    for html_path in pages:
        if url_path(dist, html_path) in NOT_PAGES:
            continue
        page = Page()
        page.feed(open(html_path, encoding="utf-8").read())
        parsed[url_path(dist, html_path)] = page
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
    for p in ("/", "/services.html", "/company.html", "/products.html", "/blog.html", "/site-policy.html"):
        if f"<loc>{SITE_URL}{p}</loc>" not in sitemap:
            fails.append(f"  ✗ sitemap に {p} が無い")

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
