import json
import re
import os

def unify_syllabus(chapter_id, notes_json_path, topics_path, unified_path):
    """Stage 2: Merge cleaned notes with synthesis and save to final JSON."""
    print(f"Stage 2: Unifying {chapter_id} with synthesis...")
    
    if not os.path.exists(notes_json_path):
        print(f"Error: {notes_json_path} not found. Run transform_notes.py first.")
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
    print(f"  --> Unified {chapter_id} saved to {unified_path}")

if __name__ == "__main__":
    B = r"g:\Girish\IAI\SP1 and SA1 Health and Care"
    W = os.path.join(B, "Practice papers", "Claude Widgets")
    
    NOTES_JSON = os.path.join(W, "data", "SA1_Revision_Notes.json")
    TOPICS_JSON = os.path.join(W, "data", "Topic_Frameworks.json")
    UNIFIED_JSON = os.path.join(W, "data", "Unified_Syllabus.json")
    
    unify_syllabus("Ch3", NOTES_JSON, TOPICS_JSON, UNIFIED_JSON)
