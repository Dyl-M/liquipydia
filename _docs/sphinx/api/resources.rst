Resources
=========

Resource classes wrap individual LPDB v3 endpoints. Each resource is accessible as an attribute on
:class:`~liquipydia.LiquipediaClient`.

Base class
----------

.. autoclass:: liquipydia.Resource
   :members: list, paginate

Standard resources
------------------

These resources inherit ``list()`` and ``paginate()`` from ``Resource`` without modifications.

.. autoclass:: liquipydia.BroadcastersResource

.. autoclass:: liquipydia.CompaniesResource

.. autoclass:: liquipydia.DatapointsResource

.. autoclass:: liquipydia.ExternalMediaLinksResource

.. autoclass:: liquipydia.PlacementsResource

.. autoclass:: liquipydia.PlayersResource

.. autoclass:: liquipydia.SeriesResource

.. autoclass:: liquipydia.SquadPlayersResource

.. autoclass:: liquipydia.StandingsEntriesResource

.. autoclass:: liquipydia.StandingsTablesResource

.. autoclass:: liquipydia.TeamsResource

.. autoclass:: liquipydia.TournamentsResource

.. autoclass:: liquipydia.TransfersResource

Specialized resources
---------------------

MatchResource
^^^^^^^^^^^^^

Inherits ``list()`` and ``paginate()`` from ``Resource``. The ``rawstreams`` and ``streamurls``
parameters are only meaningful on this endpoint.

.. autoclass:: liquipydia.MatchResource

TeamTemplateResource
^^^^^^^^^^^^^^^^^^^^

Different API signature — uses ``get()`` instead of ``list()``.

.. autoclass:: liquipydia.TeamTemplateResource
   :members: get

TeamTemplateListResource
^^^^^^^^^^^^^^^^^^^^^^^^

Different API signature — uses ``pagination`` parameter instead of ``limit``/``offset``.

.. autoclass:: liquipydia.TeamTemplateListResource
   :members: list
