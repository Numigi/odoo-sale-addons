# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Sale Project Milestone",
    "version": "1.1.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "LGPL-3",
    "category": "Project",
    "summary": "Generate project milestones from sales orders",
    "depends": [
        "project_milestone_estimated_hours",
        "sale_timesheet",
    ],
    "data": [
        "views/product_template.xml",
        "views/project_milestone.xml",
        "views/sale_order.xml",
    ],
    "installable": True,
}
