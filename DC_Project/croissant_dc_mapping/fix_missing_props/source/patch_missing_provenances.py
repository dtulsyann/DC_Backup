import json
import os

input_file = '/usr/local/google/home/dtulsyan/DC_Project/croissant_dc_mapping/provenances_full.json'
output_file = '/usr/local/google/home/dtulsyan/DC_Project/croissant_dc_mapping/patched_missing_provenances.json'

missing_dcids = [
    "dc/base/DEA_DrugCodes",
    "dc/base/FiresS2Cells",
    "dc/base/FloodsS2Cells",
    "dc/base/IndiaGeoCoordinates_Simplified",
    "dc/base/RFFGridGeos",
    "dc/base/S2Cells",
    "dc/base/TideGaugeStations",
    "dc/base/WeatherNOAA",
    "dc/base/WikipediaStatsData"
]

patches = {
    "dc/base/DEA_DrugCodes": {
        "description": "Controlled substances from Section 1308 of the most recent issue of Title 21 Code of Federal Regulations (CFR), section 1308.",
        "license": "Public Domain",
        "dataset": {
            "name": "DEA Drug Codes",
            "url": "https://www.deadiversion.usdoj.gov/21cfr/cfr/2108cfrt.htm",
            "source": {
                "name": "Drug Enforcement Administration (DEA)",
                "url": "https://www.dea.gov/"
            }
        }
    },
    "dc/base/FiresS2Cells": {
        "description": "S2Cells from levels 10 to 13 that have data on fires.",
        "license": "Apache License 2.0",
        "dataset": {
            "name": "S2 Cells - Fires Data",
            "url": "https://s2geometry.io/resources/s2cell_statistics.html",
            "source": {
                "name": "S2 Geometry",
                "url": "https://s2geometry.io/"
            }
        }
    },
    "dc/base/FloodsS2Cells": {
        "description": "S2Cells from levels 10 to 13 that have data on floods.",
        "license": "Apache License 2.0",
        "dataset": {
            "name": "S2 Cells - Floods Data",
            "url": "https://s2geometry.io/resources/s2cell_statistics.html",
            "source": {
                "name": "S2 Geometry",
                "url": "https://s2geometry.io/"
            }
        }
    },
    "dc/base/IndiaGeoCoordinates_Simplified": {
        "description": "Simplified geographic coordinates and boundaries for Indian states and districts.",
        "license": "https://creativecommons.org/licenses/by-sa/2.5/in/",
        "dataset": {
            "name": "India Geo Coordinates Simplified",
            "url": "http://projects.datameet.org/maps",
            "source": {
                "name": "DataMeet",
                "url": "http://datameet.org/"
            }
        }
    },
    "dc/base/RFFGridGeos": {
        "description": "Includes GeoGridPlace_0.25Degree and GeoGridPlace_4KM entities for the US associated with weather variability statistics.",
        "license": "https://www.rff.org/about/terms-and-conditions/",
        "dataset": {
            "name": "Resources for the Future (RFF) Grid Geos",
            "url": "https://www.rff.org/publications/data-tools/",
            "source": {
                "name": "Resources for the Future (RFF)",
                "url": "https://www.rff.org/"
            }
        }
    },
    "dc/base/S2Cells": {
        "description": "S2 Geometry cells defining spherical geometry hierarchy.",
        "license": "Apache License 2.0",
        "dataset": {
            "name": "S2 Cells Hierarchy",
            "url": "https://s2geometry.io/resources/s2cell_statistics.html",
            "source": {
                "name": "S2 Geometry",
                "url": "https://s2geometry.io/"
            }
        }
    },
    "dc/base/TideGaugeStations": {
        "description": "Includes TideGaugeStation and GeoGridPlace_1Deg entities containing sea-level projection data.",
        "license": "Public Domain",
        "dataset": {
            "name": "Tide Gauge Stations and Sea-level Projections",
            "url": "https://podaac.jpl.nasa.gov/",
            "source": {
                "name": "NASA Jet Propulsion Laboratory (JPL) PO.DAAC",
                "url": "https://podaac.jpl.nasa.gov/"
            }
        }
    },
    "dc/base/WeatherNOAA": {
        "description": "Weather and climate data provided by the National Oceanic and Atmospheric Administration (NOAA).",
        "license": "Public Domain",
        "dataset": {
            "name": "NOAA Weather Data",
            "url": "https://www.noaa.gov/weather",
            "source": {
                "name": "National Oceanic and Atmospheric Administration (NOAA)",
                "url": "https://www.noaa.gov/"
            }
        }
    },
    "dc/base/WikipediaStatsData": {
        "description": "Statistical data from Wikipedia",
        "license": "https://creativecommons.org/licenses/by-sa/4.0/",
        "dataset": {
            "name": "Wikipedia Statistics Data",
            "url": "https://stats.wikimedia.org/",
            "source": {
                "name": "Wikimedia Foundation",
                "url": "https://wikimediafoundation.org/"
            }
        }
    }
}

def main():
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    patched_provenances = []
    
    for item in data:
        if item.get("dcid") in missing_dcids:
            dcid = item["dcid"]
            patch = patches[dcid]
            
            # Apply patches (update description if missing or replace, set license, set dataset)
            if not item.get("description"):
                item["description"] = patch["description"]
            
            if not item.get("license"):
                item["license"] = patch["license"]
                
            item["dataset"] = patch["dataset"]
            
            patched_provenances.append(item)
            
    with open(output_file, 'w') as f:
        json.dump(patched_provenances, f, indent=2)
        
    print(f"Successfully wrote {len(patched_provenances)} patched provenances to {output_file}")

if __name__ == "__main__":
    main()
