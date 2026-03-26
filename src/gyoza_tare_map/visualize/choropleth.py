"""Generate a folium choropleth map colored by dominant gyoza condiment label."""
from __future__ import annotations

from pathlib import Path

import folium
import pandas as pd

from gyoza_tare_map.config import OUTPUT_MAP, PREFECTURE_GEOJSON

# Map each label to a display color
LABEL_COLORS: dict[str, str] = {
    "prepared_tare": "#e74c3c",       # red
    "self_mix_soy_vinegar": "#3498db", # blue
    "miso_dare": "#e67e22",            # orange
    "other_local_style": "#2ecc71",    # green
    "unknown": "#bdc3c7",              # grey
}

LABEL_NAMES_JA: dict[str, str] = {
    "prepared_tare": "付属タレ",
    "self_mix_soy_vinegar": "酢醤油（自作）",
    "miso_dare": "味噌だれ",
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

    # Encode dominant_label as integer for choropleth color scale
    label_order = list(LABEL_COLORS.keys())
    df = df.copy()
    df["label_code"] = df["dominant_label"].apply(
        lambda l: label_order.index(l) if l in label_order else len(label_order)
    )

    folium.Choropleth(
        geo_data=str(geojson_path),
        name="gyoza-tare",
        data=df,
        columns=["prefecture", "label_code"],
        key_on="feature.properties.nam_ja",
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=0.3,
        legend_name="餃子のたれスタイル（コード）",
        nan_fill_color="#eeeeee",
    ).add_to(m)

    # Add tooltip with human-readable info
    style_function = lambda _: {"fillOpacity": 0, "weight": 0}
    tooltip_data = {
        row["prefecture"]: {
            "label": LABEL_NAMES_JA.get(row["dominant_label"], row["dominant_label"]),
            "count": int(row["evidence_count"]),
            "low": bool(row["low_evidence"]),
        }
        for _, row in df.iterrows()
    }

    # Color legend as HTML overlay
    legend_html = _legend_html()
    m.get_root().html.add_child(folium.Element(legend_html))

    folium.LayerControl().add_to(m)

    if not dry_run:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        m.save(str(output_path))
        print(f"[map] Saved → {output_path}")

    return m


def _legend_html() -> str:
    items = "".join(
        f'<li><span style="background:{color};display:inline-block;width:14px;height:14px;margin-right:6px;"></span>{LABEL_NAMES_JA[label]}</li>'
        for label, color in LABEL_COLORS.items()
    )
    return f"""
    <div style="position:fixed;bottom:40px;left:40px;z-index:1000;background:white;
                padding:12px 16px;border-radius:6px;box-shadow:2px 2px 6px rgba(0,0,0,0.3);
                font-family:sans-serif;font-size:13px;">
      <b>餃子のたれスタイル</b>
      <ul style="list-style:none;padding:0;margin:8px 0 0 0;">{items}</ul>
    </div>
    """
