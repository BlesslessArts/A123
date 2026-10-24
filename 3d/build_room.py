import math
import os
import random

import bmesh
import bpy
from mathutils import Matrix, Vector

ROOT = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.environ["A123_3D"]
TEX = os.path.join(ROOT, "textures")
OUT_GLB = os.path.join(ROOT, "..", "public", "models", "arka123.glb")

W = 12.3
D = 10.0
H = 4.5
T = 0.4
WIN_W = 4.0
WIN_H = 3.3
WIN_RISE = 1.7
SILL = 0.95
WIN_X = (-2.9, 2.9)
COL_X = (-3.2, 3.2)
COL_Y = -2.4
X0, X1 = -W / 2, W / 2
Y0, Y1 = -D / 2, D / 2

random.seed(123)


def reset():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.images, bpy.data.collections, bpy.data.lights, bpy.data.cameras):
        for b in list(coll):
            if b.users == 0:
                coll.remove(b)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)


def collection(name, parent=None):
    c = bpy.data.collections.new(name)
    (parent or bpy.context.scene.collection).children.link(c)
    return c


def image(name):
    path = os.path.join(TEX, name)
    img = bpy.data.images.load(path, check_existing=True)
    return img


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
    return m


def mesh_object(name, bm, coll, mats):
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
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    for f in faces:
        bm.faces.new([vs[i] for i in f]).material_index = mat


def box_uv(ob, scale=1.0, rot45=False):
    me = ob.data
    uv = me.uv_layers.new(name="UVMap") if not me.uv_layers else me.uv_layers[0]
    mw = ob.matrix_world
    c45 = math.cos(math.pi / 4)
    for poly in me.polygons:
        n = poly.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        for li in poly.loop_indices:
            p = mw @ me.vertices[me.loops[li].vertex_index].co
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
    t = max(0.0, 1.0 - (x / hw) ** 2)
    return h - rise + r * math.sqrt(t)


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
    lay = []
    for y in (y0, y1):
        lay.append(([bm.verts.new((cx + x, y, z0 + z)) for x, z in outer], [bm.verts.new((cx + x, y, z0 + z)) for x, z in inner]))
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
    ev = target.evaluated_get(dg)
    me = bpy.data.meshes.new_from_object(ev)
    old = target.data
    target.modifiers.clear()
    target.data = me
    bpy.data.meshes.remove(old)
    me.name = target.name
    bpy.data.objects.remove(cutter)


def build_room(coll, M):
    bm = bmesh.new()
    floor_v = [bm.verts.new(v) for v in [(X0, Y0, 0), (X1, Y0, 0), (X1, Y1, 0), (X0, Y1, 0)]]
    bm.faces.new(floor_v)
    floor = mesh_object("Floor", bm, coll, [M["floor"]])
    box_uv(floor, 1.2, rot45=True)

    bm = bmesh.new()
    add_box(bm, X0 - T, X1 + T, Y1, Y1 + T, 0, H)
    win_wall = mesh_object("WindowWall", bm, coll, [M["plaster"]])
    cbm = bmesh.new()
    for cx in WIN_X:
        prism(cbm, arch_profile(WIN_W, WIN_H, WIN_RISE), cx, SILL, Y1 - 0.1, Y1 + T + 0.1)
    bmesh.ops.recalc_face_normals(cbm, faces=cbm.faces)
    cutter = mesh_object("Cutter", cbm, coll, [])
    apply_boolean(win_wall, cutter)
    box_uv(win_wall, 2.0)

    bm = bmesh.new()
    add_box(bm, X0 - T, X0, Y0, Y1, 0, H)
    add_box(bm, X1, X1 + T, Y0, Y1, 0, H)
    add_box(bm, -0.5, X1 + T, Y0 - T, Y0, 0, H)
    add_box(bm, X0 - T, -0.5, Y0 - T, Y0, 3.0, H)
    walls = mesh_object("Walls", bm, coll, [M["plaster"]])
    box_uv(walls, 2.0)

    bm = bmesh.new()
    cv = [bm.verts.new(v) for v in [(X0, Y0, H), (X0, Y1, H), (X1, Y1, H), (X1, Y0, H)]]
    bm.faces.new(cv)
    add_box(bm, -0.25, 0.25, COL_Y, Y1, H - 0.5, H)
    add_box(bm, X0, X1, COL_Y - 0.25, COL_Y + 0.25, H - 0.55, H)
    add_box(bm, X0, X1, Y1 - 0.35, Y1, H - 0.4, H)
    for cx in COL_X:
        add_box(bm, cx - 0.3, cx + 0.3, COL_Y - 0.3, COL_Y + 0.3, 0, H)
    for i, y in enumerate((1.2, 2.0)):
        r = 0.09 if i == 0 else 0.06
        ring = [(math.cos(2 * math.pi * k / 12) * r, math.sin(2 * math.pi * k / 12) * r) for k in range(12)]
        vs0 = [bm.verts.new((X0, y + a, H - 0.25 + b)) for a, b in ring]
        vs1 = [bm.verts.new((X1, y + a, H - 0.25 + b)) for a, b in ring]
        for k in range(12):
            j = (k + 1) % 12
            bm.faces.new([vs0[k], vs0[j], vs1[j], vs1[k]])
    mesh_object("CeilingStructure", bm, coll, [M["graphite"]])
    bm = bmesh.new()
    sk = 0.07
    add_box(bm, X0, X1, Y0, Y0 + 0.012, 0, sk)
    add_box(bm, X0, X0 + 0.012, Y0, Y1, 0, sk)
    add_box(bm, X1 - 0.012, X1, Y0, Y1, 0, sk)
    add_box(bm, X0, X1, Y1 - 0.012, Y1, 0, sk)
    for cx in WIN_X:
        add_box(bm, cx - WIN_W / 2 - 0.05, cx + WIN_W / 2 + 0.05, Y1 - 0.08, Y1 + 0.2, SILL - 0.04, SILL)
        add_box(bm, cx - 0.95, cx + 0.95, Y1 - 0.18, Y1 - 0.08, 0.16, 0.66)
        for k in range(48):
            fx = cx - 0.95 + 0.02 + k * 0.0395
            add_box(bm, fx, fx + 0.018, Y1 - 0.2, Y1 - 0.18, 0.16, 0.66)
    mesh_object("DarkTrim", bm, coll, [M["metal_dark"]])

    bm = bmesh.new()
    gbm = bmesh.new()
    ft = 0.07
    fd0, fd1 = Y1 + 0.12, Y1 + 0.2
    for cx in WIN_X:
        outer = arch_profile(WIN_W, WIN_H, WIN_RISE)
        inner = arch_profile(WIN_W, WIN_H, WIN_RISE, inset=ft)
        ring_prism(bm, outer, inner, cx, SILL, fd0, fd1)
        tz = 1.25
        add_box(bm, cx - WIN_W / 2, cx + WIN_W / 2, fd0, fd1, SILL + tz, SILL + tz + 0.06)
        for mx in (-0.95, 0.95):
            top = arch_height(mx, WIN_W, WIN_H, WIN_RISE, ft) - 0.01
            add_box(bm, cx + mx - 0.03, cx + mx + 0.03, fd0, fd1, SILL, SILL + top)
        add_box(bm, cx - WIN_W / 2, cx - 0.95, fd0, fd1, SILL + WIN_H - WIN_RISE - 0.03, SILL + WIN_H - WIN_RISE + 0.03)
        add_box(bm, cx + 0.95, cx + WIN_W / 2, fd0, fd1, SILL + WIN_H - WIN_RISE - 0.03, SILL + WIN_H - WIN_RISE + 0.03)
        gv = [gbm.verts.new((cx + x, Y1 + 0.16, SILL + z)) for x, z in inner]
        gbm.faces.new(gv)
    mesh_object("WindowFrames", bm, coll, [M["frame"]])
    mesh_object("WindowGlass", gbm, coll, [M["glass"]])

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
    mesh_object("ViewLibrary", bm, coll, [M["view"]])

    bm = bmesh.new()
    add_box(bm, X0 - T, -0.5, Y0 - 0.03, Y0 - 0.01, 0, 3.0)
    mesh_object("PartitionGlass", bm, coll, [M["glass_frost"]])
    bm = bmesh.new()
    x = X0
    while x < -0.5 + 1e-3:
        add_box(bm, x - 0.025, x + 0.025, Y0 - 0.05, Y0 + 0.01, 0, 3.0)
        x += (-0.5 - X0) / 5
    add_box(bm, X0, -0.5, Y0 - 0.05, Y0 + 0.01, 2.96, 3.02)
    for z in (1.0, 1.15, 1.45):
        add_box(bm, X0, -0.5, Y0 - 0.035, Y0 + 0.0, z, z + 0.05 if z != 1.15 else z + 0.22)
    mesh_object("PartitionFrame", bm, coll, [M["frost_band"]])

    bm = bmesh.new()
    add_box(bm, X0 - T, 2.6, Y0 - 3.0, Y0 - T, -0.01, 0.0)
    add_box(bm, X0 - T, 2.6, Y0 - 3.2, Y0 - 3.0, 0, 3.0)
    add_box(bm, X0 - T, 2.6, Y0 - 3.0, Y0 - T, 3.0, 3.02)
    mesh_object("Corridor", bm, coll, [M["white"]])

    bm = bmesh.new()
    add_box(bm, -0.5, 2.6, Y0, Y0 + 0.03, 0.0, 3.0)
    add_box(bm, 2.6, X1, Y0, Y0 + 0.08, 0.0, H)
    add_box(bm, 2.6, 2.68, Y0, Y0 + 1.1, 0.0, H)
    add_box(bm, 4.05, 4.65, Y0 + 0.3, Y0 + 0.9, 0.0, 1.1, mat=1)
    add_box(bm, 3.0, 4.05, Y0 + 0.35, Y0 + 0.95, 0.0, 0.78)
    for i, (a, b) in enumerate(((-0.5, 0.1), (0.1, 0.75), (0.75, 1.4), (1.4, 2.0), (2.0, 2.6))):
        add_box(bm, a + 0.004, a + 0.010, Y0 + 0.03, Y0 + 0.035, 0.07, 3.0, mat=2)
        zc = 1.2 + 0.9 * ((i * 37) % 5) / 5
        add_box(bm, a, b, Y0 + 0.03, Y0 + 0.035, zc, zc + 0.006, mat=2)
    add_box(bm, -0.5, 2.6, Y0 + 0.03, Y0 + 0.035, 2.994, 3.0, mat=2)
    add_box(bm, 1.35, 1.65, Y0 + 0.03, Y0 + 0.04, 1.35, 1.42, mat=2)
    add_box(bm, 1.35, 1.65, Y0 + 0.03, Y0 + 0.04, 1.5, 1.57, mat=2)
    mesh_object("BackPanels", bm, coll, [M["white"], M["graphite_panel"], M["metal_dark"]])
    bm = bmesh.new()
    add_box(bm, 3.1, 5.6, Y0 + 0.08, Y0 + 0.3, 1.25, 1.3)
    add_box(bm, 3.1, 5.6, Y0 + 0.08, Y0 + 0.1, 1.3, 1.62)
    mesh_object("ReceptionShelfLight", bm, coll, [M["led_warm"]])
    bm = bmesh.new()
    add_box(bm, 2.68, X1, Y0 + 0.08, Y0 + 0.09, 0.0, H)
    mesh_object("ReceptionWall", bm, coll, [M["graphite_panel"]])

    bm = bmesh.new()
    cz, cy = 2.6, 0.0
    for k in range(12):
        a = 2 * math.pi * k / 12
        r0, r1 = (0.62, 0.8) if k % 3 == 0 else (0.7, 0.8)
        mid = (r0 + r1) / 2
        ln = (r1 - r0) / 2
        c = Vector((0, cy + math.sin(a) * mid, cz + math.cos(a) * mid))
        tbm = bmesh.new()
        bmesh.ops.create_cube(tbm, size=1.0)
        bmesh.ops.scale(tbm, vec=(0.02, 0.035, ln * 2), verts=tbm.verts)
        bmesh.ops.rotate(tbm, verts=tbm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(-a, 3, "X"))
        bmesh.ops.translate(tbm, verts=tbm.verts, vec=(X1 - 0.02, c.y, c.z))
        tme = bpy.data.meshes.new("t")
        tbm.to_mesh(tme)
        tbm.free()
        bm.from_mesh(tme)
        bpy.data.meshes.remove(tme)
    for ang, ln, wd in ((-0.6, 0.42, 0.04), (1.9, 0.6, 0.03)):
        tbm = bmesh.new()
        bmesh.ops.create_cube(tbm, size=1.0)
        bmesh.ops.scale(tbm, vec=(0.02, wd, ln), verts=tbm.verts)
        bmesh.ops.translate(tbm, verts=tbm.verts, vec=(0, 0, ln / 2))
        bmesh.ops.rotate(tbm, verts=tbm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(-ang, 3, "X"))
        bmesh.ops.translate(tbm, verts=tbm.verts, vec=(X1 - 0.03, cy, cz))
        tme = bpy.data.meshes.new("t")
        tbm.to_mesh(tme)
        tbm.free()
        bm.from_mesh(tme)
        bpy.data.meshes.remove(tme)
    mesh_object("WallClock", bm, coll, [M["metal_dark"]])

    bm = bmesh.new()
    for i in range(20):
        lx = random.uniform(X0 + 1.2, X1 - 1.2)
        ly = random.uniform(Y0 + 1.5, Y1 - 1.2)
        a = random.uniform(0, math.pi)
        tbm = bmesh.new()
        bmesh.ops.create_cube(tbm, size=1.0)
        bmesh.ops.scale(tbm, vec=(1.6, 0.05, 0.06), verts=tbm.verts)
        bmesh.ops.rotate(tbm, verts=tbm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(a, 3, "Z"))
        bmesh.ops.translate(tbm, verts=tbm.verts, vec=(lx, ly, 3.55 + random.uniform(-0.15, 0.15)))
        tme = bpy.data.meshes.new("t")
        tbm.to_mesh(tme)
        tbm.free()
        bm.from_mesh(tme)
        bpy.data.meshes.remove(tme)
    mesh_object("PendantLights", bm, coll, [M["led"]])


def build_furniture_meshes(M):
    def to_mesh(name, bm, mats):
        me = bpy.data.meshes.new(name)
        bm.to_mesh(me)
        bm.free()
        for m in mats:
            me.materials.append(m)
        return me

    bm = bmesh.new()
    lw = 0.022
    for sx in (-1, 1):
        for sy in (-1, 1):
            x = sx * 0.2
            y = sy * 0.19
            add_box(bm, x - lw / 2, x + lw / 2, y - lw / 2, y + lw / 2, 0, 0.44, 0)
    for sx in (-1, 1):
        x = sx * 0.2
        add_box(bm, x - lw / 2, x + lw / 2, -0.21 - lw / 2, -0.21 + lw / 2, 0.44, 0.86, 0)
    add_box(bm, -0.23, 0.23, -0.21, 0.23, 0.44, 0.47, 1)
    add_box(bm, -0.23, 0.23, -0.23, -0.2, 0.6, 0.86, 1)
    chair = to_mesh("Chair", bm, [M["metal_dark"], M["oak"]])

    def table(name, lx, ly, mats):
        bm = bmesh.new()
        add_box(bm, -lx / 2, lx / 2, -ly / 2, ly / 2, 0.71, 0.75, 1)
        inset = 0.08
        for sx in (-1, 1):
            for sy in (-1, 1):
                x = sx * (lx / 2 - inset)
                y = sy * (ly / 2 - inset)
                add_box(bm, x - 0.025, x + 0.025, y - 0.025, y + 0.025, 0, 0.71, 0)
        add_box(bm, -lx / 2 + inset, lx / 2 - inset, -ly / 2 + inset - 0.01, -ly / 2 + inset + 0.01, 0.62, 0.71, 0)
        add_box(bm, -lx / 2 + inset, lx / 2 - inset, ly / 2 - inset - 0.01, ly / 2 - inset + 0.01, 0.62, 0.71, 0)
        return to_mesh(name, bm, mats)

    long_table = table("TableLong", 7.2, 1.4, [M["metal_dark"], M["white_top"]])
    small_table = table("TableSmall", 1.6, 0.9, [M["metal_dark"], M["white_top"]])

    bm = bmesh.new()
    add_box(bm, -0.02, 0.0, -1.7, 1.7, 1.05, 3.05, 0)
    add_box(bm, 0.0, 0.01, -1.6, 1.6, 1.15, 2.95, 1)
    screen = to_mesh("ProjectionScreen", bm, [M["metal_dark"], M["screen"]])

    bm = bmesh.new()
    add_box(bm, -0.22, 0.22, -0.3, 0.3, 0.0, 0.05, 0)
    add_box(bm, -0.15, 0.15, -0.2, 0.2, 0.05, 1.0, 1)
    add_box(bm, -0.25, 0.22, -0.32, 0.32, 1.0, 1.12, 1)
    lectern = to_mesh("Lectern", bm, [M["metal_dark"], M["oak"]])

    bm = bmesh.new()
    add_box(bm, -0.18, 0.18, -0.15, 0.15, 3.2, 3.32, 0)
    add_box(bm, -0.015, 0.015, -0.015, 0.015, 3.32, H - 0.55, 0)
    projector = to_mesh("Projector", bm, [M["white"]])
    return dict(chair=chair, long=long_table, small=small_table, screen=screen, lectern=lectern, projector=projector)


def place(coll, mesh, name, x, y, rot_deg=0.0):
    ob = bpy.data.objects.new(name, mesh)
    ob.location = (x, y, 0)
    ob.rotation_euler = (0, 0, math.radians(rot_deg))
    coll.objects.link(ob)
    return ob


def layout_root(name, coll):
    e = bpy.data.objects.new(name, None)
    coll.objects.link(e)
    return e


def parent_all(root, obs):
    for ob in obs:
        ob.parent = root


def build_layouts(F, coll):
    counts = {}

    root = layout_root("Layout_empty", coll)
    counts["empty"] = 0

    root = layout_root("Layout_lecture", coll)
    obs = []
    screen_y = 1.4
    obs.append(place(coll, F["screen"], "Screen", X0 + 0.02, screen_y))
    obs.append(place(coll, F["lectern"], "Lectern", X0 + 1.3, screen_y - 2.3, 0))
    obs.append(place(coll, F["projector"], "Projector", -1.0, screen_y))
    n = 0
    for r in range(7):
        x = -3.6 + r * 1.0
        for y in (3.6, 3.05, 2.5, 1.95, 0.85, 0.3, -0.25, -0.8):
            obs.append(place(coll, F["chair"], f"Lecture_Chair_{n:02d}", x, y, 90))
            n += 1
    parent_all(root, obs)
    counts["lecture"] = n

    root = layout_root("Layout_table", coll)
    obs = []
    tx, ty = 0.3, 1.2
    obs.append(place(coll, F["long"], "BigTable", tx, ty))
    n = 0
    for k in range(9):
        x = tx - 3.12 + k * 0.78
        obs.append(place(coll, F["chair"], f"Table_Chair_{n:02d}", x, ty - 0.95, 0)); n += 1
        obs.append(place(coll, F["chair"], f"Table_Chair_{n:02d}", x, ty + 0.95, 180)); n += 1
    obs.append(place(coll, F["chair"], f"Table_Chair_{n:02d}", tx - 4.05, ty, -90)); n += 1
    obs.append(place(coll, F["chair"], f"Table_Chair_{n:02d}", tx + 4.05, ty, 90)); n += 1
    parent_all(root, obs)
    counts["table"] = n

    root = layout_root("Layout_groups", coll)
    obs = []
    n = 0
    t = 0
    for gy in (2.7, -0.5):
        for gx in (-3.8, 0.0, 3.8):
            obs.append(place(coll, F["small"], f"GroupTable_{t}", gx, gy)); t += 1
            for dx in (-0.4, 0.4):
                obs.append(place(coll, F["chair"], f"Group_Chair_{n:02d}", gx + dx, gy - 0.72, 0)); n += 1
                obs.append(place(coll, F["chair"], f"Group_Chair_{n:02d}", gx + dx, gy + 0.72, 180)); n += 1
            obs.append(place(coll, F["chair"], f"Group_Chair_{n:02d}", gx - 1.12, gy, -90)); n += 1
            obs.append(place(coll, F["chair"], f"Group_Chair_{n:02d}", gx + 1.12, gy, 90)); n += 1
    parent_all(root, obs)
    counts["groups"] = n
    return counts


def materials():
    return dict(
        floor=material("Floor_Herringbone", tex="floor_herringbone.jpg", rough=0.55),
        plaster=material("Wall_Plaster", tex="wall_plaster.jpg", rough=0.9),
        graphite=material("Ceiling_Graphite", color=(0.06, 0.065, 0.07), rough=0.85),
        graphite_panel=material("Panel_Graphite", color=(0.11, 0.115, 0.12), rough=0.6),
        metal_dark=material("Metal_Black", color=(0.025, 0.025, 0.028), rough=0.45, metal=0.6),
        frame=material("Window_Frame", color=(0.03, 0.032, 0.035), rough=0.4, metal=0.3),
        glass=material("Window_Glass", color=(0.75, 0.82, 0.85), rough=0.05, alpha=0.12),
        glass_frost=material("Partition_Glass", color=(0.85, 0.88, 0.9), rough=0.2, alpha=0.3),
        frost_band=material("Partition_Frame", color=(0.75, 0.77, 0.8), rough=0.35, metal=0.5),
        white=material("Panel_White", color=(0.86, 0.86, 0.85), rough=0.5),
        white_top=material("Table_White", color=(0.9, 0.9, 0.88), rough=0.35),
        oak=material("Oak", color=(0.55, 0.38, 0.22), rough=0.5),
        screen=material("Screen", color=(0.95, 0.95, 0.95), rough=0.9),
        led=material("LED_Linear", color=(1, 1, 1), emit=(1.0, 0.97, 0.92), emit_strength=6.0),
        led_warm=material("LED_Shelf", color=(1, 1, 1), emit=(0.85, 0.93, 1.0), emit_strength=3.0),
        view=material("View_Library", emit_tex="view_library.jpg", emit_strength=1.0),
    )


def preview_lighting(coll):
    sun = bpy.data.lights.new("Sun", "SUN")
    sun.energy = 4.0
    sun.angle = math.radians(2)
    s = bpy.data.objects.new("Sun", sun)
    s.rotation_euler = (math.radians(55), 0, math.radians(200))
    coll.objects.link(s)
    for i, cx in enumerate(WIN_X):
        a = bpy.data.lights.new(f"WindowFill{i}", "AREA")
        a.shape = "RECTANGLE"
        a.size, a.size_y = WIN_W, WIN_H
        a.energy = 500
        a.color = (0.9, 0.95, 1.0)
        o = bpy.data.objects.new(f"WindowFill{i}", a)
        o.location = (cx, Y1 + 0.3, SILL + WIN_H / 2)
        o.rotation_euler = (math.radians(-90), 0, 0)
        coll.objects.link(o)
    a = bpy.data.lights.new("CeilingFill", "AREA")
    a.shape = "RECTANGLE"
    a.size, a.size_y = W - 1, D - 1
    a.energy = 350
    o = bpy.data.objects.new("CeilingFill", a)
    o.location = (0, 0, 3.4)
    coll.objects.link(o)
    cam = bpy.data.cameras.new("Camera")
    cam.lens = 18
    c = bpy.data.objects.new("Camera", cam)
    c.location = (-1.5, -4.2, 1.6)
    c.rotation_euler = (math.radians(88), 0, math.radians(-8))
    coll.objects.link(c)
    bpy.context.scene.camera = c
    w = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = w
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs["Color"].default_value = (0.75, 0.82, 0.9, 1)
    bg.inputs["Strength"].default_value = 0.4
    bpy.context.scene.view_settings.exposure = -0.4


def set_layout(name):
    for ob in bpy.data.objects:
        if ob.name.startswith("Layout_"):
            show = ob.name == f"Layout_{name}"
            for o in [ob, *ob.children]:
                o.hide_render = not show
                o.hide_viewport = not show


def export_glb(path=OUT_GLB):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    for ob in bpy.data.objects:
        ob.hide_viewport = False
        ob.hide_render = False
        ob.hide_set(False)
    bpy.ops.object.select_all(action="DESELECT")
    keep = set()
    for c in ("Room", "Layouts"):
        for ob in bpy.data.collections[c].all_objects:
            ob.select_set(True)
            keep.add(ob.name)
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


def render_previews(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    s = bpy.context.scene
    s.render.resolution_x, s.render.resolution_y = 1600, 900
    s.render.image_settings.file_format = "JPEG"
    s.render.image_settings.quality = 82
    for name in ("empty", "lecture", "table", "groups"):
        set_layout(name)
        s.render.filepath = os.path.join(out_dir, f"{name}.jpg")
        bpy.ops.render.render(write_still=True)


def build():
    reset()
    M = materials()
    room = collection("Room")
    layouts = collection("Layouts")
    preview = collection("Preview")
    build_room(room, M)
    F = build_furniture_meshes(M)
    counts = build_layouts(F, layouts)
    preview_lighting(preview)
    return counts


if __name__ == "__main__":
    print(build())
