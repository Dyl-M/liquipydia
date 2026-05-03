Client
======

The main entry point for interacting with the Liquipedia API.

A ``LiquipediaClient`` instance owns a single ``httpx`` session and exposes one resource attribute
per LPDB v3 data type (e.g. ``client.players``, ``client.matches``). See :doc:`resources` for the
full list and per-resource details.

Use the client as a context manager — the ``with`` block guarantees the HTTP session is closed
on exit, including when exceptions propagate.

.. autoclass:: liquipydia.LiquipediaClient
   :members: __init__, close

Direct HTTP access
------------------

The methods below are public and resource classes call them internally. You only need them when
hitting an endpoint that the resource layer does not yet model, or when implementing your own
``Resource`` subclass.

.. automethod:: liquipydia.LiquipediaClient.get
   :no-index:

.. automethod:: liquipydia.LiquipediaClient.paginate
   :no-index:
