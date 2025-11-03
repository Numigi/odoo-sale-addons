================================
CRM Custom
================================
Le module permet d'ajouter des améliorations aux fonctionnalités de module CRM.

Les points traités par ce module:

* L'ajout de champ "Emails" dans l'objet crm.team
       .. image:: hb_crm_custom/static/description/1.png
          :class: img-responsive
          :align: center
          :width: 80%

* Le chef d’équipe est toujours un membre de l’équipe.
       .. image:: hb_crm_custom/static/description/2.png
          :class: img-responsive
          :align: center
          :width: 80%

.. note::
       Je n'ai pas ajouté le cas de la suppression automatique de membre si l'utilisateur change le responsable de l'équipe ,
       car ce responsable pouvait être un membre avant d'être le responsable.


* Création de trois équipes commerciales attachées à la société existante.
       .. image:: hb_crm_custom/static/description/3.png
          :class: img-responsive
          :align: center
          :width: 80%

- L'équipe SAV doit avoir pipeline cochée avec accepter les emails des partenaires authentifiés seulement:

       .. image:: hb_crm_custom/static/description/3_1.png
          :class: img-responsive
          :align: center
          :width: 80%

* Les paramètres de configuration suivantes sont cochées à l’installation:
       .. image:: hb_crm_custom/static/description/4.png
          :class: img-responsive
          :align: center
          :width: 80%

* Un cron faisant l'envoie des notifications à tous les membres de l'équipe si une opportunité dépasse plus de 10 jours de sa création sans passer à un autre statut que Nouveau:
       .. image:: hb_crm_custom/static/description/5.png
          :class: img-responsive
          :align: center
          :width: 80%

- La notification créée:

       .. image:: hb_crm_custom/static/description/5_1.png
          :class: img-responsive
          :align: center
          :width: 80%

* Le champ “Revenu espéré” est invisible sur toutes les vues de piste et opportunité si l'utilisateur n'appartient pas au groupe "Administrateur des ventes".
       Vue Kanban:

       .. image:: hb_crm_custom/static/description/6_1.png
          :class: img-responsive
          :align: center
          :width: 80%

       Vue Formulaire:

       .. image:: hb_crm_custom/static/description/6_2.png
          :class: img-responsive
          :align: center
          :width: 80%

       .. image:: hb_crm_custom/static/description/6_2_1.png
          :class: img-responsive
          :align: center
          :width: 80%


       Vue Liste:

       .. image:: hb_crm_custom/static/description/6_3.png
          :class: img-responsive
          :align: center
          :width: 80%

       Vue pivot:

       .. image:: hb_crm_custom/static/description/6_4.png
          :class: img-responsive
          :align: center
          :width: 80%


* La piste créée à partir de formulaire de contact de site web a comme équipe commerciale "Équipe de vente".
       .. image:: hb_crm_custom/static/description/7_1.png
          :class: img-responsive
          :align: center
          :width: 80%

       .. image:: hb_crm_custom/static/description/7_2.png
          :class: img-responsive
          :align: center
          :width: 80%