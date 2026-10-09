"""
MCP (Model Context Protocol) tools for BIS.

Single GraphQL-based tool for BIS data analysis.
The LLM writes GraphQL queries to select exactly the fields it needs.
Export mode sends full XLSX (with PII) to the authenticated user's email; the
bot has to name a recipient who can see all data instead.
A second tool reads the application logs, see bis/logs.py.
"""

import logging
from concurrent.futures import ThreadPoolExecutor

from bis import logs as log_files
from bis.background import closes_db_connection
from bis.models import User
from django.conf import settings
from django.utils.text import get_valid_filename
from mcp_server import MCPToolset
from other.models import SavedFile

logger = logging.getLogger("mcp")


@closes_db_connection
def _export_and_email(queryset, user_email, name):
    """Run do_export_to_xlsx, save to SavedFile, and email the link."""
    from bis import emails
    from xlsx_export.export import do_export_to_xlsx

    try:
        file = do_export_to_xlsx(queryset)
        saved_file = SavedFile.store(file.name, f"{name}.xlsx")
        emails.text(
            [user_email],
            f"Export: {name}",
            f"tu: {saved_file.get_absolute_url()} máš!",
        )
    except Exception:
        logger.exception("Failed MCP export")


_export_executor = ThreadPoolExecutor(max_workers=1)


class BISTools(MCPToolset):
    """BIS data analysis via GraphQL."""

    def query(
        self,
        query: str,
        variables: dict | None = None,
        export: bool = False,
        export_name: str | None = None,
        export_to: str | None = None,
    ) -> dict | str:
        """Execute a GraphQL query against BIS data.

        The schema exposes events, feedbacks, applications, users, memberships,
        donors, donations, opportunities, locations and administration units,
        plus an `aggregate` root for counts and sums. PII (names, emails,
        phones, birthdays, addresses) is excluded; people appear as
        anonymous users with a birth year and region.

        When export=True, all matching data (no limit) is exported as full XLSX
        (including PII) and emailed to you instead of being returned.

        Args:
            query: A GraphQL query string.
            variables: Optional dict of GraphQL variables.
            export: If true, exports matching data as XLSX to your email.
            export_name: File name (without .xlsx) and email subject of the
                export; defaults to the dataset name.
            export_to: Recipient of the export, required for the bot account
                and only allowed for it. Must be the email of a person who can
                see all data (office, auditors, executives, fundraisers).

        Returns:
            Query result dict, or confirmation message when export=True.
        """
        logger.info(
            "Received MCP query",
            extra={"data": {"query": query, "variables": variables, "export": export}},
        )
        try:
            return self._execute_query(query, variables, export, export_name, export_to)
        except Exception as e:
            logger.exception("Failed MCP query")
            return f"Error: {type(e).__name__}: {e}"

    def logs(
        self,
        since: str | None = None,
        until: str | None = None,
        level: str = "INFO",
        message: str | None = None,
        text: str | None = None,
        filters: dict | None = None,
        exclude: dict | None = None,
        group_by: list[str] | None = None,
        limit: int = 100,
        offset: int = 0,
        tracebacks: bool = False,
    ) -> list | str:
        """Search the BIS application logs. Superusers and the bot only.

        Each record has: time, level, logger, message, request_id, user_id,
        duration (seconds), data (a dict), traceback. People appear by id only.

        The message is a fixed phrase, optionally ending in a value from a
        small set, so search by phrase: "Finished GET request on", "Sent
        email", "Logged in". Longer operations log "Started X" / "Finished X" /
        "Failed X"; a logged exception appends its class ("Failed job
        call_command sync_ecomail: HTTPError") and puts its text in data.error.
        Everything logged while serving one request, or during one scheduled
        run, shares a request_id. Loggers: `request` (one line per HTTP
        request), `mcp`, `root` (everything else).

        Start with group_by to see what exists, e.g. group_by: ["message"],
        or group_by: ["day", "level"].

        Args:
            since: ISO datetime, Prague time unless it has an offset.
                Defaults to 24 hours before `until`.
            until: ISO datetime, defaults to now.
            level: Minimal level: INFO, WARNING, ERROR or CRITICAL.
            message: Case-insensitive substring of the message.
            text: Case-insensitive substring anywhere in the record.
            filters: Exact matches by dotted path; a list means any of, e.g.
                {"user_id": 12, "data.template_id": [162, 163]}.
            exclude: Same shape as filters; drops matching records, e.g.
                {"logger": "request"}.
            group_by: Paths to count records by instead of listing them; also
                accepts `hour` and `day`. Returns the counts, largest first.
            limit: At most 1000 records, newest first.
            offset: Records to skip, for paging.
            tracebacks: Include the traceback field, which is long.

        Returns:
            A list of records, or of groups with their `count`.
        """
        user = self.request.user
        if not (user.is_superuser or user.is_bot):
            return "Error: logs are available to superusers only."

        parameters = {
            "since": since,
            "until": until,
            "level": level,
            "message": message,
            "text": text,
            "filters": filters,
            "exclude": exclude,
            "group_by": group_by,
            "limit": limit,
            "offset": offset,
            "tracebacks": tracebacks,
        }
        logger.info(
            "Received MCP logs search",
            extra={"data": {key: value for key, value in parameters.items() if value}},
        )
        try:
            return log_files.search(settings.LOG_DIR, **parameters)
        except Exception as e:
            logger.exception("Failed MCP logs search")
            return f"Error: {type(e).__name__}: {e}"

    def _export_recipient(self, export_to):
        user = self.request.user
        if not user.is_bot:
            if export_to:
                return None, "Error: export_to is only for the bot account."
            if not user.email:
                return None, "Error: No email address on your account."
            return user.email, None

        if not export_to:
            return None, "Error: the bot has to name the recipient in export_to."
        recipient = User.get(email=export_to)
        if not recipient or recipient.is_bot or not recipient.can_see_all:
            return (
                None,
                "Error: export_to must belong to a person who can see all data.",
            )
        return export_to.lower(), None

    def _execute_query(self, query, variables, export, export_name, export_to):
        from bis.mcp_schema import schema

        context = {
            "request": self.request,
            "_export": export,
            "_export_qs": {},
        }
        result = schema.execute_sync(
            query,
            variable_values=variables,
            context_value=context,
        )

        if result.errors:
            messages = []
            for err in result.errors:
                msg = str(err)
                if hasattr(err, "locations") and err.locations:
                    locs = ", ".join(
                        f"line {loc.line} col {loc.column}" for loc in err.locations
                    )
                    msg += f" (at {locs})"
                if hasattr(err, "path") and err.path:
                    msg += f" [path: {'.'.join(str(p) for p in err.path)}]"
                messages.append(msg)
            return "GraphQL errors:\n" + "\n".join(f"- {m}" for m in messages)

        if export:
            user_email, error = self._export_recipient(export_to)
            if error:
                return error

            if not context["_export_qs"]:
                return "No data matched for export."

            datasets = context["_export_qs"]
            names = {
                dataset: get_valid_filename(
                    f"{export_name}_{dataset}"
                    if export_name and len(datasets) > 1
                    else export_name or dataset
                )
                for dataset in datasets
            }
            max_length = SavedFile._meta.get_field("name").max_length - len(".xlsx")
            if any(len(name) > max_length for name in names.values()):
                return f"Error: export_name is too long, use at most {max_length} characters."

            for dataset, queryset in datasets.items():
                _export_executor.submit(
                    _export_and_email, queryset, user_email, names[dataset]
                )

            exported = ", ".join(names.values())
            return f"Exporting {exported}. You will receive an email at {user_email}."

        return result.data


# Append GraphQL schema SDL to MCP server instructions so the LLM knows
# which types and fields are available when writing queries.
from bis.mcp_schema import schema as _schema  # noqa: E402
from mcp_server.djangomcp import global_mcp_server  # noqa: E402

global_mcp_server.append_instructions("GRAPHQL SCHEMA:\n" + _schema.as_str())
