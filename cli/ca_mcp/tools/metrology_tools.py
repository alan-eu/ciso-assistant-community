"""MCP tools for metrology (metric definitions, instances, samples, dashboards)."""

import json

from ..client import (
    make_get_request,
    make_post_request,
    make_patch_request,
    make_delete_request,
    get_paginated_results,
)
from ..resolvers import resolve_folder_id, resolve_id_or_name
from ..utils.detail_formatter import fmt_m2m_cell
from ..utils.response_formatter import (
    empty_response,
    error_response,
    http_error_response,
    success_response,
)


# ---------- Metric definitions ----------


async def get_metric_definitions(
    folder: str = None,
    category: str = None,
    unit: str = None,
    provider: str = None,
    is_published: bool = None,
):
    """List metric definitions (the 'what' of a metric)."""
    try:
        params, filters = {}, {}
        if folder:
            params["folder"] = resolve_folder_id(folder)
            filters["folder"] = folder
        if category:
            params["category"] = category
            filters["category"] = category
        if unit:
            params["unit"] = unit
            filters["unit"] = unit
        if provider:
            params["provider"] = provider
            filters["provider"] = provider
        if is_published is not None:
            params["is_published"] = str(is_published).lower()
            filters["is_published"] = is_published
        res = make_get_request("/metrology/metric-definitions/", params=params)
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        items = get_paginated_results(res.json())
        if not items:
            return empty_response("metric definitions", filters)
        result = f"Found {len(items)} metric definitions\n\n|ID|Name|Category|Unit|Provider|Published|\n|---|---|---|---|---|---|\n"
        for m in items:
            result += (
                f"|{m.get('id')}|{m.get('name', '-')}|{m.get('category', '-')}"
                f"|{m.get('unit', '-')}|{m.get('provider', '-')}"
                f"|{m.get('is_published', '-')}|\n"
            )
        return success_response(result, "get_metric_definitions", None)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def create_metric_definition(
    name: str,
    category: str,
    folder: str,
    description: str = "",
    unit: str = None,
    provider: str = None,
    is_published: bool = True,
) -> str:
    """Create a metric definition.

    Args:
        name: Metric name
        category: Category
        folder: Folder ID/name
        description: Description
        unit: Unit (e.g. "%", "count", "days")
        provider: Provider tag
        is_published: Visible to instance creators
    """
    try:
        payload = {
            "name": name,
            "category": category,
            "folder": resolve_folder_id(folder),
            "description": description,
            "is_published": is_published,
        }
        if unit:
            payload["unit"] = unit
        if provider:
            payload["provider"] = provider
        res = make_post_request("/metrology/metric-definitions/", payload)
        if res.status_code == 201:
            m = res.json()
            return success_response(
                f"Created metric definition '{m.get('name')}' (ID: {m.get('id')})",
                "create_metric_definition",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def update_metric_definition(
    metric_definition_id: str,
    name: str = None,
    description: str = None,
    category: str = None,
    unit: str = None,
    is_published: bool = None,
) -> str:
    """Update a metric definition."""
    try:
        payload = {
            k: v
            for k, v in {
                "name": name,
                "description": description,
                "category": category,
                "unit": unit,
                "is_published": is_published,
            }.items()
            if v is not None
        }
        if not payload:
            return error_response("No-op", "No fields provided", "Pass at least one", True)
        res = make_patch_request(
            f"/metrology/metric-definitions/{metric_definition_id}/", payload
        )
        if res.status_code == 200:
            return success_response(
                f"Updated metric definition {metric_definition_id}",
                "update_metric_definition",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def delete_metric_definition(metric_definition_id: str) -> str:
    """Delete a metric definition."""
    try:
        res = make_delete_request(
            f"/metrology/metric-definitions/{metric_definition_id}/"
        )
        if res.status_code == 204:
            return success_response(
                f"Deleted metric definition {metric_definition_id}",
                "delete_metric_definition",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


# ---------- Metric instances ----------


async def get_metric_instances(
    folder: str = None,
    metric_definition: str = None,
    status: str = None,
    collection_frequency: str = None,
):
    """List metric instances (instantiations of a metric definition)."""
    try:
        params, filters = {}, {}
        if folder:
            params["folder"] = resolve_folder_id(folder)
            filters["folder"] = folder
        if metric_definition:
            params["metric_definition"] = resolve_id_or_name(
                metric_definition, "/metrology/metric-definitions/"
            )
            filters["metric_definition"] = metric_definition
        if status:
            params["status"] = status
            filters["status"] = status
        if collection_frequency:
            params["collection_frequency"] = collection_frequency
            filters["collection_frequency"] = collection_frequency
        res = make_get_request("/metrology/metric-instances/", params=params)
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        items = get_paginated_results(res.json())
        if not items:
            return empty_response("metric instances", filters)
        result = f"Found {len(items)} metric instances\n\n|ID|Name|Definition|Status|Frequency|Owner|\n|---|---|---|---|---|---|\n"
        for mi in items:
            result += (
                f"|{mi.get('id')}|{mi.get('name', '-')}"
                f"|{(mi.get('metric_definition') or {}).get('str', '-')}"
                f"|{mi.get('status', '-')}|{mi.get('collection_frequency', '-')}"
                f"|{fmt_m2m_cell(mi.get('owner'), max_inline=2)}|\n"
            )
        return success_response(result, "get_metric_instances", None)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def create_metric_instance(
    name: str,
    metric_definition: str,
    folder: str,
    status: str = None,
    collection_frequency: str = None,
) -> str:
    """Create a metric instance."""
    try:
        payload = {
            "name": name,
            "metric_definition": resolve_id_or_name(
                metric_definition, "/metrology/metric-definitions/"
            ),
            "folder": resolve_folder_id(folder),
        }
        if status:
            payload["status"] = status
        if collection_frequency:
            payload["collection_frequency"] = collection_frequency
        res = make_post_request("/metrology/metric-instances/", payload)
        if res.status_code == 201:
            mi = res.json()
            return success_response(
                f"Created metric instance '{mi.get('name')}' (ID: {mi.get('id')})",
                "create_metric_instance",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def update_metric_instance(
    metric_instance_id: str,
    name: str = None,
    status: str = None,
    collection_frequency: str = None,
) -> str:
    """Update a metric instance."""
    try:
        payload = {
            k: v
            for k, v in {
                "name": name,
                "status": status,
                "collection_frequency": collection_frequency,
            }.items()
            if v is not None
        }
        if not payload:
            return error_response("No-op", "No fields provided", "Pass at least one", True)
        res = make_patch_request(
            f"/metrology/metric-instances/{metric_instance_id}/", payload
        )
        if res.status_code == 200:
            return success_response(
                f"Updated metric instance {metric_instance_id}",
                "update_metric_instance",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def delete_metric_instance(metric_instance_id: str) -> str:
    """Delete a metric instance."""
    try:
        res = make_delete_request(
            f"/metrology/metric-instances/{metric_instance_id}/"
        )
        if res.status_code == 204:
            return success_response(
                f"Deleted metric instance {metric_instance_id}",
                "delete_metric_instance",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


# ---------- Custom metric samples ----------


async def get_custom_metric_samples(metric_instance: str = None):
    """List custom metric samples (user-recorded observations)."""
    try:
        params = {}
        if metric_instance:
            params["metric_instance"] = resolve_id_or_name(
                metric_instance, "/metrology/metric-instances/"
            )
        res = make_get_request("/metrology/custom-metric-samples/", params=params)
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        items = get_paginated_results(res.json())
        if not items:
            return empty_response("custom metric samples", {"metric_instance": metric_instance})
        result = f"Found {len(items)} custom samples\n\n|ID|Instance|Timestamp|Observation|\n|---|---|---|---|\n"
        for s in items:
            obs = (s.get("observation") or "")
            if isinstance(obs, (dict, list)):
                obs = json.dumps(obs)[:80]
            result += (
                f"|{s.get('id')}"
                f"|{(s.get('metric_instance') or {}).get('str', '-')}"
                f"|{s.get('timestamp', '-')}|{obs}|\n"
            )
        return success_response(result, "get_custom_metric_samples", None)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def create_custom_metric_sample(
    metric_instance: str, observation, timestamp: str
) -> str:
    """Record a sample for a custom metric instance.

    Args:
        metric_instance: Metric instance ID/name
        observation: Observation value (str/number/dict depending on metric)
        timestamp: ISO 8601 datetime
    """
    try:
        payload = {
            "metric_instance": resolve_id_or_name(
                metric_instance, "/metrology/metric-instances/"
            ),
            "observation": observation,
            "timestamp": timestamp,
        }
        res = make_post_request("/metrology/custom-metric-samples/", payload)
        if res.status_code == 201:
            return success_response(
                f"Recorded sample for {metric_instance} at {timestamp}",
                "create_custom_metric_sample",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


# ---------- Dashboards & widgets ----------


async def get_dashboards(folder: str = None):
    """List dashboards."""
    try:
        params = {}
        if folder:
            params["folder"] = resolve_folder_id(folder)
        res = make_get_request("/metrology/dashboards/", params=params)
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        items = get_paginated_results(res.json())
        if not items:
            return empty_response("dashboards", {"folder": folder})
        result = f"Found {len(items)} dashboards\n\n|ID|Name|Folder|\n|---|---|---|\n"
        for d in items:
            result += (
                f"|{d.get('id')}|{d.get('name', '-')}"
                f"|{(d.get('folder') or {}).get('str', '-')}|\n"
            )
        return success_response(result, "get_dashboards", None)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def create_dashboard(name: str, folder: str, description: str = "") -> str:
    """Create a dashboard."""
    try:
        payload = {
            "name": name,
            "folder": resolve_folder_id(folder),
            "description": description,
        }
        res = make_post_request("/metrology/dashboards/", payload)
        if res.status_code == 201:
            d = res.json()
            return success_response(
                f"Created dashboard {d.get('id')}", "create_dashboard", None
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def delete_dashboard(dashboard_id: str) -> str:
    """Delete a dashboard."""
    try:
        res = make_delete_request(f"/metrology/dashboards/{dashboard_id}/")
        if res.status_code == 204:
            return success_response(
                f"Deleted dashboard {dashboard_id}", "delete_dashboard", None
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def get_dashboard_widgets(dashboard: str = None):
    """List dashboard widgets."""
    try:
        params = {}
        if dashboard:
            params["dashboard"] = resolve_id_or_name(dashboard, "/metrology/dashboards/")
        res = make_get_request("/metrology/dashboard-widgets/", params=params)
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        items = get_paginated_results(res.json())
        if not items:
            return empty_response("dashboard widgets", {"dashboard": dashboard})
        result = f"Found {len(items)} widgets\n\n|ID|Dashboard|Chart|Metric Instance|Position|\n|---|---|---|---|---|\n"
        for w in items:
            result += (
                f"|{w.get('id')}"
                f"|{(w.get('dashboard') or {}).get('str', '-')}"
                f"|{w.get('chart_type', '-')}"
                f"|{(w.get('metric_instance') or {}).get('str', '-')}"
                f"|({w.get('position_x', 0)},{w.get('position_y', 0)})|\n"
            )
        return success_response(result, "get_dashboard_widgets", None)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)
