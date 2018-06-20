# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class RentalReturnWizard(models.TransientModel):

    _name = 'rental.return.wizard'
    _description = 'Rental Return Wizard'

    line_ids = fields.One2many('rental.return.line', 'wizard_id', 'Products To Return')

    def process_rental_return(self):
        self.line_ids.process_rental_return()
