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
        if prod.date_planned_finished:
            delta = self._get_delta(prod.product_id)
            prod.write({"date_planned_finished": prod.date_planned_finished + delta})