# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Sale Rental",
    "version": "1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "LGPL-3",
    "category": "Sales",
    "summary": "Allow to rent equipments",
    "depends": ["sale_kit", "sale_stock"],
    "data": [
        "data/ir_cron.xml",
        "data/stock_location.xml",
        "views/sale_order.xml",
        "views/product_template.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
}
