# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    is_rental_order = fields.Boolean(related="order_id.is_rental")
    rental_date_from = fields.Date()
    rental_date_to = fields.Date()
    rental_date_from_editable = fields.Boolean()
    rental_date_from_required = fields.Boolean()
    rental_date_to_editable = fields.Boolean()
    is_rental_service = fields.Boolean()

    @api.onchange("product_id")
    def product_id_change(self):
        super().product_id_change()

        if (
            self.is_rental_order
            and self.product_id.can_be_rented
            and not self.kit_reference
        ):
            self.is_kit = True

    def initialize_kit(self):
        super().initialize_kit()
        if self.order_id.is_rental and self.product_id.can_be_rented:
            service_line = self.prepare_kit_rental_service()
            self.order_id.order_line |= service_line

    def prepare_kit_rental_service(self):
        new_line = self.new({})
        new_line.kit_reference = self.kit_reference
        new_line.is_rental_service = True
        new_line.product_readonly = True
        new_line.product_uom_qty_readonly = False
        new_line.product_uom_readonly = True
        new_line.handle_widget_invisible = True
        new_line.trash_widget_invisible = True
        new_line.rental_date_from_required = True
        new_line.rental_date_from_editable = True
        new_line.rental_date_to_editable = True
        new_line.set_product_and_quantity(
            order=self.order_id,
            product=self.product_id.rental_service_id,
            qty=1,
            uom=self.env.ref("uom.product_uom_day"),
        )
        new_line.rental_date_from = fields.Date.context_today(self)
        return new_line

    def sorted_by_importance(self):
        result = super().sorted_by_importance()
        return result.sorted(key=lambda l: 0 if l.is_rental_service else 1)
