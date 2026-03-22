import pdfplumber
import sys
import os

def extract(pdf_path, txt_path):
    print(f"Extracting {pdf_path} to {txt_path}...")
    try:
        with pdfplumber.open(pdf_path) as pdf:
            with open(txt_path, 'w', encoding='utf-8') as f:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        f.write(f"--- PAGE {i+1} ---\n")
                        f.write(text)
                        f.write("\n\n")
        print("Extraction complete.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python extract_pdf.py <pdf_path> <txt_path>")
    else:
        extract(sys.argv[1], sys.argv[2])
