import json
import os

# Configuration
INPUT_FILE = 'provenances_full.json'
OUTPUT_DIR = 'croissant-dc-files'
REPORT_FILE = os.path.join(OUTPUT_DIR, 'missing_properties_report.json')

# Croissant Context Template
CONTEXT = {
    "@language": "en",
    "@vocab": "https://schema.org/",
    "sc": "https://schema.org/",
    "cr": "http://mlcommons.org/croissant/",
    "rai": "http://mlcommons.org/croissant/RAI/",
    "dct": "http://purl.org/dc/terms/",
    "citeAs": "cr:citeAs",
    "column": "cr:column",
    "conformsTo": "dct:conformsTo",
    "data": {
        "@id": "cr:data",
        "@type": "@json"
    },
    "dataType": {
        "@id": "cr:dataType",
        "@type": "@vocab"
    },
    "examples": {
        "@id": "cr:examples",
        "@type": "@json"
    },
    "extract": "cr:extract",
    "field": "cr:field",
    "fileProperty": "cr:fileProperty",
    "fileObject": "cr:fileObject",
    "fileSet": "cr:fileSet",
    "format": "cr:format",
    "includes": "cr:includes",
    "isLiveDataset": "cr:isLiveDataset",
    "jsonPath": "cr:jsonPath",
    "key": "cr:key",
    "md5": "cr:md5",
    "parentField": "cr:parentField",
    "path": "cr:path",
    "recordSet": "cr:recordSet",
    "references": "cr:references",
    "regex": "cr:regex",
    "repeated": "cr:repeated",
    "replace": "cr:replace",
    "separator": "cr:separator",
    "source": "cr:source",
    "subField": "cr:subField",
    "transform": "cr:transform"
}

def generate_mappings():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        provenances = json.load(f)

    missing_info_list = []

    for prov in provenances:
        dcid = prov.get('dcid')
        name = prov.get('name', 'unknown')
        raw_description = prov.get('description')
        license = prov.get('license', '') or ''
        
        dataset = prov.get('dataset', {}) or {}
        dataset_name = dataset.get('name', '') or ''
        dataset_url = dataset.get('url', '') or ''
        
        source = dataset.get('source', {}) or {}
        source_name = source.get('name', '') or ''
        source_url = source.get('url', '') or ''

        # Tracking missing properties
        missing_props = []
        if not raw_description: missing_props.append('description')
        if not license: missing_props.append('license')
        if not dataset_name: missing_props.append('dataset.name')
        if not dataset_url: missing_props.append('dataset.url')
        if not source_name: missing_props.append('dataset.source.name')
        if not source_url: missing_props.append('dataset.source.url')

        if missing_props:
            missing_info_list.append({
                "dcid": dcid,
                "name": name,
                "missing_properties": missing_props
            })

        # Format description
        if raw_description:
            formatted_description = f"This dataset contains information related to provenances of {name}, containing {raw_description}"
        else:
            formatted_description = ""

        # Construct JSON-LD
        mapping = {
            "@context": CONTEXT,
            "@type": "sc:Dataset",
            "name": dataset_name,
            "description": formatted_description,
            "license": license,
            "url": dataset_url,
            "conformsTo": "http://mlcommons.org/croissant/1.1",
            "creator": [
                {
                    "@type": "Organization",
                    "name": source_name,
                    "url": source_url
                }
            ],
            "distribution": [],
            "recordSet": []
        }

        # Save file
        file_path = os.path.join(OUTPUT_DIR, f"{name}.json")
        with open(file_path, 'w', encoding='utf-8') as f_out:
            json.dump(mapping, f_out, indent=2, ensure_ascii=False)

    # Save missing properties report
    with open(REPORT_FILE, 'w', encoding='utf-8') as f_rep:
        json.dump(missing_info_list, f_rep, indent=2, ensure_ascii=False)

    print(f"Generated {len(provenances)} files in '{OUTPUT_DIR}'")
    print(f"Missing properties report saved to '{REPORT_FILE}'")

if __name__ == "__main__":
    generate_mappings()
