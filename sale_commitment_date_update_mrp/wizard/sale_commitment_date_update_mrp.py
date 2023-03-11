# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models
from datetime import timedelta


class SaleCommitmentDateUpdateMrp(models.TransientModel):
    _inherit = "sale.commitment.date.update"

    def _propagate_date(self):
        super()._propagate_date()
        moves = self._get_all_stock_moves()
        prod_ids = moves.mapped("created_production_id")
        for prod in prod_ids:
            self._process_production(prod)

    def _process_production(self, prod):
        finish_date = self._get_production_finish_date(prod)
        start_date = self._get_production_start_date(prod, finish_date)
        prod.date_planned_finished = finish_date
        prod.date_planned_start = start_date

    def _get_production_finish_date(self, prod):
        move = prod.move_dest_ids[:1]
        return self._compute_stock_move_date(move)

    def _get_production_start_date(self, prod, finish):
        return (
            finish
            - timedelta(self.order_id.company_id.manufacturing_lead or 0)
            - timedelta(prod.product_id.produce_delay or 0)
        )
