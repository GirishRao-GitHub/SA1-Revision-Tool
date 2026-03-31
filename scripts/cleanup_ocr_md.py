"""
cleanup_ocr_md.py v2 - Post-processing cleaner for OCR-extracted Markdown files.

Strategy:
  - Line-by-line: keep the original line breaks (don't merge paragraphs)
  - Strip page headers/footers/copyright/page-number lines
  - Remove clear OCR noise-only lines
  - Fix bullet characters (°, ®, •) → proper markdown bullets
  - Detect and format Question / Solution / Example blocks with blockquotes
  - Close Q/S blocks at page boundaries

Usage:
    python cleanup_ocr_md.py <input_md_path> [output_md_path]
"""

import re
import sys
import os

# ── 1. PAGE HEADER / FOOTER PATTERNS ────────────────────────────────────────
RE_HEADER = re.compile(
    r'^(?:SA\d+-\d+[:\s].+?Page\s+\d+\b|Page\s+\d+\s+SA\d+-\d+[:\s].+)$',
    re.IGNORECASE
)
RE_COPYRIGHT = re.compile(
    r'(?:©\s*I[FP]E|Actuarial Education Company|IFE:\s*\d{4}\s*Examinations)',
    re.IGNORECASE
)
# Standalone page numbers / garbled page-number-like strings (at end of page)
RE_LONE_PAGENUM = re.compile(r'^\s*[0-9]{2,4}\s*$')  # pure digits like 719, 730
RE_GARBLED_PAGENUM = re.compile(r'^\s*[0-9][A-Za-z0-9?\.]{1,6}\s*$')  # "72?", "7ONn", "waev.l"

# ── 2. NOISE LINE PATTERNS ────────────────────────────────────────────────────
# A line is noise if it matches ANY of these after stripping whitespace
NOISE_RE = [
    re.compile(r'^$'),                                         # blank (handled separately)
    re.compile(r'^[|_\/\\]{1,5}$'),                           # just pipes/slashes
    re.compile(r'^[°•®]\s*$'),                                # lone bullet char
    re.compile(r'^[~\-=_\s]{3,}$'),                           # decorative separators
    re.compile(r'^[^\w]{1,4}$'),                              # 1-4 non-word chars only
    re.compile(r'^e{2,4}$'),                                  # "ee", "eee", "eeee"
    re.compile(r'^[a-z]{1,2}$'),                              # single/double lowercase
    re.compile(r'^[a-z]\s[a-zA-Z]\s?[a-z]?$'),               # "e a", "oe A e"
    re.compile(r'^[xX]\s*\d\s*$'),                            # "x 2", "x 3"
    re.compile(r'^t[Ll]\)?$'),                                # "tL)", "tl"
    re.compile(r'^I\.\s*s{1,2}$'),                            # "I. ss"
    re.compile(r'^[oO]n\s*$'),                                # "on"
    re.compile(r'^[aA]n\s*$'),                                # "an"
    re.compile(r'^[°|]\s*[oO][oO]"?$'),                      # '| oo"'
    re.compile(r'^ew$|^ax$|^[sS]{2}$'),                      # specific artefacts
    re.compile(r'^\s*[|]\s*$'),                               # isolated pipe
    re.compile(r'^[A-Z]{1,3}[:;]?\s*$'),                     # "CC", "S$", "CC:"
    # Lines that are ONLY dashes/underscores/tildes/equals mixed with spaces
    re.compile(r'^[\-_=~\s]+$'),
    # Very short lines that are purely noise symbols
    re.compile(r'^[^\w\d]{1,6}$'),
    # Lines like "_—_—_—_—" or "——XSX-" — common OCR border artefacts
    re.compile(r'^[_\-—]+[A-Za-z\-—_]*[_\-—]+$'),
    # "v_ improve" style line-start noise
    re.compile(r'^v_\s'),
    # Lines that are just combinations of letters/dashes that look like noise
    re.compile(r'^[\-—_=~*]{2,}\s*[A-Za-z]{0,4}\s*[\-—_=~]{2,}'),
    # Lone OCR icon chars at start (o, x, f, L_ etc)
    re.compile(r'^[oxf]\s+[A-Z][a-z]'),                      # matched below with Question check
    # Lines like "| 2 assessment" or "| oo" — pipe followed by short junk
    re.compile(r'^\|\s*[0-9°]\s'),
    # Lines like "L_#3", "C4)", "Ly -"
    re.compile(r'^[A-Za-z_][_#@\(\)]{1,2}\d?\)?$'),
    # Lines that are purely punctuation/symbols like "—E———— eS ES"
    re.compile(r'^[—\-–E\s]{4,}[A-Z]?[a-z]?[\s—\-E]+$'),
    # "a a —— SF" style
    re.compile(r'^[a-z]\s+[a-z]\s+[—\-]{2}'),
    # "_—_—_——XSX-" style OCR border artefacts anywhere on line
    re.compile(r'^[_\-—X]{4,}'),
    # Lines like "jet Lt DL", "ib SE", "eal 28S bli" — garbled OCR
    re.compile(r'^[a-z]{2,3}\s+[A-Z]{1,3}\s+[A-Z]{1,3}\s*$'),
    re.compile(r'^[a-z]{2,4}\s+\d{2,3}[A-Z]\s'),
    # "pie EE", "os ad e e" style
    re.compile(r'^[a-z]{2,3}\s+[A-Z]{1,2}\s*$'),
    # Lines like "Mn ey 2", "ro\" eo ooo"
    re.compile(r'^[A-Za-z]{2}\s[a-z]{1,3}\s+\d+\s*$'),
    re.compile(r'^ro.{0,2}\s+eo\s'),
]

# A separate set for lines that are MOSTLY noise but MAY have a word or two
# We use a whitelist approach: if stripped line has <4 chars total, likely noise
def is_short_noise(s: str) -> bool:
    """Lines with fewer than 4 printable non-space characters are likely noise."""
    return len(re.sub(r'\s', '', s)) < 4

def is_noise_line(line: str) -> bool:
    s = line.strip()
    if not s:
        return False  # blanks handled separately
    for pat in NOISE_RE:
        if pat.match(s):
            return True
    if is_short_noise(s):
        return True
    return False

def is_page_header_footer(line: str) -> bool:
    s = line.strip()
    if RE_HEADER.match(s):
        return True
    if RE_COPYRIGHT.search(s):
        return True
    if RE_LONE_PAGENUM.match(s):
        return True
    if RE_GARBLED_PAGENUM.match(s):
        return True
    return False

# ── 3. BULLET NORMALISATION ───────────────────────────────────────────────────
# Lines starting with °, ®, •, * (bullet) → "- "
RE_BULLET_CHARS = re.compile(r'^[°®•]\s+(.+)$')
# Lines starting with "e " where e is a bullet OCR artefact
# Only match if next chars are lowercase NOT a common English word start
RE_E_BULLET = re.compile(r'^e\s+([a-z].*)$')
COMMON_WORD_STARTS = {
    'eg', 'etc', 'each', 'either', 'even', 'ever', 'every', 'example',
    'exactly', 'except', 'existing', 'experience', 'expected', 'ensuring',
    'establish', 'essentially', 'expertise', 'expanding',
    'experience', 'extension', 'extent',
}
# Inline noise scrubbing: remove runs of OCR noise characters within text
RE_INLINE_RUNS = [
    re.compile(r'[—\-_]{4,}[A-Za-z\-_—X]*[—\-_]{2,}'),   # "—_—_——XSX-"
    re.compile(r'\bE[—\-E\s]{3,}[A-Z]{1,2}\b'),              # "—E———— eS ES"
    re.compile(r'\b[a-z]{1,2}\s__\s'),                       # "v_ "
    re.compile(r'\s[_/]{1,2}\s'),                             # " _ " or " / "
]

def fix_bullet(line: str) -> str:
    s = line.strip()
    m = RE_BULLET_CHARS.match(s)
    if m:
        return '- ' + m.group(1)
    # Handle "e <word>" style OCR bullets
    m2 = RE_E_BULLET.match(s)
    if m2:
        first_word = m2.group(1).split()[0].lower().rstrip(',')
        if first_word not in COMMON_WORD_STARTS:
            return '- ' + m2.group(1)
    # Handle "® " or "@ " at start
    if s.startswith('@ ') or s.startswith('® '):
        return '- ' + s[2:]
    return line.rstrip()

# ── 4. INLINE NOISE CLEANING ─────────────────────────────────────────────────
# Remove inline decorative runs of dashes/underscores/tildes that span 3+ chars
RE_INLINE_NOISE_DASHES = re.compile(r'[_\-]{4,}')
RE_INLINE_NOISE_MIXED  = re.compile(r'[_\-~=]{3,}[A-Za-z\-_~=]*[_\-~=]{2,}')

def clean_inline(line: str) -> str:
    # Remove long blocks of underscores/dashes (decorative OCR noise)
    line = RE_INLINE_NOISE_DASHES.sub('', line)
    line = RE_INLINE_NOISE_MIXED.sub('', line)
    # Remove inline noise runs
    for pat in RE_INLINE_RUNS:
        line = pat.sub('', line)
    # Remove trailing OCR margin noise chars  (single letter/symbol at end of content line)
    line = re.sub(r'\s+[a-zA-Z_/\\.`]\s*$', '', line)
    # Remove leading noise like "| °" or "| 2"
    line = re.sub(r'^\|\s*[°•2@®]?\s+', '', line)
    # Remove lines that start with noise icon chars like '= : ~ -'
    line = re.sub(r'^[=:\-~\s]{4,}', '', line)
    return line.strip()

# ── 5. QUESTION / SOLUTION / EXAMPLE DETECTION ──────────────────────────────
RE_QUESTION = re.compile(r'^\s*(?:[tfoLCx✦⬜□|\[\(]?\s*[|]?\s*)?[Qq]uestion\s*$')
RE_SOLUTION = re.compile(r'^\s*[Ss]olution\s*$')
RE_EXAMPLE  = re.compile(r'^\s*[Ee]xample\s*$')

# ── MAIN PROCESSING ──────────────────────────────────────────────────────────

def process(lines):
    out = []
    # Track whether we are inside a special block
    block = None  # None | 'question' | 'solution' | 'example'

    def emit(text, in_block=None):
        ib = in_block if in_block is not None else block
        if ib and not text.startswith('## ') and not text.startswith('---'):
            out.append('> ' + text if text.strip() else '>')
        else:
            out.append(text)

    def close_block():
        nonlocal block
        if block:
            out.append('>')
            block = None

    for raw in lines:
        s = raw.strip()

        # ── Page heading (## Page N) ─────────────────────────────────────────
        if s.startswith('## Page '):
            close_block()
            out.append('')
            out.append(s)
            out.append('')
            continue

        # ── Page separator (---) ─────────────────────────────────────────────
        if s == '---':
            close_block()
            out.append('---')
            out.append('')
            continue

        # ── Blank line ────────────────────────────────────────────────────────
        if not s:
            if block:
                out.append('>')
            else:
                # Only add blank if last line wasn't already blank
                if out and out[-1] != '':
                    out.append('')
            continue

        # ── Page headers / footers (checked before noise to protect real text) ──
        if is_page_header_footer(raw):
            continue

        # ── Question/Solution/Example MUST be checked BEFORE noise filtering ──
        # because markers like "f Question", "o Question" match noise patterns.
        if RE_QUESTION.match(s):
            close_block()
            out.append('')
            out.append('> **Question**')
            out.append('>')
            block = 'question'
            continue

        if RE_SOLUTION.match(s):
            if block == 'question':
                out.append('>')
            elif block != 'solution':
                close_block()
                out.append('')
            out.append('> **Solution**')
            out.append('>')
            block = 'solution'
            continue

        if RE_EXAMPLE.match(s):
            close_block()
            out.append('')
            out.append('> **Example**')
            out.append('>')
            block = 'example'
            continue

        # ── Noise lines ───────────────────────────────────────────────────────
        if is_noise_line(raw):
            continue

        # ── Document title (# ...) ────────────────────────────────────────────
        if s.startswith('# ') or s.startswith('*Source'):
            out.append(s)
            continue

        # ── Section/sub-section headings heuristic ────────────────────────────
        # e.g. "1 Assessment of the market..." or "1.1 Consumer demand"
        heading_match = re.match(r'^(\d+(?:\.\d+)*)\s+([A-Z].{5,})$', s)
        if heading_match and not block:
            level = heading_match.group(1).count('.') + 3  # 1 → ###, 1.1 → ####
            prefix = '#' * min(level, 4)
            out.append('')
            out.append(f'{prefix} {heading_match.group(1)} {heading_match.group(2)}')
            out.append('')
            continue

        # ── Inline clean + bullet fix ─────────────────────────────────────────
        line = fix_bullet(raw)
        line = clean_inline(line)

        if not line:
            continue

        # Emit in appropriate context
        if block:
            out.append('> ' + line)
        else:
            out.append(line)

    close_block()
    return out


def collapse_blanks(lines):
    """Collapse 3+ consecutive blanks → 2 max."""
    result = []
    blanks = 0
    for line in lines:
        if line == '' or line == '>':
            blanks += 1
            if blanks <= 2:
                result.append(line)
        else:
            blanks = 0
            result.append(line)
    return result


def clean_md(input_path: str, output_path: str):
    with open(input_path, 'r', encoding='utf-8') as f:
        raw_lines = [l.rstrip('\r\n') for l in f.readlines()]

    processed = process(raw_lines)
    final = collapse_blanks(processed)

    with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(final))
        f.write('\n')

    print(f"Done. Lines in: {len(raw_lines)}  Lines out: {len(final)}")
    print(f"Output: {output_path}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python cleanup_ocr_md.py <input_md_path> [output_md_path]")
        sys.exit(1)

    inp = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) >= 3 else os.path.splitext(inp)[0] + '_clean.md'

    clean_md(inp, out)
