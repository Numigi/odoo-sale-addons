# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Commission Payroll Preparation",
    "version": "1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "LGPL-3",
    "category": "Sales",
    "summary": "",
    "depends": ["base", "commission", "payroll_preparation", "date_range"],
    "data": [
        "wizard/commission_payroll_preparation_wizard.xml",
        "views/commission_target.xml",
        "views/payroll_preparation_line.xml",
    ],
    "installable": True,
}
