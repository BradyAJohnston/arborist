import os
import time

import bpy

from arborist import live
from arborist.props import props

CUBE = (
    "from nodebpy import geometry as g\n"
    "with g.tree({name!r}, clear=True) as tree:\n"
    "    g.Cube() >> tree.outputs.geometry()\n"
)
SPHERE = CUBE.replace("g.Cube()", "g.UVSphere()")


def _text(code: str, name: str = "script.py") -> bpy.types.Text:
    text = bpy.data.texts.new(name)
    text.from_string(code)
    return text


def test_text_source_runs_and_rebuilds_in_place():
    p = props()
    p.source = "TEXT"
    p.text_block = _text(CUBE.format(name="Live"))

    result = live.execute()
    assert result is not None
    assert p.last_status == "SUCCESS"
    assert p.run_count == 1
    assert result.tree is bpy.data.node_groups["Live"]
    first = result.tree.as_pointer()

    p.text_block.from_string(SPHERE.format(name="Live"))
    result = live.execute()
    assert result is not None
    assert result.tree.as_pointer() == first
    assert "GeometryNodeMeshUVSphere" in {n.bl_idname for n in result.tree.nodes}
    assert p.run_count == 2


def test_error_records_traceback_with_source_name():
    p = props()
    p.source = "TEXT"
    p.text_block = _text("x = 1\n1 / 0\n", name="broken.py")

    assert live.execute() is None
    assert p.last_status == "ERROR"
    assert "ZeroDivisionError" in p.last_error
    assert 'broken.py", line 2' in p.last_error


def test_missing_source_is_reported():
    p = props()
    p.source = "TEXT"
    p.text_block = None
    assert live.execute() is None
    assert p.last_error == "No text block selected"

    p.source = "FILE"
    p.file_path = ""
    assert live.execute() is None
    assert p.last_error == "No file selected"


def test_stdout_is_captured():
    p = props()
    p.source = "TEXT"
    p.text_block = _text("print('hello from script')\n")
    live.execute()
    assert p.last_output == "hello from script"


def test_file_watcher_runs_on_change(tmp_path):
    path = tmp_path / "tree.py"
    path.write_text(CUBE.format(name="Watched"))
    p = props()
    p.source = "FILE"
    p.file_path = str(path)
    p.auto_reload = True

    # First tick baselines a newly selected source without running it.
    assert live.watch() == live.WATCH_INTERVAL
    assert p.run_count == 0

    path.write_text(SPHERE.format(name="Watched"))
    later = time.time() + 2
    os.utime(path, (later, later))
    live.watch()
    assert p.run_count == 1
    assert "GeometryNodeMeshUVSphere" in {
        n.bl_idname for n in bpy.data.node_groups["Watched"].nodes
    }

    # Unchanged file: no extra run.
    live.watch()
    assert p.run_count == 1


def test_text_watcher_runs_on_edit():
    p = props()
    p.source = "TEXT"
    p.text_block = _text(CUBE.format(name="Edited"))
    p.auto_reload = True

    live.watch()
    assert p.run_count == 0
    p.text_block.from_string(SPHERE.format(name="Edited"))
    live.watch()
    assert p.run_count == 1


def test_watcher_idles_when_disabled():
    p = props()
    p.auto_reload = False
    assert live.watch() == live.IDLE_INTERVAL
