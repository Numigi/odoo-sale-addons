{
    "name": "Numigi - Test CRM",
    "version": "14.0.1.0.0",
    "author": "Yamna Azzirari",
    "category": "Sales/CRM",
    "website": "https://www.numigi.fr",
    "license": "AGPL-3",
    "summary": "The Module adds CRM functionalities for Numigi",
    "depends": [
        "crm",
        "website_crm",
    ],
    "data": [
        "data/crm_team_data.xml",
        "data/ir_cron_data.xml",
        "data/config_parameter_data.xml",
        "data/res_groups_data.xml",
        "data/mail_template_data.xml",
        "views/crm_team_views.xml",
        "views/crm_lead_views.xml",
    ],
    "demo": [
        "data/crm_team_demo.xml",
    ],
    "installable": True,
    "auto_install": True,
    "application": True,
}
