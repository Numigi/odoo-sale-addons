# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from collections import defaultdict
from odoo import api, fields, models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    is_kit = fields.Boolean()
    kit_sequence = fields.Integer()
    is_kit_component = fields.Boolean()
    is_important_kit_component = fields.Boolean()
    kit_reference = fields.Char()
    kit_reference_readonly = fields.Boolean()
    kit_initialized = fields.Boolean()
    available_kit_references = fields.Char(related="order_id.available_kit_references")
    next_kit_reference = fields.Char(related="order_id.next_kit_reference")

    @api.onchange("product_id")
    def product_id_change(self):
        super().product_id_change()
        self.is_kit = self.product_id.is_kit

    def initialize_kit(self):
        self.kit_reference = self.next_kit_reference
        self.add_kit_components()
        self.set_kit_line_readonly_conditions()
        self.kit_initialized = True

    def set_kit_line_readonly_conditions(self):
        self.handle_widget_invisible = False
        self.trash_widget_invisible = False
        self.product_readonly = True
        self.product_uom_qty_readonly = True
        self.product_uom_readonly = True
        self.kit_reference_readonly = True

    def add_kit_components(self):
        for kit_line in self.product_id.kit_line_ids:
            component_line = self.prepare_kit_component(kit_line)
            self.order_id.order_line |= component_line

    def prepare_kit_component(self, kit_line):
        new_line = self.new({})
        new_line.kit_reference = self.kit_reference
        new_line.is_kit_component = True
        new_line.is_important_kit_component = kit_line.is_important
        self._set_kit_component_product_and_quantity(new_line, kit_line)
        self._set_kit_component_readonly_conditions(new_line, kit_line)
        return new_line

    def _set_kit_component_product_and_quantity(self, new_line, kit_line):
        new_line.set_product_and_quantity(
            order=self.order_id,
            product=kit_line.component_id,
            uom=kit_line.uom_id,
            qty=kit_line.quantity,
        )

    def set_product_and_quantity(self, order, product, uom, qty):
        self.product_id = product
        self.order_id = order
        self.product_id_change()

        self.product_uom = uom
        self.product_uom_qty = qty
        self.product_uom_change()

    def _set_kit_component_readonly_conditions(self, new_line, kit_line):
        is_important = kit_line.is_important
        new_line.handle_widget_invisible = is_important
        new_line.trash_widget_invisible = is_important
        new_line.product_readonly = is_important
        new_line.product_uom_qty_readonly = is_important
        new_line.product_uom_readonly = is_important
        new_line.kit_reference_readonly = is_important

    def recompute_sequences(self):
        next_sequence = 1
        for line in self:
            line.sequence = next_sequence
            next_sequence += 1

    def recompute_kit_sequences(self, kits):
        kit_sequences = {l.kit_reference: l.sequence for l in kits}
        next_sequences = defaultdict(lambda: 1)

        for line in self:
            kit_ref = line.kit_reference
            line.sequence = kit_sequences.get(kit_ref)
            line.kit_sequence = next_sequences[kit_ref]
            next_sequences[kit_ref] += 1

    def sorted_by_sequence(self):
        return self.sorted(key=lambda l: l.sequence)

    def sorted_by_kit_sequence(self):
        return self.sorted(key=lambda l: l.kit_sequence)

    def sorted_by_importance(self):
        return self.sorted(key=lambda l: 0 if l.is_important_kit_component else 1)


class SaleOrderLineWithLinkBetweenLines(models.Model):

    _inherit = "sale.order.line"

    kit_line_ids = fields.One2many(
        "sale.order.line", "kit_id", "Components", readonly=True
    )
    kit_id = fields.Many2one(
        "sale.order.line", "Kit", store=True, compute="_compute_kit_id"
    )

    @api.depends("kit_reference")
    def _compute_kit_id(self):
        for line in self:
            line.kit_id = line._get_kit_line()

    def _get_kit_line(self):
        if self.is_kit or not self.kit_reference:
            return None

        return self.order_id.order_line.filtered(
            lambda l: l.is_kit and l.kit_reference == self.kit_reference
        )[0:1]


class SaleOrderLineDeliveredQty(models.Model):
    """Add the logic related to the delivered qty of a kit."""

    _inherit = "sale.order.line"

    qty_delivered_method = fields.Selection(selection_add=[("kit", "Kit")])

    @api.depends("is_kit")
    def _compute_qty_delivered_method(self):
        super()._compute_qty_delivered_method()
        kits = self.filtered(lambda l: l.is_kit)
        kits.update({"qty_delivered_method": "kit"})

    @api.depends("kit_line_ids", "kit_line_ids.qty_delivered")
    def _compute_qty_delivered(self):
        super()._compute_qty_delivered()
        kit_lines = self.filtered(lambda l: l.qty_delivered_method == "kit")
        kit_lines._compute_kit_qty_delivered()

    def _compute_kit_qty_delivered(self):
        for line in self:
            line.qty_delivered = line._get_kit_qty_delivered()

    def _get_kit_qty_delivered(self):
        important_components = self.kit_line_ids.filtered(
            lambda l: l.is_important_kit_component
        )
        return all(l.qty_delivered >= l.product_uom_qty for l in important_components)
