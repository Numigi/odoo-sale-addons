# CRM - Configuration et automatisation

**Version** : 14.0.1.0.0
**Auteur** : Sylvain Fotso
**Licence** : [AGPL-3.0](https://www.gnu.org/licenses/agpl-3.0.html)
**Catégorie** : CRM
**Dépendances** : `base`, `crm`, `website_crm`

---

## Présentation

Ce module regroupe sept fonctionnalités CRM personnalisées pour Odoo 14 Enterprise :

1. Champ regroupant les emails des membres de l'équipe commerciale
2. Chef d'équipe automatiquement ajouté comme membre de son équipe
3. Création automatique des équipes Support Technique, Ventes et SAV
4. Activation automatique des paramètres CRM à l'installation
5. Notification automatique après 10 jours sans évolution d'une opportunité
6. Champ Revenu espéré restreint aux Administrateurs des ventes
7. Attribution automatique des pistes web à l'équipe Ventes

---

## Fonctionnalités

### 1. Emails des membres de l'équipe

Le modèle `crm.team` est étendu avec un champ calculé `x_members_emails`
qui concatène les adresses email de tous les membres de l'équipe.

Le champ se recalcule automatiquement lorsque `member_ids` ou leurs emails sont modifiés.

Fichier concerné : `models/crm_team.py`

---

### 2. Chef d'équipe ajouté automatiquement comme membre

Lorsque le responsable (`user_id`) d'une équipe est défini ou modifié,
il est automatiquement ajouté à la liste des membres (`member_ids`)
s'il n'en fait pas déjà partie.

Fichier concerné : `models/crm_team.py`

---

### 3. Création automatique des équipes

À l'installation du module, trois équipes sont créées automatiquement :

| Équipe | Particularité |
|---|---|
| Support Technique | Équipe standard |
| Ventes | Équipe standard |
| SAV | Filtrée sur les emails des partenaires authentifiés uniquement |

Fichiers concernés : `data/crm_team_data.xml`

---

### 4. Activation automatique des paramètres CRM

Déclenché par le `post_init_hook` lors de l'installation du module.

Active automatiquement :
- Les **pistes** (`group_use_lead = True`)
- La génération de pistes depuis les **emails reçus** (`generate_lead_from_alias = True`)
- L'**alias email** préfixe = `contact`

Fichiers concernés : `hooks.py`, `data/crm_config_settings.xml`

---

### 5. Notification automatique des opportunités inactives

Un cron quotidien détecte les opportunités restées en brouillon (première étape)
depuis plus de **10 jours** sans évolution, et envoie une **notification inbox** 🔔
à tous les membres de l'équipe commerciale associée.

Critères de détection :
- `type = opportunity`
- `active = True`
- `probability` entre 1 et 99 (ni gagnée ni perdue)
- `create_date` > 10 jours
- `reminder_sent = False`

Format du message envoyé :
```
Bonjour,
Merci de donner une suite à cette opportunité [Nom ← lien cliquable].
Cordialement.
```

Le champ `reminder_sent` est mis à `True` après envoi pour éviter les doublons.

Fichiers concernés : `models/crm_lead.py`, `data/ir_cron_data.xml`

---

### 6. Restriction du champ Revenu espéré

Le champ `expected_revenue` est restreint au groupe **Administrateur des ventes**
au niveau du modèle, ce qui le masque automatiquement sur toutes les vues :
formulaire, liste et kanban.

Les totaux de colonnes dans la vue kanban sont également masqués
pour les utilisateurs n'appartenant pas à ce groupe.

Fichier concerné : `views/crm_lead_expected_revenue_security_views.xml`

---

### 7. Attribution automatique des pistes web à l'équipe Ventes

Les pistes créées via le formulaire Contact du site web (`website_crm`)
sans équipe définie sont automatiquement attribuées à l'équipe configurée par défaut dans le menu configuration du module CRM.

L'équipe est recherchée dans cet ordre :
1. Paramètre `crm.default_team_id` dans `ir.config_parameter`
2. Champ `crm_default_team_id` dans `res.config.settings`

Fichier concerné : `models/crm_lead.py`

---

## Installation

1. Copier le dossier dans le répertoire des addons Odoo
2. Mettre à jour la liste des modules :
   **Paramètres → Activer le mode développeur → Mettre à jour la liste des applications**
3. Rechercher `numigi_test_crm_sylvain_fotso` et cliquer sur **Installer**

Le `post_init_hook` s'exécute automatiquement à l'installation et configure
les paramètres CRM ainsi que les équipes par défaut.

---

## Structure du module

```
numigi_test_crm_sylvain_fotso/
├── __init__.py
├── __manifest__.py
├── hooks.py                                    
|                                    
├── data/
│   ├── crm_config_settings.xml                       # Paramètres CRM initiaux
│   ├── crm_team_data.xml                             # Création des 3 équipes
│   └── ir_cron_data.xml                              # Cron rappel opportunités
├── models/
│   ├── crm_lead.py                                   # Assignation équipe + rappel
│   └── crm_team.py                                   # Emails membres + ajout chef
├── security/
│   └── ir.model.access.csv
├── tests/
│   ├── __init__.py
│   ├── test_crm_lead.py                              # Tests crm.lead
│   ├── test_crm_team.py                              # Tests crm.team
│   └── test_hooks.py                                 # Tests post_init_hook
└── views/
    ├── crm_lead_expected_revenue_security_views.xml  # Restriction revenu espéré
    └── crm_team_views.xml                            # Vue équipe commerciale
```

---

## Lancer les tests
## Environnement :Pour  Windows 10, Python 3.7.7, pytest-7.4.4, pytest-odoo 0.9.0
## Se placer à la racine du serveur Odoo (C:\odoo14\server) et exécuter :
set PYTHONPATH=C:\odoo14\server
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

C:\odoo14\python\python.exe -m pytest ^
    --odoo-config=chemin_fichier_config ^
    --odoo-database=nom_base ^
    odoo\enterprise-addons\numigi_test_crm_sylvain_fotso\tests\ -v
---

## Licence

Ce module est publié sous licence **AGPL-3.0 or later**.
Voir [https://www.gnu.org/licenses/agpl-3.0.html](https://www.gnu.org/licenses/agpl-3.0.html)

Conformément à cette licence :
- Le code source doit rester accessible à quiconque utilise ce logiciel, y compris via un service web (SaaS)
- Toute modification ou module dérivé doit être publié sous la même licence
- La paternité de l'auteur original doit être préservée