import json
import os
import re

DATA_DIR = "g:/Girish/IAI/SP1 and SA1 Health and Care/Practice papers/Claude Widgets/data/"
SITTINGS = ["201904", "201909", "202004", "202009", "202104", "202109", "202204", "202209", "202304", "202309", "202404", "202409", "202504"]

def parse_marks(m_str):
    if not m_str: return 0.0
    m_str = m_str.replace('[', '').replace(']', '').replace('½', '.5')
    try:
        return float(m_str)
    except:
        return 0.0

def generate():
    report = "# Detailed Question-Solution Mapping Report\n\n"
    report += "| Sitting | ID | QP Marks | Sol Marks | Diff | Topic(s) |\n"
    report += "| :--- | :--- | :---: | :---: | :---: | :--- |\n"
    
    for sit in SITTINGS:
        path = os.path.join(DATA_DIR, f"{sit}.json")
        if not os.path.exists(path):
            continue
            
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        sit_label = data.get("label", sit)
        for q_id, q_data in data.get("questions", {}).items():
            for p_id, p_data in q_data.get("parts", {}).items():
                qp_marks = p_data.get("marks", 0)
                sol_marks = 0.0
                for sec, bullets in p_data.get("sections", {}).items():
                    if sec == "Solution":
                        for b in bullets:
                            marks_found = re.findall(r'\[(.*?)\]', b)
                            for m_str in marks_found:
                                sol_marks += parse_marks(m_str)
                
                diff = qp_marks - sol_marks
                themes = ", ".join(p_data.get("themes", []))
                
                # Highlight discrepancies
                diff_str = f"**{diff}**" if diff > 0 else f"{diff}"
                
                report += f"| {sit_label} | {q_id}{p_id} | {qp_marks} | {sol_marks} | {diff_str} | {themes} |\n"
                
    with open("full_mapping_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("Report generated: full_mapping_report.md")

if __name__ == "__main__":
    generate()
