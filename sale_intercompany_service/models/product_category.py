# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ProductCategory(models.Model):

    _inherit = "product.category"

    intercompany_revenue_account_id = fields.Many2one(
        'account.account',
        domain=[('deprecated', '=', False)],
    )

    intercompany_expense_account_id = fields.Many2one(
        'account.account',
        domain=[('deprecated', '=', False)],
    )
