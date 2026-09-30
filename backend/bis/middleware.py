import logging
from time import monotonic

from bis.logs import start_trace
from django.db import connection
from django.utils.timezone import now
from django.views.static import serve

logger = logging.getLogger("request")

# the compose healthcheck asks for the api root every second
HEALTHCHECK = "swagger-ui"


def sql_middleware(get_response):
    def middleware(request):
        start = now()
        response = get_response(request)

        sqltime = sum(float(query["time"]) for query in connection.queries)

        logging.debug(
            "Page render %s: sqltime=%s sec for %d queries",
            now() - start,
            sqltime,
            len(connection.queries),
        )
        return response

    return middleware


class RequestLogMiddleware:
    """Trace every request and log how it ended.

    The view name and the status are closed sets, so they stay in the message;
    the path carries ids and goes to `data`. Query values and bodies are left
    out because that is where people type names and emails.

    A request no url matched is a scanner, and a static file or a healthcheck
    is not work, so none of them is logged; a 404 answered by a real view is.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_trace("request", request)
        start = monotonic()
        response = self.get_response(request)

        match = request.resolver_match
        if match is None or match.func is serve or match.view_name == HEALTHCHECK:
            return response

        # resolves a lazy session user, so the record below carries its id
        getattr(getattr(request, "user", None), "id", None)
        logger.info(
            f"Finished {request.method} request on {match.view_name} "
            f"with {response.status_code}",
            extra={
                "duration": monotonic() - start,
                "data": {"path": request.path, "query": sorted(request.GET)},
            },
        )
        return response

    def process_exception(self, request, exception):
        logger.error(
            f"Failed {request.method} request on {request.resolver_match.view_name}",
            exc_info=exception,
            extra={"data": {"path": request.path}},
        )
