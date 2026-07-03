import os
import sys
import json
import subprocess
import requests

def get_bq_provenances():
    """
    Fetches the list of Provenance IDs from BigQuery using the bq CLI tool.
    """
    print("Fetching provenances from BigQuery...", flush=True)
    query = "SELECT id FROM `datcom-store.dc_kg_latest.Provenance`"
    cmd = [
        "bq", "query",
        "--project_id=datcom-store",
        "--format=json",
        "--max_rows=2000",
        "--use_legacy_sql=false",
        query
    ]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        records = json.loads(result.stdout)
        bq_ids = {row["id"] for row in records if "id" in row}
        return bq_ids
    except subprocess.CalledProcessError as e:
        print(f"Error running bq query: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error parsing BigQuery results: {e}", file=sys.stderr)
        sys.exit(1)

def get_api_provenances(api_key):
    """
    Fetches the list of Provenance DCIDs from the Data Commons v2 API.
    """
    print("Fetching provenances from Data Commons API...", flush=True)
    url = "https://api.datacommons.org/v2/node"
    headers = {
        "Content-Type": "application/json"
    }
    if api_key:
        headers["X-API-Key"] = api_key

    api_ids = set()
    next_token = None

    while True:
        payload = {
            "nodes": ["Provenance"],
            "property": "<-typeOf"
        }
        if next_token:
            payload["nextToken"] = next_token

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        arcs = data.get("data", {}).get("Provenance", {}).get("arcs", {})
        nodes = arcs.get("typeOf", {}).get("nodes", [])
        
        for node in nodes:
            if "dcid" in node:
                api_ids.add(node["dcid"])

        next_token = data.get("nextToken")
        if not next_token:
            break

    return api_ids

def main():
    api_key = os.environ.get("DC_API_KEY")
    if not api_key:
        print("Warning: DC_API_KEY environment variable not set. API request may fail.", file=sys.stderr)

    bq_ids = get_bq_provenances()
    api_ids = get_api_provenances(api_key)

    only_in_bq = bq_ids - api_ids
    only_in_api = api_ids - bq_ids
    in_both = bq_ids & api_ids

    print("\n--- Summary ---")
    print(f"Total provenances in BigQuery: {len(bq_ids)}")
    print(f"Total provenances in API:      {len(api_ids)}")
    print(f"Matching provenances (both):   {len(in_both)}")
    print(f"Only in BigQuery:             {len(only_in_bq)}")
    print(f"Only in API:                  {len(only_in_api)}")

    mismatches = {
        "only_in_bq": sorted(list(only_in_bq)),
        "only_in_api": sorted(list(only_in_api)),
        "in_both": sorted(list(in_both))
    }

    with open("mismatches.json", "w") as f:
        json.dump(mismatches, f, indent=2)
    print("\nDetailed mismatches saved to 'mismatches.json'")

if __name__ == "__main__":
    main()
