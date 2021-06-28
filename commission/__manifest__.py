# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Commission",
    "version": "1.0.0",
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
    ],
    "data": ["views/commission.xml", "views/target.xml", "views/category.xml"],
    "installable": True,
}
