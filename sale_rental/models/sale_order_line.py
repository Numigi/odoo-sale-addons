# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    is_rental_order = fields.Boolean(related="order_id.is_rental")
    rental_date_from = fields.Datetime()
    rental_date_to = fields.Datetime()
    rental_date_from_editable = fields.Boolean()
    rental_date_from_required = fields.Boolean()
    rental_date_to_editable = fields.Boolean()
    is_rental_service = fields.Boolean()

    @api.onchange("product_id")
    def product_id_change(self):
        res = super().product_id_change()

        if (
            self.is_rental_order
            and self.product_id.can_be_rented
            and not self.kit_reference
        ):
            self.is_kit = True

        return res

    @api.onchange("product_uom", "product_uom_qty")
    def product_uom_change(self):
        super().product_uom_change()

        if self._is_rented_kit_component():
            self.price_unit = 0

    @api.onchange("rental_date_from", "rental_date_to")
    def onchange_rental_dates(self):
        if self.is_rental_service and self.rental_date_from and self.rental_date_to:
            self._force_rental_date_to_after_date_from()
            self.product_uom_qty = self._get_qty_based_on_rental_dates()

    def _force_rental_date_to_after_date_from(self):
        if self.rental_date_from > self.rental_date_to:
            self.rental_date_to = self.rental_date_from

    def _get_qty_based_on_rental_dates(self):
        buffer = self._get_buffer()
        quantity = self.rental_date_to - self.rental_date_from - buffer
        return max(quantity.days + 1, 1)

    def _get_buffer(self):
        buffer = timedelta(hours=int(self.company_id.rental_buffer))
        return buffer

    def _compute_tax_id(self):
        super()._compute_tax_id()

        lines_with_no_tax = self.filtered(
            lambda l: l._is_rented_kit() or l._is_rented_kit_component()
        )
        lines_with_no_tax.update({"tax_id": None})

    def _compute_qty_delivered(self):
        super()._compute_qty_delivered()

        lines_to_update = self.filtered(
            lambda l: l.qty_delivered_method == "stock_move" and l.order_id.is_rental
        )

        for line in lines_to_update:
            done_rental_moves = line.move_ids.filtered(
                lambda m: m.is_done_move() and m.is_rental_move()
            )
            line.qty_delivered = sum(
                self._get_stock_move_qty_in_sale_line_uom(move)
                for move in done_rental_moves
            )

    def _get_stock_move_qty_in_sale_line_uom(self, move):
        return move.product_uom._compute_quantity(
            move.product_uom_qty, self.product_uom
        )

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        rental_lines = self.filtered(lambda l: l.order_id.is_rental)
        rental_orders = rental_lines.mapped("order_id")

        for order in rental_orders:
            rental_location = order.get_rental_customer_location()
            lines = rental_lines.filtered(lambda l: l.order_id == order).with_context(
                force_rental_customer_location=rental_location
            )
            super(SaleOrderLine, lines)._action_launch_stock_rule(previous_product_uom_qty=previous_product_uom_qty)

        other_lines = self - rental_lines
        super(SaleOrderLine, other_lines)._action_launch_stock_rule(previous_product_uom_qty=previous_product_uom_qty)
        return True

    def initialize_kit(self):
        if self.is_rental_order:
            self._check_kit_can_be_rented()

        super().initialize_kit()

        if self.is_rental_order:
            self._add_readonly_flags_for_rented_kit()

    def add_kit_components(self):
        if self.is_rental_order:
            self._add_kit_rental_service_to_order()

        super().add_kit_components()

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
        self.product_uom_qty_readonly = True
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
        new_line.kit_reference_readonly = True
        new_line.is_rental_service = True
        new_line.product_readonly = True
        new_line.product_uom_qty_readonly = False
        new_line.product_uom_readonly = True
        new_line.handle_widget_invisible = False
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
        new_line.rental_date_from = datetime.now()
        return new_line

    def _is_rented_kit(self):
        return self.is_kit and self.is_rental_order

    def _is_rented_kit_component(self):
        return self.is_kit_component and self.is_rental_order


class SaleOrderLineWithRentalDates(models.Model):
    _inherit = "sale.order.line"

    expected_rental_date = fields.Datetime()
    expected_return_date = fields.Datetime()

    @api.model
    def create(self, vals):
        line = super().create(vals)
        line.refresh()
        line.order_id.propagate_service_rental_dates()
        return line

    def write(self, vals):
        super().write(vals)
        if (
            "kit_reference" in vals
            or "rental_date_from" in vals
            or "rental_date_to" in vals
        ):
            self.mapped("order_id").propagate_service_rental_dates()

        if "expected_rental_date" in vals or "expected_return_date" in vals:
            for line in self:
                line.propagate_stock_rental_dates()

        return True

    def propagate_service_rental_dates(self):
        lines_to_update = self.order_id.order_line.filtered(
            lambda l: (
                self._is_in_same_kit(l)
                and not self._service_rental_dates_already_propagated(l)
            )
        )
        if lines_to_update:
            lines_to_update.write(
                {
                    "expected_rental_date": self.rental_date_from,
                    "expected_return_date": self.rental_date_to,
                }
            )

    def _is_in_same_kit(self, other_line):
        return other_line.kit_reference == self.kit_reference

    def _service_rental_dates_already_propagated(self, other_line):
        return (
            other_line.expected_rental_date == self.rental_date_from
            and other_line.expected_return_date == self.rental_date_to
        )

    def propagate_stock_rental_dates(self):
        rental_date = self.expected_rental_date or datetime.now()
        return_date = self.expected_return_date or rental_date
        self._propagate_rental_date_to_stock_moves(rental_date)
        self._propagate_return_date_to_stock_moves(return_date)

    def _propagate_rental_date_to_stock_moves(self, date_):
        rental_moves = self.move_ids.filtered(lambda m: m.is_rental_move())
        moves_to_update = rental_moves.with_all_origin_moves().filtered(
            lambda m: not m.is_processed_move()
        )
        moves_to_update.set_expected_date(date_)

    def _propagate_return_date_to_stock_moves(self, date_):
        moves_to_update = self.move_ids.filtered(
            lambda m: m.is_rental_return_move() and not m.is_processed_move()
        )
        moves_to_update.set_expected_date(date_)


class SaleOrderLineWithReturnedQty(models.Model):

    _inherit = "sale.order.line"

    rental_returned_qty = fields.Float(
        "Rental Returned Quantity",
        copy=False,
        compute="_compute_rental_returned_qty",
        compute_sudo=True,
        store=True,
        digits=dp.get_precision("Product Unit of Measure"),
        default=0.0,
    )

    @api.depends("kit_line_ids.rental_returned_qty", "move_ids.state")
    def _compute_rental_returned_qty(self):
        kits = self.filtered(lambda l: l.product_id.type == "service" and l.is_kit)
        for line in kits:
            line.rental_returned_qty = line._get_kit_rental_returned_qty()

        physical_products = self.filtered(
            lambda l: l.product_id.type in ("product", "consu")
        )
        for line in physical_products:
            line.rental_returned_qty = self._get_product_rental_returned_qty()

    def _get_kit_rental_returned_qty(self):
        all_important_components_returned = all(
            l.rental_returned_qty >= l.product_uom_qty
            for l in self.kit_line_ids
            if l.is_important_kit_component
        )
        return 1 if all_important_components_returned else 0

    def _get_product_rental_returned_qty(self):
        done_rental_return_moves = self.move_ids.filtered(
            lambda m: m.is_done_move() and m.is_rental_return_move()
        )
        return sum(
            self._get_stock_move_qty_in_sale_line_uom(move)
            for move in done_rental_return_moves
        )


class SaleOrderLineWithRentalServiceReturnedQty(models.Model):

    _inherit = "sale.order.line"

    kit_delivered_qty = fields.Float(
        digits=dp.get_precision("Product Unit of Measure"), default=0.0, copy=False
    )

    kit_returned_qty = fields.Float(
        digits=dp.get_precision("Product Unit of Measure"), default=0.0, copy=False
    )

    @api.depends("is_rental_service")
    def _compute_qty_delivered_method(self):
        super()._compute_qty_delivered_method()
        rental_services = self.filtered(lambda l: l.is_rental_service)
        rental_services.update({"qty_delivered_method": "rental_service"})

    qty_delivered_method = fields.Selection(
        selection_add=[("rental_service", "Rental Service")]
    )

    def update_rental_service_qty_delivered_cron(self):
        lines_to_recompute = self.search(
            [
                ("is_rental_service", "=", True),
                ("state", "in", ("sale", "done")),
                ("kit_returned_qty", "<=", 0),
                ("rental_date_from", "!=", False),
            ]
        )
        lines_to_recompute.modified(["rental_date_from"])
        lines_to_recompute.recompute()

    @api.depends(
        "kit_delivered_qty", "kit_returned_qty", "product_uom_qty", "rental_date_from"
    )
    def _compute_qty_delivered(self):
        super()._compute_qty_delivered()
        rental_services = self.filtered(
            lambda l: l.qty_delivered_method == "rental_service"
        )
        rental_services._compute_rental_service_qty_delivered()

    def _compute_rental_service_qty_delivered(self):
        for line in self:
            line.qty_delivered = line._get_rental_service_qty_delivered()

    def _get_rental_service_qty_delivered(self):
        if self.kit_delivered_qty < 1:
            return 0

        if self.kit_returned_qty > 0:
            return self.product_uom_qty

        if not self.rental_date_from:
            return 0

        now = datetime.now()
        number_of_days = (now - self.rental_date_from).days
        return max(number_of_days + 1, 0)
