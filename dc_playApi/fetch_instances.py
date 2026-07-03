import datacommons_client as dc
import os
import json

def main():
    api_key = os.environ.get('DC_API_KEY')
    client = dc.DataCommonsClient(api_key=api_key)

    types = ["Source", "Dataset", "Provenance"]
    
    results = {}
    for type_id in types:
        print(f"Finding instances of {type_id}...")
        try:
            # Find up to 5 instances
            resp = client.node.fetch(type_id, "<-typeOf", all_pages=False)
            instances = resp.extract_connected_dcids(type_id, "<-typeOf")
            
            if instances:
                print(f"Found instances: {instances[:3]}")
                # Fetch properties of the first instance
                inst_id = instances[0]
                inst_props_resp = client.node.fetch_property_labels(inst_id, out=True)
                inst_props = inst_props_resp.get_properties().root.get(inst_id, [])
                results[type_id] = {
                    "instance_dcid": inst_id,
                    "instance_properties": inst_props
                }
            else:
                results[type_id] = {"error": "No instances found"}
        except Exception as e:
            results[type_id] = {"error": str(e)}

    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
