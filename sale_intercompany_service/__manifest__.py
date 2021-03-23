# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Sale Inter-Company Service",
    "version": "1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "LGPL-3",
    "category": "Sales",
    "summary": "Sell to a customer on behalf of another company",
    "depends": ["sale_management"],
    "data": [
        "views/account_invoice.xml",
        "views/res_config_settings.xml",
        "views/sale_order.xml",
        "wizard/sale_interco_service_invoice.xml",
    ],
    "installable": True,
}
