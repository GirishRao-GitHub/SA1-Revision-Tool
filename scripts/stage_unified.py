import json
import os

def stage_chapter_to_unified(chapter_id, notes_json_path, unified_path):
    """Stage 2: Move cleaned notes into Unified_Syllabus.json (no synthesis)."""
    print(f"\n--- STAGE 2: STAGING [{chapter_id}] ---")
    
    if not os.path.exists(notes_json_path):
        print(f"Error: {notes_json_path} not found.")
        return
        
    with open(notes_json_path, 'r', encoding='utf-8') as f:
        notes_data = json.load(f)
        
    chapter_data = notes_data.get("Chapters", {}).get(chapter_id)
    if not chapter_data:
        print(f"Error: Chapter {chapter_id} not found in {notes_json_path}")
        return
        
    if os.path.exists(unified_path):
        with open(unified_path, 'r', encoding='utf-8') as f:
            full_data = json.load(f)
    else:
        full_data = {"Chapters": {}}
    
    # Overwrite/Add chapter (Clean version)
    full_data["Chapters"][chapter_id] = chapter_data
    
    with open(unified_path, 'w', encoding='utf-8') as f:
        json.dump(full_data, f, indent=2)
        
    # RECONCILIATION
    print(f"RECONCILIATION [Stage 2]:")
    print(f"  - Nodes Staged:       {len(chapter_data['content'])}")
    print(f"  - Target Status:      Clean integration (No Synthesis)")
    print(f"  - Result Saved To:   {unified_path}")

if __name__ == "__main__":
    B = r"g:\Girish\IAI\SP1 and SA1 Health and Care"
    W = os.path.join(B, "Practice papers", "Claude Widgets")
    
    NOTES_JSON = os.path.join(W, "data", "SA1_Revision_Notes.json")
    UNIFIED_JSON = os.path.join(W, "data", "Unified_Syllabus.json")
    
    stage_chapter_to_unified("Ch3", NOTES_JSON, UNIFIED_JSON)
