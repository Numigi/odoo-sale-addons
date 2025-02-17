# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "CRM Assign In House",
    "summary": """This module assigns customer's salesperson to
    CRM when select In-house customer""",
    "version": "14.0.1.0.0",
    "website": "https://bit.ly/numigi-com",
    "author": "Numigi",
    "maintainer": "Numigi",
    "license": "AGPL-3",
    "depends": ["sale_crm"],
    "data": ["views/res_partner.xml", "views/crm_lead.xml"],
    "installable": True,
}
