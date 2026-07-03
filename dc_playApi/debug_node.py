import datacommons_client as dc
import os

def main():
    api_key = os.environ.get('DC_API_KEY')
    client = dc.DataCommonsClient(api_key=api_key)

    node_id = "Source"
    print(f"Fetching raw properties for {node_id}...")
    
    resp = client.node.fetch(node_id, "->*")
    print(resp.model_dump_json(indent=2))

if __name__ == "__main__":
    main()
