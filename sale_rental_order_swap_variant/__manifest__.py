# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sale Rental Order Swap Variant",
    "summary": "Allow to change an important product from a kit",
    "version": "14.0.1.0.1",
    "website": "https://bit.ly/numigi-com",
    "author": "Numigi",
    "maintainer": "Numigi",
    "license": "AGPL-3",
    "depends": ["sale_rental"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/sale_rental_order_swap_variant.xml",
        "views/product_template.xml",
        "views/sale_order.xml",
    ],
    "installable": True,
}
