"""MCP tools for security intelligence: advisories and CWEs."""

import json

from ..client import (
    make_get_request,
    make_post_request,
    make_patch_request,
    make_delete_request,
    get_paginated_results,
)
from ..resolvers import resolve_folder_id, resolve_id_or_name
from ..utils.response_formatter import (
    empty_response,
    error_response,
    http_error_response,
    success_response,
)


# ---------- Security advisories ----------


async def get_security_advisories(
    folder: str = None,
    provider: str = None,
    source: str = None,
    urn: str = None,
):
    """List security advisories.

    Args:
        folder: Folder ID/name
        provider: Provider tag
        source: Source (e.g. nvd, euvd, kev, manual)
        urn: Exact URN match
    """
    try:
        params, filters = {}, {}
        if folder:
            params["folder"] = resolve_folder_id(folder)
            filters["folder"] = folder
        if provider:
            params["provider"] = provider
            filters["provider"] = provider
        if source:
            params["source"] = source
            filters["source"] = source
        if urn:
            params["urn"] = urn
            filters["urn"] = urn
        res = make_get_request("/security-advisories/", params=params)
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        items = get_paginated_results(res.json())
        if not items:
            return empty_response("security advisories", filters)
        result = f"Found {len(items)} security advisories\n\n|ID|Ref ID|Name|Source|CVSS|EPSS|\n|---|---|---|---|---|---|\n"
        for a in items:
            result += (
                f"|{a.get('id')}|{a.get('ref_id', '-')}|{a.get('name', '-')}"
                f"|{a.get('source', '-')}|{a.get('cvss_score', '-')}"
                f"|{a.get('epss_score', '-')}|\n"
            )
        return success_response(result, "get_security_advisories", None)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def get_security_advisory(advisory_id: str):
    """Retrieve a single security advisory (full JSON, includes references/aliases)."""
    try:
        resolved = resolve_id_or_name(advisory_id, "/security-advisories/")
        res = make_get_request(f"/security-advisories/{resolved}/")
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        return success_response(
            json.dumps(res.json(), indent=2), "get_security_advisory", None
        )
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def create_security_advisory(
    name: str,
    folder: str,
    ref_id: str = None,
    description: str = "",
    cvss_vector: str = None,
    cvss_score: float = None,
    references: list = None,
    aliases: list = None,
    source: str = "manual",
) -> str:
    """Create a manual security advisory."""
    try:
        payload = {
            "name": name,
            "folder": resolve_folder_id(folder),
            "description": description,
            "source": source,
        }
        for k, v in {
            "ref_id": ref_id,
            "cvss_vector": cvss_vector,
            "cvss_score": cvss_score,
            "references": references,
            "aliases": aliases,
        }.items():
            if v is not None:
                payload[k] = v
        res = make_post_request("/security-advisories/", payload)
        if res.status_code == 201:
            return success_response(
                f"Created security advisory {res.json().get('id')}",
                "create_security_advisory",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def delete_security_advisory(advisory_id: str) -> str:
    """Delete a security advisory."""
    try:
        resolved = resolve_id_or_name(advisory_id, "/security-advisories/")
        res = make_delete_request(f"/security-advisories/{resolved}/")
        if res.status_code == 204:
            return success_response(
                f"Deleted security advisory {resolved}",
                "delete_security_advisory",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def sync_kev_advisories() -> str:
    """Sync the CISA KEV (Known Exploited Vulnerabilities) catalog."""
    try:
        res = make_post_request("/security-advisories/sync_kev/", {})
        if res.status_code in (200, 201, 202):
            return success_response(
                f"KEV sync started: {res.text}", "sync_kev_advisories", None
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def sync_euvd_advisories() -> str:
    """Sync the EUVD (European Vulnerability Database) catalog."""
    try:
        res = make_post_request("/security-advisories/sync_euvd/", {})
        if res.status_code in (200, 201, 202):
            return success_response(
                f"EUVD sync started: {res.text}", "sync_euvd_advisories", None
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def enrich_security_advisory(advisory_id: str) -> str:
    """Enrich an advisory with external data (CVSS, EPSS, references)."""
    try:
        resolved = resolve_id_or_name(advisory_id, "/security-advisories/")
        res = make_post_request(f"/security-advisories/{resolved}/enrich/", {})
        if res.status_code in (200, 201, 202):
            return success_response(
                f"Enriched advisory {resolved}", "enrich_security_advisory", None
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


# ---------- CWEs ----------


async def get_cwes(folder: str = None, provider: str = None, urn: str = None):
    """List CWE (Common Weakness Enumeration) entries."""
    try:
        params, filters = {}, {}
        if folder:
            params["folder"] = resolve_folder_id(folder)
            filters["folder"] = folder
        if provider:
            params["provider"] = provider
            filters["provider"] = provider
        if urn:
            params["urn"] = urn
            filters["urn"] = urn
        res = make_get_request("/cwes/", params=params)
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        items = get_paginated_results(res.json())
        if not items:
            return empty_response("CWEs", filters)
        result = f"Found {len(items)} CWEs\n\n|ID|Ref ID|Name|Provider|\n|---|---|---|---|\n"
        for c in items:
            result += (
                f"|{c.get('id')}|{c.get('ref_id', '-')}|{c.get('name', '-')}"
                f"|{c.get('provider', '-')}|\n"
            )
        return success_response(result, "get_cwes", None)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def get_cwe(cwe_id: str):
    """Retrieve a single CWE entry."""
    try:
        resolved = resolve_id_or_name(cwe_id, "/cwes/")
        res = make_get_request(f"/cwes/{resolved}/")
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        return success_response(json.dumps(res.json(), indent=2), "get_cwe", None)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def sync_cwe_catalog() -> str:
    """Sync the MITRE CWE catalog."""
    try:
        res = make_post_request("/cwes/sync_catalog/", {})
        if res.status_code in (200, 201, 202):
            return success_response(
                f"CWE catalog sync started: {res.text}",
                "sync_cwe_catalog",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)
