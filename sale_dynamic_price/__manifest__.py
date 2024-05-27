# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Sale Dynamic Price",
    "version": "14.0.1.0.1",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "LGPL-3",
    "category": "Sales",
    "summary": "Compute sale prices based on product cost",
    "depends": ["base_view_inheritance_extension", "product", "queue_job_cron"],
    "data": [
        "views/product_template.xml",
        "views/product_product.xml",
        "views/product_template_attribute_value.xml",
        "data/ir_cron.xml",
    ],
    "installable": True,
}
