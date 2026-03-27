import json
import os
import re

# Paths
BASE_DIR = "g:\\Girish\\IAI\\SP1 and SA1 Health and Care\\Practice papers\\Claude Widgets"
THEMES_PATH = os.path.join(BASE_DIR, "data", "Topic_Frameworks.json")
STRUCTURE_PATH = os.path.join(BASE_DIR, "data", "Syllabus_Structure.json")
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "Unified_Syllabus.json")

def load_json(path):
    if not os.path.exists(path): return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def parse_markdown(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    content = []
    
    for line in lines:
        line = line.strip()
        if not line: continue
        
        # Simple Header Detection (e.g., "1  Private medical insurance", "1.1 Benefits and features")
        header_match = re.match(r'^(\d+(\.\d+)?)\s+(.+)', line)
        if header_match:
            level = header_match.group(2)
            text = header_match.group(3).strip()
            num = header_match.group(1)
            type_tag = "h3" if not level else "h4"
            content.append({"type": type_tag, "text": f"{num} {text}"})
            continue
            
        # Question / Solution Detection
        if line.lower() == "question":
            content.append({"type": "h4", "text": "Question"})
            continue
        if line.lower() == "solution":
            content.append({"type": "h4", "text": "Solution"})
            continue
            
        # Bullet points or normal text
        if line.startswith("-") or line.startswith("*"):
            text = re.sub(r'^[-*]\s*', '', line)
            content.append({"type": "point", "text": text})
        else:
            # Check for bold starts
            bold_match = re.match(r'^\*\*(.*?)\*\*\s*(.*)', line)
            if bold_match:
                content.append({"type": "point", "bold": bold_match.group(1), "text": bold_match.group(2)})
            else:
                content.append({"type": "point", "text": line})
                
    return content

def integrate_chapter(chapter_id, markdown_path, theme_keywords=None):
    themes = load_json(THEMES_PATH)
    structure = load_json(STRUCTURE_PATH)
    
    chapter_info = structure.get("Chapters", {}).get(chapter_id, {})
    title = chapter_info.get("title", f"Chapter {chapter_id}")
    
    # Parse Core Content
    core_content = parse_markdown(markdown_path)
    
    # Interweaving Logic
    integrated_content = []
    
    # Standard: Add Six Pillar Overview at the start
    pillars = themes.get("The Six Pillar Framework (P1-P6)", {}).get("content", [])
    if pillars:
        integrated_content.append({"type": "text", "text": "***Expert Synthesis: Six Pillar Framework*** [src:IAI_Master]"})
        count = 0
        for node in pillars:
            if node.get("type") in ["point", "sub"]:
                new_node = node.copy()
                new_node["text"] = new_node.get("text", "") + " [src:IAI_Synthesis]"
                integrated_content.append(new_node)
                count += 1
            if count >= 3: break # Just a teaser for pillars

    # Interleave based on keywords
    for node in core_content:
        integrated_content.append(node)
        
        # If node is a header, check for related theme content
        if node["type"] in ["h3", "h4"] and theme_keywords:
            text = node["text"].lower()
            for keyword, theme_name in theme_keywords.items():
                if keyword.lower() in text:
                    theme_content = themes.get(theme_name, {}).get("content", [])
                    if theme_content:
                        integrated_content.append({"type": "text", "text": f"***Expert Insights: {theme_name}*** [src:IFoA_Link]"})
                        count = 0
                        for t_node in theme_content:
                            if t_node.get("type") in ["point", "sub"]:
                                # Check if t_node text contains specific keyword to keep it relevant
                                if keyword.lower() in t_node.get("text", "").lower() or keyword.lower() in t_node.get("bold", "").lower():
                                    new_node = t_node.copy()
                                    new_node["text"] = new_node.get("text", "") + f" [src:Synthesis_{theme_name}]"
                                    integrated_content.append(new_node)
                                    count += 1
                            if count >= 5: break

    # Save to Unified Syllabus
    unified = load_json(OUTPUT_PATH)
    if "Chapters" not in unified: unified["Chapters"] = {}
    
    unified["Chapters"][chapter_id] = {
        "title": title,
        "content": integrated_content
    }
    
    save_json(unified, OUTPUT_PATH)
    print(f"Chapter {chapter_id} Integrated Successfully.")

if __name__ == "__main__":
    # Integration for Chapter 3
    CH3_MD = "g:\\Girish\\IAI\\SP1 and SA1 Health and Care\\SA1 Health and Care Advanced\\SA1 Course Material\\SA1 Ch3\\SA1 Ch3.md"
    KEYWORDS = {
        "Private medical insurance": "Pricing",
        "Health cash plans": "Pricing",
        "Major medical expense": "Pricing",
        "Claims": "Claims Management",
        "Underwriting": "Pricing",
        "Regulation": "Regulation"
    }
    integrate_chapter("Ch3", CH3_MD, theme_keywords=KEYWORDS)
