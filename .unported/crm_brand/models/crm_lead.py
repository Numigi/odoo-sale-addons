# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class Lead(models.Model):

    _inherit = "crm.lead"

    brand_ids = fields.Many2many(
        "product.brand",
        "crm_lead_product_brand_rel",
        "lead_id",
        "product_id",
        string="Brands",
    )
