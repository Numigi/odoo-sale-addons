# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models

class SaleCommitmentDateUpdate(models.TransientModel):
    _name = "sale.commitment.date.update"
    _description = "Sale Commitment Date Update"

    order_id = fields.Many2one("sale.order")
    date = fields.Datetime()

    def confirm(self):
        delta = self.date - self.order_id.commitment_date
        self.order_id.commitment_date = self.date

        moves = self.order_id.mapped("order_line.move_ids")

        # import ipdb;ipdb.set_trace()
        for move in moves:
            move.write({"date_expected": move.date_expected + delta})