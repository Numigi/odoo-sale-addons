# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sale Rental Order Swap Variant",
    "summary": "This module adds new option on kit product to allow user to swap products with have same variant on rental sale order",
    "version": "12.0.1.0.0",
    "website": "https://bit.ly/numigi-com",
    "author": "Numigi",
    "maintainer": "Numigi",
    "license": "AGPL-3",
    "depends": ["sale_rental", "sale_kit", "sale_management"],
    "data": [
        "wizard/sale_rental_order_swap_variant.xml",
        "views/product_template.xml",
        "views/sale_order.xml",
    ],
    "installable": True,
}
