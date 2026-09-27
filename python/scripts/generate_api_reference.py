"""Generate the Markdown API reference for the `appconnect` package.

Writes one page per area into ``docs/reference/python/`` at the repository
root. The output is deterministic (``__all__`` order, source annotations
verbatim), so CI can regenerate it and fail when the committed reference is
stale.

Usage (from ``python/``)::

    uv run python scripts/generate_api_reference.py
"""

from __future__ import annotations

import inspect
import typing
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any

from pydantic import BaseModel

import appconnect
import appconnect.framework

OUT_DIR = Path(__file__).resolve().parents[2] / "docs" / "reference" / "python"

CLIENT_NAMES = ["AppConnectClient", "SyncAppConnectClient", "AppConnectError"]
FUNCTION_NAMES = ["verify_webhook_signature"]
CONTEXT_MANAGER_NOTES = {
    "__aenter__": "Supports `async with`; the underlying HTTP client is closed on exit.",
    "__enter__": "Supports `with`; the underlying HTTP client is closed on exit.",
}


def doc(obj: object) -> str:
    return inspect.getdoc(obj) or ""


def annotation_text(annotation: Any) -> str:
    """Source annotation text: modules use `from __future__ import annotations`."""
    if isinstance(annotation, typing.ForwardRef):
        return annotation.__forward_arg__
    return annotation if isinstance(annotation, str) else inspect.formatannotation(annotation)


def signature(
    name: str,
    func: Callable[..., Any],
    *,
    drop_self: bool = False,
    constructor: bool = False,
) -> str:
    sig = inspect.signature(func)
    params = list(sig.parameters.values())[1 if drop_self else 0 :]
    parts: list[str] = []
    for param in params:
        text = param.name
        if param.kind is param.VAR_POSITIONAL:
            text = f"*{text}"
        elif param.kind is param.VAR_KEYWORD:
            text = f"**{text}"
        if param.annotation is not param.empty:
            text += f": {annotation_text(param.annotation)}"
        if param.default is not param.empty:
            joiner = " = " if param.annotation is not param.empty else "="
            text += f"{joiner}{param.default!r}"
        parts.append(text)
    args = ", ".join(parts)
    if constructor:
        return f"{name}({args})"
    returns = ""
    if sig.return_annotation is not sig.empty:
        returns = f" -> {annotation_text(sig.return_annotation)}"
    prefix = "async def " if inspect.iscoroutinefunction(func) else "def "
    return f"{prefix}{name}({args}){returns}"


def code_block(source: str) -> list[str]:
    return ["```python", source, "```", ""]


def paragraph(text: str) -> list[str]:
    return [text, ""] if text else []


def render_function(name: str, func: Callable[..., Any], level: str) -> list[str]:
    return [f"{level} `{name}()`", "", *code_block(signature(name, func)), *paragraph(doc(func))]


def public_methods(cls: type) -> Iterable[tuple[str, Callable[..., Any]]]:
    for name, member in cls.__dict__.items():
        if not callable(member):
            continue
        if name.startswith("_"):
            continue
        yield name, member


def render_class(name: str, cls: type) -> list[str]:
    lines = [f"## `{name}`", "", *paragraph(doc(cls))]
    init = cls.__dict__.get("__init__")
    if init is not None:
        lines += [
            "### Constructor",
            "",
            *code_block(signature(name, init, drop_self=True, constructor=True)),
        ]
    for dunder, note in CONTEXT_MANAGER_NOTES.items():
        if dunder in cls.__dict__:
            lines += [note, ""]
    for method_name, method in public_methods(cls):
        lines += [
            f"### `{method_name}()`",
            "",
            *code_block(signature(method_name, method, drop_self=True)),
            *paragraph(doc(method)),
        ]
    return lines


def field_rows(cls: type) -> list[str]:
    """One table row per annotated field, using the source annotation text."""
    annotations: dict[str, str] = {}
    for base in reversed(cls.__mro__):
        if base in (BaseModel, object) or base.__module__.startswith(("pydantic", "typing")):
            continue
        annotations.update(getattr(base, "__annotations__", {}))
    model_fields = getattr(cls, "model_fields", {})
    required_keys = getattr(cls, "__required_keys__", None)
    rows = ["| Field | Type | Required |", "| --- | --- | --- |"]
    for field, annotation in annotations.items():
        if field.startswith("_") or field == "model_config":
            continue
        if field in model_fields:
            required = "yes" if model_fields[field].is_required() else "no"
        elif required_keys is not None:
            required = "yes" if field in required_keys else "no"
        else:
            required = "yes"
        type_text = annotation_text(annotation).replace("|", "\\|")
        rows.append(f"| `{field}` | `{type_text}` | {required} |")
    return [*rows, ""]


def render_type(name: str, obj: Any) -> list[str]:
    lines = [f"## `{name}`", ""]
    if isinstance(obj, type):
        lines += [*paragraph(doc(obj)), *field_rows(obj)]
    else:
        # A type alias: a (possibly discriminated) union of response models.
        note = ""
        if typing.get_origin(obj) is typing.Annotated:
            obj, *metadata = typing.get_args(obj)
            discriminator = next(
                (m.discriminator for m in metadata if getattr(m, "discriminator", None)), None
            )
            if discriminator:
                note = f"Discriminated by the `{discriminator}` field."
        members = " | ".join(arg.__name__ for arg in typing.get_args(obj))
        lines += [*code_block(f"{name} = {members}"), *paragraph(note)]
    return lines


def write_page(filename: str, title: str, intro: str, body: list[str]) -> None:
    content = [f"# {title}", "", intro, "", *body]
    text = "\n".join(content).rstrip() + "\n"
    (OUT_DIR / filename).write_text(text, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for stale in OUT_DIR.glob("*.md"):
        stale.unlink()

    body: list[str] = []
    for name in CLIENT_NAMES:
        body += render_class(name, getattr(appconnect, name))
    for name in FUNCTION_NAMES:
        body += render_function(name, getattr(appconnect, name), "##")
    write_page(
        "clients.md",
        "Clients and helpers",
        "Import from `appconnect`. `AppConnectClient` is async; "
        "`SyncAppConnectClient` has the same methods for synchronous code.",
        body,
    )

    type_names = [
        n
        for n in appconnect.__all__
        if n not in CLIENT_NAMES and n not in FUNCTION_NAMES and n != "__version__"
    ]
    body = []
    for name in type_names:
        body += render_type(name, getattr(appconnect, name))
    write_page(
        "types.md",
        "Response types",
        "Pydantic models returned by the clients, importable from `appconnect`. "
        "Field names mirror the API's JSON keys.",
        body,
    )

    body = []
    for name in appconnect.framework.__all__:
        obj = getattr(appconnect.framework, name)
        if inspect.isfunction(obj):
            body += render_function(name, obj, "##")
        elif typing.is_typeddict(obj):
            body += [f"## `{name}`", "", *paragraph(doc(obj)), *field_rows(obj)]
    write_page(
        "framework.md",
        "Framework adapters",
        "Import from `appconnect.framework`. `to_langchain_tools()` needs the "
        '`langchain` extra (`pip install "appconnect[langchain]"`).',
        body,
    )

    write_page(
        "index.md",
        "appconnect API reference",
        f"Generated from `appconnect` {appconnect.__version__}.",
        [
            "- [Clients and helpers](clients.md)",
            "- [Response types](types.md)",
            "- [Framework adapters](framework.md)",
        ],
    )


if __name__ == "__main__":
    main()
