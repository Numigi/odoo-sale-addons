# -*- coding: utf-8 -*-
# License AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0).


{
    "name": "Numigi test CRM Chama EL SAILI",
    "version": "14.0",
    "description": "This module offers customizations designed to optimize your CRM management.",
    "author": "Chama",
    "license": "AGPL-3",
    "category": "CRM",
    "depends": ["base_automation", "website_crm"],
    "data": [
        "data/mail_template_data.xml",
        "data/base_automation_data.xml",
        "data/crm_team_data.xml",
        "views/crm_team_views.xml",
        "views/crm_lead_views.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "post_init_hook": "post_init_hook",
}
