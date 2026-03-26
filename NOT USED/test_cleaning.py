import re

def clean_text_test(text):
    patterns = [
        r'---\s*PAGE\s+\d+\s*---',
        r'SA1\s+[AS]\d{4}',
        r'Institute and Faculty of Actuaries',
        r'© .*',
        r'www\.actuaries\.org\.uk',
        # Simple keyword-based header removal
        r'^Subject\s+S[AP]1.*Examiners?.*?report.*$',
        r'^S[AP]1.*Examiners?.*?report.*$',
        r'EXAMINERS.?\s+REPORT.*Subject\s+S[AP]1.*$',
        r'PLEASE\s+TURN\s+OVER',
        r'In\s+addition\s+to\s+this\s+paper\s+.*?edition\s+of\s+the\s+Formulae\s+and\s+Tables.*',
        r'Solutions\s+for\s+Subject\s+S[AP]1\s+-\s+[A-Za-z]+\s+\d{4}',
    ]
    
    # Process line by line for better control
    lines = text.split('\n')
    new_lines = []
    for line in lines:
        cleaned_line = line
        for p in patterns:
            if re.search(p, cleaned_line, flags=re.I):
                cleaned_line = "[CLEANED]"
                break
        new_lines.append(cleaned_line)
            
    return '\n'.join(new_lines)

test_cases = [
    "Subject SP1 – (Health and Care Specialist Applications) – April 2019 – Examiner’s report",
    "Subject SP1 – (Health and Care Specialist Applications) – April 2019 – Examiner’s report And using resources...",
    "SA1 ‑ Health and Care ‑ Specialist Advanced - April 2025 - Examiners’ report",
    "EXAMINERS’ REPORT April 2019 Examinations Subject SA1 – Health and Care Specialist Applications",
    "In addition to this paper you should have available the 2002 edition of the Formulae and Tables and your own electronic calculator from the approved list.",
    "--- PAGE 5 ---"
]

if __name__ == "__main__":
    for i, case in enumerate(test_cases):
        print(f"\n--- Test Case {i+1} ---")
        print(f"Original: {case[:100]}")
        result = clean_text_test(case)
        print(f"Result:   {result[:100]}")
