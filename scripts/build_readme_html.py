"""Render README.md → docs/index.html as a styled snapshot."""
from __future__ import annotations

import datetime
from pathlib import Path

import markdown

ROOT = Path(__file__).parent.parent

# When running inside Docker, README is at the repo root (mounted as volume or baked in)
_candidates = [ROOT / "README.md", Path("/app/README.md"), Path("README.md")]
README = next((p for p in _candidates if p.exists()), ROOT / "README.md")
OUTPUT = ROOT / "docs" / "index.html"

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
  background: #0d1117;
  color: #e6edf3;
  line-height: 1.7;
  padding: 2rem 1rem 4rem;
}

.container {
  max-width: 860px;
  margin: 0 auto;
}

/* Header accent */
h1 {
  font-size: 2.4rem;
  font-weight: 800;
  background: linear-gradient(90deg, #f97316, #ec4899, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.4rem;
}

h2 {
  font-size: 1.4rem;
  font-weight: 700;
  color: #58a6ff;
  margin: 2.4rem 0 0.8rem;
  padding-bottom: 0.3rem;
  border-bottom: 1px solid #21262d;
}

h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #79c0ff;
  margin: 1.6rem 0 0.5rem;
}

p { margin: 0.6rem 0; color: #c9d1d9; }

blockquote {
  border-left: 3px solid #f97316;
  padding: 0.4rem 1rem;
  margin: 0.8rem 0;
  color: #8b949e;
  font-style: italic;
}

/* Tables */
table {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
  font-size: 0.9rem;
}

th {
  background: #161b22;
  color: #8b949e;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.05em;
  padding: 0.6rem 0.8rem;
  text-align: left;
  border-bottom: 1px solid #21262d;
}

td {
  padding: 0.55rem 0.8rem;
  border-bottom: 1px solid #161b22;
  color: #c9d1d9;
}

tr:hover td { background: #161b22; }

/* Code */
code {
  font-family: "SF Mono", "Fira Code", "Cascadia Code", monospace;
  font-size: 0.85em;
  background: #161b22;
  color: #f97316;
  padding: 0.15em 0.4em;
  border-radius: 4px;
  border: 1px solid #21262d;
}

pre {
  background: #161b22;
  border: 1px solid #21262d;
  border-radius: 8px;
  padding: 1.1rem 1.2rem;
  overflow-x: auto;
  margin: 1rem 0;
  line-height: 1.55;
}

pre code {
  background: none;
  border: none;
  padding: 0;
  color: #c9d1d9;
  font-size: 0.88rem;
}

/* Pipeline diagram */
pre:has(code:first-child:not([class])) {
  border-left: 3px solid #8b5cf6;
}

/* HR */
hr {
  border: none;
  border-top: 1px solid #21262d;
  margin: 2rem 0;
}

/* Lists */
ul, ol { padding-left: 1.4rem; margin: 0.5rem 0; color: #c9d1d9; }
li { margin: 0.25rem 0; }

/* Badge strip at the top */
.meta {
  font-size: 0.78rem;
  color: #484f58;
  margin-top: 0.5rem;
  margin-bottom: 2rem;
}

.badge {
  display: inline-block;
  background: #21262d;
  border: 1px solid #30363d;
  border-radius: 20px;
  padding: 2px 10px;
  font-size: 0.75rem;
  color: #8b949e;
  margin-right: 6px;
}

.badge.green { border-color: #238636; color: #3fb950; }
.badge.orange { border-color: #9e6a03; color: #d29922; }
.badge.purple { border-color: #6e40c9; color: #a371f7; }

a { color: #58a6ff; text-decoration: none; }
a:hover { text-decoration: underline; }
"""

TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>gyoza-tare-map</title>
  <style>{css}</style>
</head>
<body>
<div class="container">
  <div class="meta">
    <span class="badge green">38 / 47 prefectures</span>
    <span class="badge orange">Phase 3 in progress</span>
    <span class="badge purple">MIT License</span>
    <span style="margin-left:8px">Snapshot: {date}</span>
  </div>
  {body}
</div>
</body>
</html>
"""


def main() -> None:
    md_text = README.read_text(encoding="utf-8")

    md = markdown.Markdown(
        extensions=["tables", "fenced_code", "toc"],
    )
    body = md.convert(md_text)

    html = TEMPLATE.format(
        css=CSS,
        body=body,
        date=datetime.date.today().isoformat(),
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"[build] Rendered → {OUTPUT}")


if __name__ == "__main__":
    main()
