import os
import sys
import tempfile
from pathlib import Path

# Importing bpy puts Blender's user extensions site-packages first on
# sys.path, where an installed nodebpy wheel would shadow the one we test
# against. Point it at an empty directory before the import.
os.environ.setdefault("BLENDER_USER_EXTENSIONS", tempfile.mkdtemp())

import bpy
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import arborist


@pytest.fixture(scope="session", autouse=True)
def registered():
    arborist.register()
    yield
    arborist.unregister()


@pytest.fixture(autouse=True)
def fresh_file():
    bpy.ops.wm.read_homefile(use_empty=True)
    from arborist import live

    live.mark_seen(bpy.context.scene.arborist)
    yield
