# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Sale Stock Availablity Popup',
    'version': '1.0.0',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://bit.ly/numigi-com',
    'license': 'LGPL-3',
    'category': 'Hr',
    'summary': 'Modify the available quantity popover widget in sale order lines',
    'depends': [
        'sale_stock',
    ],
    'data': [
    ],
    "qweb": [
        "static/src/xml/sale_stock.xml",
    ],
    'installable': True,
}
