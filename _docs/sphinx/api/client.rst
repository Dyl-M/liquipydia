Client
======

The main entry point for interacting with the Liquipedia API.

After construction, access data through resource attributes (e.g. ``client.players``,
``client.matches``). See :doc:`resources` for the full list.

.. autoclass:: liquipydia.LiquipediaClient
   :members: __init__, close, __enter__, __exit__

Low-level methods
-----------------

These methods are used internally by resource classes. You typically don't need to call them
directly — use the resource ``list()`` and ``paginate()`` methods instead.

.. automethod:: liquipydia.LiquipediaClient.get
   :no-index:

.. automethod:: liquipydia.LiquipediaClient.paginate
   :no-index:
