import os
from datacommons_client.client import DataCommonsClient

def print_properties(title, data, node_dcid):
    print(f"\n--- {title} for {node_dcid} ---")
    
    node_data = data.get('data', {}).get(node_dcid, {})
    arcs = node_data.get('arcs', {})
    
    if not arcs:
        print("No properties found.")
        return

    for prop in sorted(arcs.keys()):
        content = arcs[prop]
        print( f"{prop} :")
        nodes = content.get('nodes', [])
        for node in nodes:
            name_or_val = node.get('name') or node.get('value')
            dcid = node.get('dcid')
            if name_or_val and dcid:
                print(f"  - {name_or_val} (DCID: {dcid})")
            elif name_or_val:
                print(f"  - {name_or_val}")
            elif dcid:
                print(f"  - (DCID: {dcid})")
            else:
                print(f"  - [Unknown Node]")

# Initialize the client using environment variable
api_key = os.getenv("DC_API_KEY")
if not api_key:
    print("Error: DC_API_KEY environment variable not set.")
    exit(1)

client = DataCommonsClient(api_key=api_key)

# Define the node DCID you want to explore
node_dcid = "dc/base/BEA_USStatesQuarterlyGDP"

# Get all OUTGOING properties
raw_outgoing = client.node.fetch(
    node_dcids=[node_dcid], 
    expression="->*"
).to_dict()

import json
print("\n--- Raw Outgoing Data ---")
print(json.dumps(raw_outgoing, indent=2))

# Print results
print_properties("Outgoing Properties", raw_outgoing, node_dcid)
