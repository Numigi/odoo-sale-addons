# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    so_popover_alternative = fields.Boolean("Product availability by warehouse")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()

        res['so_popover_alternative'] =self.env['ir.config_parameter'].sudo().get_param(
            'sale_order_available_qty_popover_alternative.so_popover_alternative')

        return res

    @api.model
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param(
            'sale_order_available_qty_popover_alternative.so_popover_alternative', self.so_popover_alternative)

        super(ResConfigSettings, self).set_values()

