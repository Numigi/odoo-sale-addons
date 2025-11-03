# Numigi Test CRM Ouasmi

## Sujet

Ce module a été développé dans le cadre du test technique Numigi 
Il étend le module **CRM** standard d’Odoo afin d’améliorer la gestion et le suivi des opportunités

---

## Fonctionnalités 

### 1. Calcul automatique des emails des membres
Un champ calculé `emails` concatène automatiquement les emails des membres d’une équipe, pour faciliter les notifications et les échanges internes.

---

### 2. Synchronisation automatique du responsable d’équipe
Lorsqu’un **responsable d’équipe (user_id)** est défini sur une équipe (`crm.team`), il est automatiquement ajouté dans les membres de cette équipe :
- À la **création**
- Lors d’une **modification**
- Lors d’un **changement via l’interface utilisateur**

---

###  3. Création automatique de trois équipes commerciales
Lors de l’installation du module, trois équipes CRM sont automatiquement créées et rattachées à la société existante :

| Équipe |
|--------|
| **Équipe Support Technique** |
| **Équipe Ventes** |
| **Équipe SAV** |

Ces équipes sont définies dans le fichier `data/crm_team_data.xml` et associées à la société principale (`res.company` existante).

---

### 4. Activation automatique de la gestion des pistes et des emails
Lors de l’installation du module :
- Les options **“Utiliser les pistes (Leads)”** et **“Générer les leads à partir des emails”** sont automatiquement activées.
- Cette configuration est effectuée via un **hook post-installation** (`post_init_hook`).

---

### 5. Notification automatique des opportunités dormantes
Une tâche planifiée (cron) notifie automatiquement les membres des équipes CRM lorsqu’une opportunité reste **inactive ou non mise à jour depuis plus de 10 jours**.

- Notification par message interne (mail.message)
- Lien direct vers l’opportunité concernée
- Déclenchée par un cron (`crm_lead_cron.xml`)

### 6. Restriction du champ “Revenu espéré”
Le champ **“Revenu espéré”** sur les opportunités (`expected_revenue`) est désormais visible **uniquement pour les utilisateurs appartenant au groupe “Administrateur des ventes”**.

---

### 7. Attribution automatique d’équipe sur formulaire web
Les leads créés via le site web sont automatiquement associés à l’équipe **“Équipe Ventes”**.


## Actiond planifiées (Cron)

Fichier : `data/crm_lead_cron.xml`

- **Nom** : Notification des opportunités inactives  
- **Modèle** : `crm.lead`  
- **Méthode appelée** : `notify_stale_opportunities`  
- **Fréquence** : quotidienne

---

