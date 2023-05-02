# Copyright 2019-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    route_id = fields.Many2one(
        'stock.location.route', string='Route',
        ondelete='restrict', readonly=True, tracking=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        check_company=True,
        domain="['|', ('company_id', '=', company_id), ('company_id', '=', False), ('sale_selectable', '=', True)]")

    def _action_confirm(self):
        # Takes into account the scenario where route_id has a value, then SO is
        # cancelled+back to draft, then route_id = False and SO is confirmed again
        for order in self:
            vals = {'route_id': order.route_id.id or False}
            order.order_line.filtered(
                lambda l:
                l.product_id and l.product_id.type in ('product', 'consu')).write(vals)
        return super()._action_confirm()
