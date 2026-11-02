# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Sale Stock Availability Popover",
    "version": "18.0.1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://numigi.com",
    "license": "LGPL-3",
    "category": "Sale",
    "summary": "Modify the available quantity popover widget in sale order lines",
    "depends": [
        "sale_stock",
        "sale_management",
    ],
    "data": [
        "views/sale_order.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "sale_stock_availability_popover/static/src/js/qty_at_date_widget.js",
            "sale_stock_availability_popover/static/src/xml/qty_at_date_popover.xml",
        ],
    },
    "installable": True,
}
