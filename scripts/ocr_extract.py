"""
ocr_extract.py - True OCR extraction from PDF using PyMuPDF (fitz) + Tesseract.

Usage:
    python ocr_extract.py <pdf_path> <output_md_path> [start_page] [end_page]

All pages are 1-indexed and inclusive.
"""

import sys
import os
import fitz  # PyMuPDF
import subprocess
import tempfile

# Resolution multiplier: higher = better quality & accuracy, but slower
DPI = 300
ZOOM = DPI / 72  # fitz uses 72dpi internally


def ocr_page(page, page_num):
    """Render a single fitz page to an image and run Tesseract OCR on it."""
    mat = fitz.Matrix(ZOOM, ZOOM)
    pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB, alpha=False)

    # Write pixmap to a temp PNG file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_img:
        tmp_img_path = tmp_img.name

    try:
        pix.save(tmp_img_path)

        # Run tesseract on the PNG, output to stdout
        result = subprocess.run(
            ["tesseract", tmp_img_path, "stdout", "--oem", "1", "--psm", "6", "-l", "eng"],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        if result.returncode != 0:
            print(f"  [WARNING] Tesseract error on page {page_num}: {result.stderr.strip()}", file=sys.stderr)
            return ""
        return result.stdout

    finally:
        os.unlink(tmp_img_path)


def extract(pdf_path, md_path, start_page=None, end_page=None):
    print(f"Opening: {pdf_path}")
    with fitz.open(pdf_path) as doc:
        total = doc.page_count
        print(f"Total pages in PDF: {total}")

        s = (start_page - 1) if start_page else 0
        e = end_page if end_page else total
        e = min(e, total)

        print(f"Extracting pages {s+1} to {e} (OCR at {DPI} DPI)...")

        with open(md_path, "w", encoding="utf-8") as out:
            out.write(f"# OCR Extract: {os.path.basename(pdf_path)}\n\n")
            out.write(f"*Source: `{pdf_path}`*\n\n")
            out.write("---\n\n")

            for i in range(s, e):
                page_num = i + 1
                print(f"  Processing page {page_num}/{e}...", end="\r")
                page = doc[i]
                text = ocr_page(page, page_num)
                out.write(f"## Page {page_num}\n\n")
                if text.strip():
                    out.write(text.strip())
                else:
                    out.write("*(No text detected on this page)*")
                out.write("\n\n---\n\n")

    print(f"\nDone! Output saved to: {md_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python ocr_extract.py <pdf_path> <output_md_path> [start_page] [end_page]")
        sys.exit(1)

    pdf_path = sys.argv[1]
    md_path = sys.argv[2]
    start_page = int(sys.argv[3]) if len(sys.argv) >= 4 else None
    end_page = int(sys.argv[4]) if len(sys.argv) >= 5 else None

    extract(pdf_path, md_path, start_page, end_page)
