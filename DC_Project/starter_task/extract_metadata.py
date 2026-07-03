from datacommons_client.client import DataCommonsClient
import pandas as pd
import os
import json
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load API Key
load_dotenv()

# Initialize Client
client = DataCommonsClient(api_key=os.environ.get("DC_API_KEY"))

# Cache for metadata resolution to avoid redundant API calls
facet_cache = {}

def resolve_all_facets(import_names):
    """
    Resolves provenance, dataset, and source info for a list of importNames in batch.
    """
    to_resolve = [name for name in import_names if name and name != "N/A" and name not in facet_cache]
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

def get_global_places(stat_var):
    """
    Fetches ALL places globally that have data for the statistical variable.
    Discovers Countries, AdministrativeArea1 (States), and AdministrativeArea2 (Counties).
    """
    print(f"--- Discovering Places Globally for {stat_var} ---")

    all_places = []
    level_counts = {}

    # Levels to discover
    levels = ["Country", "AdministrativeArea1", "AdministrativeArea2"]

    for level in levels:
        print(f"Discovering {level}...")
        try:
            # We use parent_entity="Earth" and entity_dcids="all" to find all descendants of that type.
            # We use date="latest" for speed during discovery.
            df = client.observations_dataframe(
                variable_dcids=stat_var,
                date="latest",
                entity_dcids="all",
                parent_entity="Earth",
                entity_type=level
            )
            if not df.empty:
                found = df['entity'].unique().tolist()
                count = len(found)
                print(f"  Found {count} {level}s.")
                all_places.extend(found)
                level_counts[level] = count
            else:
                print(f"  No {level}s found.")
                level_counts[level] = 0
        except Exception as e:
            print(f"  Warning: Could not discover {level} from Earth: {e}")
            level_counts[level] = "Error"

    # Remove duplicates
    all_places = list(set(all_places))

    print("\n--- Discovery Summary ---")
    for level, count in level_counts.items():
        print(f"{level}: {count}")
    print(f"Total unique places collected: {len(all_places)}\n")

    return all_places

def extract_metadata(stat_var, place_dcids):
    """
    Fetches all historical observations and aggregates metadata per facet.
    """
    print(f"--- Fetching all historical data for {stat_var} ---")
    
    results = {}
    batch_size = 50  # Decreased batch size to prevent 504 Gateway Timeout
    
    import time
    
    num_batches = (len(place_dcids) - 1) // batch_size + 1
    for i in range(0, len(place_dcids), batch_size):
        batch = place_dcids[i:i + batch_size]
        print(f"Processing batch {i//batch_size + 1}/{num_batches}...")
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # date="all" is crucial here to get Min/Max dates
                df = client.observations_dataframe(
                    date="all",
                    entity_dcids=batch,
                    variable_dcids=stat_var
                )
                
                if df.empty:
                    break # Successful but empty, move to next batch

                # Collect all unique importNames in this batch to resolve them
                if "importName" in df.columns:
                    unique_imports = df["importName"].unique().tolist()
                    resolve_all_facets(unique_imports)

                # Facet columns
                facet_cols = ["importName", "measurementMethod", "provenanceUrl", "observationPeriod", "unit"]
                available_facet_cols = [c for c in facet_cols if c in df.columns]
                
                # Grouping to find min/max dates
                for place_id, place_df in df.groupby("entity"):
                    if place_id not in results:
                        results[place_id] = []
                    
                    # Further group by the available facet metadata
                    for _, facet_df in place_df.groupby(available_facet_cols, dropna=False):
                        row = facet_df.iloc[0]
                        
                        import_name = row.get("importName", "N/A")
                        prov_id, dataset_name, source_name = facet_cache.get(import_name, (f"dc/base/{import_name}", "N/A", "N/A"))

                        metadata_entry = {
                            "source": source_name,
                            "dataset": dataset_name,
                            "provenance": prov_id,
                            "unit": row.get("unit", "N/A"),
                            "measurement_method": row.get("measurementMethod", "N/A"),
                            "observation_period": row.get("observationPeriod", "N/A"),
                            "min_date": str(facet_df["date"].min()),
                            "max_date": str(facet_df["date"].max())
                        }
                        
                        # Clean up "N/A" values
                        metadata_entry = {k: (v if pd.notna(v) else "N/A") for k, v in metadata_entry.items()}
                        
                        results[place_id].append(metadata_entry)
                
                break # Success, break out of retry loop


            except Exception as e:
                print(f"Warning: Error processing batch starting at index {i} (Attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"Failed to process batch starting at index {i} after {max_retries} attempts.")

    return {stat_var: results}

if __name__ == "__main__":
    target_var = input("Enter the Statistical Variable (e.g., 'Count_Person'): ") or "Count_Person"
    
    places = get_global_places(target_var)
    
    if not places:
        print("No places found. Exiting.")
    else:
        final_output = extract_metadata(target_var, places)
        
        # Save to a unique file based on the Statistical Variable
        output_file = f"{target_var}_metadata.json"
        with open(output_file, "w") as f:
            json.dump(final_output, f, indent=2)
        
        extracted_count = len(final_output[target_var])
        print(f"\nSuccessfully extracted metadata for {extracted_count} places.")
        print(f"Output saved to: {output_file}")
