"""Product-specific facts; empty fields never imply an unverified claim."""
import json
import math

OCCASIONS = {'everyday': 'Everyday & work', 'gatherings': 'Family & friends', 'celebrations': 'Eid & celebrations', 'weddings': 'Wedding guest'}
FABRICS = ['Lawn', 'Cotton', 'Linen', 'Khaddar', 'Silk / silk blend', 'Chiffon', 'Organza', 'Velvet', 'Nida', 'Other']
MEASUREMENTS = {'chest': 'Chest width', 'hip': 'Hip width', 'length': 'Shirt / dress length', 'sleeve': 'Sleeve length'}
TEXT_FIELDS = {'included': 600, 'not_included': 400, 'composition': 300, 'lining': 300, 'fit': 400, 'care': 600, 'fabric_lengths': 800, 'craft': 600, 'dispatch': 300}

def empty_details():
    return dict({key: '' for key in TEXT_FIELDS}, fabric_family='', occasions=[], measurements={})

def decode_details(raw):
    result = empty_details()
    if raw:
        result.update(json.loads(raw))
    return result

def form_details(form, sizes):
    result = empty_details()
    for key in TEXT_FIELDS:
        result[key] = form.get('detail_' + key, '').strip()
    result['fabric_family'] = form.get('detail_fabric_family', '')
    result['occasions'] = list(dict.fromkeys(form.getlist('detail_occasions')))
    for size in sizes:
        row = {key: form.get(f'measure_{size}_{key}', '').strip() for key in MEASUREMENTS}
        if any(row.values()): result['measurements'][size] = row
    return result

def validate_details(result, sizes):
    for key, limit in TEXT_FIELDS.items():
        if len(result[key]) > limit: raise ValueError(f'{key.replace("_", " ").title()} must be at most {limit} characters.')
    if result['fabric_family'] and result['fabric_family'] not in FABRICS:
        raise ValueError('Choose a listed fabric family.')
    if any(x not in OCCASIONS for x in result['occasions']):
        raise ValueError('Choose a listed occasion.')
    for size, row in result['measurements'].items():
        if size not in sizes or size == 'Custom Unstitched': raise ValueError('Garment measurements are for selected stitched sizes only.')
        for key, value in row.items():
            if value == '': row[key] = None; continue
            try: number = float(value)
            except (ValueError, TypeError): raise ValueError('Measurements must be numbers in inches.') from None
            if not math.isfinite(number) or not 0.01 <= number <= 150:
                raise ValueError('Measurements must be from 0.01 to 150 inches.')
            row[key] = round(number, 2)
    return result

def missing_facts(item):
    details = item['details']
    missing = []
    for key, label in [('included', 'included pieces'), ('composition', 'composition'), ('lining', 'lining / opacity'), ('care', 'care')]:
        if not details[key]: missing.append(label)
    stitched = [s for s in item['sizes'] if s != 'Custom Unstitched']
    if stitched and any(not all(details['measurements'].get(s, {}).get(k) for k in ('chest', 'length')) for s in stitched):
        missing.append('chest width & length for every stitched size')
    if 'Custom Unstitched' in item['sizes'] and not details['fabric_lengths']: missing.append('fabric lengths & widths')
    return missing
