import json
from urllib.parse import urlparse

# Discovered license URLs based on the domain of prov_url or fallbacks
domain_license_url_map = {
    "nces.ed.gov": "https://ies.ed.gov/funding/researchaccess.asp",
    "www.indec.gob.ar": "https://www.indec.gob.ar/indec/web/Institucional-Indec-Transparencia",
    "www.abs.gov.au": "https://creativecommons.org/licenses/by/4.0/",
    "datacommons.org": "https://datacommons.org/disclaimer",
    "www.bea.gov": "https://www.bea.gov/policies-and-information",
    "data.bis.org": "https://www.bis.org/terms_statistics.htm",
    "www.bls.gov": "https://www.bls.gov/bls/linksite.htm",
    "www.census.gov": "https://www.census.gov/about/policies.html",
    "www.ibge.gov.br": "https://www.ibge.gov.br/en/access-to-information/institutional/the-ibge.html",
    "aplicacoes.cidadania.gov.br": "https://creativecommons.org/licenses/by-nd/3.0/",
    "sidra.ibge.gov.br": "https://dados.gov.br/",
    "www.nsi.bg": "https://www.nsi.bg/en/pages/license-to-use-statistical-information-produced-and-disseminated-by-the-national-statistical-institute-485",
    "www.eia.gov": "https://www.eia.gov/about/copyrights_reuse.php",
    "www.cdc.gov": "https://www.cdc.gov/other/agencymaterials.html",
    "gis.cdc.gov": "https://www.cdc.gov/other/agencymaterials.html",
    "wonder.cdc.gov": "https://wonder.cdc.gov/datause.html#",
    "data.cdc.gov": "https://www.cdc.gov/other/agencymaterials.html",
    "wwwn.cdc.gov": "https://www.cdc.gov/nchs/data_access/ftp_data.htm",
    "www.atsdr.cdc.gov": "https://www.cdc.gov/other/agencymaterials.html",
    "ocrdata.ed.gov": "https://civilrightsdata.ed.gov/data",
    "civilrightsdata.ed.gov": "https://civilrightsdata.ed.gov/data",
    "caaspp-elpac.ets.org": "https://www.cde.ca.gov/re/di/or/copyright.asp",
    "www150.statcan.gc.ca": "https://www.statcan.gc.ca/en/reference/licence"
}

def main():
    # Load first 50 provenances
    with open("provenances_full.json", "r") as f:
        full_data = json.load(f)
    first_50 = full_data[:50]
        
    output_data = []
    
    for i, entry in enumerate(first_50):
        dcid = entry.get("dcid")
        existing_license = entry.get("license")
        prov_url = entry.get("prov_url")
        
        # Determine the jet_license URL
        # 1. If existing license is a URL, use it
        if existing_license and existing_license.startswith("http"):
            jet_license = existing_license
        else:
            # 2. Otherwise discover license based on domain of prov_url
            if prov_url:
                parsed = urlparse(prov_url)
                domain = parsed.netloc
                
                # Match domain or use CDC / Census / BLS fallbacks
                jet_license = domain_license_url_map.get(domain)
                if not jet_license:
                    if "cdc.gov" in domain:
                        jet_license = "https://www.cdc.gov/other/agencymaterials.html"
                    elif "census.gov" in domain:
                        jet_license = "https://www.census.gov/about/policies.html"
                    elif "bls.gov" in domain:
                        jet_license = "https://www.bls.gov/bls/linksite.htm"
                    elif "bea.gov" in domain:
                        jet_license = "https://www.bea.gov/policies-and-information"
                    else:
                        jet_license = f"Unknown (please check {prov_url})"
            else:
                jet_license = "No URL available"
                
        output_data.append({
            "dcid": dcid,
            "license": existing_license,
            "jet_license": jet_license
        })

    # Write output to provenances_licenses.json
    with open("provenances_licenses.json", "w") as f:
        json.dump(output_data, f, indent=2)
        
    print("Successfully populated provenances_licenses.json with URL licenses.")

if __name__ == "__main__":
    main()
