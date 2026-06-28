"""Detail (single-object) read tools.

These fill the gaps where only a list tool existed before. The list tools must
flatten objects into table rows, which forces them to drop M2M relations and
nested fields; these detail tools render the full backend payload so the model
can see every field the API returned (and chain follow-up calls using IDs).
"""

from ..client import make_get_request, safe_json
from ..resolvers import (
    resolve_applied_control_id,
    resolve_asset_id,
    resolve_attack_path_id,
    resolve_entity_assessment_id,
    resolve_operational_scenario_id,
    resolve_requirement_assessment_id,
    resolve_user_id,
)
from ..utils.detail_formatter import fmt_fk, fmt_m2m, render_detail
from ..utils.response_formatter import (
    error_response,
    http_error_response,
    success_response,
)


async def get_applied_control(applied_control_id: str):
    """Retrieve full details of a single applied control by UUID or name.

    Returns every field the backend exposes, including the lists of linked
    requirement assessments, evidences, owners, reference control, objectives,
    findings count, and linked-models flags. Use this when `get_applied_controls`
    truncated the relation you need.

    Args:
        applied_control_id: Applied control UUID or name
    """
    try:
        resolved = resolve_applied_control_id(applied_control_id)
        res = make_get_request(f"/applied-controls/{resolved}/")
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        ac, _err = safe_json(res)
        if _err:
            return error_response("Backend Error", _err, "Report to backend team; the retrieve endpoint returned a bad response", False)

        result = render_detail(
            f"Applied Control: {ac.get('name', 'N/A')}",
            [
                (
                    "",
                    [
                        ("ID", ac.get("id")),
                        ("Ref ID", ac.get("ref_id")),
                        ("Description", ac.get("description")),
                        ("Status", ac.get("status")),
                        ("ETA", ac.get("eta")),
                        ("Expiry", ac.get("expiry_date")),
                        ("Start Date", ac.get("start_date")),
                        ("Folder", fmt_fk(ac.get("folder"))),
                        ("Category", ac.get("category")),
                        ("CSF Function", ac.get("csf_function")),
                        ("Priority", ac.get("priority")),
                        ("Effort", ac.get("effort")),
                        ("Cost", ac.get("cost")),
                        ("Impact", ac.get("control_impact")),
                        ("Reference Control", fmt_fk(ac.get("reference_control"))),
                        ("Findings Count", ac.get("findings_count")),
                        ("Linked Models", ac.get("linked_models")),
                    ],
                ),
                (
                    "Relations",
                    [
                        ("Owners", fmt_m2m(ac.get("owner"))),
                        ("Evidences", fmt_m2m(ac.get("evidences"))),
                        ("Objectives", fmt_m2m(ac.get("objectives"))),
                        ("Assets", fmt_m2m(ac.get("assets"))),
                        ("Incidents", fmt_m2m(ac.get("incidents"))),
                        ("Security Exceptions", fmt_m2m(ac.get("security_exceptions"))),
                        ("Filtering Labels", fmt_m2m(ac.get("filtering_labels"))),
                        (
                            "Requirement Assessments",
                            fmt_m2m(ac.get("requirement_assessments")),
                        ),
                    ],
                ),
            ],
        )
        return success_response(
            result,
            "get_applied_control",
            "Use update_applied_control to modify, or follow IDs to the linked resources",
        )
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def get_requirement_assessment(requirement_assessment_id: str):
    """Retrieve full details of a single requirement assessment by UUID.

    Returns the full lists of applied controls, evidences, threats, reference
    controls, security exceptions, and answers — none of which are present in
    `get_requirement_assessments` table rows.

    Args:
        requirement_assessment_id: Requirement assessment UUID
    """
    try:
        resolved = resolve_requirement_assessment_id(requirement_assessment_id)
        res = make_get_request(f"/requirement-assessments/{resolved}/")
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        ra, _err = safe_json(res)
        if _err:
            return error_response("Backend Error", _err, "Report to backend team; the retrieve endpoint returned a bad response", False)

        result = render_detail(
            f"Requirement Assessment: {ra.get('name') or ra.get('ref_id') or ra.get('id')}",
            [
                (
                    "",
                    [
                        ("ID", ra.get("id")),
                        ("Ref ID", ra.get("ref_id")),
                        ("Name", ra.get("name")),
                        ("Description", ra.get("description")),
                        ("Status", ra.get("status")),
                        ("Result", ra.get("result")),
                        ("Score", ra.get("score")),
                        ("Is Scored", ra.get("is_scored")),
                        ("Documentation Score", ra.get("documentation_score")),
                        ("Mapping Inference", ra.get("mapping_inference")),
                        ("Observation", ra.get("observation")),
                        ("Folder", fmt_fk(ra.get("folder"))),
                        (
                            "Compliance Assessment",
                            fmt_fk(ra.get("compliance_assessment")),
                        ),
                        ("Requirement", fmt_fk(ra.get("requirement"))),
                    ],
                ),
                (
                    "Relations",
                    [
                        ("Applied Controls", fmt_m2m(ra.get("applied_controls"))),
                        ("Evidences", fmt_m2m(ra.get("evidences"))),
                        ("Threats", fmt_m2m(ra.get("threats"))),
                        ("Reference Controls", fmt_m2m(ra.get("reference_controls"))),
                        (
                            "Security Exceptions",
                            fmt_m2m(ra.get("security_exceptions")),
                        ),
                        ("Answers", ra.get("answers")),
                    ],
                ),
            ],
        )
        return success_response(
            result,
            "get_requirement_assessment",
            "Use update_requirement_assessment to modify, or follow applied-control IDs",
        )
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def get_asset(asset_id: str):
    """Retrieve full details of a single asset by UUID or name.

    Returns owners, parent/children assets, applied controls, solutions,
    security/recovery objectives & capabilities, filtering labels, asset class,
    personal data flag, and security exceptions — fields the list tool drops.

    Args:
        asset_id: Asset UUID or name
    """
    try:
        resolved = resolve_asset_id(asset_id)
        res = make_get_request(f"/assets/{resolved}/")
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        asset, _err = safe_json(res)
        if _err:
            return error_response("Backend Error", _err, "Report to backend team; the retrieve endpoint returned a bad response", False)

        result = render_detail(
            f"Asset: {asset.get('name', 'N/A')}",
            [
                (
                    "",
                    [
                        ("ID", asset.get("id")),
                        ("Ref ID", asset.get("ref_id")),
                        ("Type", asset.get("type")),
                        ("Description", asset.get("description")),
                        ("Folder", fmt_fk(asset.get("folder"))),
                        ("Asset Class", fmt_fk(asset.get("asset_class"))),
                        ("Personal Data", asset.get("personal_data")),
                    ],
                ),
                (
                    "Hierarchy",
                    [
                        ("Parent Assets", fmt_m2m(asset.get("parent_assets"))),
                        ("Children Assets", fmt_m2m(asset.get("children_assets"))),
                        ("Support Assets", fmt_m2m(asset.get("support_assets"))),
                    ],
                ),
                (
                    "Ownership & Labels",
                    [
                        ("Owners", fmt_m2m(asset.get("owner"))),
                        ("Filtering Labels", fmt_m2m(asset.get("filtering_labels"))),
                        ("Solutions", fmt_m2m(asset.get("solutions"))),
                    ],
                ),
                (
                    "Controls & Exceptions",
                    [
                        ("Applied Controls", fmt_m2m(asset.get("applied_controls"))),
                        (
                            "Security Exceptions",
                            fmt_m2m(asset.get("security_exceptions")),
                        ),
                    ],
                ),
                (
                    "Capabilities",
                    [
                        ("Security Objectives", asset.get("security_objectives")),
                        (
                            "Disaster Recovery Objectives",
                            asset.get("disaster_recovery_objectives"),
                        ),
                        ("Security Capabilities", asset.get("security_capabilities")),
                        ("Recovery Capabilities", asset.get("recovery_capabilities")),
                        (
                            "Overridden Children Capabilities",
                            asset.get("overridden_children_capabilities"),
                        ),
                    ],
                ),
            ],
        )
        return success_response(
            result,
            "get_asset",
            "Use update_asset to modify, or follow IDs to linked resources",
        )
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def get_user(user_id: str):
    """Retrieve full details of a single user by UUID or email.

    Returns groups, permissions, staff/superuser flags, last login, and
    third-party status — none of which appear in `get_users` rows.

    Args:
        user_id: User UUID or email address
    """
    try:
        resolved = resolve_user_id(user_id)
        res = make_get_request(f"/users/{resolved}/")
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        user, _err = safe_json(res)
        if _err:
            return error_response("Backend Error", _err, "Report to backend team; the retrieve endpoint returned a bad response", False)

        result = render_detail(
            f"User: {user.get('email', 'N/A')}",
            [
                (
                    "",
                    [
                        ("ID", user.get("id")),
                        ("Email", user.get("email")),
                        ("First Name", user.get("first_name")),
                        ("Last Name", user.get("last_name")),
                        ("Active", user.get("is_active")),
                        ("Staff", user.get("is_staff")),
                        ("Superuser", user.get("is_superuser")),
                        ("Third Party", user.get("is_third_party")),
                        ("Last Login", user.get("last_login")),
                        ("Date Joined", user.get("date_joined")),
                    ],
                ),
                (
                    "Groups & Permissions",
                    [
                        ("User Groups", fmt_m2m(user.get("user_groups"))),
                        ("Permissions", fmt_m2m(user.get("permissions"))),
                    ],
                ),
            ],
        )
        return success_response(
            result, "get_user", "Use the UUID as `owner` when assigning resources"
        )
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def get_entity_assessment(entity_assessment_id: str):
    """Retrieve full details of a single TPRM entity assessment.

    Returns the linked compliance assessment, evidence, solutions,
    representatives, authors, reviewers, and validation flows — fields the
    list tool drops.

    Args:
        entity_assessment_id: Entity assessment UUID or name
    """
    try:
        resolved = resolve_entity_assessment_id(entity_assessment_id)
        res = make_get_request(f"/entity-assessments/{resolved}/")
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        ea, _err = safe_json(res)
        if _err:
            return error_response("Backend Error", _err, "Report to backend team; the retrieve endpoint returned a bad response", False)

        result = render_detail(
            f"Entity Assessment: {ea.get('name', 'N/A')}",
            [
                (
                    "",
                    [
                        ("ID", ea.get("id")),
                        ("Ref ID", ea.get("ref_id")),
                        ("Description", ea.get("description")),
                        ("Status", ea.get("status")),
                        ("Conclusion", ea.get("conclusion")),
                        ("Criticality", ea.get("criticality")),
                        ("Penetration", ea.get("penetration")),
                        ("Dependency", ea.get("dependency")),
                        ("Maturity", ea.get("maturity")),
                        ("Trust", ea.get("trust")),
                        ("Eta", ea.get("eta")),
                        ("Due Date", ea.get("due_date")),
                        ("Entity", fmt_fk(ea.get("entity"))),
                        (
                            "Compliance Assessment",
                            fmt_fk(ea.get("compliance_assessment")),
                        ),
                        ("Evidence", fmt_fk(ea.get("evidence"))),
                        ("Perimeter", fmt_fk(ea.get("perimeter"))),
                        ("Folder", fmt_fk(ea.get("folder"))),
                    ],
                ),
                (
                    "Relations",
                    [
                        ("Solutions", fmt_m2m(ea.get("solutions"))),
                        ("Representatives", fmt_m2m(ea.get("representatives"))),
                        ("Authors", fmt_m2m(ea.get("authors"))),
                        ("Reviewers", fmt_m2m(ea.get("reviewers"))),
                        ("Validation Flows", fmt_m2m(ea.get("validation_flows"))),
                    ],
                ),
            ],
        )
        return success_response(
            result,
            "get_entity_assessment",
            "Use update_entity_assessment to modify",
        )
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def get_attack_path(attack_path_id: str):
    """Retrieve full details of a single EBIOS RM attack path.

    Returns the ro_to couple (with risk origin / target objective expanded),
    full stakeholder list, and study context — fields the list tool drops.

    Args:
        attack_path_id: Attack path UUID or name
    """
    try:
        resolved = resolve_attack_path_id(attack_path_id)
        res = make_get_request(f"/ebios-rm/attack-paths/{resolved}/")
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        ap, _err = safe_json(res)
        if _err:
            return error_response("Backend Error", _err, "Report to backend team; the retrieve endpoint returned a bad response", False)

        result = render_detail(
            f"Attack Path: {ap.get('name', 'N/A')}",
            [
                (
                    "",
                    [
                        ("ID", ap.get("id")),
                        ("Ref ID", ap.get("ref_id")),
                        ("Description", ap.get("description")),
                        ("Selected", ap.get("is_selected")),
                        ("Justification", ap.get("justification")),
                        ("EBIOS RM Study", fmt_fk(ap.get("ebios_rm_study"))),
                        ("Strategic Scenario", fmt_fk(ap.get("strategic_scenario"))),
                        ("RO/TO Couple", fmt_fk(ap.get("ro_to_couple"))),
                        ("Risk Origin", fmt_fk(ap.get("risk_origin"))),
                        ("Target Objective", fmt_fk(ap.get("target_objective"))),
                    ],
                ),
                (
                    "Relations",
                    [("Stakeholders", fmt_m2m(ap.get("stakeholders")))],
                ),
            ],
        )
        return success_response(
            result,
            "get_attack_path",
            "Use update_attack_path to modify, or create_operational_scenario from this path",
        )
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def get_operational_scenario(operational_scenario_id: str):
    """Retrieve full details of a single EBIOS RM operational scenario.

    Returns stakeholders, threats, operating modes, and the linked attack
    path — fields the list tool drops or summarizes to counts.

    Args:
        operational_scenario_id: Operational scenario UUID
    """
    try:
        resolved = resolve_operational_scenario_id(operational_scenario_id)
        res = make_get_request(f"/ebios-rm/operational-scenarios/{resolved}/")
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        os_, _err = safe_json(res)
        if _err:
            return error_response("Backend Error", _err, "Report to backend team; the retrieve endpoint returned a bad response", False)

        result = render_detail(
            f"Operational Scenario: {os_.get('name') or os_.get('str') or os_.get('id')}",
            [
                (
                    "",
                    [
                        ("ID", os_.get("id")),
                        ("Ref ID", os_.get("ref_id")),
                        ("Name", os_.get("name") or os_.get("str")),
                        ("Description", os_.get("description")),
                        ("Selected", os_.get("is_selected")),
                        ("Justification", os_.get("justification")),
                        ("Likelihood", fmt_fk(os_.get("likelihood"))),
                        ("Gravity", fmt_fk(os_.get("gravity"))),
                        ("Risk Level", fmt_fk(os_.get("risk_level"))),
                        ("EBIOS RM Study", fmt_fk(os_.get("ebios_rm_study"))),
                        ("Attack Path", fmt_fk(os_.get("attack_path"))),
                        (
                            "Operating Modes Description",
                            os_.get("operating_modes_description"),
                        ),
                    ],
                ),
                (
                    "Relations",
                    [
                        ("Stakeholders", fmt_m2m(os_.get("stakeholders"))),
                        ("RO/TO", fmt_m2m(os_.get("ro_to"))),
                        ("Threats", fmt_m2m(os_.get("threats"))),
                        ("Operating Modes", fmt_m2m(os_.get("operating_modes"))),
                    ],
                ),
            ],
        )
        return success_response(
            result,
            "get_operational_scenario",
            "Use update_operational_scenario to modify",
        )
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)
