import datacommons_client as dc
import os
import json

def main():
    api_key = os.environ.get('DC_API_KEY')
    client = dc.DataCommonsClient(api_key=api_key)

    target_types = {"Source", "Dataset", "Provenance", "Organization", "Thing"}
    
    print("Fetching all properties...")
    # Fetch all properties (this might be large, so we fetch in pages if needed)
    # Actually, let's try to fetch properties and their domainIncludes in one go
    try:
        # Get all nodes that are of type Property
        # And for each, get its domainIncludes
        resp = client.node.fetch("Property", "<-typeOf", all_pages=True)
        property_dcids = resp.extract_connected_dcids("Property", "<-typeOf")
        print(f"Found {len(property_dcids)} properties. Fetching their domains...")
        
        # We can't fetch domains for all of them at once easily if it's too many.
        # But we can try in batches of 100
        batch_size = 100
        results = {t: set() for t in target_types}
        
        for i in range(0, len(property_dcids), batch_size):
            batch = property_dcids[i:i+batch_size]
            domain_resp = client.node.fetch(batch, "->domainIncludes")
            props_data = domain_resp.get_properties().root
            
            for prop_id, arcs in props_data.items():
                domains = arcs.get("->domainIncludes", [])
                for d in domains:
                    if d.dcid in target_types:
                        results[d.dcid].add(prop_id)
        
        # Convert sets to sorted lists
        final_results = {t: sorted(list(props)) for t, props in results.items()}
        print(json.dumps(final_results, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
