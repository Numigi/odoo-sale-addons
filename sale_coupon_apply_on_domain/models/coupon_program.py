# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import fields, models


class CouponReward(models.Model):

    _inherit = 'coupon.reward'

    discount_apply_on = fields.Selection(selection_add=[
        ('all_products', 'All targeted products'),
    ])
