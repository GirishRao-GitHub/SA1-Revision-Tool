import os, re

DATA_DIR = r"g:/Girish/IAI/SP1 and SA1 Health and Care/Practice papers/Claude Widgets/data"

def clean_q(text):
    # Remove "In addition to this paper..."
    text = re.sub(r'In addition to this paper.*list\.', '', text, flags=re.I | re.DOTALL)
    # Strip until the first question (1 or Q1)
    # Looking for a line starting with 1 followed by a capital letter
    match = re.search(r'(?:\n|^)\s*(?:Q|Question\s*)?1\s+(?=[A-Z])', text, flags=re.I)
    if match:
        return text[match.start():].strip()
    return text.strip()

def clean_s(text):
    # Strip until Solutions or Q1
    match = re.search(r'(?:Solutions|Q1)', text, re.I)
    if match:
        return text[match.start():].strip()
    return text.strip()

for folder in os.listdir(DATA_DIR):
    folder_path = os.path.join(DATA_DIR, folder)
    if os.path.isdir(folder_path):
        q_path = os.path.join(folder_path, "raw_Q.txt")
        s_path = os.path.join(folder_path, "raw_S.txt")
        
        if os.path.exists(q_path):
            with open(q_path, 'r', encoding='utf-8') as f:
                content = f.read()
            cleaned = clean_q(content)
            with open(q_path, 'w', encoding='utf-8') as f:
                f.write(cleaned)
            print(f"Cleaned {q_path}")
            
        if os.path.exists(s_path):
            with open(s_path, 'r', encoding='utf-8') as f:
                content = f.read()
            cleaned = clean_s(content)
            with open(s_path, 'w', encoding='utf-8') as f:
                f.write(cleaned)
            print(f"Cleaned {s_path}")
