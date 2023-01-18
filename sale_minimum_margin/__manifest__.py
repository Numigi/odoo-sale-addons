# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Sale Minimum Margin",
    'version': '14.0.1.0.0',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://bit.ly/numigi-com',
    'license': 'LGPL-3',
    "category": "Sales",
    "summary": "Set a minimum sale price margin on product categories",
    "depends": ['sale_dynamic_price'],
    "data": [
        'views/product.xml',
        'views/product_category.xml',
    ],
    "installable": True,
}
