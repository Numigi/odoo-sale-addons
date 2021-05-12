from odoo import models

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
        prod.date_planned_finished = finish_date

    def _get_production_finish_date(self, prod):
        move = prod.move_dest_ids[:1]
        return self._compute_stock_move_date(move)

