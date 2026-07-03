import json
import os

with open("datasets_provs.json") as f:
    data = json.load(f)

artifact_path = "/usr/local/google/home/dtulsyan/.gemini/jetski/brain/6d90ebc0-1c84-484e-b5d9-804690dd26f5/datacommons_datasets.md"

with open(artifact_path, "w") as f:
    f.write("# Data Commons Datasets and Provenances\n\n")
    f.write("This document lists all datasets in Data Commons along with the provenances under each dataset and their counts.\n\n")
    for ds in data:
        name = ds["dataset_name"]
        dcid = ds["dataset_dcid"]
        count = ds["provenance_count"]
        f.write(f"## {name}\n")
        f.write(f"**DCID**: `{dcid}`  \n")
        f.write(f"**Provenance Count**: {count}\n\n")
        f.write("### Provenances\n")
        for prov in ds["provenances"]:
            f.write(f"- `{prov}`\n")
        f.write("\n")
