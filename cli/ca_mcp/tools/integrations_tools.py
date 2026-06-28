"""MCP tools for integrations (external systems: Jira, ServiceNow, etc.)."""

import json

from ..client import (
    make_get_request,
    make_post_request,
    make_patch_request,
    make_delete_request,
    get_paginated_results,
)
from ..resolvers import resolve_folder_id
from ..utils.response_formatter import (
    empty_response,
    error_response,
    http_error_response,
    success_response,
)


async def get_integration_providers():
    """List available integration providers (Jira, ServiceNow, ...)."""
    try:
        res = make_get_request("/integrations/providers/")
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        data = res.json()
        return success_response(
            json.dumps(data, indent=2), "get_integration_providers", None
        )
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def get_integration_configurations(folder: str = None, provider: str = None, is_active: bool = None):
    """List integration configurations.

    Args:
        folder: Folder ID/name
        provider: Provider id filter
        is_active: Active flag filter
    """
    try:
        params = {}
        filters = {}
        if folder:
            params["folder"] = resolve_folder_id(folder)
            filters["folder"] = folder
        if provider:
            params["provider"] = provider
            filters["provider"] = provider
        if is_active is not None:
            params["is_active"] = str(is_active).lower()
            filters["is_active"] = is_active
        res = make_get_request("/integrations/configs/", params=params)
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        items = get_paginated_results(res.json())
        if not items:
            return empty_response("integration configurations", filters)
        result = f"Found {len(items)} integration configurations\n\n|ID|Provider|Folder|Active|\n|---|---|---|---|\n"
        for c in items:
            result += (
                f"|{c.get('id')}|{c.get('provider', '-')}"
                f"|{(c.get('folder') or {}).get('str', '-')}"
                f"|{c.get('is_active', '-')}|\n"
            )
        return success_response(result, "get_integration_configurations", None)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def get_integration_configuration(configuration_id: str):
    """Retrieve a single integration configuration (credentials are stripped)."""
    try:
        res = make_get_request(f"/integrations/configs/{configuration_id}/")
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        return success_response(
            json.dumps(res.json(), indent=2), "get_integration_configuration", None
        )
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def create_integration_configuration(
    provider_id: str,
    folder: str,
    credentials: dict,
    settings: dict = None,
    is_active: bool = True,
    webhook_secret: str = None,
) -> str:
    """Create an integration configuration.

    Args:
        provider_id: Provider identifier (use get_integration_providers to list)
        folder: Folder ID/name
        credentials: Provider-specific credential dict (validated server-side)
        settings: Provider-specific settings dict
        is_active: Active flag
        webhook_secret: Shared secret for inbound webhook calls
    """
    try:
        payload = {
            "provider_id": provider_id,
            "folder_id": resolve_folder_id(folder),
            "credentials": credentials,
            "is_active": is_active,
        }
        if settings is not None:
            payload["settings"] = settings
        if webhook_secret is not None:
            payload["webhook_secret"] = webhook_secret
        res = make_post_request("/integrations/configs/", payload)
        if res.status_code == 201:
            c = res.json()
            return success_response(
                f"Created integration configuration {c.get('id')}",
                "create_integration_configuration",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def update_integration_configuration(
    configuration_id: str,
    credentials: dict = None,
    settings: dict = None,
    is_active: bool = None,
    webhook_secret: str = None,
) -> str:
    """Update an integration configuration."""
    try:
        payload = {}
        if credentials is not None:
            payload["credentials"] = credentials
        if settings is not None:
            payload["settings"] = settings
        if is_active is not None:
            payload["is_active"] = is_active
        if webhook_secret is not None:
            payload["webhook_secret"] = webhook_secret
        if not payload:
            return error_response("No-op", "No fields provided", "Pass at least one", True)
        res = make_patch_request(f"/integrations/configs/{configuration_id}/", payload)
        if res.status_code == 200:
            return success_response(
                f"Updated integration configuration {configuration_id}",
                "update_integration_configuration",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def delete_integration_configuration(configuration_id: str) -> str:
    """Delete an integration configuration."""
    try:
        res = make_delete_request(f"/integrations/configs/{configuration_id}/")
        if res.status_code == 204:
            return success_response(
                f"Deleted integration configuration {configuration_id}",
                "delete_integration_configuration",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def test_integration_connection(provider_id: str, credentials: dict) -> str:
    """Test credentials against a provider without persisting them.

    Args:
        provider_id: Provider identifier
        credentials: Credential dict
    """
    try:
        res = make_post_request(
            "/integrations/test-connection/",
            {"provider_id": provider_id, "credentials": credentials},
        )
        if res.status_code in (200, 201):
            return success_response(
                json.dumps(res.json(), indent=2),
                "test_integration_connection",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def list_integration_remote_objects(configuration_id: str) -> str:
    """List remote objects available through a configured integration."""
    try:
        res = make_get_request(
            f"/integrations/configs/{configuration_id}/list-remote-objects/"
        )
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        return success_response(
            json.dumps(res.json(), indent=2),
            "list_integration_remote_objects",
            None,
        )
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def run_integration_rpc(configuration_id: str, action: str, params: dict = None) -> str:
    """Run a generic RPC action against an integration.

    Args:
        configuration_id: Integration configuration UUID
        action: Action name (provider-specific)
        params: Action-specific params
    """
    try:
        res = make_post_request(
            f"/integrations/configs/{configuration_id}/rpc/",
            {"action": action, "params": params or {}},
        )
        if res.status_code in (200, 201):
            return success_response(
                json.dumps(res.json(), indent=2), "run_integration_rpc", None
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)
