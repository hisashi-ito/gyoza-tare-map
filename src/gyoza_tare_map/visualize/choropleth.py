"""Generate a folium choropleth map colored by dominant gyoza condiment label."""
from __future__ import annotations

import json
from pathlib import Path

import folium
import pandas as pd

from gyoza_tare_map.config import OUTPUT_MAP, PREFECTURE_GEOJSON

# Map each label to a display color
LABEL_COLORS: dict[str, str] = {
    "prepared_tare": "#e74c3c",       # red
    "self_mix_soy_vinegar": "#3498db", # blue
    "miso_dare": "#e67e22",            # orange
    "su_kosho": "#9b59b6",             # purple
    "other_local_style": "#2ecc71",    # green
    "unknown": "#bdc3c7",              # grey
}

LABEL_NAMES_JA: dict[str, str] = {
    "prepared_tare": "付属タレ",
    "self_mix_soy_vinegar": "酢醤油（自作）",
    "miso_dare": "味噌だれ",
    "su_kosho": "酢コショウ",
    "other_local_style": "その他",
    "unknown": "不明",
}


def build_map(
    df: pd.DataFrame,
    geojson_path: Path = PREFECTURE_GEOJSON,
    output_path: Path = OUTPUT_MAP,
    dry_run: bool = False,
) -> folium.Map:
    if not geojson_path.exists():
        raise FileNotFoundError(
            f"GeoJSON not found: {geojson_path}\nRun: python scripts/fetch_geodata.py"
        )

    m = folium.Map(location=[36.5, 137.5], zoom_start=5, tiles="CartoDB positron")

    # Build lookup: prefecture name → (color, label_ja, evidence_count, low_evidence)
    pref_info: dict[str, dict] = {}
    for _, row in df.iterrows():
        label = row["dominant_label"]
        pref_info[row["prefecture"]] = {
            "color": LABEL_COLORS.get(label, "#cccccc"),
            "label_ja": LABEL_NAMES_JA.get(label, label),
            "evidence_count": int(row["evidence_count"]),
            "low_evidence": bool(row["low_evidence"]),
        }

    geojson_data = json.loads(geojson_path.read_text(encoding="utf-8"))

    def style_function(feature: dict) -> dict:
        name = feature["properties"].get("nam_ja", "")
        info = pref_info.get(name)
        color = info["color"] if info else "#eeeeee"
        return {
            "fillColor": color,
            "fillOpacity": 0.75,
            "color": "#555555",
            "weight": 0.5,
        }

    def tooltip_fn(feature: dict) -> str:
        name = feature["properties"].get("nam_ja", "")
        info = pref_info.get(name)
        if not info:
            return f"<b>{name}</b><br>データなし"
        low = " ⚠低証拠" if info["low_evidence"] else ""
        return (
            f"<b>{name}</b><br>"
            f"スタイル: {info['label_ja']}{low}<br>"
            f"証拠数: {info['evidence_count']}"
        )

    folium.GeoJson(
        geojson_data,
        name="gyoza-tare",
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(
            fields=["nam_ja"],
            aliases=["都道府県"],
            localize=True,
        ),
    ).add_to(m)

    # Color legend as HTML overlay
    legend_html = _legend_html(df)
    m.get_root().html.add_child(folium.Element(legend_html))

    folium.LayerControl().add_to(m)

    if not dry_run:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        m.save(str(output_path))
        print(f"[map] Saved → {output_path}")

    return m


def _legend_html(df: pd.DataFrame | None = None) -> str:
    # Only show labels that actually appear in the data
    if df is not None:
        used_labels = set(df["dominant_label"].tolist())
    else:
        used_labels = set(LABEL_COLORS.keys())
    # Always show uncovered
    items = "".join(
        f'<li><span style="background:{color};display:inline-block;width:14px;height:14px;'
        f'border-radius:3px;margin-right:6px;"></span>{LABEL_NAMES_JA[label]}</li>'
        for label, color in LABEL_COLORS.items()
        if label in used_labels
    )
    # Add "no data" entry
    items += (
        '<li><span style="background:#eeeeee;display:inline-block;width:14px;height:14px;'
        'border-radius:3px;margin-right:6px;border:1px solid #ccc;"></span>データなし</li>'
    )
    return f"""
    <div style="position:fixed;bottom:40px;left:40px;z-index:1000;background:white;
                padding:12px 16px;border-radius:6px;box-shadow:2px 2px 6px rgba(0,0,0,0.3);
                font-family:sans-serif;font-size:13px;">
      <b>餃子のたれスタイル</b>
      <ul style="list-style:none;padding:0;margin:8px 0 0 0;">{items}</ul>
    </div>
    """
