import json
import os
import re
import sys

def parse_marks(m_str):
    if not m_str: return 0.0
    # Clean up common mark formats
    m_str = m_str.replace('[', '').replace(']', '').replace('½', '.5').replace('1⁄2', '.5').replace('1/2', '.5')
    m_str = m_str.strip()
    try:
        if not m_str: return 0.0
        return float(m_str)
    except:
        return 0.0

def main():
    data_dir = "data"
    
    if len(sys.argv) > 1:
        sittings = [f"{sys.argv[1]}.json"]
    else:
        sittings = [f for f in os.listdir(data_dir) if f.endswith('.json')]
    
    for sitting in sorted(sittings):
        path = os.path.join(data_dir, sitting)
        if not os.path.exists(path):
            print(f"File {path} not found.")
            continue
            
        with open(path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except:
                print(f"Error reading {sitting}")
                continue
                
            print(f"\n--- Audit: {sitting} ---")
            for q_id, q_data in data.get("questions", {}).items():
                for p_id, p_data in q_data.get("parts", {}).items():
                    qp_marks = p_data.get("marks", 0)
                    sol_marks = 0.0
                    for sec, bullets in p_data.get("sections", {}).items():
                        for b in bullets:
                            # Find all bracketed marks like [1], [½], [1½]
                            marks_found = re.findall(r'\[(.*?)\]', b)
                            for m_str in marks_found:
                                sol_marks += parse_marks(m_str)
                    
                    status = "OK" if sol_marks >= qp_marks else "LESS"
                    if qp_marks == 0 and sol_marks == 0: status = "SKIP"
                    
                    if status == "LESS":
                        print(f"  {q_id} {p_id}: QP({qp_marks}) > Sol({sol_marks})")
                    elif len(sys.argv) > 1:
                        # Print all for single-sitting audit
                        print(f"  {q_id} {p_id}: QP({qp_marks}) == Sol({sol_marks}) ({status})")

if __name__ == "__main__":
    main()
