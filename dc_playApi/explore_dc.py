import datacommons_client as dc
import pandas as pd
import os

def main():
    # Verify API Key
    api_key = os.environ.get('DC_API_KEY')
    if not api_key:
        print("Error: DC_API_KEY not found in environment.")
        return

    # Initialize the Data Commons Client
    client = dc.DataCommonsClient(api_key=api_key)
    #client = dc.DataCommonsClient(dc_instance="datacommons.org")

    print("--- Data Commons API Playground ---")
    
    # 1. Search for a variable
    query = "population"
    print(f"\nSearching for indicators related to: '{query}'...")
    
    # Use the client to fetch indicators
    search_response = client.resolve.fetch_indicators(query)
    
    # Check if we have any results
    if not search_response.entities or not search_response.entities[0].candidates:
        print("No results found.")
        return

    # Let's take the first result
    first_var = search_response.entities[0].candidates[0].dcid
    print(f"Found Variable: {first_var}")

    # 2. Get observations for a place
    # Let's use 'geoId/06' for California, USA
    place = 'wikidataId/Q1164'
    print(f"\nFetching observations for {first_var} in California ({place})...")
    
    # Using observations_dataframe to get a time series
    try:
        df = client.observations_dataframe(
            variable_dcids=first_var,
            entity_dcids=place,
            date="all"
        )
        
        if not df.empty:
            # Sort by date
            df = df.sort_values('date')
            
            print("\nLatest Observations:")
            # Selecting relevant columns for display
            display_cols = ['date', 'value', 'measurementMethod', 'observationPeriod']
            # Only show columns that exist in the dataframe
            actual_cols = [c for c in display_cols if c in df.columns]
            print(df[actual_cols].tail(5).to_string(index=False))
        else:
            print("No data found for this combination.")
    except Exception as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    main()
