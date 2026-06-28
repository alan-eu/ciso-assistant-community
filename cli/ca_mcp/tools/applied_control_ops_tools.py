"""MCP tools for applied-control operations beyond CRUD.

Wraps the AppliedControlViewSet custom actions: duplicate, merge, todo,
to_review, analytics, sync-to-reference-control. Also provides a delete
tool that complements the existing update_applied_control.
"""

import json

from ..client import (
    make_get_request,
    make_post_request,
    make_delete_request,
    get_paginated_results,
)
from ..resolvers import (
    resolve_applied_control_id,
    resolve_folder_id,
)
from ..utils.detail_formatter import fmt_m2m_cell
from ..utils.response_formatter import (
    error_response,
    http_error_response,
    success_response,
)


async def delete_applied_control(control_id: str) -> str:
    """Delete an applied control.

    Args:
        control_id: Control UUID or name
    """
    try:
        resolved = resolve_applied_control_id(control_id)
        res = make_delete_request(f"/applied-controls/{resolved}/")
        if res.status_code == 204:
            return success_response(
                f"Deleted applied control {resolved}", "delete_applied_control", None
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def duplicate_applied_control(
    control_id: str,
    name: str,
    folder: str = None,
    description: str = "",
    duplicate_evidences: bool = False,
) -> str:
    """Duplicate an applied control under a new name (optionally cloning evidences).

    Args:
        control_id: Source control UUID or name
        name: Name for the new duplicate
        folder: Target folder ID/name (defaults to source folder)
        description: Description for the new control
        duplicate_evidences: Also duplicate linked evidences
    """
    try:
        resolved = resolve_applied_control_id(control_id)
        payload = {
            "name": name,
            "description": description,
            "duplicate_evidences": duplicate_evidences,
        }
        if folder:
            payload["folder"] = resolve_folder_id(folder)
        res = make_post_request(
            f"/applied-controls/{resolved}/duplicate/", payload
        )
        if res.status_code in (200, 201):
            new = res.json()
            return success_response(
                f"Duplicated applied control {resolved} -> {new.get('id')} ({new.get('name')})",
                "duplicate_applied_control",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def merge_applied_controls(
    control_ids: list[str],
    target_type: str = "new",
    target_id: str = None,
    target_fields: dict = None,
) -> str:
    """Merge multiple applied controls into one.

    Args:
        control_ids: List of source control UUIDs or names (>= 2)
        target_type: "new" to create a new control, "existing" to merge into one of them
        target_id: Required when target_type='existing' — the surviving control ID/name
        target_fields: Required when target_type='new' — dict of fields for the new control (at least "name", "folder")
    """
    try:
        if len(control_ids) < 2:
            return error_response(
                "Bad Request",
                "Need at least 2 control_ids to merge",
                "Provide 2+ ids",
                True,
            )
        sources = [resolve_applied_control_id(c) for c in control_ids]
        target = {"type": target_type}
        if target_type == "existing":
            if not target_id:
                return error_response(
                    "Bad Request",
                    "target_id required when target_type='existing'",
                    "Pass target_id",
                    True,
                )
            target["id"] = resolve_applied_control_id(target_id)
        else:
            if not target_fields or not target_fields.get("name"):
                return error_response(
                    "Bad Request",
                    "target_fields with at least 'name' required when target_type='new'",
                    "Pass target_fields",
                    True,
                )
            if target_fields.get("folder"):
                target_fields["folder"] = resolve_folder_id(target_fields["folder"])
            target["fields"] = target_fields

        res = make_post_request(
            "/applied-controls/merge/", {"sources": sources, "target": target}
        )
        if res.status_code in (200, 201):
            return success_response(
                f"Merged {len(sources)} controls\n{res.text}",
                "merge_applied_controls",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def sync_applied_control_to_reference(control_id: str) -> str:
    """Sync an applied control's metadata from its linked reference control.

    Args:
        control_id: Control UUID or name (must have a reference_control set)
    """
    try:
        resolved = resolve_applied_control_id(control_id)
        res = make_post_request(
            f"/applied-controls/{resolved}/sync-to-reference-control/", {}
        )
        if res.status_code in (200, 204):
            return success_response(
                f"Synced applied control {resolved} to its reference control",
                "sync_applied_control_to_reference",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def get_applied_controls_todo() -> str:
    """List applied controls in 'to do' state, ordered for action planning."""
    try:
        res = make_get_request("/applied-controls/todo/")
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        items = get_paginated_results(res.json())
        if not items:
            return success_response(
                "No to-do applied controls", "get_applied_controls_todo", None
            )
        result = f"Found {len(items)} to-do applied controls\n\n"
        result += "|ID|Name|Status|ETA|Priority|Owner|\n|---|---|---|---|---|---|\n"
        for c in items:
            result += (
                f"|{c.get('id')}|{c.get('name')}|{c.get('status')}|{c.get('eta') or '-'}"
                f"|{c.get('priority') or '-'}"
                f"|{fmt_m2m_cell(c.get('owner'), max_inline=2)}|\n"
            )
        return success_response(result, "get_applied_controls_todo", None)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def get_applied_controls_to_review() -> str:
    """List applied controls awaiting review (e.g. expiring or past their review date)."""
    try:
        res = make_get_request("/applied-controls/to_review/")
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        items = get_paginated_results(res.json())
        if not items:
            return success_response(
                "No applied controls awaiting review",
                "get_applied_controls_to_review",
                None,
            )
        result = f"Found {len(items)} applied controls to review\n\n"
        result += "|ID|Name|Status|Expiry|Owner|\n|---|---|---|---|---|\n"
        for c in items:
            result += (
                f"|{c.get('id')}|{c.get('name')}|{c.get('status')}"
                f"|{c.get('expiry_date') or '-'}"
                f"|{fmt_m2m_cell(c.get('owner'), max_inline=2)}|\n"
            )
        return success_response(result, "get_applied_controls_to_review", None)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def get_applied_controls_analytics() -> str:
    """Return applied-controls analytics: counts by status / category / priority."""
    try:
        res = make_get_request("/applied-controls/analytics/")
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        return success_response(
            json.dumps(res.json(), indent=2),
            "get_applied_controls_analytics",
            None,
        )
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)
