from datacommons_client.client import DataCommonsClient
import pandas as pd
import os
from dotenv import load_dotenv

# Load API Key
load_dotenv()

# Initialize Data Commons Client
client = DataCommonsClient(api_key=os.environ.get("DC_API_KEY"))

def get_all_children(parent_dcid):
    """
    Finds child entities. 
    If parent is a Country, finds AdministrativeArea1 (States).
    If parent is AdministrativeArea1, finds AdministrativeArea2 (Counties).
    """
    print(f"--- Discovering sub-regions for {parent_dcid} ---")
    
    # Check the type of the parent to decide what children to look for
    types = client.node.fetch_property_values(parent_dcid, "typeOf").extract_connected_dcids(parent_dcid, "typeOf")
    
    if "Country" in types:
        child_type = "AdministrativeArea1"
    elif "AdministrativeArea1" in types or "State" in types:
        child_type = "AdministrativeArea2"
    else:
        # Fallback/Default
        child_type = "AdministrativeArea1"

    print(f"Parent type(s): {', '.join(types)}. Searching for: {child_type}")
    
    children = client.node.fetch_place_children(parent_dcid, children_type=child_type)
    child_ids = []

    for node in children.get(parent_dcid, []):
        child_ids.append(node['dcid'])
    
    return child_ids

def analyze_place_metadata(place_dcids, variable_dcid):
    """Fetches observations and identifies the latest data providers."""
    print(f"\n--- Analyzing Metadata for Variable: {variable_dcid} ---")
    
    try:
        df = client.observations_dataframe(date="latest", entity_dcids=place_dcids, variable_dcids=variable_dcid)
        if df.empty:
            print("No data found.")
            return df

        # Select and sort using original API column names
        display_cols = ["entity_name", "date", "value", "importName", "provenanceUrl", "measurementMethod", "observationPeriod"]
        df = df[[c for c in display_cols if c in df.columns]].sort_values(["entity_name", "date"], ascending=[True, False])

        print("\n--- All Available Facets ---")
        print(df.to_string(index=False))

        if "date" in df.columns:
            
            latest_per_place = df.drop_duplicates("entity_name")
            print("\n--- Latest Source Per Place ---")
            print(latest_per_place[["entity_name", "date", "importName"]].to_string(index=False))

        return df
    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    parent_dcid = input("Enter Parent ID (e.g., 'country/USA', 'geoId/06' for California): ").strip()
    
    if parent_dcid:
        target_var = input("Enter variable (default 'UnemploymentRate_Person'): ") or "UnemploymentRate_Person"
        children = get_all_children(parent_dcid)
        places = [parent_dcid] + children
        print(f"Analyzing {len(places)} places...")
        analyze_place_metadata(places, target_var)
    else:
        print("No ID provided.")
