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
seeds.yaml → Crawl → Extract → Classify → Aggregate → Visualize
```

1. **Crawl** — `seeds.yaml` に記載したURLをクロール（RSS/HTML対応）。robots.txt遵守・ドメイン別レート制限・SQLiteキャッシュ付き
2. **Extract** — trafilaturaでHTML→テキスト変換、正規表現で都道府県を検出
3. **Classify** — キーワード辞書によるルールベース分類（Phase 1）
4. **Aggregate** — 確信度加重で都道府県ごとに集計、Parquet/CSV出力
5. **Visualize** — foliumでコロプレス地図（`outputs/map.html`）を生成

## クイックスタート

```bash
# 1. seeds.yaml にクロール対象URLを記入
# 2. ビルド＆実行
docker compose up app

# GeoJSONダウンロード（地図生成に必要、初回のみ）
docker compose run --rm app python scripts/fetch_geodata.py

# クロールをスキップして集計のみ再実行
docker compose run --rm app python scripts/run_pipeline.py --skip-crawl
```

### seeds.yaml の書き方

```yaml
sources:
  - type: rss
    url: https://example.com/feed
    prefectures: []            # 空なら本文から自動検出

  - type: html
    url: https://example.com/article
    prefectures: ["大阪府"]    # 明示的に都道府県を指定
```

## 実装フェーズ

| フェーズ | 内容 | 状態 |
|---------|------|------|
| Phase 1 | ルールベース分類、フォーカス4都府県（東京・大阪・神奈川・兵庫） | ✅ 実装済み |
| Phase 2 | キーワード辞書の充実、否定表現対応（「〜ではなく」検出） | 未着手 |
| Phase 3 | 全47都道府県展開、Playwright対応 | 未着手 |

## 必要環境

- Docker
- （Phase 2以降）GPU: VRAM 16GB × 2

## ライセンス

MIT
