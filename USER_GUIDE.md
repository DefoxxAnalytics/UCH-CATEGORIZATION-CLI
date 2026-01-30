# UCH Spend Categorization - User Guide

## Purpose

This tool categorizes UCH procurement transactions by mapping them to:
- **UNSPSC codes** - Industry-standard product/service classification
- **Healthcare Taxonomy** - 5-level hierarchy for spend analytics reporting

## Prerequisites

### Software Requirements

- Python 3.7 or higher
- Required packages: pandas, openpyxl

### Installation

Open a command prompt and run:

```bash
pip install pandas openpyxl
```

### Required Files

Ensure these files are in the project folder:

| File | Description |
|------|-------------|
| `categorize_uch.py` | The categorization script |
| `UCH-2026Data.xlsx` | Source procurement data |

## Running the Script

### Step 1: Open Command Prompt

Navigate to the project folder:

```bash
cd C:\Users\MLawali\Documents\Projects\VSTX-Projects\NewClients\UCH-Categorization
```

### Step 2: Run the Script

```bash
python categorize_uch.py
```

### Step 3: Review Output

The script displays progress and a summary:

```
Loading UCH data...
Processing Services Only (1236 rows)...
Processing Org Data Pull (4649 rows)...
Writing output to UCH-2026Data_Categorized.xlsx...

=== Summary ===
Total transactions: 5885
With UNSPSC code: 5885 (100.0%)
With Taxonomy L1: 5885 (100.0%)
With Taxonomy L3: 5702 (96.9%)
...
```

## Output File

### Location

`UCH-2026Data_Categorized.xlsx` (same folder as the script)

### Contents

The output contains 3 sheets matching the input structure:

| Sheet | Description |
|-------|-------------|
| Supplier Listing | Unchanged from input |
| Services Only | Original data + categorization columns |
| Org Data Pull | Original data + categorization columns |

### New Columns Added

| Column | Description | Example |
|--------|-------------|---------|
| UNSPSC_Code | 8-digit UNSPSC code | 72101516 |
| UNSPSC_Category_Name | UNSPSC description | Elevator repair services |
| UNSPSC_Category_Description | Same as above | Elevator repair services |
| Original_Custom_Code | Internal code if mapped | 99000033 |
| Taxonomy_L1 | Level 1 category | Facilities |
| Taxonomy_L2 | Level 2 category | Facilities Services |
| Taxonomy_L3 | Level 3 category | Building Maintenance |
| Taxonomy_L4 | Level 4 category | Elevator Maintenance |
| Taxonomy_L5 | Level 5 category | (if applicable) |
| Taxonomy_Key | Full path | Facilities > Facilities Services > Building Maintenance |

## Understanding the Results

### Taxonomy Hierarchy

The Healthcare Taxonomy has 5 levels. Not all items have all 5 levels populated:

- **Level 1** (100% coverage) - Broadest category (e.g., Facilities, Medical)
- **Level 2** (100% coverage) - Sub-category (e.g., Cleaning, Equipment)
- **Level 3** (96.9% coverage) - Specific area (e.g., Janitorial Services)
- **Level 4** (53.9% coverage) - Detail level
- **Level 5** (39.5% coverage) - Most specific

### Taxonomy Key

The `Taxonomy_Key` column provides the full path for easy filtering:

```
Facilities > Facilities Services > Building Maintenance > Elevator Maintenance
```

Use Excel filters on this column to analyze spend by category.

### Custom Code Handling

Some transactions have internal codes (starting with 99). These are automatically mapped to standard UNSPSC codes. The original code is preserved in `Original_Custom_Code` for reference.

## Using the Output in Excel

### Filter by Category

1. Open `UCH-2026Data_Categorized.xlsx`
2. Select the data range
3. Click **Data > Filter**
4. Use dropdown on `Taxonomy_L1` to filter by top-level category

### Create Pivot Table

1. Select all data including headers
2. Click **Insert > PivotTable**
3. Drag `Taxonomy_Key` to Rows
4. Drag `Paid Amount` to Values
5. Set Values to **Sum**

### Export for Reporting

The categorized data can be exported to other tools:
- Power BI: Open Excel file directly
- Tableau: Connect to Excel data source
- CSV: Save As > CSV format

## Troubleshooting

### "No module named pandas"

Run:
```bash
pip install pandas openpyxl
```

### "FileNotFoundError: UCH-2026Data.xlsx"

Ensure the input file is in the same folder as the script.

### Empty Taxonomy Columns

Some items may not have taxonomy mappings if:
- The UNSPSC code is not in the mapping tables
- The item is a new category not yet configured

Report these to the administrator for mapping updates.

## Updating Mappings

If new transaction types need categorization, the script can be updated:

1. **New internal codes** - Add to `CUSTOM_CODE_MAPPING`
2. **New UNSPSC mappings** - Add to `DETAILED_TAXONOMY_MAP`
3. **New keyword rules** - Add to `DESCRIPTION_RULES`

See [CLAUDE.md](CLAUDE.md) for technical details.

## Support

For questions or issues:
- Technical support: VTX Solutions / Defoxx Analytics
- Data questions: UCH Procurement Team
