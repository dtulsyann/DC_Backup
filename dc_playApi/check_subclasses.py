import datacommons_client as dc
import os

def main():
    api_key = os.environ.get('DC_API_KEY')
    client = dc.DataCommonsClient(api_key=api_key)

    for node_id in ["Source", "Dataset", "Provenance"]:
        print(f"--- {node_id} ---")
        resp = client.node.fetch(node_id, "->subClassOf")
        subclasses = resp.extract_connected_dcids(node_id, "->subClassOf")
        print(f"subClassOf: {list(subclasses)}")

if __name__ == "__main__":
    main()
