# © 2023 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Partner Sale Target",
    "version": "1.0.1",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "LGPL-3",
    "category": "Sales",
    "summary": "Sales objective per contact",
    "depends": ["contacts", "sale_management"],
    "data": [
        "security/security_groups.xml",
        "security/ir.model.access.csv",
        "views/sale_target_views.xml",
        "views/res_partner_views.xml",
        "wizard/change_parent_warning_wizard.xml",
    ],
    "installable": True,
}
