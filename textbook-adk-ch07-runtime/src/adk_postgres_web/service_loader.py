"""
Minimal service URL + plugin loader for runtime services.

Supports either a scheme URL or a Python import string:
  - "python:package.module:Class?arg=val&flag=true"
  - "inmemory:"                                  (all kinds)
  - "db+postgresql://...": DatabaseSessionService (session)
  - "db+mysql://...", "db+sqlite://...":         DatabaseSessionService (session)
  - "gcs://bucket/prefix?param=..."              GcsArtifactService (artifact)
  - "memorybank://projects/...?...":             VertexAiMemoryBankService (memory)
  - "rag://projects/...?...":                    VertexAiRagMemoryService (memory)

Public surface:
    load_service(url, kind) -> instance
    register_scheme(kind, scheme, factory) -> None
"""

from __future__ import annotations

from typing import Callable, Dict, Any
from urllib.parse import urlparse, parse_qsl
import importlib
import inspect

# registry[kind][scheme] = factory(parse_result, kwargs) -> instance
_REGISTRY: Dict[str, Dict[str, Callable[..., Any]]] = {
    "session": {},
    "memory": {},
    "artifact": {},
}


def _to_kwargs(query: str) -> dict:
    return {k: v for k, v in parse_qsl(query, keep_blank_values=True)}


def register_scheme(kind: str, scheme: str, factory: Callable[..., Any]) -> None:
    """Register a loader factory for a given kind/scheme pair.

    factory signature: factory(parsed_url, kwargs_dict) -> instance
    """
    kind = kind.lower()
    scheme = scheme.lower()
    if kind not in _REGISTRY:
        raise ValueError(f"Unknown kind: {kind}")
    _REGISTRY[kind][scheme] = factory


def _import_object(spec: str):
    """
    Import an object from 'package.module:Name.Subname' style string.
    """
    module_name, _, qualname = spec.partition(":")
    if not module_name or not qualname:
        raise ValueError(
            "python: URLs must be of the form python:package.module:Class[.Name]"
        )
    mod = importlib.import_module(module_name)
    obj = mod
    for attr in qualname.split("."):
        obj = getattr(obj, attr)
    return obj


def _load_python(url: str):
    # url is "python:pkg.mod:Class?arg=val"
    spec_qs = url[len("python:") :]
    spec, _, qs = spec_qs.partition("?")
    obj = _import_object(spec)
    params = _to_kwargs(qs)
    if inspect.isclass(obj):
        return obj(**params)
    elif callable(obj):
        return obj(**params)
    else:
        if params:
            raise ValueError(
                "Non-callable python: target cannot accept query parameters"
            )
        return obj


def load_service(url: str | None, kind: str):
    """Return a runtime service instance of the given kind.

    kind ∈ {"session","memory","artifact"}
    """
    if not url:
        raise ValueError("load_service requires a non-empty URL")

    if url.startswith("python:"):
        return _load_python(url)

    parsed = urlparse(url)
    scheme = (parsed.scheme or "").lower()
    kwargs = _to_kwargs(parsed.query)

    # registry lookup
    factory = _REGISTRY.get(kind, {}).get(scheme)
    if factory:
        return factory(parsed, kwargs)

    # Fallback built-ins (lazy imports; give actionable errors)
    if kind == "session":
        if scheme.startswith("db+"):
            try:
                from google.adk.sessions import DatabaseSessionService  # type: ignore
            except Exception as e:  # pragma: no cover
                raise ValueError(
                    "DatabaseSessionService not available; install ADK db extras"
                ) from e
            return DatabaseSessionService(db_url=url)
        if scheme == "inmemory":
            try:
                from google.adk.sessions import InMemorySessionService  # type: ignore
            except Exception as e:  # pragma: no cover
                raise ValueError(
                    "InMemorySessionService not available (is ADK installed?)"
                ) from e
            return InMemorySessionService()

    if kind == "memory":
        if scheme == "inmemory":
            try:
                from google.adk.memory import InMemoryMemoryService  # type: ignore
            except Exception as e:  # pragma: no cover
                raise ValueError(
                    "InMemoryMemoryService not available (is ADK installed?)"
                ) from e
            return InMemoryMemoryService()
        if scheme == "memorybank":
            try:
                from google.adk.memory import VertexAiMemoryBankService  # type: ignore
            except Exception as e:  # pragma: no cover
                raise ValueError(
                    "VertexAiMemoryBankService not available; install ADK vertex extras"
                ) from e
            return VertexAiMemoryBankService(**kwargs)
        if scheme == "rag":
            try:
                from google.adk.memory import VertexAiRagMemoryService  # type: ignore
            except Exception as e:  # pragma: no cover
                raise ValueError(
                    "VertexAiRagMemoryService not available; install ADK vertex extras"
                ) from e
            return VertexAiRagMemoryService(**kwargs)

    if kind == "artifact":
        if scheme == "inmemory":
            try:
                from google.adk.artifacts import InMemoryArtifactService  # type: ignore
            except Exception as e:  # pragma: no cover
                raise ValueError(
                    "InMemoryArtifactService not available (is ADK installed?)"
                ) from e
            return InMemoryArtifactService()
        if scheme == "gcs":
            try:
                from google.adk.artifacts import GcsArtifactService  # type: ignore
            except Exception as e:  # pragma: no cover
                raise ValueError(
                    "GcsArtifactService not available; install ADK gcs extras"
                ) from e
            bucket = parsed.netloc
            prefix = parsed.path.lstrip("/")
            return GcsArtifactService(bucket=bucket, prefix=prefix, **kwargs)

    raise ValueError(f"Unsupported {kind} service URL (scheme={scheme!r}): {url}")
