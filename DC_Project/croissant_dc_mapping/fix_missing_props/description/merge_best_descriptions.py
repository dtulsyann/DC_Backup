import json
import os

rich_file = '/usr/local/google/home/dtulsyan/DC_Project/croissant_dc_mapping/fix_missing_props/description/rich_descriptions_provenances.json'
web_file = '/usr/local/google/home/dtulsyan/DC_Project/croissant_dc_mapping/fix_missing_props/description/web_scraped_descriptions.json'
output_file = '/usr/local/google/home/dtulsyan/DC_Project/croissant_dc_mapping/fix_missing_props/description/best_descriptions_provenances.json'

# These phrases typically indicate that the web scraper pulled generic homepage SEO marketing rather than dataset details.
bad_phrases = [
    "search the world's information",
    "google has many special features",
    "data commons aggregates",
    "mission is to serve",
    "find the latest news",
    "discover the data collections",
    "provides trusted environmental data",
    "welcome to",
    "explore our",
    "official website",
    "this section provides",
    "information on the importance",
    "further details are provided",
    "downloadformat="
]

def main():
    with open(rich_file, 'r') as f:
        rich_data = json.load(f)
    with open(web_file, 'r') as f:
        web_data = json.load(f)
        
    web_dict = {x.get("dcid"): x.get("description", "") for x in web_data}
    
    merged_data = []
    web_chosen_count = 0
    rich_chosen_count = 0
    
    for rich_item in rich_data:
        dcid = rich_item.get("dcid")
        rich_desc = rich_item.get("description", "")
        web_desc = web_dict.get(dcid, "")
        
        chosen_desc = rich_desc
        
        if web_desc and web_desc != rich_desc:
            web_lower = web_desc.lower()
            is_generic = any(phrase in web_lower for phrase in bad_phrases)
            
            # If the web description is practically just the name, skip it
            if web_lower == rich_item.get("name", "").lower():
                is_generic = True
                
            if not is_generic and len(web_desc) > 25:
                chosen_desc = web_desc
                web_chosen_count += 1
            else:
                rich_chosen_count += 1
        else:
            rich_chosen_count += 1
            
        final_item = rich_item.copy()
        final_item["description"] = chosen_desc
        
        # Override the WDI manually as discussed earlier
        if dcid == "dc/base/WorldDevelopmentIndicators":
            final_item["description"] = "The World Development Indicators (WDI) is the World Bank's premier compilation of internationally comparable statistics, featuring over 1,400 time-series indicators covering global social, economic, financial, environmental, and political development for over 200 economies."
            
        merged_data.append(final_item)
        
    with open(output_file, 'w') as f:
        json.dump(merged_data, f, indent=2)
        
    print(f"Merge complete! Saved to {output_file}")
    print(f"  - Web Scraped version was selected for {web_chosen_count} datasets (Rich, detailed paragraphs).")
    print(f"  - AI-Generated version was selected for {rich_chosen_count} datasets (Fell back from generic SEO marketing or missing data).")

if __name__ == "__main__":
    main()
