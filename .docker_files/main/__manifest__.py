# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Main Module',
    'version': '1.0.0',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://www.numigi.com',
    'license': 'LGPL-3',
    'category': 'Other',
    'summary': 'Install all addons required for testing.',
    'depends': [
        'sale_dynamic_price',
        'sale_minimum_margin',
        'sale_order_margin_percent',
        'sale_persistent_product_warning',
        'sale_warranty',
        'sale_warranty_extension',
        'sale_warranty_lead_on_expiry',
        'sale_whole_order_invoiced',
    ],
    'installable': True,
}
