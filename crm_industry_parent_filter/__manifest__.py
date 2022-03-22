# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "CRM Industry Parent Filter",
    "version": "1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "license": "LGPL-3",
    "category": "CRM",
    "summary": "Filter secondary industries on leads based on the main industry",
    "depends": ["crm_industry",],
    "data": [
        "views/crm_lead.xml",
        "views/res_partner.xml",
    ],
    "installable": True,
}
