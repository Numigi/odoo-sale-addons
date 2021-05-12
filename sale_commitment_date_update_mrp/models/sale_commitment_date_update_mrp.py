from odoo import models

class SaleCommitmentDateUpdateMrp(models.TransientModel):
    _inherit = "sale.commitment.date.update"

    def confirm(self):
        super().confirm()
        mrp_order = self.env["mrp.production"].search([('procurement_group_id', '=', self.order_id.procurement_group_id.id)])
        mrp_order.write({'date_planned_finished': self.date,})