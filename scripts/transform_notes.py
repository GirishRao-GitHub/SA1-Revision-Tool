import json
import re
import os

def parse_markdown(file_path):
    """Parses raw markdown into a list of structured nodes, filtering out textbook noise."""
    nodes = []
    
    # Aggressive and Targeted noise patterns
    NOISE_PATTERNS = [
        r"(?i)page\s+[\d\=\\_\s]+.*$",
        r"(?i)^the\s+actuarial\s+education\s+company",
        r"(?i)^[do]?ife:?\s*\d{4}\s*examinations", 
        r"(?i)^sa1-\d+",
        r"(?i)^sat[o]?\s*[\d\s]*",
        r"^\s*\d+\s*$",
        r"(?i)actuarial\s+education\s+company",
        r"(?i)^2024\s+examinations",
        r"(?i)^nal\s+of\s+men",
        r"(?i)^dife\s+\d+",
        r"^\s*[\*\s\-\.\/\\]+\s*$",
        r"^\s*\(this\s+is\s+only\s+part\s+of\s+syllabus\s+objective.*\)\s*$",
        r"(?i)^short\s*term\s*health\s*and\s*care\s*insurance\s*products\s*$"
    ]

    if not os.path.exists(file_path):
        return []

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        if not line: continue
            
        # 1. PRE-CLEAN for matching
        line = line.replace('\u00a0', ' ').replace('\u2013', '-').replace('\u2014', '-')
        line = line.replace('**', '').replace('\\-', '-').replace('\\.', '.').replace('\\_', '_').replace('\\', '')
        line = line.strip()
        
        # 2. MATCH NOISE
        if any(re.search(pattern, line, re.IGNORECASE) for pattern in NOISE_PATTERNS):
            continue
            
        # 3. EXTRA CLEAN
        if len(line) < 3 and not line.isdigit():
            continue
        if line.isdigit() and len(line) < 3:
            continue

        header_match = re.match(r'^(\d+(\.\d+)?)\s+(.+)', line)
        if header_match:
            level = header_match.group(2)
            text = header_match.group(3).strip()
            num = header_match.group(1)
            type_tag = "h3" if not level else "h4"
            nodes.append({"type": type_tag, "text": f"{num} {text}"})
            continue
            
        if line.lower() == "question":
            nodes.append({"type": "h4", "text": "Question"})
            continue
        if line.lower() == "solution":
            nodes.append({"type": "h4", "text": "Solution"})
            continue
            
        nodes.append({"type": "point", "text": line})
                
    return nodes, len(lines)

def transform_chapter(chapter_id, md_path, notes_json_path):
    """Stage 1: Clean raw notes and save to intermediate JSON."""
    print(f"\n--- STAGE 1: TRANSFORMATION [{chapter_id}] ---")
    print(f"Reading from: {md_path}")
    
    nodes, raw_line_count = parse_markdown(md_path)
    if not nodes:
        print("Error: No nodes extracted.")
        return
        
    if os.path.exists(notes_json_path):
        with open(notes_json_path, 'r', encoding='utf-8') as f:
            notes_data = json.load(f)
    else:
        notes_data = {"Chapters": {}}
        
    if "Chapters" not in notes_data: notes_data["Chapters"] = {}
    
    notes_data["Chapters"][chapter_id] = {
        "title": nodes[0]["text"] if nodes and "text" in nodes[0] else chapter_id,
        "content": nodes
    }
    
    with open(notes_json_path, 'w', encoding='utf-8') as f:
        json.dump(notes_data, f, indent=2)
    
    # RECONCILIATION
    print(f"RECONCILIATION [Stage 1]:")
    print(f"  - Raw Lines Filtered: {raw_line_count}")
    print(f"  - Nodes Extracted:    {len(nodes)}")
    print(f"  - Result Saved To:   {notes_json_path}")

if __name__ == "__main__":
    B = r"g:\Girish\IAI\SP1 and SA1 Health and Care"
    W = os.path.join(B, "Practice papers", "Claude Widgets")
    
    # Process Chapter 3
    CH3_MD = os.path.join(B, "SA1 Health and Care Advanced", "SA1 Course Material", "SA1 Ch3", "SA1 Ch3.md")
    NOTES_JSON = os.path.join(W, "data", "SA1_Revision_Notes.json")
    
    transform_chapter("Ch3", CH3_MD, NOTES_JSON)
