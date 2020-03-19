# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


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

    @api.onchange("product_uom", "product_uom_qty")
    def product_uom_change(self):
        super().product_uom_change()

        if self._is_rented_kit() or self._is_rented_kit_component():
            self.price_unit = 0

    @api.multi
    def _compute_tax_id(self):
        super()._compute_tax_id()

        lines_with_no_tax = self.filtered(
            lambda l: l._is_rented_kit() or l._is_rented_kit_component()
        )
        lines_with_no_tax.update({"tax_id": None})

    def initialize_kit(self):
        if self.is_rental_order:
            self._check_kit_can_be_rented()

        super().initialize_kit()

        if self.is_rental_order:
            self._add_kit_rental_service_to_order()
            self._add_readonly_flags_for_rented_kit()

    def _check_kit_can_be_rented(self):
        if not self.product_id.can_be_rented:
            raise ValidationError(
                _("The kit {} can not be rented.").format(self.product_id.display_name)
            )

    def _add_kit_rental_service_to_order(self):
        service_line = self.prepare_kit_rental_service()
        service_line._compute_tax_id()
        self.order_id.order_line |= service_line

    def _add_readonly_flags_for_rented_kit(self):
        self.price_unit_readonly = True
        self.taxes_readonly = True

    def prepare_kit_component(self, kit_line):
        new_line = super().prepare_kit_component(kit_line)

        if self.is_rental_order:
            new_line.price_unit = 0
            new_line.price_unit_readonly = True
            new_line.taxes_readonly = True

        return new_line

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

    def _is_rented_kit(self):
        return self.is_kit and self.is_rental_order

    def _is_rented_kit_component(self):
        return self.is_kit_component and self.is_rental_order
