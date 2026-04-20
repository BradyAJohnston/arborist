from math import tau

import bpy
from nodebpy import compositor as c
from nodebpy import geometry as g
from nodebpy import shader as s

existing_tree = bpy.data.node_groups["Geometry Nodes"]


def compositing_tree() -> bpy.types.CompositorNodeTree:
    tree = bpy.data.node_groups["Compositor Nodes"]
    with c.tree(tree) as tree:
        tree.nodes.clear()
        tree.tree.interface.clear()

        layers = c.RenderLayers()

        _ = c.Glare.bloom(layers, size=0.4) >> tree.outputs.color("Image")
    return tree.tree


scene = bpy.context.scene
assert scene
scene.compositing_node_group = compositing_tree()


def material() -> bpy.types.Material:
    mat = bpy.data.materials["Material"]
    with s.tree(mat.node_tree) as tree:
        tree.nodes.clear()
        pos = s.Attribute.geometry("position")

        _ = pos >> s.Emission(..., (pos.o.vector.z + 2) * 4) >> s.MaterialOutput()
    return mat


with g.tree(existing_tree, collapse=False) as tree:
    tree.tree.nodes.clear()
    tree.tree.interface.clear()

    time = g.SceneTime()
    curve = g.CurveCircle(resolution=100)
    cat = g.CaptureAttribute.point()
    factor = cat.capture(g.SplineParameter().o.factor)
    sample_fac = (factor + time.o.frame / 250) >> g.Math.wrap(..., 0, 1)

    sample = g.SampleCurve.factor(
        curves=curve,
        factor=sample_fac,
    )

    offset = g.Math.sine(sample_fac * tau * 3) * 0.2

    points = (
        curve
        >> cat
        >> g.SetPosition(position=sample.o.position, offset=g.CombineXYZ(z=offset))
        >> g.CurveToPoints.count(count=300)
    )

    iop = (
        g.InstanceOnPoints(
            points,
            instance=g.Cube(),
            rotation=points.o.rotation,
            scale=g.CombineXYZ(x=0.1, y=0.05, z=0.01) * (g.Index() % 10) * 0.4,
        )
        >> g.RealizeInstances()
    )

    _ = iop >> g.SetMaterial(material=material()) >> tree.outputs.geometry()
