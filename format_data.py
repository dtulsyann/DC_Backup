import json
import sys

# Load JSON output from the curl command (passed as an argument or read from a file, but here I'll just embed the data or read from a file if I saved it. Actually, I didn't save it, so I'll curl again and pipe it.)
import json

def get_val(node_data, prop):
    arcs = node_data.get('arcs', {})
    if prop not in arcs:
        return ""
    nodes = arcs[prop].get('nodes', [])
    if not nodes:
        return ""
    
    # Try to get value or name
    vals = []
    for n in nodes:
        if 'value' in n:
            vals.append(n['value'])
        elif 'name' in n:
            vals.append(n['name'])
        elif 'dcid' in n:
            vals.append(n['dcid'])
    return ", ".join(vals)

with open('data.json') as f:
    data = json.load(f)['data']

headers = ["dcid", "name", "description", "license", "url", "isPartOf", "source", 
           "lastDataRefreshDate", "earliestDataImportDate", "importedSourceReleaseDate", 
           "earliestObservationDate", "latestObservationDate"]

print("| " + " | ".join(headers) + " |")
print("|" + "|".join(["---"] * len(headers)) + "|")

for dcid in sorted(data.keys()):
    row = [dcid]
    node_data = data[dcid]
    for h in headers[1:]:
        val = get_val(node_data, h)
        row.append(val.replace('\n', ' '))
    print("| " + " | ".join(row) + " |")

