# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Sale Privilege Level Delivery",
    "version": "1.1.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "LGPL-3",
    "category": "Sales",
    "summary": "Integrate privilege levels with carriers",
    "depends": ["sale_privilege_level", "delivery"],
    "data": [
        "views/delivery_carrier.xml",
        "views/sale_privilege_level.xml",
        "views/res_partner.xml",
    ],
    "installable": True,
}
