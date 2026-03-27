import json
import os
import re

# Paths (Using escaped backslashes for Windows)
BASE_DIR = "g:\\Girish\\IAI\\SP1 and SA1 Health and Care\\Practice papers\\Claude Widgets"
THEMES_PATH = os.path.join(BASE_DIR, "data", "Topic_Frameworks.json")
STRUCTURE_PATH = os.path.join(BASE_DIR, "data", "Syllabus_Structure.json")
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "Unified_Syllabus.json")

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def integrate_ch1():
    # Load Master Data
    themes = load_json(THEMES_PATH)
    structure = load_json(STRUCTURE_PATH)
    
    # Chapter 1 Core Content (The backbone we just extracted)
    ch1_content = [
        {"type": "h3", "text": "0. Introduction"},
        {"type": "point", "text": "This introductory chapter provides an overview of health and care insurance, linking concepts from SP1 and establishing the control/product cycles."},
        {"type": "point", "text": "Sections covered: Advice for passing SA1, Links with SP1, Control and product cycles, and Further reading."},
        
        {"type": "h3", "text": "1. Advice to help you pass Subject SA1"},
        {"type": "h4", "text": "1.1 Higher skills"},
        {"type": "point", "bold": "Analysis", "text": "Identify issues and investigations required in complex/unusual situations. Pore over details carefully."},
        {"type": "point", "bold": "Synthesis", "text": "Creative activity. Suggest methods/solutions based on analysis. Filter out irrelevant or minor points."},
        {"type": "point", "bold": "Critical judgement", "text": "Make decisions/recommendations based on quality of supporting arguments rather than just the final result."},
        {"type": "point", "bold": "Communication", "text": "Use clear logical structure and meet audience needs (e.g., Marketing vs Director)."},
        
        {"type": "h4", "text": "1.2 Problem solving"},
        {"type": "point", "text": "Revisit these skills in Chapter 26 'Solving Complex Issues'."},
        
        {"type": "h3", "text": "2. Links with Subject SP1"},
        {"type": "point", "text": "Subject SA1 builds upon SP1, revisiting topics in greater depth."},
        {"type": "point", "text": "Knowledge of the entire SP1 course is essential for the SA1 exam."},
        
        {"type": "h3", "text": "3. Control and product cycles"},
        {"type": "h4", "text": "3.1 The actuarial control cycle"},
        {"type": "mermaid", "text": "flowchart TD\n    SP[Specifying the Problem] --> DS[Developing the Solution]\n    DS --> ME[Monitoring the Experience]\n    ME --> SP\n    ENV((Environment)) -.-> Cycle\n    PROF((Professionalism)) -.-> Cycle"},
        
        {"type": "h4", "text": "3.2 The product cycle"},
        {"type": "mermaid", "text": "flowchart TD\n    PD[\"Product design\"] --> PR[\"Pricing\"]\n    PR --> MS[\"Marketing Sales\"]\n    MS --> UN[\"Underwriting\"]\n    UN --> CM[\"Claims management\"]\n    CM --> EM[\"Experience monitoring\"]\n    EM --> VL[\"Valuation\"]\n    VL --> PD\n    EM -.Expert Feedback.-> PR"}
    ]
    
    # Interweaving Expert Synthesis from Topic_Frameworks.json
    # Finding "Six Pillar Framework"
    six_pillars = themes.get("The Six Pillar Framework (P1-P6)", {}).get("content", [])
            
    # Injection Logic: Add Six Pillars to "3.1 The actuarial control cycle"
    if six_pillars:
        ch1_content.append({"type": "text", "text": "***Expert Synthesis: Six Pillar Framework*** [src:IAI_Master]"})
        # We take a subset of relevant pillar points for Ch 1 intro
        count = 0
        for node in six_pillars:
            if node.get("type") in ["point", "sub"]:
                # Explicitly add source tag for filtering logic
                new_node = node.copy()
                new_node["text"] = new_node.get("text", "") + " [src:IAI_Synthesis]"
                ch1_content.append(new_node)
                count += 1
            if count >= 10: break

    # Pull "Product Cycle" Expert Insights
    product_cycle_expert = themes.get("Product Cycle", {}).get("content", [])
    if product_cycle_expert:
        ch1_content.append({"type": "text", "text": "***Expert Synthesis: Product Cycle Insights*** [src:IFoA_Master]"})
        count = 0
        for node in product_cycle_expert:
            if node.get("type") in ["point", "sub"]:
                new_node = node.copy()
                new_node["text"] = new_node.get("text", "") + " [src:IFoA_Synthesis]"
                ch1_content.append(new_node)
                count += 1
            if count >= 5: break

    # Initialize Unified Syllabus if it doesn't exist
    if not os.path.exists(OUTPUT_PATH):
        unified = {"Chapters": {}}
    else:
        unified = load_json(OUTPUT_PATH)
        
    unified["Chapters"]["Ch1"] = {
        "title": "Introduction",
        "content": ch1_content
    }
    
    save_json(unified, OUTPUT_PATH)
    print("Chapter 1 Integrated Successfully.")

if __name__ == "__main__":
    integrate_ch1()
