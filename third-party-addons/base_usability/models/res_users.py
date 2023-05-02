# Copyright 2018-2020 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, SUPERUSER_ID
import logging
from odoo.tools.misc import format_datetime

logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def _script_partners_linked_to_users_no_company(self):
        if self.env.user.id != SUPERUSER_ID:
            self = self.sudo()
        logger.info(
            'START to set company_id=False on partners related to users')
        users = self.with_context(active_test=False).search([])
        for user in users:
            if user.partner_id.company_id:
                user.partner_id.write({'company_id': False})
                logger.info(
                    'Wrote company_id=False on user %s ID %d',
                    user.login, user.id)
        logger.info(
            'END setting company_id=False on partners related to users')

    def _report_print_datetime(self, lang_code):
        # Used to print current datetime in a report in the user's timezone
        res = format_datetime(self.env, fields.Datetime.now(), lang_code=lang_code)
        return res
