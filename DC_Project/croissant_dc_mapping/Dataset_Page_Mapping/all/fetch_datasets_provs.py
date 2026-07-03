import os
import sys
import json
from collections import defaultdict
from datacommons_client.client import DataCommonsClient

def get_datasets_and_provenances():
    dc_api_key = os.environ.get('DC_API_KEY')
    if not dc_api_key:
        print("Error: DC_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)
        
    client = DataCommonsClient(api_key=dc_api_key)
    
    # Get all Provenance nodes
    print("Fetching Provenance DCIDs...", file=sys.stderr)
    try:
        res = client.node.fetch(node_dcids=["Provenance"], expression="<-typeOf").to_dict()
        provenance_nodes = res.get("data", {}).get("Provenance", {}).get("arcs", {}).get("typeOf", {}).get("nodes", [])
        provenance_dcids = [dcid for node in provenance_nodes if (dcid := node.get("dcid"))]
    except Exception as e:
        print(f"Error fetching provenances: {e}", file=sys.stderr)
        return

    dataset_to_provenances = defaultdict(list)
    dataset_dcids_set = set()

    batch_size = 50
    for i in range(0, len(provenance_dcids), batch_size):
        batch = provenance_dcids[i:i+batch_size]
        batch_res = client.node.fetch(node_dcids=batch, expression="->isPartOf").to_dict()
        data = batch_res.get("data", {})
        
        for prov_dcid in batch:
            node_data = data.get(prov_dcid, {})
            arcs = node_data.get("arcs", {})
            part_of_nodes = arcs.get("isPartOf", {}).get("nodes", [])
            dataset_dcid = part_of_nodes[0].get("dcid") if part_of_nodes else "UnknownDataset"
            dataset_to_provenances[dataset_dcid].append(prov_dcid)
            if dataset_dcid != "UnknownDataset":
                dataset_dcids_set.add(dataset_dcid)

    dataset_names = {}
    dataset_list = list(dataset_dcids_set)
    for i in range(0, len(dataset_list), batch_size):
        batch = dataset_list[i:i+batch_size]
        batch_res = client.node.fetch(node_dcids=batch, expression="->name").to_dict()
        data = batch_res.get("data", {})
        for ds_dcid in batch:
            node_data = data.get(ds_dcid, {})
            arcs = node_data.get("arcs", {})
            name_nodes = arcs.get("name", {}).get("nodes", [])
            dataset_names[ds_dcid] = name_nodes[0].get("value") if name_nodes else ds_dcid

    result = []
    for ds_dcid, provs in dataset_to_provenances.items():
        name = dataset_names.get(ds_dcid, ds_dcid)
        result.append({
            "dataset_dcid": ds_dcid,
            "dataset_name": name,
            "provenance_count": len(provs),
            "provenances": provs
        })
    
    result.sort(key=lambda x: x["provenance_count"], reverse=True)
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    get_datasets_and_provenances()
