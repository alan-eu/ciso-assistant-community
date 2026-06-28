"""MCP tools for resilience: BIA update/delete, asset assessments,
escalation thresholds, DORA incident reports. BIA list/create already
exists in write_tools.py + read_tools.py."""

import json

from ..client import (
    make_get_request,
    make_post_request,
    make_patch_request,
    make_delete_request,
    get_paginated_results,
)
from ..resolvers import (
    resolve_asset_id,
    resolve_folder_id,
    resolve_id_or_name,
    resolve_user_id,
)
from ..utils.response_formatter import (
    empty_response,
    error_response,
    http_error_response,
    success_response,
)


def _resolve_bia(bia_id_or_name: str) -> str:
    return resolve_id_or_name(bia_id_or_name, "/resilience/business-impact-analysis/")


# ---------- Business Impact Analyses (update/delete + actions) ----------


async def update_business_impact_analysis(
    bia_id: str,
    name: str = None,
    description: str = None,
    status: str = None,
    version: str = None,
    eta: str = None,
    due_date: str = None,
    observation: str = None,
    authors: list[str] = None,
    reviewers: list[str] = None,
) -> str:
    """Update a Business Impact Analysis.

    Args:
        bia_id: BIA UUID or name
        Other args: optional new values; authors/reviewers lists replace existing.
    """
    try:
        resolved = _resolve_bia(bia_id)
        payload = {}
        for k, v in {
            "name": name,
            "description": description,
            "status": status,
            "version": version,
            "eta": eta,
            "due_date": due_date,
            "observation": observation,
        }.items():
            if v is not None:
                payload[k] = v
        if authors is not None:
            payload["authors"] = [resolve_user_id(a) for a in authors]
        if reviewers is not None:
            payload["reviewers"] = [resolve_user_id(r) for r in reviewers]
        if not payload:
            return error_response("No-op", "No fields provided", "Pass at least one", True)
        res = make_patch_request(
            f"/resilience/business-impact-analysis/{resolved}/", payload
        )
        if res.status_code == 200:
            return success_response(
                f"Updated BIA {resolved}", "update_business_impact_analysis", None
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def delete_business_impact_analysis(bia_id: str) -> str:
    """Delete a Business Impact Analysis (cascades to asset assessments)."""
    try:
        resolved = _resolve_bia(bia_id)
        res = make_delete_request(f"/resilience/business-impact-analysis/{resolved}/")
        if res.status_code == 204:
            return success_response(
                f"Deleted BIA {resolved}", "delete_business_impact_analysis", None
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def get_business_impact_analysis_metrics(bia_id: str) -> str:
    """Get BIA metrics/scorecard."""
    try:
        resolved = _resolve_bia(bia_id)
        res = make_get_request(
            f"/resilience/business-impact-analysis/{resolved}/metrics/"
        )
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        return success_response(
            json.dumps(res.json(), indent=2),
            "get_business_impact_analysis_metrics",
            None,
        )
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


# ---------- Asset assessments ----------


async def get_asset_assessments(bia: str = None, asset: str = None):
    """List asset assessments under BIAs."""
    try:
        params, filters = {}, {}
        if bia:
            params["bia"] = _resolve_bia(bia)
            filters["bia"] = bia
        if asset:
            params["asset"] = resolve_asset_id(asset)
            filters["asset"] = asset
        res = make_get_request("/resilience/asset-assessments/", params=params)
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        items = get_paginated_results(res.json())
        if not items:
            return empty_response("asset assessments", filters)
        result = f"Found {len(items)} asset assessments\n\n|ID|BIA|Asset|Recovery Documented|Recovery Tested|Targets Met|\n|---|---|---|---|---|---|\n"
        for aa in items:
            result += (
                f"|{aa.get('id')}|{(aa.get('bia') or {}).get('str', '-')}"
                f"|{(aa.get('asset') or {}).get('str', '-')}"
                f"|{aa.get('recovery_documented', '-')}"
                f"|{aa.get('recovery_tested', '-')}"
                f"|{aa.get('recovery_targets_met', '-')}|\n"
            )
        return success_response(result, "get_asset_assessments", None)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def create_asset_assessment(
    bia: str,
    asset: str,
    folder: str = None,
    recovery_documented: str = None,
    recovery_tested: str = None,
    recovery_targets_met: str = None,
    observation: str = "",
) -> str:
    """Create an asset assessment under a BIA.

    Args:
        bia: BIA UUID or name
        asset: Asset UUID or name
        folder: Folder ID/name (defaults to BIA folder)
        recovery_documented: e.g. yes/no/partial
        recovery_tested: e.g. yes/no/partial
        recovery_targets_met: e.g. yes/no/partial
        observation: Observation
    """
    try:
        payload = {
            "bia": _resolve_bia(bia),
            "asset": resolve_asset_id(asset),
            "observation": observation,
        }
        if folder:
            payload["folder"] = resolve_folder_id(folder)
        for k, v in {
            "recovery_documented": recovery_documented,
            "recovery_tested": recovery_tested,
            "recovery_targets_met": recovery_targets_met,
        }.items():
            if v is not None:
                payload[k] = v
        res = make_post_request("/resilience/asset-assessments/", payload)
        if res.status_code == 201:
            aa = res.json()
            return success_response(
                f"Created asset assessment {aa.get('id')}",
                "create_asset_assessment",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def update_asset_assessment(
    asset_assessment_id: str,
    recovery_documented: str = None,
    recovery_tested: str = None,
    recovery_targets_met: str = None,
    observation: str = None,
) -> str:
    """Update an asset assessment."""
    try:
        payload = {
            k: v
            for k, v in {
                "recovery_documented": recovery_documented,
                "recovery_tested": recovery_tested,
                "recovery_targets_met": recovery_targets_met,
                "observation": observation,
            }.items()
            if v is not None
        }
        if not payload:
            return error_response("No-op", "No fields provided", "Pass at least one", True)
        res = make_patch_request(
            f"/resilience/asset-assessments/{asset_assessment_id}/", payload
        )
        if res.status_code == 200:
            return success_response(
                f"Updated asset assessment {asset_assessment_id}",
                "update_asset_assessment",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def delete_asset_assessment(asset_assessment_id: str) -> str:
    """Delete an asset assessment."""
    try:
        res = make_delete_request(
            f"/resilience/asset-assessments/{asset_assessment_id}/"
        )
        if res.status_code == 204:
            return success_response(
                f"Deleted asset assessment {asset_assessment_id}",
                "delete_asset_assessment",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


# ---------- Escalation thresholds ----------


async def get_escalation_thresholds(asset_assessment: str = None):
    """List escalation thresholds for an asset assessment."""
    try:
        params = {}
        if asset_assessment:
            params["asset_assessment"] = asset_assessment
        res = make_get_request("/resilience/escalation-thresholds/", params=params)
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        items = get_paginated_results(res.json())
        if not items:
            return empty_response(
                "escalation thresholds", {"asset_assessment": asset_assessment}
            )
        result = f"Found {len(items)} escalation thresholds\n\n|ID|Asset Assessment|Point in Time|Quali Impact|Quanti Impact|\n|---|---|---|---|---|\n"
        for t in items:
            result += (
                f"|{t.get('id')}"
                f"|{(t.get('asset_assessment') or {}).get('str', '-')}"
                f"|{t.get('point_in_time', '-')}"
                f"|{(t.get('quali_impact') or {}).get('str', '-')}"
                f"|{t.get('quanti_impact', '-')} {t.get('quanti_impact_unit', '') or ''}|\n"
            )
        return success_response(result, "get_escalation_thresholds", None)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def create_escalation_threshold(
    asset_assessment: str,
    point_in_time: str,
    quanti_impact: float = None,
    quanti_impact_unit: str = None,
    quali_impact: int = None,
    justification: str = "",
) -> str:
    """Create an escalation threshold on an asset assessment.

    Args:
        asset_assessment: Asset assessment UUID
        point_in_time: Duration in hours / ISO 8601 duration
        quanti_impact: Quantitative impact value
        quanti_impact_unit: Unit (e.g. EUR, USD)
        quali_impact: Qualitative impact level (int matrix value)
        justification: Justification
    """
    try:
        payload = {
            "asset_assessment": asset_assessment,
            "point_in_time": point_in_time,
            "justification": justification,
        }
        if quanti_impact is not None:
            payload["quanti_impact"] = quanti_impact
        if quanti_impact_unit is not None:
            payload["quanti_impact_unit"] = quanti_impact_unit
        if quali_impact is not None:
            payload["quali_impact"] = quali_impact
        res = make_post_request("/resilience/escalation-thresholds/", payload)
        if res.status_code == 201:
            return success_response(
                f"Created escalation threshold {res.json().get('id')}",
                "create_escalation_threshold",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def delete_escalation_threshold(threshold_id: str) -> str:
    """Delete an escalation threshold."""
    try:
        res = make_delete_request(f"/resilience/escalation-thresholds/{threshold_id}/")
        if res.status_code == 204:
            return success_response(
                f"Deleted escalation threshold {threshold_id}",
                "delete_escalation_threshold",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


# ---------- DORA incident reports ----------


async def get_dora_incident_reports(folder: str = None, incident: str = None):
    """List DORA incident reports."""
    try:
        params, filters = {}, {}
        if folder:
            params["folder"] = resolve_folder_id(folder)
            filters["folder"] = folder
        if incident:
            params["incident"] = resolve_id_or_name(incident, "/incidents/")
            filters["incident"] = incident
        res = make_get_request("/resilience/dora-incident-reports/", params=params)
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        items = get_paginated_results(res.json())
        if not items:
            return empty_response("DORA incident reports", filters)
        result = f"Found {len(items)} DORA incident reports\n\n|ID|Incident|Submission|Submitted|At|\n|---|---|---|---|---|\n"
        for r in items:
            result += (
                f"|{r.get('id')}|{(r.get('incident') or {}).get('str', '-')}"
                f"|{r.get('incident_submission', '-')}"
                f"|{r.get('is_submitted', '-')}|{r.get('submitted_at', '-')}|\n"
            )
        return success_response(result, "get_dora_incident_reports", None)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def get_dora_incident_report(dora_report_id: str):
    """Retrieve a single DORA incident report (full JSON payload)."""
    try:
        res = make_get_request(
            f"/resilience/dora-incident-reports/{dora_report_id}/"
        )
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        return success_response(
            json.dumps(res.json(), indent=2), "get_dora_incident_report", None
        )
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def validate_dora_incident_report(dora_report_id: str) -> str:
    """Run the DORA report validator (server-side completeness check)."""
    try:
        res = make_get_request(
            f"/resilience/dora-incident-reports/{dora_report_id}/validate_report/"
        )
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        return success_response(
            json.dumps(res.json(), indent=2),
            "validate_dora_incident_report",
            None,
        )
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def delete_dora_incident_report(dora_report_id: str) -> str:
    """Delete a DORA incident report."""
    try:
        res = make_delete_request(
            f"/resilience/dora-incident-reports/{dora_report_id}/"
        )
        if res.status_code == 204:
            return success_response(
                f"Deleted DORA incident report {dora_report_id}",
                "delete_dora_incident_report",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)
