import json

agg_path = '/usr/local/google/home/dtulsyan/DC_Project/croissant_dc_mapping/fix_missing_props/license/fix/missing_license_aggregates.json'
full_path = '/usr/local/google/home/dtulsyan/DC_Project/croissant_dc_mapping/fix_missing_props/license/fix/provenances_full.json'

with open(agg_path) as f:
    aggregates = json.load(f)

with open(full_path) as f:
    full = json.load(f)

license_map = {p['dcid']: p.get('license') for p in full if p.get('dcid')}
license_type_map = {p['dcid']: p.get('licenseType') for p in full if p.get('dcid')}
result = []
for agg_dcid, parent_dcid in aggregates.items():
    if parent_dcid == "No Parent Found":
        continue
    lic = license_map.get(parent_dcid)
    lic_type = license_type_map.get(parent_dcid)
    if lic or lic_type:
        result.append({
            "aggregate_dcid": agg_dcid,
            "parent_dcid": parent_dcid,
            "parent_license": lic,
            "parent_licenseType": lic_type
        })

output_path = '/usr/local/google/home/dtulsyan/DC_Project/croissant_dc_mapping/fix_missing_props/license/fix/aggregates_with_parent_license.json'
with open(output_path, 'w') as f:
    json.dump(result, f, indent=2)

print(f"Found {len(result)} items.")
