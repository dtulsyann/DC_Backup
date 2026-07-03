import json
from urllib.parse import urlparse

def get_domain(url):
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except:
        return "unknown"

def main():
    input_file = "provenances_full.json"
    output_file = "provenances_by_domain.json"

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    grouped_data = {}

    for entry in data:
        prov_url = entry.get('prov_url', '')
        domain = get_domain(prov_url)
        
        # Strip 'www.' for cleaner grouping
        if domain.startswith("www."):
            domain = domain[4:]
            
        if not domain:
            domain = "unknown"

        filtered_entry = {
            "dcid": entry.get("dcid"),
            "prov_url": prov_url,
            "sourceDataUrl": entry.get("sourceDataUrl"),
            "license": entry.get("license"),
            "jet_license": entry.get("jet_license")
        }

        if domain not in grouped_data:
            grouped_data[domain] = []
        
        grouped_data[domain].append(filtered_entry)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(grouped_data, f, indent=4)

    print(f"Processed {len(data)} entries.")
    print(f"Grouped data into {len(grouped_data)} domains.")
    print(f"Saved to {output_file}")

if __name__ == "__main__":
    main()
