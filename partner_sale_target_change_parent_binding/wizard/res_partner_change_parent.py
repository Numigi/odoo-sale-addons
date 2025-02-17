# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, models


class ResPartnerParentChange(models.TransientModel):

    _inherit = 'res.partner.change.parent'

    @api.onchange('new_company_id')
    def _onchange_new_company_id(self):
        if self.new_company_id and self.contact_id.sale_target_ids and\
                self.contact_id.company_type == 'person':
            return {'warning': {
                'title': _("Warning"),
                'message': _('Please note that the Sales Targets will be '
                             'deleted, Sales Targets will be managed on '
                             'the commercial entity.'
                             ),
            }}
