import json
from urllib.parse import urlparse

# Predefined domain license URLs mapping
domain_license_url_map = {
    # NCES / Department of Ed
    "nces.ed.gov": "https://ies.ed.gov/funding/researchaccess.asp",
    "ocrdata.ed.gov": "https://civilrightsdata.ed.gov/data",
    "civilrightsdata.ed.gov": "https://civilrightsdata.ed.gov/data",
    "collegescorecard.ed.gov": "https://collegescorecard.ed.gov/data/",
    "caaspp-elpac.ets.org": "https://www.cde.ca.gov/re/di/or/copyright.asp",
    
    # CDC
    "www.cdc.gov": "https://www.cdc.gov/other/agencymaterials.html",
    "data.cdc.gov": "https://www.cdc.gov/other/agencymaterials.html",
    "gis.cdc.gov": "https://www.cdc.gov/other/agencymaterials.html",
    "wonder.cdc.gov": "https://wonder.cdc.gov/datause.html#",
    "wwwn.cdc.gov": "https://www.cdc.gov/nchs/data_access/ftp_data.htm",
    "www.atsdr.cdc.gov": "https://www.cdc.gov/other/agencymaterials.html",
    "ephtracking.cdc.gov": "https://www.cdc.gov/other/agencymaterials.html",
    
    # US Federal Gov
    "www.bea.gov": "https://www.bea.gov/policies-and-information",
    "www.census.gov": "https://www.census.gov/about/policies.html",
    "data.census.gov": "https://www.census.gov/about/policies.html",
    "www2.census.gov": "https://www.census.gov/about/policies.html",
    "www.eia.gov": "https://www.eia.gov/about/copyrights_reuse.php",
    "epa.gov": "https://www.epa.gov/privacy/privacy-and-security-notice",
    "noaa.gov": "https://www.noaa.gov/protecting-our-data",
    "fema.gov": "https://www.fema.gov/about/openfema/terms-conditions",
    "bts.dot.gov": "https://www.bts.gov/information-guidelines",
    "nhtsa.gov": "https://www.nhtsa.gov/website-disclaimer",
    "deadiversion.usdoj.gov": "https://www.justice.gov/legalpolicies",
    "dol.gov": "https://www.dol.gov/general/aboutdol/copyright",
    "nass.usda.gov": "https://www.nass.usda.gov/About_NASS/Disclaimers/index.php",
    "waterdata.usgs.gov": "https://www.usgs.gov/information-policies-and-instructions/copyrights-and-permissions",
    "ncses.nsf.gov": "https://www.nsf.gov/policies/reproduction.jsp",
    "ncsesdata.nsf.gov": "https://www.nsf.gov/policies/reproduction.jsp",
    "drought.gov": "https://www.drought.gov/about/data-use-policy",
    "huduser.gov": "https://www.huduser.gov/portal/about/legal.html",
    "commerce.gov": "https://www.commerce.gov/about/policies/privacy-policy",
    "trade.gov": "https://www.trade.gov/privacy-and-disclaimer",
    "ntia.gov": "https://www.ntia.gov/page/privacy-policy",
    "bjs.gov": "https://bjs.ojp.gov/about",
    "hazards.fema.gov": "https://www.fema.gov/about/openfema/terms-conditions",
    
    # US State Gov
    "healthdata.dshs.texas.gov": "https://www.dshs.texas.gov/policies/web-site-disclaimer.aspx",
    "www.health.ny.gov": "https://www.health.ny.gov/privacy.htm",
    "www.tn.gov": "https://www.tn.gov/help/terms---disclaimer.html",
    
    # UK Gov
    "www.gov.uk": "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
    "geoportal.statistics.gov.uk": "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
    
    # Singapore Gov
    "www.singstat.gov.sg": "https://www.singstat.gov.sg/terms-of-use",
    
    # Korea Gov
    "kosis.kr": "https://kosis.kr/eng/oneStopService/oneStopService_01List.jsp",
    
    # Finland Gov
    "pxdata.stat.fi": "https://creativecommons.org/licenses/by/4.0/",
    
    # Denmark Gov
    "www.statbank.dk": "https://www.dst.dk/en/Statistik/vilkaar",
    
    # Sweden Gov
    "www.statistikdatabasen.scb.se": "https://creativecommons.org/licenses/by/4.0/",
    
    # Poland Gov
    "stat.gov.pl": "https://stat.gov.pl/en/terms-of-use/",
    
    # France Gov
    "www.insee.fr": "https://www.insee.fr/en/information/1892141",
    
    # Mongolia Gov
    "www.1212.mn": "http://www.1212.mn/en/contents/about-us",
    
    # UAE Gov
    "bayanat.ae": "https://bayanat.ae/en/terms-and-conditions",
    
    # India Gov
    "censusindia.gov.in": "https://data.gov.in/government-open-data-license-india",
    "mospi.gov.in": "https://data.gov.in/government-open-data-license-india",
    "esankhyiki.mospi.gov.in": "https://data.gov.in/government-open-data-license-india",
    "ndap.niti.gov.in": "https://data.gov.in/government-open-data-license-india",
    "pgi.seshagun.gov.in": "https://data.gov.in/government-open-data-license-india",
    "indiawris.gov.in": "https://data.gov.in/government-open-data-license-india",
    "geosadak-pmgsy.nic.in": "https://data.gov.in/government-open-data-license-india",
    "lgdirectory.gov.in": "https://data.gov.in/government-open-data-license-india",
    "hmis.nhp.gov.in": "https://data.gov.in/government-open-data-license-india",
    "socialjustice.gov.in": "https://data.gov.in/government-open-data-license-india",
    "rbi.org.in": "https://data.gov.in/government-open-data-license-india",
    
    # Vietnam Gov
    "www.gso.gov.vn": "https://www.gso.gov.vn/en/terms-of-use/",
    
    # Indonesia Gov
    "www.bps.go.id": "https://www.bps.go.id/en/disclaimer",
    
    # Ireland Gov
    "www.cso.ie": "https://creativecommons.org/licenses/by/4.0/",
    
    # Israel Gov
    "www.cbs.gov.il": "https://creativecommons.org/licenses/by/4.0/",
    
    # Japan Gov
    "www.e-stat.go.jp": "https://www.e-stat.go.jp/en/terms-of-use",
    
    # Mexico Gov
    "www.inegi.org.mx": "https://creativecommons.org/licenses/by/4.0/",
    
    # International Orgs
    "www.oecd.org": "https://www.oecd.org/termsandconditions/",
    "data-explorer.oecd.org": "https://www.oecd.org/termsandconditions/",
    "data.oecd.org": "https://www.oecd.org/termsandconditions/",
    "stats.oecd.org": "https://www.oecd.org/termsandconditions/",
    "www.worldbank.org": "https://www.worldbank.org/en/about/legal/terms-of-use-for-datasets",
    "databank.worldbank.org": "https://www.worldbank.org/en/about/legal/terms-of-use-for-datasets",
    "datacatalog.worldbank.org": "https://www.worldbank.org/en/about/legal/terms-of-use-for-datasets",
    "datatopics.worldbank.org": "https://www.worldbank.org/en/about/legal/terms-of-use-for-datasets",
    "www.who.int": "https://www.who.int/about/policies/publishing/copyright-and-licensing",
    "data.who.int": "https://www.who.int/about/policies/publishing/copyright-and-licensing",
    "www.fao.org": "https://www.fao.org/contact-us/terms-licensing/en/",
    "data.un.org": "https://data.un.org/Host.aspx?Content=UNdataUse",
    "geoportal.un.org": "https://data.un.org/Host.aspx?Content=UNdataUse",
    "unstats.un.org": "https://data.un.org/Host.aspx?Content=UNdataUse",
    
    # Copernicus / Climate
    "cds.climate.copernicus.eu": "https://cds.climate.copernicus.eu/disclaimer-privacy",
    "land.copernicus.eu": "https://land.copernicus.eu/en/copyright-policy",
    "climatetrace.org": "https://creativecommons.org/licenses/by/4.0/",
    "api.climatetrace.org": "https://creativecommons.org/licenses/by/4.0/",
    
    # NYC
    "data.cityofnewyork.us": "https://www.nyc.gov/home/terms-of-use.page",
    
    # Zurich
    "data.stadt-zuerich.ch": "https://creativecommons.org/publicdomain/zero/1.0/",
    
    # Academics & NGOs
    "atlasdata.dartmouth.edu": "https://creativecommons.org/licenses/by-nc/4.0/",
    "opportunityinsights.org": "https://creativecommons.org/licenses/by/4.0/",
    "www.rff.org": "https://creativecommons.org/licenses/by/4.0/",
    "www.stanfordecholab.com": "https://creativecommons.org/licenses/by/4.0/",
    "www.glims.org": "https://creativecommons.org/licenses/by/4.0/",
    "www.marineregions.org": "https://creativecommons.org/licenses/by/4.0/",
    "projects.datameet.org": "https://creativecommons.org/licenses/by/4.0/",
    "data.humdata.org": "https://creativecommons.org/licenses/by/4.0/",
    "www.feedingamerica.org": "https://creativecommons.org/licenses/by-nc/4.0/",
    "map.feedingamerica.org": "https://creativecommons.org/licenses/by-nc/4.0/",
    "educationdata.urban.org": "https://creativecommons.org/licenses/by/4.0/",
    
    # NY Times / Wikipedia
    "www.nytimes.com": "https://creativecommons.org/licenses/by-nc/4.0/",
    "en.wikipedia.org": "https://creativecommons.org/licenses/by-sa/4.0/",
    "en.m.wikipedia.org": "https://creativecommons.org/licenses/by-sa/4.0/",
    "www.wikipedia.org": "https://creativecommons.org/licenses/by-sa/4.0/",
    "www.wikidata.org": "https://creativecommons.org/publicdomain/zero/1.0/",
    
    # OpenFIGI
    "www.openfigi.com": "https://www.openfigi.com/terms",
    
    # S2 Geometry
    "s2geometry.io": "https://www.apache.org/licenses/LICENSE-2.0",
    
    # GitHub
    "github.com": "https://docs.github.com/en/site-policy/github-terms/github-terms-of-service",
    
    # DOI fallback
    "doi.org": "https://creativecommons.org/publicdomain/zero/1.0/",
    
    # Fallback mappings from first 50
    "www.indec.gob.ar": "https://www.indec.gob.ar/indec/web/Institucional-Indec-Transparencia",
    "www.abs.gov.au": "https://creativecommons.org/licenses/by/4.0/",
    "datacommons.org": "https://datacommons.org/disclaimer",
    "www.ibge.gov.br": "https://www.ibge.gov.br/en/access-to-information/institutional/the-ibge.html",
    "aplicacoes.cidadania.gov.br": "https://creativecommons.org/licenses/by-nd/3.0/",
    "sidra.ibge.gov.br": "https://dados.gov.br/",
    "www.nsi.bg": "https://www.nsi.bg/en/pages/license-to-use-statistical-information-produced-and-disseminated-by-the-national-statistical-institute-485",
    "www150.statcan.gc.ca": "https://www.statcan.gc.ca/en/reference/licence",
    "www12.statcan.gc.ca": "https://www.statcan.gc.ca/en/reference/licence"
}

def main():
    # Read the full provenances file
    with open("provenances_full.json", "r") as f:
        data = json.load(f)
        
    updated_data = []
    
    for entry in data:
        # Extract domain
        prov_url = entry.get("prov_url")
        domain = ""
        if prov_url:
            parsed = urlparse(prov_url)
            domain = parsed.netloc
            
        # Determine the jet_license URL
        existing_license = entry.get("license")
        
        # 1. First priority: Use existing license URL if it exists
        if existing_license and existing_license.startswith("http"):
            jet_license = existing_license
        else:
            # 2. Match domain or subdomains
            jet_license = None
            if domain in domain_license_url_map:
                jet_license = domain_license_url_map[domain]
            else:
                # Suffix / subdomain check
                for d_key, url_val in domain_license_url_map.items():
                    if domain.endswith(d_key):
                        jet_license = url_val
                        break
            
            # 3. Suffix fallbacks
            if not jet_license:
                if domain.endswith(".gov.in") or domain.endswith(".nic.in"):
                    jet_license = "https://data.gov.in/government-open-data-license-india"
                elif domain.endswith(".gov.uk"):
                    jet_license = "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/"
                elif domain.endswith(".gov.au"):
                    jet_license = "https://creativecommons.org/licenses/by/4.0/"
                elif domain.endswith(".gov.br"):
                    jet_license = "https://dados.gov.br/"
                elif domain.endswith(".gov"):
                    jet_license = "https://www.usa.gov/government-works"
                elif "opendataforafrica.org" in domain:
                    jet_license = "https://creativecommons.org/licenses/by/4.0/"
                else:
                    # Generic default or construct from existing non-url license
                    if existing_license:
                        if "apache" in existing_license.lower():
                            jet_license = "https://www.apache.org/licenses/LICENSE-2.0"
                        elif "creative commons" in existing_license.lower() or "cc-by" in existing_license.lower():
                            jet_license = "https://creativecommons.org/licenses/by/4.0/"
                        else:
                            jet_license = f"https://datacommons.org/disclaimer?lic={existing_license}"
                    else:
                        jet_license = "https://datacommons.org/disclaimer"
                        
        # Construct the entry preserving key ordering so jet_license is below license
        new_entry = {}
        for k, v in entry.items():
            new_entry[k] = v
            if k == "license":
                new_entry["jet_license"] = jet_license
                
        updated_data.append(new_entry)

    # Write the output back to provenances_full.json
    with open("provenances_full.json", "w") as f:
        json.dump(updated_data, f, indent=2)
        
    print(f"Successfully processed all {len(updated_data)} elements and added jet_license to provenances_full.json")

if __name__ == "__main__":
    main()
