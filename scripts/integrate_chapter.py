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
                
    return nodes

def transform_chapter(chapter_id, md_path, notes_json_path):
    """Stage 1: Clean raw notes and save to intermediate JSON."""
    print(f"Stage 1: Transforming {chapter_id} from {md_path}...")
    
    nodes = parse_markdown(md_path)
    if not nodes:
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
    print(f"  --> Saved to {notes_json_path}")

def unify_syllabus(chapter_id, notes_json_path, topics_path, unified_path):
    """Stage 2: Merge cleaned notes with synthesis and save to final JSON."""
    print(f"Stage 2: Unifying {chapter_id} with synthesis...")
    
    if not os.path.exists(notes_json_path):
        print(f"Error: {notes_json_path} not found. Run Stage 1 first.")
        return
        
    with open(notes_json_path, 'r', encoding='utf-8') as f:
        notes_data = json.load(f)
        
    chapter_data = notes_data.get("Chapters", {}).get(chapter_id)
    if not chapter_data:
        print(f"Error: Chapter {chapter_id} not found in {notes_json_path}")
        return
        
    with open(topics_path, 'r', encoding='utf-8') as f:
        topics_data = json.load(f)
        
    KEYWORDS = {
        "Private medical insurance": ["Pricing", "Product Design"],
        "Health cash plans": ["Pricing"],
        "Major medical expense": ["Pricing", "Product Design"],
        "Claims": ["Claims Management"],
        "Underwriting": ["Pricing"],
        "Selection": ["Pricing"],
        "Regulation": ["Regulation"]
    }
    
    final_nodes = []
    nodes = chapter_data["content"]
    
    # Interweave
    added_in_section = set()
    for node in nodes:
        if node["type"] in ["h3", "h4"]:
            added_in_section = set()
            
        final_nodes.append(node)
        
        node_text = node.get("text", "").lower()
        if len(node_text) < 30 and node["type"] == "point":
            continue

        for key, themes in KEYWORDS.items():
            if key.lower() in node_text:
                for theme_name in themes:
                    if theme_name in added_in_section: continue
                        
                    theme_data = topics_data.get(theme_name, {})
                    if theme_data:
                        theme_points = [n for n in theme_data.get("content", []) if n.get("type") == "point"]
                        if theme_points:
                            teaser = theme_points[0].copy()
                            teaser_text = teaser.get("text", "")
                            
                            if "IAI" in teaser_text: source_tag = "IAI_Synthesis"
                            elif "IFoA" in teaser_text: source_tag = "IFoA_Synthesis"
                            else: source_tag = "Notes"
                                
                            teaser["bold"] = f"Expert Insight: {theme_name}"
                            teaser["text"] = teaser_text + f" [src:{source_tag}]"
                            final_nodes.append(teaser)
                            added_in_section.add(theme_name)
                            break
    
    if os.path.exists(unified_path):
        with open(unified_path, 'r', encoding='utf-8') as f:
            full_data = json.load(f)
    else:
        full_data = {"Chapters": {}}
    
    if "Chapters" not in full_data: full_data["Chapters"] = {}
        
    full_data["Chapters"][chapter_id] = {
        "title": chapter_data["title"],
        "content": final_nodes
    }
    
    with open(unified_path, 'w', encoding='utf-8') as f:
        json.dump(full_data, f, indent=2)
    print(f"  --> Saved to {unified_path}")

if __name__ == "__main__":
    B = r"g:\Girish\IAI\SP1 and SA1 Health and Care"
    W = os.path.join(B, "Practice papers", "Claude Widgets")
    
    CH3_MD = os.path.join(B, "SA1 Health and Care Advanced", "SA1 Course Material", "SA1 Ch3", "SA1 Ch3.md")
    NOTES_JSON = os.path.join(W, "data", "SA1_Revision_Notes.json")
    TOPICS_JSON = os.path.join(W, "data", "Topic_Frameworks.json")
    UNIFIED_JSON = os.path.join(W, "data", "Unified_Syllabus.json")
    
    # Step 1: Transform
    transform_chapter("Ch3", CH3_MD, NOTES_JSON)
    
    # Step 2: Unify
    unify_syllabus("Ch3", NOTES_JSON, TOPICS_JSON, UNIFIED_JSON)
