import datacommons_client as dc
import os
import json

def main():
    api_key = os.environ.get('DC_API_KEY')
    client = dc.DataCommonsClient(api_key=api_key)

    nodes = ["Source", "Dataset", "Provenance"]
    
    results = {}
    for node_id in nodes:
        print(f"Investigating {node_id}...")
        
        # Get subClassOf
        subclass_resp = client.node.fetch(node_id, "->subClassOf")
        subclasses = subclass_resp.extract_connected_dcids(node_id, "->subClassOf")
        
        # Get typeOf
        typeof_resp = client.node.fetch(node_id, "->typeOf")
        types = typeof_resp.extract_connected_dcids(node_id, "->typeOf")
        
        results[node_id] = {
            "subClassOf": list(subclasses),
            "typeOf": list(types)
        }

    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
