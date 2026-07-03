import os
import requests

def check_provenance_for_stats(provenance_dcids: list[str]) -> dict[str, bool]:
    """
    Checks if the given Provenance DCIDs contain statistical data.
    
    Returns:
        A dictionary mapping the Provenance DCID to a boolean 
        (True if it contains StatVarObservations, False otherwise).
    """
    api_key = os.environ.get("DC_API_KEY")
    url = "https://api.datacommons.org/v2/node"
    headers = {"x-api-key": api_key, "Content-Type": "application/json"}
    
    results = {}
    
    # Process in batches to avoid payload size limits if you pass a large list
    batch_size = 100
    for i in range(0, len(provenance_dcids), batch_size):
        batch = provenance_dcids[i:i+batch_size]
        
        # We want to find nodes that have an outgoing `provenance` edge 
        # pointing to our target Provenance DCIDs.
        payload = {
            "nodes": batch,
            "property": "<-provenance"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            print(f"Error fetching data: {response.status_code}")
            continue
            
        data = response.json().get("data", {})
        
        for prov_dcid in batch:
            has_stats = False
            
            # Extract the nodes imported by this specific provenance
            imported_nodes = data.get(prov_dcid, {}).get("arcs", {}).get("provenance", {}).get("nodes", [])
            
            # Check the types of the imported nodes
            for node in imported_nodes:
                types = node.get("types", [])
                if "StatVarObservation" in types:
                    has_stats = True
                    break # We found stats, no need to check the rest
            
            results[prov_dcid] = has_stats
            
    return results

# --- Example Usage ---
if __name__ == "__main__":
    
    # Let's test one known statistical provenance and one known structural provenance
    test_provs = [
        "dc/base/CensusACS5YearSurvey",     # Known to have stats
        "dc/base/AustraliaGeoCoordinates"   # Known to just have map coordinates
    ]
    
    print("Checking provenances...")
    stats_check = check_provenance_for_stats(test_provs)
    
    for prov, has_stats in stats_check.items():
        if has_stats:
            print(f"✅ {prov} CONTAINS statistical data.")
        else:
            print(f"❌ {prov} DOES NOT contain statistical data.")
