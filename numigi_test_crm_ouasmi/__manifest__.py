# -*- coding: utf-8 -*-
{
    "name": "Numigi Test CRM OUASMI",
    "version": "14.0.1.0.0",
    "category": "CRM",
    "author": "OUASMI Anas",
    "license": "AGPL-3",
    "depends": ["crm", "website_crm", "mail"],
    "data": [
        #"security/security.xml",
        "data/crm_team_data.xml",
        "data/crm_lead_cron.xml",
        "views/crm_team_views.xml",
        "views/crm_lead_views.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "application": False,
    "auto_install": False,
}
