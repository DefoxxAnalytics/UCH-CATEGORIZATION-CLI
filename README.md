# UCH Spend Categorization

Automated categorization of UCH (University of Cincinnati Health) procurement data using UNSPSC codes and Healthcare Taxonomy v2.9.

## Overview

This tool processes UCH spend data and enriches it with:
- **UNSPSC codes** (United Nations Standard Products and Services Code)
- **Healthcare Taxonomy** (5-level hierarchy for spend analytics)

## Results

| Metric | Value |
|--------|-------|
| Total transactions | 5,885 |
| UNSPSC coverage | 100% |
| Taxonomy L1 coverage | 100% |
| Taxonomy L3 coverage | 96.9% |

## Quick Start

```bash
# Install dependencies
pip install pandas openpyxl

# Run categorization
python categorize_uch.py

# With analytics report
python categorize_uch.py --analytics

# Custom input/output
python categorize_uch.py --input data.xlsx --output results.xlsx
```

**Input**: `UCH-2026Data.xlsx` (default)
**Output**: `UCH-2026Data_Categorized.xlsx` (default)

## CLI Options

| Option | Short | Description |
|--------|-------|-------------|
| `--input` | `-i` | Input Excel file |
| `--output` | `-o` | Output Excel file |
| `--analytics` | `-a` | Generate spend analytics report |
| `--quiet` | `-q` | Suppress progress output |

## How It Works

The script uses a 3-tier matching approach:

1. **Direct UNSPSC** - Parses 8-digit codes from the `Category Name` column
2. **Custom Code Mapping** - Maps internal 99xxxxxx codes to standard UNSPSC
3. **Description Fallback** - Keyword matching for items without valid UNSPSC codes

## Output Columns

The categorized output adds these columns to transaction sheets:

| Column | Example |
|--------|---------|
| UNSPSC_Code | 72101516 |
| UNSPSC_Category_Name | Elevator repair services |
| Taxonomy_L1 | Facilities |
| Taxonomy_L2 | Facilities Services |
| Taxonomy_L3 | Building Maintenance |
| Taxonomy_L4 | Elevator Maintenance |
| Taxonomy_Key | Facilities > Facilities Services > Building Maintenance > Elevator Maintenance |
| Match_Method | DIRECT |

## Match Methods (Audit Trail)

Each row includes a `Match_Method` column for transparency:

| Method | Description |
|--------|-------------|
| `DIRECT` | UNSPSC code found in detailed taxonomy map |
| `CUSTOM_MAP` | Internal 99xxxxxx code mapped to standard UNSPSC |
| `SEGMENT_FALLBACK` | Used segment-level (first 2 digits) fallback |
| `DESCRIPTION_FALLBACK` | Matched via keyword rules on item description |
| `UNMATCHED` | No taxonomy assigned |

## Top Categories

| Taxonomy Path | Transactions |
|---------------|--------------|
| Facilities > Facilities Services > Building Maintenance | 1,993 |
| Facilities > Facilities Services > Building Maintenance > Electrical Services > Supplies | 1,863 |
| Facilities > Facilities Services > Safety > PPE | 507 |
| Facilities > Facilities Services > Building Maintenance > Building Systems Maintenance > Supplies | 419 |

## Project Structure

```
UCH-Categorization/
├── categorize_uch.py              # Main script
├── UCH-2026Data.xlsx              # Input data
├── UCH-2026Data_Categorized.xlsx  # Output data
├── Healthcare Taxonomy v2.9.xlsx  # Reference taxonomy
├── unspsc/                        # UNSPSC reference files
├── README.md                      # This file
├── USER_GUIDE.md                  # Detailed user instructions
└── CLAUDE.md                      # Developer reference
```

## Requirements

- Python 3.7+
- pandas
- openpyxl

## Documentation

- [USER_GUIDE.md](USER_GUIDE.md) - Step-by-step instructions for end users
- [CLAUDE.md](CLAUDE.md) - Technical reference for developers

## License

Proprietary - VTX Solutions / Defoxx Analytics
