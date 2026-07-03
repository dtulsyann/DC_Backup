import datacommons_client as dc
import os
import json

def get_subclasses(client, node_id):
    resp = client.node.fetch(node_id, "->subClassOf")
    return resp.extract_connected_dcids(node_id, "subClassOf")

def main():
    api_key = os.environ.get('DC_API_KEY')
    client = dc.DataCommonsClient(api_key=api_key)

    nodes = ["Source", "Dataset", "Provenance"]
    
    results = {}
    for node_id in nodes:
        print(f"Analyzing {node_id}...")
        
        # 1. Properties of the node itself (outgoing)
        out_resp = client.node.fetch(node_id, "->*")
        out_arcs = out_resp.get_properties().root.get(node_id, {})
        node_metadata = list(out_arcs.keys())
        
        # 2. Properties that have this node as domain
        domain_resp = client.node.fetch(node_id, "<-domainIncludes")
        domain_arcs = domain_resp.get_properties().root.get(node_id, {})
        domain_props = [p.dcid for p in domain_arcs.get("domainIncludes", []) if p.dcid]
        
        # 3. Inheritance
        parents = get_subclasses(client, node_id)
        parent_props = {}
        for parent in parents:
            p_domain_resp = client.node.fetch(parent, "<-domainIncludes")
            p_domain_arcs = p_domain_resp.get_properties().root.get(parent, {})
            p_domain_props = [p.dcid for p in p_domain_arcs.get("domainIncludes", []) if p.dcid]
            parent_props[parent] = p_domain_props

        results[node_id] = {
            "metadata_properties": node_metadata,
            "domain_properties": domain_props,
            "parent_classes": list(parents),
            "inherited_properties": parent_props
        }

    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
