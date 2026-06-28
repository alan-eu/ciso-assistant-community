"""MCP tools for incident timeline entries and comments.

Both are small, single-purpose resources. Auto-generated timeline entries
(SEVERITY_CHANGED, STATUS_CHANGED) are protected from deletion by the backend.
"""

from ..client import (
    make_get_request,
    make_post_request,
    make_patch_request,
    make_delete_request,
    get_paginated_results,
)
from ..resolvers import (
    resolve_applied_control_id,
    resolve_finding_id,
    resolve_folder_id,
    resolve_id_or_name,
    resolve_requirement_assessment_id,
    resolve_risk_scenario_id,
    resolve_user_id,
)
from ..utils.detail_formatter import fmt_fk, render_detail
from ..utils.response_formatter import (
    empty_response,
    error_response,
    http_error_response,
    success_response,
)


# ---------------- Timeline entries ----------------


async def get_timeline_entries(incident: str = None):
    """List incident timeline entries.

    Args:
        incident: Incident ID/name (the only backend filter)
    """
    try:
        params = {}
        filters = {}
        if incident:
            params["incident"] = resolve_id_or_name(incident, "/incidents/")
            filters["incident"] = incident
        res = make_get_request("/timeline-entries/", params=params)
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        items = get_paginated_results(res.json())
        if not items:
            return empty_response("timeline entries", filters)

        result = f"Found {len(items)} timeline entries\n\n"
        result += "|ID|Incident|Entry Type|Timestamp|Author|Observation|\n"
        result += "|---|---|---|---|---|---|\n"
        for te in items:
            result += (
                f"|{te.get('id', 'N/A')}"
                f"|{(te.get('incident') or {}).get('str', '-')}"
                f"|{te.get('entry_type', '-')}"
                f"|{te.get('timestamp', '-')}"
                f"|{(te.get('author') or {}).get('str', '-')}"
                f"|{(te.get('observation') or '').replace(chr(10), ' ')}|\n"
            )
        return success_response(
            result,
            "get_timeline_entries",
            "Use create_timeline_entry to add an observation, or update/delete_timeline_entry.",
        )
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def get_timeline_entry(timeline_entry_id: str):
    """Retrieve a single timeline entry.

    Args:
        timeline_entry_id: Timeline entry UUID
    """
    try:
        res = make_get_request(f"/timeline-entries/{timeline_entry_id}/")
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        te = res.json()
        result = render_detail(
            f"Timeline Entry {te.get('id', '?')}",
            [
                (
                    "",
                    [
                        ("Incident", fmt_fk(te.get("incident"))),
                        ("Entry Type", te.get("entry_type")),
                        ("Timestamp", te.get("timestamp")),
                        ("Author", fmt_fk(te.get("author"))),
                        ("Observation", te.get("observation")),
                        ("Folder", fmt_fk(te.get("folder"))),
                    ],
                )
            ],
        )
        return success_response(result, "get_timeline_entry", None)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def create_timeline_entry(
    incident: str,
    entry_type: str,
    timestamp: str,
    observation: str = "",
    folder: str = None,
) -> str:
    """Create a manual timeline entry on an incident.

    Args:
        incident: Incident ID/name
        entry_type: Entry type (manual entry types — see backend choices)
        timestamp: ISO 8601 datetime (e.g. "2024-04-12T15:30:00Z")
        observation: Observation text
        folder: Folder ID/name (defaults to the incident's folder)
    """
    try:
        payload = {
            "incident": resolve_id_or_name(incident, "/incidents/"),
            "entry_type": entry_type,
            "timestamp": timestamp,
            "observation": observation,
        }
        if folder:
            payload["folder"] = resolve_folder_id(folder)
        res = make_post_request("/timeline-entries/", payload)
        if res.status_code == 201:
            te = res.json()
            return success_response(
                f"Created timeline entry (ID: {te.get('id')})",
                "create_timeline_entry",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def update_timeline_entry(
    timeline_entry_id: str,
    entry_type: str = None,
    timestamp: str = None,
    observation: str = None,
) -> str:
    """Update a manual timeline entry (auto-generated ones cannot be edited)."""
    try:
        payload = {}
        if entry_type is not None:
            payload["entry_type"] = entry_type
        if timestamp is not None:
            payload["timestamp"] = timestamp
        if observation is not None:
            payload["observation"] = observation
        if not payload:
            return error_response("No-op", "No fields provided", "Pass at least one", True)
        res = make_patch_request(f"/timeline-entries/{timeline_entry_id}/", payload)
        if res.status_code == 200:
            return success_response(
                f"Updated timeline entry {timeline_entry_id}",
                "update_timeline_entry",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def delete_timeline_entry(timeline_entry_id: str) -> str:
    """Delete a manual timeline entry. The backend blocks deletion of auto entries."""
    try:
        res = make_delete_request(f"/timeline-entries/{timeline_entry_id}/")
        if res.status_code == 204:
            return success_response(
                f"Deleted timeline entry {timeline_entry_id}",
                "delete_timeline_entry",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


# ---------------- Comments ----------------


async def get_comments(
    requirement_assessment: str = None,
    risk_scenario: str = None,
    applied_control: str = None,
    finding: str = None,
    author: str = None,
    is_active: bool = None,
):
    """List comments. Exactly one parent (requirement_assessment / risk_scenario /
    applied_control / finding) is expected per comment.

    Args:
        requirement_assessment: Requirement assessment UUID
        risk_scenario: Risk scenario ID/name
        applied_control: Applied control ID/name
        finding: Finding ID/name
        author: Author UUID or email
        is_active: Filter by active flag
    """
    try:
        params = {}
        filters = {}
        if requirement_assessment:
            params["requirement_assessment"] = resolve_requirement_assessment_id(
                requirement_assessment
            )
            filters["requirement_assessment"] = requirement_assessment
        if risk_scenario:
            params["risk_scenario"] = resolve_risk_scenario_id(risk_scenario)
            filters["risk_scenario"] = risk_scenario
        if applied_control:
            params["applied_control"] = resolve_applied_control_id(applied_control)
            filters["applied_control"] = applied_control
        if finding:
            params["finding"] = resolve_finding_id(finding)
            filters["finding"] = finding
        if author:
            params["author"] = resolve_user_id(author)
            filters["author"] = author
        if is_active is not None:
            params["is_active"] = str(is_active).lower()
            filters["is_active"] = is_active

        res = make_get_request("/comments/", params=params)
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        items = get_paginated_results(res.json())
        if not items:
            return empty_response("comments", filters)

        result = f"Found {len(items)} comments\n\n"
        result += "|ID|Author|Parent|Active|Created|Body|\n"
        result += "|---|---|---|---|---|---|\n"
        for c in items:
            parent = (
                (c.get("requirement_assessment") or {}).get("str")
                or (c.get("risk_scenario") or {}).get("str")
                or (c.get("applied_control") or {}).get("str")
                or (c.get("finding") or {}).get("str")
                or "-"
            )
            body = (c.get("body") or "").replace("\n", " ")
            result += (
                f"|{c.get('id', 'N/A')}"
                f"|{(c.get('author') or {}).get('str', '-')}"
                f"|{parent}|{c.get('is_active', '-')}"
                f"|{c.get('created_at', '-')}|{body}|\n"
            )
        return success_response(result, "get_comments", None)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def create_comment(
    body: str,
    requirement_assessment: str = None,
    risk_scenario: str = None,
    applied_control: str = None,
    finding: str = None,
) -> str:
    """Create a comment. Exactly one of the four parent params must be set.

    Args:
        body: Comment body (markdown supported by the UI)
        requirement_assessment: Requirement assessment UUID
        risk_scenario: Risk scenario ID/name
        applied_control: Applied control ID/name
        finding: Finding ID/name
    """
    try:
        parents = [requirement_assessment, risk_scenario, applied_control, finding]
        if sum(1 for x in parents if x) != 1:
            return error_response(
                "Bad Request",
                "Exactly one of requirement_assessment, risk_scenario, applied_control, finding must be set",
                "Set one parent and retry",
                True,
            )
        payload = {"body": body}
        if requirement_assessment:
            payload["requirement_assessment"] = resolve_requirement_assessment_id(
                requirement_assessment
            )
        if risk_scenario:
            payload["risk_scenario"] = resolve_risk_scenario_id(risk_scenario)
        if applied_control:
            payload["applied_control"] = resolve_applied_control_id(applied_control)
        if finding:
            payload["finding"] = resolve_finding_id(finding)

        res = make_post_request("/comments/", payload)
        if res.status_code == 201:
            c = res.json()
            return success_response(
                f"Created comment {c.get('id')}", "create_comment", None
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def update_comment(comment_id: str, body: str = None, is_active: bool = None) -> str:
    """Update a comment (author-only on the backend).

    Args:
        comment_id: Comment UUID
        body: New body
        is_active: Toggle active flag
    """
    try:
        payload = {}
        if body is not None:
            payload["body"] = body
        if is_active is not None:
            payload["is_active"] = is_active
        if not payload:
            return error_response("No-op", "No fields provided", "Pass at least one", True)
        res = make_patch_request(f"/comments/{comment_id}/", payload)
        if res.status_code == 200:
            return success_response(f"Updated comment {comment_id}", "update_comment", None)
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def delete_comment(comment_id: str) -> str:
    """Delete a comment (author-only on the backend)."""
    try:
        res = make_delete_request(f"/comments/{comment_id}/")
        if res.status_code == 204:
            return success_response(f"Deleted comment {comment_id}", "delete_comment", None)
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)
