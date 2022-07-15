# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Website(models.Model):
    _inherit = 'website'
    
    
    crm_default_team_id = fields.Many2one(
        'crm.team', string='Default Sales Teams',
        default=lambda self :self.env['ir.model.data'].get_object('numigi_test_crm_minoumissek', 'crm_team_equip_vent').id)
