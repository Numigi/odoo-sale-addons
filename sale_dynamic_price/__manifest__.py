# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Sale Dynamic Price",
    'version': '1.0.0',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://bit.ly/numigi-com',
    'license': 'LGPL-3',
    "category": "Sales",
    "summary": "Compute sale prices based on product cost",
    "depends": ['sale_stock'],
    "data": [
        'views/product.xml',
        'data/sale_price_update_cron.xml',
    ],
    "installable": True,
}
