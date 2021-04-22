# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    sale_analytic_tag_ids = fields.Many2many(
        "account.analytic.tag",
        "product_template_sale_analytic_tag_rel",
        "product_template_id",
        "tag_id",
    )
