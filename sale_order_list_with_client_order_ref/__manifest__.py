# Copyright 2025 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Order Lists with Client Order Reference",
    "version": "14.0.1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "AGPL-3",
    "category": "sale",
    "depends": ["sale_management"],
    "summary": """
        Add `Customer Reference` in some sale order lists views.
    """,
    "data": [
        "views/sale_order_views.xml",
    ],
    "installable": True,
}
