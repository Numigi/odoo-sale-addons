# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Website Stock Availability Enhanced",
    "summary": "Enhance the display of product availability on the website",
    "version": "14.0.1.0.2",
    "website": "https://numigi.com/r/home",
    "author": "Numigi",
    "maintainer": "Numigi",
    "license": "LGPL-3",
    "depends": [
        "queue_job",
        "purchase",
        "website_sale_stock",
    ],
    "data": [
        "data/ir_cron.xml",
        "data/queue_job_function.xml",
        "views/assets.xml",
        "views/product_template.xml",
        "views/sale_order.xml",
    ],
    "installable": True,
}
