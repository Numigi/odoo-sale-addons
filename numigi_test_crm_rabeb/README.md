# Numigi Test CRM - Personnalisation CRM

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Odoo](https://img.shields.io/badge/Odoo-14.0-875A7B.svg)](https://www.odoo.com/)

## Contexte

Module développé dans le cadre du test technique Numigi pour démontrer l'expertise en personnalisation Odoo 14. Ce module améliore et automatise les processus du CRM en se concentrant sur la gestion des équipes commerciales et le suivi des opportunités.

## Description

Ce module apporte cinq personnalisations essentielles au CRM Odoo :

1. **Emails consolidés des membres** - Champ calculé affichant tous les emails des membres d'une équipe
2. **Chef d'équipe auto-membre** - Ajout automatique du responsable dans la liste des membres
3. **Notifications d'opportunités stagnantes** - Alertes automatiques après 10 jours d'inactivité
4. **Restriction du revenu espéré** - Visibilité limitée aux administrateurs des ventes
5. **Assignation automatique web** - Attribution des pistes web à l'équipe de vente

## Utilisation

### Configuration initiale

Trois équipes commerciales sont créées automatiquement à l'installation :

| Équipe | Règle d'assignation |
|--------|---------------------|
| Équipe Support Technique | Aucune règle spécifique |
| Équipe Ventes | Reçoit les pistes web automatiquement |
| Équipe SAV | Accepte uniquement les emails authentifiés |

### Consulter les emails consolidés

1. Naviguer vers **CRM > Configuration > Équipes Commerciales**
2. Ouvrir une équipe existante
3. Le champ **Emails des membres** affiche toutes les adresses séparées par des virgules

![Champ Emails des membres](https://i.postimg.cc/C5QGxTZj/adresses-membres.png)

### Gestion du revenu espéré

Le champ **Revenu espéré** est visible uniquement pour le groupe **Administrateur des ventes** (`sales_team.group_sale_manager`).

![Vue group Administrateur des ventes](https://i.postimg.cc/rsRx9WST/vente-admin.png)
**Vue Kanban Administrateur :**

![Vue Kanban Administrateur](https://i.postimg.cc/fLmzt9ST/kanban-crm-admin.png)

**Vue Kanban - Utilisateur standard :**

![Vue Kanban Utilisateur](https://i.postimg.cc/gcsLcCvC/kanban-crm.png)

**Vue Formulaire :**

![Vue Formulaire](https://i.postimg.cc/nVmjBsft/form-crm.png)

**Vue Liste :**

![Vue Liste](https://i.postimg.cc/nhGq7X7Q/list-crm-vue.png)

### Notifications automatiques

Les opportunités inactives depuis plus de 10 jours génèrent une alerte dans le chatter :

![Notification d'alerte](https://i.postimg.cc/SK8W8cfx/notification-alert.png)

### Formulaire web

Les pistes créées via le formulaire **Contact Form** sont automatiquement assignées à l'**Équipe Ventes**.

**Note :** Nécessite l'installation du module `website_crm`.

## Détails techniques

### Emails consolidés

**Modèle :** `crm.team`

**Implémentation :** Champ calculé (`member_emails`) qui concatène les adresses email de tous les membres de l'équipe, séparées par des virgules.

### Chef d'équipe auto-membre

**Modèle :** `crm.team`

**Implémentation :** Méthode `create()` et `write()` surchargées pour ajouter automatiquement le responsable (`user_id`) à la liste des membres (`member_ids`).

### Notifications d'opportunités stagnantes

**Modèle :** `crm.lead`

**Déclencheur :** Action planifiée exécutée quotidiennement

**Condition :** Opportunité au statut "Nouveau" depuis plus de 10 jours

**Action :** Envoi d'un message dans le chatter de l'opportunité alertant l'équipe assignée

**Message :** *"Cette opportunité est inactive depuis 10 jours. Veuillez prendre des mesures."*

### Restriction du revenu espéré

**Modèle :** `crm.lead`

**Implémentation :** Attribut `groups="sales_team.group_sale_manager"` ajouté au champ `expected_revenue` dans les vues :
- Vue Kanban (`crm.crm_lead_view_kanban`)
- Vue Formulaire (`crm.crm_lead_view_form`)
- Vue Liste (`crm.crm_case_tree_view_oppor`)

### Assignation automatique web

**Modèle :** `crm.lead`

**Prérequis :** Module `website_crm` installé

**Implémentation :** Surcharge du contrôleur web pour assigner automatiquement `team_id` à l'équipe "Équipe Ventes" lors de la création d'une piste via le formulaire web.

## Prérequis

- Odoo 14.0
- Module `crm` (standard)
- Module `sales_team` (standard)
- Module `website_crm` (optionnel, pour l'assignation web)

## Installation

1. Placer le module dans le répertoire `addons` de votre instance Odoo 14
2. Mettre à jour la liste des applications : **Apps > Update Apps List**
3. Rechercher "Numigi Test CRM"
4. Cliquer sur **Install**

## Licence

Ce module est distribué sous licence **AGPL v3**.