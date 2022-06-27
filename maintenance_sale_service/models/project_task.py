# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    equipment_id = fields.Many2one("maintenance.equipment")
    manufacturer_id = fields.Many2one(
        "res.partner", related="equipment_id.model_id.manufacturer_id"
    )
    model_id = fields.Many2one(
        "maintenance.equipment.model", related="equipment_id.model_id"
    )
    serial_no = fields.Char("Serial Number", related="equipment_id.serial_no")
