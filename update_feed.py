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

def make_btn(lang_code, label, is_active=False):
    weight = "bold" if is_active else "normal"
    bg = "rgba(128, 128, 128, 0.2)" if is_active else "transparent"
    # Встроенный JS-код прямо в клик по кнопке (не вырезается движком Quartz)
    js = (
        f"document.querySelectorAll('.vsci-fbtn').forEach(b=>{{b.style.fontWeight='normal';b.style.background='transparent';}});"
        f"this.style.fontWeight='bold';this.style.background='rgba(128,128,128,0.2)';"
        f"document.querySelectorAll('.pub-item').forEach(el=>{{el.style.display=('{lang_code}'==='all'||el.dataset.lang==='{lang_code}')?'block':'none';}});"
    )
    return (
        f'<button type="button" class="vsci-fbtn" onclick="{js}" '
        f'style="cursor:pointer; padding: 5px 12px; border-radius: 6px; border: 1px solid #888; font-weight: {weight}; background: {bg};">'
        f'{label}</button>'
    )

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

    # Считаем количество статей по каждому языку для кнопок
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
                f'  <li class="pub-item" data-lang="{art["lang"]}" style="margin-bottom: 10px; list-style: none;">'
                f'<span style="font-family: monospace; opacity: 0.75;">{art["date_str"]}</span> &nbsp;|&nbsp; '
                f'<strong style="font-size: 0.85em; padding: 2px 6px; border: 1px solid currentColor; border-radius: 4px;">{lang_upper}</strong> &nbsp;|&nbsp; '
                f'<a href="{art["url"]}" class="internal">{art["title"]}</a>'
                f'</li>'
            )
        feed_html = '<ul id="pub-list" style="padding-left: 0;">\n' + "\n".join(items) + '\n</ul>'

    buttons_html = "\n  ".join([
        make_btn("all", f"All ({len(articles)})", True),
        make_btn("en", f"EN ({counts['en']})"),
        make_btn("ru", f"RU ({counts['ru']})"),
        make_btn("fr", f"FR ({counts['fr']})"),
        make_btn("es", f"ES ({counts['es']})"),
    ])

    content = f"""---
title: Published Analyses & Chronological Papers
---

**Navigation:** [Publications](index) | [Methodology](methodology) | [About Laboratory](about)

---

**Vivien Yor** — independent geopolitical analyst and expert on global economics, international relations, and technological development.

### Published Analyses & Chronological Papers
*Chronological analytical notes & completed papers — **VSCI-laboratory***

<div id="lang-filters" style="margin: 20px 0; display: flex; gap: 8px; flex-wrap: wrap;">
  {buttons_html}
</div>

{feed_html}
"""

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Updated index.md with {len(articles)} articles.")

if __name__ == "__main__":
    build_index()
