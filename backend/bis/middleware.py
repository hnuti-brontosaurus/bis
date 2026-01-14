import logging

from django.db import connection
from django.utils.timezone import now


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
