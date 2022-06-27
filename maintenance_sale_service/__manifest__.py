# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Maintenance Sale Service",
    "version": "1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "LGPL-3",
    "category": "Sales",
    "summary": "Propagation of Equipment from the sale order line to the task when the sales line creates a task",
    "depends": [
        "maintenance_equipment_model",
        "sale_timesheet",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/project_task.xml",
        "views/sale_order_line.xml",
    ],
    "installable": True,
}
