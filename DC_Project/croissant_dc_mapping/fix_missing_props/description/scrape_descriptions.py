import json
import os
import urllib.request
import urllib.error
from bs4 import BeautifulSoup
import concurrent.futures
import time

input_file = '/usr/local/google/home/dtulsyan/DC_Project/croissant_dc_mapping/fix_missing_props/description/get_missing_descriptions/missing_description_provenances.json'
output_file = '/usr/local/google/home/dtulsyan/DC_Project/croissant_dc_mapping/fix_missing_props/description/web_scraped_descriptions.json'

def fetch_meta_description(url):
    if not url or not url.startswith('http'):
        return None
        
    # Some basic headers to avoid instant blocking
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read()
            soup = BeautifulSoup(html, 'html.parser')
            
            # Look for various description meta tags
            desc = soup.find('meta', attrs={'name': 'description'}) or \
                   soup.find('meta', attrs={'property': 'og:description'}) or \
                   soup.find('meta', attrs={'name': 'twitter:description'})
                   
            if desc and desc.get('content'):
                content = desc.get('content').strip()
                if len(content) > 15: # basic sanity check to avoid useless tags
                    return content
    except urllib.error.HTTPError as e:
        # Many gov sites return 403 Forbidden for scrapers
        print(f"HTTP Error {e.code} for {url}")
    except Exception as e:
        print(f"Failed {url}: {str(e)[:50]}")
        
    return None

def process_item(item):
    # Try the dataset url first, then the prov_url
    dataset_url = item.get("dataset", {}).get("url")
    prov_url = item.get("prov_url")
    
    # We will try to fetch from dataset_url first
    scraped_desc = fetch_meta_description(dataset_url)
    if not scraped_desc and prov_url != dataset_url:
        scraped_desc = fetch_meta_description(prov_url)
        
    # If we got a good scrape, prepend or replace
    if scraped_desc:
        print(f"SUCCESS scraped description for {item['dcid']}")
        item["description"] = scraped_desc
    else:
        # Fall back to the rich description we generated previously
        pass
        
    return item

def main():
    with open(input_file, 'r') as f:
        data = json.load(f)
        
    print(f"Starting web scrape for {len(data)} provenances...")
    
    results = []
    # Using ThreadPoolExecutor to run requests in parallel to save time
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(process_item, item): item for item in data}
        
        for future in concurrent.futures.as_completed(futures):
            item = futures[future]
            try:
                processed_item = future.result()
                results.append(processed_item)
            except Exception as e:
                print(f"Exception processing {item['dcid']}: {e}")
                results.append(item)
                
    # Sort results to maintain original order (roughly) based on dcid
    results.sort(key=lambda x: x.get('dcid', ''))
            
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
        
    print(f"Successfully finished web scraping fallback script.")
    print(f"Saved new provenances to {output_file}")

if __name__ == "__main__":
    main()
