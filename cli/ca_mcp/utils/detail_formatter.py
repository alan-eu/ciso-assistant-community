"""Helpers to render full backend objects (detail views) and M2M relations.

These complement response_formatter by handling the *content* shape, not the
success/error envelope. The goal is to never silently drop a field the backend
returned: list M2M relations with their IDs so the model can chain follow-up
calls, and render FK objects as `name (id)` rather than opaque strings.
"""

from typing import Any, Iterable


def _as_dict(value: Any) -> dict | None:
    return value if isinstance(value, dict) else None


def fmt_fk(value: Any) -> str:
    """Render a foreign-key field as `name (id)` when both are available."""
    if value is None:
        return "-"
    obj = _as_dict(value)
    if obj is None:
        return str(value)
    name = obj.get("str") or obj.get("name") or obj.get("email") or ""
    obj_id = obj.get("id", "")
    if name and obj_id:
        return f"{name} ({obj_id})"
    return name or str(obj_id) or "-"


def fmt_m2m(items: Iterable[Any] | None) -> str:
    """Render an M2M list as `(N) name1 (id1), name2 (id2), ...`.

    Always includes every item — never truncates. The model relies on these
    IDs to chain follow-up calls (e.g. fetch each applied control).
    """
    if not items:
        return "(0)"
    rendered = []
    for it in items:
        if isinstance(it, dict):
            name = it.get("str") or it.get("name") or it.get("email") or ""
            it_id = it.get("id", "")
            if name and it_id:
                rendered.append(f"{name} ({it_id})")
            elif name:
                rendered.append(str(name))
            elif it_id:
                rendered.append(str(it_id))
        else:
            rendered.append(str(it))
    return f"({len(rendered)}) " + ", ".join(rendered)


def fmt_m2m_cell(items: Iterable[Any] | None, max_inline: int = 5) -> str:
    """Render an M2M list compactly for a table cell.

    Shows the count plus the first `max_inline` names so the row stays readable
    while still surfacing the relation. For the full list use a detail tool.
    """
    if not items:
        return "(0)"
    items = list(items)
    names = []
    for it in items[:max_inline]:
        if isinstance(it, dict):
            names.append(it.get("str") or it.get("name") or it.get("email") or str(it.get("id", "")))
        else:
            names.append(str(it))
    suffix = "" if len(items) <= max_inline else f", +{len(items) - max_inline} more"
    return f"({len(items)}) " + ", ".join(names) + suffix


def render_detail(title: str, sections: list[tuple[str, list[tuple[str, Any]]]]) -> str:
    """Render a detail view as nested markdown.

    Args:
        title: Top-level heading.
        sections: List of (section_title, [(field_label, value), ...]). A
            section_title of "" inlines its fields directly under the title.

    Each `value` is passed through unchanged — use fmt_fk / fmt_m2m at the
    callsite to format related objects.
    """
    out = [f"## {title}\n"]
    for section_title, fields in sections:
        if section_title:
            out.append(f"\n### {section_title}\n")
        for label, value in fields:
            if value is None or value == "":
                value = "-"
            out.append(f"**{label}:** {value}\n")
    return "".join(out)
