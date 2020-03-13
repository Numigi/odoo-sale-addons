# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"
    _order = "order_id, sequence, kit_sequence, id"

    is_kit = fields.Boolean()
    kit_sequence = fields.Integer()
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
        new_line.is_important_kit_component = kit_line.is_important
        self._set_kit_component_product_and_quantity(new_line, kit_line)
        self._set_kit_component_readonly_conditions(new_line, kit_line)
        return new_line

    def _set_kit_component_product_and_quantity(self, new_line, kit_line):
        uom = self.env.ref("uom.product_uom_unit")
        quantity = 1
        new_line.product_id = kit_line.component_id
        context = {
            "partner_id": self.order_id.partner_id.id,
            "quantity": quantity,
            "pricelist": self.order_id.pricelist_id.id,
            "uom": uom.id,
            "company_id": self.order_id.company_id.id,
        }
        new_line.with_context(**context).product_id_change()
        new_line.product_uom = uom
        new_line.product_uom_qty = quantity

    def _set_kit_component_readonly_conditions(self, new_line, kit_line):
        is_important = kit_line.is_important
        new_line.handle_widget_invisible = is_important
        new_line.trash_widget_invisible = is_important
        new_line.product_readonly = is_important
        new_line.product_uom_qty_readonly = is_important
        new_line.product_uom_readonly = is_important
        new_line.kit_reference_readonly = is_important
