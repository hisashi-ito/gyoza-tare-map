#!/usr/bin/env python3
"""One-time script to download prefecture boundary GeoJSON from the National Land Numerical Info.

Usage:
    python scripts/fetch_geodata.py
"""
import sys
import urllib.request
from pathlib import Path
import zipfile
import io

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from gyoza_tare_map.config import GEO_DIR, PREFECTURE_GEOJSON

# N03 Administrative Boundary (2024) — GeoJSON version from GitHub mirror
# Original source: https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-v3_1.html
GEOJSON_URL = "https://raw.githubusercontent.com/dataofjapan/land/master/japan.geojson"


def main() -> None:
    GEO_DIR.mkdir(parents=True, exist_ok=True)
    if PREFECTURE_GEOJSON.exists():
        print(f"Already exists: {PREFECTURE_GEOJSON}")
        return

    print(f"Downloading GeoJSON from {GEOJSON_URL} ...")
    urllib.request.urlretrieve(GEOJSON_URL, PREFECTURE_GEOJSON)
    print(f"Saved → {PREFECTURE_GEOJSON}")
    print("Note: This GeoJSON uses 'name' as the prefecture property key.")
    print("Update choropleth.py key_on if your GeoJSON uses a different property.")


if __name__ == "__main__":
    main()
