Sale XML-RPC Compatible
=======================

.. contents:: Table of Contents

Context
-------
Odoo uses XML-RPC as solution to expose its API.

It exposes all object methods that are not prefixed with a underscore.

However, when a method returns ``None``, it fails to properly create the HTTP response
and the request end up in error.

In such case, you end up with a stack trace such as:

[ERROR] XmlRpcFaultException :
Server returned a fault exception: [1] Traceback (most recent call last):
  File "/home/odoo/src/odoo/odoo/addons/base/controllers/rpc.py", line 88, in xmlrpc_2
    response = self._xmlrpc(service)
  File "/home/odoo/src/odoo/odoo/addons/base/controllers/rpc.py", line 69, in _xmlrpc
    return dumps((result,), methodresponse=1, allow_none=False)
  File "/usr/lib/python3.8/xmlrpc/client.py", line 968, in dumps
    data = m.dumps(params)
  File "/usr/lib/python3.8/xmlrpc/client.py", line 501, in dumps
    dump(v, write)
  File "/usr/lib/python3.8/xmlrpc/client.py", line 523, in __dump
    f(self, value, write)
  File "/usr/lib/python3.8/xmlrpc/client.py", line 527, in dump_nil
    raise TypeError("cannot marshal None unless allow_none is enabled")
TypeError: cannot marshal None unless allow_none is enabled

Overview
--------
This module modifies the method update_prices on sale.order to return True instead of None.

Therefore, the method can be called with xmlrpc.

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)
