import json

agg_path = '/usr/local/google/home/dtulsyan/DC_Project/croissant_dc_mapping/fix_missing_props/license/fix/aggregates_with_parent_license.json'
full_path = '/usr/local/google/home/dtulsyan/DC_Project/croissant_dc_mapping/fix_missing_props/license/fix/provenances_full.json'

with open(agg_path) as f:
    aggregates = json.load(f)

update_map = {}
for item in aggregates:
    update_map[item["aggregate_dcid"]] = {
        "license": item.get("parent_license"),
        "licenseType": item.get("parent_licenseType")
    }

with open(full_path) as f:
    full = json.load(f)

updated_count = 0
for p in full:
    dcid = p.get('dcid')
    if dcid in update_map:
        if update_map[dcid]["license"] is not None:
            p['license'] = update_map[dcid]["license"]
        if update_map[dcid]["licenseType"] is not None:
            p['licenseType'] = update_map[dcid]["licenseType"]
        updated_count += 1

with open(full_path, 'w') as f:
    json.dump(full, f, indent=2)

print(f"Updated {updated_count} items in provenances_full.json.")
