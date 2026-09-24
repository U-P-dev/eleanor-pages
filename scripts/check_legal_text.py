#!/usr/bin/env python3
"""移したページ9枚の本文が、旧サイトの版と一字も違わないかを確かめる。

アプリストアの掲載情報・アプリ内のリンク・決済画面から参照されているページなので、枠を作り替えても本文は変えない。
比べるのは「旧サイトの <div class="container"> の中の文字」と「dist/ の <div class="legal"> の中の文字」（空白は詰める）。

使い方: python3 scripts/check_legal_text.py   （先に npm run build）
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "13413b1"  # 作り直す直前の旧サイト
# 基準から意図して直した箇所（旧サイトの文字 → 今の文字）。ここに無い違いは失敗にする
INTENDED = {
    # 2026-09-24 👤 承認: どのプランにも無い「1〜3営業日」を、特定商取引法に基づく表示と料金データに合わせた
    # （日数が料金データの最短・最長と合っているかは scripts/check_prices.py が見る）
    "thanks.html": [("1〜3営業日で制作したページ", "1〜2営業日（フルオーダーは10〜20営業日）で制作したページ")],
}
PAGES = ["privacy.html", "support.html", "account-deletion.html", "privacy-hitomoyou.html", "terms-hitomoyou.html",
         "tokusho-hitomoyou.html", "support-hitomoyou.html", "thanks.html", "cancel.html"]


class Text(HTMLParser):
    """start_attr の要素の中の文字だけを集める"""

    def __init__(self, cls: str) -> None:
        super().__init__(convert_charrefs=True)
        self.cls = cls
        self.depth = 0
        self.out: list[str] = []

    def handle_starttag(self, tag, attrs):
        if self.depth:
            if tag not in ("br", "hr", "img", "input", "meta", "link"):
                self.depth += 1
        elif tag == "div" and self.cls in (dict(attrs).get("class") or "").split():
            self.depth = 1

    def handle_endtag(self, tag):
        if self.depth:
            self.depth -= 1

    def handle_data(self, data):
        if self.depth:
            self.out.append(data)


def text_of(html: str, cls: str) -> str:
    p = Text(cls)
    p.feed(html)
    return re.sub(r"\s+", " ", "".join(p.out)).strip()


def main() -> int:
    fails = []
    for name in PAGES:
        old = subprocess.run(["git", "-C", ROOT, "show", f"{BASE}:{name}"], capture_output=True, text=True, check=True).stdout
        new_path = os.path.join(ROOT, "dist", name)
        if not os.path.isfile(new_path):
            fails.append(f"  ✗ {name}: dist に無い（ビルドしていないか、ページが消えた）")
            continue
        a = text_of(old, "container")
        for before, after in INTENDED.get(name, []):
            if a.count(before) != 1:
                fails.append(f"  ✗ {name}: 意図して直した箇所が旧サイトの本文に1つだけ無い（{before!r}）")
            a = a.replace(before, after)
        b = text_of(open(new_path, encoding="utf-8").read(), "legal")
        if not a:
            fails.append(f"  ✗ {name}: 旧サイトの本文が取れない")
        elif a != b:
            i = next((k for k in range(min(len(a), len(b))) if a[k] != b[k]), min(len(a), len(b)))
            fails.append(f"  ✗ {name}: 本文が違う（{i} 文字目）旧 …{a[max(0, i - 20):i + 20]!r}… 新 …{b[max(0, i - 20):i + 20]!r}…")
    print("=== 移したページの本文の照合 — " + ("❌" if fails else f"✅ {len(PAGES)} 枚とも一致") + " ===")
    for f in fails:
        print(f)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
