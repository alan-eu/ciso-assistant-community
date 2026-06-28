"""MCP tools for findings and findings assessments.

A FindingsAssessment is a campaign/audit that produces zero or more Findings.
Each Finding can link to applied controls, evidences, and vulnerabilities.
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
    resolve_evidence_id,
    resolve_finding_id,
    resolve_findings_assessment_id,
    resolve_folder_id,
    resolve_perimeter_id,
    resolve_user_id,
    resolve_vulnerability_id,
)
from ..utils.detail_formatter import fmt_fk, fmt_m2m, fmt_m2m_cell, render_detail
from ..utils.response_formatter import (
    empty_response,
    error_response,
    http_error_response,
    success_response,
)


# ---------------- Findings Assessments ----------------


async def get_findings_assessments(
    folder: str = None,
    perimeter: str = None,
    category: str = None,
    status: str = None,
    author: str = None,
):
    """List findings assessments.

    Args:
        folder: Folder ID/name
        perimeter: Perimeter ID/name
        category: Category filter
        status: Status filter
        author: Author UUID or email
    """
    try:
        params = {}
        filters = {}
        if folder:
            params["folder"] = resolve_folder_id(folder)
            filters["folder"] = folder
        if perimeter:
            params["perimeter"] = resolve_perimeter_id(perimeter)
            filters["perimeter"] = perimeter
        if category:
            params["category"] = category
            filters["category"] = category
        if status:
            params["status"] = status
            filters["status"] = status
        if author:
            params["authors"] = resolve_user_id(author)
            filters["author"] = author

        res = make_get_request("/findings-assessments/", params=params)
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        items = get_paginated_results(res.json())
        if not items:
            return empty_response("findings assessments", filters)

        result = f"Found {len(items)} findings assessments\n\n"
        result += "|ID|Ref|Name|Category|Status|Perimeter|Folder|Authors|\n"
        result += "|---|---|---|---|---|---|---|---|\n"
        for fa in items:
            result += (
                f"|{fa.get('id', 'N/A')}|{fa.get('ref_id') or '-'}|{fa.get('name', 'N/A')}"
                f"|{fa.get('category') or '-'}|{fa.get('status') or '-'}"
                f"|{(fa.get('perimeter') or {}).get('str', '-')}"
                f"|{(fa.get('folder') or {}).get('str', '-')}"
                f"|{fmt_m2m_cell(fa.get('authors'), max_inline=2)}|\n"
            )
        return success_response(
            result,
            "get_findings_assessments",
            "Use get_findings(findings_assessment=<id>) to list the findings of one assessment.",
        )
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def get_findings_assessment(findings_assessment_id: str):
    """Retrieve a single findings assessment with full relations.

    Args:
        findings_assessment_id: Findings assessment UUID or name
    """
    try:
        resolved = resolve_findings_assessment_id(findings_assessment_id)
        res = make_get_request(f"/findings-assessments/{resolved}/")
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        fa = res.json()
        result = render_detail(
            f"Findings Assessment: {fa.get('name', 'N/A')}",
            [
                (
                    "",
                    [
                        ("ID", fa.get("id")),
                        ("Ref ID", fa.get("ref_id")),
                        ("Category", fa.get("category")),
                        ("Status", fa.get("status")),
                        ("Description", fa.get("description")),
                        ("Folder", fmt_fk(fa.get("folder"))),
                        ("Perimeter", fmt_fk(fa.get("perimeter"))),
                        ("Owner", fmt_fk(fa.get("owner"))),
                    ],
                ),
                (
                    "Relations",
                    [
                        ("Authors", fmt_m2m(fa.get("authors"))),
                        ("Evidences", fmt_m2m(fa.get("evidences"))),
                    ],
                ),
            ],
        )
        return success_response(result, "get_findings_assessment", None)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def create_findings_assessment(
    name: str,
    folder: str,
    perimeter: str = None,
    category: str = None,
    status: str = None,
    description: str = "",
    authors: list[str] = None,
) -> str:
    """Create a findings assessment.

    Args:
        name: Assessment name
        folder: Folder ID/name
        perimeter: Perimeter ID/name (optional)
        category: Category
        status: Status
        description: Description
        authors: List of author UUIDs or emails
    """
    try:
        payload = {
            "name": name,
            "folder": resolve_folder_id(folder),
            "description": description,
        }
        if perimeter:
            payload["perimeter"] = resolve_perimeter_id(perimeter)
        if category:
            payload["category"] = category
        if status:
            payload["status"] = status
        if authors:
            payload["authors"] = [resolve_user_id(a) for a in authors]

        res = make_post_request("/findings-assessments/", payload)
        if res.status_code == 201:
            fa = res.json()
            return success_response(
                f"Created findings assessment '{fa.get('name')}' (ID: {fa.get('id')})",
                "create_findings_assessment",
                "Use create_finding to add findings to this assessment.",
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def update_findings_assessment(
    findings_assessment_id: str,
    name: str = None,
    description: str = None,
    status: str = None,
    category: str = None,
    perimeter: str = None,
    authors: list[str] = None,
) -> str:
    """Update a findings assessment.

    Args:
        findings_assessment_id: UUID or name
        name, description, status, category: optional new values
        perimeter: New perimeter ID/name
        authors: Replace the authors list with these users (UUIDs or emails)
    """
    try:
        resolved = resolve_findings_assessment_id(findings_assessment_id)
        payload = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if status is not None:
            payload["status"] = status
        if category is not None:
            payload["category"] = category
        if perimeter is not None:
            payload["perimeter"] = resolve_perimeter_id(perimeter)
        if authors is not None:
            payload["authors"] = [resolve_user_id(a) for a in authors]
        if not payload:
            return error_response("No-op", "No fields provided", "Pass at least one", True)
        res = make_patch_request(f"/findings-assessments/{resolved}/", payload)
        if res.status_code == 200:
            return success_response(
                f"Updated findings assessment {resolved}",
                "update_findings_assessment",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def delete_findings_assessment(findings_assessment_id: str) -> str:
    """Delete a findings assessment (cascades to its findings)."""
    try:
        resolved = resolve_findings_assessment_id(findings_assessment_id)
        res = make_delete_request(f"/findings-assessments/{resolved}/")
        if res.status_code == 204:
            return success_response(
                f"Deleted findings assessment {resolved}",
                "delete_findings_assessment",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


# ---------------- Findings ----------------


async def get_findings(
    folder: str = None,
    findings_assessment: str = None,
    owner: str = None,
    status: str = None,
    severity: int = None,
    priority: str = None,
    applied_control: str = None,
    evidence: str = None,
    vulnerability: str = None,
):
    """List findings.

    Args:
        folder: Folder ID/name
        findings_assessment: Findings assessment ID/name
        owner: Owner UUID or email
        status: Status filter
        severity: Severity integer (-1 undefined, 0 info, ..., 4 critical)
        priority: Priority filter
        applied_control: Applied control ID/name linked to the finding
        evidence: Evidence ID/name linked to the finding
        vulnerability: Vulnerability ID/name linked to the finding
    """
    try:
        params = {}
        filters = {}
        if folder:
            params["folder"] = resolve_folder_id(folder)
            filters["folder"] = folder
        if findings_assessment:
            params["findings_assessment"] = resolve_findings_assessment_id(
                findings_assessment
            )
            filters["findings_assessment"] = findings_assessment
        if owner:
            params["owner"] = resolve_user_id(owner)
            filters["owner"] = owner
        if status:
            params["status"] = status
            filters["status"] = status
        if severity is not None:
            params["severity"] = severity
            filters["severity"] = severity
        if priority:
            params["priority"] = priority
            filters["priority"] = priority
        if applied_control:
            params["applied_controls"] = resolve_applied_control_id(applied_control)
            filters["applied_control"] = applied_control
        if evidence:
            params["evidences"] = resolve_evidence_id(evidence)
            filters["evidence"] = evidence
        if vulnerability:
            params["vulnerabilities"] = resolve_vulnerability_id(vulnerability)
            filters["vulnerability"] = vulnerability

        res = make_get_request("/findings/", params=params)
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        items = get_paginated_results(res.json())
        if not items:
            return empty_response("findings", filters)

        result = f"Found {len(items)} findings\n\n"
        result += "|ID|Ref|Name|Status|Severity|Priority|Assessment|Owners|Due Date|Applied Controls|Evidences|\n"
        result += "|---|---|---|---|---|---|---|---|---|---|---|\n"
        for f in items:
            result += (
                f"|{f.get('id', 'N/A')}|{f.get('ref_id') or '-'}|{f.get('name', 'N/A')}"
                f"|{f.get('status') or '-'}|{f.get('severity', '-')}|{f.get('priority') or '-'}"
                f"|{(f.get('findings_assessment') or {}).get('str', '-')}"
                f"|{fmt_m2m_cell(f.get('owner'), max_inline=2)}"
                f"|{f.get('due_date') or '-'}"
                f"|{fmt_m2m_cell(f.get('applied_controls'), max_inline=2)}"
                f"|{fmt_m2m_cell(f.get('evidences'), max_inline=2)}|\n"
            )
        return success_response(
            result,
            "get_findings",
            "Use get_finding(<id>) for full details, or update_finding to modify.",
        )
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def get_finding(finding_id: str):
    """Retrieve a single finding with all linked resources.

    Args:
        finding_id: Finding UUID or name
    """
    try:
        resolved = resolve_finding_id(finding_id)
        res = make_get_request(f"/findings/{resolved}/")
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        f = res.json()
        result = render_detail(
            f"Finding: {f.get('name', 'N/A')}",
            [
                (
                    "",
                    [
                        ("ID", f.get("id")),
                        ("Ref ID", f.get("ref_id")),
                        ("Description", f.get("description")),
                        ("Severity", f.get("severity")),
                        ("Priority", f.get("priority")),
                        ("Status", f.get("status")),
                        ("Due Date", f.get("due_date")),
                        ("Findings Assessment", fmt_fk(f.get("findings_assessment"))),
                        ("Folder", fmt_fk(f.get("folder"))),
                    ],
                ),
                (
                    "Relations",
                    [
                        ("Owners", fmt_m2m(f.get("owner"))),
                        ("Applied Controls", fmt_m2m(f.get("applied_controls"))),
                        ("Evidences", fmt_m2m(f.get("evidences"))),
                        ("Vulnerabilities", fmt_m2m(f.get("vulnerabilities"))),
                    ],
                ),
            ],
        )
        return success_response(result, "get_finding", None)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def create_finding(
    name: str,
    findings_assessment: str,
    description: str = "",
    severity: int = None,
    priority: str = None,
    status: str = None,
    due_date: str = None,
    owner: list[str] = None,
    applied_controls: list[str] = None,
    evidences: list[str] = None,
    vulnerabilities: list[str] = None,
    ref_id: str = None,
) -> str:
    """Create a finding under an existing findings assessment.

    Args:
        name: Finding name
        findings_assessment: Findings assessment ID/name
        description: Description
        severity: Severity integer (-1 undefined, 0 info, ..., 4 critical)
        priority: Priority
        status: Status
        due_date: YYYY-MM-DD
        owner: List of owner UUIDs or emails
        applied_controls: List of applied-control IDs/names to link
        evidences: List of evidence IDs/names to link
        vulnerabilities: List of vulnerability IDs/names to link
        ref_id: Optional reference id
    """
    try:
        payload = {
            "name": name,
            "findings_assessment": resolve_findings_assessment_id(findings_assessment),
            "description": description,
        }
        if severity is not None:
            payload["severity"] = severity
        if priority:
            payload["priority"] = priority
        if status:
            payload["status"] = status
        if due_date:
            payload["due_date"] = due_date
        if ref_id:
            payload["ref_id"] = ref_id
        if owner:
            payload["owner"] = [resolve_user_id(o) for o in owner]
        if applied_controls:
            payload["applied_controls"] = [
                resolve_applied_control_id(x) for x in applied_controls
            ]
        if evidences:
            payload["evidences"] = [resolve_evidence_id(x) for x in evidences]
        if vulnerabilities:
            payload["vulnerabilities"] = [
                resolve_vulnerability_id(x) for x in vulnerabilities
            ]

        res = make_post_request("/findings/", payload)
        if res.status_code == 201:
            f = res.json()
            return success_response(
                f"Created finding '{f.get('name')}' (ID: {f.get('id')})",
                "create_finding",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def update_finding(
    finding_id: str,
    name: str = None,
    description: str = None,
    severity: int = None,
    priority: str = None,
    status: str = None,
    due_date: str = None,
    owner: list[str] = None,
    applied_controls: list[str] = None,
    evidences: list[str] = None,
    vulnerabilities: list[str] = None,
) -> str:
    """Update a finding.

    Args:
        finding_id: Finding UUID or name
        Other args: optional new values; M2M lists replace existing.
    """
    try:
        resolved = resolve_finding_id(finding_id)
        payload = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if severity is not None:
            payload["severity"] = severity
        if priority is not None:
            payload["priority"] = priority
        if status is not None:
            payload["status"] = status
        if due_date is not None:
            payload["due_date"] = due_date
        if owner is not None:
            payload["owner"] = [resolve_user_id(o) for o in owner]
        if applied_controls is not None:
            payload["applied_controls"] = [
                resolve_applied_control_id(x) for x in applied_controls
            ]
        if evidences is not None:
            payload["evidences"] = [resolve_evidence_id(x) for x in evidences]
        if vulnerabilities is not None:
            payload["vulnerabilities"] = [
                resolve_vulnerability_id(x) for x in vulnerabilities
            ]
        if not payload:
            return error_response("No-op", "No fields provided", "Pass at least one", True)

        res = make_patch_request(f"/findings/{resolved}/", payload)
        if res.status_code == 200:
            return success_response(f"Updated finding {resolved}", "update_finding", None)
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def delete_finding(finding_id: str) -> str:
    """Delete a finding.

    Args:
        finding_id: Finding UUID or name
    """
    try:
        resolved = resolve_finding_id(finding_id)
        res = make_delete_request(f"/findings/{resolved}/")
        if res.status_code == 204:
            return success_response(f"Deleted finding {resolved}", "delete_finding", None)
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)
