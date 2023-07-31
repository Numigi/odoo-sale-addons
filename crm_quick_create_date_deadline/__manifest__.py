# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "CRM Quick Create Date Deadline",
    "version": "1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "AGPL-3",
    "category": "CRM",
    "depends": ["crm"],
    "summary": """
        Blocks the creation of an opportunity from the kanban view (quick creation) 
        of opportunities if no planned closing date is entered.
        """,
    "data": [
        "views/crm_lead.xml",
    ],
    "installable": True,
}
