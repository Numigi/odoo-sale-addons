# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    is_intercompany_delivery = fields.Boolean()

    def _get_accounting_data_for_valuation(self):
        (
            journal_id,
            acc_src,
            acc_dest,
            acc_valuation,
        ) = super()._get_accounting_data_for_valuation()

        if self.is_intercompany_delivery:
            return journal_id, acc_dest, acc_src, acc_valuation
        else:
            return journal_id, acc_src, acc_dest, acc_valuation
