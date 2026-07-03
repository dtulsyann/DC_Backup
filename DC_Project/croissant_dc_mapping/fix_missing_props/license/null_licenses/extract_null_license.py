import csv
import json

def main():
    input_file = "/usr/local/google/home/dtulsyan/DC_Project/croissant_dc_mapping/prov_properties_stats/filtered_provenance/provenances_filtered_props.json"
    output_json = "provenances_null_license.json"
    output_csv = "provenances_null_license.csv"
    
    with open(input_file, "r") as f:
        data = json.load(f)
        
    extracted = []
    for item in data:
        if item.get("license") is None:
            dataset = item.get("dataset") or {}
            source = dataset.get("source") or {}
            
            extracted.append({
                "dcid": item.get("dcid"),
                "prov_url": item.get("sourceDataUrl"),
                "sourceDataUrl": item.get("sourceDataUrl"),
                "dataset_url": dataset.get("url"),
                "source_url": source.get("url"),
            })
            
    with open(output_json, "w") as f:
        json.dump(extracted, f, indent=2)
        
    # Write to CSV
    keys = ["dcid", "prov_url", "sourceDataUrl", "dataset_url", "source_url"]
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(extracted)
        
    print(f"Extracted {len(extracted)} elements where license is null.")
    print(f"Saved JSON to {output_json}")
    print(f"Saved CSV to {output_csv}")

if __name__ == "__main__":
    main()
