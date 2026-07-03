from datacommons_client.client import DataCommonsClient
import pandas as pd
import os
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load API Key
load_dotenv()
client = DataCommonsClient(api_key=os.environ.get("DC_API_KEY"))

def get_source_name(url):
    if pd.isna(url) or not isinstance(url, str):
        return url
    domain = urlparse(url).netloc
    if "worldbank.org" in domain:
        return "World Bank"
    elif "niti.gov.in" in domain:
        return "NITI Aayog (NDAP)"
    elif "oecd.org" in domain:
        return "OECD"
    else:
        return domain

def resolve_place_name(name):
    """Resolves a human-readable name to a Data Commons DCID."""
    print(f"--- Resolving Place Name: {name} ---")
    resolved = client.resolve.fetch_dcids_by_name(names=[name]).to_flat_dict()
    dcid = resolved.get(name)
    if isinstance(dcid, list) and dcid:
        return dcid[0]
    return dcid

def get_sub_regions(parent_dcid):
    """
    Finds sub-regions (Districts/AdministrativeArea2) within a parent place.
    If the parent is a country, it first finds states, then districts.
    If it's a state, it finds districts directly.
    """
    print(f"--- Discovering sub-regions for {parent_dcid} ---")
    
    # Check if the parent is a country or state to decide how to fetch districts
    type_resp = client.node.fetch_property_values(parent_dcid, "typeOf")
    types = [t.dcid for t in type_resp.get_properties().get(parent_dcid, {}).get("typeOf", [])]
    
    all_districts = []
    
    if "Country" in types:
        # Get states first
        states_resp = client.node.fetch_place_children(parent_dcid, children_type="AdministrativeArea1")
        states = [node['dcid'] for node in states_resp.get(parent_dcid, [])]
        print(f"Found {len(states)} states. Fetching districts for each...")
        for state_dcid in states:
            dist_resp = client.node.fetch_place_children(state_dcid, children_type="AdministrativeArea2")
            all_districts.extend([node['dcid'] for node in dist_resp.get(state_dcid, [])])
    elif "AdministrativeArea1" in types or "State" in types:
        # Get districts directly
        dist_resp = client.node.fetch_place_children(parent_dcid, children_type="AdministrativeArea2")
        all_districts = [node['dcid'] for node in dist_resp.get(parent_dcid, [])]
    else:
        # Try fetching children directly as a fallback
        dist_resp = client.node.fetch_place_children(parent_dcid, children_type="AdministrativeArea2")
        all_districts = [node['dcid'] for node in dist_resp.get(parent_dcid, [])]
        
    return all_districts

def get_variable_dimensions(variable_dcid):
    """
    Extracts the inherent demographic dimensions (like gender, race, age)
    encoded in the Statistical Variable itself.
    """
    print(f"\n--- Extracting Demographic Dimensions for: {variable_dcid} ---")
    try:
        labels_resp = client.node.fetch_property_labels(node_dcids=[variable_dcid]).get_properties().to_dict()
        labels = labels_resp.get(variable_dcid, [])
        
        # Properties to ignore that are not demographic dimensions
        ignore_props = {
            'constraintProperties', 'memberOf', 'name', 'provenance', 
            'typeOf', 'statType', 'dcid', 'description', 
            'populationType', 'measuredProperty'
        }
        
        dimensions = [p for p in labels if p not in ignore_props]
        
        if not dimensions:
            print("No specific demographic dimensions found (e.g. this is a general aggregate variable).")
            return

        dim_values = {}
        for dim in dimensions:
            vals = client.node.fetch_property_values(variable_dcid, dim).get_properties().get(variable_dcid, {})
            dim_vals = vals.get(dim, [])
            
            extracted = []
            for v in dim_vals:
                if hasattr(v, 'dcid') and v.dcid:
                    extracted.append(v.dcid)
                elif hasattr(v, 'value') and v.value:
                    extracted.append(v.value)
                    
            if extracted:
                dim_values[dim] = extracted

        if dim_values:
            print("Demographic Dimensions encoded in this variable:")
            for dim, vals in dim_values.items():
                print(f"  - {dim.capitalize()}: {', '.join(vals)}")
        else:
            print("No specific demographic dimensions found.")
            
    except Exception as e:
        print(f"Warning: Could not fetch dimensions: {e}")

def analyze_district_metadata(place_dcids, variable_dcid):
    """
    Fetches observations and extracts metadata for a list of places.
    Similar to the logic in analyze_metadata.py.
    """
    print(f"\n--- Analyzing Metadata for Variable: {variable_dcid} ---")
    get_variable_dimensions(variable_dcid)
    
    try:
        if not place_dcids:
            print("No places to analyze.")
            return
            
        # Fetch latest observations
        df = client.observations_dataframe(
            date="latest", 
            entity_dcids=place_dcids, 
            variable_dcids=variable_dcid
        )
        
        if df.empty:
            print(f"No data found for the specified places and variable '{variable_dcid}'.")
            return

        # Rename columns for readability
        df_display = df.rename(columns={
            "entity_name": "Place Name",
            "entity": "DCID",
            "value": "Latest Value",
            "date": "Year",
            "importName": "Internal Label",
            "provenanceUrl": "Actual Provider",
            "measurementMethod": "Method",
            "observationPeriod": "Period"
        })

        if "Actual Provider" in df_display.columns:
            df_display["Actual Provider"] = df_display["Actual Provider"].apply(get_source_name)

        # Fill NaNs
        df_display = df_display.fillna("N/A")

        # Select relevant columns
        cols = ["Place Name", "Year", "Latest Value", "Internal Label", "Actual Provider", "Method", "Period"]
        # Ensure all columns exist before selecting
        cols = [c for c in cols if c in df_display.columns]
        df_display = df_display[cols].sort_values(["Place Name", "Year"], ascending=[True, False])

        print("\n--- Latest Observations & Metadata ---")
        print(df_display.to_string(index=False))

        # Analysis Summary
        if "Year" in df_display.columns:
            latest_year = df_display["Year"].max()
            print(f"\nSummary: The most recent data point is from {latest_year}.")
            
            if "Internal Label" in df_display.columns:
                latest_sources = df_display[df_display["Year"] == latest_year]["Internal Label"].unique()
                print(f"Internal Labels providing {latest_year} data: {', '.join(latest_sources)}")

    except Exception as e:
        print(f"Error during analysis: {e}")

if __name__ == "__main__":
    # 1. Get Place Name from user
    place_name = input("Enter the name of a City, State, or Country (e.g., 'Karnataka', 'India'): ")
    
    # 2. Resolve to DCID
    target_dcid = resolve_place_name(place_name)
    
    if not target_dcid:
        print(f"Could not resolve '{place_name}' to a Data Commons DCID.")
    else:
        print(f"Resolved to DCID: {target_dcid}")
        
        # 3. Get Sub-regions (Districts)
        districts = get_sub_regions(target_dcid)
        
        # Include the parent place itself in the analysis
        places_to_analyze = [target_dcid] + districts
        
        print(f"Found {len(districts)} sub-regions. Total places to analyze: {len(places_to_analyze)}")
        
        # 4. Get Variable from user or use default
        target_variable = input("Enter the target variable (default 'Count_Person'): ") or "Count_Person"
        
        # 5. Run Analysis
        analyze_district_metadata(places_to_analyze, target_variable)
