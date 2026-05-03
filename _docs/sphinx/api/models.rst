:tocdepth: 3

Models
======

Pydantic models for typed access to API response records. The client returns raw dicts inside
:class:`~liquipydia.ApiResponse`; convert each one with ``Model.model_validate(record)``:

.. code-block:: python

   from liquipydia import LiquipediaClient, Player

   with LiquipediaClient("my-app") as client:
       response = client.players.list("dota2", limit=5)
       players = [Player.model_validate(record) for record in response.result]

Conventions
-----------

- **All fields are optional** (``type | None = None``). LPDB endpoints can omit fields without
  notice, so models never raise on missing data.
- **Unknown fields are preserved** via ``ConfigDict(extra="allow")``. New API fields are
  accessible on the validated model even before this library is updated.
- **Models are standalone.** They don't reference the client or each other and can be reused for
  any dict that follows the LPDB schema.

Type aliases
------------

Three reusable field types handle LPDB's quirky null-encoding so consumers see clean
``None`` / ``date`` / ``datetime`` / ``dict`` values:

.. autodata:: liquipydia._models.NullableDate
   :no-value:

.. autodata:: liquipydia._models.NullableDatetime
   :no-value:

.. autodata:: liquipydia._models.LpdbDict
   :no-value:

A handful of fields (e.g. ``stream`` on :class:`~liquipydia.Match`, ``earningsbyyear`` on
:class:`~liquipydia.Player`) legitimately vary between dict and list shapes. Those use an
explicit ``dict[str, Any] | list[Any] | None`` union rather than ``LpdbDict``.

Internal base classes
---------------------

The classes below are not part of the public API (they are prefixed with ``_``). They are
documented here only to make field inheritance visible — refer to the concrete model classes for
day-to-day use.

.. autoclass:: liquipydia._models._LpdbModel

.. autoclass:: liquipydia._models._TeamTemplateBase

Standard models
---------------

.. autoclass:: liquipydia.Broadcaster

.. autoclass:: liquipydia.Company

.. autoclass:: liquipydia.Datapoint

.. autoclass:: liquipydia.ExternalMediaLink

.. autoclass:: liquipydia.Match

.. autoclass:: liquipydia.Placement

.. autoclass:: liquipydia.Player

.. autoclass:: liquipydia.Series

.. autoclass:: liquipydia.SquadPlayer

.. autoclass:: liquipydia.StandingsEntry

.. autoclass:: liquipydia.StandingsTable

.. autoclass:: liquipydia.Team

.. autoclass:: liquipydia.Tournament

.. autoclass:: liquipydia.Transfer

Team template models
--------------------

.. autoclass:: liquipydia.TeamTemplate

.. autoclass:: liquipydia.TeamTemplateList
