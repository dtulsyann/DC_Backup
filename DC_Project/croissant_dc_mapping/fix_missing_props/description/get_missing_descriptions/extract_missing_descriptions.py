import json
import os

input_file = '/usr/local/google/home/dtulsyan/DC_Project/croissant_dc_mapping/provenances_full.json'
output_dir = '/usr/local/google/home/dtulsyan/DC_Project/croissant_dc_mapping/fix_missing_props/description'
output_file = os.path.join(output_dir, 'missing_description_dcid.json')

# Create the directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

def main():
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    missing_desc = []
    
    for item in data:
        if item.get("description") is None:
            missing_desc.append(item.get("dcid"))
            
    with open(output_file, 'w') as f:
        json.dump(missing_desc, f, indent=2)
        
    print(f"Found {len(missing_desc)} provenances with a null description.")
    print(f"Saved them to {output_file}")

if __name__ == "__main__":
    main()
