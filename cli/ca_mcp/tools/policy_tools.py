"""MCP tools for policies.

A Policy is a polymorphic AppliedControl served at /policies/. Most fields
match AppliedControl; the dedicated endpoint exists so policies can be
listed/filtered separately.
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
    resolve_id_or_name,
    resolve_policy_id,
)
from ..utils.detail_formatter import fmt_fk, fmt_m2m, fmt_m2m_cell, render_detail
from ..utils.response_formatter import (
    empty_response,
    error_response,
    http_error_response,
    success_response,
)


async def get_policies(
    folder: str = None,
    status: str = None,
    csf_function: str = None,
    effort: str = None,
    reference_control: str = None,
):
    """List policies.

    Args:
        folder: Folder ID/name
        status: planned | active | inactive | deprecated | ...
        csf_function: identify | protect | detect | respond | recover | govern
        effort: XS | S | M | L | XL
        reference_control: Reference control ID/name
    """
    try:
        params = {}
        filters = {}
        if folder:
            params["folder"] = resolve_folder_id(folder)
            filters["folder"] = folder
        if status:
            params["status"] = status
            filters["status"] = status
        if csf_function:
            params["csf_function"] = csf_function
            filters["csf_function"] = csf_function
        if effort:
            params["effort"] = effort
            filters["effort"] = effort
        if reference_control:
            params["reference_control"] = resolve_id_or_name(
                reference_control, "/reference-controls/"
            )
            filters["reference_control"] = reference_control

        res = make_get_request("/policies/", params=params)
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        items = get_paginated_results(res.json())
        if not items:
            return empty_response("policies", filters)

        result = f"Found {len(items)} policies\n\n"
        result += "|ID|Ref|Name|Status|CSF Function|Effort|Folder|Owners|Evidences|\n"
        result += "|---|---|---|---|---|---|---|---|---|\n"
        for p in items:
            result += (
                f"|{p.get('id', 'N/A')}|{p.get('ref_id') or '-'}|{p.get('name', 'N/A')}"
                f"|{p.get('status') or '-'}|{p.get('csf_function') or '-'}"
                f"|{p.get('effort') or '-'}|{(p.get('folder') or {}).get('str', '-')}"
                f"|{fmt_m2m_cell(p.get('owner'), max_inline=2)}"
                f"|{fmt_m2m_cell(p.get('evidences'), max_inline=2)}|\n"
            )
        return success_response(
            result,
            "get_policies",
            "Use get_policy(<id>) for full details, or update_policy / create_policy to manage.",
        )
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def get_policy(policy_id: str):
    """Retrieve a single policy with all linked resources.

    Args:
        policy_id: Policy UUID or name
    """
    try:
        resolved = resolve_policy_id(policy_id)
        res = make_get_request(f"/policies/{resolved}/")
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        p = res.json()
        result = render_detail(
            f"Policy: {p.get('name', 'N/A')}",
            [
                (
                    "",
                    [
                        ("ID", p.get("id")),
                        ("Ref ID", p.get("ref_id")),
                        ("Description", p.get("description")),
                        ("Status", p.get("status")),
                        ("CSF Function", p.get("csf_function")),
                        ("Category", p.get("category")),
                        ("Effort", p.get("effort")),
                        ("Priority", p.get("priority")),
                        ("Folder", fmt_fk(p.get("folder"))),
                        ("Reference Control", fmt_fk(p.get("reference_control"))),
                    ],
                ),
                (
                    "Relations",
                    [
                        ("Owners", fmt_m2m(p.get("owner"))),
                        ("Evidences", fmt_m2m(p.get("evidences"))),
                        ("Risk Scenarios", fmt_m2m(p.get("risk_scenarios"))),
                        (
                            "Requirement Assessments",
                            fmt_m2m(p.get("requirement_assessments")),
                        ),
                    ],
                ),
            ],
        )
        return success_response(result, "get_policy", None)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def create_policy(
    name: str,
    folder: str,
    description: str = "",
    status: str = "planned",
    csf_function: str = None,
    effort: str = None,
    priority: str = None,
    reference_control: str = None,
) -> str:
    """Create a policy.

    Args:
        name: Policy name
        folder: Folder ID/name
        description: Description
        status: Status (default planned)
        csf_function: identify | protect | detect | respond | recover | govern
        effort: XS | S | M | L | XL
        priority: P1..P4
        reference_control: Reference control ID/name
    """
    try:
        payload = {
            "name": name,
            "folder": resolve_folder_id(folder),
            "description": description,
            "status": status,
        }
        if csf_function:
            payload["csf_function"] = csf_function
        if effort:
            payload["effort"] = effort
        if priority:
            payload["priority"] = priority
        if reference_control:
            payload["reference_control"] = resolve_id_or_name(
                reference_control, "/reference-controls/"
            )

        res = make_post_request("/policies/", payload)
        if res.status_code == 201:
            p = res.json()
            return success_response(
                f"Created policy '{p.get('name')}' (ID: {p.get('id')})",
                "create_policy",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def update_policy(
    policy_id: str,
    name: str = None,
    description: str = None,
    status: str = None,
    csf_function: str = None,
    effort: str = None,
    priority: str = None,
) -> str:
    """Update a policy.

    Args:
        policy_id: Policy UUID or name
        name, description, status, csf_function, effort, priority: optional new values
    """
    try:
        resolved = resolve_policy_id(policy_id)
        payload = {
            k: v
            for k, v in {
                "name": name,
                "description": description,
                "status": status,
                "csf_function": csf_function,
                "effort": effort,
                "priority": priority,
            }.items()
            if v is not None
        }
        if not payload:
            return error_response("No-op", "No fields provided", "Pass at least one field", True)
        res = make_patch_request(f"/policies/{resolved}/", payload)
        if res.status_code == 200:
            return success_response(f"Updated policy {resolved}", "update_policy", None)
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def delete_policy(policy_id: str) -> str:
    """Delete a policy.

    Args:
        policy_id: Policy UUID or name
    """
    try:
        resolved = resolve_policy_id(policy_id)
        res = make_delete_request(f"/policies/{resolved}/")
        if res.status_code == 204:
            return success_response(f"Deleted policy {resolved}", "delete_policy", None)
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)
