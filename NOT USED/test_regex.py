import re
import os
import glob

s_files = glob.glob(r"data/*/raw_S.txt")
regex = r'(?:Subject.{0,100}?)?(?:©|@|© )?Institute and Faculty of Actuaries[\s]*'

for f in s_files[:5]:
    with open(f, 'r', encoding='utf-8') as file:
        text = file.read()
    
    matches = re.findall(regex, text, flags=re.IGNORECASE | re.DOTALL)
    print(f"[{f}] Found {len(matches)} matches")
    if matches:
        print(repr(matches[0]))
