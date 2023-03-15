# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    property_product_pricelist = fields.Many2one(
        domain=[("rental", "=", False)],
    )

    rental_pricelist_id = fields.Many2one(
        "product.pricelist",
        compute="_compute_rental_pricelist",
    )

    property_rental_pricelist_id = fields.Many2one(
        "product.pricelist",
        company_dependent=True,
        string="Rental Pricelist (Company Property)",
        domain=[("rental", "=", True)],
    )

    def _commercial_fields(self):
        return super()._commercial_fields() + ["property_rental_pricelist_id"]

    @api.depends("property_rental_pricelist_id")
    def _compute_rental_pricelist(self):
        for partner in self:
            partner.rental_pricelist_id = partner.property_rental_pricelist_id
