# © 2025 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Sale Purchase Procurement Link",
    "version": "14.0.1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "LGPL-3",
    "category": "Hidden",
    "summary": "Add sale order info in purchase order line from procurement",
    "depends": [
        "sale_purchase_stock",
        "purchase_line_procurement_no_grouping",
    ],
    "data": [
        "views/purchase_order_views.xml",
    ],
    "installable": True,
}
