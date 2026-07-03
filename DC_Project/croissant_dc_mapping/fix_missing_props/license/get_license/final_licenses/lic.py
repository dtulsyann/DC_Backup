import json
import requests
from bs4 import BeautifulSoup
import time
import urllib3
from urllib.parse import urljoin, urlparse

# Suppress warnings for foreign sites with outdated SSL certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ================= CONFIGURATION =================
INPUT_FILE = "provenances_full.json"          # Your file with the 627 provenances
OUTPUT_FILE = "output.json"        # Where the results will be saved
TOP_X_LIMIT = 5                    # Limit top X. Set to None to process all 627.
# =================================================

def extract_license_url(url, publisher_name):
    """Strictly extracts the LICENSE URL, ignoring text names."""
    if not url or not str(url).startswith('http'):
        return "No Valid URL"

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    extracted_url = None
    
    try:
        response = requests.get(url, headers=headers, timeout=12, verify=False)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # STRATEGY 1: Schema.org JSON-LD (Strictly look for URLs)
            for script in soup.find_all('script', type='application/ld+json'):
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict): data = [data]
                    for item in data:
                        if item.get('@type') == 'Dataset' and 'license' in item:
                            lic = item['license']
                            
                            if isinstance(lic, dict):
                                if 'url' in lic and str(lic['url']).startswith('http'):
                                    extracted_url = lic['url']
                                elif '@id' in lic and str(lic['@id']).startswith('http'):
                                    extracted_url = lic['@id']
                            elif isinstance(lic, str) and lic.startswith('http'):
                                extracted_url = lic
                                
                            if extracted_url: break
                except Exception:
                    continue
                    
            # STRATEGY 2: Common global license domains
            if not extracted_url:
                for a_tag in soup.find_all('a', href=True):
                    href = a_tag['href'].lower()
                    if 'creativecommons.org' in href or 'opendatacommons.org' in href:
                        extracted_url = urljoin(url, a_tag['href'])
                        break

            # STRATEGY 3: HTML standard rel="license"
            if not extracted_url:
                license_link = soup.find('a', rel=lambda x: x and 'license' in x.lower() if x else False)
                if license_link and license_link.get('href'):
                    extracted_url = urljoin(url, license_link['href'])

            # STRATEGY 4: Multilingual Keyword Match
            if not extracted_url:
                # Added 'copyright' to catch the Australian standard links
                multilingual_keywords = ['license', 'licencia', 'terms', 'terminos', 'términos', 'transparencia', 'copyright']
                for a_tag in soup.find_all('a', href=True):
                    href = a_tag['href'].lower()
                    if any(kw in href for kw in multilingual_keywords):
                        extracted_url = urljoin(url, a_tag['href'])
                        break
                        
    except Exception as e:
        pass # Ignore exceptions and move to fallback

    # =========================================================
    # THE FIX IS HERE: Strict domain parsing for U.S. Fallback
    # =========================================================
    if not extracted_url or not extracted_url.startswith('http'):
        pub_lower = str(publisher_name).lower()
        
        # Extract the actual domain (e.g. 'www.abs.gov.au' or 'nces.ed.gov')
        domain = urlparse(url).netloc.lower()
        
        # A true U.S. Federal Government site STRICTLY ends with .gov or .mil
        is_us_gov = domain.endswith('.gov') or domain.endswith('.mil')
        
        if "u.s. census" in pub_lower or is_us_gov:
             # Standard URL for U.S. Public Domain government works
             extracted_url = "https://www.usa.gov/government-works"

    return extracted_url if (extracted_url and extracted_url.startswith('http')) else "URL Not Found Automatically"

def main():
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"File {INPUT_FILE} not found. Please create it.")
        return

    to_process = data[:TOP_X_LIMIT] if TOP_X_LIMIT else data
    results = []
    
    print(f"Processing {len(to_process)} provenances...\n")
    
    for idx, item in enumerate(to_process):
        dcid = item.get("dcid")
        pub_name = item.get("dataset", {}).get("source", {}).get("name", "")
        
        target_url = item.get("sourceDataUrl") or item.get("dataset", {}).get("url") or item.get("prov_url")
        
        print(f"[{idx+1}/{len(to_process)}] Scraping {target_url}...")
        extracted_url = extract_license_url(target_url, pub_name)
        print(f"  -> Extracted: {extracted_url}")
        
        results.append({
            "dcid": dcid,
            "prov_url": item.get("prov_url"),
            "license": item.get("license"),
            "jet_license": item.get("jet_license"),
            "extracted_license": extracted_url
        })
        
        time.sleep(1) 
        
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4)
        
    print(f"\nDone! Saved results to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()