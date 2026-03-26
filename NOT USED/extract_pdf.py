import pdfplumber
import sys
import os

def extract(pdf_path, txt_path, start_page=None, end_page=None):
    print(f"Extracting {pdf_path} to {txt_path}...")
    try:
        with pdfplumber.open(pdf_path) as pdf:
            with open(txt_path, 'w', encoding='utf-8') as f:
                pages = pdf.pages
                if start_page and end_page:
                    pages = pages[start_page-1:end_page]
                
                for i, page in enumerate(pages):
                    curr_page_num = (start_page + i) if start_page else (i + 1)
                    text = page.extract_text()
                    if text:
                        f.write(f"--- PAGE {curr_page_num} ---\n")
                        f.write(text)
                        f.write("\n\n")
        print("Extraction complete.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python extract_pdf.py <pdf_path> <txt_path> [start_page] [end_page]")
    elif len(sys.argv) == 3:
        extract(sys.argv[1], sys.argv[2])
    else:
        extract(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
