# Data Commons Metadata Analyzer

This script allows you to compare the source and methodology (metadata) for statistical variables across different geographic levels.

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set your Data Commons API Key:
   ```bash
   export DC_API_KEY='your_api_key_here'
   ```

## How to use
- Open `analyze_metadata.py`.
- Edit the `my_places` list with any DCIDs you want to compare.
- Change `target_variable` to any statistical variable (e.g., `UnemploymentRate_Person`).
- Run the script:
   ```bash
   python analyze_metadata.py
   ```

## What to look for
- **Source Consistency:** Does the source change from a national agency to an international one (UN, World Bank)?
- **Methodology:** Does the `measurementMethod` change (e.g., Census vs. Projection)?
- **Data Freshness:** Are the latest years consistent across all levels?
