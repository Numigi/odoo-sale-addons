# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Personnalisation du module CRM",
    "version": "1.0.0",
    "author": "MINOUMISSEK CEDRIGUE CLAUVIS",
    "maintainer": "MINOUMISSEK CEDRIGUE CLAUVIS",
    "website": "https://www.linkedin.com/in/cedrigue-clauvis-minoumissek-990893103",
    "license": "AGPL-3",
    "category": "Sales",
    "summary": "",
    "depends": ["crm","website_crm"],
    "data": [
        "views/crm_team.xml",
        "views/crm_lead_views.xml",

        'data/data_crm_team.xml',
        'data/data_res_config.xml',
        'data/service_cron.xml',

        ],
    "installable": True,
}