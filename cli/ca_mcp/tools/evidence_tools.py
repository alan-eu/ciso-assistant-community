"""MCP tools for evidences (read / write / file upload).

Evidences are the artifacts (documents, screenshots, exports) attached to
applied controls, requirement assessments, findings, and timeline entries.
The backend supports file upload either via multipart POST on the create
endpoint or via the dedicated `/evidences/{id}/upload/` action.
"""

from ..client import (
    make_get_request,
    make_post_request,
    make_patch_request,
    make_delete_request,
    make_multipart_post_request,
    get_paginated_results,
)
from ..resolvers import (
    resolve_applied_control_id,
    resolve_evidence_id,
    resolve_finding_id,
    resolve_findings_assessment_id,
    resolve_folder_id,
    resolve_requirement_assessment_id,
)
from ..utils.detail_formatter import fmt_fk, fmt_m2m, fmt_m2m_cell, render_detail
from ..utils.response_formatter import (
    empty_response,
    error_response,
    http_error_response,
    success_response,
)


async def get_evidences(
    folder: str = None,
    applied_control: str = None,
    requirement_assessment: str = None,
    finding: str = None,
    findings_assessment: str = None,
    owner: str = None,
    status: str = None,
    name: str = None,
):
    """List evidences. All filters map to backend EvidenceFilterSet fields.

    Args:
        folder: Folder ID/name
        applied_control: Applied control ID/name — returns evidences linked to it
        requirement_assessment: Requirement assessment UUID
        finding: Finding ID/name
        findings_assessment: Findings assessment ID/name
        owner: Owner UUID (use get_users to resolve email -> id)
        status: Evidence status
        name: Filter by exact name
    """
    try:
        params = {}
        filters = {}

        if folder:
            params["folder"] = resolve_folder_id(folder)
            filters["folder"] = folder
        if applied_control:
            params["applied_controls"] = resolve_applied_control_id(applied_control)
            filters["applied_control"] = applied_control
        if requirement_assessment:
            params["requirement_assessments"] = resolve_requirement_assessment_id(
                requirement_assessment
            )
            filters["requirement_assessment"] = requirement_assessment
        if finding:
            params["findings"] = resolve_finding_id(finding)
            filters["finding"] = finding
        if findings_assessment:
            params["findings_assessments"] = resolve_findings_assessment_id(
                findings_assessment
            )
            filters["findings_assessment"] = findings_assessment
        if owner:
            params["owner"] = owner
            filters["owner"] = owner
        if status:
            params["status"] = status
            filters["status"] = status
        if name:
            params["name"] = name
            filters["name"] = name

        res = make_get_request("/evidences/", params=params)
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)

        evidences = get_paginated_results(res.json())
        if not evidences:
            return empty_response("evidences", filters)

        result = f"Found {len(evidences)} evidences"
        if filters:
            result += f" ({', '.join(f'{k}={v}' for k, v in filters.items())})"
        result += "\n\n"
        result += "|ID|Name|Status|Folder|Owners|Attachment|Link|Expiry|\n"
        result += "|---|---|---|---|---|---|---|---|\n"

        for ev in evidences:
            ev_id = ev.get("id", "N/A")
            name_v = ev.get("name", "N/A")
            status_v = ev.get("status") or "-"
            folder_v = (ev.get("folder") or {}).get("str", "-")
            owners = fmt_m2m_cell(ev.get("owner"), max_inline=2)
            # `attachment` is either None or a relative path on the server
            attachment = ev.get("attachment") or "-"
            link = ev.get("link") or "-"
            expiry = ev.get("expiry_date") or "-"
            result += (
                f"|{ev_id}|{name_v}|{status_v}|{folder_v}|{owners}|{attachment}"
                f"|{link}|{expiry}|\n"
            )

        return success_response(
            result,
            "get_evidences",
            "Use get_evidence(<id>) for full details, or attach_evidence_file(<id>, <path>) to upload a file.",
        )
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def get_evidence(evidence_id: str):
    """Retrieve full details of a single evidence.

    Args:
        evidence_id: Evidence UUID or name
    """
    try:
        resolved = resolve_evidence_id(evidence_id)
        res = make_get_request(f"/evidences/{resolved}/")
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        ev = res.json()

        result = render_detail(
            f"Evidence: {ev.get('name', 'N/A')}",
            [
                (
                    "",
                    [
                        ("ID", ev.get("id")),
                        ("Description", ev.get("description")),
                        ("Status", ev.get("status")),
                        ("Folder", fmt_fk(ev.get("folder"))),
                        ("Attachment", ev.get("attachment")),
                        ("Link", ev.get("link")),
                        ("Expiry Date", ev.get("expiry_date")),
                        ("Size", ev.get("size")),
                        ("Filename", ev.get("filename")),
                    ],
                ),
                (
                    "Relations",
                    [
                        ("Owners", fmt_m2m(ev.get("owner"))),
                        ("Applied Controls", fmt_m2m(ev.get("applied_controls"))),
                        (
                            "Requirement Assessments",
                            fmt_m2m(ev.get("requirement_assessments")),
                        ),
                        ("Findings", fmt_m2m(ev.get("findings"))),
                        (
                            "Findings Assessments",
                            fmt_m2m(ev.get("findings_assessments")),
                        ),
                        ("Timeline Entries", fmt_m2m(ev.get("timeline_entries"))),
                        ("Contracts", fmt_m2m(ev.get("contracts"))),
                    ],
                ),
            ],
        )
        return success_response(
            result,
            "get_evidence",
            "Use attach_evidence_file to upload a file, or update_evidence to modify fields",
        )
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def create_evidence(
    name: str,
    folder: str,
    description: str = "",
    link: str = None,
    status: str = None,
    expiry_date: str = None,
    applied_controls: list[str] = None,
    requirement_assessments: list[str] = None,
    findings: list[str] = None,
) -> str:
    """Create an evidence record (without a file — use attach_evidence_file after).

    Args:
        name: Evidence name
        folder: Folder ID/name
        description: Description
        link: External URL
        status: Status (see backend choices)
        expiry_date: YYYY-MM-DD
        applied_controls: List of applied-control IDs/names to link
        requirement_assessments: List of requirement-assessment UUIDs to link
        findings: List of finding IDs/names to link
    """
    try:
        payload = {
            "name": name,
            "folder": resolve_folder_id(folder),
            "description": description,
        }
        if link:
            payload["link"] = link
        if status:
            payload["status"] = status
        if expiry_date:
            payload["expiry_date"] = expiry_date
        if applied_controls:
            payload["applied_controls"] = [
                resolve_applied_control_id(x) for x in applied_controls
            ]
        if requirement_assessments:
            payload["requirement_assessments"] = [
                resolve_requirement_assessment_id(x) for x in requirement_assessments
            ]
        if findings:
            payload["findings"] = [resolve_finding_id(x) for x in findings]

        res = make_post_request("/evidences/", payload)
        if res.status_code == 201:
            ev = res.json()
            return success_response(
                f"Created evidence '{ev.get('name')}' (ID: {ev.get('id')})",
                "create_evidence",
                "Use attach_evidence_file(<id>, <path>) to upload a file to this evidence",
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def update_evidence(
    evidence_id: str,
    name: str = None,
    description: str = None,
    link: str = None,
    status: str = None,
    expiry_date: str = None,
    folder: str = None,
    applied_controls: list[str] = None,
    requirement_assessments: list[str] = None,
    findings: list[str] = None,
) -> str:
    """Update an evidence record.

    Args:
        evidence_id: Evidence UUID or name
        name, description, link, status, expiry_date: optional new values
        folder: New folder ID/name
        applied_controls, requirement_assessments, findings: replace the M2M lists
    """
    try:
        resolved = resolve_evidence_id(evidence_id)
        payload = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if link is not None:
            payload["link"] = link
        if status is not None:
            payload["status"] = status
        if expiry_date is not None:
            payload["expiry_date"] = expiry_date
        if folder is not None:
            payload["folder"] = resolve_folder_id(folder)
        if applied_controls is not None:
            payload["applied_controls"] = [
                resolve_applied_control_id(x) for x in applied_controls
            ]
        if requirement_assessments is not None:
            payload["requirement_assessments"] = [
                resolve_requirement_assessment_id(x) for x in requirement_assessments
            ]
        if findings is not None:
            payload["findings"] = [resolve_finding_id(x) for x in findings]

        if not payload:
            return error_response(
                "No-op", "No fields provided to update", "Pass at least one field", True
            )

        res = make_patch_request(f"/evidences/{resolved}/", payload)
        if res.status_code == 200:
            return success_response(
                f"Updated evidence {resolved}",
                "update_evidence",
                "Use get_evidence to verify",
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def delete_evidence(evidence_id: str) -> str:
    """Delete an evidence.

    Args:
        evidence_id: Evidence UUID or name
    """
    try:
        resolved = resolve_evidence_id(evidence_id)
        res = make_delete_request(f"/evidences/{resolved}/")
        if res.status_code == 204:
            return success_response(
                f"Deleted evidence {resolved}", "delete_evidence", None
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def attach_evidence_file(evidence_id: str, file_path: str) -> str:
    """Upload a file to an existing evidence record.

    Calls the dedicated /evidences/{id}/upload/ endpoint with a multipart
    body. Use create_evidence first to get an evidence ID.

    Args:
        evidence_id: Evidence UUID or name
        file_path: Local absolute path to the file to upload
    """
    try:
        resolved = resolve_evidence_id(evidence_id)
        res = make_multipart_post_request(
            f"/evidences/{resolved}/upload/",
            file_path=file_path,
            field_name="file",
        )
        if res.status_code in (200, 201, 204):
            return success_response(
                f"Uploaded {file_path} to evidence {resolved}",
                "attach_evidence_file",
                "Use get_evidence to confirm the attachment field is populated",
            )
        return http_error_response(res.status_code, res.text)
    except FileNotFoundError:
        return error_response(
            "File Not Found",
            f"No file at {file_path}",
            "Provide an absolute path to an existing file",
            True,
        )
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)
