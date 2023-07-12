# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import logging
from odoo import fields, models


class CouponReward(models.Model):

    _inherit = 'coupon.reward'

    discount_apply_on = fields.Selection(selection_add=[
        ('all_products', 'All targeted products'),
    ])
