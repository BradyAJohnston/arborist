from math import tau

import bpy
from nodebpy.builder import TreeBuilder, CustomCompositorGroup
from nodebpy import compositor as c
from nodebpy import geometry as g
from nodebpy import shader as s
from nodebpy.types import InputColor, InputFloat, InputInteger, InputVector

existing_tree = bpy.data.node_groups["Geometry Nodes"]


class Outline(CustomCompositorGroup):
    _name = "Outline"
    _color_tag = "CONVERTER"

    def __init__(
        self,
        image: InputColor = None,
        depth: InputFloat = None,
        depth_treshold: InputFloat = 0.01,
        normal: InputVector = None,
        normal_threshold: InputFloat = 0.5,
        outline_color: InputColor = None,
        outline_size: InputInteger = 1,
    ):
        bpy.data.node_groups.remove(bpy.data.node_groups["Outline"])
        super().__init__()
        kwargs = {
            "Image": image,
            "Depth": depth,
            "Depth Threshold": depth_treshold,
            "Normal": normal,
            "Normal Threshold": normal_threshold,
            "Outline Color": outline_color,
            "Outline Size": outline_size,
        }
        self._establish_links(**kwargs)

    def _build_group(self, tree: TreeBuilder[bpy.types.CompositorNodeTree]):
        tree.collapse = True
        image = tree.inputs.color("Image", hide_value=True)
        depth = tree.inputs.float("Depth", hide_value=True)
        depth_threshold = tree.inputs.float("Depth Threshold")
        normal = tree.inputs.vector("Normal", hide_value=True)
        normal_threshold = tree.inputs.float("Normal Threshold")
        outline_color = tree.inputs.color("Outline Color")
        outline_size = tree.inputs.integer("Outline Size")

        diff = c.AntiAliasing(
            (c.Filter.sobel(depth) > depth_threshold)
            - (c.Filter.sobel(normal) < normal_threshold)
        ) >> c.Dilateerode.distance(size=outline_size)
        c.AlphaOver(image, outline_color, diff) >> tree.outputs.color("Image")


def compositing_tree() -> bpy.types.CompositorNodeTree:
    with c.tree(bpy.data.node_groups.get("Compositor Nodes", "Compositor")) as tree:
        tree.nodes.clear()
        tree.tree.interface.clear()

        layers = c.RenderLayers()
        depth = c.SetAlpha(layers.o.depth, alpha=layers.o.alpha)
        normal = layers.o.normal

        (
            c.Glare.bloom(layers, size=0.1)
            >> Outline(
                ...,
                depth,
                depth_treshold=0.000001,
                normal=normal,
                outline_color=(0.0, 0.0, 0.0, 1.0),
                normal_threshold=0.01,
                outline_size=0,
            )
            >> c.AlphaOver((0.0, 0.0, 0.0, 1.0), ...)
            >> tree.outputs.color("Image")
        )
    return tree.tree


scene = bpy.context.scene
assert scene
scene.compositing_node_group = compositing_tree()


def material() -> bpy.types.Material:
    mat = bpy.data.materials["Material"]
    with s.tree(mat.node_tree) as tree:
        tree.nodes.clear()
        pos = s.Attribute.geometry("position")

        _ = pos >> s.Emission(..., (pos.o.vector.z + 2) * 1) >> s.MaterialOutput()
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
        >> g.SetPosition(
            position=sample.o.position, offset=g.CombineXYZ(z=offset + 0.5)
        )
        >> g.CurveToPoints.count(count=200)
    )

    iop = (
        g.InstanceOnPoints(
            points,
            instance=g.Cube(),
            rotation=points.o.rotation,
            scale=g.Vector((0.1, 0.05, 0.01)) * (g.Index() % 10) * 0.8,
        )
        >> g.RealizeInstances()
    )

    iop >> g.SetMaterial(material=material()) >> tree.outputs.geometry()
