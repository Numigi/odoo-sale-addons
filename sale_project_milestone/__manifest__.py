# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Sale Project Milestone",
    "version": "1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "LGPL-3",
    "category": "Project",
    "summary": """Add two new services trackings products to generate or update milestones
    generated from a sale order line of a confirmed sale_order""",
    "depends": [
        "project_milestone_estimated_hours",
        "sale_timesheet_service_generation_override",
        "web_domain_field",
    ],
    "data": [
        "views/product.xml",
        "views/project_milestone.xml",
        "views/sale.xml",
    ],
    "installable": True,
}
