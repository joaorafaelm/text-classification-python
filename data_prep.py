# -*- coding: utf8 -*-

import io
import json
from collections import Counter


def depth(field, n, sep=' > '):
    """Split category depth helper"""
    if n <= 0:
        return field
    return sep.join(field.split(sep, n)[: n])

# Category depth
default_depth = 0

# Min n of samples per category
min_samples = 50

"""
Top Level Categories Filter.
Available categories:
    # A
    'Appliances', 'Arts, Crafts & Sewing', 'Automotive',

    # B
    'Baby Products', 'Beauty & Personal Care', 'Books',

    # C
    'CDs & Vinyl', 'Car & Vehicle Electronics', 'Cell Phones & Accessories',
    'Clothing, Shoes & Jewelry', 'Collectibles & Fine Art',

    # E
    'Electronics',

    # G
    'Grocery & Gourmet Food',

    # H
    'Health & Household', 'Hobbies', 'Home & Kitchen', 'Hunting & Fishing',
    'Hydraulics, Pneumatics & Plumbing',

    # I
    'Industrial & Scientific',

    # K
    'Kindle Store', 'Kitchen & Dining',

    # L
    'Lights & Lighting Accessories',

    # M
    'Magazine Subscriptions', 'Medical Supplies & Equipment',
    'Mobility & Daily Living Aids', 'Motorcycle & Powersports',
    'Movies & TV', 'Musical Instruments',

    # O
    'Office Electronics', 'Office Products',

    # P
    'Patio, Lawn & Garden', 'Pet Supplies', 'Power & Hand Tools',
    'Power Tool Parts & Accessories',

    # R
    'Remote & App Controlled Vehicle Parts',
    'Remote & App Controlled Vehicles & Parts',

    # S
    'Small Appliance Parts & Accessories', 'Software', 'Sports & Outdoors',

    # T
    'Tools & Home Improvement', 'Toys & Games',

    # V
    'Video Games'
"""
domain = ['Home & Kitchen', 'Industrial & Scientific', 'Automotive']

content = json.load(open('dumps/all_products.json'), encoding='utf8')

# Counter n of samples/category
categories = Counter(
    depth(x['category'], default_depth)
    for x in content.get('results') if x['category']
)

# Filter categories that have above x samples
categories_filter = {}
for x in categories:
    if any([x.startswith(j) for j in domain]) or not domain:
        if categories[x] > min_samples:
            categories_filter[x] = categories[x]


products = {
    'target_names': list(categories_filter),
    'target': [],
    'data': []
}

for product in content.get('results'):
    if product.get('category') and any([
        product.get('description'),
        product.get('features'),
        product.get('name')
    ]):
        if depth(
                product.get('category'), default_depth
        ) in products.get('target_names'):

            if categories.get(depth(product.get('category'), default_depth)):

                products['target'].append(
                    products.get('target_names').index(
                        depth(product.get('category'), default_depth)
                    )
                )

                products['data'].append(
                    u'{}. {}. {}'.format(
                        product.get('description') or '',
                        product.get('features') or '',
                        product.get('name') or ''
                    )
                )

with io.open('products.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(products, ensure_ascii=False))


# Build tree for printing.
categories_dict = {}

for cat in sorted(categories_filter):
    # noinspection PyRedeclaration
    parent = categories_dict

    for i in cat.split(' > '):
        parent = parent.setdefault(i, {})


def pretty(d, indent=0):
    for key, value in d.items():
        print(u'{} {} ({})'.format('    ' * indent, key, len(value)))
        pretty(value, indent + 1)

pretty(categories_dict)
