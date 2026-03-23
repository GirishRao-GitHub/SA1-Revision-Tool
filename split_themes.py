import os
import json

# Adjust this if you move the script outside the Claude Widgets folder
DATA_DIR = r"G:\Girish\IAI\SP1 and SA1 Health and Care\Practice papers\Claude Widgets\data"

# 1. Defined the legacy theme we want to split or replace
OLD_THEME = "Data & Models"

# 2. Define the new themes and the unique keywords that trigger them
# If any of these keywords are found in the question's examiner points, the specific new theme is applied.
NEW_THEMES = {
    "Data": ["data", "volume", "heterogeneity", "credibility", "experience", "statistics", "information", "proxy"],
    "Models": ["model", "stochastic", "deterministic", "markov", "formula", "equation of value", "monte carlo", "projection"]
}

def scan_and_split():
    # Only scan practice paper JSONs, not the frameworks or settings files
    files = [f for f in os.listdir(DATA_DIR) if f.endswith('.json') and f not in ("Topic_Frameworks.json", "Pillars_Hooks.json")]
    
    updated_files = 0
    updated_questions = 0

    for file in files:
        filepath = os.path.join(DATA_DIR, file)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        file_modified = False
        
        # Loop over every question and sub-question
        for q_id, q_data in data.get('questions', {}).items():
            for p_id, p_data in q_data.get('parts', {}).items():
                themes = p_data.get('themes', [])
                
                # Check if the old theme is present
                if OLD_THEME in themes:
                    themes.remove(OLD_THEME)
                    
                    # Combine all text tightly to search for keywords
                    full_text = p_data.get('question', '').lower()
                    for sec_title, bullets in p_data.get('sections', {}).items():
                        full_text += " " + sec_title.lower()
                        for b in bullets:
                            full_text += " " + b.lower()
                    
                    # Check which new themes apply
                    added_new = False
                    for new_theme, keywords in NEW_THEMES.items():
                        if any(kw in full_text for kw in keywords):
                            if new_theme not in themes:
                                themes.append(new_theme)
                                added_new = True
                    
                    # If magically neither keyword matched, give it both natively to be safe
                    if not added_new:
                        if "Data" not in themes: themes.append("Data") 
                        if "Models" not in themes: themes.append("Models")
                    
                    # Sort themes cleanly back into array
                    p_data['themes'] = sorted(list(set(themes)))
                    file_modified = True
                    updated_questions += 1
                    
        # Save back to file safely if changes were made
        if file_modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            updated_files += 1

    print(f"✅ Successfully split '{OLD_THEME}' into {list(NEW_THEMES.keys())}.")
    print(f"✅ Updated {updated_questions} individual questions across {updated_files} exam files.")

if __name__ == "__main__":
    scan_and_split()
