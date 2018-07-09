# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class MrpRepairWithAnalyticAccount(models.Model):

    _inherit = 'mrp.repair'

    analytic_account_id = fields.Many2one(
        'account.analytic.account', 'Analytic Account', ondelete='restrict')


class MrpRepairLineWithAnalyticAccountPropagationToInvoice(models.Model):

    _inherit = 'mrp.repair.line'

    @api.multi
    def write(self, vals):
        super().write(vals)

        if 'invoice_line_id' in vals:
            self._propagate_analytic_account_to_invoice_line()

        return True

    def _propagate_analytic_account_to_invoice_line(self):
        invoiced_lines = self.filtered(lambda l: l.invoice_line_id)

        for line in invoiced_lines:
            line.invoice_line_id.account_analytic_id = line.repair_id.analytic_account_id


class MrpRepairFeesWithAnalyticAccountPropagationToInvoice(models.Model):

    _inherit = 'mrp.repair.fee'

    @api.multi
    def write(self, vals):
        super().write(vals)

        if 'invoice_line_id' in vals:
            self._propagate_analytic_account_to_invoice_line()

        return True

    def _propagate_analytic_account_to_invoice_line(self):
        invoiced_lines = self.filtered(lambda l: l.invoice_line_id)

        for line in invoiced_lines:
            line.invoice_line_id.account_analytic_id = line.repair_id.analytic_account_id


class MrpRepairLineWithAnalyticAccountPropagationStockMove(models.Model):

    _inherit = 'mrp.repair.line'

    @api.multi
    def write(self, vals):
        super().write(vals)

        if 'move_id' in vals:
            self._propagate_analytic_account_to_stock_move()

        return True

    def _propagate_analytic_account_to_stock_move(self):
        processed_lines = self.filtered(lambda l: l.move_id)

        for line in processed_lines:
            line.move_id.analytic_account_id = line.repair_id.analytic_account_id
