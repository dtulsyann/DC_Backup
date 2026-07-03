import os
import sys
import json
from datacommons_client.client import DataCommonsClient

def get_all_provenances(api_key: str, output_file: str = "provenances.json") -> None:
    """
    Fetches all Provenance nodes and their properties from Data Commons.
    """
    client = DataCommonsClient(api_key=api_key)

    # 1. Get all nodes of type 'Provenance'
    print("Fetching Provenance DCIDs...", file=sys.stderr)
    try:
        res = client.node.fetch(node_dcids=["Provenance"], expression="<-typeOf").to_dict()
        provenance_nodes = res.get("data", {}).get("Provenance", {}).get("arcs", {}).get("typeOf", {}).get("nodes", [])
        
        provenance_dcids = [dcid for node in provenance_nodes if (dcid := node.get("dcid"))]
        
    except Exception as e:
        print(f"Error fetching provenances: {e}", file=sys.stderr)
        return
    
    if not provenance_dcids:
        print("No provenances found.", file=sys.stderr)
        return
        
    print(f"Found {len(provenance_dcids)} provenances. Fetching properties...", file=sys.stderr)

    # 2. Fetch properties for all these DCIDs at once
    try:
        batch_size = 50
        all_provenances = []
        
        for i in range(0, len(provenance_dcids), batch_size):
            batch = provenance_dcids[i:i+batch_size]
            batch_res = client.node.fetch(node_dcids=batch, expression="->*").to_dict()
            
            data = batch_res.get("data", {})
            for dcid in batch:
                node_data = data.get(dcid, {})
                arcs = node_data.get("arcs", {})
                
                provenance_entry = {"dcid": dcid}
                for prop, prop_data in sorted(arcs.items()):
                    # Avoid shadowing 'nodes' variable from outer scope
                    prop_nodes = prop_data.get("nodes", [])
                    values = [val_node.get("dcid") or val_node.get("value", "") for val_node in prop_nodes]
                    
                    # Store as single value or list based on count
                    provenance_entry[prop] = values[0] if len(values) == 1 else values
                
                all_provenances.append(provenance_entry)
                
        with open(output_file, "w") as f:
            json.dump(all_provenances, f, indent=2)
        
        print(f"Successfully wrote {len(all_provenances)} provenances to {output_file}", file=sys.stderr)
         
    except Exception as e:
         print(f"An error occurred while fetching properties: {e}", file=sys.stderr)

if __name__ == "__main__":
    dc_api_key = os.environ.get('DC_API_KEY')
    if not dc_api_key:
        print("Error: DC_API_KEY environment variable not set. Please set it before running.", file=sys.stderr)
        sys.exit(1)
        
    get_all_provenances(api_key=dc_api_key)
