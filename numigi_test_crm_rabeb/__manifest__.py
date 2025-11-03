{
    "name": "Numigi Test CRM Rabeb",
    "version": "14.0.1.0.0",
    "category": "Sales/CRM",
    "summary": "Personnalisations Odoo pour le module CRM (Test Technique).",
    "description": """
Implémentation des personnalisations demandées pour le module CRM:
1. Champ emails dans l'équipe commerciale.
2. Le chef d'équipe est automatiquement membre.
3. Création de 3 équipes commerciales.
4. Configuration des paramètres à l'installation.
5. Notification si opportunité reste en 'draft' plus de 10 jours.
6. Visibilité du champ 'Revenu espéré' limitée à Administrateur des ventes.
7. Équipe de vente par défaut pour le formulaire de contact web.
""",
    "author": "Rabeb",
    "license": "AGPL-3",
    "depends": [
        "crm",
        "mail",
        "website_crm",
        "sales_team",
    ],
    "data": [
        "data/crm_team_data.xml",
        "data/ir_cron_data.xml",
        "views/crm_team_views.xml",
        "data/mail_data.xml",
        "views/crm_lead_views.xml",
        'views/assets.xml',
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "auto_install": False,
    "application": False,
}
