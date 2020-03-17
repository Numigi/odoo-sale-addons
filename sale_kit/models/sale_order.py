# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import re
from collections import defaultdict
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
            references = {l.kit_reference for l in self.order_line if l.kit_reference}
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

    @api.onchange("order_line")
    def unlink_dangling_kit_components(self):
        available_kit_refs = {
            line.kit_reference for line in self.order_line if line.is_kit
        }
        dangling_lines = self.order_line.filtered(
            lambda l: l.kit_reference and l.kit_reference not in available_kit_refs
        )
        self.order_line -= dangling_lines

    @api.onchange("order_line")
    def update_kit_component_sequences(self):
        kits = self.order_line.filtered(lambda l: l.is_kit)
        components = self.order_line.filtered(
            lambda l: not l.is_kit and l.kit_reference
        )
        other_lines = self.order_line - components - kits

        _recompute_sequences(kits | other_lines)
        _recompute_kit_sequences(kits, components)

        self.order_line = self.order_line.sorted(lambda l: (l.sequence, l.kit_sequence))


def _recompute_sequences(lines):
    next_sequence = 1
    for line in lines.sorted(lambda l: l.sequence):
        line.sequence = next_sequence
        next_sequence += 1


def _recompute_kit_sequences(kits, component_lines):
    kit_sequences = {
        l.kit_reference: l.sequence for l in kits.filtered(lambda l: l.is_kit)
    }
    component_sequences = defaultdict(int)

    def _set_line_sequence(kit_reference):
        line.sequence = kit_sequences.get(line.kit_reference)
        line.kit_sequence = component_sequences[line.kit_reference]
        component_sequences[line.kit_reference] += 1

    important_lines = component_lines.filtered(lambda l: l.is_important_kit_component)
    non_important_lines = component_lines - important_lines

    for line in important_lines.sorted(lambda l: l.sequence):
        _set_line_sequence(line)

    for line in non_important_lines.sorted(lambda l: l.sequence):
        _set_line_sequence(line)


def extract_kit_number(ref: str) -> int:
    match = re.search(r"(?P<number>\d+)$", ref)
    return int(match.group()) if match else 0
