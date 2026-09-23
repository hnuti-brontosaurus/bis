"""
MCP (Model Context Protocol) tools for BIS.

Single GraphQL-based tool for BIS data analysis.
The LLM writes GraphQL queries to select exactly the fields it needs.
Export mode sends full XLSX (with PII) to the authenticated user's email.
"""

import logging
from concurrent.futures import ThreadPoolExecutor

from bis.background import closes_db_connection
from django.utils.text import get_valid_filename
from mcp_server import MCPToolset
from other.models import SavedFile

logger = logging.getLogger(__name__)


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
    except Exception as e:
        logger.exception(f"Error exporting {name} to email: {e}")


_export_executor = ThreadPoolExecutor(max_workers=1)


class BISTools(MCPToolset):
    """BIS data analysis via GraphQL."""

    def query(
        self,
        query: str,
        variables: dict | None = None,
        export: bool = False,
        export_name: str | None = None,
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

        Returns:
            Query result dict, or confirmation message when export=True.
        """
        try:
            return self._execute_query(query, variables, export, export_name)
        except Exception as e:
            logger.exception("MCP query error")
            return f"Error: {type(e).__name__}: {e}"

    def _execute_query(self, query, variables, export, export_name):
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
            user_email = self.request.user.email
            if not user_email:
                return "Error: No email address on your account."

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
