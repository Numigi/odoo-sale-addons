# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    property_product_pricelist = fields.Many2one(
        domain=[("rental", "=", False)],
    )

    property_rental_pricelist = fields.Many2one(
        "product.pricelist",
        company_dependent=True,
        string="Rental Pricelist",
        domain=[("rental", "=", True)],
    )

    def _commercial_fields(self):
        return super()._commercial_fields() + ['property_rental_pricelist']
