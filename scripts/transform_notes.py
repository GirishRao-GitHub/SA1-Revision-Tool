import json
import re
import os

def parse_markdown_enhanced(file_path):
    """
    Parses raw markdown into a list of structured nodes with automated paraphrasing.
    - Joins sentences broken across lines.
    - Filters out textbook noise and 'introductory' filler.
    - Distills paragraphs into bullet points.
    """
    if not os.path.exists(file_path):
        return [], 0

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    raw_line_count = len(lines)
    
    # Noise patterns (Same as before but with minor additions)
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
    
    # Filler patterns to remove (Summarization logic)
    FILLER_PATTERNS = [
        r"(?i)^this\s+chapter\s+follows\s+on\s+from",
        r"(?i)^we\s+will\s+consider\s+a\s+product",
        r"(?i)^introduction$",
        r"(?i)^this\s+chapter\s+describes",
        r"(?i)^the\s+aim\s+of\s+this\s+chapter"
    ]

    intermediate_lines = []
    
    for line in lines:
        line = line.strip()
        if not line: continue
            
        # 1. CLEANING
        line = line.replace('\u00a0', ' ').replace('\u2013', '-').replace('\u2014', '-')
        line = line.replace('**', '').replace('\\-', '-').replace('\\.', '.').replace('\\_', '_').replace('\\', '')
        line = line.strip()
        
        # 2. NOISE FILTERING
        if any(re.search(pattern, line, re.IGNORECASE) for pattern in NOISE_PATTERNS):
            continue
        if any(re.search(pattern, line, re.IGNORECASE) for pattern in FILLER_PATTERNS):
            continue
            
        # 3. EXTRA CLEAN
        if len(line) < 3 and not line.isdigit():
            continue
            
        intermediate_lines.append(line)

    # 4. SENTENCE RECONSTRUCTION (Joining broken lines)
    final_nodes = []
    buffer = ""
    
    def flush_buffer(buf):
        if not buf: return
        # Simple distilling: if it's very long, split into key points if possible (basic heuristic)
        buf = buf.strip()
        if buf:
            final_nodes.append({"type": "point", "text": buf})

    for line in intermediate_lines:
        # Header detection
        header_match = re.match(r'^(\d+(\.\d+)?)\s+(.+)', line)
        if header_match or line.lower() in ["question", "solution"]:
            flush_buffer(buffer)
            buffer = ""
            
            if header_match:
                num = header_match.group(1)
                text = header_match.group(3).strip()
                type_tag = "h3" if not header_match.group(2) else "h4"
                final_nodes.append({"type": type_tag, "text": f"{num} {text}"})
            else:
                final_nodes.append({"type": "h4", "text": line.capitalize()})
            continue

        # If line starts with a bullet marker or looks like a new list item
        if line.startswith(('-', '*', '+')) or (len(line) > 0 and line[0].isupper() and buffer.endswith('.')):
            flush_buffer(buffer)
            buffer = line.lstrip('-*+ ').strip()
        else:
            # Append to buffer with a space, rebuilding the sentence
            if buffer:
                buffer += " " + line
            else:
                buffer = line

    flush_buffer(buffer)
    
    return final_nodes, raw_line_count

def transform_chapter(chapter_id, md_path, notes_json_path):
    """Stage 1: Transform with Automated Extraction Logic."""
    print(f"\n--- STAGE 1: AUTOMATED EXTRACTION [{chapter_id}] ---")
    
    nodes, raw_count = parse_markdown_enhanced(md_path)
    if not nodes:
        print("Error: Extraction resulted in 0 nodes.")
        return
        
    if os.path.exists(notes_json_path):
        with open(notes_json_path, 'r', encoding='utf-8') as f:
            try:
                notes_data = json.load(f)
            except json.JSONDecodeError:
                notes_data = {"Chapters": {}}
    else:
        notes_data = {"Chapters": {}}

    # 5. TITLE EXTRACTION (Take shorter first point if possible)
    extracted_title = chapter_id
    if nodes and "text" in nodes[0]:
        first_text = nodes[0]["text"]
        # Split by common title separators or limit length
        clean_title = first_text.split("Syllabus objectives")[0].split("\n")[0].strip()
        if len(clean_title) > 60:
            clean_title = clean_title[:57] + "..."
        extracted_title = clean_title if clean_title else chapter_id

    notes_data["Chapters"][chapter_id] = {
        "title": extracted_title,
        "content": nodes
    }
    
    with open(notes_json_path, 'w', encoding='utf-8') as f:
        json.dump(notes_data, f, indent=2)
    
    print(f"RECONCILIATION [Stage 1 - Automated]:")
    print(f"  - Raw Lines Input:    {raw_count}")
    print(f"  - Extracted Nodes:    {len(nodes)}")
    print(f"  - Mode:              Intelligent Extraction (Non-Verbatim)")

if __name__ == "__main__":
    B = r"g:\Girish\IAI\SP1 and SA1 Health and Care"
    W = os.path.join(B, "Practice papers", "Claude Widgets")
    CH3_MD = os.path.join(B, "SA1 Health and Care Advanced", "SA1 Course Material", "SA1 Ch3", "SA1 Ch3.md")
    NOTES_JSON = os.path.join(W, "data", "SA1_Revision_Notes.json")
    
    transform_chapter("Ch3", CH3_MD, NOTES_JSON)
