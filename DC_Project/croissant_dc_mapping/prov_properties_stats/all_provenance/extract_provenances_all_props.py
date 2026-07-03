import os
import sys
import json
from collections import defaultdict
from datacommons_client.client import DataCommonsClient

def get_node_property(node_data, prop_name, default=None):
    """
    Helper to extract a property value from the node data dictionary.
    """
    arcs = node_data.get("arcs", {})
    prop_nodes = arcs.get(prop_name, {}).get("nodes", [])
    if not prop_nodes:
        return default
    
    val = prop_nodes[0].get("value") 
    return val

def get_node_dcid(node_data, prop_name):
    """
    Helper to extract a DCID from a property.
    """
    arcs = node_data.get("arcs", {})
    prop_nodes = arcs.get(prop_name, {}).get("nodes", [])
    if not prop_nodes:
        return None
    return prop_nodes[0].get("dcid")

def fetch_all_provenances(api_key: str, output_file: str = "provenances_all_props.json") -> None:
    """
    Fetches Provenance nodes, extracts all their properties, computes missing property stats, 
    and traverses to Dataset and Source levels to extract metadata.
    """
    client = DataCommonsClient(api_key=api_key)

    # 1. Get all nodes of type 'Provenance'
    print("Fetching Provenance DCIDs...", file=sys.stderr)
    try:
        res = client.node.fetch(node_dcids=["Provenance"], expression="<-typeOf").to_dict()
        provenance_nodes = res.get("data", {}).get("Provenance", {}).get("arcs", {}).get("typeOf", {}).get("nodes", [])
        provenance_dcids = [dcid for node in provenance_nodes if (dcid := node.get("dcid"))]
    except Exception as e:
        print(f"Error fetching provenances: {e}", file=sys.stderr)
        return
    
    if not provenance_dcids:
        print("No provenances found.", file=sys.stderr)
        return
        
    total_provenances = len(provenance_dcids)
    print(f"Found {total_provenances} provenances.", file=sys.stderr)

    # 2. Fetch Provenance details and find Dataset DCIDs
    print("Fetching Provenance details...", file=sys.stderr)
    provenance_data_map = {}
    dataset_dcids = set()
    
    # To track property presence across all provenances
    property_counts = defaultdict(int)
    all_properties_seen = set()
    
    batch_size = 50
    for i in range(0, len(provenance_dcids), batch_size):
        batch = provenance_dcids[i:i+batch_size]
        batch_res = client.node.fetch(node_dcids=batch, expression="->*").to_dict()
        data = batch_res.get("data", {})
        
        for dcid in batch:
            node_data = data.get(dcid, {})
            arcs = node_data.get("arcs", {})
            
            # Track properties for this provenance
            for prop in arcs.keys():
                property_counts[prop] += 1
                all_properties_seen.add(prop)
            
            # Base properties that were extracted previously
            prov_entry = {
                "dcid": dcid,
                "name": get_node_property(node_data, "name"),
                "description": get_node_property(node_data, "description"),
                "sourceDataUrl": get_node_property(node_data, "sourceDataUrl"),
                "license": get_node_property(node_data, "license"),
                "dataset_dcid": get_node_dcid(node_data, "isPartOf")
            }
            
            # Include all other properties dynamically
            for prop, prop_data in arcs.items():
                if prop not in ["typeOf"]:  # Skip typeOf to reduce noise, though you can include it if needed
                    nodes = prop_data.get("nodes", [])
                    if nodes:
                        vals = []
                        for n in nodes:
                            if "value" in n: vals.append(n["value"])
                            elif "dcid" in n: vals.append(n["dcid"])
                        
                        if prop not in prov_entry: # Don't overwrite explicitly formatted properties above
                            if len(vals) == 1:
                                prov_entry[prop] = vals[0]
                            elif len(vals) > 1:
                                prov_entry[prop] = vals

            provenance_data_map[dcid] = prov_entry
            if prov_entry["dataset_dcid"]:
                dataset_dcids.add(prov_entry["dataset_dcid"])

    # 3. Fetch Dataset details and find Source DCIDs
    print(f"Fetching {len(dataset_dcids)} Dataset details...", file=sys.stderr)
    dataset_data_map = {}
    source_dcids = set()
    
    dataset_list = list(dataset_dcids)
    for i in range(0, len(dataset_list), batch_size):
        batch = dataset_list[i:i+batch_size]
        batch_res = client.node.fetch(node_dcids=batch, expression="->*").to_dict()
        data = batch_res.get("data", {})
        
        for dcid in batch:
            node_data = data.get(dcid, {})
            ds_entry = {
                "name": get_node_property(node_data, "name"),
                "url": get_node_property(node_data, "url"),
                "source_dcid": get_node_dcid(node_data, "isPartOf")
            }
            dataset_data_map[dcid] = ds_entry
            if ds_entry["source_dcid"]:
                source_dcids.add(ds_entry["source_dcid"])

    # 4. Fetch Source details
    print(f"Fetching {len(source_dcids)} Source details...", file=sys.stderr)
    source_data_map = {}
    source_list = list(source_dcids)
    for i in range(0, len(source_list), batch_size):
        batch = source_list[i:i+batch_size]
        batch_res = client.node.fetch(node_dcids=batch, expression="->*").to_dict()
        data = batch_res.get("data", {})
        
        for dcid in batch:
            node_data = data.get(dcid, {})
            source_data_map[dcid] = {
                "name": get_node_property(node_data, "name"),
                "url": get_node_property(node_data, "url")
            }

    # 5. Assemble final hierarchy
    print("Assembling final hierarchy...", file=sys.stderr)
    final_output = []
    for prov_dcid, prov in provenance_data_map.items():
        ds_dcid = prov.pop("dataset_dcid", None)
        dataset_info = None
        
        if ds_dcid:
            ds_data = dataset_data_map.get(ds_dcid, {})
            src_dcid = ds_data.get("source_dcid")
            source_info = None
            
            if src_dcid:
                source_info = source_data_map.get(src_dcid)
            
            dataset_info = {
                "name": ds_data.get("name"),
                "url": ds_data.get("url"),
                "source": source_info
            }
            
        prov["dataset"] = dataset_info
        final_output.append(prov)

    with open(output_file, "w") as f:
        json.dump(final_output, f, indent=2)
    
    print(f"Successfully wrote {len(final_output)} provenances to {output_file}", file=sys.stderr)

    # 6. Output missing properties stats
    missing_stats = {}
    print("\n--- Missing Properties Statistics ---", file=sys.stderr)
    for prop in sorted(all_properties_seen):
        missing_count = total_provenances - property_counts[prop]
        missing_stats[prop] = {
            "present": property_counts[prop],
            "missing": missing_count
        }
        print(f"Property '{prop}': Missing in {missing_count} / {total_provenances} provenances", file=sys.stderr)
        
    stats_file = "provenance_missing_stats.json"
    with open(stats_file, "w") as f:
        json.dump(missing_stats, f, indent=2)
    print(f"Wrote missing statistics to {stats_file}", file=sys.stderr)


if __name__ == "__main__":
    dc_api_key = os.environ.get('DC_API_KEY')
    if not dc_api_key:
        print("Error: DC_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)
        
    fetch_all_provenances(api_key=dc_api_key)
