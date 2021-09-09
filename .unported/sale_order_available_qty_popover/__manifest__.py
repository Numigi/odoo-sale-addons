# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Sale Order Available Qty Popover",
    "version": "1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "LGPL-3",
    "category": "Sales",
    "summary": "Add a widget to view the available quantity of a product",
    "depends": ["sale_stock"],
    "data": ["views/assets.xml", "views/sale_order.xml"],
    "qweb": ["static/src/xml/popover.xml"],
    "installable": True,
}
