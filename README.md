# Arborist

A Blender extension for building and editing node trees live with
[nodebpy](https://github.com/BradyAJohnston/nodebpy) code. It adds an
**Arborist** tab to the node editor sidebar (press N) for geometry, shader and
compositor trees.

- **Export to Code** turns the open tree, or the selected group node, into
  nodebpy source in a Text block or a file on disk.
- **Run** executes that source and shows the resulting tree. **Run as Group**
  drops it into the open editor as a group node under the cursor.
- **Auto Reload** re-runs the source whenever the Text block or file changes,
  so edits in Blender's text editor, an external editor or a coding agent show
  up in the node editor immediately.

Exported code rebuilds the tree it came from in place, so modifiers, group
nodes and pinned editors stay attached across re-runs. Re-running group
classes rebuilds them and remaps their users. Both behaviours come from
`nodebpy.live`, which this extension is a thin interface over.

## Install

Download the zip from a release and install it via
Edit → Preferences → Get Extensions → Install from Disk. nodebpy is bundled;
nothing else needs installing.

## Development

The extension source is `src/arborist`. Point the VS Code Blender add-on at it
(`.vscode/settings.json` already does) to run it from the checkout.

Build a distributable zip, with nodebpy's wheel bundled for every configured
platform, using [extbpy](https://github.com/BradyAJohnston/extbpy):

```sh
uv sync --all-extras
uv run extbpy build --source-dir src
```

The tests need a real `bpy` module. Run them with a Python that has one
installed, for example the nodebpy checkout's virtualenv:

```sh
../nodebpy/.venv/bin/python -m pytest tests -q
```
