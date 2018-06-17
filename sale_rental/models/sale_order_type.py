# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class SaleOrderTypeWithIsRental(models.Model):

    _inherit = 'sale.order.type'

    is_rental = fields.Boolean('Is Rental')
