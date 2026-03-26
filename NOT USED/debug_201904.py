import re
import os

def extract_bullets(text):
    text = re.split(r'\[Marks available|\[Maximum|\[Max\s*\d+|\[Total\s+\d+|Commentary:', text, flags=re.I)[0]
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
    return bullets

with open('data/201904/raw_S.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Using the EXACT SAME regex as batch_parse.py
q_blocks = re.split(r'(?:\n|^)\s*(?:Q|Question\s+)([1-9][0-9]*)(?:\s+|\n|$)', text, flags=re.I)
if len(q_blocks) < 3:
    q_blocks = re.split(r'(?:\n|^)\s*([1-9][0-9]*)(?:\s*\n)', text)

print(f"Number of q_blocks found: {len(q_blocks)}")
for idx in range(1, len(q_blocks), 2):
    q_num = q_blocks[idx]
    q_body = q_blocks[idx+1]
    print(f"\n--- Q{q_num} block (length {len(q_body)}) ---")
    
    print(f"Sample: {repr(q_body[:100])}")
    
    body_trunc = re.split(r'(?m)^\s*(?:Commentary:|Well-prepared|Candidates who|Most candidates|The examiners|Part\s+\([ivx]+\)\s+was)', q_body, flags=re.I)[0]
    print(f"Body length after truncation: {len(body_trunc)}")
    
    ps = re.split(r'(?m)^\s*(\([ivxlca-d1-4]{1,4}\))', body_trunc)
    print(f"Parts found for Q{q_num}: {[p for p in ps if re.match(r'^\(.*\)$', p.strip())]}")
