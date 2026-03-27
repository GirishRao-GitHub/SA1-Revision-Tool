import json
import re
import os

def unify_syllabus(chapter_id, unified_path, topics_path):
    """Stage 3: Interweave synthesis into the already staged Unified_Syllabus.json."""
    print(f"\n--- STAGE 3: UNIFICATION [{chapter_id}] ---")
    
    if not os.path.exists(unified_path):
        print(f"Error: {unified_path} not found. Run stage_unified.py first.")
        return
        
    with open(unified_path, 'r', encoding='utf-8') as f:
        full_data = json.load(f)
        
    chapter_data = full_data.get("Chapters", {}).get(chapter_id)
    if not chapter_data:
        print(f"Error: Chapter {chapter_id} not found in {unified_path}")
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
    initial_node_count = len(nodes)
    synthesis_nodes_added = 0
    
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
                            synthesis_nodes_added += 1
                            break
    
    full_data["Chapters"][chapter_id] = {
        "title": chapter_data["title"],
        "content": final_nodes
    }
    
    with open(unified_path, 'w', encoding='utf-8') as f:
        json.dump(full_data, f, indent=2)
    
    # RECONCILIATION
    print(f"RECONCILIATION [Stage 3]:")
    print(f"  - Initial Nodes:      {initial_node_count}")
    print(f"  - Synthesis Added:    {synthesis_nodes_added}")
    print(f"  - Final Node Count:   {len(final_nodes)}")
    print(f"  - Result Saved To:   {unified_path}")

if __name__ == "__main__":
    B = r"g:\Girish\IAI\SP1 and SA1 Health and Care"
    W = os.path.join(B, "Practice papers", "Claude Widgets")
    
    TOPICS_JSON = os.path.join(W, "data", "Topic_Frameworks.json")
    UNIFIED_JSON = os.path.join(W, "data", "Unified_Syllabus.json")
    
    unify_syllabus("Ch3", UNIFIED_JSON, TOPICS_JSON)
