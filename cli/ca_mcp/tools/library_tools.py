"""Library management MCP tools for CISO Assistant"""

import json

from ..client import (
    make_get_request,
    make_post_request,
    make_delete_request,
    fetch_all_results,
)
from ..resolvers import resolve_library_id


async def get_stored_libraries(
    object_type: str = None,
    provider: str = None,
):
    """List available libraries (frameworks) for import. Use URN/ID with import_stored_library()

    Args:
        object_type: Object type (e.g. "framework", "risk_matrix")
        provider: Provider name
    """
    try:
        params = {}
        if object_type:
            params["object_type"] = object_type
        if provider:
            params["provider"] = provider

        # Fetch all stored libraries (with pagination)
        libraries, error = fetch_all_results("/stored-libraries/", params=params)
        if error:
            return error

        if not libraries:
            return "No stored libraries found"

        result = f"Found {len(libraries)} stored libraries\n\n"
        result += "|URN|Name|Version|Provider|\n"
        result += "|---|---|---|---|\n"

        for lib in libraries:
            urn = lib.get("urn", "N/A")
            name = lib.get("name", "N/A")
            version = lib.get("version", "N/A")
            provider = lib.get("provider", "N/A")

            result += f"|{urn}|{name}|{version}|{provider}|\n"

        return result
    except Exception as e:
        return f"Error in get_stored_libraries: {str(e)}"


async def get_loaded_libraries():
    """List loaded/imported libraries (frameworks) activated in the system"""
    try:
        # Fetch all loaded libraries (with pagination)
        libraries, error = fetch_all_results("/loaded-libraries/")
        if error:
            return error

        if not libraries:
            return "No loaded libraries found"

        result = f"Found {len(libraries)} loaded libraries\n\n"
        result += "|URN|Name|Version|Provider|\n"
        result += "|---|---|---|---|\n"

        for lib in libraries:
            urn = lib.get("urn", "N/A")
            name = lib.get("name", "N/A")
            version = lib.get("version", "N/A")
            provider = lib.get("provider", "N/A")

            result += f"|{urn}|{name}|{version}|{provider}|\n"

        return result
    except Exception as e:
        return f"Error in get_loaded_libraries: {str(e)}"


async def import_stored_library(urn_or_id: str) -> str:
    """Import library (framework) to make it available for compliance assessments. Use get_stored_libraries() to find URNs

    Args:
        urn_or_id: Library URN/ID (e.g. "urn:intuitem:risk:library:nist-csf-2.0")
    """
    try:
        res = make_post_request(f"/stored-libraries/{urn_or_id}/import/", {})

        if res.status_code == 200:
            result = res.json()
            if result.get("status") == "success":
                return f"Imported library: {urn_or_id}"
            else:
                error = result.get("error", "Unknown error")
                return f"Error importing library: {error}"
        else:
            return f"Error importing library: {res.status_code} - {res.text}"
    except Exception as e:
        return f"Error in import_stored_library: {str(e)}"


async def get_stored_library_content(urn_or_id: str) -> str:
    """Fetch the processed content of a stored library."""
    try:
        res = make_get_request(f"/stored-libraries/{urn_or_id}/content/")
        if res.status_code != 200:
            return f"Error: HTTP {res.status_code} - {res.text}"
        return json.dumps(res.json(), indent=2)
    except Exception as e:
        return f"Error in get_stored_library_content: {str(e)}"


async def get_stored_library_tree(urn_or_id: str) -> str:
    """Fetch the requirement-nodes hierarchy of a stored library."""
    try:
        res = make_get_request(f"/stored-libraries/{urn_or_id}/tree/")
        if res.status_code != 200:
            return f"Error: HTTP {res.status_code} - {res.text}"
        return json.dumps(res.json(), indent=2)
    except Exception as e:
        return f"Error in get_stored_library_tree: {str(e)}"


async def delete_stored_library(urn_or_id: str) -> str:
    """Delete a stored library (the source, not the loaded copy)."""
    try:
        res = make_delete_request(f"/stored-libraries/{urn_or_id}/")
        if res.status_code == 204:
            return f"Deleted stored library {urn_or_id}"
        return f"Error: HTTP {res.status_code} - {res.text}"
    except Exception as e:
        return f"Error in delete_stored_library: {str(e)}"


async def unload_stored_library(urn_or_id: str) -> str:
    """Unload a stored library (removes its loaded copy if present)."""
    try:
        res = make_post_request(f"/stored-libraries/{urn_or_id}/unload/", {})
        if res.status_code in (200, 204):
            return f"Unloaded stored library {urn_or_id}"
        return f"Error: HTTP {res.status_code} - {res.text}"
    except Exception as e:
        return f"Error in unload_stored_library: {str(e)}"


async def get_loaded_library_content(library_id: str) -> str:
    """Fetch metadata about the loaded library's objects (frameworks, matrices, ...)."""
    try:
        resolved = resolve_library_id(library_id)
        res = make_get_request(f"/loaded-libraries/{resolved}/content/")
        if res.status_code != 200:
            return f"Error: HTTP {res.status_code} - {res.text}"
        return json.dumps(res.json(), indent=2)
    except Exception as e:
        return f"Error in get_loaded_library_content: {str(e)}"


async def get_loaded_library_tree(library_id: str) -> str:
    """Fetch the requirement-nodes hierarchy of a loaded library."""
    try:
        resolved = resolve_library_id(library_id)
        res = make_get_request(f"/loaded-libraries/{resolved}/tree/")
        if res.status_code != 200:
            return f"Error: HTTP {res.status_code} - {res.text}"
        return json.dumps(res.json(), indent=2)
    except Exception as e:
        return f"Error in get_loaded_library_tree: {str(e)}"


async def delete_loaded_library(library_id: str) -> str:
    """Unload (delete) a loaded library. Fails if any object still references it."""
    try:
        resolved = resolve_library_id(library_id)
        res = make_delete_request(f"/loaded-libraries/{resolved}/")
        if res.status_code == 204:
            return f"Deleted loaded library {resolved}"
        return f"Error: HTTP {res.status_code} - {res.text}"
    except Exception as e:
        return f"Error in delete_loaded_library: {str(e)}"


async def update_loaded_library(library_id: str, action: str = "rule_of_three") -> str:
    """Apply a pending update to a loaded library.

    Args:
        library_id: Loaded library URN or UUID
        action: rule_of_three (merge upgrades, keep custom edits) | reset | clamp
    """
    try:
        resolved = resolve_library_id(library_id)
        res = make_get_request(
            f"/loaded-libraries/{resolved}/update/", params={"action": action}
        )
        if res.status_code in (200, 201, 204):
            return f"Applied '{action}' update to loaded library {resolved}"
        return f"Error: HTTP {res.status_code} - {res.text}"
    except Exception as e:
        return f"Error in update_loaded_library: {str(e)}"


async def get_available_loaded_library_updates() -> str:
    """List loaded libraries that have a newer stored version available."""
    try:
        res = make_get_request("/loaded-libraries/available_updates/")
        if res.status_code != 200:
            return f"Error: HTTP {res.status_code} - {res.text}"
        return json.dumps(res.json(), indent=2)
    except Exception as e:
        return f"Error in get_available_loaded_library_updates: {str(e)}"
