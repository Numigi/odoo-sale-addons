==================================
Numigi Test CRM – EL SAILI Chama
==================================

This module provides several custom enhancements to the Odoo CRM application,
implemented as part of a technical evaluation.  
It introduces team-level utilities, business rules, UI restrictions, and
website-to-CRM routing improvements.

🌟 Features
============

The module implements the following functionalities:

    1. Display team members’ emails in a single field.
    -------------------------------------------------

    A computed field ``emails`` is added to the sales team model.  
    It lists the email addresses of all team members, separated by commas.

        .. figure:: static/description/membre_emails.png
            :alt: Emails for team members
            :width: 400px

    2. Automatically include the team leader as a member.
    -----------------------------------------------------

    Whenever a team leader is assigned in Odoo, the user is automatically added to
    the team’s members list to ensure consistency.

        .. figure:: static/description/team_leader.png
            :alt: Team leader
            :width: 400px

    3. creation of three sales teams : Technical Support Team, Sales Team and SAV team.

       The SAV Team must have a pipeline that only accepts emails from authenticated partners.

        .. figure:: static/description/three_team.png
            :alt: Three sales teams
            :width: 400px
        
        .. figure:: static/description/authentificated_partners.png.png
            :alt: Authentificated partners for SAV team
            :width: 400px

    4. Enable specific CRM configuration options at installation.
    ------------------------------------------------------------

    Upon installation, the module automatically activates CRM settings such as
    lead management and incoming email handling.

        .. figure:: static/description/settings_crm.png
            :alt: CRM configuration
            :width: 400px

    5. Notify team members when an opportunity remains in draft for over 10 days.
    ----------------------------------------------------------------------------

    A scheduled action checks for opportunities that have stayed in the *draft*
    stage for more than 10 days. If found, a notification is sent to all members
    of the corresponding sales team.
        .. figure:: static/description/reminder_for_opportunity.png
            :alt: Reminder for opportunity
            :width: 400px

    6. Restrict the visibility of “Expected Revenue” across all views.
    -----------------------------------------------------------------

    The *Expected Revenue* fields is visible only to users in the **Sales Administrator** group.  
    It is hidden in:

    - Form views
    - List views  
    - Kanban views    

        .. figure:: static/description/expected_income_form_view.png
            :alt: Form view
            :width: 400px

        .. figure:: static/description/expected_income_tree_view.png
            :alt: Kanban view
            :width: 400px

        .. figure:: static/description/expected_income_kanban_view.png
            :alt: List view
            :width: 400px

    7. Automatically assign website leads to the Sales Team.
    -------------------------------------------------------

    Leads created through the Website Contact Form (Opportunity form) are
    automatically assigned to the *Sales Team* by default, ensuring consistent
    routing of web-originated leads.

        .. figure:: static/description/form_website.png
            :alt: Form website
            :width: 400px

        .. figure:: static/description/assign_lead_to_sales_team.png
            :alt: Assign lead to sales team
            :width: 400px

Credits
=======

Developed by EL SAILI as part of the Numigi technical assessment.
