# © 2026 Sylvain Fotso
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.html).
{
    'name': 'CRM - Configuration et automatisation',
    'summary': 'Configuration automatique CRM, rappel opportunités inactives et restriction du revenu espéré.',
    'description': """
        Ce module regroupe quatre fonctionnalités CRM personnalisées :
        - Ajout d’un champ regroupant les emails des membres de l’équipe commerciale.
        - Chef d’équipe automatiquement ajouté comme membre de son équipe.
        - Création automatique des équipes Support Technique, Ventes et SAV (SAV filtré emails partenaires authentifiés).
        - Activation automatique des paramètres CRM requis à l’installation.
        - Notification automatique après 10 jours sans évolution d’une opportunité en brouillon.
        - Champ “Revenu espéré” visible uniquement pour les Administrateurs des ventes (Kanban, Liste, Formulaire).
        - Attribution automatique des pistes web à l’équipe Ventes (website_crm).
    """,
    'author': 'Sylvain Fotso',
    'website': 'http://www.yourcompany.com',
    'license': 'AGPL-3',
    'category': 'CRM',
    'version': '14.0.1.0.0',
    'depends': ['base', 'crm', 'website_crm'],
    'data': [
        'views/crm_team_views.xml',
        'views/crm_lead_expected_revenue_security_views.xml',
        'data/crm_team_data.xml',
        'data/crm_config_settings.xml',
        'data/ir_cron_data.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}