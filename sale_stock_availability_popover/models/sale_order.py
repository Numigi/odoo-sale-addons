from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    qty_available_color = fields.Char(
        compute="_compute_qty_available_color",
    )
    qty_reserved = fields.Float(
        compute="_compute_qty_reserved",
    )

    @api.depends("free_qty_today", "qty_to_deliver")
    def _compute_qty_available_color(self):
        for line in self:
            line.qty_available_color = line._get_qty_color()

    def _get_qty_color(self):
        self.ensure_one()
        if self._is_fully_available():
            return "text-success"
        if self._is_partially_available():
            return "text-warning"
        return "text-danger"

    def _is_fully_available(self):
        self.ensure_one()
        return self.free_qty_today and self.qty_to_deliver <= self.free_qty_today

    def _is_partially_available(self):
        self.ensure_one()
        return 0 < self.free_qty_today < self.qty_to_deliver

    @api.depends("qty_available_today", "free_qty_today")
    def _compute_qty_reserved(self):
        for line in self:
            line.qty_reserved = line.qty_available_today - line.free_qty_today

    @api.depends("state", "product_type", "qty_delivered")
    def _compute_display_qty_widget(self):
        super()._compute_display_qty_widget()
        for line in self:
            if line._should_force_widget_display():
                line.display_qty_widget = True

    def _should_force_widget_display(self):
        self.ensure_one()
        return self.state in ["draft", "sent", "sale"] and self.product_type == "consu"