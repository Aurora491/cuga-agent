"""Resolve the app scope shared by tool preparation and native tool binding."""

from __future__ import annotations

from typing import Any, List, Optional

from cuga.backend.cuga_graph.nodes.cuga_lite.helpers.find_tools import (
    _ensure_web_app,
    _web_search_enabled,
)
from cuga.config import settings


def select_scoped_apps(state: Any, all_apps: List[Any]) -> Optional[List[Any]]:
    """Return the apps allowed by the current task, or ``None`` for an unscoped task.

    This is the single source of truth for both the sandbox execution context and
    native ``bind_tools``. Keeping the decision request-local prevents one graph
    invocation from leaking its app scope into another concurrent invocation.
    """
    sub_task_app = getattr(state, "sub_task_app", None)
    if sub_task_app:
        builtin_apps = list(getattr(settings.advanced_features, "builtin_tools", []) or [])
        if builtin_apps:
            allowed_names = {sub_task_app, *builtin_apps}
            if _web_search_enabled():
                allowed_names.add("web")
            return [app for app in all_apps if getattr(app, "name", None) in allowed_names]

        selected = [app for app in all_apps if getattr(app, "name", None) == sub_task_app]
        return _ensure_web_app(selected, all_apps)

    relevant_apps = getattr(state, "api_intent_relevant_apps", None)
    if relevant_apps:
        selected = [
            app for app in relevant_apps if getattr(app, "type", None) == "api" and getattr(app, "name", None)
        ]
        return _ensure_web_app(selected, all_apps)

    return None
