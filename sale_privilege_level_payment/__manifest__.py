# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Sale Privilege Level Payment",
    "version": "14.0.1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://numigi.com/r/home",
    "license": "LGPL-3",
    "category": "Sales",
    "summary": "Integrate privilege levels with payments for the e-commerce",
    "depends": ["sale_privilege_level", "payment"],
    "data": ["views/payment_acquirer.xml", "views/sale_privilege_level.xml"],
    "installable": True,
}
