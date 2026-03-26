import json
import sys
import os

def apply_patch(sitting, json_patch_str):
    try:
        patch = json.loads(json_patch_str)
        filepath = f'data/{sitting}.json'
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for qk, qparts in patch.items():
            if 'parts' in data['questions'].get(qk, {}):
                for pk, synopsis in qparts.items():
                    if pk in data['questions'][qk]['parts']:
                        data['questions'][qk]['parts'][pk]['synopsis'] = synopsis
            else:
                data['questions'][qk]['synopsis'] = qparts
                
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        # Update progress
        with open('data/ai_progress.json', 'r') as f:
            prog = json.load(f)
        if sitting not in prog['processed']:
            prog['processed'].append(sitting)
        with open('data/ai_progress.json', 'w') as f:
            json.dump(prog, f)
            
        print(f"Successfully applied synopses to {sitting}")
    except Exception as e:
        print(f"Error applying patch to {sitting}: {e}")

if __name__ == "__main__":
    sitting = sys.argv[1]
    patch_file = sys.argv[2]
    with open(patch_file, 'r', encoding='utf-8') as f:
        apply_patch(sitting, f.read())
