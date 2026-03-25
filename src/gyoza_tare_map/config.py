from pathlib import Path

# --- Paths ---
ROOT = Path(__file__).parent.parent.parent
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
EXTRACTED_DIR = DATA_DIR / "extracted"
CLASSIFIED_DIR = DATA_DIR / "classified"
GEO_DIR = DATA_DIR / "geo"
OUTPUTS_DIR = ROOT / "outputs"
DOCS_DIR = ROOT / "docs"

CACHE_DB = DATA_DIR / "cache.db"
SEEDS_FILE = ROOT / "seeds.yaml"

RAW_JSONL = RAW_DIR / "documents.jsonl"
EXTRACTED_JSONL = EXTRACTED_DIR / "snippets.jsonl"
CLASSIFIED_JSONL = CLASSIFIED_DIR / "records.jsonl"
PREFECTURE_GEOJSON = GEO_DIR / "N03_prefecture.geojson"
OUTPUT_PARQUET = OUTPUTS_DIR / "evidence.parquet"
OUTPUT_CSV = OUTPUTS_DIR / "evidence.csv"
OUTPUT_MAP = OUTPUTS_DIR / "map.html"

# --- Labels ---
LABELS = [
    "prepared_tare",
    "self_mix_soy_vinegar",
    "miso_dare",
    "other_local_style",
    "unknown",
]

# --- Prefectures ---
PHASE1_PREFECTURES = ["東京都", "大阪府", "神奈川県", "兵庫県"]

ALL_PREFECTURES = [
    "北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県",
    "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県",
    "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県",
    "岐阜県", "静岡県", "愛知県", "三重県",
    "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県",
    "鳥取県", "島根県", "岡山県", "広島県", "山口県",
    "徳島県", "香川県", "愛媛県", "高知県",
    "福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県",
]

# --- Crawl Policy ---
DEFAULT_CRAWL_DELAY_SEC = 3.0   # minimum seconds between requests per domain
MAX_CONCURRENT_DOMAINS = 5      # max simultaneous domains
REQUEST_TIMEOUT_SEC = 30
CACHE_TTL_DAYS = 7

# --- Classification ---
MIN_CONFIDENCE = 0.3            # records below this threshold become "unknown"
AMBIGUOUS_MARGIN = 0.1          # top-2 label score within this → ambiguous=True
MAX_RULE_CONFIDENCE = 0.95      # cap for rule-based classifier
