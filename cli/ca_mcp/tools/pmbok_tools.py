"""MCP tools for PMBOK: projects, accreditations, generic collections,
responsibility matrices and their activities/actors."""

import json

from ..client import (
    make_get_request,
    make_post_request,
    make_patch_request,
    make_delete_request,
    get_paginated_results,
)
from ..resolvers import resolve_folder_id, resolve_id_or_name, resolve_user_id
from ..utils.response_formatter import (
    empty_response,
    error_response,
    http_error_response,
    success_response,
)


# ---------- Projects ----------


async def get_projects(folder: str = None, status: str = None, kind: str = None, owner: str = None):
    """List PMBOK projects."""
    try:
        params, filters = {}, {}
        if folder:
            params["folder"] = resolve_folder_id(folder)
            filters["folder"] = folder
        if status:
            params["status"] = status
            filters["status"] = status
        if kind:
            params["kind"] = kind
            filters["kind"] = kind
        if owner:
            params["owner"] = resolve_user_id(owner)
            filters["owner"] = owner
        res = make_get_request("/pmbok/projects/", params=params)
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        items = get_paginated_results(res.json())
        if not items:
            return empty_response("projects", filters)
        result = f"Found {len(items)} projects\n\n|ID|Name|Kind|Status|Priority|Health|Folder|\n|---|---|---|---|---|---|---|\n"
        for p in items:
            result += (
                f"|{p.get('id')}|{p.get('name', '-')}|{p.get('kind', '-')}"
                f"|{p.get('status', '-')}|{p.get('priority', '-')}|{p.get('health', '-')}"
                f"|{(p.get('folder') or {}).get('str', '-')}|\n"
            )
        return success_response(result, "get_projects", None)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def get_project(project_id: str):
    """Retrieve a single project."""
    try:
        resolved = resolve_id_or_name(project_id, "/pmbok/projects/")
        res = make_get_request(f"/pmbok/projects/{resolved}/")
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        return success_response(json.dumps(res.json(), indent=2), "get_project", None)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def create_project(
    name: str,
    folder: str,
    description: str = "",
    kind: str = None,
    status: str = None,
    priority: str = None,
    health: str = None,
    owner: str = None,
    sponsor: str = None,
    parent_project: str = None,
    start_date: str = None,
    end_date: str = None,
    eta: str = None,
    purpose: str = "",
    objectives: str = "",
    budget: float = None,
    currency: str = None,
    create_collection: bool = False,
) -> str:
    """Create a PMBOK project."""
    try:
        payload = {
            "name": name,
            "folder": resolve_folder_id(folder),
            "description": description,
            "purpose": purpose,
            "objectives": objectives,
            "create_collection": create_collection,
        }
        for k, v in {
            "kind": kind,
            "status": status,
            "priority": priority,
            "health": health,
            "start_date": start_date,
            "end_date": end_date,
            "eta": eta,
            "currency": currency,
            "budget": budget,
        }.items():
            if v is not None:
                payload[k] = v
        if owner:
            payload["owner"] = resolve_user_id(owner)
        if sponsor:
            payload["sponsor"] = resolve_user_id(sponsor)
        if parent_project:
            payload["parent_project"] = resolve_id_or_name(
                parent_project, "/pmbok/projects/"
            )
        res = make_post_request("/pmbok/projects/", payload)
        if res.status_code == 201:
            p = res.json()
            return success_response(
                f"Created project '{p.get('name')}' (ID: {p.get('id')})",
                "create_project",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def update_project(
    project_id: str,
    name: str = None,
    description: str = None,
    status: str = None,
    priority: str = None,
    health: str = None,
    owner: str = None,
    sponsor: str = None,
    start_date: str = None,
    end_date: str = None,
    eta: str = None,
) -> str:
    """Update a project."""
    try:
        resolved = resolve_id_or_name(project_id, "/pmbok/projects/")
        payload = {}
        for k, v in {
            "name": name,
            "description": description,
            "status": status,
            "priority": priority,
            "health": health,
            "start_date": start_date,
            "end_date": end_date,
            "eta": eta,
        }.items():
            if v is not None:
                payload[k] = v
        if owner is not None:
            payload["owner"] = resolve_user_id(owner)
        if sponsor is not None:
            payload["sponsor"] = resolve_user_id(sponsor)
        if not payload:
            return error_response("No-op", "No fields provided", "Pass at least one", True)
        res = make_patch_request(f"/pmbok/projects/{resolved}/", payload)
        if res.status_code == 200:
            return success_response(f"Updated project {resolved}", "update_project", None)
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def delete_project(project_id: str) -> str:
    """Delete a project."""
    try:
        resolved = resolve_id_or_name(project_id, "/pmbok/projects/")
        res = make_delete_request(f"/pmbok/projects/{resolved}/")
        if res.status_code == 204:
            return success_response(f"Deleted project {resolved}", "delete_project", None)
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


# ---------- Accreditations ----------


async def get_accreditations(folder: str = None, status: str = None):
    """List accreditations."""
    try:
        params, filters = {}, {}
        if folder:
            params["folder"] = resolve_folder_id(folder)
            filters["folder"] = folder
        if status:
            params["status"] = status
            filters["status"] = status
        res = make_get_request("/pmbok/accreditations/", params=params)
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        items = get_paginated_results(res.json())
        if not items:
            return empty_response("accreditations", filters)
        result = f"Found {len(items)} accreditations\n\n|ID|Name|Status|Category|Authority|Expiry|\n|---|---|---|---|---|---|\n"
        for a in items:
            result += (
                f"|{a.get('id')}|{a.get('name', '-')}|{a.get('status', '-')}"
                f"|{a.get('category', '-')}"
                f"|{(a.get('authority') or {}).get('str', '-')}"
                f"|{a.get('expiry_date', '-')}|\n"
            )
        return success_response(result, "get_accreditations", None)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def create_accreditation(
    name: str,
    folder: str,
    status: str = None,
    category: str = None,
    description: str = "",
    commission_date: str = None,
    duration_months: int = None,
    expiry_date: str = None,
) -> str:
    """Create an accreditation."""
    try:
        payload = {
            "name": name,
            "folder": resolve_folder_id(folder),
            "description": description,
        }
        for k, v in {
            "status": status,
            "category": category,
            "commission_date": commission_date,
            "duration_months": duration_months,
            "expiry_date": expiry_date,
        }.items():
            if v is not None:
                payload[k] = v
        res = make_post_request("/pmbok/accreditations/", payload)
        if res.status_code == 201:
            return success_response(
                f"Created accreditation {res.json().get('id')}",
                "create_accreditation",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def update_accreditation(
    accreditation_id: str,
    name: str = None,
    status: str = None,
    expiry_date: str = None,
    duration_months: int = None,
) -> str:
    """Update an accreditation."""
    try:
        payload = {
            k: v
            for k, v in {
                "name": name,
                "status": status,
                "expiry_date": expiry_date,
                "duration_months": duration_months,
            }.items()
            if v is not None
        }
        if not payload:
            return error_response("No-op", "No fields provided", "Pass at least one", True)
        res = make_patch_request(f"/pmbok/accreditations/{accreditation_id}/", payload)
        if res.status_code == 200:
            return success_response(
                f"Updated accreditation {accreditation_id}", "update_accreditation", None
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def delete_accreditation(accreditation_id: str) -> str:
    """Delete an accreditation."""
    try:
        res = make_delete_request(f"/pmbok/accreditations/{accreditation_id}/")
        if res.status_code == 204:
            return success_response(
                f"Deleted accreditation {accreditation_id}", "delete_accreditation", None
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


# ---------- Generic collections ----------


async def get_generic_collections(folder: str = None):
    """List generic collections (PMBOK bundles of assessments/policies/etc.)."""
    try:
        params = {}
        if folder:
            params["folder"] = resolve_folder_id(folder)
        res = make_get_request("/pmbok/generic-collections/", params=params)
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        items = get_paginated_results(res.json())
        if not items:
            return empty_response("generic collections", {"folder": folder})
        result = f"Found {len(items)} collections\n\n|ID|Name|Folder|\n|---|---|---|\n"
        for c in items:
            result += (
                f"|{c.get('id')}|{c.get('name', '-')}"
                f"|{(c.get('folder') or {}).get('str', '-')}|\n"
            )
        return success_response(result, "get_generic_collections", None)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def create_generic_collection(name: str, folder: str, description: str = "") -> str:
    """Create a generic collection."""
    try:
        payload = {
            "name": name,
            "folder": resolve_folder_id(folder),
            "description": description,
        }
        res = make_post_request("/pmbok/generic-collections/", payload)
        if res.status_code == 201:
            return success_response(
                f"Created generic collection {res.json().get('id')}",
                "create_generic_collection",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def delete_generic_collection(collection_id: str) -> str:
    """Delete a generic collection."""
    try:
        res = make_delete_request(f"/pmbok/generic-collections/{collection_id}/")
        if res.status_code == 204:
            return success_response(
                f"Deleted generic collection {collection_id}",
                "delete_generic_collection",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


# ---------- Responsibility matrices ----------


async def get_responsibility_matrices(folder: str = None):
    """List responsibility (RACI / similar) matrices."""
    try:
        params = {}
        if folder:
            params["folder"] = resolve_folder_id(folder)
        res = make_get_request("/pmbok/responsibility-matrices/", params=params)
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        items = get_paginated_results(res.json())
        if not items:
            return empty_response("responsibility matrices", {"folder": folder})
        result = f"Found {len(items)} matrices\n\n|ID|Name|Preset|Folder|\n|---|---|---|---|\n"
        for m in items:
            result += (
                f"|{m.get('id')}|{m.get('name', '-')}|{m.get('preset', '-')}"
                f"|{(m.get('folder') or {}).get('str', '-')}|\n"
            )
        return success_response(result, "get_responsibility_matrices", None)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def create_responsibility_matrix(
    name: str, folder: str, preset: str = None, description: str = ""
) -> str:
    """Create a responsibility matrix."""
    try:
        payload = {
            "name": name,
            "folder": resolve_folder_id(folder),
            "description": description,
        }
        if preset:
            payload["preset"] = preset
        res = make_post_request("/pmbok/responsibility-matrices/", payload)
        if res.status_code == 201:
            return success_response(
                f"Created responsibility matrix {res.json().get('id')}",
                "create_responsibility_matrix",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def delete_responsibility_matrix(matrix_id: str) -> str:
    """Delete a responsibility matrix (cascades activities, actors, assignments)."""
    try:
        res = make_delete_request(f"/pmbok/responsibility-matrices/{matrix_id}/")
        if res.status_code == 204:
            return success_response(
                f"Deleted responsibility matrix {matrix_id}",
                "delete_responsibility_matrix",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def cycle_responsibility_matrix_cell(
    matrix_id: str, activity_id: str, actor_id: str, role_id: str = None
) -> str:
    """Toggle (cycle) an assignment cell in a responsibility matrix.

    Args:
        matrix_id: Responsibility matrix UUID
        activity_id: Activity UUID
        actor_id: Actor UUID
        role_id: Optional role UUID (R/A/C/I etc.) to set explicitly
    """
    try:
        payload = {"activity": activity_id, "actor": actor_id}
        if role_id:
            payload["role"] = role_id
        res = make_post_request(
            f"/pmbok/responsibility-matrices/{matrix_id}/cycle_cell/", payload
        )
        if res.status_code in (200, 201):
            return success_response(
                f"Cycled cell for matrix {matrix_id}",
                "cycle_responsibility_matrix_cell",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def get_responsibility_roles():
    """List the role catalog (R/A/C/I, etc.)."""
    try:
        res = make_get_request("/pmbok/responsibility-roles/")
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        items = get_paginated_results(res.json())
        return success_response(
            json.dumps(items, indent=2), "get_responsibility_roles", None
        )
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)
