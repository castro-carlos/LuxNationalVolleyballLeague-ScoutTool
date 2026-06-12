# main.py
import glob
import os
import pandas as pd
from report_parser import DataVolleyParser

def main():
    saved_files = glob.glob("match_reports/match_*.pdf")
    all_records = []

    print(f"Beginning extraction on {len(saved_files)} files...\n")

    for file_path in saved_files:
        file_name = os.path.basename(file_path)
        print(f"Processing: {file_name}")

        try:
            # 1. Initialize parser and build the data object
            parser = DataVolleyParser(file_path)
            report = parser.build_report()

            # 2. Flatten the data objects into row dictionaries for Pandas
            for player in report.players:
                flat_record = {
                    "match_date": report.match_date,
                    "season": report.season,
                    "home_team": report.home_team,
                    "away_team": report.away_team,
                    "file_origin": report.file_name,
                    **player.__dict__  # Automatically dumps dataclass attributes as keys
                }
                all_records.append(flat_record)

        except Exception as e:
            print(f"Error processing {file_name}: {e}")

    # 3. Export to final analytical medium
    if all_records:
        df = pd.DataFrame(all_records)
        df.to_csv("volleyball_master_stats.csv", index=False)
        print(f"\nExtraction complete! Saved {len(df)} records to CSV.")

if __name__ == "__main__":
    main()