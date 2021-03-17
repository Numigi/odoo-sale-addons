# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class SaleIntercoServiceInvoice(models.TransientModel):

    _name = "sale.interco.service.invoice"
    _description = "Sale Interco Service Invoice"

    order_id = fields.Many2one("sale.order")

    company_id = fields.Many2one("res.company")
    discount = fields.Float(related="company_id.interco_service_discount")

    interco_company_id = fields.Many2one("res.company")
    interco_partner_id = fields.Many2one("res.partner")
    interco_position_id = fields.Many2one("account.fiscal.position")

    customer_id = fields.Many2one("res.partner")
    customer_position = fields.Char()
    customer_delivery_address_id = fields.Many2one("res.partner")
