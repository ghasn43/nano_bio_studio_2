# core/tab_runner.py
from __future__ import annotations

import importlib
import inspect
from typing import Any, Dict


def load_tab_module(module_path: str):
    return importlib.import_module(module_path)


def safe_render(tab_module, **kwargs) -> None:
    """
    Calls tab_module.render(...) but only passes kwargs it accepts.
    Fixes: render() got unexpected keyword argument 'sklearn_ok'
    """
    if not hasattr(tab_module, "render"):
        raise AttributeError(f"Tab module '{tab_module.__name__}' has no render() function.")

    fn = tab_module.render
    sig = inspect.signature(fn)

    if any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()):
        # render(**kwargs) supported
        fn(**kwargs)
        return

    allowed = set(sig.parameters.keys())
    filtered = {k: v for k, v in kwargs.items() if k in allowed}
    fn(**filtered)
