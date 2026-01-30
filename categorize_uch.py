"""
UCH Spend Categorization Script

Populates UNSPSC columns from Category Name and maps to Healthcare Taxonomy v2.9.
Extended to support all 5 taxonomy levels.
"""

import pandas as pd
import re
from pathlib import Path

CUSTOM_CODE_MAPPING = {
    '99000001': ('80101604', 'Certification or accreditation assessment'),
    '99000006': ('72102103', 'Asbestos removal or encapsulation'),
    '99000030': ('80161504', 'Document destruction services'),
    '99000033': ('72101516', 'Elevator repair services'),
    '99000038': ('72101500', 'Building maintenance and repair services'),
    '99000039': ('73110000', 'Machinery and equipment rental'),
    '99000040': ('76111501', 'Building cleaning services'),
    '99000042': ('81101500', 'Building and facility consultants'),
    '99000051': ('70111706', 'Lawn care services'),
    '99000059': ('72102900', 'Facility maintenance and repair services'),
    '99000060': ('72151900', 'Equipment installation services'),
    '99000063': ('80141600', 'Graphic design'),
    '99000080': ('78111800', 'Relocation services'),
    '99000089': ('78181500', 'Parking facilities'),
    '99000098': ('80131500', 'Real estate services'),
    '99000107': ('80101507', 'Risk or hazard assessment'),
    '99000108': ('92121700', 'Guard services'),
    '99000116': ('78100000', 'Mail and cargo transport'),
    '99000121': ('76121500', 'Refuse collection and disposal'),
    '99000131': ('80101500', 'Business consulting services'),
    '99000154': ('80101500', 'Business consulting services'),
    '99000167': ('78181500', 'Vehicle leasing'),
    '99999999': ('00000000', 'Uncategorized'),
}

DETAILED_TAXONOMY_MAP = {
    # Elevator services
    '72101516': ('Facilities', 'Facilities Services', 'Building Maintenance', 'Elevator Maintenance', None),
    # Asbestos
    '72102103': ('Facilities', 'Facilities Services', 'Building Maintenance', 'Environmental Services', 'Asbestos Abatement'),
    # Building maintenance general
    '72101500': ('Facilities', 'Facilities Services', 'Building Maintenance', None, None),
    '72102900': ('Facilities', 'Facilities Services', 'Building Maintenance', None, None),
    # Lawn/grounds
    '70111706': ('Facilities', 'Facilities Services', 'Building Maintenance', 'Landscaping Services', None),
    '72102902': ('Facilities', 'Facilities Services', 'Building Maintenance', 'Landscaping Services', None),
    '72102905': ('Facilities', 'Facilities Services', 'Building Maintenance', 'Grounds Maintenance', None),
    # HVAC
    '40101500': ('Facilities', 'Facilities Services', 'Building Maintenance', 'HVAC Installation & Maintenance', None),
    '40101700': ('Facilities', 'Facilities Services', 'Building Maintenance', 'HVAC Installation & Maintenance', None),
    # Electrical/Power
    '26130000': ('Facilities', 'Facilities Services', 'Building Maintenance', 'Electrical Services', 'Generators'),
    '26110000': ('Facilities', 'Facilities Services', 'Building Maintenance', 'Electrical Services', None),
    '26111702': ('Facilities', 'Facilities Services', 'Building Maintenance', 'Electrical Services', 'Supplies'),
    '26120000': ('Facilities', 'Facilities Services', 'Building Maintenance', 'Electrical Services', 'Supplies'),
    # Plumbing
    '40140000': ('Facilities', 'Facilities Services', 'Building Maintenance', 'Plumbing Maintenance', None),
    '30180000': ('Facilities', 'Facilities Services', 'Building Maintenance', 'Plumbing Maintenance', 'Supplies'),
    # Flooring
    '30160000': ('Facilities', 'Facilities Services', 'Building Maintenance', 'Flooring Services', 'Supplies'),
    '47131802': ('Facilities', 'Facilities Services', 'Building Maintenance', 'Flooring Services', 'Supplies'),
    # Painting
    '31210000': ('Facilities', 'Facilities Services', 'Building Maintenance', 'Painting Services', 'Supplies'),
    # Roofing
    '30140000': ('Facilities', 'Facilities Services', 'Building Maintenance', 'Roof Maintenance', 'Supplies'),
    # Lighting/Lamps
    '39100000': ('Facilities', 'Facilities Services', 'Building Maintenance', 'Electrical Services', 'Supplies'),
    '39101612': ('Facilities', 'Facilities Services', 'Building Maintenance', 'Electrical Services', 'Supplies'),
    '39110000': ('Facilities', 'Facilities Services', 'Building Maintenance', 'Electrical Services', 'Supplies'),
    '39112102': ('Facilities', 'Facilities Services', 'Building Maintenance', 'Electrical Services', 'Supplies'),
    '39120000': ('Facilities', 'Facilities Services', 'Building Maintenance', 'Electrical Services', 'Supplies'),
    '55121703': ('Facilities', 'Facilities Services', 'Building Maintenance', 'Electrical Services', 'Supplies'),
    # Hardware
    '31160000': ('Facilities', 'Facilities Services', 'Building Maintenance', 'Building Systems Maintenance', 'Supplies'),
    '31150000': ('Facilities', 'Facilities Services', 'Building Maintenance', 'Building Systems Maintenance', 'Supplies'),
    '31170000': ('Facilities', 'Facilities Services', 'Building Maintenance', 'Building Systems Maintenance', 'Supplies'),
    '31180000': ('Facilities', 'Facilities Services', 'Building Maintenance', 'Building Systems Maintenance', 'Supplies'),
    '31200000': ('Facilities', 'Facilities Services', 'Building Maintenance', 'Building Systems Maintenance', 'Supplies'),
    # Tools
    '27110000': ('Facilities', 'Equipment & Machinery', 'Equipment', None, None),
    # Door/lock services
    '46171503': ('Facilities', 'Facilities Services', 'Building Maintenance', 'Door Installation & Maintenance', 'Supplies'),
    '46171505': ('Facilities', 'Facilities Services', 'Building Maintenance', 'Door Installation & Maintenance', 'Supplies'),
    # Security
    '46160000': ('Facilities', 'Facilities Services', 'Security', 'Security Equipment', None),
    '46170000': ('Facilities', 'Facilities Services', 'Security', 'Security Equipment', None),
    '92121700': ('Facilities', 'Facilities Services', 'Security', 'Security Services', 'Security Guards'),
    # Safety/PPE
    '46180000': ('Facilities', 'Facilities Services', 'Safety', 'PPE', None),
    '46181504': ('Facilities', 'Facilities Services', 'Safety', 'PPE', 'Gloves'),
    '46182402': ('Facilities', 'Facilities Services', 'Safety', 'PPE', None),
    # Fire
    '46190000': ('Facilities', 'Facilities Services', 'Fire', 'Fire Safety Systems', None),
    '46191503': ('Facilities', 'Facilities Services', 'Fire', 'Fire Equipment', None),
    '46191505': ('Facilities', 'Facilities Services', 'Fire', 'Fire Safety Systems', None),
    # Cleaning/Janitorial
    '47100000': ('Facilities', 'Cleaning', 'Cleaning Services', None, None),
    '47120000': ('Facilities', 'Cleaning', 'Cleaning Equipment', None, None),
    '47121701': ('Facilities', 'Cleaning', 'Cleaning Supplies', None, None),
    '47121702': ('Facilities', 'Cleaning', 'Cleaning Equipment', None, None),
    '47130000': ('Facilities', 'Cleaning', 'Cleaning Supplies', None, None),
    '47131601': ('Facilities', 'Cleaning', 'Cleaning Equipment', None, None),
    '47131604': ('Facilities', 'Cleaning', 'Cleaning Equipment', None, None),
    '47131609': ('Facilities', 'Cleaning', 'Cleaning Equipment', None, None),
    '47131805': ('Facilities', 'Cleaning', 'Cleaning Supplies', None, None),
    '76111501': ('Facilities', 'Cleaning', 'Cleaning Services', 'Janitorial Services', None),
    '76121500': ('Facilities', 'Waste Management', 'Waste Disposal', None, None),
    # Document management
    '80161504': ('Facilities', 'Facilities Services', 'Document Management', 'Document Destruction', None),
    # Moving/storage
    '78111800': ('Facilities', 'Facilities Services', 'Moving and Storage Services', 'Moving Services', None),
    # Construction
    '30121601': ('Facilities', 'Construction Services', 'Contractors', None, None),
    '30190000': ('Facilities', 'Construction Services', 'Contractors', None, None),
    # Medical equipment
    '42132105': ('Medical', 'Medical Equipment', 'Medical Facility Equipment', 'Linens', None),
    '42141603': ('Medical', 'Medical Consumables', 'Medical Supplies', None, None),
    '42170000': ('Medical', 'Medical Equipment', 'Emergency & Field Medical Equipment', None, None),
    '42172001': ('Medical', 'Medical Equipment', 'Emergency & Field Medical Equipment', None, None),
    '42191815': ('Medical', 'Medical Equipment', 'Medical Facility Equipment', None, None),
    '42271701': ('Medical', 'Medical Consumables', 'Medical Gas', None, None),
    # Laboratory
    '41110000': ('Medical', 'Laboratory', 'Laboratory Equipment', None, None),
    '60104202': ('Medical', 'Laboratory', 'Laboratory Supplies', None, None),
    # Pharmaceuticals
    '51100000': ('Medical', 'Pharmaceuticals', None, None, None),
    # IT/Computer
    '43210000': ('IT & Telecoms', 'IT Hardware', None, None, None),
    '43211500': ('IT & Telecoms', 'IT Hardware', 'Computers', None, None),
    # Office supplies
    '44110000': ('Facilities', 'Office Equipment & Supplies', 'Office Supplies', None, None),
    '44120000': ('Facilities', 'Office Equipment & Supplies', 'Office Supplies', None, None),
    # Uniforms/apparel
    '53102710': ('Facilities', 'Uniform', None, None, None),
    '53130000': ('Facilities', 'Uniform', None, None, None),
    # Furniture
    '56100000': ('Facilities', 'Furniture', None, None, None),
    '56101532': ('Facilities', 'Furniture', None, None, None),
    # Food & beverage
    '48100000': ('Facilities', 'Food & Beverage', 'Food & Beverage Equipment', None, None),
    '48101905': ('Facilities', 'Food & Beverage', 'Food & Beverage Equipment', None, None),
    '50200000': ('Facilities', 'Food & Beverage', None, None, None),
    # Signage
    '55120000': ('Facilities', 'Facilities Services', 'Building Maintenance', None, None),
    '55121718': ('Facilities', 'Facilities Services', 'Building Maintenance', None, None),
    # Material handling
    '24100000': ('Facilities', 'Facilities Services', 'Material Handling', 'Material Handling Equipment', None),
    '24110000': ('Facilities', 'Facilities Services', 'Material Handling', 'Material Handling Equipment', None),
    '24120000': ('Logistics', 'Freight & Distribution', 'Packaging', None, None),
    '24140000': ('Logistics', 'Freight & Distribution', 'Packaging', None, None),
    '24141506': ('Logistics', 'Freight & Distribution', 'Packaging', None, None),
    # Transportation/vehicles
    '25170000': ('Facilities', 'Vehicles', None, None, None),
    '78100000': ('Logistics', 'Transportation', None, None, None),
    '78181500': ('Logistics', 'Transportation', None, None, None),
    # Consulting/professional services
    '80101500': ('Professional Services', 'Consulting', 'General Consulting Services', None, None),
    '80101507': ('Professional Services', 'Consulting', 'General Consulting Services', None, None),
    '80101604': ('Professional Services', 'Consulting', 'General Consulting Services', None, None),
    '80131500': ('Professional Services', 'Consulting', 'General Consulting Services', None, None),
    '80141600': ('Professional Services', 'Consulting', 'Design and Architectural Services', None, None),
    '81101500': ('Professional Services', 'Engineering Services', None, None, None),
    # Equipment rental/machinery
    '73110000': ('Facilities', 'Equipment & Machinery', 'Equipment', None, None),
    '72151900': ('Facilities', 'Equipment & Machinery', 'Service & Maintenance', None, None),
    # Fuels/utilities
    '15100000': ('Facilities', 'Utilities', 'Energy', None, None),
    '15120000': ('Facilities', 'Utilities', 'Energy', None, None),
    # Industrial equipment
    '20110000': ('Facilities', 'Equipment & Machinery', 'Equipment', None, None),
    '21101801': ('Facilities', 'Equipment & Machinery', 'Equipment', None, None),
    '23150000': ('Facilities', 'Equipment & Machinery', 'Equipment', None, None),
    '23170000': ('Facilities', 'Equipment & Machinery', 'Equipment', None, None),
    '23181803': ('Facilities', 'Equipment & Machinery', 'Equipment', None, None),
    '23200000': ('Facilities', 'Equipment & Machinery', 'Equipment', None, None),
    '40100000': ('Facilities', 'Facilities Services', 'Building Maintenance', 'HVAC Installation & Maintenance', None),
    '40150000': ('Facilities', 'Equipment & Machinery', 'Equipment', None, None),
    '40160000': ('Facilities', 'Equipment & Machinery', 'Equipment', None, None),
    # Materials
    '11160000': ('Facilities', 'Operating Supplies and Equipment', None, None, None),
    '12141904': ('Medical', 'Medical Consumables', 'Medical Gas', None, None),
    '12180000': ('Facilities', 'Operating Supplies and Equipment', None, None, None),
    '13110000': ('Facilities', 'Operating Supplies and Equipment', None, None, None),
    '14111701': ('Facilities', 'Office Equipment & Supplies', 'Office Supplies', None, None),
    '31240000': ('Facilities', 'Equipment & Machinery', 'Equipment', None, None),
    '31370000': ('Facilities', 'Operating Supplies and Equipment', None, None, None),
    # Electronics
    '52140000': ('Facilities', 'Technology Systems', None, None, None),
    '52160000': ('Facilities', 'Technology Systems', None, None, None),
    '52161505': ('Facilities', 'Technology Systems', None, None, None),
    '52161511': ('Facilities', 'Technology Systems', None, None, None),
    # Training/education
    '60106108': ('Human Resources', 'Training', None, None, None),
    '60130000': ('Human Resources', 'Training', None, None, None),
}

SEGMENT_FALLBACK = {
    '10': ('Facilities', 'Operating Supplies and Equipment', None, None, None),
    '11': ('Facilities', 'Operating Supplies and Equipment', None, None, None),
    '12': ('Medical', 'Medical Consumables', None, None, None),
    '13': ('Facilities', 'Operating Supplies and Equipment', None, None, None),
    '14': ('Facilities', 'Office Equipment & Supplies', None, None, None),
    '15': ('Facilities', 'Utilities', None, None, None),
    '20': ('Facilities', 'Equipment & Machinery', None, None, None),
    '21': ('Facilities', 'Equipment & Machinery', None, None, None),
    '22': ('Facilities', 'Equipment & Machinery', None, None, None),
    '23': ('Facilities', 'Equipment & Machinery', None, None, None),
    '24': ('Logistics', 'Freight & Distribution', None, None, None),
    '25': ('Facilities', 'Vehicles', None, None, None),
    '26': ('Facilities', 'Utilities', None, None, None),
    '27': ('Facilities', 'Equipment & Machinery', None, None, None),
    '30': ('Facilities', 'Construction Services', None, None, None),
    '31': ('Facilities', 'Facilities Services', 'Building Maintenance', None, None),
    '39': ('Facilities', 'Facilities Services', 'Building Maintenance', 'Electrical Services', None),
    '40': ('Facilities', 'Facilities Services', 'Building Maintenance', None, None),
    '41': ('Medical', 'Laboratory', None, None, None),
    '42': ('Medical', 'Medical Equipment', None, None, None),
    '43': ('IT & Telecoms', 'IT Hardware', None, None, None),
    '44': ('Facilities', 'Office Equipment & Supplies', None, None, None),
    '46': ('Facilities', 'Facilities Services', 'Safety', None, None),
    '47': ('Facilities', 'Cleaning', None, None, None),
    '48': ('Facilities', 'Food & Beverage', None, None, None),
    '50': ('Facilities', 'Food & Beverage', None, None, None),
    '51': ('Medical', 'Pharmaceuticals', None, None, None),
    '52': ('Facilities', 'Technology Systems', None, None, None),
    '53': ('Facilities', 'Uniform', None, None, None),
    '55': ('Facilities', 'Facilities Services', None, None, None),
    '56': ('Facilities', 'Furniture', None, None, None),
    '60': ('Human Resources', 'Training', None, None, None),
    '70': ('Facilities', 'Facilities Services', 'Building Maintenance', 'Landscaping Services', None),
    '72': ('Facilities', 'Facilities Services', 'Building Maintenance', None, None),
    '73': ('Facilities', 'Equipment & Machinery', None, None, None),
    '76': ('Facilities', 'Cleaning', None, None, None),
    '77': ('Facilities', 'Waste Management', None, None, None),
    '78': ('Logistics', 'Transportation', None, None, None),
    '80': ('Professional Services', 'Consulting', None, None, None),
    '81': ('Professional Services', 'Engineering Services', None, None, None),
    '92': ('Facilities', 'Facilities Services', 'Security', None, None),
    '99': ('Professional Services', 'Consulting', None, None, None),
}

DESCRIPTION_RULES = [
    # (keywords_tuple, taxonomy_tuple, inferred_description)
    # Food Service Items
    (('KNIFE', 'FORK', 'SPOON', 'NAPKIN', 'CUTLERY'),
     ('Facilities', 'Food & Beverage', 'Food Service Supplies', None, None),
     'Food service supplies'),

    # Water Treatment
    (('WATER SOFTENER', 'SOFTENER SALT'),
     ('Facilities', 'Utilities', 'Water', None, None),
     'Water treatment supplies'),

    # Equipment Maintenance (boilers, piping)
    (('BOILER', 'BLOWDOWN', 'PIPING'),
     ('Facilities', 'Equipment & Machinery', 'Service & Maintenance', None, None),
     'Equipment maintenance services'),
]


def parse_category_name(cat_name):
    if pd.isna(cat_name):
        return None, None
    match = re.match(r'^(\d{8})-(.+)$', str(cat_name))
    if match:
        return match.group(1), match.group(2)
    return None, None


def get_unspsc_info(code, description):
    if code is None:
        return None, None, None
    if code.startswith('99'):
        mapped = CUSTOM_CODE_MAPPING.get(code)
        if mapped:
            return mapped[0], mapped[1], code
        return None, None, code
    return code, description, None


def get_taxonomy(unspsc_code):
    if unspsc_code is None or str(unspsc_code) == '00000000':
        return None, None, None, None, None, None

    code_str = str(unspsc_code).zfill(8)

    if code_str in DETAILED_TAXONOMY_MAP:
        levels = DETAILED_TAXONOMY_MAP[code_str]
    else:
        segment = code_str[:2]
        levels = SEGMENT_FALLBACK.get(segment, (None, None, None, None, None))

    l1, l2, l3, l4, l5 = levels
    parts = [p for p in [l1, l2, l3, l4, l5] if p is not None]
    key = ' > '.join(parts) if parts else None

    return l1, l2, l3, l4, l5, key


def get_taxonomy_from_description(item_name, item_desc):
    """Fallback: infer taxonomy from Item Name/Description when UNSPSC is missing."""
    search_text = f"{item_name or ''} {item_desc or ''}".upper()

    for keywords, taxonomy, desc in DESCRIPTION_RULES:
        if any(kw in search_text for kw in keywords):
            l1, l2, l3, l4, l5 = taxonomy
            parts = [p for p in taxonomy if p is not None]
            key = ' > '.join(parts) if parts else None
            return l1, l2, l3, l4, l5, key, desc

    return None, None, None, None, None, None, None


def categorize_dataframe(df):
    results = []
    for _, row in df.iterrows():
        cat_name = row.get('Category Name')
        code, desc = parse_category_name(cat_name)
        unspsc_code, unspsc_desc, original_custom = get_unspsc_info(code, desc)
        l1, l2, l3, l4, l5, key = get_taxonomy(unspsc_code)

        # FALLBACK: If uncategorized, try description-based rules
        if unspsc_code == '00000000' or l1 is None:
            item_name = row.get('Item Name', '')
            item_desc = row.get('Item Description', '')
            fb_l1, fb_l2, fb_l3, fb_l4, fb_l5, fb_key, inferred_desc = get_taxonomy_from_description(item_name, item_desc)
            if fb_l1 is not None:
                l1, l2, l3, l4, l5, key = fb_l1, fb_l2, fb_l3, fb_l4, fb_l5, fb_key
                unspsc_desc = inferred_desc

        results.append({
            'UNSPSC_Code': unspsc_code,
            'UNSPSC_Category_Name': unspsc_desc,
            'UNSPSC_Category_Description': unspsc_desc,
            'Original_Custom_Code': original_custom,
            'Taxonomy_L1': l1,
            'Taxonomy_L2': l2,
            'Taxonomy_L3': l3,
            'Taxonomy_L4': l4,
            'Taxonomy_L5': l5,
            'Taxonomy_Key': key,
        })

    result_df = pd.DataFrame(results)
    return pd.concat([df.reset_index(drop=True), result_df], axis=1)


def main():
    base_path = Path(__file__).parent

    print("Loading UCH data...")
    uch_data = pd.ExcelFile(base_path / 'UCH-2026Data.xlsx')
    services = pd.read_excel(uch_data, sheet_name='Services Only')
    org = pd.read_excel(uch_data, sheet_name='Org Data Pull')
    suppliers = pd.read_excel(uch_data, sheet_name='Supplier Listing')

    print(f"Processing Services Only ({len(services)} rows)...")
    services_cat = categorize_dataframe(services)

    print(f"Processing Org Data Pull ({len(org)} rows)...")
    org_cat = categorize_dataframe(org)

    output_path = base_path / 'UCH-2026Data_Categorized.xlsx'
    print(f"Writing output to {output_path}...")

    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        suppliers.to_excel(writer, sheet_name='Supplier Listing', index=False)
        services_cat.to_excel(writer, sheet_name='Services Only', index=False)
        org_cat.to_excel(writer, sheet_name='Org Data Pull', index=False)

    print("\n=== Summary ===")
    all_cat = pd.concat([services_cat, org_cat])

    total = len(all_cat)
    with_unspsc = all_cat['UNSPSC_Code'].notna().sum()
    with_l1 = all_cat['Taxonomy_L1'].notna().sum()
    with_l3 = all_cat['Taxonomy_L3'].notna().sum()
    with_l4 = all_cat['Taxonomy_L4'].notna().sum()
    with_l5 = all_cat['Taxonomy_L5'].notna().sum()
    custom_mapped = all_cat['Original_Custom_Code'].notna().sum()

    print(f"Total transactions: {total}")
    print(f"With UNSPSC code: {with_unspsc} ({with_unspsc/total*100:.1f}%)")
    print(f"With Taxonomy L1: {with_l1} ({with_l1/total*100:.1f}%)")
    print(f"With Taxonomy L3: {with_l3} ({with_l3/total*100:.1f}%)")
    print(f"With Taxonomy L4: {with_l4} ({with_l4/total*100:.1f}%)")
    print(f"With Taxonomy L5: {with_l5} ({with_l5/total*100:.1f}%)")
    print(f"Custom codes mapped: {custom_mapped}")

    print("\n=== Top 10 Taxonomy Keys by Transaction Count ===")
    key_counts = all_cat['Taxonomy_Key'].value_counts().head(10)
    for key, count in key_counts.items():
        print(f"  {key}: {count}")

    print(f"\nDone! Output saved to: {output_path}")


if __name__ == '__main__':
    main()
