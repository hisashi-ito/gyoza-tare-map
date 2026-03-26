# gyoza-tare-map

日本全国の餃子のたれ文化を、ウェブ上の公開データから推定・可視化するデータパイプラインです。

## 概要

ブログ記事・グルメサイト等のテキストから「餃子をどんなたれで食べるか」を都道府県ごとに集計し、インタラクティブな地図として出力します。

### たれラベル

| ラベル | 説明 |
|--------|------|
| `prepared_tare` | 付属・特製タレ（店が用意したたれ） |
| `self_mix_soy_vinegar` | 酢醤油の自作（卓上で自分で割る） |
| `miso_dare` | 味噌だれ |
| `su_kosho` | 酢コショウ（酢に胡椒をふる食べ方） |
| `other_local_style` | その他地域スタイル（マヨ・ゆずこしょう等） |
| `unknown` | 該当なし・信頼度不足 |

## パイプライン

```
Discover → seeds.yaml → Crawl → Extract → Classify → Aggregate → Visualize
```

### 0. Discover（URL自動発見）

**はてなブックマーク検索RSS** を使い、クロール対象URLを自動収集します。APIキー不要・無料。

```bash
# Phase 1 の4都府県を検索して seeds.yaml に自動追記
docker compose run --rm app python scripts/discover_seeds.py --auto-append

# 全47都道府県を対象に検索（時間がかかる）
docker compose run --rm app python scripts/discover_seeds.py --all-prefectures --auto-append

# 候補を確認してから手動で追記する場合
docker compose run --rm app python scripts/discover_seeds.py --prefectures 福岡県 広島県
```

- 1クエリあたり最大5ページ（200件）取得
- タイトルに餃子キーワードを含まない記事は自動除外
- 既に `seeds.yaml` に登録済みのURLは重複追加しない

### 1–5. Crawl → Visualize

```
seeds.yaml → Crawl → Extract → Classify → Aggregate → Visualize
```

1. **Crawl** — `seeds.yaml` のURLをクロール（RSS/HTML対応）。robots.txt遵守・ドメイン別レート制限（3秒）・SQLiteキャッシュ（7日TTL）
2. **Extract** — trafilaturaでHTML→テキスト変換、正規表現で都道府県を検出。餃子キーワードを含まない記事は除外
3. **Classify** — キーワード辞書によるルールベース分類。NFKC正規化後にキーワード出現回数を集計し、割合でラベルを決定
4. **Aggregate** — 確信度加重で都道府県ごとに集計、Parquet/CSV出力
5. **Visualize** — foliumでコロプレス地図（`outputs/map.html`）を生成

## クイックスタート

```bash
# 初回セットアップ
docker compose run --rm app python scripts/fetch_geodata.py   # GeoJSONダウンロード
docker compose run --rm app python scripts/discover_seeds.py --all-prefectures --auto-append

# フルパイプライン実行
docker compose up app

# クロールをスキップして再集計のみ
docker compose run --rm app python scripts/run_pipeline.py --skip-crawl

# ドライラン（ファイル書き込みなし）
docker compose run --rm app python scripts/run_pipeline.py --dry-run
```

### seeds.yaml の書き方

`discover_seeds.py` で自動生成されますが、手動追加も可能です。

```yaml
sources:
  - type: rss
    url: https://example.com/feed
    prefectures: []            # 空なら本文から自動検出

  - type: html
    url: https://example.com/article
    prefectures: ["大阪府"]    # 明示的に都道府県を指定
```

## 分類器の評価

ラベル付きテストセット（`tests/classifier_testset.yaml`）に対して precision / recall / F1 を計算します。

```bash
docker compose run --rm app python scripts/evaluate_classifier.py --verbose
```

現在の評価結果（macro avg）：Precision 0.979 / Recall 0.981 / F1 0.979

キーワードを追加・変更したら必ず実行してリグレッションがないか確認してください。

## 分類ロジック（Phase 1）

`classify/labels.py` のキーワード辞書を使ったルールベース分類。

```
1. テキストをNFKC正規化
2. 各ラベルのキーワードが何回出現するか count()
3. 全ヒット数で割って正規化（割合に変換）
4. 最大割合のラベルを採用
   - confidence = min(割合, 0.95)
   - 上位2ラベルの差 ≤ 0.1 → ambiguous = True
   - confidence < 0.3 → unknown
```

キーワードの追加は `classify/labels.py` を編集するだけです。

## 実装フェーズ

| フェーズ | 内容 | 状態 |
|---------|------|------|
| Phase 1 | ルールベース分類・はてなブックマーク検索でURL自動発見・4都府県フォーカス | ✅ 実装済み |
| Phase 2 | キーワード辞書の充実、否定表現対応（「〜ではなく」検出） | 着手中 |
| Phase 3 | 全47都道府県展開、Playwright対応 | 未着手 |

## 必要環境

- Docker

## ライセンス

MIT
