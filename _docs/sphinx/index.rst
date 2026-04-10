liquipydia
==========

**A modern, typed Python client for the Liquipedia API (LPDB v3).**

liquipydia is a Python client library for the `Liquipedia <https://liquipedia.net/>`_ Database
(LPDB) REST API v3, covering all 16 data types (matches, tournaments, teams, players, transfers,
and more).

Built with `httpx <https://www.python-httpx.org/>`_ and `pydantic <https://docs.pydantic.dev/>`_.

Features
--------

- **Full LPDB v3 coverage** — all 16 data types accessible as client attributes
- **Typed models** — Pydantic models for every data type with IDE autocompletion
- **Automatic pagination** — iterate through results without manual offset management
- **Keyword filters** — Pythonic query syntax instead of raw LPDB condition strings
- **Rate limit handling** — automatic retries with exponential backoff on HTTP 429
- **Context manager** — clean resource management with ``with`` statement

Quick example
-------------

.. code-block:: python

   from liquipydia import LiquipediaClient, Player

   with LiquipediaClient("my-app", api_key="your-api-key") as client:
       response = client.players.list("dota2", pagename="Miracle-")
       for record in response.result:
           player = Player.model_validate(record)
           print(player.name, player.nationality)

.. code-block:: text

   Miracle- Jordan

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   getting-started
   examples

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/client
   api/resources
   api/models
   api/response
   api/exceptions

.. toctree::
   :maxdepth: 1
   :caption: Project

   changelog

Data license
------------

Data returned by the Liquipedia API is subject to
`CC-BY-SA 3.0 <https://creativecommons.org/licenses/by-sa/3.0/>`_ as required by Liquipedia's
`API Terms of Use <https://liquipedia.net/api-terms-of-use>`_.
