# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Sale Rental",
    "version": "14.0.2.0.1",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://numigi.com/r/home",
    "license": "LGPL-3",
    "category": "Sales",
    "summary": "Allow to rent equipments",
    "depends": ["sale_kit", "sale_stock", "stock_rental"],
    "data": [
        "data/ir_cron.xml",
        "views/sale_order.xml",
        "views/product_template.xml",
        "views/menu.xml",
        "views/res_config_settings.xml",
        "report/sale_report_views.xml",
    ],
    "installable": True,
}
