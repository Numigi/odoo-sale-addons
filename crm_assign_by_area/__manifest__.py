# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "CRM Assign By Area",
    "summary": "This module adds ability to assign salesperson to crm pipeline and contact",
    "version": "12.0.1.0.0",
    "website": "https://bit.ly/numigi-com",
    "author": "Numigi",
    "maintainer": "Numigi",
    "license": "AGPL-3",
    "depends": ["forward_sorting_area", "crm"],
    "data": [
        "views/crm_lead.xml",
        "views/res_partner.xml",
        "views/res_territory.xml",
        "wizard/assign_salesperson_by_area_wizard.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
