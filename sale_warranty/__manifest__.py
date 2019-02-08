# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Sales Warranty",
    'version': '1.0.0',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://bit.ly/numigi-com',
    'license': 'LGPL-3',
    "category": "Sales",
    "summary": "Manage warranties on sales",
    "depends": ['sale_stock'],
    "data": [
        'security/groups.xml',
        'security/rules.xml',
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/warranty_type.xml',
        'views/warranty.xml',
        'views/product.xml',
        'views/sale_order.xml',
        'data/ir_sequence.xml',
    ],
    "installable": True,
}
