# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ProductCategory(models.Model):

    _name = 'product.category'
    _inherit = ['product.category', 'mail.thread']

    minimum_margin = fields.Float(tracking=True)


class Product(models.Model):

    _inherit = 'product.product'

    minimum_margin = fields.Float(related='categ_id.minimum_margin')


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    minimum_margin = fields.Float(related='categ_id.minimum_margin')
