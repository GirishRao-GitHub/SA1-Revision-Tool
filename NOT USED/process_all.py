import os
import glob
import subprocess

sittings = ["201904", "201909", "202004", "202009", "202104", "202109", "202204", "202209", 
            "202304", "202309", "202404", "202409", "202504", "202509"]

q_dir = r"g:\Girish\IAI\SP1 and SA1 Health and Care\SA1 Health and Care Advanced\SA1 IFOA Exam Papers\SA1 IFoA Question Papers 2019-2025"
s_dir = r"g:\Girish\IAI\SP1 and SA1 Health and Care\SA1 Health and Care Advanced\SA1 IFOA Exam Papers\SA1 IFoA Solutions 2019-2025"

for s in sittings:
    q_matches = glob.glob(os.path.join(q_dir, f"IandF_SA1_{s}_*.pdf"))
    s_matches = glob.glob(os.path.join(s_dir, f"IandF_SA1_{s}_*.pdf"))
    
    if not q_matches or not s_matches:
        print(f"Skipping {s} - missing PDF")
        continue

    q_pdf = q_matches[0]
    s_pdf = s_matches[0]
    
    out_dir = os.path.join("data", s)
    out_json = os.path.join("data", f"{s}.json")
    
    month = "April" if s[-2:] == "04" else "September"
    year = s[:4]
    label = f"{month} {year}"
    
    print(f"[{s}] Processing {label}...")
    subprocess.run(["python", "dump_sitting.py", q_pdf, s_pdf, out_dir], check=True)
    subprocess.run(["python", "auto_parser.py", os.path.join(out_dir, "raw_Q.txt"), os.path.join(out_dir, "raw_S.txt"), out_json, label], check=True)

print("Batch processing complete.")
