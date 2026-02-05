"""
MCP (Model Context Protocol) tools for BIS.

Single GraphQL-based tool for event and feedback analysis.
The LLM writes GraphQL queries to select exactly the fields it needs.
Export mode sends full XLSX (with PII) to the authenticated user's email.
"""

import logging
from concurrent.futures import ThreadPoolExecutor

from django.conf import settings
from mcp_server import MCPToolset

logger = logging.getLogger(__name__)


def _export_and_email(queryset, user_email, subject_label):
    """Run do_export_to_xlsx, save to SavedFile, and email the link."""
    from bis import emails
    from other.models import SavedFile
    from xlsx_export.export import do_export_to_xlsx

    try:
        file = do_export_to_xlsx(queryset)
        saved_file = SavedFile.objects.create(name=file.name)
        name = f"saved_file_{saved_file.id}.xlsx"
        saved_file.file.save(name, open(file.name, "rb"), save=False)
        emails.text(
            [user_email],
            f"Export: {subject_label}",
            f"tu: {settings.FULL_HOSTNAME}/media/saved_files/{name} máš!",
        )
    except Exception as e:
        logger.exception(f"Error exporting {subject_label} to email: {e}")


_export_executor = ThreadPoolExecutor(max_workers=1)


class BISTools(MCPToolset):
    """BIS event and feedback analysis via GraphQL."""

    def query(
        self,
        query: str,
        variables: dict | None = None,
        export: bool = False,
    ) -> dict | str:
        """Execute a GraphQL query against BIS data.

        The schema exposes events with their locations, categories, feedback
        forms, individual feedbacks with replies, and event records.
        PII fields (organizer names/emails, feedback author info) are excluded.

        When export=True, matching data is exported as full XLSX (including PII)
        and emailed to you instead of being returned.

        Args:
            query: A GraphQL query string.
            variables: Optional dict of GraphQL variables.
            export: If true, exports matching data as XLSX to your email.

        Returns:
            Query result dict, or confirmation message when export=True.
        """
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
            error_msgs = "; ".join(str(e) for e in result.errors)
            raise ValueError(f"GraphQL error: {error_msgs}")

        if export:
            user_email = self.request.user.email
            if not user_email:
                raise ValueError("No email address on your account.")

            if not context["_export_qs"]:
                return "No data matched for export."

            for label, qs in context["_export_qs"].items():
                _export_executor.submit(_export_and_email, qs, user_email, label)

            exported = ", ".join(context["_export_qs"].keys())
            return (
                f"Exporting {exported}. " f"You will receive an email at {user_email}."
            )

        return result.data


from mcp_server.djangomcp import global_mcp_server

# Append GraphQL schema SDL to MCP server instructions so the LLM knows
# which types and fields are available when writing queries.
from bis.mcp_schema import schema as _schema

global_mcp_server.append_instructions("GRAPHQL SCHEMA:\n" + _schema.as_str())
