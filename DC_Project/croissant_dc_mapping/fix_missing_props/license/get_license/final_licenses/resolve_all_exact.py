import json
from urllib.parse import urlparse

# Predefined domain license URLs mapping for all 153 domains in the dataset
domain_license_url_map = {
    # NCES / Department of Ed
    "nces.ed.gov": "https://ies.ed.gov/funding/researchaccess.asp",
    "ocrdata.ed.gov": "https://civilrightsdata.ed.gov/data",
    "civilrightsdata.ed.gov": "https://civilrightsdata.ed.gov/data",
    "collegescorecard.ed.gov": "https://collegescorecard.ed.gov/data/",
    "caaspp-elpac.ets.org": "https://www.cde.ca.gov/",
    "educationdata.urban.org": "https://creativecommons.org/licenses/by/4.0/",
    
    # CDC
    "www.cdc.gov": "https://www.cdc.gov/other/agencymaterials.html",
    "data.cdc.gov": "https://www.cdc.gov/other/agencymaterials.html",
    "gis.cdc.gov": "https://www.cdc.gov/other/agencymaterials.html",
    "wonder.cdc.gov": "https://wonder.cdc.gov/wonder/help/restrictions.html",
    "wwwn.cdc.gov": "https://www.cdc.gov/nchs/policy/data-user-agreement.html",
    "www.atsdr.cdc.gov": "https://www.cdc.gov/other/agencymaterials.html",
    "ephtracking.cdc.gov": "https://www.cdc.gov/other/agencymaterials.html",
    
    # US Federal Gov
    "www.bea.gov": "https://www.bea.gov/policies-and-information",
    "www.census.gov": "https://www.census.gov/about/policies/open-gov/open-data.html",
    "data.census.gov": "https://www.census.gov/about/policies/open-gov/open-data.html",
    "www2.census.gov": "https://www.census.gov/about/policies/open-gov/open-data.html",
    "www.eia.gov": "https://www.eia.gov/about/copyrights_reuse.php",
    "epa.gov": "https://www.epa.gov/privacy/privacy-and-security-notice",
    "noaa.gov": "https://www.usa.gov/policies",
    "fema.gov": "https://www.fema.gov/about/openfema/terms-conditions",
    "bts.dot.gov": "https://www.bts.gov/information-guidelines",
    "nhtsa.gov": "https://www.nhtsa.gov/website-disclaimer",
    "deadiversion.usdoj.gov": "https://www.justice.gov/legalpolicies",
    "dol.gov": "https://www.dol.gov/general/aboutdol/copyright",
    "nass.usda.gov": "https://www.usda.gov/policies-and-links",
    "waterdata.usgs.gov": "https://www.usgs.gov/information-policies-and-instructions/copyrights-and-permissions",
    "ncses.nsf.gov": "https://www.nsf.gov/policies/reuse.jsp",
    "ncsesdata.nsf.gov": "https://www.nsf.gov/policies/reuse.jsp",
    "drought.gov": "https://www.drought.gov/",
    "huduser.gov": "https://www.usa.gov/policies",
    "commerce.gov": "https://www.commerce.gov/about/policies/privacy-policy",
    "trade.gov": "https://www.trade.gov/",
    "ntia.gov": "https://www.ntia.gov/",
    "bjs.gov": "https://bjs.ojp.gov/about",
    "hazards.fema.gov": "https://www.fema.gov/about/openfema/terms-conditions",
    "www.fema.gov": "https://www.fema.gov/about/openfema/terms-conditions",
    "www.bjs.gov": "https://bjs.ojp.gov/about",
    "www.commerce.gov": "https://www.commerce.gov/about/policies/privacy-policy",
    "www.dol.gov": "https://www.dol.gov/general/aboutdol/copyright",
    "www.eia.gov": "https://www.eia.gov/about/copyrights_reuse.php",
    "www.epa.gov": "https://www.epa.gov/privacy/privacy-and-security-notice",
    "www.fec.gov": "https://www.fec.gov/",
    "www.federalreserve.gov": "https://www.federalreserve.gov/",
    "www.noaa.gov": "https://www.usa.gov/policies",
    "www.nass.usda.gov": "https://www.usda.gov/policies-and-links",
    "www.ncei.noaa.gov": "https://www.usa.gov/policies",
    "www.ncdc.noaa.gov": "https://www.usa.gov/policies",
    "www.deadiversion.usdoj.gov": "https://www.justice.gov/legalpolicies",
    "www.bts.dot.gov": "https://www.bts.gov/information-guidelines",
    "www.huduser.gov": "https://www.usa.gov/policies",
    "www.trade.gov": "https://www.trade.gov/",
    "www.ntia.gov": "https://www.ntia.gov/",
    "www.bjs.gov": "https://bjs.ojp.gov/about",
    "www.bls.gov": "https://www.bls.gov/bls/linksite.htm",
    "hazards.fema.gov": "https://www.fema.gov/about/openfema/terms-conditions",
    "www.fema.gov": "https://www.fema.gov/about/openfema/terms-conditions",
    "fam.nwcg.gov": "https://www.nwcg.gov/disclaimer-and-copyright-notice",
    "www.mtbs.gov": "https://www.usa.gov/policies",
    
    # US State Gov
    "healthdata.dshs.texas.gov": "https://www.dshs.texas.gov/",
    "www.health.ny.gov": "https://www.health.ny.gov/",
    "www.tn.gov": "https://www.tn.gov/about-tn/policies.html",
    
    # UK Gov
    "www.gov.uk": "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
    "geoportal.statistics.gov.uk": "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
    
    # Singapore Gov
    "www.singstat.gov.sg": "https://www.singstat.gov.sg/terms-of-use",
    
    # Korea Gov
    "kosis.kr": "https://kosis.kr/eng/",
    
    # Finland Gov
    "pxdata.stat.fi": "https://creativecommons.org/licenses/by/4.0/",
    
    # Denmark Gov
    "www.statbank.dk": "https://www.dst.dk/en/",
    
    # Sweden Gov
    "www.statistikdatabasen.scb.se": "https://creativecommons.org/licenses/by/4.0/",
    
    # Poland Gov
    "stat.gov.pl": "https://stat.gov.pl/en/",
    
    # France Gov
    "www.insee.fr": "https://www.etalab.gouv.fr/licence-ouverte-open-licence",
    
    # Mongolia Gov
    "www.1212.mn": "http://www.1212.mn/en/contents/about-us",
    
    # UAE Gov
    "bayanat.ae": "https://bayanat.ae/",
    
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
    "www.gso.gov.vn": "https://www.gso.gov.vn/en/",
    
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

    "ourworldindata.org": "https://ourworldindata.org/",
    "www.stats.govt.nz": "https://www.stats.govt.nz/about-us/copyright/",
    "www.openfigi.com": "https://www.openfigi.com/",
    "www.worldbank.org": "https://www.worldbank.org/en/about/legal/terms-of-use-for-datasets",
    "databank.worldbank.org": "https://www.worldbank.org/en/about/legal/terms-of-use-for-datasets",
    "datacatalog.worldbank.org": "https://www.worldbank.org/en/about/legal/terms-of-use-for-datasets",
    "datatopics.worldbank.org": "https://www.worldbank.org/en/about/legal/terms-of-use-for-datasets",
    "www.who.int": "https://www.who.int/about/policies/terms-of-use",
    "data.who.int": "https://www.who.int/about/policies/terms-of-use",
    "www.fao.org": "https://www.fao.org/contact-us/terms/en/",
    "data.un.org": "https://data.un.org/Host.aspx?Content=UNdataUse",
    "geoportal.un.org": "https://data.un.org/Host.aspx?Content=UNdataUse",
    "unstats.un.org": "https://data.un.org/Host.aspx?Content=UNdataUse",
    
    # Copernicus / Climate
    "cds.climate.copernicus.eu": "https://cds.climate.copernicus.eu/disclaimer-privacy",
    "land.copernicus.eu": "https://land.copernicus.eu/",
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
    
    # Fallback mappings
    "www.indec.gob.ar": "https://www.indec.gob.ar/indec/web/Institucional-Indec-Transparencia",
    "www.abs.gov.au": "https://creativecommons.org/licenses/by/4.0/",
    "datacommons.org": "https://creativecommons.org/licenses/by/4.0/",
    "www.ibge.gov.br": "https://www.ibge.gov.br/en/access-to-information/institutional/the-ibge.html",
    "aplicacoes.cidadania.gov.br": "https://creativecommons.org/licenses/by-nd/3.0/",
    "sidra.ibge.gov.br": "https://dados.gov.br/",
    "www.nsi.bg": "https://www.nsi.bg/en/pages/license-to-use-statistical-information-produced-and-disseminated-by-the-national-statistical-institute-485",
    "www150.statcan.gc.ca": "https://www.statcan.gc.ca/en/reference/licence",
    "www12.statcan.gc.ca": "https://www.statcan.gc.ca/en/reference/licence"
}

# Specific dataset-level licenses mapping for known microdata / special provenances
exact_dataset_licenses = {
    # WONDER natality/mortality data use restrictions
    "CDCMortality": "https://wonder.cdc.gov/wonder/help/restrictions.html",
    "CDCWonderNatality": "https://wonder.cdc.gov/wonder/help/restrictions.html",
    "CDCWonder_NNDSS_InfectiousAnnual": "https://wonder.cdc.gov/wonder/help/restrictions.html",
    "CDCWonder_NNDSS_InfectiousWeekly": "https://wonder.cdc.gov/wonder/help/restrictions.html",
    "CDC_Mortality_UnderlyingCause": "https://wonder.cdc.gov/wonder/help/restrictions.html",
    "CDC_Mortality_UnderlyingCause_SingleRace": "https://wonder.cdc.gov/wonder/help/restrictions.html"
}

def resolve_license(entry):
    dcid = entry.get("dcid")
    
    # Extract clean basename of dcid (without dc/base/)
    dcid_base = dcid.replace("dc/base/", "")
    
    # 1. Check if we have exact dataset override
    if dcid_base in exact_dataset_licenses:
        return exact_dataset_licenses[dcid_base]
        
    # Check if this is a WONDER dataset by suffix or name
    if "wonder" in dcid.lower() or "mortality" in dcid.lower():
        prov_url = entry.get("prov_url") or ""
        if "wonder.cdc.gov" in prov_url:
            return "https://wonder.cdc.gov/wonder/help/restrictions.html"
            
    # Check if there is a specific NCHS user agreement or FTP data license already in the provenance
    existing_license = entry.get("license")
    if existing_license and "data-user-agreement" in existing_license:
        return "https://www.cdc.gov/nchs/policy/data-user-agreement.html"
    if existing_license and "ftp_data" in existing_license:
        return "https://www.cdc.gov/nchs/policy/data-user-agreement.html"
        
    # 2. Extract prov_url domain
    prov_url = entry.get("prov_url")
    domain = ""
    if prov_url:
        parsed = urlparse(prov_url)
        domain = parsed.netloc
        
    # 3. Match against domain mapping
    jet_license = None
    if domain in domain_license_url_map:
        jet_license = domain_license_url_map[domain]
    else:
        # Check subdomains/suffix matching
        for d_key, url_val in domain_license_url_map.items():
            if domain.endswith(d_key):
                jet_license = url_val
                break
                
    # 4. Suffix fallbacks
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
            # Fallback to existing URL license if present, else default
            if existing_license and existing_license.startswith("http"):
                jet_license = existing_license
            elif existing_license:
                if "apache" in existing_license.lower():
                    jet_license = "https://www.apache.org/licenses/LICENSE-2.0"
                elif "creative commons" in existing_license.lower() or "cc-by" in existing_license.lower():
                    jet_license = "https://creativecommons.org/licenses/by/4.0/"
                else:
                    jet_license = "https://creativecommons.org/licenses/by/4.0/"
            else:
                jet_license = "https://creativecommons.org/licenses/by/4.0/"
                
    return jet_license

def main():
    import os
    dir_path = os.path.dirname(os.path.abspath(__file__))
    
    # Load the full dataset
    with open(os.path.join(dir_path, "provenances_full.json"), "r") as f:
        full_data = json.load(f)
        
    updated_full_data = []
    output_licenses_only = []
    
    for entry in full_data:
        jet_license = resolve_license(entry)
        
        # 1. Update entry preserving dict order
        new_entry = {}
        for k, v in entry.items():
            if k == "jet_license":
                continue
            new_entry[k] = v
            if k == "license":
                new_entry["jet_license"] = jet_license
        updated_full_data.append(new_entry)
        
        # 2. Add to licenses-only mapping list
        output_licenses_only.append({
            "dcid": entry.get("dcid"),
            "license": entry.get("license"),
            "jet_license": jet_license
        })
        
    # Write full provenances file with jet_license URLs
    with open(os.path.join(dir_path, "provenances_full.json"), "w") as f:
        json.dump(updated_full_data, f, indent=2)
        
    # Write licenses-only file containing all 627 elements
    with open(os.path.join(dir_path, "provenances_licenses.json"), "w") as f:
        json.dump(output_licenses_only, f, indent=2)
        
    print(f"Processed all {len(updated_full_data)} entries.")
    print("Generated provenances_full.json and provenances_licenses.json in final_licenses.")

if __name__ == "__main__":
    main()
