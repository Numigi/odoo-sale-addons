# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Sale Privilege Level",
    "version": "1.2.3",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "LGPL-3",
    "category": "Sales",
    "summary": "Add privilege levels on partners",
    "depends": ["contacts", "sale"],
    "data": [
        "views/res_partner.xml",
        "views/sale_privilege_level.xml",
        "views/res_config_settings.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
