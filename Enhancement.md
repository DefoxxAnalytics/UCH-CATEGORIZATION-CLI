UCH Spend Categorization Plan - Enhancement
Goal
Integrate description-based rules into categorize_uch.py to handle 8 "Default Category" items that cannot be mapped by UNSPSC code alone.

Problem
Current script leaves 8 items uncategorized (UNSPSC_Code = 00000000):

3 food service items: KNIFE, FORK, NAPKIN
4 water treatment items: WATER SOFTENER SALT
1 equipment maintenance: Boiler blowdown piping repair
Solution
Add keyword-based fallback rules that examine Item Name and Item Description columns when UNSPSC code is 00000000.

Implementation
Changes to categorize_uch.py
1. Add Description Rules Dictionary (after SEGMENT_FALLBACK)

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
2. Add New Function: get_taxonomy_from_description()

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
3. Modify categorize_dataframe()
Add fallback logic when UNSPSC code is 00000000:


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
            l1, l2, l3, l4, l5, key, inferred_desc = get_taxonomy_from_description(item_name, item_desc)
            if inferred_desc:
                unspsc_desc = inferred_desc  # Update description

        results.append({...})
File to Modify
File	Action
categorize_uch.py	MODIFY - Add DESCRIPTION_RULES + fallback logic
Expected Results
Metric	Before	After
Uncategorized items	8	0
With Taxonomy L1	99.9%	100%
Item categorization:

KNIFE, FORK, NAPKIN → Facilities > Food & Beverage > Food Service Supplies
WATER SOFTENER SALT → Facilities > Utilities > Water
Boiler blowdown piping → Facilities > Equipment & Machinery > Service & Maintenance
Verification
Run: python categorize_uch.py
Check summary shows 0 uncategorized
Verify the 8 items now have Taxonomy_L1 populated
Spot-check the taxonomy paths are correct
