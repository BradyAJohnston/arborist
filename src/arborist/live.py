"""Run the script and watch its source for changes."""

import contextlib
import time
import traceback
from io import StringIO
from pathlib import Path

import bpy

from . import utils
from .props import ArboristProperties, props

WATCH_INTERVAL = 0.1
IDLE_INTERVAL = 1.0

# Identity of the source being watched and its last seen state (file mtime or
# text hash). Module state, not scene state: it means nothing once saved.
_watch_key: tuple | None = None
_watch_state: int | None = None


class SourceError(Exception):
    """The script source could not be read."""


def read_source(p: ArboristProperties) -> tuple[str, str]:
    """The script text and a filename for tracebacks."""
    if p.source == "FILE":
        if not p.file_path:
            raise SourceError("No file selected")
        path = Path(bpy.path.abspath(p.file_path))
        try:
            return path.read_text(), str(path)
        except OSError as e:
            raise SourceError(f"Could not read {path}: {e}") from e
    if p.text_block is None:
        raise SourceError("No text block selected")
    name = p.text_block.filepath or p.text_block.name
    return p.text_block.as_string(), name


def execute(context: bpy.types.Context | None = None):
    """Run the script once, recording status on the scene properties.

    Returns the ``nodebpy.live.RunResult``, or ``None`` when the run failed
    (the traceback is in ``last_error``).
    """
    from nodebpy.live import run_source

    p = props(context)
    try:
        code, filename = read_source(p)
    except SourceError as e:
        _record_error(p, str(e))
        return None

    captured = StringIO()
    try:
        with contextlib.redirect_stdout(captured):
            result = run_source(code, filename=filename)
    except Exception:
        _record_error(p, traceback.format_exc(), output=captured.getvalue())
        return None

    output = captured.getvalue().strip()
    p.last_executed_time = int(time.time())
    p.last_status = "SUCCESS"
    p.last_error = ""
    p.last_output = output
    p.run_count += 1
    mark_seen(p)
    utils.redraw_node_editors()
    print(f"arborist: ran {filename}")
    if output:
        print(output)
    return result


def _record_error(p: ArboristProperties, message: str, output: str = "") -> None:
    p.last_executed_time = int(time.time())
    p.last_status = "ERROR"
    p.last_error = message
    p.last_output = output.strip()
    mark_seen(p)
    utils.redraw_node_editors()
    print(f"arborist: run failed\n{message}")


# ---------------------------------------------------------------------- watch


def _current_state(p: ArboristProperties) -> tuple[tuple, int] | None:
    """(identity, state) of the watched source, or ``None`` if there is none."""
    if p.source == "FILE":
        if not p.file_path:
            return None
        path = Path(bpy.path.abspath(p.file_path))
        try:
            return ("FILE", str(path)), path.stat().st_mtime_ns
        except OSError:
            return None
    if p.text_block is None:
        return None
    return ("TEXT", p.text_block.name), hash(p.text_block.as_string())


def mark_seen(p: ArboristProperties) -> None:
    """Treat the current source state as already run, so the watcher stays quiet."""
    global _watch_key, _watch_state
    current = _current_state(p)
    _watch_key, _watch_state = current if current else (None, None)


def watch() -> float:
    global _watch_key, _watch_state
    scene = bpy.context.scene
    if scene is None:
        return IDLE_INTERVAL
    p = props()
    if not p.auto_reload:
        return IDLE_INTERVAL

    current = _current_state(p)
    if current is None:
        return IDLE_INTERVAL
    key, state = current
    if key != _watch_key:
        # A different source was selected: baseline it, don't run it.
        _watch_key, _watch_state = key, state
    elif state != _watch_state:
        _watch_state = state
        execute()
        with contextlib.suppress(RuntimeError):
            bpy.ops.ed.undo_push(message="Arborist Run")
    return WATCH_INTERVAL


def register():
    bpy.app.timers.register(watch, persistent=True)


def unregister():
    if bpy.app.timers.is_registered(watch):
        bpy.app.timers.unregister(watch)
