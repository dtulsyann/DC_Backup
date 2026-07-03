from datacommons_client.client import DataCommonsClient  # Or standard: import datacommons as dc
import pandas as pd
import os
from dotenv import load_dotenv

# Load API Key
load_dotenv()

# Initialize Data Commons Client
# Note: If using the standard library, you can just use `import datacommons as dc` 
# and it automatically picks up the 'DC_API_KEY' environment variable.
client = DataCommonsClient(api_key=os.environ.get("DC_API_KEY"))

def resolve_place_name(name):
    """Resolves a human-readable name to a Data Commons DCID."""
    print(f"--- Resolving Place Name: {name} ---")
    try:
        resolved = client.resolve.fetch_dcids_by_name(names=[name]).to_flat_dict()
        dcid = resolved.get(name)
        return dcid[0] if isinstance(dcid, list) and dcid else dcid
    except Exception:
        # Fallback to direct property search if fetch_dcids_by_name isn't supported in your client version
        return name # e.g., 'country/USA'

def get_all_states(parent_dcid):
    """Finds all child entities of type 'AdministrativeArea1' (States/Provinces)."""
    print(f"--- Discovering sub-regions for {parent_dcid} ---")
    try:
        child_type = "AdministrativeArea1"
        children = client.node.fetch_place_children(parent_dcid, children_type=child_type)
        return [node['dcid'] for node in children.get(parent_dcid, [])]
    except Exception as e:
        print(f"Warning: Could not fetch child states: {e}")
        return []

def analyze_facets_and_extremes(place_dcids, variable_dcid):
    """Fetches full observation series for all facets, extracts latest, min, and max metadata."""
    print(f"\n--- Analyzing Historical Facets for Variable: {variable_dcid} ---")
    
    records = []
    
    # We loop or query the bulk observations. To get ALL facets reliably with timelines,
    # we use fetch_obs_all or equivalent series wrapper.
    try:
        # Fetching all series data for places and variable
        obs_data = client.observation.fetch_obs_all(entity_dcids=place_dcids, variable_dcids=[variable_dcid])
        
        # Parse the nested response structure
        # Structure: obs_data[variable][entity]['sourceObservations'] -> list of facets
        var_data = obs_data.get(variable_dcid, {})
        
        for entity_dcid, entity_info in var_data.items():
            sources = entity_info.get('sourceObservations', [])
            
            for source in sources:
                # Extract facet metadata
                facet = source.get('facet', {})
                import_name = facet.get('importName', 'N/A')
                provenance_url = facet.get('provenanceUrl', 'N/A')
                measurement_method = facet.get('measurementMethod', 'N/A')
                observation_period = facet.get('observationPeriod', 'N/A')
                
                # 'source' often maps to the provider domain or root provenance
                source_provider = provenance_url.split('//')[-1].split('/')[0] if provenance_url != 'N/A' else 'N/A'
                
                # Extract time series points to find Latest, Min, and Max
                points = source.get('points', [])
                if not points:
                    continue
                
                # Sort points chronologically by date string (YYYY-MM-DD or YYYY)
                points_sorted = sorted(points, key=lambda x: x.get('date', ''))
                
                # Latest Data
                latest_point = points_sorted[-1]
                latest_val = float(latest_point.get('value'))
                latest_date = latest_point.get('date')
                
                # Min and Max values
                valid_points = []
                for p in points:
                    try:
                        valid_points.append((float(p['value']), p['date']))
                    except ValueError:
                        continue
                
                if not valid_points:
                    continue
                    
                min_val, min_date = min(valid_points, key=lambda x: x[0])
                max_val, max_date = max(valid_points, key=lambda x: x[0])
                
                records.append({
                    "Place DCID": entity_dcid,
                    "Import Name": import_name,
                    "Provenance URL": provenance_url,
                    "Source": source_provider,
                    "Measurement Method": measurement_method,
                    "Observation Period": observation_period,
                    "Latest Year": latest_date,
                    "Latest Value": latest_val,
                    "Min Data (Value)": min_val,
                    "Min Data (Year)": min_date,
                    "Max Data (Value)": max_val,
                    "Max Data (Year)": max_date
                })
                
    except Exception as e:
        print(f"Error fetching/parsing data: {e}")
        return pd.DataFrame()

    df = pd.DataFrame(records)
    return df

if __name__ == "__main__":
    place_input = input("Enter country/region (e.g., 'USA', 'India'): ")
    country_dcid = resolve_place_name(place_input)
    
    if country_dcid:
        target_var = input("Enter variable (default 'UnemploymentRate_Person'): ") or "UnemploymentRate_Person"
        
        # Collect parent country + all states
        places = [country_dcid] + get_all_states(country_dcid)
        print(f"Analyzing {len(places)} total regions...")
        
        # Run analysis
        result_df = analyze_facets_and_extremes(places, target_var)
        
        if not result_df.empty:
            # Display configuration
            pd.set_option('display.max_columns', None)
            pd.set_option('display.width', 1000)
            
            print("\n--- Summary Table (All Facets with Min/Max) ---")
            print(result_df.to_string(index=False))
            
            # Optionally save to CSV
            result_df.to_csv("datacommons_facets_output.csv", index=False)
            print("\nResults successfully saved to 'datacommons_facets_output.csv'")
        else:
            print("No facet data could be retrieved for those selections.")
    else:
        print(f"Could not resolve '{place_input}'.")
