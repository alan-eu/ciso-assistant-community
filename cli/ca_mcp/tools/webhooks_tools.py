"""MCP tools for outbound webhooks (endpoints + audit sinks)."""

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


async def get_webhook_event_types() -> str:
    """List available event types you can subscribe a webhook to."""
    try:
        res = make_get_request("/webhooks/event-types/")
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        return success_response(
            json.dumps(res.json(), indent=2), "get_webhook_event_types", None
        )
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


# ---------- WebhookEndpoint ----------


async def get_webhook_endpoints(is_active: bool = None):
    """List webhook endpoints owned by the authenticated user."""
    try:
        params = {}
        if is_active is not None:
            params["is_active"] = str(is_active).lower()
        res = make_get_request("/webhooks/endpoints/", params=params)
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        items = get_paginated_results(res.json())
        if not items:
            return empty_response("webhook endpoints", {"is_active": is_active})
        result = f"Found {len(items)} webhook endpoints\n\n|ID|Name|URL|Format|Active|\n|---|---|---|---|---|\n"
        for w in items:
            result += (
                f"|{w.get('id')}|{w.get('name', '-')}|{w.get('url', '-')}"
                f"|{w.get('payload_format', '-')}|{w.get('is_active', '-')}|\n"
            )
        return success_response(result, "get_webhook_endpoints", None)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def create_webhook_endpoint(
    name: str,
    url: str,
    event_types: list[str],
    payload_format: str = "json",
    is_active: bool = True,
    secret: str = None,
    description: str = "",
    target_folders: list[str] = None,
) -> str:
    """Create a webhook endpoint that subscribes to event types.

    Args:
        name: Endpoint name
        url: Target URL
        event_types: Event type slugs (use get_webhook_event_types)
        payload_format: Payload format (json, cloudevents, etc.)
        is_active: Active flag
        secret: Optional shared secret for HMAC signing (write-only)
        description: Description
        target_folders: List of folder IDs/names to scope events to
    """
    try:
        payload = {
            "name": name,
            "url": url,
            "event_types": event_types,
            "payload_format": payload_format,
            "is_active": is_active,
            "description": description,
        }
        if secret is not None:
            payload["secret"] = secret
        if target_folders:
            payload["target_folders"] = [resolve_folder_id(f) for f in target_folders]
        res = make_post_request("/webhooks/endpoints/", payload)
        if res.status_code == 201:
            w = res.json()
            return success_response(
                f"Created webhook endpoint {w.get('id')} ({w.get('name')})",
                "create_webhook_endpoint",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def update_webhook_endpoint(
    endpoint_id: str,
    name: str = None,
    url: str = None,
    event_types: list[str] = None,
    payload_format: str = None,
    is_active: bool = None,
    secret: str = None,
    description: str = None,
    target_folders: list[str] = None,
) -> str:
    """Update a webhook endpoint."""
    try:
        payload = {}
        for k, v in {
            "name": name,
            "url": url,
            "event_types": event_types,
            "payload_format": payload_format,
            "is_active": is_active,
            "secret": secret,
            "description": description,
        }.items():
            if v is not None:
                payload[k] = v
        if target_folders is not None:
            payload["target_folders"] = [resolve_folder_id(f) for f in target_folders]
        if not payload:
            return error_response("No-op", "No fields provided", "Pass at least one", True)
        res = make_patch_request(f"/webhooks/endpoints/{endpoint_id}/", payload)
        if res.status_code == 200:
            return success_response(
                f"Updated webhook endpoint {endpoint_id}",
                "update_webhook_endpoint",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def delete_webhook_endpoint(endpoint_id: str) -> str:
    """Delete a webhook endpoint."""
    try:
        res = make_delete_request(f"/webhooks/endpoints/{endpoint_id}/")
        if res.status_code == 204:
            return success_response(
                f"Deleted webhook endpoint {endpoint_id}",
                "delete_webhook_endpoint",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


# ---------- AuditSink ----------


async def get_audit_sinks(is_active: bool = None):
    """List audit log sinks (admin)."""
    try:
        params = {}
        if is_active is not None:
            params["is_active"] = str(is_active).lower()
        res = make_get_request("/webhooks/audit-sinks/", params=params)
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        items = get_paginated_results(res.json())
        if not items:
            return empty_response("audit sinks", {"is_active": is_active})
        result = f"Found {len(items)} audit sinks\n\n|ID|Name|Transport|Active|\n|---|---|---|---|\n"
        for s in items:
            result += (
                f"|{s.get('id')}|{s.get('name', '-')}|{s.get('transport', '-')}"
                f"|{s.get('is_active', '-')}|\n"
            )
        return success_response(result, "get_audit_sinks", None)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def create_audit_sink(
    name: str,
    transport: str,
    folder: str,
    url: str = None,
    body_format: str = None,
    headers: dict = None,
    kafka_config: dict = None,
    is_active: bool = True,
    description: str = "",
    target_folders: list[str] = None,
) -> str:
    """Create an audit log sink.

    Args:
        name: Sink name
        transport: WEBHOOK or KAFKA
        folder: Owning folder ID/name
        url: Webhook URL (transport=WEBHOOK)
        body_format: Body format identifier
        headers: Extra HTTP headers (write-only, transport=WEBHOOK)
        kafka_config: Kafka config dict (transport=KAFKA; SASL password write-only)
        is_active: Active flag
        description: Description
        target_folders: Folder IDs/names to scope events to
    """
    try:
        payload = {
            "name": name,
            "transport": transport,
            "folder": resolve_folder_id(folder),
            "is_active": is_active,
            "description": description,
        }
        if url is not None:
            payload["url"] = url
        if body_format is not None:
            payload["body_format"] = body_format
        if headers is not None:
            payload["headers"] = headers
        if kafka_config is not None:
            payload["kafka_config"] = kafka_config
        if target_folders:
            payload["target_folders"] = [resolve_folder_id(f) for f in target_folders]
        res = make_post_request("/webhooks/audit-sinks/", payload)
        if res.status_code == 201:
            s = res.json()
            return success_response(
                f"Created audit sink {s.get('id')} ({s.get('name')})",
                "create_audit_sink",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def update_audit_sink(
    audit_sink_id: str,
    name: str = None,
    url: str = None,
    body_format: str = None,
    headers: dict = None,
    kafka_config: dict = None,
    is_active: bool = None,
    description: str = None,
    target_folders: list[str] = None,
) -> str:
    """Update an audit sink."""
    try:
        payload = {}
        for k, v in {
            "name": name,
            "url": url,
            "body_format": body_format,
            "headers": headers,
            "kafka_config": kafka_config,
            "is_active": is_active,
            "description": description,
        }.items():
            if v is not None:
                payload[k] = v
        if target_folders is not None:
            payload["target_folders"] = [resolve_folder_id(f) for f in target_folders]
        if not payload:
            return error_response("No-op", "No fields provided", "Pass at least one", True)
        res = make_patch_request(f"/webhooks/audit-sinks/{audit_sink_id}/", payload)
        if res.status_code == 200:
            return success_response(
                f"Updated audit sink {audit_sink_id}", "update_audit_sink", None
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def delete_audit_sink(audit_sink_id: str) -> str:
    """Delete an audit sink."""
    try:
        res = make_delete_request(f"/webhooks/audit-sinks/{audit_sink_id}/")
        if res.status_code == 204:
            return success_response(
                f"Deleted audit sink {audit_sink_id}", "delete_audit_sink", None
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def replay_audit_sink(audit_sink_id: str, since: str, until: str = None) -> str:
    """Re-emit historical audit events through an audit sink.

    Args:
        audit_sink_id: Audit sink UUID
        since: ISO 8601 timestamp lower bound
        until: ISO 8601 timestamp upper bound (optional)
    """
    try:
        payload = {"since": since}
        if until is not None:
            payload["until"] = until
        res = make_post_request(
            f"/webhooks/audit-sinks/{audit_sink_id}/replay/", payload
        )
        if res.status_code in (200, 201, 202):
            return success_response(
                f"Replayed audit sink {audit_sink_id} from {since}",
                "replay_audit_sink",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)
