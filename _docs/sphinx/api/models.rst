:tocdepth: 3

Models
======

Pydantic models for typed access to API response records. Use ``Model.model_validate(record)``
on dicts from :class:`~liquipydia.ApiResponse`.

All fields are optional (``type | None = None``) for forward compatibility. Unknown API fields
are preserved via ``extra="allow"``.

Type aliases
------------

These handle LPDB API quirks automatically:

- **NullableDate** — converts null sentinels (``"0000-01-01"``, ``""``) to ``None``
- **NullableDatetime** — same for datetime fields (``"0000-01-01 00:00:00"``)
- **LpdbDict** — converts empty API lists (``[]``) to ``None`` for dict-like fields

Base classes
------------

Most models inherit from ``_LpdbModel``, which provides common fields shared across standard
endpoints. Team template models use ``_TeamTemplateBase`` instead (different field set).

.. autoclass:: liquipydia._models._LpdbModel
   :members:
   :inherited-members: BaseModel

.. autoclass:: liquipydia._models._TeamTemplateBase
   :members:
   :inherited-members: BaseModel

Standard models
---------------

.. autoclass:: liquipydia.Broadcaster
   :members:
   :inherited-members: BaseModel

.. autoclass:: liquipydia.Company
   :members:
   :inherited-members: BaseModel

.. autoclass:: liquipydia.Datapoint
   :members:
   :inherited-members: BaseModel

.. autoclass:: liquipydia.ExternalMediaLink
   :members:
   :inherited-members: BaseModel

.. autoclass:: liquipydia.Match
   :members:
   :inherited-members: BaseModel

.. autoclass:: liquipydia.Placement
   :members:
   :inherited-members: BaseModel

.. autoclass:: liquipydia.Player
   :members:
   :inherited-members: BaseModel

.. autoclass:: liquipydia.Series
   :members:
   :inherited-members: BaseModel

.. autoclass:: liquipydia.SquadPlayer
   :members:
   :inherited-members: BaseModel

.. autoclass:: liquipydia.StandingsEntry
   :members:
   :inherited-members: BaseModel

.. autoclass:: liquipydia.StandingsTable
   :members:
   :inherited-members: BaseModel

.. autoclass:: liquipydia.Team
   :members:
   :inherited-members: BaseModel

.. autoclass:: liquipydia.Tournament
   :members:
   :inherited-members: BaseModel

.. autoclass:: liquipydia.Transfer
   :members:
   :inherited-members: BaseModel

Team template models
--------------------

.. autoclass:: liquipydia.TeamTemplate
   :members:
   :inherited-members: BaseModel

.. autoclass:: liquipydia.TeamTemplateList
   :members:
   :inherited-members: BaseModel
