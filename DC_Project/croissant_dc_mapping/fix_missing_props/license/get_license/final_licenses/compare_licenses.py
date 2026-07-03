import json
import os

def main():
    # Read provenances_licenses.json in the same folder
    file_path = "provenances_licenses.json"
    if not os.path.exists(file_path):
        # Fallback if run from other locations
        file_path = os.path.join(os.path.dirname(__file__), "provenances_licenses.json")
        
    with open(file_path, "r") as f:
        data = json.load(f)
        
    print(f"Comparing license vs jet_license across all {len(data)} entries...")
    print("-" * 80)
    
    diff_count = 0
    was_null = 0
    updated_url = 0
    total_non_null = 0
    same_non_null = 0
    
    for entry in data:
        lic = entry.get("license")
        jet = entry.get("jet_license")
        
        if lic is not None:
            total_non_null += 1
            if lic == jet:
                same_non_null += 1
            else:
                updated_url += 1
                diff_count += 1
                print(f"- {entry['dcid']}:")
                print(f"  Old: {lic}")
                print(f"  New: {jet}")
                print()
        else:
            if lic != jet:
                diff_count += 1
                was_null += 1
                
    print("-" * 80)
    print("Comparison Summary:")
    print(f"Total entries analyzed: {len(data)}")
    print(f"Total originally null, now resolved: {was_null}")
    print(f"Total originally non-null: {total_non_null}")
    print(f"  - Exactly same: {same_non_null} ({same_non_null/total_non_null*100:.1f}%)")
    print(f"  - Different/Standardized: {updated_url} ({updated_url/total_non_null*100:.1f}%)")

if __name__ == "__main__":
    main()
