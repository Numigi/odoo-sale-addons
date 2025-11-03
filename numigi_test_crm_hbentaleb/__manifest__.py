{
    "name": "CRM Custom ",
    "version": "14.0.1.0.0",
    "author": "Houda BENTALEB",
    "summary": "Ajouter des améliorations aux fonctionnalités de module CRM.",
    "category": "Sales/CRM",
    "description": "",
    "depends": [
        "website_crm",
    ],
    "data": [
        # views
        "views/crm_team_views.xml",
        "views/crm_lead_views.xml",
        # data
        "data/crm_team_data.xml",
        "data/ir_cron.xml",
    ],
    "post_init_hook": "_set_configuration",
    "application": False,
}
