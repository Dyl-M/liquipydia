Response
========

Every successful API call returns an :class:`~liquipydia.ApiResponse`. It is an immutable
dataclass holding the raw response payload — the resource layer leaves parsing into Pydantic
models to the caller, so you can opt in or out per query.

.. code-block:: python

   from liquipydia import LiquipediaClient, Player

   with LiquipediaClient("my-app") as client:
       response = client.players.list("dota2", limit=5)

       # response.result is a list of dicts; convert to typed models when you need them
       players = [Player.model_validate(record) for record in response.result]

       # response.warnings carries non-fatal API warnings (always a list, possibly empty)
       for warning in response.warnings:
           print(f"[liquipedia] {warning}")

.. autoclass:: liquipydia.ApiResponse
   :no-members:
