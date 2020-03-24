# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _


class StockMove(models.Model):

    _inherit = "stock.move"

    def _action_done(self):
        result = super()._action_done()

        rental_return_moves = self.filtered(lambda l: l.is_rental_return_move())
        for move in rental_return_moves:
            move._update_sale_rental_service_line()

        return result

    def _update_sale_rental_service_line(self):
        kit_line = self.sale_line_id.kit_id
        service_line = kit_line.mapped("kit_line_ids").filtered(
            lambda l: l.is_rental_service
        )
        service_line.kit_returned_qty = kit_line.rental_returned_qty

    def is_processed_move(self):
        return self.state in ("done", "cancel")

    def is_done_move(self):
        return self.state == "done"

    def is_rental_move(self):
        return self.location_dest_id.is_rental_customer_location

    def is_rental_return_move(self):
        return self.location_id.is_rental_customer_location

    def set_expected_date(self, date_):
        self.write({"date_expected": date_})
