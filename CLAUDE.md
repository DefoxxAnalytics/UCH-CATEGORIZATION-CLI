# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Project**: UCH Spend Categorization
**Client**: UCH (University of Cincinnati Health)
**Purpose**: Map procurement/spend data to UNSPSC codes and Healthcare Taxonomy for spend analytics
**Company**: VTX Solutions / Defoxx Analytics
**Status**: Complete

## Project Status

The categorization script is **production-ready** and achieves:

| Metric | Value |
|--------|-------|
| Total transactions | 5,885 |
| With UNSPSC code | 100.0% |
| With Taxonomy L1 | 100.0% |
| With Taxonomy L3 | 96.9% |
| Custom codes mapped | 2,254 |

## Quick Start

```bash
pip install pandas openpyxl
python categorize_uch.py
```

Output: `UCH-2026Data_Categorized.xlsx`

## Project Structure

```
UCH-Categorization/
├── categorize_uch.py          # Main categorization script
├── UCH-2026Data.xlsx          # Source data (input)
├── UCH-2026Data_Categorized.xlsx  # Enriched data (output)
├── Healthcare Taxonomy v2.9.xlsx  # Reference taxonomy
├── unspsc/                    # UNSPSC reference data
│   ├── unspsc.xlsx
│   ├── UNSPSC_Comprehensive_Guide.xlsx
│   └── unspsc-cheatsheet.xls
├── CLAUDE.md                  # This file
├── README.md                  # Project documentation
└── USER_GUIDE.md              # End-user instructions
```

## Data Files

### UCH-2026Data.xlsx (Input)

| Sheet | Rows | Purpose |
|-------|------|---------|
| Supplier Listing | 250,000 | Master supplier/vendor directory |
| Services Only | 1,236 | Service transactions |
| Org Data Pull | 4,649 | Full transaction data |

**Key columns:**
- `Category Name` - Source for UNSPSC parsing (format: `XXXXXXXX-Description`)
- `Item Name`, `Item Description` - Fallback for description-based matching
- `Paid Amount`, `Purchase Order Amount` - Spend values

### UCH-2026Data_Categorized.xlsx (Output)

Same structure as input, plus these columns added to transaction sheets:

| Column | Description |
|--------|-------------|
| UNSPSC_Code | 8-digit UNSPSC code |
| UNSPSC_Category_Name | UNSPSC description |
| UNSPSC_Category_Description | UNSPSC description |
| Original_Custom_Code | Original 99xxxxxx code if mapped |
| Taxonomy_L1 | Healthcare Taxonomy Level 1 |
| Taxonomy_L2 | Healthcare Taxonomy Level 2 |
| Taxonomy_L3 | Healthcare Taxonomy Level 3 |
| Taxonomy_L4 | Healthcare Taxonomy Level 4 |
| Taxonomy_L5 | Healthcare Taxonomy Level 5 |
| Taxonomy_Key | Full path (e.g., "Facilities > Cleaning > Supplies") |

## Categorization Logic

The script uses a 3-tier matching approach:

1. **Direct UNSPSC** - Parse 8-digit code from `Category Name` column
2. **Custom Code Mapping** - Map internal 99xxxxxx codes to standard UNSPSC
3. **Description Fallback** - Keyword matching on `Item Name`/`Item Description` for uncategorized items

### Custom Code Mappings

Internal codes (99xxxxxx) are mapped to standard UNSPSC:

| Custom Code | Maps To | Description |
|-------------|---------|-------------|
| 99000033 | 72101516 | Elevator repair services |
| 99000006 | 72102103 | Asbestos removal |
| 99000040 | 76111501 | Building cleaning services |
| ... | ... | (22 total mappings) |

### Description-Based Rules

Items with `00000000` UNSPSC are categorized by keywords:

| Keywords | Taxonomy Path |
|----------|---------------|
| KNIFE, FORK, SPOON, NAPKIN | Facilities > Food & Beverage > Food Service Supplies |
| WATER SOFTENER, SOFTENER SALT | Facilities > Utilities > Water |
| BOILER, BLOWDOWN, PIPING | Facilities > Equipment & Machinery > Service & Maintenance |

## Dependencies

```bash
pip install pandas openpyxl
```

- **pandas**: DataFrame operations and Excel I/O
- **openpyxl**: .xlsx file support

## Modifying the Script

### Add New Custom Code Mapping

Edit `CUSTOM_CODE_MAPPING` in `categorize_uch.py`:

```python
CUSTOM_CODE_MAPPING = {
    '99000001': ('80101604', 'Certification or accreditation assessment'),
    # Add new mapping here
    '99000XXX': ('XXXXXXXX', 'Description'),
}
```

### Add New Taxonomy Mapping

Edit `DETAILED_TAXONOMY_MAP` for specific UNSPSC codes:

```python
DETAILED_TAXONOMY_MAP = {
    'XXXXXXXX': ('L1', 'L2', 'L3', 'L4', 'L5'),
}
```

Or edit `SEGMENT_FALLBACK` for segment-level defaults (first 2 digits).

### Add New Description Rule

Edit `DESCRIPTION_RULES`:

```python
DESCRIPTION_RULES = [
    (('KEYWORD1', 'KEYWORD2'),
     ('L1', 'L2', 'L3', None, None),
     'Inferred description'),
]
```

## Reference Data

### Healthcare Taxonomy v2.9

5-level hierarchy with 441 categories:

**Level 1**: Facilities, Finance, Human Resources, IT & Telecoms, Logistics, Marketing, Medical, Professional Services, Travel

### UNSPSC

8-digit codes (XX-XX-XX-XX):
- Digits 1-2: Segment (56 segments)
- Digits 3-4: Family (411 families)
- Digits 5-6: Class (3,713 classes)
- Digits 7-8: Commodity (46,137 commodities)
