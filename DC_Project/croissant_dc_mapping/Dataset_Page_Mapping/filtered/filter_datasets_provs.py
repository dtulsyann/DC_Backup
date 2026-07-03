import os
import sys
import json
from datacommons_client.client import DataCommonsClient

def filter_datasets():
    dc_api_key = os.environ.get('DC_API_KEY')
    if not dc_api_key:
        print("Error: DC_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)
        
    client = DataCommonsClient(api_key=dc_api_key)
    
    input_file = "Dataset_Page_Mapping/datasets_provs.json"
    output_file = "Dataset_Page_Mapping/datasets_provs_filtered.json"
    
    with open(input_file) as f:
        data = json.load(f)
        
    # Gather all provenances to fetch categories in batches
    all_provs = []
    for ds in data:
        all_provs.extend(ds["provenances"])
        
    prov_categories = {}
    batch_size = 50
    print("Fetching provenance categories...", file=sys.stderr)
    for i in range(0, len(all_provs), batch_size):
        batch = all_provs[i:i+batch_size]
        try:
            res = client.node.fetch(node_dcids=batch, expression="->provenanceCategory").to_dict()
            node_data = res.get("data", {})
            for p in batch:
                arcs = node_data.get(p, {}).get("arcs", {})
                nodes = arcs.get("provenanceCategory", {}).get("nodes", [])
                categories = []
                for n in nodes:
                    val = n.get("dcid") or n.get("value")
                    if val:
                        categories.append(val)
                prov_categories[p] = categories
        except Exception as e:
            print(f"Error fetching batch: {e}", file=sys.stderr)
            
    allowed_categories = {"StatisticsProvenance", "AggregatedStatisticsProvenance"}
    
    filtered_data = []
    
    for ds in data:
        new_provs = []
        for p in ds["provenances"]:
            cats = prov_categories.get(p, [])
            if any(c in allowed_categories for c in cats):
                new_provs.append(p)
                
        if new_provs:
            filtered_ds = {
                "dataset_dcid": ds["dataset_dcid"],
                "dataset_name": ds["dataset_name"],
                "provenance_count": len(new_provs),
                "provenances": new_provs
            }
            filtered_data.append(filtered_ds)
            
    filtered_data.sort(key=lambda x: x["provenance_count"], reverse=True)
            
    with open(output_file, "w") as f:
        json.dump(filtered_data, f, indent=2)
        
    print(f"Successfully wrote filtered data to {output_file}", file=sys.stderr)

if __name__ == "__main__":
    filter_datasets()
