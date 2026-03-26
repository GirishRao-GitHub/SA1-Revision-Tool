import os
import json
import re

def extract_sittings(html_path, prefix="iai"):
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Try to find the SITTINGS object. It usually starts with const SITTINGS = {
    # and ends with };
    match = re.search(r"const SITTINGS = ({[\s\S]+?});", content)
    if not match:
        print(f"Could not find SITTINGS in {html_path}")
        return
    
    sittings_str = match.group(1)
    
    # We need to turn this JS object into valid JSON.
    # 1. Add quotes to keys if they don't have them.
    # 2. Remove trailing commas.
    # This is tricky with regex. A better way might be a small JS script if we had node.
    # But since we're in Python, let's try a simpler approach if the JS is relatively clean.
    
    # Simple cleanup for common JS objects
    # This is a bit risky but often works for these study tools.
    clean_str = sittings_str
    # Quote keys
    clean_str = re.sub(r'(\s+)([a-zA-Z0-9_]+):', r'\1"\2":', clean_str)
    # Remove trailing commas before closing braces/brackets
    clean_str = re.sub(r',\s*([}\]])', r'\1', clean_str)
    
    try:
        sittings = json.loads(clean_str)
        for key, value in sittings.items():
            filename = f"iai_{key}.json" if not key.startswith("iai") else f"{key}.json"
            # Ensure it has a label
            if "label" not in value:
                value["label"] = f"IAI {key}"
            
            with open(os.path.join("data", filename), "w", encoding="utf-8") as out:
                json.dump(value, out, indent=2)
            print(f"Extracted {filename}")
        return list(sittings.keys())
    except Exception as e:
        print(f"Error parsing JSON from {html_path}: {e}")
        # If it fails, we might need a more specialized parser or manual extraction.
        return []

# Run extraction
os.makedirs("data", exist_ok=True)
s1 = extract_sittings("IAI SA1 Exam Revision Tool 2006-2016.html")
s2 = extract_sittings("IAI SA1 Exam Revision Tool 2017-2025.html")

print("\nAll extracted keys:", (s1 or []) + (s2 or []))
