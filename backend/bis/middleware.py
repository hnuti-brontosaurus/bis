from django.db import connection
from django.utils.timezone import now


def sql_middleware(get_response):
    def middleware(request):
        start = now()
        response = get_response(request)

        sqltime = sum(float(query["time"]) for query in connection.queries)

        print(
            f"Page render {now() - start}: {sqltime=} sec for {len(connection.queries)} queries"
        )
        return response

    return middleware
