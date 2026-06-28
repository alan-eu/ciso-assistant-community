"""MCP tools for risk acceptances (read, write, lifecycle).

A RiskAcceptance moves through states (created -> submitted -> accepted/rejected
-> revoked) via dedicated POST actions on the backend ViewSet.
"""

from ..client import (
    make_get_request,
    make_post_request,
    make_patch_request,
    make_delete_request,
    get_paginated_results,
)
from ..resolvers import (
    resolve_folder_id,
    resolve_risk_acceptance_id,
    resolve_risk_scenario_id,
    resolve_user_id,
)
from ..utils.detail_formatter import fmt_fk, fmt_m2m, render_detail
from ..utils.response_formatter import (
    empty_response,
    error_response,
    http_error_response,
    success_response,
)


async def get_risk_acceptances(
    folder: str = None,
    state: str = None,
    risk_scenario: str = None,
    approver: str = None,
    to_review: bool = None,
):
    """List risk acceptances.

    Args:
        folder: Folder ID/name
        state: created | submitted | accepted | rejected | revoked
        risk_scenario: Risk scenario ID/name (returns acceptances covering it)
        approver: Approver user UUID or email
        to_review: Only acceptances awaiting review
    """
    try:
        params = {}
        filters = {}
        if folder:
            params["folder"] = resolve_folder_id(folder)
            filters["folder"] = folder
        if state:
            params["state"] = state
            filters["state"] = state
        if risk_scenario:
            params["risk_scenarios"] = resolve_risk_scenario_id(risk_scenario)
            filters["risk_scenario"] = risk_scenario
        if approver:
            params["approver"] = resolve_user_id(approver)
            filters["approver"] = approver
        if to_review is not None:
            params["to_review"] = str(to_review).lower()
            filters["to_review"] = to_review

        res = make_get_request("/risk-acceptances/", params=params)
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)

        items = get_paginated_results(res.json())
        if not items:
            return empty_response("risk acceptances", filters)

        result = f"Found {len(items)} risk acceptances\n\n"
        result += "|ID|Name|State|Approver|Expiry|Folder|Scenarios|\n"
        result += "|---|---|---|---|---|---|---|\n"
        from ..utils.detail_formatter import fmt_m2m_cell

        for ra in items:
            result += (
                f"|{ra.get('id', 'N/A')}|{ra.get('name', 'N/A')}"
                f"|{ra.get('state', '-')}"
                f"|{(ra.get('approver') or {}).get('str', '-')}"
                f"|{ra.get('expiry_date') or '-'}"
                f"|{(ra.get('folder') or {}).get('str', '-')}"
                f"|{fmt_m2m_cell(ra.get('risk_scenarios'), max_inline=3)}|\n"
            )
        return success_response(
            result,
            "get_risk_acceptances",
            "Use submit/accept/reject/revoke_risk_acceptance to drive state, or get_risk_acceptance for details.",
        )
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def get_risk_acceptance(risk_acceptance_id: str):
    """Retrieve a single risk acceptance with all linked scenarios and timestamps.

    Args:
        risk_acceptance_id: Risk acceptance UUID or name
    """
    try:
        resolved = resolve_risk_acceptance_id(risk_acceptance_id)
        res = make_get_request(f"/risk-acceptances/{resolved}/")
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        ra = res.json()
        result = render_detail(
            f"Risk Acceptance: {ra.get('name', 'N/A')}",
            [
                (
                    "",
                    [
                        ("ID", ra.get("id")),
                        ("Description", ra.get("description")),
                        ("State", ra.get("state")),
                        ("Justification", ra.get("justification")),
                        ("Expiry Date", ra.get("expiry_date")),
                        ("Accepted At", ra.get("accepted_at")),
                        ("Rejected At", ra.get("rejected_at")),
                        ("Revoked At", ra.get("revoked_at")),
                        ("Approver", fmt_fk(ra.get("approver"))),
                        ("Folder", fmt_fk(ra.get("folder"))),
                    ],
                ),
                (
                    "Relations",
                    [("Risk Scenarios", fmt_m2m(ra.get("risk_scenarios")))],
                ),
            ],
        )
        return success_response(result, "get_risk_acceptance", None)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def create_risk_acceptance(
    name: str,
    folder: str,
    risk_scenarios: list[str],
    approver: str = None,
    description: str = "",
    justification: str = "",
    expiry_date: str = None,
) -> str:
    """Create a risk acceptance covering one or more risk scenarios.

    Args:
        name: Acceptance name
        folder: Folder ID/name
        risk_scenarios: List of risk scenario IDs/names
        approver: Approver user UUID or email
        description: Description
        justification: Justification text
        expiry_date: YYYY-MM-DD
    """
    try:
        payload = {
            "name": name,
            "folder": resolve_folder_id(folder),
            "risk_scenarios": [resolve_risk_scenario_id(x) for x in risk_scenarios],
            "description": description,
            "justification": justification,
        }
        if approver:
            payload["approver"] = resolve_user_id(approver)
        if expiry_date:
            payload["expiry_date"] = expiry_date

        res = make_post_request("/risk-acceptances/", payload)
        if res.status_code == 201:
            ra = res.json()
            return success_response(
                f"Created risk acceptance '{ra.get('name')}' (ID: {ra.get('id')})",
                "create_risk_acceptance",
                "Use submit_risk_acceptance to move it to 'submitted' state",
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def update_risk_acceptance(
    risk_acceptance_id: str,
    name: str = None,
    description: str = None,
    justification: str = None,
    expiry_date: str = None,
    approver: str = None,
    risk_scenarios: list[str] = None,
) -> str:
    """Update a risk acceptance (does not change state — use lifecycle actions).

    Args:
        risk_acceptance_id: Risk acceptance UUID or name
        name, description, justification, expiry_date: optional new values
        approver: Approver UUID or email
        risk_scenarios: Replace the linked scenario list
    """
    try:
        resolved = resolve_risk_acceptance_id(risk_acceptance_id)
        payload = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if justification is not None:
            payload["justification"] = justification
        if expiry_date is not None:
            payload["expiry_date"] = expiry_date
        if approver is not None:
            payload["approver"] = resolve_user_id(approver)
        if risk_scenarios is not None:
            payload["risk_scenarios"] = [
                resolve_risk_scenario_id(x) for x in risk_scenarios
            ]
        if not payload:
            return error_response("No-op", "No fields provided", "Pass at least one field", True)
        res = make_patch_request(f"/risk-acceptances/{resolved}/", payload)
        if res.status_code == 200:
            return success_response(
                f"Updated risk acceptance {resolved}", "update_risk_acceptance", None
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def delete_risk_acceptance(risk_acceptance_id: str) -> str:
    """Delete a risk acceptance.

    Args:
        risk_acceptance_id: Risk acceptance UUID or name
    """
    try:
        resolved = resolve_risk_acceptance_id(risk_acceptance_id)
        res = make_delete_request(f"/risk-acceptances/{resolved}/")
        if res.status_code == 204:
            return success_response(
                f"Deleted risk acceptance {resolved}", "delete_risk_acceptance", None
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def _ra_action(risk_acceptance_id: str, action: str) -> str:
    resolved = resolve_risk_acceptance_id(risk_acceptance_id)
    res = make_post_request(f"/risk-acceptances/{resolved}/{action}/", {})
    if res.status_code in (200, 204):
        return success_response(
            f"{action.title()} succeeded for risk acceptance {resolved}",
            f"{action}_risk_acceptance",
            "Use get_risk_acceptance to verify the new state",
        )
    return http_error_response(res.status_code, res.text)


async def submit_risk_acceptance(risk_acceptance_id: str) -> str:
    """Move a risk acceptance from draft to 'submitted' (awaiting approver)."""
    try:
        return await _ra_action(risk_acceptance_id, "submit")
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def draft_risk_acceptance(risk_acceptance_id: str) -> str:
    """Move a risk acceptance back to 'draft' state."""
    try:
        return await _ra_action(risk_acceptance_id, "draft")
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def accept_risk_acceptance(risk_acceptance_id: str) -> str:
    """Approve (accept) a submitted risk acceptance. Caller must be the approver."""
    try:
        return await _ra_action(risk_acceptance_id, "accept")
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def reject_risk_acceptance(risk_acceptance_id: str) -> str:
    """Reject a submitted risk acceptance. Caller must be the approver."""
    try:
        return await _ra_action(risk_acceptance_id, "reject")
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def revoke_risk_acceptance(risk_acceptance_id: str) -> str:
    """Revoke a previously accepted risk acceptance."""
    try:
        return await _ra_action(risk_acceptance_id, "revoke")
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)
