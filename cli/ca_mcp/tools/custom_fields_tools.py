"""MCP tools for custom field definitions.

The custom_fields feature is gated; reads return empty if the feature flag is
off, writes return 403.
"""

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


async def get_custom_field_definitions(
    model: str = None, for_folder: str = None
):
    """List custom field definitions.

    Args:
        model: app_label.model string (e.g. "core.appliedcontrol") to filter
        for_folder: Folder ID/name — also returns global + ancestor-owned defs
    """
    try:
        params = {}
        filters = {}
        if model:
            params["model"] = model
            filters["model"] = model
        if for_folder:
            params["for_folder"] = resolve_folder_id(for_folder)
            filters["for_folder"] = for_folder
        res = make_get_request("/custom-fields/", params=params)
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        items = get_paginated_results(res.json())
        if not items:
            return empty_response("custom field definitions", filters)
        result = f"Found {len(items)} custom field definitions\n\n"
        result += "|ID|Key|Label|Type|Model|Required|Filterable|Folder|\n"
        result += "|---|---|---|---|---|---|---|---|\n"
        for f in items:
            result += (
                f"|{f.get('id')}|{f.get('key', '-')}|{f.get('label', '-')}"
                f"|{f.get('field_type', '-')}|{f.get('model', '-')}"
                f"|{f.get('required', '-')}|{f.get('filterable', '-')}"
                f"|{(f.get('folder') or {}).get('str', '-')}|\n"
            )
        return success_response(result, "get_custom_field_definitions", None)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def get_custom_field_definition(definition_id: str):
    """Retrieve a custom field definition (with its choices for CHOICE types)."""
    try:
        res = make_get_request(f"/custom-fields/{definition_id}/")
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        return success_response(
            json.dumps(res.json(), indent=2), "get_custom_field_definition", None
        )
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def create_custom_field_definition(
    key: str,
    label: str,
    field_type: str,
    model: str,
    folder: str = None,
    help_text: str = "",
    required: bool = False,
    filterable: bool = False,
    visible: bool = True,
    searchable: bool = False,
    order: int = None,
    choices: list[dict] = None,
) -> str:
    """Create a custom field definition.

    Args:
        key: Field key (unique per model)
        label: Display label
        field_type: text | number | date | choice | multi_choice | boolean | url
        model: app_label.model (e.g. "core.appliedcontrol")
        folder: Folder ID/name (omit for global)
        help_text: Help text
        required: Required flag
        filterable: Surface this field in list filters
        visible: Visible by default
        searchable: Searchable (text/choice/multi-choice only)
        order: Display order integer
        choices: For choice/multi-choice fields, list of {value, label} dicts
    """
    try:
        payload = {
            "key": key,
            "label": label,
            "field_type": field_type,
            "model": model,
            "help_text": help_text,
            "required": required,
            "filterable": filterable,
            "visible": visible,
            "searchable": searchable,
        }
        if folder:
            payload["folder"] = resolve_folder_id(folder)
        if order is not None:
            payload["order"] = order
        if choices is not None:
            payload["choices"] = choices
        res = make_post_request("/custom-fields/", payload)
        if res.status_code == 201:
            f = res.json()
            return success_response(
                f"Created custom field '{f.get('key')}' (ID: {f.get('id')})",
                "create_custom_field_definition",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def update_custom_field_definition(
    definition_id: str,
    label: str = None,
    help_text: str = None,
    required: bool = None,
    filterable: bool = None,
    visible: bool = None,
    searchable: bool = None,
    order: int = None,
    choices: list[dict] = None,
) -> str:
    """Update a custom field definition.

    Note: field_type cannot be changed if values exist. The key+model pair is
    immutable.
    """
    try:
        payload = {
            k: v
            for k, v in {
                "label": label,
                "help_text": help_text,
                "required": required,
                "filterable": filterable,
                "visible": visible,
                "searchable": searchable,
                "order": order,
                "choices": choices,
            }.items()
            if v is not None
        }
        if not payload:
            return error_response("No-op", "No fields provided", "Pass at least one", True)
        res = make_patch_request(f"/custom-fields/{definition_id}/", payload)
        if res.status_code == 200:
            return success_response(
                f"Updated custom field definition {definition_id}",
                "update_custom_field_definition",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def delete_custom_field_definition(definition_id: str) -> str:
    """Delete a custom field definition (and its stored values)."""
    try:
        res = make_delete_request(f"/custom-fields/{definition_id}/")
        if res.status_code == 204:
            return success_response(
                f"Deleted custom field definition {definition_id}",
                "delete_custom_field_definition",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)
