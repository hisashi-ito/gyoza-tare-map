# Condiment Labels

## Label Definitions

| Label                | 日本語名          | Description                                                       |
|----------------------|-------------------|-------------------------------------------------------------------|
| `prepared_tare`      | 付属タレ          | Pre-made bottled or house-made sauce served with the gyoza        |
| `self_mix_soy_vinegar` | 酢醤油（自作）  | Customer mixes soy sauce and vinegar at the table themselves      |
| `miso_dare`          | 味噌だれ          | Miso-based dipping sauce                                          |
| `other_local_style`  | その他地域スタイル | Regional variants (mayo, yuzu pepper, sesame sauce, etc.)        |
| `unknown`            | 不明              | No condiment mention, or confidence too low (< 0.3)              |

## Keyword Lists (Phase 1 Rule Classifier)

See `src/gyoza_tare_map/classify/labels.py` for the full keyword dictionaries.

### `prepared_tare`
タレ、たれ、付属のたれ、付属タレ、専用タレ、秘伝のタレ、ラー油、辣油、ポン酢、特製タレ、オリジナルタレ …

### `self_mix_soy_vinegar`
自分で酢醤油、自分でかける、酢と醤油、酢醤油を作、酢醤油で食べ、卓上酢、自分で割る …

### `miso_dare`
味噌だれ、みそだれ、味噌タレ、名古屋の味噌、赤味噌、八丁味噌 …

### `other_local_style`
マヨネーズ、ゆずこしょう、ごまだれ、ねぎ塩、塩だれ、生姜醤油、ニンニク醤油 …

## Ambiguity Notes

- `酢醤油` alone is ambiguous: it can be `prepared_tare` (bottled soy-vinegar sauce) or `self_mix_soy_vinegar` (mixing yourself). Context phrases like `自分で` or `卓上` resolve the ambiguity.
- Records where the top-2 label scores differ by ≤ 0.1 are flagged `ambiguous: true` in ClassifiedRecord.
- Phase 2 LLM classification is intended to resolve ambiguous cases.
