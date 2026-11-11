Testing
=======

:mod:`liquipydia.testing` lets you test code that uses liquipydia without network access or an API key.
:class:`~liquipydia.testing.FakeLpdb` is an in-memory LPDB: it serves the records you give it to a **real**
:class:`~liquipydia.LiquipediaClient`, whose network layer only is replaced. Keyword filters, ``query``
validation, pagination, retries, error mapping and model parsing therefore behave exactly as in production.

.. code-block:: python

   from liquipydia import Match
   from liquipydia.testing import FakeLpdb

   def latest_matches(client):
       return [Match.model_validate(r) for r in client.matches.paginate("rocketleague", page_size=2)]

   def test_latest_matches():
       fake = FakeLpdb({"match": [{"match2id": "m1"}, {"match2id": "m2"}, {"match2id": "m3"}]})

       with fake.client() as client:
           matches = latest_matches(client)

       assert [m.match2id for m in matches] == ["m1", "m2", "m3"]
       assert [r.params["offset"] for r in fake.requests] == ["0", "2", "4"]

What the fake reproduces
------------------------

- **Records per endpoint**, keyed by LPDB endpoint name (``"match"``, ``"player"``, ``"teamtemplate"``...);
  an endpoint without records answers an empty page.
- **Paging**: results are sliced by ``limit`` / ``offset``, so ``paginate()`` walks the pages.
- **Field selection**: with ``query``, records keep only the named fields (case-insensitive) plus ``wiki``.
- **Failures**: :meth:`~liquipydia.testing.FakeLpdb.fail` makes an endpoint answer an HTTP error or time out,
  optionally for a limited number of requests, so the client raises its real errors (``RateLimitError``,
  ``NetworkError``, ``NotFoundError``...), after its retries.
- **A request log**: :attr:`~liquipydia.testing.FakeLpdb.requests` lists every request with its endpoint and
  parameters, so tests can check what was asked.

It does **not** evaluate ``conditions`` or keyword filters (every record of the endpoint is returned; check the
request log instead), nor compute ``query`` functions such as ``sum::prizemoney`` (those items are left out).

Reference
---------

.. autoclass:: liquipydia.testing.FakeLpdb
   :members: add, fail, client, requests

.. autoclass:: liquipydia.testing.RecordedRequest
   :no-members:
