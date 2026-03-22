import fitz
import sys
import os

def dump_pdf_to_text(pdf_path, output_path):
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return False
        
    try:
        doc = fitz.open(pdf_path)
        with open(output_path, 'w', encoding='utf-8') as f:
            for i in range(len(doc)):
                f.write(f"--- PAGE {i+1} ---\n")
                f.write(doc[i].get_text())
                f.write("\n\n")
        print(f"Successfully dumped {len(doc)} pages to {output_path}")
        return True
    except Exception as e:
        print(f"Error dumping {pdf_path}: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python dump_sitting.py <question_pdf> <solution_pdf> <output_dir>")
        sys.exit(1)
        
    q_pdf = sys.argv[1]
    s_pdf = sys.argv[2]
    out_dir = sys.argv[3]
    
    os.makedirs(out_dir, exist_ok=True)
    
    q_out = os.path.join(out_dir, "raw_Q.txt")
    s_out = os.path.join(out_dir, "raw_S.txt")
    
    dump_pdf_to_text(q_pdf, q_out)
    dump_pdf_to_text(s_pdf, s_out)
