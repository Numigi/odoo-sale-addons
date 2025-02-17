# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import re
from odoo import api, fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    next_kit_reference = fields.Char(compute="_compute_next_kit_reference")
    available_kit_references = fields.Char(compute="_compute_available_kit_references")

    @api.depends("order_line", "order_line.kit_reference")
    def _compute_next_kit_reference(self):
        for order in self:
            order.next_kit_reference = order._get_next_kit_reference()

    @api.depends("order_line", "order_line.kit_reference")
    def _compute_available_kit_references(self):
        for order in self:
            references = {
                line.kit_reference for line in self.order_line if line.kit_reference
            }
            sorted_refs = sorted(list(references))
            order.available_kit_references = ",".join(sorted_refs)

    def _get_next_kit_reference(self):
        kit_refs = [ref for ref in self.order_line.mapped("kit_reference") if ref]

        if not kit_refs:
            return "K1"

        highest_ref = sorted(kit_refs)[-1]
        number = extract_kit_number(highest_ref)
        return "K{}".format(number + 1)

    @api.onchange("order_line")
    def initialize_kits(self):
        uninitialized_kit_lines = self.order_line.filtered(
            lambda l: l.is_kit and not l.kit_initialized
        )

        for line in uninitialized_kit_lines:
            line.initialize_kit()
            line._compute_tax_id()

    @api.onchange("order_line")
    def update_kit_component_quantities(self):
        kits = self.order_line.filtered(lambda l: l.is_kit and l.product_uom_qty)
        for kit in kits:
            kit._update_kit_component_quantities()

    @api.onchange("order_line")
    def unlink_dangling_kit_components(self):
        kits = self.get_kits_per_reference()
        dangling_lines = self.order_line.filtered(
            lambda l: l.kit_reference and l.kit_reference not in kits
        )
        self.order_line -= dangling_lines

    @api.onchange("order_line")
    def update_kit_component_sequences(self):
        self.recompute_order_line_sequences()
        self.order_line = self.order_line.sorted(lambda l: l.sequence)

    def recompute_order_line_sequences(self):
        kits = self.get_kits()
        components = self.get_kit_components()
        other_lines = self.order_line - components - kits

        (kits | other_lines).sorted_by_sequence().recompute_sequences()

        kits.update({"kit_sequence": 0})

        sorted_components = components.sorted_by_sequence().sorted_by_kit_sequence()
        sorted_components.recompute_kit_sequences(kits)

        all_lines = kits | components | other_lines
        all_lines_sorted = all_lines.sorted(
            lambda line: (line.sequence, line.kit_sequence)
        )
        all_lines_sorted.recompute_sequences()

    def get_kits_per_reference(self):
        return {line.kit_reference: line for line in self.get_kits()}

    def get_kits(self):
        return self.order_line.filtered(lambda line: line.is_kit)

    def get_kit_components(self):
        return self.order_line.filtered(
            lambda line: not line.is_kit and line.kit_reference
        )


def extract_kit_number(ref: str) -> int:
    match = re.search(r"(?P<number>\d+)$", ref)
    return int(match.group()) if match else 0
