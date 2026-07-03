from datacommons_client.client import DataCommonsClient
import os
    
def get_provenance_dates(provenance_dcids: list[str]) -> dict[str, dict]:
    """
    Fetches the earliest and latest observation dates for a list of Provenance DCIDs.
    """
    # Initialize the V2 client
    client = DataCommonsClient(api_key=os.environ.get("DC_API_KEY"))
        
    # We want to fetch both properties. The Node endpoint allows fetching
    # multiple properties using a list.
    properties_to_fetch = ["earliestObservationDate", "latestObservationDate"]
    
    # Fetch the properties
    response = client.node.fetch_property_values(
        node_dcids=provenance_dcids,
        properties=properties_to_fetch
    )
    
    # The response provides a get_properties() method that returns a structured dictionary
    data = response.get_properties()
    
    results = {}
    for prov_dcid in provenance_dcids:
        prov_data = data.get(prov_dcid, {})
        
        # Extract the values from the response nodes. The values are usually 
        # in the 'value' or 'dcid' field of the returned Node objects.
        earliest_nodes = prov_data.get("earliestObservationDate", [])
        latest_nodes = prov_data.get("latestObservationDate", [])
        
        earliest_date = earliest_nodes[0].value if earliest_nodes else None
        latest_date = latest_nodes[0].value if latest_nodes else None
        
        results[prov_dcid] = {
            "earliestObservationDate": earliest_date,
            "latestObservationDate": latest_date
        }
            
    return results

# --- Example Usage ---
if __name__ == "__main__":
    import json
    
    input_file = "../../provenances_full.json"
    all_props_file = "../../prov_prop_stat/provenances_all_props.json"
    output_file = "provenance_dates.json"
    
    # Load all provenances list
    print(f"Loading provenances from {input_file}...")
    with open(input_file, "r") as f:
        provenances_data = json.load(f)
        
    provenances = [item["dcid"] for item in provenances_data if "dcid" in item]
    print(f"Total provenances found: {len(provenances)}")
    
    # Load the pre-fetched properties which contains exactly the right data (matches 241 missing)
    print(f"Loading full properties from {all_props_file}...")
    with open(all_props_file, "r") as f:
        all_props_data = json.load(f)
        
    # Create a lookup dictionary
    props_lookup = {item["dcid"]: item for item in all_props_data if "dcid" in item}
    
    all_dates_info = {}
    
    for prov_dcid in provenances:
        prov_data = props_lookup.get(prov_dcid, {})
        
        earliest_date = prov_data.get("earliestObservationDate")
        latest_date = prov_data.get("latestObservationDate")
        
        all_dates_info[prov_dcid] = {
            "earliestObservationDate": earliest_date,
            "latestObservationDate": latest_date
        }
            
    # Save the results
    print(f"Saving results to {output_file}...")
    with open(output_file, "w") as f:
        json.dump(all_dates_info, f, indent=2)
        
    print(f"Successfully processed and saved dates for {len(all_dates_info)} provenances.")
