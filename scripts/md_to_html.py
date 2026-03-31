"""
md_to_html.py - Convert a cleaned OCR markdown file to a beautifully styled HTML document.

Usage:
    python md_to_html.py <input_md_path> [output_html_path]
"""

import re
import sys
import os

# ── HTML TEMPLATE ─────────────────────────────────────────────────────────────
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Lora:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #0f1117;
      --surface: #1a1d2e;
      --surface2: #222640;
      --border: #2e3259;
      --accent: #6c7bff;
      --accent2: #a78bfa;
      --gold: #f5c842;
      --text: #e2e8f0;
      --text-dim: #94a3b8;
      --text-muted: #64748b;
      --green: #4ade80;
      --green-bg: #0d2318;
      --green-border: #166534;
      --blue: #60a5fa;
      --blue-bg: #0d1b35;
      --blue-border: #1e3a5f;
      --page-tag: #ff7c52;
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      background: var(--bg);
      color: var(--text);
      font-family: 'Inter', sans-serif;
      font-size: 15px;
      line-height: 1.75;
      min-height: 100vh;
    }}

    /* ── LAYOUT ── */
    #sidebar {{
      position: fixed;
      top: 0; left: 0;
      width: 260px;
      height: 100vh;
      background: var(--surface);
      border-right: 1px solid var(--border);
      overflow-y: auto;
      padding: 24px 0;
      z-index: 100;
    }}

    #sidebar h2 {{
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--text-muted);
      padding: 0 20px 12px;
    }}

    #sidebar ul {{ list-style: none; }}
    #sidebar ul li a {{
      display: block;
      padding: 6px 20px;
      font-size: 13px;
      color: var(--text-dim);
      text-decoration: none;
      border-left: 3px solid transparent;
      transition: all 0.15s;
    }}
    #sidebar ul li a:hover {{
      color: var(--text);
      background: rgba(108,123,255,0.08);
      border-left-color: var(--accent);
    }}
    #sidebar ul li a.active {{
      color: var(--accent);
      border-left-color: var(--accent);
      background: rgba(108,123,255,0.12);
    }}
    #sidebar .sub-link {{
      padding-left: 36px !important;
      font-size: 12px !important;
    }}

    #content {{
      margin-left: 260px;
      max-width: 860px;
      padding: 60px 60px 120px;
    }}

    /* ── HEADER ── */
    .doc-header {{
      margin-bottom: 56px;
      padding-bottom: 32px;
      border-bottom: 1px solid var(--border);
    }}
    .doc-header h1 {{
      font-family: 'Lora', Georgia, serif;
      font-size: 32px;
      font-weight: 600;
      color: var(--text);
      line-height: 1.3;
      margin-bottom: 10px;
    }}
    .doc-header .source-tag {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 12px;
      color: var(--text-muted);
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 4px 10px;
      font-family: 'Courier New', monospace;
    }}

    /* ── PAGE MARKER ── */
    .page-marker {{
      display: flex;
      align-items: center;
      gap: 12px;
      margin: 48px 0 24px;
    }}
    .page-marker .badge {{
      background: var(--surface2);
      border: 1px solid var(--border);
      color: var(--page-tag);
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      padding: 4px 10px;
      border-radius: 20px;
    }}
    .page-marker .line {{
      flex: 1;
      height: 1px;
      background: var(--border);
    }}

    /* ── HEADINGS ── */
    h2.section-heading {{
      font-family: 'Lora', Georgia, serif;
      font-size: 22px;
      font-weight: 600;
      color: var(--text);
      margin: 36px 0 12px;
      padding-bottom: 8px;
      border-bottom: 1px solid var(--border);
    }}
    h3.sub-heading {{
      font-size: 16px;
      font-weight: 600;
      color: var(--accent2);
      margin: 28px 0 10px;
      letter-spacing: 0.01em;
    }}

    /* ── PARAGRAPHS ── */
    p {{
      margin-bottom: 14px;
      color: var(--text);
    }}

    /* ── BULLET LISTS ── */
    ul {{
      margin: 10px 0 16px 0;
      padding-left: 0;
      list-style: none;
    }}
    ul li {{
      position: relative;
      padding: 4px 0 4px 22px;
      color: var(--text);
    }}
    ul li::before {{
      content: '▸';
      position: absolute;
      left: 0;
      color: var(--accent);
      font-size: 12px;
      top: 7px;
    }}

    /* ── Q&A BLOCKS ── */
    .qa-block {{
      margin: 24px 0;
      border-radius: 12px;
      overflow: hidden;
      border: 1px solid var(--border);
      box-shadow: 0 4px 24px rgba(0,0,0,0.3);
    }}

    .qa-question {{
      background: var(--blue-bg);
      border-bottom: 1px solid var(--blue-border);
      padding: 16px 20px;
    }}
    .qa-question .label {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: var(--blue);
      margin-bottom: 8px;
    }}
    .qa-question .label::before {{
      content: '?';
      display: inline-block;
      width: 18px; height: 18px;
      background: var(--blue);
      color: #000;
      border-radius: 50%;
      text-align: center;
      line-height: 18px;
      font-size: 11px;
    }}
    .qa-question p {{
      color: var(--text);
      font-weight: 500;
      margin: 0;
    }}

    .qa-solution {{
      background: var(--green-bg);
      padding: 16px 20px;
    }}
    .qa-solution .label {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: var(--green);
      margin-bottom: 8px;
    }}
    .qa-solution .label::before {{
      content: '✓';
      display: inline-block;
      width: 18px; height: 18px;
      background: var(--green);
      color: #000;
      border-radius: 50%;
      text-align: center;
      line-height: 18px;
      font-size: 11px;
    }}
    .qa-solution p, .qa-solution li {{
      color: #c7f5d8;
    }}
    .qa-solution ul li::before {{
      color: var(--green);
    }}

    /* ── EXAMPLE BLOCKS ── */
    .example-block {{
      background: rgba(245,200,66,0.06);
      border: 1px solid rgba(245,200,66,0.25);
      border-radius: 10px;
      padding: 16px 20px;
      margin: 20px 0;
    }}
    .example-block .label {{
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: var(--gold);
      margin-bottom: 8px;
    }}
    .example-block p {{ color: #f0e0a0; margin-bottom: 10px; }}
    .example-block li {{ color: #f0e0a0; }}

    /* ── TABLE OF CONTENTS TOGGLE (mobile) ── */
    hr.page-sep {{ display: none; }}

    /* ── SCROLLBAR ── */
    ::-webkit-scrollbar {{ width: 6px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 3px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: var(--accent); }}

    @media (max-width: 900px) {{
      #sidebar {{ display: none; }}
      #content {{ margin-left: 0; padding: 32px 24px 80px; }}
    }}
  </style>
</head>
<body>

<nav id="sidebar">
  <h2>Contents</h2>
  <ul>
{nav_items}
  </ul>
</nav>

<main id="content">
{body}
</main>

<script>
  // Active section highlighting in sidebar
  const links = document.querySelectorAll('#sidebar a');
  const observer = new IntersectionObserver(entries => {{
    entries.forEach(e => {{
      if (e.isIntersecting) {{
        links.forEach(l => l.classList.remove('active'));
        const id = e.target.id;
        const link = document.querySelector(`#sidebar a[href="#${{id}}"]`);
        if (link) link.classList.add('active');
      }}
    }});
  }}, {{ threshold: 0.2, rootMargin: '-20% 0px -60% 0px' }});

  document.querySelectorAll('[id]').forEach(el => observer.observe(el));
</script>
</body>
</html>"""


# ── PARSER ───────────────────────────────────────────────────────────────────

def escape(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def inline_format(text):
    """Apply inline markdown: **bold**, *italic*, `code`"""
    text = escape(text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    return text

def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

def convert(md_text):
    lines = md_text.splitlines()
    body_parts = []
    nav_items = []
    title = 'Document'

    # State machine
    state = None  # None | 'question' | 'solution' | 'example'
    q_lines = []
    s_lines = []
    e_lines = []
    cur_list = []
    section_counter = 0

    def flush_list():
        nonlocal cur_list
        if cur_list:
            items = ''.join(f'<li>{inline_format(l)}</li>' for l in cur_list)
            body_parts.append(f'<ul>{items}</ul>')
            cur_list = []

    def flush_block():
        nonlocal state, q_lines, s_lines, e_lines, cur_list
        flush_list()
        if state == 'example':
            content = ''.join(f'<p>{inline_format(l)}</p>' for l in e_lines if l.strip())
            body_parts.append(f'<div class="example-block"><div class="label">Example</div>{content}</div>')
            e_lines = []
        elif state in ('question', 'solution'):
            q_html = ''.join(f'<p>{inline_format(l)}</p>' for l in q_lines if l.strip())
            # Build solution: may have bullets and paragraphs
            s_html_parts = []
            s_list = []
            for sl in s_lines:
                if sl.startswith('- '):
                    s_list.append(sl[2:])
                else:
                    if s_list:
                        items = ''.join(f'<li>{inline_format(i)}</li>' for i in s_list)
                        s_html_parts.append(f'<ul>{items}</ul>')
                        s_list = []
                    if sl.strip():
                        s_html_parts.append(f'<p>{inline_format(sl)}</p>')
            if s_list:
                items = ''.join(f'<li>{inline_format(i)}</li>' for i in s_list)
                s_html_parts.append(f'<ul>{items}</ul>')
            s_html = ''.join(s_html_parts)
            block = f'''<div class="qa-block">
  <div class="qa-question"><div class="label">Question</div>{q_html}</div>
  <div class="qa-solution"><div class="label">Solution</div>{s_html}</div>
</div>'''
            body_parts.append(block)
            q_lines = []
            s_lines = []
        state = None

    page_num = 0
    i = 0

    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()

        # ── Document title ──
        if stripped.startswith('# ') and not stripped.startswith('## '):
            title = stripped[2:]
            src_match = lines[i+1].strip() if i+1 < len(lines) else ''
            src_text = ''
            if src_match.startswith('*Source:'):
                src_text = src_match.strip('*').replace('Source: ', '').strip('`')
                i += 1
            header_html = f'''<div class="doc-header">
  <h1>{inline_format(title)}</h1>
  <span class="source-tag">📄 {escape(src_text)}</span>
</div>'''
            body_parts.append(header_html)
            i += 1
            continue

        # ── Page break markers ──
        if stripped == '---':
            flush_block()
            i += 1
            continue

        # ── Page heading ──
        if stripped.startswith('## Page '):
            flush_block()
            page_num = stripped.replace('## Page ', '')
            pid = f'page-{page_num}'
            body_parts.append(f'<div class="page-marker" id="{pid}"><span class="badge">Page {page_num}</span><div class="line"></div></div>')
            nav_items.append(f'    <li><a href="#{pid}">Page {page_num}</a></li>')
            i += 1
            continue

        # ── Section headings (### = section, #### = subsection) ──
        if stripped.startswith('### ') and not stripped.startswith('#### '):
            flush_block()
            text = stripped[4:]
            sid = f'sec-{slugify(text)}'
            body_parts.append(f'<h2 class="section-heading" id="{sid}">{inline_format(text)}</h2>')
            nav_items.append(f'    <li><a href="#{sid}">{escape(text[:50])}</a></li>')
            i += 1
            continue

        if stripped.startswith('#### '):
            flush_block()
            text = stripped[5:]
            sid = f'sub-{slugify(text)}'
            body_parts.append(f'<h3 class="sub-heading" id="{sid}">{inline_format(text)}</h3>')
            nav_items.append(f'    <li><a href="#{sid}" class="sub-link">{escape(text[:45])}</a></li>')
            i += 1
            continue

        # ── Blockquote lines (Q/S/Example) ──
        if stripped.startswith('> ') or stripped == '>':
            content = stripped[2:] if stripped.startswith('> ') else ''

            # Block state transitions
            if content == '**Question**':
                if state in ('question', 'solution', 'example'):
                    flush_block()
                state = 'question'
                i += 1
                continue
            if content == '**Solution**':
                if state == 'question':
                    pass  # transition from Q to S
                elif state in ('example',):
                    flush_block()
                state = 'solution'
                i += 1
                continue
            if content == '**Example**':
                if state:
                    flush_block()
                state = 'example'
                i += 1
                continue

            # Accumulate content into active block
            if state == 'question':
                if content and not is_ocr_noise(content):
                    # Bullets inside question
                    if content.startswith('- '):
                        q_lines.append(content[2:])
                    else:
                        q_lines.append(content)
            elif state == 'solution':
                if content and not is_ocr_noise(content):
                    if content.startswith('- '):
                        s_lines.append('- ' + content[2:])
                    else:
                        s_lines.append(content)
            elif state == 'example':
                if content and not is_ocr_noise(content):
                    e_lines.append(content)
            i += 1
            continue

        # ── Bullet list items ──
        if stripped.startswith('- ') or stripped.startswith('* '):
            flush_block()  # close any open Q/S/Example first
            state = None
            cur_list.append(stripped[2:])
            i += 1
            continue

        # ── Blank line ──
        if not stripped:
            flush_list()
            i += 1
            continue

        # ── Regular paragraph text ──
        if stripped and not is_ocr_noise(stripped):
            flush_block()
            flush_list()
            body_parts.append(f'<p>{inline_format(stripped)}</p>')
        i += 1

    flush_block()
    flush_list()

    return title, '\n'.join(nav_items), '\n'.join(body_parts)


# OCR noise lines remaining in clean MD that should be silently skipped in HTML
INLINE_NOISE_PATTERNS = [
    re.compile(r'^[—\-E\s]{5,}'),
    re.compile(r'^[a-z]{1,3}\s+[a-z]{1,3}\s+[a-z]{1,3}$'),
    re.compile(r'^\s*[°|•]\s*$'),
    re.compile(r'^[~\-=_\s]+$'),
    re.compile(r'^\s*[A-Z]{1,3}\s*$'),
    re.compile(r'^[a-z]{1,2}\s+[A-Z]{1,2}\s*$'),
    re.compile(r'^we\s+\d'),
    re.compile(r'^[a-z]{2,3}\s+\d{2,3}[A-Z]'),
]
def is_ocr_noise(text: str) -> bool:
    s = text.strip()
    if len(re.sub(r'\s', '', s)) < 3:
        return True
    for pat in INLINE_NOISE_PATTERNS:
        if pat.match(s):
            return True
    return False


def md_to_html(input_path: str, output_path: str):
    with open(input_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    title, nav_items, body = convert(md_text)

    html = HTML_TEMPLATE.format(
        title=title,
        nav_items=nav_items,
        body=body
    )

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Done. Output: {output_path}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python md_to_html.py <input_md_path> [output_html_path]")
        sys.exit(1)

    inp = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) >= 3 else os.path.splitext(inp)[0] + '.html'

    md_to_html(inp, out)
