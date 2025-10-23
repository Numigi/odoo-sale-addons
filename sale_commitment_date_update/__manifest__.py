# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Sale Commitment Date Update",
    "version": "14.0.1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://numigi.com/r/home",
    "license": "LGPL-3",
    "category": "Sales",
    "summary": "Allows to change the sale commitment date",
    "depends": [
        "sale_stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/sale_commitment_date_update.xml",
        "views/sale_order.xml",
    ],
    "installable": True,
}
