# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Sale Privilege Level Pricelist",
    "version": "14.0.1.0.1",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "LGPL-3",
    "category": "Sales",
    "summary": "Integrate privilege levels with pricelists",
    "depends": ["sale_privilege_level", "product"],
    "data": ["views/sale_privilege_level.xml", "security/ir.model.access.csv"],
    "installable": True,
    "post_init_hook": "_post_init_hook",
}
