import json
from urllib.parse import urlparse

def main():
    with open("provenances_full.json", "r") as f:
        data = json.load(f)
        
    null_entries = []
    for entry in data:
        if not entry.get("license"):
            null_entries.append({
                "dcid": entry.get("dcid"),
                "prov_url": entry.get("prov_url")
            })
            
    # Group by domain
    domain_groups = {}
    for entry in null_entries:
        prov_url = entry["prov_url"]
        if prov_url:
            parsed = urlparse(prov_url)
            domain = parsed.netloc
        else:
            domain = "No URL"
            
        if domain not in domain_groups:
            domain_groups[domain] = []
        domain_groups[domain].append(entry["dcid"])
        
    print(json.dumps(domain_groups, indent=2))
    print(f"Total null license groups: {len(domain_groups)}")

if __name__ == "__main__":
    main()
