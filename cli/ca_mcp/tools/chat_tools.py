"""MCP tools for chat sessions, indexed documents, and questionnaire runs.

Streaming actions (chat session `message`, agent prefill) are intentionally
not exposed — they return SSE which doesn't map to a single MCP tool result.
Use the UI for interactive chat.
"""

import json

from ..client import (
    make_get_request,
    make_post_request,
    make_patch_request,
    make_delete_request,
    get_paginated_results,
)
from ..resolvers import resolve_folder_id, resolve_id_or_name
from ..utils.detail_formatter import fmt_fk, render_detail
from ..utils.response_formatter import (
    empty_response,
    error_response,
    http_error_response,
    success_response,
)


# ---------- Chat sessions ----------


async def get_chat_sessions(folder: str = None):
    """List chat sessions owned by the authenticated user.

    Args:
        folder: Folder ID/name filter
    """
    try:
        params = {}
        if folder:
            params["folder"] = resolve_folder_id(folder)
        res = make_get_request("/chat/sessions/", params=params)
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        items = get_paginated_results(res.json())
        if not items:
            return empty_response("chat sessions", {"folder": folder})
        result = f"Found {len(items)} chat sessions\n\n|ID|Title|Folder|Created|\n|---|---|---|---|\n"
        for s in items:
            result += (
                f"|{s.get('id')}|{s.get('title', '-')}"
                f"|{(s.get('folder') or {}).get('str', '-')}"
                f"|{s.get('created_at', '-')}|\n"
            )
        return success_response(result, "get_chat_sessions", None)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def create_chat_session(title: str, folder: str) -> str:
    """Create a new chat session.

    Args:
        title: Session title
        folder: Folder ID/name
    """
    try:
        payload = {"title": title, "folder": resolve_folder_id(folder)}
        res = make_post_request("/chat/sessions/", payload)
        if res.status_code == 201:
            s = res.json()
            return success_response(
                f"Created chat session '{s.get('title')}' (ID: {s.get('id')})",
                "create_chat_session",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def delete_chat_session(session_id: str) -> str:
    """Delete a chat session.

    Args:
        session_id: Chat session UUID
    """
    try:
        res = make_delete_request(f"/chat/sessions/{session_id}/")
        if res.status_code == 204:
            return success_response(
                f"Deleted chat session {session_id}", "delete_chat_session", None
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


# ---------- Indexed documents (RAG) ----------


async def get_indexed_documents(folder: str = None, source_type: str = None, status: str = None):
    """List indexed documents available to the chat RAG layer.

    Args:
        folder: Folder ID/name
        source_type: Source type filter
        status: Status filter
    """
    try:
        params = {}
        filters = {}
        if folder:
            params["folder"] = resolve_folder_id(folder)
            filters["folder"] = folder
        if source_type:
            params["source_type"] = source_type
            filters["source_type"] = source_type
        if status:
            params["status"] = status
            filters["status"] = status
        res = make_get_request("/chat/documents/", params=params)
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        items = get_paginated_results(res.json())
        if not items:
            return empty_response("indexed documents", filters)
        result = f"Found {len(items)} indexed documents\n\n|ID|Name|Source|Status|Folder|\n|---|---|---|---|---|\n"
        for d in items:
            result += (
                f"|{d.get('id')}|{d.get('name', '-')}|{d.get('source_type', '-')}"
                f"|{d.get('status', '-')}"
                f"|{(d.get('folder') or {}).get('str', '-')}|\n"
            )
        return success_response(result, "get_indexed_documents", None)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def delete_indexed_document(document_id: str) -> str:
    """Delete an indexed (RAG) document.

    Args:
        document_id: Indexed document UUID
    """
    try:
        res = make_delete_request(f"/chat/documents/{document_id}/")
        if res.status_code == 204:
            return success_response(
                f"Deleted indexed document {document_id}",
                "delete_indexed_document",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


# ---------- Questionnaire runs ----------


async def get_questionnaire_runs(folder: str = None, status: str = None):
    """List questionnaire runs.

    Args:
        folder: Folder ID/name
        status: Status filter
    """
    try:
        params = {}
        filters = {}
        if folder:
            params["folder"] = resolve_folder_id(folder)
            filters["folder"] = folder
        if status:
            params["status"] = status
            filters["status"] = status
        res = make_get_request("/chat/questionnaire-runs/", params=params)
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        items = get_paginated_results(res.json())
        if not items:
            return empty_response("questionnaire runs", filters)
        result = f"Found {len(items)} questionnaire runs\n\n|ID|Title|Filename|Status|Folder|\n|---|---|---|---|---|\n"
        for q in items:
            result += (
                f"|{q.get('id')}|{q.get('title', '-')}|{q.get('filename', '-')}"
                f"|{q.get('status', '-')}"
                f"|{(q.get('folder') or {}).get('str', '-')}|\n"
            )
        return success_response(result, "get_questionnaire_runs", None)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def get_questionnaire_run(questionnaire_run_id: str):
    """Retrieve a single questionnaire run with parsed metadata."""
    try:
        res = make_get_request(f"/chat/questionnaire-runs/{questionnaire_run_id}/")
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        q = res.json()
        return success_response(
            json.dumps(q, indent=2), "get_questionnaire_run", None
        )
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def delete_questionnaire_run(questionnaire_run_id: str) -> str:
    """Delete a questionnaire run."""
    try:
        res = make_delete_request(
            f"/chat/questionnaire-runs/{questionnaire_run_id}/"
        )
        if res.status_code == 204:
            return success_response(
                f"Deleted questionnaire run {questionnaire_run_id}",
                "delete_questionnaire_run",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


# ---------- Agent actions ----------


async def get_agent_runs(folder: str = None, kind: str = None, status: str = None):
    """List background agent runs (proposals, prefills, etc.)."""
    try:
        params = {}
        filters = {}
        if folder:
            params["folder"] = resolve_folder_id(folder)
            filters["folder"] = folder
        if kind:
            params["kind"] = kind
            filters["kind"] = kind
        if status:
            params["status"] = status
            filters["status"] = status
        res = make_get_request("/chat/agent-runs/", params=params)
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        items = get_paginated_results(res.json())
        if not items:
            return empty_response("agent runs", filters)
        result = f"Found {len(items)} agent runs\n\n|ID|Kind|Status|Folder|Created|\n|---|---|---|---|---|\n"
        for r in items:
            result += (
                f"|{r.get('id')}|{r.get('kind', '-')}|{r.get('status', '-')}"
                f"|{(r.get('folder') or {}).get('str', '-')}|{r.get('created_at', '-')}|\n"
            )
        return success_response(result, "get_agent_runs", None)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def get_agent_actions(agent_run: str = None, state: str = None):
    """List agent proposals (CRUD actions an agent wants to take).

    Args:
        agent_run: Agent run UUID filter
        state: State filter (e.g. pending, approved, rejected)
    """
    try:
        params = {}
        filters = {}
        if agent_run:
            params["agent_run"] = agent_run
            filters["agent_run"] = agent_run
        if state:
            params["state"] = state
            filters["state"] = state
        res = make_get_request("/chat/agent-actions/", params=params)
        if res.status_code != 200:
            return http_error_response(res.status_code, res.text)
        items = get_paginated_results(res.json())
        if not items:
            return empty_response("agent actions", filters)
        result = f"Found {len(items)} agent actions\n\n|ID|Run|State|Kind|Created|\n|---|---|---|---|---|\n"
        for a in items:
            result += (
                f"|{a.get('id')}|{(a.get('agent_run') or {}).get('str', '-')}"
                f"|{a.get('state', '-')}|{a.get('kind', '-')}"
                f"|{a.get('created_at', '-')}|\n"
            )
        return success_response(result, "get_agent_actions", None)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)


async def set_agent_action_state(agent_action_id: str, state: str) -> str:
    """Approve or reject an agent action proposal.

    Args:
        agent_action_id: Agent action UUID
        state: New state (e.g. approved, rejected)
    """
    try:
        res = make_patch_request(
            f"/chat/agent-actions/{agent_action_id}/", {"state": state}
        )
        if res.status_code == 200:
            return success_response(
                f"Set agent action {agent_action_id} to '{state}'",
                "set_agent_action_state",
                None,
            )
        return http_error_response(res.status_code, res.text)
    except Exception as e:
        return error_response("Internal Error", str(e), "Report this error", False)
