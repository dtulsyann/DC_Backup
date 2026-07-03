import pandas as pd
import requests
import os

def get_states(api_key):
    url = f"https://api.datacommons.org/v2/node"
    payload = {
        "nodes": ["country/USA"],
        "property": "<-containedInPlace"
    }
    response = requests.post(url, json=payload, params={"key": api_key})
    data = response.json()
    nodes = data.get('data', {}).get('country/USA', {}).get('arcs', {}).get('containedInPlace', {}).get('nodes', [])
    return [n['dcid'] for n in nodes if 'State' in n.get('types', [])]

def get_countries(api_key):
    url = f"https://api.datacommons.org/v2/node"
    payload = {
        "nodes": ["earth"],
        "property": "<-containedInPlace"
    }
    response = requests.post(url, json=payload, params={"key": api_key})
    data = response.json()
    nodes = data.get('data', {}).get('earth', {}).get('arcs', {}).get('containedInPlace', {}).get('nodes', [])
    return [n['dcid'] for n in nodes if 'Country' in n.get('types', [])]

def fetch_names(dcids, api_key):
    if not dcids:
        return {}
    
    url = "https://api.datacommons.org/v2/node"
    headers = {"Content-Type": "application/json"}
    names_dict = {}
    
    chunk_size = 500
    for i in range(0, len(dcids), chunk_size):
        chunk = dcids[i:i + chunk_size]
        payload = {
            "nodes": chunk,
            "property": "->name"
        }
        try:
            response = requests.post(url, json=payload, params={"key": api_key}, headers=headers)
            if response.status_code == 200:
                data = response.json().get('data', {})
                for dcid in chunk:
                    nodes = data.get(dcid, {}).get('arcs', {}).get('name', {}).get('nodes', [])
                    if nodes:
                        name_val = nodes[0].get('value', dcid)
                        for n in nodes:
                            if "District" in n.get('value', ''):
                                name_val = n.get('value')
                                break
                        names_dict[dcid] = name_val
                    else:
                        names_dict[dcid] = dcid
            else:
                for dcid in chunk:
                    names_dict[dcid] = dcid
        except Exception as e:
            print(f"Warning: Failed to fetch names for chunk: {e}")
            for dcid in chunk:
                names_dict[dcid] = dcid
                
    return names_dict

def parse_observations(data, records):
    by_var = data.get('byVariable', {})
    for var_id, var_data in by_var.items():
        by_entity = var_data.get('byEntity', {})
        for entity_id, entity_data in by_entity.items():
            ordered_facets = entity_data.get('orderedFacets', [])
            for facet in ordered_facets:
                obs_list = facet.get('observations', [])
                for obs in obs_list:
                    records.append({
                        "?statVar": var_id,
                        "?place": entity_id,
                        "?date": obs.get('date'),
                        "?value": obs.get('value')
                    })

def fetch_provenance_data(provenance_dcid: str):
    """
    Fetches StatVar data (observations) for a specific provenance from Data Commons.
    Uses the V2 REST API.
    """
    print(f"\nFetching Data Commons observations for provenance: {provenance_dcid}...")
    
    api_key = os.environ.get("DC_API_KEY")
    if not api_key:
        raise Exception("DC_API_KEY environment variable is not set.")

    # Step 1: Get variables for the provenance
    print("Finding statistical variables for the provenance...")
    url = f"https://api.datacommons.org/v2/node"
    payload = {
        "nodes": [provenance_dcid],
        "property": "<-provenance"
    }
    headers = {"Content-Type": "application/json"}
    
    variables = []
    var_names = {}
    next_token = ""
    while True:
        params = {"key": api_key}
        response = requests.post(url, json=payload, params=params, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch variables for provenance: {response.text}")
        data = response.json()
        
        prov_data = data.get('data', {}).get(provenance_dcid, {})
        arcs = prov_data.get('arcs', {}).get('provenance', {})
        nodes = arcs.get('nodes', [])
        
        ssv_nodes = [n['dcid'] for n in nodes if 'SourceStatVarInfo' in n.get('types', [])]
        
        if ssv_nodes:
            prop_payload = {
                "nodes": ssv_nodes,
                "property": "->variable"
            }
            prop_response = requests.post(url, json=prop_payload, params=params, headers=headers)
            if prop_response.status_code == 200:
                prop_data = prop_response.json().get('data', {})
                for ssv_node in ssv_nodes:
                    var_nodes = prop_data.get(ssv_node, {}).get('arcs', {}).get('variable', {}).get('nodes', [])
                    for vn in var_nodes:
                        var_dcid = vn['dcid']
                        variables.append(var_dcid)
                        var_names[var_dcid] = vn.get('name', var_dcid)
        
        next_token = arcs.get('nextToken')
        if not next_token:
            break
        payload["nextToken"] = next_token
        
    variables = list(set(variables))
    print(f"Found variables: {variables}")
    
    if not variables:
        return pd.DataFrame()

    # Step 2: Fetch observations
    print("Fetching observations for variables...")
    records = []
    obs_url = "https://api.datacommons.org/v2/observation"
    
    # Query parent entities directly first
    for parent in ["earth", "country/USA"]:
        try:
            payload = {
                "select": ["variable", "entity", "date", "value"],
                "entity": {"dcids": [parent]},
                "variable": {"dcids": variables}
            }
            res = requests.post(obs_url, json=payload, params={"key": api_key})
            if res.status_code == 200:
                parse_observations(res.json(), records)
        except Exception as e:
            print(f"Warning: Failed to fetch for parent {parent}: {e}")
            
    # Query contained places
    place_queries = [
        {"parent": "earth", "type": "Country"},
        {"parent": "country/USA", "type": "State"},
        {"parent": "country/USA", "type": "County"},
        {"parent": "country/USA", "type": "SchoolDistrict"},
        {"parent": "country/USA", "type": "City"}
    ]
    
    for q in place_queries:
        parent = q["parent"]
        ptype = q["type"]
        
        expression = f"{parent}<-containedInPlace+{{typeOf:{ptype}}}"
        payload = {
            "select": ["variable", "entity", "date", "value"],
            "entity": {"expression": expression},
            "variable": {"dcids": variables}
        }
        res = requests.post(obs_url, json=payload, params={"key": api_key})
        
        if res.status_code == 200:
            parse_observations(res.json(), records)
        elif res.status_code == 500 and "large number of concurrent" in res.text:
            print(f"Query for {ptype} in {parent} is too large. Splitting by state/country...")
            if parent == "country/USA":
                states = get_states(api_key)
                for state in states:
                    sub_expression = f"{state}<-containedInPlace+{{typeOf:{ptype}}}"
                    sub_payload = {
                        "select": ["variable", "entity", "date", "value"],
                        "entity": {"expression": sub_expression},
                        "variable": {"dcids": variables}
                    }
                    sub_res = requests.post(obs_url, json=sub_payload, params={"key": api_key})
                    if sub_res.status_code == 200:
                        parse_observations(sub_res.json(), records)
            elif parent == "earth":
                countries = get_countries(api_key)
                for country in countries:
                    sub_expression = f"{country}<-containedInPlace+{{typeOf:{ptype}}}"
                    sub_payload = {
                        "select": ["variable", "entity", "date", "value"],
                        "entity": {"expression": sub_expression},
                        "variable": {"dcids": variables}
                    }
                    sub_res = requests.post(obs_url, json=sub_payload, params={"key": api_key})
                    if sub_res.status_code == 200:
                        parse_observations(sub_res.json(), records)
                        
    if not records:
        return pd.DataFrame()
        
    # Fetch place names
    unique_places = list(set([r["?place"] for r in records]))
    print(f"Fetching names for {len(unique_places)} places...")
    place_names = fetch_names(unique_places, api_key)
    
    # Add names to records
    for r in records:
        r["?statVarName"] = var_names.get(r["?statVar"], r["?statVar"])
        r["?placeName"] = place_names.get(r["?place"], r["?place"])
        
    df = pd.DataFrame(records)
    # Reorder columns
    cols = ["?statVar", "?statVarName", "?place", "?placeName", "?date", "?value"]
    df = df[cols]
    
    return df

def main():
    print("=== Data Commons Provenance Extractor ===")
    
    # 1. Ask for the DCID
    dcid = input("Enter the Provenance DCID (e.g., dc/provenance/WorldBank): ").strip()
    if not dcid:
        print("Error: You must enter a valid DCID.")
        return
        
    # 2. Ask for the format
    print("\nWhich format would you like to save the data in?")
    print("1. csv")
    print("2. parquet")
    print("3. both")
    
    format_choice = input("Enter your choice (csv/parquet/both) [default: both]: ").strip().lower()
    
    # Set default if user just presses Enter
    if format_choice not in ["csv", "parquet", "both"]:
        format_choice = "both"
    
    # Fetch the data into a Pandas DataFrame
    df = fetch_provenance_data(dcid)
    
    if df.empty:
        print("\nNo data found for this provenance DCID.")
        return
        
    print(f"\nSuccessfully fetched {len(df)} records.")
    
    # Clean up column names for Croissant compliance (remove the '?' from SPARQL variables)
    df.columns = [col.replace("?", "") for col in df.columns]
    
    # Save the data based on the requested format
    safe_name = dcid.replace("/", "_")
    
    if format_choice in ["csv", "both"]:
        csv_filename = f"{safe_name}_data.csv"
        df.to_csv(csv_filename, index=False)
        print(f"Saved to {csv_filename}")
        
    if format_choice in ["parquet", "both"]:
        parquet_filename = f"{safe_name}_data.parquet"
        df['value'] = pd.to_numeric(df['value'], errors='ignore')
        df.to_parquet(parquet_filename, index=False)
        print(f"Saved to {parquet_filename}")

if __name__ == "__main__":
    main()