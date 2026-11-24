import os
import re
from datetime import datetime

CONTENT_DIR = "content"
PUB_DIR = os.path.join(CONTENT_DIR, "publications")
INDEX_FILE = os.path.join(CONTENT_DIR, "index.md")

FILENAME_PATTERN = re.compile(r"^(en|ru|fr|es)_(\d{2}-\d{2}-\d{4})_(.+)\.md$", re.IGNORECASE)

def extract_title(filepath, fallback):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    match = re.search(r"^---\s*.*?^title:\s*[\"']?(.*?)[\"']?\s*$.*?^---", text, re.MULTILINE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return fallback

def build_index():
    os.makedirs(PUB_DIR, exist_ok=True)
    articles = []

    for filename in os.listdir(PUB_DIR):
        match = FILENAME_PATTERN.match(filename)
        if not match:
            continue
        
        lang = match.group(1).lower()
        date_str = match.group(2)
        slug = match.group(3)
        filepath = os.path.join(PUB_DIR, filename)
        
        try:
            date_obj = datetime.strptime(date_str, "%d-%m-%Y")
        except ValueError:
            continue

        title = extract_title(filepath, slug.replace("-", " "))
        url = f"./publications/{filename[:-3]}"
        
        articles.append({
            "date_obj": date_obj,
            "date_str": date_str,
            "lang": lang,
            "title": title,
            "url": url
        })

    articles.sort(key=lambda x: x["date_obj"], reverse=True)

    counts = {"en": 0, "ru": 0, "fr": 0, "es": 0}
    for a in articles:
        if a["lang"] in counts:
            counts[a["lang"]] += 1

    if not articles:
        feed_html = '<p><em>No publications yet. Add files to <code>content/publications/</code>.</em></p>'
    else:
        items = []
        for art in articles:
            lang_upper = art["lang"].upper()
            items.append(
                f'    <li class="pub-item lang-{art["lang"]}" style="margin-bottom: 10px; list-style: none;">'
                f'<span style="font-family: monospace; opacity: 0.75;">{art["date_str"]}</span> &nbsp;|&nbsp; '
                f'<strong style="font-size: 0.85em; padding: 2px 6px; border: 1px solid currentColor; border-radius: 4px;">{lang_upper}</strong> &nbsp;|&nbsp; '
                f'<a href="{art["url"]}" class="internal">{art["title"]}</a>'
                f'</li>'
            )
        feed_html = '  <ul id="pub-list" style="padding-left: 0; margin-top: 15px;">\n' + "\n".join(items) + '\n  </ul>'

    content = f"""---
title: Published Analyses & Chronological Papers
---

**Navigation:** [Publications](index) | [Methodology](methodology) | [About Laboratory](about)

---

**Vivien Yor** — independent geopolitical analyst and expert on global economics, international relations, and technological development.

### Published Analyses & Chronological Papers
*Chronological analytical notes & completed papers — **VSCI-laboratory***

<div class="vsci-filter-box">
  <input type="radio" name="vsci-lang" id="flt-all" checked>
  <label for="flt-all">All ({len(articles)})</label>

  <input type="radio" name="vsci-lang" id="flt-en">
  <label for="flt-en">EN ({counts['en']})</label>

  <input type="radio" name="vsci-lang" id="flt-ru">
  <label for="flt-ru">RU ({counts['ru']})</label>

  <input type="radio" name="vsci-lang" id="flt-fr">
  <label for="flt-fr">FR ({counts['fr']})</label>

  <input type="radio" name="vsci-lang" id="flt-es">
  <label for="flt-es">ES ({counts['es']})</label>

{feed_html}
</div>
"""

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Updated index.md with {len(articles)} articles.")

if __name__ == "__main__":
    build_index()
