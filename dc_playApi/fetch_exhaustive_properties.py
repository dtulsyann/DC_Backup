import datacommons_client as dc
import os
import json

def main():
    api_key = os.environ.get('DC_API_KEY')
    client = dc.DataCommonsClient(api_key=api_key)

    nodes = ["Source", "Dataset", "Provenance", "Organization"]
    
    results = {}
    for node_id in nodes:
        print(f"Fetching properties for {node_id} via <-domainIncludes...")
        
        # We need to fetch all pages to be exhaustive
        resp = client.node.fetch(node_id, "<-domainIncludes", all_pages=True)
        arcs = resp.get_properties().root
        # The key in the response is just the property name, even for incoming edges
        domain_props = arcs.get(node_id, {}).get("domainIncludes", [])
        
        # Also fetch properties from parent classes if any
        # For example Source is subClassOf Organization
        
        results[node_id] = [p.dcid for p in domain_props if p.dcid]

    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
