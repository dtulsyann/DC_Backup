import os
import sys
import json
from datacommons_client.client import DataCommonsClient

def check_categories():
    dc_api_key = os.environ.get('DC_API_KEY')
    client = DataCommonsClient(api_key=dc_api_key)
    
    with open("Dataset_Page_Mapping/datasets_provs.json") as f:
        data = json.load(f)
        
    all_provs = []
    for ds in data:
        all_provs.extend(ds["provenances"])
        
    batch_size = 50
    categories = set()
    for i in range(0, len(all_provs), batch_size):
        batch = all_provs[i:i+batch_size]
        res = client.node.fetch(node_dcids=batch, expression="->provenanceCategory").to_dict()
        node_data = res.get("data", {})
        
        for p in batch:
            arcs = node_data.get(p, {}).get("arcs", {})
            nodes = arcs.get("provenanceCategory", {}).get("nodes", [])
            for n in nodes:
                categories.add(n.get("dcid") or n.get("value"))

    print("Unique provenanceCategory values:")
    print(categories)

if __name__ == "__main__":
    check_categories()
