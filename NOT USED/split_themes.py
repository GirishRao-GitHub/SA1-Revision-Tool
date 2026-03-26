import os
import json

# Adjust this if you move the script outside the Claude Widgets folder
DATA_DIR = r"G:\Girish\IAI\SP1 and SA1 Health and Care\Practice papers\Claude Widgets\data"

# 1. Defined the legacy theme we want to split or replace
OLD_THEME = "Data & Models"

# 2. Define the new themes and the unique keywords that trigger them
NEW_THEMES = {
    "Data": ["data", "volume", "heterogeneity", "credibility", "experience", "statistics", "information", "proxy", "quality", "completeness"],
    "Models": ["model", "stochastic", "deterministic", "markov", "formula", "equation of value", "monte carlo", "projection", "parameter", "governance"]
}

def process_theme_list(themes, text_to_search):
    if OLD_THEME in themes:
        themes.remove(OLD_THEME)
        added_new = False
        for new_theme, keywords in NEW_THEMES.items():
            if any(kw in text_to_search for kw in keywords):
                if new_theme not in themes:
                    themes.append(new_theme)
                    added_new = True
        
        # Fallback: if no keyword matched, give it both
        if not added_new:
            if "Data" not in themes: themes.append("Data") 
            if "Models" not in themes: themes.append("Models")
        
        return sorted(list(set(themes))), True
    return themes, False

def scan_and_split():
    files = [f for f in os.listdir(DATA_DIR) if f.endswith('.json') and f not in ("Topic_Frameworks.json", "Pillars_Hooks.json")]
    
    updated_files = 0
    updated_questions = 0

    for file in files:
        filepath = os.path.join(DATA_DIR, file)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        file_modified = False
        
        for q_id, q_data in data.get('questions', {}).items():
            # Check top-level question themes
            q_themes = q_data.get('themes', [])
            q_text = (q_data.get('question', '') + " " + q_data.get('label', '')).lower()
            
            new_q_themes, modified = process_theme_list(q_themes, q_text)
            if modified:
                q_data['themes'] = new_q_themes
                file_modified = True
                updated_questions += 1

            # Check parts
            for p_id, p_data in q_data.get('parts', {}).items():
                p_themes = p_data.get('themes', [])
                
                # Combine all text for context
                p_text = p_data.get('question', '').lower()
                for sec_title, bullets in p_data.get('sections', {}).items():
                    p_text += " " + sec_title.lower()
                    for b in bullets:
                        p_text += " " + b.lower()
                
                new_p_themes, modified = process_theme_list(p_themes, p_text)
                if modified:
                    p_data['themes'] = new_p_themes
                    file_modified = True
                    updated_questions += 1
                    
        if file_modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            updated_files += 1

    print(f"✅ Successfully split '{OLD_THEME}' into {list(NEW_THEMES.keys())}.")
    print(f"✅ Updated {updated_questions} entities across {updated_files} exam files.")

if __name__ == "__main__":
    scan_and_split()
