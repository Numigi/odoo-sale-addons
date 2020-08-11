# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class Company(models.Model):  # Company

    _inherit = "res.company"

    rental_buffer = fields.Selection(
        [
            ("2", "2"),
            ("4", "4"),
            ("6", "6"),
            ("8", "8"),
            ("10", "10"),
            ("12", "12"),
            ("14", "14"),
            ("16", "16"),
            ("18", "18"),
            ("20", "20"),
            ("22", "22"),
            ("24", "24"),
        ],
        default="6",
        string="Rental buffer",
    )
