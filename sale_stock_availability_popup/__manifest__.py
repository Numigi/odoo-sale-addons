# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Sale Stock Availability Popup',
    'version': '1.0.1',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://bit.ly/numigi-com',
    'license': 'LGPL-3',
    'category': 'Sale',
    'summary': 'Modify the available quantity popover widget in sale order lines',
    'depends': [
        'sale_stock',
    ],
    'data': [
        "views/sale_order.xml"
    ],
    "qweb": [
        "static/src/xml/sale_stock.xml",
    ],
    'installable': True,
}