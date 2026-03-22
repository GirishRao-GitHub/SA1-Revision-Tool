"""
batch_parse.py - Robust SA1 IFoA exam data parser
Handles actual raw_Q.txt / raw_S.txt format extracted from IFoA PDFs.
"""

import re, json, os, sys

SITTINGS = [
    ('201904', 'April 2019'),
    ('201909', 'September 2019'),
    ('202004', 'April 2020'),
    ('202009', 'September 2020'),
    ('202104', 'April 2021'),
    ('202109', 'September 2021'),
    ('202204', 'April 2022'),
    ('202209', 'September 2022'),
    ('202304', 'April 2023'),
    ('202309', 'September 2023'),
    ('202404', 'April 2024'),
    ('202409', 'September 2024'),
    ('202504', 'April 2025'),
]

TAXONOMY = [
    "Product Design (Protection)", "Product Design (Health & Care)",
    "Critical Illness", "Income Protection", "Private Medical Insurance (PMI)",
    "Long-Term Care (LTC)", "Pricing & Rating", "Reserving & Valuation",
    "Underwriting", "Claims Management", "Capital & Solvency",
    "Reinsurance", "Legislation & Taxation", "State Healthcare & Demographics",
    "Risk Management", "Professional Guidance"
]

THEME_HINTS = {
    "Critical Illness": ["critical illness", " ci ", "ci insurance", "sum insured"],
    "Income Protection": ["income protection", "sickness", "disability benefit", "replacement income"],
    "Private Medical Insurance (PMI)": ["private medical insurance", "pmi", "medical expenses", "hospital cash"],
    "Long-Term Care (LTC)": ["long.term care", "ltc", "care home", "long term care"],
    "Pricing & Rating": ["pricing", "premium rate", "rating factor", "underwriting cycle", "community rating"],
    "Reserving & Valuation": ["reserv", "solvency ii", "best estimate", "technical provision", "valuation"],
    "Capital & Solvency": ["capital", "scr", "mcr", "solvency", "own funds", "risk margin"],
    "Reinsurance": ["reinsurance", "reinsurer", "reinsur"],
    "Underwriting": ["underwriting", "underwrite", "medical history", "non-disclosure"],
    "Claims Management": ["claims management", "claim settlement", "claims experience"],
    "Legislation & Taxation": ["legislation", "regulation", "regulator", "tax", "gdpr", "data protection"],
    "State Healthcare & Demographics": ["state", "government", "demographic", "population", "nhs", "universal health"],
    "Risk Management": ["risk management", "orsa", "risk appetite", "operational risk", "cyber"],
    "Product Design (Protection)": ["product design", "product feature", "sum assured", "term assurance"],
    "Product Design (Health & Care)": ["product design", "benefit design", "indemnity", "cash plan"],
    "Professional Guidance": ["professional guidance", "actuarial", "apc", "code of conduct", "ethical"],
}

def clean_text(lines, is_solution=False):
    """Aggressively clean IFoA headers, footers, blank lines and fix orphan marks."""
    # 1. Strip whitespace from lines and join for initial processing
    text = "\n".join([line.rstrip() for line in lines])
    text = text.replace('\r', '\n')
    # 2. Truncate at first question marker
    # Look for a line that starts with 1 or Q1
    if is_solution:
        # Matches "Q1", "Question 1", "Question1", "1" on a new line
        pos = re.search(r'(?:\n|^)\s*(?:Question\s*|Q)?1(?:\s*\n|\s+[\(A-Za-z])', text, flags=re.I)
    else:
        # Matches "1 " or "1 (" at start of line
        pos = re.search(r'(?:\n|^)\s*1(?:\s+|\s*\()', text)
    
    if pos:
        text = text[pos.start():].strip()
    
    # 3. Collapse excessive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # 4. Pull up orphan marks [½] sitting on a line after whitespace/newlines
    text = re.sub(r'\n+\s*(\[\s*(?:½|1|1½|2|0\.5|1\.5|2\.5)\s*\])', r' \1', text)
    
    # 5. Strip IFoA Headers & Footers (Strict Line-by-line keyword matching)
    patterns = [
        r'---\s*PAGE\s+\d+\s*---',
        r'SA1\s+[AS]\d{4}',
        r'Institute and Faculty of Actuaries',
        r'© .*',
        r'www\.actuaries\.org\.uk',
        # Simple keywords anywhere in the line for headers
        r'Subject\s+S[AP]1.+?Examiners?.+?report',
        r'S[AP]1.+?Health.+?Care.+?Examiners?.+?report',
        r'EXAMINERS.?\s+REPORT.*Subject\s+S[AP]1',
        r'PLEASE\s+TURN\s+OVER',
        r'In\s+addition\s+to\s+this\s+paper\s+.*?edition\s+of\s+the\s+Formulae\s+and\s+Tables.*',
        r'In\s+addition\s+to\s+this\s+paper, you should read the instructions on the back.*',
        r'Solutions\s+for\s+Subject\s+S[AP]1\s+-\s+[A-Za-z]+\s+\d{4}',
    ]
    
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        # Remove noisy ampersands that often appear at line ends or on own line
        stripped = re.sub(r'\s*@\s*$', '', stripped)
        
        is_header = False
        for p in patterns:
            if re.search(p, stripped, flags=re.I):
                is_header = True
                break
        if not is_header and stripped:
            cleaned_lines.append(line.rstrip())
    
    text = '\n'.join(cleaned_lines)
    
    # 6. Truncate at Commentary or End markers for raw file visibility
    if is_solution:
        # For the raw file, we only want to strip global commentary/end-of-paper junk
        # but NOT per-question commentary that might be followed by another question.
        # So we look for "END OF PAPER" or a final "Commentary:" at the end.
        pass
    
    # 7. Bridge broken lines (paragraph joining)
    lines = text.split('\n')
    bridged = []
    for line in lines:
        line = line.strip()
        if not line:
            if bridged and bridged[-1]: bridged.append("")
            continue
        
        is_structural = re.match(r'^(?:Q|Question\s*)?([1-9][0-9]?)|^\([ivxlca-d1-4]{1,4}\)|^\[', line, re.I)
        if bridged and bridged[-1] and not is_structural and not bridged[-1].endswith(('.', ':', ']', ')')):
            bridged[-1] += " " + line
        else:
            bridged.append(line)
            
    final_lines = []
    for b in bridged:
        if b: final_lines.append(b)
        elif final_lines and final_lines[-1] != "": final_lines.append("")
        
    return '\n'.join(final_lines).strip()

def parse_questions(text):
    start_match = re.search(r'(?:\n|^)\s*([1-9][0-9]?)\s+(?=[A-Z\(])', text)
    if start_match:
        text = text[start_match.start():].strip()
    
    q_blocks = re.split(r'(?:\n|^)\s*([1-9][0-9]?)\s+(?=[A-Z\(])', text)
    questions = []
    i = 1
    while i < len(q_blocks):
        qnum = q_blocks[i]
        body = q_blocks[i+1] if i+1 < len(q_blocks) else ''
        i += 2
        
        part_split = re.split(r'((?:\n|^)\s*\([ivxlca-d1-4]{1,4}\))', body)
        scenario = part_split[0].strip()
        scenario = re.split(r'\bEND OF PAPER\b', scenario, flags=re.I)[0].strip()
        
        parts_list = []
        last_top_part = None
        current_scenario_prefix = ""
        j = 1
        while j < len(part_split):
            part_label = part_split[j].strip()
            part_body  = part_split[j+1] if j+1 < len(part_split) else ''
            j += 2
            
            # Split part_body into (Question with Marks) and (Trailing Scenario for next part)
            marks_it = list(re.finditer(r'\[\d+\]', part_body))
            if marks_it:
                last_mark_end = marks_it[-1].end()
                this_part_content = part_body[:last_mark_end].strip()
                trailing_scenario = part_body[last_mark_end:].strip()
            else:
                this_part_content = part_body.strip()
                trailing_scenario = ""
            
            # Prepend prefix from previous part (if any)
            full_part_text = f"{current_scenario_prefix}\n{this_part_content}".strip()
            current_scenario_prefix = trailing_scenario
            
            # Final marks and clean text for this part
            marks_matches = re.findall(r'\[(\d+)\]', full_part_text)
            marks = sum(int(m) for m in marks_matches) if marks_matches else 0
            
            p_text = re.sub(r'\[\d+\]', '', full_part_text).strip()
            p_text = re.split(r'\[Total\s+\d+\]', p_text, flags=re.I)[0].strip()
            
            # Rule: (a), (b), (c) etc. merge into the previous (i), (ii), etc.
            if re.match(r'^\([a-h]\)$', part_label, re.I) and last_top_part:
                last_top_part['text'] += f"\n{part_label} {p_text}"
                last_top_part['marks'] += marks
            else:
                new_part = {'part': part_label, 'text': p_text, 'marks': marks}
                parts_list.append(new_part)
                # Only treat roman numerals or numbers as "top level"
                if re.match(r'^\([ivx1-9]+\)$', part_label, re.I):
                    last_top_part = new_part
                else:
                    last_top_part = None
        
        # If any trailing scenario remains at the end of the question, it's just extra info
        # maybe append it back to the last part if it exists?
        if current_scenario_prefix and parts_list:
             cleaned_trailing = re.sub(r'(?i)\[Total\s+\d+\]', '', current_scenario_prefix)
             cleaned_trailing = re.sub(r'(?i)\bEND OF PAPER\b', '', cleaned_trailing)
             cleaned_trailing = re.sub(r'(?m)^[-–]\d+\s*$', '', cleaned_trailing)
             cleaned_trailing = cleaned_trailing.strip()
             if cleaned_trailing:
                 parts_list[-1]['text'] += f"\n{cleaned_trailing}"

        questions.append({'num': f'Q{qnum}', 'scenario': scenario, 'parts': parts_list})
    return questions

def parse_solutions(text):
    """Parse Solution text into dict: { 'Q1': { '(i)': [bullets] } }"""
    # 1. Split into question blocks (Q1, Q2, etc.)
    # We use a safer regex that requires "Q" or "Question" and a following newline/end
    # This prevents splitting on mentions like "Q1 (iv)" inside text
    q_blocks = re.split(r'(?:\n|^)\s*(?:Q|Question\s*)([1-9][0-9]*)(?:\s*\n|$)', text, flags=re.I)
    
    # If no Q-prefixed blocks found, try a more cautious bare number split
    if len(q_blocks) < 3:
        q_blocks = re.split(r'(?:\n|^)\s*([1-9][0-9]*)(?:\s*\n)', text)
    
    solutions = {}
    for i in range(1, len(q_blocks), 2):
        qnum = q_blocks[i]
        body = q_blocks[i+1]
        qkey = f'Q{qnum}'
        if qkey in solutions:
            # First match wins (avoids overwriting with commentary mentioning Q number)
            continue
        solutions[qkey] = {}
        
        # 2. Truncate at Commentary or start of examiner notes
        body = re.split(r'(?m)^\s*(?:Commentary:|Well-prepared|Candidates who|Most candidates|The examiners)', body, flags=re.I)[0]
        
        # 3. Split into parts: (i), (ii), (a), (b), etc.
        part_split = re.split(r'(?m)^\s*(\([ivxlca-h1-4]{1,4}\))', body)
        
        current_top_part = None
        for j in range(len(part_split)):
            p = part_split[j].strip()
            if not p: continue
            
            if re.match(r'^\([ivxlca-h1-4]{1,4}\)$', p):
                label = p
                # Check if this is a "child" part (a), (b), etc.
                if re.match(r'^\([a-h]\)$', label, re.I) and current_top_part:
                    # Keep it as child, but subsequent bullets go to current_top_part
                    pass
                elif re.match(r'^\([ivx1-9]+\)$', label, re.I):
                    current_top_part = label
                else:
                    # e.g. (a) without a parent, treat as top for now
                    current_top_part = label
            else:
                bullets = extract_bullets(p)
                if bullets:
                    target = current_top_part if current_top_part else "General"
                    if target not in solutions[qkey]:
                        solutions[qkey][target] = []
                    solutions[qkey][target].extend(bullets)
                    
    return solutions

def extract_bullets(text):
    # Cut off totals or trailing commentary junk inside the part block
    text = re.split(r'\[Marks available|\[Maximum|\[Max\s*\d+|\[Total\s+\d+|Commentary:', text, flags=re.I)[0]
    text = text.replace('1⁄2', '½').replace('1/2', '½')
    
    # More robust mark pattern to catch various brackets and fractional formats
    mark_pattern = r'(\[[\s½\d\.\-]*\])'
    parts = re.split(mark_pattern, text)
    
    bullets = []
    current = ''
    for part in parts:
        if re.match(mark_pattern, part.strip()):
            bullet_text = current.strip()
            bullet_text = re.sub(r'^[•·\-*]\s*', '', bullet_text).strip()
            if bullet_text:
                bullets.append(f"{bullet_text} {part.strip()}")
            current = ''
        else:
            current += part
    
    if current.strip():
        remainder = re.sub(r'^[•·\-*]\s*', '', current.strip()).strip()
        if len(remainder) > 3: 
            bullets.append(remainder)
    return [re.sub(r'\s+', ' ', b).strip() for b in bullets if b.strip()]

def guess_themes(text):
    text_lower = text.lower()
    themes = []
    for theme, hints in THEME_HINTS.items():
        for hint in hints:
            if re.search(hint, text_lower):
                themes.append(theme)
                break
    return themes[:3]

def build_sitting_json(sitting_key, sitting_label, data_dir):
    q_path = os.path.join(data_dir, sitting_key, 'raw_Q.txt')
    s_path = os.path.join(data_dir, sitting_key, 'raw_S.txt')
    
    with open(q_path, encoding='utf-8') as f:
        q_lines = f.readlines()
    q_text = clean_text(q_lines, is_solution=False)
    with open(q_path, 'w', encoding='utf-8') as f:
        f.write(q_text)
    
    s_text = ""
    has_solutions = False
    if os.path.exists(s_path):
        with open(s_path, encoding='utf-8') as f:
            s_lines = f.readlines()
        if len(s_lines) > 5:
            s_text = clean_text(s_lines, is_solution=True)
            with open(s_path, 'w', encoding='utf-8') as f:
                f.write(s_text)
            has_solutions = True
    
    questions_data = parse_questions(q_text)
    solutions_data = parse_solutions(s_text) if has_solutions else {}
    
    questions_obj = {}
    for qd in questions_data:
        qkey = qd['num']
        total_marks = sum(p['marks'] for p in qd['parts'])
        full_text = qd['scenario'] + ' ' + ' '.join(p['text'] for p in qd['parts'])
        q_themes = guess_themes(full_text)
        
        parts_obj = {}
        for pd in qd['parts']:
            part_label = pd['part']
            sol_bullets = solutions_data.get(qkey, {}).get(part_label, [])
            p_themes = guess_themes(pd['text'])
            parts_obj[part_label] = {
                'partLabel': part_label,
                'marks': pd['marks'],
                'question': pd['text'],
                'synopsis': f"Auto-generated synopsis for {qkey} {part_label}",
                'themes': p_themes,
                'sections': {'Solution': sol_bullets}
            }
        
        questions_obj[qkey] = {
            'label': f'Question {qkey[1:]}',
            'marks': total_marks,
            'scenario': qd['scenario'],
            'synopsis': f"Auto-generated synopsis for {qkey}",
            'themes': q_themes,
            'parts': parts_obj
        }
    return {'label': sitting_label, 'questions': questions_obj}

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('sitting', nargs='?', help='Specific sitting key (e.g. 201904)')
    parser.add_argument('--dir', default='data', help='Data directory')
    args = parser.parse_args()
    
    data_dir = args.dir
    report_rows = []
    
    targets = SITTINGS
    if args.sitting:
        targets = [s for s in SITTINGS if s[0] == args.sitting]
        if not targets:
            print(f"Error: Sitting {args.sitting} not found.")
            return

    for sitting_key, sitting_label in targets:
        json_path = os.path.join(data_dir, f'{sitting_key}.json')
        print(f"[PARSE] {sitting_label} ...", end=' ')
        try:
            result = build_sitting_json(sitting_key, sitting_label, data_dir)
            qs = result.get('questions', {})
            q_count = len(qs)
            parts_count = sum(len(qv.get('parts', {})) for qv in qs.values())
            parts_with_sol = sum(1 for qv in qs.values() for pv in qv.get('parts', {}).values() if pv.get('sections', {}).get('Solution'))
            total_marks = sum(qv.get('marks', 0) for qv in qs.values())
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"OK — {q_count}Q, {total_marks} Marks")
            report_rows.append((sitting_label, q_count, parts_count, parts_with_sol, total_marks, 'OK'))
        except Exception as e:
            print(f"ERROR: {e}")
            report_rows.append((sitting_label, 0, 0, 0, 0, f'ERROR: {e}'))
    
    print('\n' + '='*78)
    print(f"{'Sitting':<22} {'Qs':>3} {'Parts':>5} {'W/Sol':>5} {'Marks':>5}  Status")
    print('-'*78)
    for r in report_rows:
        print(f"{r[0]:<22} {r[1]:>3} {r[2]:>5} {r[3]:>5} {r[4]:>5}  {r[5]}")
    print('='*78)

if __name__ == '__main__':
    main()
