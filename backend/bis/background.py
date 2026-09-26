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
import time
from concurrent.futures import ThreadPoolExecutor
from functools import wraps

from django.conf import settings
from django.db import close_old_connections
from django.db.utils import InterfaceError, OperationalError

logger = logging.getLogger(__name__)

# Connection-level driver errors (Postgres restart mid-task, idle kill): almost
# always transient, and a dropped background task is lost work.
CONNECTION_ERRORS = (InterfaceError, OperationalError)

RETRY_DELAY_SECONDS = 2

_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="bis-background")


def closes_db_connection(fn):
    """Release the thread's database connection once fn returns.

    Django closes connections on the request_finished signal, which never fires
    on a background thread, so its connection stays in the thread local for the
    life of the thread. One broken by a database restart then poisons every
    later call on that thread, and a thread that exits without closing leaks its
    connection to the server instead of returning it.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        finally:
            close_old_connections()

    return wrapper


def run_in_background(fn, *args, **kwargs):
    @closes_db_connection
    def attempt():
        fn(*args, **kwargs)

    def run():
        try:
            attempt()
        except CONNECTION_ERRORS as exc:
            logger.warning(
                f"background task {fn.__name__} failed with a connection error, "
                f"retrying once: {exc}"
            )
            time.sleep(RETRY_DELAY_SECONDS)
            try:
                attempt()
            except Exception:
                logger.exception(f"background task {fn.__name__} failed")
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
