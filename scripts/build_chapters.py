#!/usr/bin/env python3
"""Build chapter HTML files for Proof of Life from Project Documents MDs.

Reads Project Documents/PoL_Chapter_NN.md and writes chapters/chapter-N.html
for each chapter listed in the CHAPTERS table below.

Usage (from repo root):
    python3 scripts/build_chapters.py

To add a new chapter: append a tuple to CHAPTERS and (if the new chapter
contains subsections like "Chapter Four-A") map each subsection title to
its subhead annotation text in the subheads_map argument.
"""
import re
from pathlib import Path

ROOT = Path('/Users/bmac/Proof-of-Life')
DOCS = ROOT / 'Project Documents'
OUT = ROOT / 'chapters'

# Chapter definitions: (num_padded, word_title, md_filename, loc, time, subheads_map)
# subheads_map: { 'Chapter Four-A': 'IRGC Bunker, Outside Tehran · 16:34 IRST', ... }
CHAPTERS = [
    ('04', 'Four', 'PoL_Chapter_04.md', 'Tehran, Iran', '09:14 IRST', {
        'Chapter Four-A': 'IRGC Bunker, Outside Tehran · 16:34 IRST',
        'Chapter Four-B': 'Johnstown, PA · 10:09 EST',
    }),
    ('05', 'Five', 'PoL_Chapter_05.md', 'Fort Meade, Maryland', '05:10 EST', {}),
    ('06', 'Six', 'PoL_Chapter_06.md', "Hell's Kitchen, NYC", 'Afternoon EST', {}),
    ('07', 'Seven', 'PoL_Chapter_07.md', 'Mott Street, NYC', '13:56 EST', {
        'Chapter Seven-A': 'Greenwich, Connecticut · Afternoon EST',
    }),
    ('08', 'Eight', 'PoL_Chapter_08.md', 'Mott Street, NYC', 'Morning EST', {
        'Chapter Eight-A': 'Hudson River CFCU, NY · Wednesday, Dusk EST',
        'Chapter Eight-B': 'Downtown R Train, NYC · Thursday Morning EST',
    }),
    ('09', 'Nine', 'PoL_Chapter_09.md', 'Fort Meade, Maryland', '06:18 EST', {}),
    ('10', 'Ten', 'PoL_Chapter_10.md', 'Tehran, Iran', 'Morning IRST', {}),
]

# All chapters for drawer nav (num, word_title). Includes chapters 1-3 that already exist.
ALL_CHAPTERS = [
    ('01', 'One'),
    ('02', 'Two'),
    ('03', 'Three'),
    ('04', 'Four'),
    ('05', 'Five'),
    ('06', 'Six'),
    ('07', 'Seven'),
    ('08', 'Eight'),
    ('09', 'Nine'),
    ('10', 'Ten'),
]

SCENE_BREAK_HTML = '<div class="scene-break" role="separator" aria-label="Scene break">· · ·</div>'
SUBHEAD_STYLE = "font-family:'JetBrains Mono', monospace; font-size:.85rem; letter-spacing:.18em; text-transform:uppercase; opacity:.65; text-align:center; margin:2.5rem 0 1.5rem;"
SUBRULE_STYLE = "border:0; border-top:1px solid currentColor; opacity:.25; width:40%; margin:2.75rem auto 0;"


def unescape_md(text):
    # Markdown-escaped characters: \! \* \$ \[ \] \( \) \\ \_ \#
    return re.sub(r'\\([!*$\[\]()\\_#.-])', r'\1', text)


def convert_italics(text):
    """Convert *italic* to <em>italic</em>, careful not to touch escaped asterisks.
    Operates on text that already had \\* unescaped to literal *, so we must do
    this BEFORE unescaping. Easier: run on raw text, then unescape output.
    """
    # Non-greedy match for *...* not crossing paragraph. Avoid matching **.
    # We'll process using a regex that requires non-asterisk start/end chars.
    def repl(m):
        inner = m.group(1)
        return '<em>' + inner + '</em>'
    # Match single-asterisk pairs, not double. Content must not start/end with *.
    pattern = re.compile(r'(?<!\*)\*([^*\n][^*\n]*?)\*(?!\*)')
    return pattern.sub(repl, text)


def process_inline(text):
    # Convert italics first (on raw text, before unescape)
    text = convert_italics(text)
    # Then unescape markdown escapes
    text = unescape_md(text)
    return text


def is_fully_italic(raw_para):
    """True if entire paragraph is a single italic span."""
    s = raw_para.strip()
    if not (s.startswith('*') and s.endswith('*')):
        return False
    if s.startswith('**') or s.endswith('**'):
        return False
    inner = s[1:-1]
    # No bare * inside (not escaped) — would indicate multiple italic spans
    # Allow escaped \*
    cleaned = inner.replace(r'\*', '')
    if '*' in cleaned:
        return False
    return True


def make_first_graf(html):
    """Wrap opening clause (up to first comma) in <span class='lift'>."""
    # Find first comma; if none, wrap first ~6 words
    m = re.search(r'^(.*?,)(.*)$', html, re.DOTALL)
    if m:
        lift, rest = m.group(1), m.group(2)
        return f'<p class="first-graf"><span class="lift">{lift}</span>{rest}</p>'
    # Fallback: wrap first clause up to first period
    m = re.search(r'^(.*?\.)(.*)$', html, re.DOTALL)
    if m:
        lift, rest = m.group(1), m.group(2)
        return f'<p class="first-graf"><span class="lift">{lift}</span>{rest}</p>'
    return f'<p class="first-graf"><span class="lift">{html}</span></p>'


def parse_md(md_text, subheads_map):
    """Parse markdown and return list of HTML block strings."""
    # Split into paragraphs by blank lines
    paragraphs = re.split(r'\n\s*\n', md_text)
    blocks = []
    is_first_para = True
    pending_scene_break = False  # Track scene break so subheads can swallow it

    for raw in paragraphs:
        raw = raw.strip()
        if not raw:
            continue

        # Chapter title (first paragraph) — skip entirely
        m_title = re.match(r'^##\s+\*\*(Chapter\s+[A-Za-z][A-Za-z\-]*)\*\*\s*$', raw)
        if m_title:
            title_text = m_title.group(1)
            # Subsection subhead?
            if title_text in subheads_map:
                subhead_text = subheads_map[title_text]
                # Emit a rule + subhead (replacing pending scene break if any)
                if pending_scene_break:
                    blocks.pop()  # Remove the scene break; subhead rule replaces it
                    pending_scene_break = False
                blocks.append(f'<hr aria-hidden="true" style="{SUBRULE_STYLE}">')
                blocks.append(
                    f'<h2 class="chapter-subhead" style="{SUBHEAD_STYLE}">'
                    f'{title_text.replace("-", "&ndash;")} &mdash; {subhead_text}</h2>'
                )
                is_first_para = False  # Don't apply lift styling after subhead
            # Otherwise it's the main chapter title: skip
            continue

        # Scene break
        if raw == '---' or raw == '* * *' or raw == '\\* \\* \\*':
            blocks.append(SCENE_BREAK_HTML)
            pending_scene_break = True
            continue

        pending_scene_break = False

        # Determine paragraph class
        fully_italic = is_fully_italic(raw)

        # Convert inline
        html_text = process_inline(raw)
        # Convert in-paragraph newlines (soft breaks) to <br>
        html_text = html_text.replace('\n', '<br>\n')

        if is_first_para:
            blocks.append(make_first_graf(html_text))
            is_first_para = False
            continue

        if fully_italic:
            # html_text already has <em>...</em> wrapping entire content
            # Decide between device-text and interior:
            # Device-text: short-ish, system-announcement feel.
            # Interior: internal thought / self-address.
            # Heuristic: if contains quotes or starts with "Thousands" / all-caps-feel → device-text
            # Simpler: default to interior for subjective italic lines; use device-text when text looks like a bulletin
            # Both will render italicized; difference is only CSS flavor.
            # Looking at ch5 existing: SIGINT summary lines → device-text (bulletin style)
            # Looking at ch4: Supreme Leader quote → inline italics in quotes → NOT fully italic (has quotes)
            # Default heuristic: fully italic paragraphs → interior (internal monologue)
            blocks.append(f'<p class="interior">{html_text}</p>')
            continue

        blocks.append(f'<p>{html_text}</p>')

    return blocks


def build_drawer(current_num, from_chapters_dir=True):
    """Build nav drawer <li> items. current_num='04' or 'overview' for overview."""
    prefix = '' if from_chapters_dir else 'chapters/'
    overview_href = '../overview.html' if from_chapters_dir else 'overview.html'
    lines = []
    if current_num == 'overview':
        lines.append(f'      <li class="drawer-nav-item"><a href="{overview_href}" class="current"><span class="ch-num">&#8212;</span><span class="ch-title">Overview</span><span class="ch-status is-open">CURRENT</span></a></li>')
    else:
        lines.append(f'      <li class="drawer-nav-item"><a href="{overview_href}"><span class="ch-num">&#8212;</span><span class="ch-title">Overview</span><span class="ch-status is-open">OPEN</span></a></li>')
    for num, word in ALL_CHAPTERS:
        href = f'{prefix}chapter-{int(num)}.html'
        if num == current_num:
            lines.append(f'      <li class="drawer-nav-item"><a href="{href}" class="current"><span class="ch-num">{num}</span><span class="ch-title">Chapter {word}</span><span class="ch-status is-read">CURRENT</span></a></li>')
        else:
            # Chapters before current are READ, after are UNREAD
            if current_num != 'overview' and int(num) < int(current_num):
                lines.append(f'      <li class="drawer-nav-item"><a href="{href}"><span class="ch-num">{num}</span><span class="ch-title">Chapter {word}</span><span class="ch-status is-read">READ</span></a></li>')
            else:
                lines.append(f'      <li class="drawer-nav-item"><a href="{href}"><span class="ch-num">{num}</span><span class="ch-title">Chapter {word}</span><span class="ch-status is-unread">UNREAD</span></a></li>')
    return '\n'.join(lines)


def build_chapter_html(num, word, md_file, loc, time, subheads_map):
    md_text = (DOCS / md_file).read_text(encoding='utf-8')
    body_blocks = parse_md(md_text, subheads_map)
    body_html = '\n        '.join(body_blocks)

    drawer = build_drawer(num)

    # Prev/Next nav
    idx = next(i for i, (n, _) in enumerate(ALL_CHAPTERS) if n == num)
    prev_num, prev_word = ALL_CHAPTERS[idx - 1] if idx > 0 else (None, None)
    next_num, next_word = ALL_CHAPTERS[idx + 1] if idx + 1 < len(ALL_CHAPTERS) else (None, None)

    prev_link = f'<a href="chapter-{int(prev_num)}.html">&#8592; Chapter {prev_word}</a>' if prev_num else '<span class="nav-spacer"></span>'
    if next_num:
        next_link = f'<a href="chapter-{int(next_num)}.html">Chapter {next_word} &#8594;</a>'
    else:
        next_link = '<a href="../overview.html">Overview &#8594;</a>'

    html = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex, nofollow">
  <title>Chapter {word} &#8212; Proof of Life</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&family=Source+Serif+4:ital,wght@0,400;0,500;1,400&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../css/style.css">
</head>
<body>
  <a href="#main" class="skip-link">Skip to content</a>

  <header class="site-header" role="banner">
    <a href="../index.html" class="header-home">
      <span>PROOF_OF_LIFE</span>
      <span class="header-scope">/ CH.{num}</span>
    </a>
    <button class="nav-toggle" aria-label="Toggle index" aria-expanded="false" aria-controls="nav-drawer">
      <span class="nav-toggle-label" aria-hidden="true"></span>
      <span class="nav-toggle-bracket" aria-hidden="true"></span>
    </button>
  </header>

  <div class="nav-overlay" id="nav-overlay" aria-hidden="true"></div>

  <nav class="nav-drawer" id="nav-drawer" aria-label="Site navigation" aria-hidden="true">
    <ul class="drawer-nav-list">
{drawer}
    </ul>
  </nav>

  <main id="main">
    <div class="page-main">

      <header class="chapter-slug" aria-label="Chapter metadata">
        <div class="slug-row"><span class="slug-key">CH.</span><span class="slug-val">{num}</span></div>
        <div class="slug-row"><span class="slug-key">LOC.</span><span class="slug-val">{loc}</span></div>
        <div class="slug-row"><span class="slug-key">TIME</span><span class="slug-val">{time}</span></div>
        <div class="slug-rule" aria-hidden="true"></div>
      </header>

      <article class="chapter-body">
        {body_html}
      </article>

      <div class="chapter-footer">
        <nav class="chapter-footer-nav" aria-label="Chapter navigation">
          {prev_link}
          {next_link}
        </nav>
      </div>

    </div>
  </main>

  <footer class="log-footer" role="contentinfo">
    <div class="log-footer-row">
      <span class="led" aria-hidden="true"></span>
      <span>SYS::ARC.READER</span>
      <span style="flex:1"></span>
      <span>CH.{num}</span>
    </div>
    <div class="log-footer-row">
      <span>UPLINK</span>
      <span class="dots" aria-hidden="true">&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;&#xB7;</span>
      <span class="ok">OK</span>
    </div>
  </footer>

  <script src="../js/main.js"></script>
</body>
</html>
'''
    return html


def main():
    for num, word, md, loc, tm, subs in CHAPTERS:
        html = build_chapter_html(num, word, md, loc, tm, subs)
        path = OUT / f'chapter-{int(num)}.html'
        path.write_text(html, encoding='utf-8')
        print(f'✅ wrote {path}')


if __name__ == '__main__':
    main()
