import datacommons_client as dc
import os
import json

def main():
    api_key = os.environ.get('DC_API_KEY')
    client = dc.DataCommonsClient(api_key=api_key)

    nodes = ["Source", "Dataset", "Provenance"]
    
    results = {}
    for node_id in nodes:
        print(f"Fetching properties for {node_id}...")
        
        # 1. Fetch outgoing properties (properties of the node itself)
        out_props_resp = client.node.fetch_property_labels(node_id, out=True)
        out_props = out_props_resp.get_properties().root
        
        # 2. Fetch incoming properties
        in_props_resp = client.node.fetch_property_labels(node_id, out=False)
        in_props = in_props_resp.get_properties().root
        
        # 3. Specifically look for properties that have this node in their domainIncludes
        try:
            domain_props_resp = client.node.fetch(node_id, "<-domainIncludes")
            # For fetch with expression, get_properties() returns FlattenedArcsMapping
            # which is dict[NodeDCID, dict[Property, list[Node]]]
            arcs = domain_props_resp.get_properties().root
            domain_props = arcs.get(node_id, {}).get("<-domainIncludes", [])
            domain_prop_ids = [p.dcid for p in domain_props if p.dcid]
        except Exception as e:
            print(f"Error fetching domainIncludes for {node_id}: {e}")
            domain_prop_ids = []

        results[node_id] = {
            "outgoing_properties": out_props.get(node_id, []),
            "incoming_properties": in_props.get(node_id, []),
            "properties_with_domain": domain_prop_ids
        }

    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
