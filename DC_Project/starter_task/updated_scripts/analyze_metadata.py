from datacommons_client.client import DataCommonsClient
import pandas as pd
import os
from dotenv import load_dotenv

# Load API Key if you have a .env file
load_dotenv()

# Initialize Data Commons Client
# Ensure DC_API_KEY is set in your environment or .env file
client = DataCommonsClient(api_key=os.environ.get("DC_API_KEY"))

# Cache for metadata resolution to avoid redundant API calls
facet_cache = {}

def resolve_all_facets(import_names):
    """
    Resolves provenance, dataset, and source info for a list of importNames in batch.
    """
    to_resolve = [name for name in import_names if pd.notna(name) and name != "N/A" and name not in facet_cache]
    if not to_resolve:
        return

    prov_dcids = [f"dc/base/{name}" for name in to_resolve]
    
    try:
        # Batch fetch source and isPartOf with names
        resp = client.node.fetch_property_values(
            node_dcids=prov_dcids,
            properties=["source", "isPartOf"]
        ).get_properties()
        
        for name in to_resolve:
            prov_dcid = f"dc/base/{name}"
            props = resp.get(prov_dcid, {})
            
            source_info = "N/A"
            source_nodes = props.get("source", [])
            if source_nodes:
                n = source_nodes[0]
                source_info = n.dcid or "N/A"
                
            dataset_info = "N/A"
            dataset_nodes = props.get("isPartOf", [])
            if dataset_nodes:
                n = dataset_nodes[0]
                dataset_info = n.dcid or "N/A"
                
            facet_cache[name] = (prov_dcid, dataset_info, source_info)
            
    except Exception as e:
        print(f"Warning: Batch resolution failed: {e}")
        # Fallback for remaining
        for name in to_resolve:
            if name not in facet_cache:
                facet_cache[name] = (f"dc/base/{name}", "N/A", "N/A")

def resolve_place_name(name):
    """Resolves a human-readable name to a Data Commons DCID."""
    print(f"--- Resolving Place Name: {name} ---")
    resolved = client.resolve.fetch_dcids_by_name(names=[name]).to_flat_dict()
    dcid = resolved.get(name)
    if isinstance(dcid, list) and dcid:
        return dcid[0]
    return dcid

def get_all_states(parent_dcid):
    """
    Automatically finds all child entities of type 'State' (or AdministrativeArea1)
    within a parent country.
    """
    print(f"--- Discovering sub-regions for {parent_dcid} ---")
    
    # Check type of parent to determine children type
    type_resp = client.node.fetch_property_values(parent_dcid, "typeOf")
    types = [t.dcid for t in type_resp.get_properties().get(parent_dcid, {}).get("typeOf", [])]
    
    child_type = "AdministrativeArea1"
    if "Country" in types and parent_dcid == "country/USA":
        child_type = "State"
    
    children = client.node.fetch_place_children(parent_dcid, children_type=child_type)
    # Create an empty list to hold the state IDs
    states = []

    # Loop through each individual dictionary in the API results
    for node in children.get(parent_dcid, []):
        # Extract the value stored under the 'dcid' key
        dcid_value = node['dcid']
        # Add it to our clean list
        states.append(dcid_value)
    return states

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

def analyze_place_metadata(place_dcids, variable_dcid):
    """
    Fetches observations and extracts metadata for a list of places.
    Shows all available sources/facets and identifies the latest data providers.
    """
    print(f"\n--- Analyzing Metadata for Variable: {variable_dcid} ---")
    get_variable_dimensions(variable_dcid)
    
    try:
        # Fetch latest observations using the V2 dataframe method
        # date="latest" fetches the most recent data point for each available facet/source
        df = client.observations_dataframe(
            date="latest", 
            entity_dcids=place_dcids, 
            variable_dcids=variable_dcid
        )
        
        if df.empty:
            print("No data found for the specified places and variable.")
            return df

        if "importName" in df.columns:
            unique_imports = df["importName"].dropna().unique().tolist()
            resolve_all_facets(unique_imports)
            
            df["Provenance"] = df["importName"].apply(lambda x: facet_cache.get(x, (f"dc/base/{x}", "N/A", "N/A"))[0] if pd.notna(x) else "N/A")
            df["Dataset"] = df["importName"].apply(lambda x: facet_cache.get(x, (f"dc/base/{x}", "N/A", "N/A"))[1] if pd.notna(x) else "N/A")
            df["Source"] = df["importName"].apply(lambda x: facet_cache.get(x, (f"dc/base/{x}", "N/A", "N/A"))[2] if pd.notna(x) else "N/A")
        else:
            df["Provenance"] = "N/A"
            df["Dataset"] = "N/A"
            df["Source"] = "N/A"

        # Rename columns for readability
        df_display = df.rename(columns={
            "entity_name": "Place Name",
            "entity": "DCID",
            "value": "Latest Value",
            "date": "Year",
            "importName": "Internal Label",
            "measurementMethod": "Method",
            "observationPeriod": "Period"
        })

        # Fill NaNs for cleaner display
        df_display = df_display.fillna("N/A")

        # Select relevant columns for metadata comparison
        cols = ["Place Name", "Year", "Latest Value", "Internal Label", "Source", "Dataset", "Provenance", "Method", "Period"]
        cols = [c for c in cols if c in df_display.columns]
        df_display = df_display[cols].sort_values(["Place Name", "Year"], ascending=[True, False])

        print("\n--- All Available Facets (Latest Observations) ---")
        print(df_display.to_string(index=False))

        # --- METADATA ANALYSIS: Identify Source with Latest Data ---
        print(f"\n--- Analysis: Which source has the latest data? ---")
        
        # Get the absolute latest year in the dataset
        if "Year" in df_display.columns:
            latest_year = df_display["Year"].max()
            print(f"The most recent data point in this set is from: {latest_year}")

            # Find which sources contribute to that latest year
            if "Internal Label" in df_display.columns:
                latest_sources = df_display[df_display["Year"] == latest_year]["Internal Label"].unique()
                print(f"Internal Labels providing {latest_year} data: {', '.join(latest_sources)}")

            # Summary of the absolute latest source per place
            latest_per_place = df_display.sort_values(["Place Name", "Year"], ascending=[True, False]).drop_duplicates("Place Name")
            print("\n--- Latest Source Per Place ---")
            
            display_cols = ["Place Name", "Year", "Internal Label", "Source", "Dataset", "Provenance"]
            display_cols = [c for c in display_cols if c in latest_per_place.columns]
            print(latest_per_place[display_cols].to_string(index=False))

        return df_display

    except Exception as e:
        print(f"Error during analysis: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    # 1. Get Country or Place ID from user directly
    country_dcid = input("Enter the country or region ID (e.g., 'country/USA', 'country/IND', 'geoId/06'): ").strip()
    
    if not country_dcid:
        print("No ID provided. Exiting.")
    else:
        print(f"Using DCID: {country_dcid}")
        
        # 2. Get target variable from user
        target_variable = input("Enter the target variable (default 'UnemploymentRate_Person'): ") or "UnemploymentRate_Person"

        # 3. Automatically get all States in that country/region
        all_states = get_all_states(country_dcid)
        
        # Include the place itself in the analysis
        places_to_analyze = [country_dcid] + all_states
        
        print(f"Found {len(all_states)} sub-regions. Total places to analyze: {len(places_to_analyze)}")
        
        if places_to_analyze:
            # 4. Run the analysis on all found places
            analyze_place_metadata(places_to_analyze, target_variable)
        else:
            print("No places to analyze.")
