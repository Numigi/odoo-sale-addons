# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class sale_order_available_qty_popover_rental(models.Model):
#     _name = 'sale_order_available_qty_popover_rental.sale_order_available_qty_popover_rental'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100