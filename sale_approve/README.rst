===========================================
Approve sales before the confirmation stage
===========================================

This module adds an option to enable two steps validation.

If a salesperson creates a sale order which is a certain amount,
the sale order will be set to "To approve" state and will require a Sales manager
to approve it.

This module is based on the purchase option for two levels validation in module `purchase`.
This module is migrated from the OCA module available on `v12.0 <https://github.com/OCA/sale-workflow/tree/12.0/sale_double_validation>`_.

**Table of contents**

.. contents::
   :local:

Configuration
=============

To configure this module, you need to:

* Go to company form
* Open Configuration tab
* Enable "Levels of Approvals"
* Set the value at which you want to ask for validation in "Double validation amount"
  (0.0 means always)


Usage
=====

Once configured sales continue to create Sale orders just as normal.
If a review is required the SO will be set into the state "To Approve" when approved it will be moved into "Draft".

A sale order in "To approve" state will have a button "Approve" only visible to sales manager.


Credits
=======

Authors
~~~~~~~

* Camptocamp
* Numigi

Contributors
~~~~~~~~~~~~
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)