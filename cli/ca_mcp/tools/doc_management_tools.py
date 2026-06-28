"""MCP tools for document management (managed documents + revisions)."""

import json

from ..client import (
    make_get_request,
    make_post_request,
    make_patch_request,
    make_delete_request,
    get_paginated_results,
)
from ..resolvers import resolve_folder_id, resolve_policy_id
from ..utils.response_formatter import (
    empty_response,
    error_response,
    http_error_response,
    success_response,
)


# ---------- Managed documents ----------


async def get_managed_documents(folder: str = None):
    """List managed documents."""
    try:
        params = {}
        filters = {}
        if folder:
            params["folder"] = resolve_folder_id(folder)
            filters["folder"] = folder
        res = make_get_request("/managed-documents/", params=params)
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        items = get_paginated_results(res.json())
        if not items:
            return empty_response("managed documents", filters)
        result = f"Found {len(items)} managed documents\n\n|ID|Policy|Doc Type|Locale|Folder|\n|---|---|---|---|---|\n"
        for d in items:
            result += (
                f"|{d.get('id')}"
                f"|{(d.get('policy') or {}).get('str', '-')}"
                f"|{d.get('document_type', '-')}|{d.get('locale', '-')}"
                f"|{(d.get('folder') or {}).get('str', '-')}|\n"
            )
        return success_response(result, "get_managed_documents", None)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def get_managed_document(managed_document_id: str):
    """Retrieve a single managed document."""
    try:
        res = make_get_request(f"/managed-documents/{managed_document_id}/")
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        return success_response(
            json.dumps(res.json(), indent=2), "get_managed_document", None
        )
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def create_managed_document(
    policy: str,
    document_type: str,
    folder: str,
    locale: str = "en",
    default_locale: bool = True,
    template_used: str = None,
) -> str:
    """Create a managed document tied to a policy.

    Args:
        policy: Policy ID/name
        document_type: Document type identifier
        folder: Folder ID/name
        locale: Locale code
        default_locale: Whether this is the default locale
        template_used: Optional template identifier
    """
    try:
        payload = {
            "policy": resolve_policy_id(policy),
            "document_type": document_type,
            "folder": resolve_folder_id(folder),
            "locale": locale,
            "default_locale": default_locale,
        }
        if template_used is not None:
            payload["template_used"] = template_used
        res = make_post_request("/managed-documents/", payload)
        if res.status_code == 201:
            d = res.json()
            return success_response(
                f"Created managed document {d.get('id')}",
                "create_managed_document",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def delete_managed_document(managed_document_id: str) -> str:
    """Delete a managed document and all its revisions."""
    try:
        res = make_delete_request(f"/managed-documents/{managed_document_id}/")
        if res.status_code == 204:
            return success_response(
                f"Deleted managed document {managed_document_id}",
                "delete_managed_document",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


# ---------- Document revisions ----------


async def get_document_revisions(managed_document: str = None, status: str = None):
    """List document revisions.

    Args:
        managed_document: Managed document UUID filter
        status: Status filter (draft, in_review, validated, published, change_requested)
    """
    try:
        params = {}
        filters = {}
        if managed_document:
            params["managed_document"] = managed_document
            filters["managed_document"] = managed_document
        if status:
            params["status"] = status
            filters["status"] = status
        res = make_get_request("/document-revisions/", params=params)
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        items = get_paginated_results(res.json())
        if not items:
            return empty_response("document revisions", filters)
        result = f"Found {len(items)} document revisions\n\n|ID|Document|Version|Status|Author|Updated|\n|---|---|---|---|---|---|\n"
        for r in items:
            result += (
                f"|{r.get('id')}"
                f"|{(r.get('managed_document') or {}).get('str', '-')}"
                f"|{r.get('version_number', '-')}|{r.get('status', '-')}"
                f"|{(r.get('author') or {}).get('str', '-')}"
                f"|{r.get('updated_at', '-')}|\n"
            )
        return success_response(result, "get_document_revisions", None)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def get_document_revision(revision_id: str):
    """Retrieve a single document revision (full markdown content)."""
    try:
        res = make_get_request(f"/document-revisions/{revision_id}/")
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        return success_response(
            json.dumps(res.json(), indent=2), "get_document_revision", None
        )
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def update_document_revision(
    revision_id: str,
    content: str = None,
    change_summary: str = None,
) -> str:
    """Update a document revision's content (draft status only).

    Args:
        revision_id: Revision UUID
        content: New markdown content
        change_summary: Change summary
    """
    try:
        payload = {}
        if content is not None:
            payload["content"] = content
        if change_summary is not None:
            payload["change_summary"] = change_summary
        if not payload:
            return error_response("No-op", "No fields provided", "Pass at least one", True)
        res = make_patch_request(f"/document-revisions/{revision_id}/", payload)
        if res.status_code == 200:
            return success_response(
                f"Updated document revision {revision_id}",
                "update_document_revision",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def _doc_revision_action(revision_id: str, action: str, payload: dict = None) -> str:
    res = make_post_request(
        f"/document-revisions/{revision_id}/{action}/", payload or {}
    )
    if res.status_code in (200, 204):
        return success_response(
            f"{action} succeeded for document revision {revision_id}",
            f"document_revision_{action.replace('-', '_')}",
            None,
        )
    return http_error_response(res.status_code, res.text)


async def submit_document_revision_for_review(revision_id: str) -> str:
    """Move a draft document revision to 'in_review'."""
    try:
        return await _doc_revision_action(revision_id, "submit-for-review")
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def approve_document_revision(revision_id: str) -> str:
    """Approve an in_review document revision (-> validated)."""
    try:
        return await _doc_revision_action(revision_id, "approve")
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def publish_document_revision(revision_id: str) -> str:
    """Publish a validated document revision (generates a PDF snapshot)."""
    try:
        return await _doc_revision_action(revision_id, "publish")
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def request_changes_on_document_revision(
    revision_id: str, reviewer_comments: str = None
) -> str:
    """Send an in_review revision back to 'change_requested'.

    Args:
        revision_id: Revision UUID
        reviewer_comments: Optional reviewer comments
    """
    try:
        payload = {}
        if reviewer_comments:
            payload["reviewer_comments"] = reviewer_comments
        return await _doc_revision_action(revision_id, "request-changes", payload)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)
