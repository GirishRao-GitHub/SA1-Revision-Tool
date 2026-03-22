import json
import glob
import os
import sys

def get_next_batch():
    files = sorted(glob.glob('data/20*.json'))
    
    # Check if we have a tracking file
    if not os.path.exists('data/ai_progress.json'):
        with open('data/ai_progress.json', 'w') as f:
            json.dump({"processed": []}, f)
            
    with open('data/ai_progress.json', 'r') as f:
        progress = json.load(f)
        
    for file in files:
        sitting = os.path.basename(file).replace('.json', '')
        if sitting in progress['processed']:
            continue
            
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        print(f"--- SITTING: {sitting} ---")
        prompt = ""
        questions = data.get('questions', {})
        for qk, qv in questions.items():
            if 'parts' in qv:
                for pk, pv in qv['parts'].items():
                    prompt += f"\n--- {qk} {pk} ---\n"
                    # We only need the examiner points to categorize
                    points = []
                    if 'sections' in pv:
                        for sk, sv in pv['sections'].items():
                            points.extend(sv)
                    # Limit to top 8 distinct points to save AI context window
                    prompt += "\n".join([f"- {p[:150]}..." for p in points[:8]]) + "\n"
            else:
                 prompt += f"\n--- {qk} ---\n"
                 points = []
                 if 'sections' in qv:
                     for sk, sv in qv['sections'].items():
                         points.extend(sv)
                 prompt += "\n".join([f"- {p[:150]}..." for p in points[:8]]) + "\n"
                 
        with open('data/ai_prompt.txt', 'w', encoding='utf-8') as f:
            f.write(f"--- SITTING: {sitting} ---\n" + prompt)
        print(f"Generated prompt for {sitting} in data/ai_prompt.txt")
        sys.exit(0)
        
    print("ALL DONE")
    
if __name__ == "__main__":
    get_next_batch()
