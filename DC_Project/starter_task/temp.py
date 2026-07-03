import requests
import os

def get_all_provenance_properties(api_key: str = None):
    url = "https://api.datacommons.org/v2/node"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["X-API-Key"] = api_key

    # Step 1: Fetch all instances of 'Provenance' using incoming 'typeOf'
    print("Fetching all Provenance instances...")
    provenance_dcids = []
    next_token = None

    while True:
        payload = {
            "nodes": ["Provenance"],
            "property": "<-typeOf"
        }
        if next_token:
            payload["nextToken"] = next_token

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Parse out the matching nodes
        arcs = data.get("data", {}).get("Provenance", {}).get("arcs", {})
        nodes = arcs.get("typeOf", {}).get("nodes", [])
        
        for node in nodes:
            if "dcid" in node:
                provenance_dcids.append(node["dcid"])

        next_token = data.get("nextToken")
        if not next_token:
            break

    print(f"Total Provenances found: {len(provenance_dcids)}")

    # Step 2: Fetch all properties for retrieved provenances in batches
    print("Fetching properties for provenances...")
    batch_size = 50
    provenance_properties = {}

    for i in range(0, len(provenance_dcids), batch_size):
        batch = provenance_dcids[i:i + batch_size]
        payload = {
            "nodes": batch,
            "property": "->*"
        }

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        resp_data = data.get("data", {})
        for dcid, details in resp_data.items():
            provenance_properties[dcid] = {
                "arcs": details.get("arcs", {}),
                "properties": details.get("properties", [])
            }
            
    return provenance_properties

if __name__ == "__main__":
    # Add your Data Commons API key here if needed
    API_KEY = os.getenv("DC_API_KEY")
    provenances_data = get_all_provenance_properties(api_key=API_KEY)
    
    # Print sample extracted output
    for dcid, prop_data in list(provenances_data.items())[:5]:
        print(f"\nProvenance: {dcid}")
        print(f"Arcs (Relations): {list(prop_data['arcs'].keys())}")