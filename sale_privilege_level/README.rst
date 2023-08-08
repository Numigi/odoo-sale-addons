Sale Privilege Level
=====================
This module adds privilege levels on partners.

.. contents:: Table of Contents

Overview
--------
This module adds the concept of a privilege level and allows to select a privilege level on a partner.

However, it does not define how the privilege level is used.

See modules ``sale_privilege_level_payment`` and ``sale_privilege_level_delivery`` for examples of usage.

Configuration
-------------
As ``Partner Manager``, I notice a new menu entry ``Contacts / Configuration / Privilege Levels``.

.. image:: static/description/privilege_level_menu.png

When I click on this menu entry, I find the list of privilege levels.

.. image:: static/description/privilege_level_list.png

Partners
--------
On the form view of a partner, I can select a single privilege level.

.. image:: static/description/partner_form.png

In the list view of partner, I see the column ``Privilege Level``

.. image:: static/description/privilege_level_on_list_view.png

I can see that the ``Privilege Level`` field is avalaible on search panel.

.. image:: static/description/search_by_privilege_level.png

The group by on ``Privilege Level`` field is also available on list view.

.. image:: static/description/group_by_privilege_level.png

Default Privilege Level
-----------------------
It is possible to define a default privilege level for new partners.

.. image:: static/description/default_privilege_level.png

When a partner is created on user signup, this privilege level is automatically assigned.

This setting is customizable per company.

Related Company
---------------

Behavior when default level set
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
CONFIGURATION

As a Super User, I go to ``Sales > Configuration > Settings`` and set the privilege level ``Level 1`` as the default level for all new contacts.

.. image:: static/description/configuration_with_default_privilege_level.png

CREATION WITH NO RELATED COMPANY + ADD LATER RELATED COMPANY 

As a user with access to Contacts, I create a new ``Contact``.

I see that a the default privilege level is assigned to my new contact.

.. image:: static/description/contact_1_privilege_level.png

I save. I edit the Contact and assign it a related company (which has a “Level 2” privilege level) then I save.

.. image:: static/description/contact_1_related_company.png

.. image:: static/description/company_1_privilege_level_on_contact_1.png


From the list view of the contacts or if I export the field, I see that the privilege level has changed to the right value.

.. image:: static/description/contact_1_export.png


CREATION WITH RELATED COMPANY

As a user with access to contacts, I create a Contact, assign it to a Related Company (which has an initial privilege level) and save.

.. image:: static/description/contact_2_related_company.png

From the list view of the contacts or if I export the ``Privilege Level`` field, I see that the privilege level has the right value.

.. image:: static/description/contact_2_export.png


Behavior when default level NOT set
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

CONFIGURATION

As Super User, I go to ``Sales > Configuration > Settings`` and make sure the ``Privilege Level field`` is empty.

.. image:: static/description/configuration_without_default_privilege_level.png


CREATION WITH NO RELATED COMPANY + ADD LATER RELATED COMPANY

As a user with access to contacts, I create a Contact.

I see that the ``Privilege Level`` is empty.

.. image:: static/description/contact_3_no_privilege_level.png

I assign a new privilege level and save.

.. image:: static/description/contact_3_updated_with_privilege_level.png

I edit the contact and assign it a Related Company (which has a different privilege level) then I save.

.. image:: static/description/contact_3_updated_related_company.png

From the list view of the contacts or if I export the ``Privilege Level`` field, I see that the privilege level has the right value.

.. image:: static/description/contact_3_updated_export.png


CREATION WITH RELATED COMPANY

As a user with access to Contacts, I create a Contact, assign it to a Related Company (which has a different privilege level) and save.

.. image:: static/description/contact_4_related_company.png

From the list view of the contacts or if I export the ``Privilege Level`` field, I see that the privilege level has the right value.

.. image:: static/description/contact_4_export.png

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)

More information
----------------
* Meet us at https://bit.ly/numigi-com
