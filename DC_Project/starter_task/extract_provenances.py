import requests
import json
import sys
import os

API_KEY = os.environ.get('DC_API_KEY')
BASE_URL = 'https://api.datacommons.org/v2/node'

def fetch_provenance_dcids(limit=None):
    dcids = []
    next_token = ''
    while True:
        params = {
            'key': API_KEY,
            'nodes': 'Provenance',
            'property': '<-typeOf',
            'nextToken': next_token
        }
        resp = requests.get(BASE_URL, params=params)
        if resp.status_code != 200:
            print(f"Error fetching DCIDs: {resp.text}")
            break
        data = resp.json()
        
        nodes = data.get('data', {}).get('Provenance', {}).get('arcs', {}).get('typeOf', {}).get('nodes', [])
        for node in nodes:
            if 'dcid' in node:
                dcids.append(node['dcid'])
            if limit and len(dcids) >= limit:
                return dcids
        
        next_token = data.get('nextToken')
        if not next_token:
            break
    return dcids

def fetch_node_properties(dcids):
    batch_size = 50
    results = {}
    for i in range(0, len(dcids), batch_size):
        batch = dcids[i:i+batch_size]
        payload = {
            'nodes': batch,
            'property': '->*'
        }
        headers = {'X-API-Key': API_KEY}
        resp = requests.post(BASE_URL, json=payload, headers=headers)
        if resp.status_code != 200:
            print(f"Error fetching properties for batch {i}: {resp.text}")
            continue
        data = resp.json()
        results.update(data.get('data', {}))
    return results

def format_output(node_data):
    lines = []
    header = f"{'Property':<35} {'Value':<100}"
    separator = "-" * 135
    
    for dcid, content in node_data.items():
        lines.append(header)
        lines.append(f"{'dcid':<35} {dcid:<100}")
        
        arcs = content.get('arcs', {})
        # Sort properties for consistency
        for prop in sorted(arcs.keys()):
            details = arcs[prop]
            nodes = details.get('nodes', [])
            for val_node in nodes:
                value = val_node.get('dcid') or val_node.get('value', '')
                # Handle potentially very long values
                value_str = str(value)
                lines.append(f"{prop:<35} {value_str:<100}")
        lines.append("\n" + "="*135 + "\n")
    return "\n".join(lines)

if __name__ == "__main__":
    if not API_KEY:
        print("Error: DC_API_KEY environment variable not set.")
        sys.exit(1)
    
    dcids = fetch_provenance_dcids()
    if not dcids:
        print("No provenances found.")
        sys.exit(0)
        
    all_properties = fetch_node_properties(dcids)
    print(format_output(all_properties))
