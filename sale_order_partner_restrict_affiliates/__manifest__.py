# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Sale Order Partner Restrict Affiliates",
    "summary": "Apply restrictions when selecting from the list of customers on SO.",
    "version": "1.1.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://numigi.com/r/home",
    "license": "LGPL-3",
    "category": "Sales",
    "depends": ["sale_order_partner_restrict", "partner_affiliate"],
    "data": ["views/res_partner_view.xml"],
    "installable": True,
}
