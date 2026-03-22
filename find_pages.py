import fitz
import json
import re

def find_chapters(pdf_path):
    doc = fitz.open(pdf_path)
    res = {}
    for i in range(len(doc)):
        text = doc[i].get_text()
        
        # Look for SP1-xx
        m = re.search(r"SP1.?(0[0-4])", text)
        if m:
            ch = f"Ch{m.group(1)}"
            if ch not in res: res[ch] = []
            res[ch].append(i + 1)
        
        # Look for Question x.y
        if re.search(r"Question [0-4]\.[0-9]", text, re.I):
            if "Pract_Q" not in res: res["Pract_Q"] = []
            res["Pract_Q"].append(i + 1)

        # Look for Solutions
        if re.search(r"Chapter [0-4] Solutions", text, re.I):
            m2 = re.search(r"Chapter ([0-4]) Solutions", text, re.I)
            res[f"Ch0{m2.group(1)}_Sol"] = i + 1

    return res

if __name__ == "__main__":
    pdf_path = r"g:\Girish\IAI\SP1 and SA1 Health and Care\SP1 Health and Care Principles\SP1_Health and Care Specialist-2019.pdf"
    res = find_chapters(pdf_path)
    print(json.dumps(res, indent=2))
