import requests
import os
import sys

def get_statvars_for_provenance(provenance_dcid: str) -> list[str]:
    api_key = os.environ.get("DC_API_KEY")
    if not api_key:
        print("Error: Please set your DC_API_KEY environment variable.")
        print("Run: export DC_API_KEY='your_api_key_here'")
        sys.exit(1)
        
    url = "https://api.datacommons.org/v2/node"
    headers = {"Content-Type": "application/json"}
    params = {"key": api_key}

    statvars = set()
    next_token = ""
    
    # Step 1: Query the incoming 'SourceStatVarInfo' nodes
    while True:
        payload = {
            "nodes": [provenance_dcid],
            "property": "<-provenance"
        }
        if next_token:
            payload["nextToken"] = next_token
            
        resp = requests.post(url, json=payload, params=params, headers=headers)
        if resp.status_code != 200:
            print(f"API Error {resp.status_code}: {resp.text}")
            break
            
        data_json = resp.json()
        arcs = data_json.get("data", {}).get(provenance_dcid, {}).get("arcs", {}).get("provenance", {})
        
        # Filter strictly for SourceStatVarInfo nodes
        ssv_nodes = [n["dcid"] for n in arcs.get("nodes", []) if "SourceStatVarInfo" in n.get("types", [])]
        
        # Step 2: Fetch the actual 'StatisticalVariable' (->variable) from these nodes
        if ssv_nodes:
            # Request in batches of 500 to stay within API limits
            for i in range(0, len(ssv_nodes), 500):
                batch = ssv_nodes[i:i+500]
                var_payload = {"nodes": batch, "property": "->variable"}
                prop_resp = requests.post(url, json=var_payload, params=params, headers=headers).json()
                
                for ssv_dcid in batch:
                    var_nodes = prop_resp.get("data", {}).get(ssv_dcid, {}).get("arcs", {}).get("variable", {}).get("nodes", [])
                    for var_node in var_nodes:
                        statvars.add(var_node["dcid"])
        
        # Move to the next page if there are more than ~100 results
        next_token = arcs.get("nextToken")
        if not next_token:
            break
            
    return list(statvars)

# --- Example Usage ---
if __name__ == "__main__":
    # You can pass the DCID as a command-line argument, or it defaults to this one:
    prov = sys.argv[1] if len(sys.argv) > 1 else "dc/base/CensusACS5YearSurvey"
    
    print(f"Checking StatVars for: {prov}")
    variables = get_statvars_for_provenance(prov)
    
    print(f"\nFound {len(variables)} Statistical Variables!")
    if variables:
        print("First 10 variables:")
        for v in variables[:10]:
            print(f" - {v}")
