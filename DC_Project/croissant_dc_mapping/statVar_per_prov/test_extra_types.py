import os
import requests
import json

api_key = os.environ.get("DC_API_KEY")
obs_url = "https://api.datacommons.org/v2/observation"
variables = ["dc/l81bkq93ypbs3"]

# Query other place types
extra_types = ["CongressionalDistrict", "ZipCode", "CensusTract"]
for ptype in extra_types:
    expression = f"geoId/10<-containedInPlace+{{typeOf:{ptype}}}"
    payload = {
        "select": ["variable", "entity", "date", "value"],
        "entity": {"expression": expression},
        "variable": {"dcids": variables}
    }
    res = requests.post(obs_url, json=payload, params={"key": api_key})
    print(f"Type {ptype}: Status {res.status_code}")
    if res.status_code == 200:
        by_var = res.json().get('byVariable', {}).get('dc/l81bkq93ypbs3', {}).get('byEntity', {})
        print(f"  Found {len(by_var)} entities")
    else:
        print(f"  Error message: {res.text[:200]}")
