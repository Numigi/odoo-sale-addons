# Copyright 2024 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sales Team Account Journal",
    "version": "1.0.1",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "AGPL-3",
    "category": "Sale",
    "depends": [
        "account",
        "sale",
        "sales_team",
    ],
    "summary": "Add a default sales journal on a sales team for invoices",
    "data": [
        "views/crm_team_views.xml",
    ],
    "installable": True,
}
