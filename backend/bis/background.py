"""Process-wide single-worker background queue.

Submitted callables run on one worker thread, in submission order, off the
request/response path. Use for best-effort side effects (external API calls)
whose failure is non-fatal: the result is not awaited and exceptions are
logged, not raised.

The worker is non-daemon, so concurrent.futures joins the queue at normal
interpreter exit — pending work still runs after a request finishes or a
management command returns. Only an abrupt kill (SIGKILL, OOM) drops it.
"""

import logging
from concurrent.futures import ThreadPoolExecutor
from functools import wraps

from django.conf import settings

logger = logging.getLogger(__name__)

_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="bis-background")


def run_in_background(fn, *args, **kwargs):
    def run():
        try:
            fn(*args, **kwargs)
        except Exception:
            logger.exception(f"background task {fn.__name__} failed")

    _executor.submit(run)


def in_background(fn):
    """Run the decorated function off the request path in prod; synchronous elsewhere.

    Only for best-effort, fire-and-forget work whose result the caller doesn't
    use. Kept synchronous outside prod so dev and (transaction-wrapped) tests
    keep their current ordering and surface errors directly.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        if settings.ENVIRONMENT == "prod":
            run_in_background(fn, *args, **kwargs)
        else:
            fn(*args, **kwargs)

    return wrapper
