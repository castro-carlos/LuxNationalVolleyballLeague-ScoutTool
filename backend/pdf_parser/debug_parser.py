from pathlib import Path
import os
import sys

# 1. Dynamically find the project root directory
# __file__ is the current script. .resolve().parents[1] moves up two levels to the root
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# 2. Construct the absolute path to your PDF inside the match_reports folder
PDF_PATH = PROJECT_ROOT / "match_reports" / "match_0a97949f-d713-4e7c-bd6e-9f506a1794b4.pdf"

# 3. Add the backend directory to Python's search path so it can find your parser import
sys.path.append(str(PROJECT_ROOT))
from pdf_parser.report_parser import DataVolleyParser

if not PDF_PATH.exists():
    print(f"❌ Error: Could not find file at: {PDF_PATH}")
    print(f"Current scanned project root was: {PROJECT_ROOT}")
    exit()

# Initialize your parser engine with the absolute path string
parser = DataVolleyParser(str(PDF_PATH))

print("=" * 80)
print(f"DEBUGGING SCRIPT: WORD-BY-WORD COORDINATE MAP FOR WEBER STEVE")
print("=" * 80)

# Loop through all the reconstructed rows to find Steve Weber's data lines
for idx, row in enumerate(parser.rows):
    if "SCHUBERT Jared" in row:
        print(f"\n[FOUND SCHUBERT Jared AT ROW INDEX {idx}]")
        print(f"Raw Rebuilt Text: '{row}'")
        print("-" * 50)

        print("MAIN ROW WORDS & X-COORDINATES:")
        for x0, text in getattr(row, "words", []):
            print(f"  -> x0: {x0:<8} | text: '{text}'")

        if idx + 1 < len(parser.rows):
            next_row = parser.rows[idx + 1]
            print("-" * 50)
            print(f"[PEEKING AT NEXT ROW INDEX {idx + 1}]")
            print(f"Raw Rebuilt Text: '{next_row}'")
            print("NEXT ROW WORDS & X-COORDINATES:")
            for x0, text in getattr(next_row, "words", []):
                print(f"  -> x0: {x0:<8} | text: '{text}'")

        print("=" * 80)
        break