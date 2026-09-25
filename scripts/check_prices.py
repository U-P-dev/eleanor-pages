#!/usr/bin/env python3
"""料金表の元データ（src/data/prices.json）と、LP 事業の料金の正本（jido-lp-sales/config/pricing.json）の照合。

このサイトの `#lp` の料金表は、Stripe の審査で「サイトに載っている商品＝請求する商品」を確かめられる場所。
正本は非公開リポジトリにあり、値引きの段階や最低単価など公開しない値も持っているので、そのまま写さない。
公開してよい項目（名前・価格・請求の単位・納期・含まれるもの・説明）だけを抜き出して src/data/prices.json に置く。

  python3 scripts/check_prices.py          # 照合（ずれていれば exit 1）。正本が隣に無ければ何もせず exit 0
  python3 scripts/check_prices.py --write  # 正本から抜き出して src/data/prices.json を書き直す
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "src", "data", "prices.json")
SOURCE = os.path.join(os.path.dirname(ROOT), "jido-lp-sales", "config", "pricing.json")

# 区分ごとに公開する項目。ここに無い項目（内部の注記・判定条件など）は写さない
FIELDS = {
    "plans": ("name", "price", "delivery_days", "includes"),
    "fullorder": ("name", "price", "delivery_days", "included_pages", "extra_page_price", "includes"),
    "subscriptions": ("name", "price", "billing", "description"),
    "addons": ("name", "price", "billing", "description"),
    # スポットの description には内部の参照が混じるので名前と価格だけ
    "spot": ("name", "price", "delivery_days"),
}


def extract(pricing: dict) -> dict:
    out: dict = {}
    for section, fields in FIELDS.items():
        rows = {}
        for key, row in pricing[section].items():
            if key.startswith("_") or not isinstance(row, dict):
                continue
            if row.get("sales_status") == "stopped" or row.get("price") is None:
                continue
            rows[key] = {f: row[f] for f in fields if f in row}
        out[section] = rows
    out["tax_included"] = bool(pricing["tax"]["included"])
    out["tax_rate"] = pricing["tax"]["rate"]
    out["payment_methods"] = [pricing["payment"]["method_labels"][m] for m in pricing["payment"]["methods"]]
    out["payment_timing"] = pricing["payment"]["timing"]
    out["pre_delivery_revisions"] = pricing["revision_policy"]["pre_delivery"]
    out["revision_turnaround"] = pricing["revision_policy"]["turnaround"]
    out["refund_window_hours"] = pricing["terms"]["refund_window_hours"]
    # 保守の解約の条件と、解約後に LP と独自ドメインを引き渡すか（差額の金額は plans から計算する。ここに金額を持たない）
    out["subscription_cancellation"] = pricing["terms"]["subscription_cancellation"]
    out["buyout_includes_domain"] = bool(pricing["buyout"].get("includes_domain"))
    # 後払い（掛売り）を受けるか・インボイスの登録の状態（会社概要とよくある質問に出す。番号は登録が済んだら正本に入る）
    out["credit_terms"] = bool(pricing["payment"].get("credit_terms", False))
    out["invoice_registered"] = bool(pricing["invoice"].get("registered"))
    out["invoice_number"] = str(pricing["invoice"].get("registration_number") or "")
    return out


def main() -> int:
    if not os.path.isfile(SOURCE):
        print(f"料金の正本が見つからないので照合を省略: {SOURCE}")
        return 0
    with open(SOURCE, encoding="utf-8") as f:
        want = extract(json.load(f))
    if "--write" in sys.argv:
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(want, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(f"書き出した: {os.path.relpath(OUT, ROOT)}")
        return 0
    with open(OUT, encoding="utf-8") as f:
        have = json.load(f)
    if have == want:
        print("✅ 料金表の元データは正本と一致")
        return 0
    print("❌ src/data/prices.json が正本と違う。`python3 scripts/check_prices.py --write` で書き直してから、差分を確かめてコミットする")
    for section in sorted(set(want) | set(have)):
        if want.get(section) != have.get(section):
            print(f"  ✗ {section}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
