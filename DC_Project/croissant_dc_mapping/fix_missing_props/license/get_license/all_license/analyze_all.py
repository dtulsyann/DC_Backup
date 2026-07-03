import json
from urllib.parse import urlparse

def main():
    with open("provenances_full.json", "r") as f:
        data = json.load(f)
    
    print(f"Total provenances: {len(data)}")
    
    # Let's count how many have license set vs null
    has_license = 0
    null_license = 0
    unique_domains = set()
    
    for entry in data:
        lic = entry.get("license")
        prov_url = entry.get("prov_url")
        if lic:
            has_license += 1
        else:
            null_license += 1
            
        if prov_url:
            parsed = urlparse(prov_url)
            unique_domains.add(parsed.netloc)
            
    print(f"Has license: {has_license}")
    print(f"Null license: {null_license}")
    print(f"Unique domains: {len(unique_domains)}")
    print("Top 30 unique domains:")
    for d in sorted(list(unique_domains))[:30]:
        print(f"  {d}")

if __name__ == "__main__":
    main()
