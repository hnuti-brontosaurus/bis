from django.db import connection


def sql_middleware(get_response):
    def middleware(request):
        response = get_response(request)

        sqltime = sum(float(query["time"]) for query in connection.queries)

        print(f"Page render: {sqltime} sec for {len(connection.queries)} queries")
        return response

    return middleware
