# -*- coding: utf-8 -*-
import logging
_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    """
    Appelé après installation du module.

    """
    from odoo import api, SUPERUSER_ID
    env = api.Environment(cr, SUPERUSER_ID, {})

    # _logger.info("CRM Auto Config [post_init_hook] : Démarrage...")

    try:
        config = env['res.config.settings'].create({
            'group_use_lead': True,                  
            'generate_lead_from_alias': True,         
            'crm_alias_prefix': 'contact',          
        })
        config.set_values()
       
    except Exception as e:
        _logger.error("CRM Auto Config [post_init_hook] Erreur : %s", e)
