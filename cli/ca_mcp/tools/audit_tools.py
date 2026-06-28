"""MCP tools for compliance assessment (audit) lifecycle and analytics.

Standard CRUD is provided for the resource itself, plus the most useful
custom actions on the backend ViewSet: SoA, action plan tree, score, quality
check, controls/evidence coverage, sync-to-applied-controls, compare.
"""

import json

from ..client import (
    make_get_request,
    make_post_request,
    make_patch_request,
    make_delete_request,
    get_paginated_results,
)
from ..resolvers import (
    resolve_compliance_assessment_id,
    resolve_folder_id,
    resolve_framework_id,
    resolve_perimeter_id,
    resolve_user_id,
)
from ..utils.detail_formatter import fmt_fk, fmt_m2m, render_detail
from ..utils.response_formatter import (
    error_response,
    http_error_response,
    success_response,
)


async def get_compliance_assessment(compliance_assessment_id: str):
    """Retrieve full details of a single compliance assessment (audit).

    Args:
        compliance_assessment_id: Compliance assessment UUID or name
    """
    try:
        resolved = resolve_compliance_assessment_id(compliance_assessment_id)
        res = make_get_request(f"/compliance-assessments/{resolved}/")
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        ca = res.json()
        result = render_detail(
            f"Compliance Assessment: {ca.get('name', 'N/A')}",
            [
                (
                    "",
                    [
                        ("ID", ca.get("id")),
                        ("Ref ID", ca.get("ref_id")),
                        ("Description", ca.get("description")),
                        ("Status", ca.get("status")),
                        ("Version", ca.get("version")),
                        ("ETA", ca.get("eta")),
                        ("Due Date", ca.get("due_date")),
                        ("Show Documentation Score", ca.get("show_documentation_score")),
                        ("Selected Implementation Groups", ca.get("selected_implementation_groups")),
                        ("Min Score", ca.get("min_score")),
                        ("Max Score", ca.get("max_score")),
                        ("Folder", fmt_fk(ca.get("folder"))),
                        ("Framework", fmt_fk(ca.get("framework"))),
                        ("Perimeter", fmt_fk(ca.get("perimeter"))),
                        ("Campaign", fmt_fk(ca.get("campaign"))),
                        ("Baseline", fmt_fk(ca.get("baseline"))),
                    ],
                ),
                (
                    "Relations",
                    [
                        ("Authors", fmt_m2m(ca.get("authors"))),
                        ("Reviewers", fmt_m2m(ca.get("reviewers"))),
                        ("Assets", fmt_m2m(ca.get("assets"))),
                        ("Evidences", fmt_m2m(ca.get("evidences"))),
                        ("EBIOS RM Studies", fmt_m2m(ca.get("ebios_rm_studies"))),
                    ],
                ),
            ],
        )
        return success_response(
            result,
            "get_compliance_assessment",
            "Use get_requirement_assessments(compliance_assessment_id_or_name=<id>) to see all requirements.",
        )
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def update_compliance_assessment(
    compliance_assessment_id: str,
    name: str = None,
    description: str = None,
    status: str = None,
    version: str = None,
    eta: str = None,
    due_date: str = None,
    perimeter: str = None,
    framework: str = None,
    folder: str = None,
    authors: list[str] = None,
    reviewers: list[str] = None,
    selected_implementation_groups: list[str] = None,
) -> str:
    """Update a compliance assessment.

    Args:
        compliance_assessment_id: UUID or name
        status: planned | in_progress | in_review | done | deprecated
        Other args: optional new values; lists replace existing.
    """
    try:
        resolved = resolve_compliance_assessment_id(compliance_assessment_id)
        payload = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if status is not None:
            payload["status"] = status
        if version is not None:
            payload["version"] = version
        if eta is not None:
            payload["eta"] = eta
        if due_date is not None:
            payload["due_date"] = due_date
        if perimeter is not None:
            payload["perimeter"] = resolve_perimeter_id(perimeter)
        if framework is not None:
            payload["framework"] = resolve_framework_id(framework)
        if folder is not None:
            payload["folder"] = resolve_folder_id(folder)
        if authors is not None:
            payload["authors"] = [resolve_user_id(a) for a in authors]
        if reviewers is not None:
            payload["reviewers"] = [resolve_user_id(r) for r in reviewers]
        if selected_implementation_groups is not None:
            payload["selected_implementation_groups"] = selected_implementation_groups

        if not payload:
            return error_response("No-op", "No fields provided", "Pass at least one", True)
        res = make_patch_request(f"/compliance-assessments/{resolved}/", payload)
        if res.status_code == 200:
            return success_response(
                f"Updated compliance assessment {resolved}",
                "update_compliance_assessment",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def delete_compliance_assessment(compliance_assessment_id: str) -> str:
    """Delete a compliance assessment and its requirement assessments.

    Args:
        compliance_assessment_id: UUID or name
    """
    try:
        resolved = resolve_compliance_assessment_id(compliance_assessment_id)
        res = make_delete_request(f"/compliance-assessments/{resolved}/")
        if res.status_code == 204:
            return success_response(
                f"Deleted compliance assessment {resolved}",
                "delete_compliance_assessment",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def sync_compliance_assessment_to_applied_controls(
    compliance_assessment_id: str,
) -> str:
    """Create suggested applied controls from a compliance assessment.

    Calls POST /compliance-assessments/{id}/syncToActions/.

    Args:
        compliance_assessment_id: UUID or name
    """
    try:
        resolved = resolve_compliance_assessment_id(compliance_assessment_id)
        res = make_post_request(
            f"/compliance-assessments/{resolved}/syncToActions/", {}
        )
        if res.status_code in (200, 201, 204):
            body = res.text or "{}"
            return success_response(
                f"Synced compliance assessment {resolved} to applied controls\n{body}",
                "sync_compliance_assessment_to_applied_controls",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def get_compliance_assessment_global_score(compliance_assessment_id: str) -> str:
    """Get the global score for a compliance assessment.

    Args:
        compliance_assessment_id: UUID or name
    """
    try:
        resolved = resolve_compliance_assessment_id(compliance_assessment_id)
        res = make_get_request(f"/compliance-assessments/{resolved}/global_score/")
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        return success_response(
            json.dumps(res.json(), indent=2),
            "get_compliance_assessment_global_score",
            None,
        )
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def get_compliance_assessment_quality_check(compliance_assessment_id: str) -> str:
    """Run a quality check on a compliance assessment.

    Args:
        compliance_assessment_id: UUID or name
    """
    try:
        resolved = resolve_compliance_assessment_id(compliance_assessment_id)
        res = make_get_request(f"/compliance-assessments/{resolved}/quality_check/")
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        return success_response(
            json.dumps(res.json(), indent=2),
            "get_compliance_assessment_quality_check",
            None,
        )
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def get_statement_of_applicability(compliance_assessment_id: str) -> str:
    """Get the Statement of Applicability (SoA) of a compliance assessment.

    Args:
        compliance_assessment_id: UUID or name
    """
    try:
        resolved = resolve_compliance_assessment_id(compliance_assessment_id)
        res = make_get_request(f"/compliance-assessments/{resolved}/soa/")
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        return success_response(
            json.dumps(res.json(), indent=2),
            "get_statement_of_applicability",
            None,
        )
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def get_controls_coverage(compliance_assessment_id: str) -> str:
    """Get applied-controls coverage stats for a compliance assessment."""
    try:
        resolved = resolve_compliance_assessment_id(compliance_assessment_id)
        res = make_get_request(f"/compliance-assessments/{resolved}/controls_coverage/")
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        return success_response(
            json.dumps(res.json(), indent=2), "get_controls_coverage", None
        )
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def get_evidence_coverage(compliance_assessment_id: str) -> str:
    """Get evidence coverage stats for a compliance assessment."""
    try:
        resolved = resolve_compliance_assessment_id(compliance_assessment_id)
        res = make_get_request(f"/compliance-assessments/{resolved}/evidence_coverage/")
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        return success_response(
            json.dumps(res.json(), indent=2), "get_evidence_coverage", None
        )
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def get_compliance_timeline(compliance_assessment_id: str) -> str:
    """Get the compliance timeline (status changes over time)."""
    try:
        resolved = resolve_compliance_assessment_id(compliance_assessment_id)
        res = make_get_request(
            f"/compliance-assessments/{resolved}/compliance_timeline/"
        )
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        return success_response(
            json.dumps(res.json(), indent=2), "get_compliance_timeline", None
        )
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def compare_compliance_assessments(
    compliance_assessment_id: str, other_compliance_assessment_id: str
) -> str:
    """Compare two compliance assessments via the /compare action.

    Args:
        compliance_assessment_id: UUID or name (source)
        other_compliance_assessment_id: UUID or name to compare against
    """
    try:
        a = resolve_compliance_assessment_id(compliance_assessment_id)
        b = resolve_compliance_assessment_id(other_compliance_assessment_id)
        res = make_get_request(
            f"/compliance-assessments/{a}/compare/", params={"compare_with": b}
        )
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        return success_response(
            json.dumps(res.json(), indent=2),
            "compare_compliance_assessments",
            None,
        )
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def map_compliance_assessment_from(
    target_compliance_assessment_id: str,
    source_compliance_assessment_id: str,
) -> str:
    """Map results from a source audit into a target audit using framework mappings.

    Calls POST /compliance-assessments/{target}/map_from/.

    Args:
        target_compliance_assessment_id: Target audit (receives the mapped results)
        source_compliance_assessment_id: Source audit (provides the results)
    """
    try:
        target = resolve_compliance_assessment_id(target_compliance_assessment_id)
        source = resolve_compliance_assessment_id(source_compliance_assessment_id)
        res = make_post_request(
            f"/compliance-assessments/{target}/map_from/",
            {"source": source},
        )
        if res.status_code in (200, 201, 204):
            return success_response(
                f"Mapped from {source} into {target}\n{res.text}",
                "map_compliance_assessment_from",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)
