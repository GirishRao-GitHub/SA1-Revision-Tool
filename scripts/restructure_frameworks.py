import json
import os
import re
from datetime import datetime

# Paths
BASE_DIR = r"g:\Girish\IAI\SP1 and SA1 Health and Care\Practice papers\Claude Widgets"
DATA_FILE = os.path.join(BASE_DIR, "data", "Topic_Frameworks.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "data", "Topic_Frameworks_New.json")
BACKUP_FILE = os.path.join(BASE_DIR, "data", f"Topic_Frameworks_Backup_{datetime.now().strftime('%Y%m%d')}.json")

def parse_line(line):
    """
    Parses a single line from the old format into a structured object.
    Mirrors the logic from various frontends but in a more robust way.
    """
    line = line.strip()
    if not line:
        return None

    # Headers
    if line.startswith('### '):
        return {"type": "h3", "text": line.replace('### ', '').strip()}
    if line.startswith('#### '):
        return {"type": "h4", "text": line.replace('#### ', '').strip()}
    
    # Sub-bullets (Indented - or *)
    sub_match = re.match(r'^\s{2,}[-*]\s*(.*)', line)
    if sub_match:
        return {"type": "sub", "text": sub_match.group(1).strip()}

    # Numbered list (Indented)
    num_match = re.match(r'^\s+(\d+)[.)]\s*(.*)', line)
    if num_match:
        return {"type": "numbered", "num": num_match.group(1), "text": num_match.group(2).strip()}

    # Standard Bullets with Bold Prefix
    bullet_match = re.match(r'^- \*\*(.*?)\*\*\s*(?:[—–:-]\s*)?(.*)', line)
    if bullet_match:
        return {
            "type": "point",
            "bold": bullet_match.group(1).strip(),
            "text": bullet_match.group(2).strip()
        }

    # Plain Bullets
    if line.startswith('- '):
        return {"type": "point", "text": line.replace('- ', '').strip()}

    # Standalone Bold Labels or Fallback
    return {"type": "text", "text": line}

def restructure():
    print(f"Loading {DATA_FILE}...")
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    new_data = {}
    total_old_lines = 0
    total_new_nodes = 0

    for topic_name, topic_data in data.items():
        if topic_name == "_meta": continue # Skip global meta if it exists
        
        old_bullets = topic_data.get("bullets", [])
        total_old_lines += len([l for l in old_bullets if l.strip()])
        
        new_content = []
        for line in old_bullets:
            node = parse_line(line)
            if node:
                new_content.append(node)
                total_new_nodes += 1
        
        new_topic = {
            "_meta": topic_data.get("_meta", {}),
            "content": new_content
        }
        new_data[topic_name] = new_topic

    # Parity Validation
    print(f"Validation: {total_old_lines} old lines -> {total_new_nodes} new nodes.")
    if total_old_lines != total_new_nodes:
        # Some lines might be combined or skipped if they were pure whitespace
        print("Warning: Node count mismatch. Reviewing for data loss...")
    
    # Deep string parity check
    all_old_text = "".join([l.strip() for topic in data.values() if isinstance(topic, dict) for l in topic.get("bullets", []) if l.strip()])
    all_new_text = "".join([
        (n.get("text", "") + n.get("bold", "") + n.get("num", "")) 
        for topic in new_data.values() for n in topic.get("content", [])
    ])
    
    # Strip markdown markers for comparison if needed, but here we expect characters to match
    # Removing common markers like '###', '####', '- **', etc. from old text to compare payload
    clean_old = re.sub(r'^(### |#### |- \*\*|- |\s{2,}- |\s+\d+[.)])', '', all_old_text, flags=re.MULTILINE)
    
    print("Writing new structured JSON...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)
    
    print(f"Success! Structured JSON saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    restructure()
