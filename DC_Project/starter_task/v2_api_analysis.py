from datacommons_client.client import DataCommonsClient
import pandas as pd
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Data Commons Client
api_key = os.environ.get("DC_API_KEY")
client = DataCommonsClient(api_key=api_key)

def analyze_hierarchy_metadata(place_dcids):
    """
    PHASE 1: PLACE METADATA AUDIT
    Analyzes the structural metadata of the provided hierarchy.
    """
    print("\n" + "="*60)
    print("PHASE 1: PLACE API (V2) - STRUCTURAL METADATA AUDIT")
    print("="*60)
    
    # 1. Basic Identity Metadata
    names = client.node.fetch_entity_names(place_dcids)
    
    place_audit = []
    for dcid in place_dcids:
        # Fetch 'typeOf' and 'provenance' for structural context
        type_resp = client.node.fetch_property_values(dcid, "typeOf")
        types = [t.dcid for t in type_resp.get_properties().get(dcid, {}).get("typeOf", [])]
        
        # Discover variable density (How many variables are available for this place?)
        vars_resp = client.observation.fetch_available_statistical_variables(dcid)
        var_count = len(vars_resp.get(dcid, []))
        
        place_audit.append({
            "DCID": dcid,
            "Name": names.get(dcid).value if dcid in names else "Unknown",
            "Types": ", ".join(types),
            "Available Variables": var_count
        })
    
    print("\n--- Place Identity & Variable Density ---")
    print(pd.DataFrame(place_audit).to_string(index=False))

    # 2. Relationship Metadata (Breadcrumbs)
    print("\n--- Relationship Metadata (Parentage) ---")
    for dcid in place_dcids:
        parents = client.node.fetch_place_parents(dcid)
        parent_list = parents.get(dcid, [])
        # Extract names safely from the parent objects/dicts
        parent_names = []
        for p in reversed(parent_list):
            p_name = p.get("name") if isinstance(p, dict) else getattr(p, "name", "Unknown")
            parent_names.append(p_name)
        
        parent_str = " -> ".join(parent_names) if parent_names else "Root"
        print(f"Path to {dcid}: {parent_str}")

def analyze_observation_facets(place_dcids, variable_dcids):
    """
    PHASE 2: OBSERVATION METADATA (FACETS) AUDIT
    Deep-dives into the provenance, methodology, and units of specific data points.
    """
    print("\n" + "="*60)
    print("PHASE 2: OBSERVATION API (V2) - FACET & PROVENANCE AUDIT")
    print("="*60)
    
    for var_dcid in variable_dcids:
        print(f"\n>>> Auditing Facets for: {var_dcid}")
        
        # Fetch observations with 'date="latest"' to see the most recent metadata state
        df = client.observations_dataframe(
            variable_dcids=var_dcid,
            entity_dcids=place_dcids,
            date="latest"
        )
        
        if df.empty:
            print(f"No metadata found for {var_dcid} across these places.")
            continue

        # metadata analysis: grouping by facets
        # We look for: Source (importName), Method (measurementMethod), Unit, and Time Period
        df_meta = df.rename(columns={
            "entity_name": "Place",
            "date": "Latest Date",
            "importName": "Source",
            "measurementMethod": "Method",
            "observationPeriod": "Period",
            "unit": "Unit"
        })
        
        display_cols = ["Place", "Latest Date", "Source", "Method", "Unit", "Period"]
        # Filter only existing columns
        display_cols = [c for c in display_cols if c in df_meta.columns]
        
        print(df_meta[display_cols].to_string(index=False))

        # Diversity Summary
        print(f"\n--- Metadata Diversity Summary for {var_dcid} ---")
        unique_sources = df_meta["Source"].unique() if "Source" in df_meta.columns else []
        unique_methods = df_meta["Method"].unique() if "Method" in df_meta.columns else []
        
        print(f"Total Unique Sources: {len(unique_sources)}")
        for s in unique_sources: print(f"  - Source: {s}")
        
        print(f"Total Unique Methods: {len(unique_methods)}")
        for m in unique_methods: print(f"  - Method: {m}")

if __name__ == "__main__":
    # Define a hierarchy to audit: Country -> State -> County
    # Example: USA -> California -> Santa Clara
    places = ["country/USA", "geoId/06", "geoId/06085"]
    
    # Audit a mix of variables to see metadata differences (Demographics vs Economics)
    variables = ["Count_Person", "UnemploymentRate_Person"]
    
    try:
        # Run structural audit
        analyze_hierarchy_metadata(places)
        
        # Run data provenance/facet audit
        analyze_observation_facets(places, variables)
        
        print("\n" + "="*60)
        print("METADATA AUDIT COMPLETE")
        print("="*60)
        
    except Exception as e:
        print(f"\n[CRITICAL ERROR] {e}")
        import traceback
        traceback.print_exc()
