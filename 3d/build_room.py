import math
import os
import random

import bmesh
import bpy
from mathutils import Matrix, Vector

ROOT = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.environ["A123_3D"]
TEX = os.path.join(ROOT, "textures")
OUT_GLB = os.path.join(ROOT, "..", "public", "models", "arka123.glb")

W = 11.8
D = 10.4
H = 4.5
T = 0.4
WIN_W = 4.0
WIN_H = 3.0
WIN_RISE = 1.55
SILL = 1.0
WIN_U = (D / 2 - 2.375, D / 2 + 2.375)
COL_C = (5.9, D / 2)
KITCHEN = (6.2, 8.4, 0.65)
CLOCK_X = 3.0
GLASS_Y = (0.0, D - 1.4)
WHITE_COL_Y = 4.6
ORIGIN = Vector((-W / 2, -D / 2, 0))

random.seed(123)


def reset():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.images, bpy.data.lights, bpy.data.cameras):
        for b in list(coll):
            if b.users == 0:
                coll.remove(b)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)


def collection(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c


def image(name):
    return bpy.data.images.load(os.path.join(TEX, name), check_existing=True)


def material(name, color=(0.8, 0.8, 0.8), rough=0.6, metal=0.0, tex=None, emit=None, emit_strength=1.0, alpha=1.0, emit_tex=None):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if tex:
        t = nt.nodes.new("ShaderNodeTexImage")
        t.image = image(tex)
        nt.links.new(t.outputs["Color"], bsdf.inputs["Base Color"])
    if emit or emit_tex:
        bsdf.inputs["Emission Color"].default_value = (*(emit or (1, 1, 1)), 1.0)
        bsdf.inputs["Emission Strength"].default_value = emit_strength
        if emit_tex:
            t = nt.nodes.new("ShaderNodeTexImage")
            t.image = image(emit_tex)
            nt.links.new(t.outputs["Color"], bsdf.inputs["Emission Color"])
            bsdf.inputs["Base Color"].default_value = (0, 0, 0, 1)
    if alpha < 1.0:
        bsdf.inputs["Alpha"].default_value = alpha
        try:
            m.surface_render_method = "BLENDED"
        except (AttributeError, TypeError):
            m.blend_method = "BLEND"
    m.use_backface_culling = True
    return m


def materials():
    return dict(
        floor=material("Floor_Herringbone", tex="floor_herringbone.jpg", rough=0.5),
        plaster=material("Wall_Plaster", tex="wall_plaster.jpg", rough=0.9),
        ceiling=material("Ceiling_Anthracite", color=(0.045, 0.048, 0.052), rough=0.9),
        graphite=material("Column_Graphite", color=(0.085, 0.09, 0.098), rough=0.7),
        kitchen=material("Kitchen_Graphite", color=(0.07, 0.074, 0.08), rough=0.45),
        metal_dark=material("Metal_Black", color=(0.02, 0.02, 0.022), rough=0.45, metal=0.6),
        pipe=material("Pipe_Grey", color=(0.32, 0.33, 0.34), rough=0.5, metal=0.5),
        frame=material("Window_Frame", color=(0.03, 0.032, 0.035), rough=0.4, metal=0.3),
        glass=material("Window_Glass", color=(0.75, 0.82, 0.85), rough=0.05, alpha=0.1),
        glass_part=material("Partition_Glass", color=(0.86, 0.9, 0.92), rough=0.1, alpha=0.18),
        frost=material("Partition_Frost", color=(0.92, 0.93, 0.94), rough=0.4, alpha=0.75),
        alu=material("Aluminium", color=(0.7, 0.72, 0.74), rough=0.3, metal=0.9),
        white=material("Panel_White", color=(0.88, 0.88, 0.87), rough=0.45),
        counter=material("Counter_Light", color=(0.8, 0.8, 0.79), rough=0.3),
        tile=material("Corridor_Tile", color=(0.62, 0.63, 0.64), rough=0.3),
        led=material("LED_Linear", color=(1, 1, 1), emit=(1.0, 0.97, 0.92), emit_strength=6.0),
        led_cool=material("LED_Backsplash", color=(0.5, 0.55, 0.6), emit=(0.75, 0.88, 1.0), emit_strength=1.0),
        fridge=material("Wine_Fridge_Glass", color=(0.02, 0.02, 0.025), rough=0.05, emit=(1.0, 0.85, 0.6), emit_strength=0.15),
        view=material("View_Library", emit_tex="view_library.jpg", emit_strength=1.0),
    )


def mesh_object(name, bm, coll, mats, matrix=None):
    if matrix is not None:
        bmesh.ops.transform(bm, matrix=matrix, verts=bm.verts)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(m)
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    return ob


def add_box(bm, x0, x1, y0, y1, z0, z1, mat=0):
    vs = [bm.verts.new(v) for v in [
        (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
        (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]]
    for f in [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]:
        bm.faces.new([vs[i] for i in f]).material_index = mat


def add_quad(bm, pts, mat=0):
    bm.faces.new([bm.verts.new(p) for p in pts]).material_index = mat


def add_cylinder(bm, p0, p1, r, seg=12, mat=0, caps=False):
    p0, p1 = Vector(p0), Vector(p1)
    ax = (p1 - p0).normalized()
    ref = Vector((0, 0, 1)) if abs(ax.z) < 0.9 else Vector((1, 0, 0))
    u = ax.cross(ref).normalized()
    v = ax.cross(u)
    r0, r1 = [], []
    for k in range(seg):
        a = 2 * math.pi * k / seg
        off = (u * math.cos(a) + v * math.sin(a)) * r
        r0.append(bm.verts.new(p0 + off))
        r1.append(bm.verts.new(p1 + off))
    for k in range(seg):
        j = (k + 1) % seg
        bm.faces.new([r0[k], r1[k], r1[j], r0[j]]).material_index = mat
    if caps:
        bm.faces.new(list(reversed(r0))).material_index = mat
        bm.faces.new(r1).material_index = mat


def add_transformed_box(bm, size, matrix, mat=0):
    tbm = bmesh.new()
    bmesh.ops.create_cube(tbm, size=1.0)
    bmesh.ops.scale(tbm, vec=size, verts=tbm.verts)
    bmesh.ops.transform(tbm, matrix=matrix, verts=tbm.verts)
    for f in tbm.faces:
        f.material_index = mat
    me = bpy.data.meshes.new("tmp")
    tbm.to_mesh(me)
    tbm.free()
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)


def box_uv(ob, scale=1.0, rot45=False):
    me = ob.data
    uv = me.uv_layers[0] if me.uv_layers else me.uv_layers.new(name="UVMap")
    c45 = math.cos(math.pi / 4)
    for poly in me.polygons:
        n = poly.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        for li in poly.loop_indices:
            p = me.vertices[me.loops[li].vertex_index].co
            if ax == 2:
                u, v = p.x, p.y
            elif ax == 1:
                u, v = p.x, p.z
            else:
                u, v = p.y, p.z
            if rot45:
                u, v = (u - v) * c45, (u + v) * c45
            uv.data[li].uv = (u / scale, v / scale)


def arch_profile(w, h, rise, n=40, inset=0.0):
    hw = w / 2 - inset
    r = rise - inset
    hr = h - rise
    pts = [(-hw, inset), (hw, inset), (hw, hr)]
    for i in range(1, n):
        a = math.pi * i / n
        pts.append((hw * math.cos(a), hr + r * math.sin(a)))
    pts.append((-hw, hr))
    return pts


def arch_height(x, w, h, rise, inset=0.0):
    hw = w / 2 - inset
    r = rise - inset
    return h - rise + r * math.sqrt(max(0.0, 1.0 - (x / hw) ** 2))


def prism(bm, pts2d, cx, z0, y0, y1, mat=0):
    bottom = [bm.verts.new((cx + x, y0, z0 + z)) for x, z in pts2d]
    top = [bm.verts.new((cx + x, y1, z0 + z)) for x, z in pts2d]
    bm.faces.new(bottom).material_index = mat
    bm.faces.new(list(reversed(top))).material_index = mat
    k = len(pts2d)
    for i in range(k):
        j = (i + 1) % k
        bm.faces.new([bottom[i], bottom[j], top[j], top[i]]).material_index = mat


def ring_prism(bm, outer, inner, cx, z0, y0, y1, mat=0):
    k = len(outer)
    lay = [([bm.verts.new((cx + x, y, z0 + z)) for x, z in outer], [bm.verts.new((cx + x, y, z0 + z)) for x, z in inner]) for y in (y0, y1)]
    for (o, i_), flip in ((lay[0], False), (lay[1], True)):
        for a in range(k):
            b = (a + 1) % k
            f = [o[a], o[b], i_[b], i_[a]]
            bm.faces.new(list(reversed(f)) if flip else f).material_index = mat
    for ring in (0, 1):
        for a in range(k):
            b = (a + 1) % k
            p, q = lay[0][ring], lay[1][ring]
            f = [p[a], p[b], q[b], q[a]]
            bm.faces.new(f if ring == 0 else list(reversed(f))).material_index = mat


def apply_boolean(target, cutter):
    mod = target.modifiers.new("cut", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.object = cutter
    mod.solver = "EXACT"
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(target.evaluated_get(dg))
    old = target.data
    target.modifiers.clear()
    target.data = me
    bpy.data.meshes.remove(old)
    me.name = target.name
    bpy.data.objects.remove(cutter)


WEST = Matrix.Rotation(math.pi / 2, 4, "Z")


def build_window_wall(coll, M):
    bm = bmesh.new()
    add_box(bm, -T, D + T, 0, T, 0, H)
    wall = mesh_object("WindowWall", bm, coll, [M["plaster"]], WEST)
    cbm = bmesh.new()
    for cu in WIN_U:
        prism(cbm, arch_profile(WIN_W, WIN_H, WIN_RISE), cu, SILL, -0.1, T + 0.1)
    bmesh.ops.recalc_face_normals(cbm, faces=cbm.faces)
    cutter = mesh_object("Cutter", cbm, coll, [], WEST)
    apply_boolean(wall, cutter)
    box_uv(wall, 2.0)

    bm = bmesh.new()
    gbm = bmesh.new()
    ft = 0.07
    fd0, fd1 = 0.12, 0.2
    for cu in WIN_U:
        inner = arch_profile(WIN_W, WIN_H, WIN_RISE, inset=ft)
        ring_prism(bm, arch_profile(WIN_W, WIN_H, WIN_RISE), inner, cu, SILL, fd0, fd1)
        tz = SILL + 1.25
        add_box(bm, cu - WIN_W / 2, cu + WIN_W / 2, fd0, fd1, tz, tz + 0.06)
        spring = SILL + WIN_H - WIN_RISE
        for mx in (-0.95, 0.95):
            add_box(bm, cu + mx - 0.03, cu + mx + 0.03, fd0, fd1, SILL, SILL + arch_height(mx, WIN_W, WIN_H, WIN_RISE, ft) - 0.01)
        add_box(bm, cu - WIN_W / 2, cu - 0.95, fd0, fd1, spring - 0.03, spring + 0.03)
        add_box(bm, cu + 0.95, cu + WIN_W / 2, fd0, fd1, spring - 0.03, spring + 0.03)
        add_box(bm, cu - 1.88, cu - 1.84, fd0 - 0.03, fd0, SILL + 0.1, SILL + 1.15)
        gbm.faces.new([gbm.verts.new((cu + x, 0.16, SILL + z)) for x, z in inner])
    mesh_object("WindowFrames", bm, coll, [M["frame"]], WEST)
    mesh_object("WindowGlass", gbm, coll, [M["glass"]], WEST)

    bm = bmesh.new()
    for cu in WIN_U:
        add_box(bm, cu - WIN_W / 2 - 0.05, cu + WIN_W / 2 + 0.05, -0.08, 0.2, SILL - 0.04, SILL)
        add_box(bm, cu - 0.95, cu + 0.95, -0.18, -0.08, 0.16, 0.66)
        for k in range(48):
            fx = cu - 0.93 + k * 0.0395
            add_box(bm, fx, fx + 0.018, -0.2, -0.18, 0.16, 0.66)
        for sx in (-0.85, 0.85):
            add_box(bm, cu + sx - 0.012, cu + sx + 0.012, -0.12, -0.1, 0.0, 0.16, 1)
    mesh_object("Radiators", bm, coll, [M["metal_dark"], M["alu"]], WEST)


def build_walls(coll, M):
    kx0, kx1, kd = KITCHEN
    bm = bmesh.new()
    add_box(bm, -T, W + T, -T, 0, 0, H)
    add_box(bm, 0, kx0, D, D + T, 0, H)
    add_box(bm, kx1, W + T, D, D + T, 0, H)
    walls = mesh_object("Walls", bm, coll, [M["plaster"]])
    box_uv(walls, 2.0)

    bm = bmesh.new()
    add_box(bm, kx0, kx1, D + kd - 0.02, D + kd, 0, H, 0)
    add_box(bm, kx0, kx0 + 0.02, D, D + kd, 0, H, 0)
    add_box(bm, kx1 - 0.02, kx1, D, D + kd, 0, H, 0)
    add_box(bm, kx0 + 0.02, kx1 - 0.6, D + 0.02, D + kd - 0.02, 0.0, 0.86, 0)
    add_box(bm, kx0 + 0.02, kx1 - 0.6, D + 0.0, D + kd - 0.02, 0.86, 0.9, 1)
    add_box(bm, kx0 + 0.02, kx1 - 0.02, D + kd - 0.38, D + kd - 0.02, 1.55, 2.45, 0)
    add_box(bm, kx0 + 0.02, kx1 - 0.02, D + kd - 0.38, D + kd - 0.02, 1.53, 1.55, 3)
    add_box(bm, kx1 - 0.6, kx1 - 0.02, D + 0.02, D + kd - 0.02, 0.0, 0.86, 0)
    add_box(bm, kx1 - 0.58, kx1 - 0.04, D + 0.0, D + 0.02, 0.06, 0.8, 2)
    for k in range(4):
        x = kx0 + 0.02 + (kx1 - 0.62 - kx0) * k / 4
        add_box(bm, x, x + 0.006, D - 0.002, D + 0.0, 0.05, 0.84, 4)
    add_box(bm, kx0 - 0.01, kx1 + 0.01, D - 0.35, D, 2.75, H, 0)
    mesh_object("Kitchenette", bm, coll, [M["kitchen"], M["counter"], M["fridge"], M["led_cool"], M["metal_dark"]])
    bm = bmesh.new()
    add_box(bm, kx0 + 0.02, kx1 - 0.02, D + kd - 0.03, D + kd - 0.02, 0.9, 1.53)
    mesh_object("KitchenBacksplash", bm, coll, [M["led_cool"]])

    bm = bmesh.new()
    seam = 1
    px0, px1 = kx1, W - 0.8
    add_box(bm, px0, px1, D - 0.04, D, 0.07, 3.0, 0)
    add_box(bm, W - 0.8, W, D - 1.4, D, 0.0, 3.0, 0)
    add_box(bm, W - 0.3, W + 0.3, WHITE_COL_Y - 0.3, WHITE_COL_Y + 0.3, 0.0, H, 0)
    xs = [px0, px0 + 0.55, px0 + 1.1, px0 + 1.65, px0 + 2.2, px1]
    hz = [2.1, 1.6, 2.4, 1.2, 2.0]
    for i, (a, b) in enumerate(zip(xs, xs[1:])):
        add_box(bm, a + 0.002, a + 0.008, D - 0.045, D - 0.04, 0.07, 3.0, seam)
        add_box(bm, a, b, D - 0.045, D - 0.04, hz[i], hz[i] + 0.006, seam)
        add_box(bm, a, b, D - 0.045, D - 0.04, 0.6 + 0.15 * i, 0.606 + 0.15 * i, seam)
    for gx in (px0 + 1.75, px0 + 1.97):
        for gz in (1.05, 1.2):
            add_box(bm, gx, gx + 0.17, D - 0.05, D - 0.04, gz, gz + 0.09, seam)
    for sy in (D - 1.4, D - 0.7):
        add_box(bm, W - 0.805, W - 0.8, sy, sy + 0.006, 0.07, 3.0, seam)
    for z in (1.4, 2.2):
        add_box(bm, W - 0.81, W - 0.8, D - 1.4, D - 0.7, z, z + 0.006, seam)
    for z in (1.35, 2.1):
        for sx in (-0.301, 0.301):
            add_box(bm, W + sx - 0.003, W + sx + 0.003, WHITE_COL_Y - 0.3, WHITE_COL_Y + 0.3, z, z + 0.01, seam)
        for sy in (-0.301, 0.301):
            add_box(bm, W - 0.3, W + 0.3, WHITE_COL_Y + sy - 0.003, WHITE_COL_Y + sy + 0.003, z, z + 0.01, seam)
    add_box(bm, px0, W, D - 1.4, D, 3.0, 3.02, 0)
    mesh_object("WhitePanels", bm, coll, [M["white"], M["metal_dark"]])

    bm = bmesh.new()
    sk = 0.07
    add_box(bm, 0, W, 0, 0.012, 0, sk)
    add_box(bm, 0, 0.012, 0, D, 0, sk)
    add_box(bm, 0, kx0, D - 0.012, D, 0, sk)
    add_box(bm, kx1, W - 0.8, D - 0.052, D - 0.04, 0, sk)
    mesh_object("Skirting", bm, coll, [M["metal_dark"]])


def build_partition(coll, M):
    y0, y1 = GLASS_Y
    gz = 3.0
    bm = bmesh.new()
    add_box(bm, W - 0.01, W + 0.01, y0, y1, 0.0, gz)
    mesh_object("PartitionGlass", bm, coll, [M["glass_part"]])
    bm = bmesh.new()
    for z, h in ((0.95, 0.06), (1.12, 0.32), (1.5, 0.05), (2.05, 0.04)):
        add_box(bm, W - 0.014, W - 0.012, y0, y1, z, z + h)
    mesh_object("PartitionFrost", bm, coll, [M["frost"]])
    bm = bmesh.new()
    add_box(bm, W - 0.03, W + 0.03, y0, y1, 0.0, 0.04)
    add_box(bm, W - 0.03, W + 0.03, y0, y1, gz - 0.04, gz)
    n = 7
    for k in range(n + 1):
        y = y0 + (y1 - y0) * k / n
        add_box(bm, W - 0.02, W + 0.02, y - 0.01, y + 0.01, 0.0, gz)
    for dy in (WHITE_COL_Y + 0.9, WHITE_COL_Y + 1.85):
        add_box(bm, W - 0.03, W - 0.01, dy - 0.03, dy + 0.03, 1.0, 1.06)
        add_box(bm, W - 0.03, W + 0.03, dy - 0.45, dy - 0.33, 0.0, 0.08)
    mesh_object("PartitionFrame", bm, coll, [M["alu"]])

    bm = bmesh.new()
    add_box(bm, W, W + 0.25, y0 - T, D, gz, H, 0)
    add_box(bm, W, W + 4.0, -T, D, -0.02, 0.0, 1)
    add_box(bm, W + 4.0, W + 4.2, -T, D, 0.0, gz + 0.3, 0)
    add_box(bm, W, W + 4.0, -T, D, gz + 0.3, gz + 0.32, 0)
    mesh_object("Corridor", bm, coll, [M["white"], M["tile"]])
    bm = bmesh.new()
    for k in range(5):
        y = 0.8 + k * 2.1
        add_box(bm, W + 1.0, W + 3.0, y - 0.06, y + 0.06, gz + 0.27, gz + 0.3)
    mesh_object("CorridorLights", bm, coll, [M["led"]])


def build_structure(coll, M):
    cx, cy = COL_C
    kx0, kx1, _ = KITCHEN
    bm = bmesh.new()
    add_box(bm, cx - 0.3, cx + 0.3, cy - 0.3, cy + 0.3, 0, H)
    add_box(bm, kx0 - 0.6, kx0, D - 0.35, D, 0, H)
    add_box(bm, 1.4, 2.6, 0, 0.6, 0, H)
    mesh_object("Columns", bm, coll, [M["graphite"]])

    bm = bmesh.new()
    add_quad(bm, [(-T, -T, H), (-T, D + 1.1, H), (W + T, D + 1.1, H), (W + T, -T, H)])
    add_box(bm, 0, W, cy - 0.28, cy + 0.28, H - 0.62, H)
    add_box(bm, cx - 0.28, cx + 0.28, 0, D, H - 0.62, H)
    add_box(bm, 0, W, 0, 0.45, H - 0.55, H)
    add_box(bm, 0, W, D - 0.4, D, H - 0.55, H)
    add_box(bm, 0, 0.5, 0, D, H - 0.55, H)
    add_box(bm, W - 0.45, W, 0, D, H - 0.55, H)
    add_box(bm, 1.4, 2.6, 0, cy - 0.28, H - 0.62, H)
    for y in (cy / 2, cy + (D - cy) / 2):
        add_box(bm, 0.5, W - 0.45, y - 0.13, y + 0.13, H - 0.32, H)
    for x in (cx / 2, cx + (W - cx) / 2):
        add_box(bm, x - 0.13, x + 0.13, 0.45, D - 0.4, H - 0.32, H)
    mesh_object("CeilingStructure", bm, coll, [M["ceiling"]])

    bm = bmesh.new()
    zd = H - 0.36
    add_cylinder(bm, (0.5, 3.6, zd), (W, 3.6, zd), 0.17, 16, 0)
    add_cylinder(bm, (0.5, 7.2, zd), (W, 7.2, zd), 0.13, 16, 0)
    add_cylinder(bm, (8.6, 0.45, zd - 0.05), (8.6, D - 0.4, zd - 0.05), 0.11, 14, 0)
    for k in range(4):
        x = 2.0 + k * 3.0
        add_box(bm, x - 0.22, x + 0.22, 3.6 - 0.12, 3.6 + 0.12, zd - 0.24, zd - 0.17, 1)
        add_box(bm, x - 0.18, x + 0.18, 7.2 - 0.1, 7.2 + 0.1, zd - 0.2, zd - 0.13, 1)
    for x in (0.8, 1.0):
        add_cylinder(bm, (x, 0.45, H - 0.12), (x, D - 0.4, H - 0.12), 0.035, 8, 0)
    add_cylinder(bm, (0.5, 1.1, H - 0.1), (W - 0.45, 1.1, H - 0.1), 0.04, 8, 0)
    add_cylinder(bm, (0.5, 9.1, H - 0.1), (W - 0.45, 9.1, H - 0.1), 0.05, 8, 0)
    tz = H - 0.42
    y = 6.3
    add_box(bm, 0.5, W - 0.45, y - 0.15, y + 0.15, tz, tz + 0.006, 2)
    add_box(bm, 0.5, W - 0.45, y - 0.15, y - 0.144, tz, tz + 0.06, 2)
    add_box(bm, 0.5, W - 0.45, y + 0.144, y + 0.15, tz, tz + 0.06, 2)
    for k in range(int((W - 1) / 1.2)):
        x = 1.0 + k * 1.2
        add_box(bm, x - 0.004, x + 0.004, y - 0.15, y + 0.15, tz + 0.06, H, 2)
    add_box(bm, 3.0, 3.06, 0.45, D - 0.4, H - 0.36, H - 0.32, 2)
    for i in range(4):
        for j in range(4):
            x = 1.5 + i * 2.9
            y = 1.3 + j * 2.6
            add_cylinder(bm, (x, y, H), (x, y, H - 0.14), 0.012, 6, 3)
            add_cylinder(bm, (x, y, H - 0.14), (x, y, H - 0.16), 0.035, 10, 3, caps=True)
    for x, y in ((2.2, 2.4), (4.5, 8.4), (8.0, 2.6), (9.8, 8.2), (3.5, 6.2), (8.8, 5.6)):
        add_cylinder(bm, (x, y, H), (x, y, H - 0.05), 0.06, 14, 4, caps=True)
    mesh_object("CeilingServices", bm, coll, [M["pipe"], M["metal_dark"], M["metal_dark"], M["alu"], M["white"]])

    bm = bmesh.new()
    lbm = bmesh.new()
    cells = [(i, j) for i in range(7) for j in range(5)][1:-1]
    for i, j in cells:
        lx = 0.9 + (W - 1.8) * (i + 0.5) / 7 + random.uniform(-0.3, 0.3)
        ly = 0.9 + (D - 1.8) * (j + 0.5) / 5 + random.uniform(-0.3, 0.3)
        if math.hypot(lx - cx, ly - cy) < 1.0:
            lx += 1.0
        a = random.uniform(0, math.pi)
        lz = 3.35 + random.uniform(-0.25, 0.3)
        ln = 1.5
        rot = Matrix.Rotation(a, 4, "Z")
        add_transformed_box(bm, (ln, 0.06, 0.04), Matrix.Translation((lx, ly, lz + 0.05)) @ rot)
        add_transformed_box(lbm, (ln - 0.02, 0.064, 0.032), Matrix.Translation((lx, ly, lz + 0.014)) @ rot)
        d = Vector((math.cos(a), math.sin(a), 0)) * (ln / 2 - 0.15)
        for s in (-1, 1):
            p = Vector((lx, ly, lz + 0.07)) + d * s
            add_cylinder(bm, p, (p.x, p.y, H - 0.02), 0.004, 4)
            add_cylinder(bm, (p.x, p.y, H - 0.02), (p.x, p.y, H - 0.035), 0.03, 8, caps=True)
    mesh_object("PendantLights", bm, coll, [M["metal_dark"]])
    mesh_object("PendantLightsDiffuser", lbm, coll, [M["led"]])


def build_clock(coll, M):
    bm = bmesh.new()
    cz = 2.55
    yw = D - 0.01
    for k in range(12):
        a = 2 * math.pi * k / 12
        place = Matrix.Translation((CLOCK_X + math.sin(a) * 0.7, yw - 0.01, cz + math.cos(a) * 0.7)) @ Matrix.Rotation(-a, 4, "Y")
        size = (0.1, 0.015, 0.14) if k % 3 == 0 else (0.03, 0.015, 0.14)
        add_transformed_box(bm, size, place)
    for ang, ln, wd in ((-0.55, 0.42, 0.035), (2.0, 0.6, 0.025)):
        place = Matrix.Translation((CLOCK_X, yw - 0.025, cz)) @ Matrix.Rotation(ang, 4, "Y") @ Matrix.Translation((0, 0, ln / 2 - 0.05))
        add_transformed_box(bm, (wd, 0.012, ln), place)
    add_cylinder(bm, (CLOCK_X, yw, cz), (CLOCK_X, yw - 0.04, cz), 0.03, 12, caps=True)
    mesh_object("WallClock", bm, coll, [M["metal_dark"]])


def build_floor(coll, M):
    bm = bmesh.new()
    add_quad(bm, [(0, 0, 0), (W, 0, 0), (W, D, 0), (0, D, 0)])
    add_quad(bm, [(KITCHEN[0], D, 0), (KITCHEN[1], D, 0), (KITCHEN[1], D + KITCHEN[2], 0), (KITCHEN[0], D + KITCHEN[2], 0)])
    floor = mesh_object("Floor", bm, coll, [M["floor"]])
    box_uv(floor, 1.2, rot45=True)


def build_view(coll, M):
    bm = bmesh.new()
    vimg = image("view_library.jpg")
    radius = 30.0
    span = math.radians(120)
    vw = radius * span
    vh = vw * vimg.size[1] / vimg.size[0]
    vz0 = -10.5
    seg = 48
    uvl = bm.loops.layers.uv.new("UVMap")
    cols = []
    for i in range(seg + 1):
        u = i / seg
        a = -span / 2 + span * u - math.radians(14)
        x, y = radius * math.sin(a), radius * math.cos(a)
        cols.append((u, bm.verts.new((x, y, vz0)), bm.verts.new((x, y, vz0 + vh))))
    for (u0, b0, t0), (u1, b1, t1) in zip(cols, cols[1:]):
        f = bm.faces.new([b0, b1, t1, t0])
        for l, uvc in zip(f.loops, [(u0, 0), (u1, 0), (u1, 1), (u0, 1)]):
            l[uvl].uv = uvc
    mesh_object("ViewLibrary", bm, coll, [M["view"]], Matrix.Translation((W / 2, D / 2, 0)) @ WEST)


def preview_rig(coll):
    sun = bpy.data.lights.new("Sun", "SUN")
    sun.energy = 4.0
    sun.angle = math.radians(2)
    s = bpy.data.objects.new("Sun", sun)
    s.rotation_euler = (math.radians(58), 0, math.radians(-110))
    coll.objects.link(s)
    for i, cu in enumerate(WIN_U):
        a = bpy.data.lights.new(f"WindowFill{i}", "AREA")
        a.shape = "RECTANGLE"
        a.size, a.size_y = WIN_H, WIN_W
        a.energy = 500
        a.color = (0.9, 0.95, 1.0)
        o = bpy.data.objects.new(f"WindowFill{i}", a)
        o.location = ORIGIN + Vector((-0.3, cu, SILL + WIN_H / 2))
        o.rotation_euler = (0, math.radians(-90), 0)
        coll.objects.link(o)
    a = bpy.data.lights.new("CeilingFill", "AREA")
    a.shape = "RECTANGLE"
    a.size, a.size_y = W - 1, D - 1
    a.energy = 400
    o = bpy.data.objects.new("CeilingFill", a)
    o.location = (0, 0, 3.2)
    coll.objects.link(o)
    cam = bpy.data.cameras.new("Camera")
    cam.lens = 16
    c = bpy.data.objects.new("Camera", cam)
    coll.objects.link(c)
    bpy.context.scene.camera = c
    w = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = w
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs["Color"].default_value = (0.75, 0.82, 0.9, 1)
    bg.inputs["Strength"].default_value = 0.4
    bpy.context.scene.view_settings.exposure = -0.4


VIEWS = {
    "entrance": ((W - 1.0, 0.9, 1.55), (88, 0, 52)),
    "along_clock_wall": ((0.9, 6.0, 1.5), (88, 0, -84)),
    "windows": ((8.8, D / 2 + 1.7, 1.6), (88, 0, 98)),
}


def set_view(name):
    loc, rot = VIEWS[name]
    c = bpy.context.scene.camera
    c.location = ORIGIN + Vector(loc)
    c.rotation_euler = tuple(math.radians(v) for v in rot)


def render_previews(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    s = bpy.context.scene
    s.render.resolution_x, s.render.resolution_y = 1600, 900
    s.render.image_settings.file_format = "JPEG"
    s.render.image_settings.quality = 82
    for name in VIEWS:
        set_view(name)
        s.render.filepath = os.path.join(out_dir, f"{name}.jpg")
        bpy.ops.render.render(write_still=True)


def export_glb(path=OUT_GLB):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    for ob in bpy.data.collections["Room"].all_objects:
        ob.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=path,
        export_format="GLB",
        use_selection=True,
        export_yup=True,
        export_apply=True,
        export_lights=False,
        export_cameras=False,
        export_image_format="AUTO",
        export_extras=False,
    )
    return os.path.getsize(path)


def build():
    reset()
    M = materials()
    room = collection("Room")
    build_floor(room, M)
    build_window_wall(room, M)
    build_walls(room, M)
    build_partition(room, M)
    build_structure(room, M)
    build_clock(room, M)
    build_view(room, M)
    root = bpy.data.objects.new("ARKA123", None)
    room.objects.link(root)
    for ob in room.objects:
        if ob is not root:
            ob.parent = root
    root.location = ORIGIN
    preview_rig(collection("Preview"))
    set_view("entrance")
    return len(room.objects)


if __name__ == "__main__":
    print(build())
