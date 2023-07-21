# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Display Quantity Widget Secondary Unit",
    "version": "1.0.1",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "AGPL-3",
    "category": "Sale",
    "depends": ["sale_stock", "stock_secondary_unit"],
    "summary": "Add the possibility to access the secondary unit on Sale Quantity Widget",
    "data": [
        'views/sale_order_views.xml',
    ],
    'qweb': ['static/src/xml/sale_stock.xml'],
    "installable": True,
}
