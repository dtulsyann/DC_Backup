import pandas as pd
import os
import json
from urllib.parse import urlparse
from dotenv import load_dotenv
from datacommons_client.client import DataCommonsClient


# Initialize Client
client = DataCommonsClient(api_key=os.environ.get("DC_API_KEY"))

def get_source_name(url):
    """Simplified source resolver based on URL."""
    if pd.isna(url) or not isinstance(url, str):
        return "N/A"
    return urlparse(url).netloc or "N/A"

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
    batch_size = 200  
    
    num_batches = (len(place_dcids) - 1) // batch_size + 1
    for i in range(0, len(place_dcids), batch_size):
        batch = place_dcids[i:i + batch_size]
        print(f"Processing batch {i//batch_size + 1}/{num_batches}...")
        
        try:
            # date="all" is crucial here to get Min/Max dates
            df = client.observations_dataframe(
                date="all",
                entity_dcids=batch,
                variable_dcids=stat_var
            )
            
            if df.empty:
                continue

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
                    
                    metadata_entry = {
                        "source": get_source_name(row.get("provenanceUrl")),
                        "importName": row.get("importName", "N/A"),
                        "provenanceUrl": row.get("provenanceUrl", "N/A"),
                        "unit": row.get("unit", "N/A"),
                        "measurementMethod": row.get("measurementMethod", "N/A"),
                        "observationPeriod": row.get("observationPeriod", "N/A"),
                        "earliestDate": str(facet_df["date"].min()),
                        "latestDate": str(facet_df["date"].max())
                    }
                    
                    # Clean up "N/A" values
                    metadata_entry = {k: (v if pd.notna(v) else "N/A") for k, v in metadata_entry.items()}
                    
                    results[place_id].append(metadata_entry)
            
        except Exception as e:
            print(f"Error processing batch starting at index {i}: {e}")

    return {stat_var: results}

if __name__ == "__main__":
    target_var = input("Enter the Statistical Variable (e.g., 'Count_Person'): ") or "Count_Person"
    
    places = get_global_places(target_var)
    
    if not places:
        print("No places found. Exiting.")
    else:
        final_output = extract_metadata(target_var, places)
        
        # Replace '/' with '_' to avoid directory issues in filenames
        safe_var_name = target_var.replace("/", "_")

        output_file = f"{safe_var_name}_metadata.json"
        with open(output_file, "w") as f:
            json.dump(final_output, f, indent=2)
        
        extracted_count = len(final_output[target_var])
        print(f"\nSuccessfully extracted metadata for {extracted_count} places.")
        print(f"Output saved to: {output_file}")

