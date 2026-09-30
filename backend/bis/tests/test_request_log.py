import logging

import pytest
from bis.middleware import RequestLogMiddleware
from django.http import Http404, HttpResponse
from django.test import RequestFactory
from django.urls import ResolverMatch
from django.views.static import serve


def view():
    pass


def call(path, resolved_to=view, status=200):
    def get_response(request):
        if resolved_to:
            request.resolver_match = ResolverMatch(resolved_to, (), {}, "event-detail")
        return HttpResponse(status=status)

    request = RequestFactory().get(path, {"search": "Jan Novák"})
    request.resolver_match = None
    RequestLogMiddleware(get_response)(request)
    return request


@pytest.fixture
def log(caplog):
    caplog.set_level(logging.INFO, logger="request")
    return caplog


def test_request_is_logged_by_view_and_status_without_query_values(log):
    call("/api/frontend/events/5/", status=404)

    [record] = log.records
    assert record.getMessage() == "Finished GET request on event-detail with 404"
    assert record.data == {"path": "/api/frontend/events/5/", "query": ["search"]}


def test_unresolved_and_static_requests_are_not_logged(log):
    call("/wp-login.php", resolved_to=None, status=404)
    call("/backend_static/admin.css", resolved_to=serve)

    assert log.records == []


def test_unhandled_exception_is_logged_with_its_traceback(log):
    request = RequestFactory().get("/api/frontend/events/5/")
    request.resolver_match = ResolverMatch(view, (), {}, "event-detail")
    error = Http404("gone")

    RequestLogMiddleware(None).process_exception(request, error)

    [record] = log.records
    assert record.getMessage() == "Failed GET request on event-detail"
    assert record.exc_info[1] is error
