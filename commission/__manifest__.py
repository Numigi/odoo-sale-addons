# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Commission",
    "version": "1.1.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "LGPL-3",
    "category": "Sales",
    "summary": "Adds commission functionality to sales.",
    "depends": [
        "account",
        "hr",
        "date_range",
        "base_extended_security",
        "sale_order_tag",
        "sale_stock",
        "sales_team",
    ],
    "data": [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "security/extended_security_rule.xml",
        "views/account_invoice_line.xml",
        "views/commission_target.xml",
        "views/commission_category.xml",
        "views/menus.xml",
        "data/ir_sequence.xml",
    ],
    "installable": True,
}
