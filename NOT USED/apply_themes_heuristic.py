import json
import os

MASTER_TAXONOMY = {
  "Underwriting": ["anti-selection", "financial underwriting", "medical underwriting", "tele-underwriting", "free cover limit", "underwriting"],
  "Pricing": ["data & assumptions", "data and assumptions", "risk profile", "expense", "profit", "cross-subsidy", "pricing", "premium", "morbidity", "mortality", "sensitivity analysis"],
  "Product Design": ["benefits & conditions", "benefits and conditions", "target market", "options & guarantees", "options and guarantees", "exclusion", "product design", "surrender value"],
  "Group Products": ["master trust", "take-up rate", "administration", "unit cost saving", "group product", "group scheme", "group critical illness", "group income protection", "group pmi", "employer"],
  "Claims Management": ["definition", "rehabilitation", "fraud", "verification", "claim control", "claim management", "return to work", "claims"],
  "Regulation": ["treating customers fairly", "capital requirement", "taxation", "state provision", "regulation", "compliance", "solvency", "fca", "pra"],
  "Reinsurance": ["risk transfer", "capital relief", "technical assistance", "quota share", "excess of loss", "reinsurance", "catastrophe cover", "catastrophe"],
  "Risk Management & Capital": ["economic capital", "stress testing", "solvency ii", "solvency 2", "asset liability management", "alm", "risk appetite", "risk management", "capital management", "capital"],
  "Reserving & Valuation": ["ibnr", "ibner", "bornhuetter-ferguson", "bornhuetter", "run-off triangle", "best estimate liability", "best estimate", "bel", "risk margin", "prudence", "reserving", "valuation", "reserves"],
  "Data & Models": ["credibility", "heterogeneity", "proxy", "proxies", "machine learning", "artificial intelligence", "backtesting", "model governance", "data quality", "model risk", "data"],
  "Investments": ["matching", "liquidity", "standard formula", "internal model", "asset class", "yield curve", "investment", "asset allocation"],
  "Professional Guidance": ["actuarial standard", "peer review", "conflict of interest", "whistleblowing", "communication", "professional guidance"]
}

ifoa_files = ['201904.json', '201909.json', '202004.json', '202009.json', '202104.json', '202109.json', '202204.json', '202209.json', '202304.json', '202309.json', '202404.json', '202409.json', '202504.json', '202509.json']
iai_files = [
  'iai_1115.json', 'iai_0416.json', 'iai_0916.json', 'iai_0317.json', 'iai_0917.json', 
  'iai_0318.json', 'iai_0918.json', 'iai_0619.json', 'iai_1119.json', 
  'iai_1120.json', 'iai_0321.json', 'iai_0921.json', 'iai_0322.json', 
  'iai_0722.json', 'iai_1222.json', 'iai_0523.json', 'iai_1123.json', 
  'iai_0524.json', 'iai_1124.json', 'iai_0525.json', 'iai_1125.json'
]
files_to_process = ifoa_files + iai_files
data_dir = r"g:\Girish\IAI\SP1 and SA1 Health and Care\Practice papers\Claude Widgets\data"

def process_item(item):
    text_content = ""
    if "question" in item: text_content += " " + item["question"]
    if "synopsis" in item: text_content += " " + item["synopsis"]
    if "sections" in item:
        for head, points in item["sections"].items():
            text_content += " " + head
            text_content += " " + " ".join(points)
    
    text_content = text_content.lower()
    
    themes = set()
    for theme, hooks in MASTER_TAXONOMY.items():
        if theme.lower() in text_content:
            themes.add(theme)
            continue
            
        for hook in hooks:
            if hook in text_content or hook + "s" in text_content:
                themes.add(theme)
                break
    
    if len(themes) == 0:
        if "risk" in text_content: themes.add("Risk Management & Capital")
        if "design" in text_content: themes.add("Product Design")
        if "claim" in text_content: themes.add("Claims Management")
        if "capital" in text_content: themes.add("Risk Management & Capital")
        
    item["themes"] = sorted(list(themes))

updated_count = 0
for filename in files_to_process:
    filepath = os.path.join(data_dir, filename)
    if not os.path.exists(filepath):
        continue
        
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    questions_modified = False
    if "questions" in data:
        for qk, q in data["questions"].items():
            if "parts" in q and q["parts"]:
                for pk, p in q["parts"].items():
                    process_item(p)
                    questions_modified = True
            else:
                process_item(q)
                questions_modified = True
                
    if questions_modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        updated_count += 1
        print(f"Updated {filename}")

print(f"Successfully processed {updated_count} files!")
