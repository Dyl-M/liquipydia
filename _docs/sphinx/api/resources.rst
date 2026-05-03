Resources
=========

Resource classes wrap individual LPDB v3 endpoints. Each resource is reachable as an attribute on
:class:`~liquipydia.LiquipediaClient`. The resource layer adds three things on top of the raw
HTTP API:

- **Keyword filters** — kwargs like ``nationality="Denmark"`` are turned into
  ``[[nationality::Denmark]]`` and AND-joined with any explicit ``conditions`` string.
- **Filter-key validation** — keys that don't match the resource's Pydantic model raise
  ``ValueError`` before a request goes out.
- **Pagination** — ``paginate()`` yields individual records, transparently fetching successive
  pages.

Base class
----------

All standard endpoints share the same surface, defined on :class:`~liquipydia.Resource`:

.. autoclass:: liquipydia.Resource
   :members: list, paginate

Standard resources
------------------

These 13 resources inherit ``list()`` and ``paginate()`` from :class:`~liquipydia.Resource`
unchanged. They differ only in their endpoint path and the model used for filter-key validation:

.. list-table::
   :header-rows: 1
   :widths: 35 25 25

   * - Class
     - Endpoint
     - Model
   * - :class:`~liquipydia.BroadcastersResource`
     - ``/broadcasters``
     - :class:`~liquipydia.Broadcaster`
   * - :class:`~liquipydia.CompaniesResource`
     - ``/company``
     - :class:`~liquipydia.Company`
   * - :class:`~liquipydia.DatapointsResource`
     - ``/datapoint``
     - :class:`~liquipydia.Datapoint`
   * - :class:`~liquipydia.ExternalMediaLinksResource`
     - ``/externalmedialink``
     - :class:`~liquipydia.ExternalMediaLink`
   * - :class:`~liquipydia.PlacementsResource`
     - ``/placement``
     - :class:`~liquipydia.Placement`
   * - :class:`~liquipydia.PlayersResource`
     - ``/player``
     - :class:`~liquipydia.Player`
   * - :class:`~liquipydia.SeriesResource`
     - ``/series``
     - :class:`~liquipydia.Series`
   * - :class:`~liquipydia.SquadPlayersResource`
     - ``/squadplayer``
     - :class:`~liquipydia.SquadPlayer`
   * - :class:`~liquipydia.StandingsEntriesResource`
     - ``/standingsentry``
     - :class:`~liquipydia.StandingsEntry`
   * - :class:`~liquipydia.StandingsTablesResource`
     - ``/standingstable``
     - :class:`~liquipydia.StandingsTable`
   * - :class:`~liquipydia.TeamsResource`
     - ``/team``
     - :class:`~liquipydia.Team`
   * - :class:`~liquipydia.TournamentsResource`
     - ``/tournament``
     - :class:`~liquipydia.Tournament`
   * - :class:`~liquipydia.TransfersResource`
     - ``/transfer``
     - :class:`~liquipydia.Transfer`

Specialized resources
---------------------

Three resources need their own entry, either because of an extra parameter or a different method
signature.

MatchResource
^^^^^^^^^^^^^

Inherits ``list()`` and ``paginate()`` from :class:`~liquipydia.Resource`. The ``rawstreams`` and
``streamurls`` keyword arguments accepted by the base class are only meaningful on this endpoint;
on any other resource the API ignores them.

.. autoclass:: liquipydia.MatchResource

TeamTemplateResource
^^^^^^^^^^^^^^^^^^^^

Single-template lookup. Uses ``get(wiki, template, date=...)`` — ``conditions``, ``limit``,
``offset``, ``order`` and multi-wiki are not supported. The optional ``date`` parameter returns
the template state at that historical date (useful for rendering era-correct logos on archived
tournament pages).

.. autoclass:: liquipydia.TeamTemplateResource
   :members: get

TeamTemplateListResource
^^^^^^^^^^^^^^^^^^^^^^^^

Bulk template listing. Uses ``list(wiki, pagination=N)`` — page-based navigation, no
``limit``/``offset`` and no multi-wiki. Some result rows can be ``None`` and must be filtered
before validation:

.. code-block:: python

   response = client.team_template_list.list("rocketleague")
   for record in response.result:
       if record is None:
           continue
       template = TeamTemplateList.model_validate(record)

.. autoclass:: liquipydia.TeamTemplateListResource
   :members: list
