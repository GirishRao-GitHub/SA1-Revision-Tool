import fitz
import sys

def extract_all(pdf_path, output_path, max_pages=300):
    try:
        doc = fitz.open(pdf_path)
        with open(output_path, 'w', encoding='utf-8') as f:
            for i in range(min(max_pages, len(doc))):
                f.write(f"--- PAGE {i+1} ---\n")
                f.write(doc[i].get_text())
                f.write("\n\n")
        print(f"Successfully extracted {min(max_pages, len(doc))} pages to {output_path}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    pdf_path = r"g:\Girish\IAI\SP1 and SA1 Health and Care\SP1 Health and Care Principles\SP1_Health and Care Specialist-2019.pdf"
    extract_all(pdf_path, "all_chapters_raw.txt")
