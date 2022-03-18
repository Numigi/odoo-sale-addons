# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Sale Privilege Level Rental Pricelist",
    "version": "1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "LGPL-3",
    "category": "Sales",
    "summary": "Integrate privilege levels with rental pricelists",
    "depends": ["sale_privilege_level_pricelist", "sale_rental_pricelist"],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_privilege_level.xml",
    ],
    "installable": True,
}
