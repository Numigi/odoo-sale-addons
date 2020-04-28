# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class StockRentalConversionWizard(models.TransientModel):

    _name = "stock.rental.conversion.wizard"
    _description = "Stock Rental Conversion Wizard"

    product_id = fields.Many2one("product.product")
    lot_id = fields.Many2one("stock.production.lot")
    source_location_id = fields.Many2one("stock.location")
    destination_location_id = fields.Many2one("stock.location")

    @api.onchange("lot_id")
    def _set_locations_from_selected_serial_number(self):
        if self.lot_id:
            current_location = self.lot_id.get_current_location()[:1]
            current_warehouse = current_location.get_warehouse()
            self.source_location_id = current_location
            self.destination_location_id = current_warehouse.rental_location_id
