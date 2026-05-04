Exceptions
==========

All exceptions raised by liquipydia inherit from :class:`~liquipydia.LiquipediaError`. Catch the
base class to handle every library failure with a single ``except``, or catch specific subclasses
when you want to react differently per failure mode.

Hierarchy
---------

.. code-block:: text

   LiquipediaError              # base — catch this for any library error
   ├── AuthError                # HTTP 403: invalid or missing API key
   ├── NotFoundError            # HTTP 404: requested data does not exist
   ├── RateLimitError           # HTTP 429: retries exhausted (carries retry_after)
   └── ApiError                 # API responded 2xx but the body contains an error array

Other transport-level failures (non-2xx responses without a dedicated subclass, malformed JSON,
unexpected response shapes) are raised as the bare :class:`~liquipydia.LiquipediaError`.

Reference
---------

.. autoexception:: liquipydia.LiquipediaError
   :members:

.. autoexception:: liquipydia.AuthError
   :members:

.. autoexception:: liquipydia.NotFoundError
   :members:

.. autoexception:: liquipydia.RateLimitError
   :members:

.. autoexception:: liquipydia.ApiError
   :members:
