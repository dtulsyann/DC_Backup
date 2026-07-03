import json

with open("provenances_full.json", "r") as f:
    data = json.load(f)

diff_list = []
for entry in data:
    dc_license = entry.get("license")
    jet_license = entry.get("jet_license")
    
    # Check if both exist, are not null, and are different
    if dc_license and jet_license and dc_license != jet_license:
        diff_list.append({
            "dcid": entry.get("dcid"),
            "prov_url": entry.get("prov_url"),
            "datacommons_license": dc_license,
            "jet_license": jet_license
        })

# Save to a new file
output_file = "diff_licenses_only.json"
with open(output_file, "w") as f:
    json.dump(diff_list, f, indent=2)

print(f"Successfully wrote {len(diff_list)} records to {output_file}")
