from bs4 import BeautifulSoup
import requests
import re
import time
from urllib.parse import urljoin, urlparse, parse_qs
import os

results_page = requests.get("https://flvb.lu/indoor/results/championship/men/division-nationale?saison134=5abf1462-614b-44ee-bb92-751f50becae8")
soup = BeautifulSoup(results_page.content, 'html.parser')

match_data_list = soup.find_all(href=re.compile("match-data"))

base_url = "https://flvb.lu"

output_dir = "match_reports"
os.makedirs(output_dir, exist_ok=True)

match_report_list = soup.find_all(href=re.compile("match_reports"))

for match_report_tag in match_report_list:
    relative_link = match_report_tag.get('href')
    print(match_report_tag)
    full_match_report_url = urljoin(base_url, relative_link)


    match_id = relative_link.split('/')[-1].replace('?', '_').replace('=', '_')

    filename = os.path.join(output_dir, f"match_{match_id}")

    # Only download if we don't already have it locally!
    if not os.path.exists(filename):
        print(f"Downloading: {full_match_report_url} -> Saving to {filename}")
        try:
            match_report_page = requests.get(full_match_report_url)

            # Save the raw HTML content as a local file
            with open(filename, "wb") as f:
                f.write(match_report_page.content)

            time.sleep(1)  # Polite scraping delay
        except Exception as e:
            print(f"Failed to download {full_match_report_url}: {e}")
    else:
        print(f"Already have {filename} locally. Skipping download.")

print("\nAll match reports saved successfully!")