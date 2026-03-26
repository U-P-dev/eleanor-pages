# jido-lp-sales インフラ構成

> **概要**: LP/HP を持たない都内事業者への LP 制作営業〜納品〜保守を全自動化するシステム
> **リポジトリ**: `C:\Projects\jido-lp-sales\`
> **ステータス**: 開発中（ローカル Python スクリプト）

---

## 実行環境

| 項目 | 値 |
|---|---|
| 言語 | Python |
| 実行方式 | ローカルスクリプト（クラウドデプロイなし） |
| 仮想環境 | `.venv/` |

---

## 起動方法

```bash
python scripts/main.py          # 通常起動
python scripts/health_check.py  # ヘルスチェックのみ
```

---

## 外部サービス（予定）

| サービス | 用途 |
|---|---|
| Claude API | LP コンテンツ自動生成（予定） |

詳細構成: `docs/architecture.md`（プロジェクト内）
