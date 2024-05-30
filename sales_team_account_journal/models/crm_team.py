# Copyright 2024 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class CrmTeam(models.Model):
    _inherit = "crm.team"

    sales_journal_id = fields.Many2one(
        "account.journal",
        string="Sales Journal",
        domain=[("type", "=", "sale")],
        help=(
            "This Sales Journal will be set as default on all Sales related \
            to this Sales Team. Only Sales type journals can be selected.",
        ),
    )
