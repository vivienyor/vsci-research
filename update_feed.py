import os
import re
from datetime import datetime

CONTENT_DIR = "content"
PUB_DIR = os.path.join(CONTENT_DIR, "publications")
INDEX_FILE = os.path.join(CONTENT_DIR, "index.md")

# Шаблон имени файла: lang_DD-MM-YYYY_slug.md
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
        # Относительный URL для корректной работы на GitHub Pages
        url = f"./publications/{filename[:-3]}"
        
        articles.append({
            "date_obj": date_obj,
            "date_str": date_str,
            "lang": lang,
            "title": title,
            "url": url
        })

    # Сортировка от самых свежих к более ранним
    articles.sort(key=lambda x: x["date_obj"], reverse=True)

    # Формируем HTML-список с атрибутами для мгновенной фильтрации
    if not articles:
        feed_html = '<p><em>No publications yet. Add files to <code>content/publications/</code>.</em></p>'
    else:
        items = []
        for art in articles:
            lang_upper = art["lang"].upper()
            items.append(
                f'  <li class="pub-item" data-lang="{art["lang"]}" style="margin-bottom: 10px; list-style: none;">'
                f'<span style="font-family: monospace; opacity: 0.75;">{art["date_str"]}</span> &nbsp;|&nbsp; '
                f'<strong style="font-size: 0.85em; padding: 2px 6px; border: 1px solid currentColor; border-radius: 4px;">{lang_upper}</strong> &nbsp;|&nbsp; '
                f'<a href="{art["url"]}" class="internal">{art["title"]}</a>'
                f'</li>'
            )
        feed_html = '<ul id="pub-list" style="padding-left: 0;">\n' + "\n".join(items) + '\n</ul>'

    # Собираем итоговый index.md
    content = f"""---
title: Published Analyses & Chronological Papers
---

**Navigation:** [Publications](index) | [Methodology](methodology) | [About Laboratory](about)

---

**Vivien Yor** — independent geopolitical analyst and expert on global economics, international relations, and technological development.

### Published Analyses & Chronological Papers
*Chronological analytical notes & completed papers — **VSCI-laboratory***

<div id="lang-filters" style="margin: 20px 0; display: flex; gap: 8px; flex-wrap: wrap;">
  <button onclick="filterPubs('all', this)" class="filter-btn active" style="cursor:pointer; padding: 5px 12px; border-radius: 6px; border: 1px solid #888; font-weight: bold;">All ({len(articles)})</button>
  <button onclick="filterPubs('en', this)" class="filter-btn" style="cursor:pointer; padding: 5px 12px; border-radius: 6px; border: 1px solid #888; background: transparent;">EN</button>
  <button onclick="filterPubs('ru', this)" class="filter-btn" style="cursor:pointer; padding: 5px 12px; border-radius: 6px; border: 1px solid #888; background: transparent;">RU</button>
  <button onclick="filterPubs('fr', this)" class="filter-btn" style="cursor:pointer; padding: 5px 12px; border-radius: 6px; border: 1px solid #888; background: transparent;">FR</button>
  <button onclick="filterPubs('es', this)" class="filter-btn" style="cursor:pointer; padding: 5px 12px; border-radius: 6px; border: 1px solid #888; background: transparent;">ES</button>
</div>

{feed_html}

<script>
function filterPubs(lang, btn) {{
  document.querySelectorAll('.filter-btn').forEach(b => {{
    b.style.fontWeight = 'normal';
    b.style.background = 'transparent';
  }});
  btn.style.fontWeight = 'bold';
  btn.style.background = 'rgba(128, 128, 128, 0.2)';

  document.querySelectorAll('.pub-item').forEach(item => {{
    if (lang === 'all' || item.getAttribute('data-lang') === lang) {{
      item.style.display = 'block';
    }} else {{
      item.style.display = 'none';
    }}
  }});
}}
</script>
"""

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Updated index.md with {len(articles)} articles.")

if __name__ == "__main__":
    build_index()
