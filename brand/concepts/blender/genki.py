# Darb Genki brand directions, rendered in Blender Cycles. Everything is built here in code: no imported art.
#   blender -b -P genki.py -- <direction> <out.png> [size] [samples]
#   directions: gather | mesh | trace | kintsugi
# Every direction carries one idea from the product and one from the show:
#   the product runs every Darb Budokai service on Kubernetes, traces every request across all of them into one
#   view (the Mesh Map), and breaks things on purpose (chaos drills) to prove it can see and recover;
#   in the show, the Genki-dama (Spirit Bomb) is one sphere of energy lent by everyone who raises their hands.
import bpy, sys, math, json, random
from pathlib import Path
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:]
D, OUT = argv[0], argv[1]
SIZE = int(argv[2]) if len(argv) > 2 else 1024
SAMPLES = int(argv[3]) if len(argv) > 3 else 160
ROOT = Path(__file__).resolve().parents[2]
T = json.loads((ROOT / 'src' / 'tokens.json').read_text())
rng = random.Random(T['render']['seed'])


def lin(hexstr, k=1.0):
    """sRGB hex to linear RGBA, optionally scaled."""
    h = hexstr.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return (c[0] * k, c[1] * k, c[2] * k, 1.0)


COL = {k: v['hex'] for k, v in T['color'].items()}

# ---------- scene, renderer, colour ----------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
prefs = bpy.context.preferences.addons['cycles'].preferences
try:
    prefs.compute_device_type = 'METAL'
    prefs.get_devices()
    for d in prefs.devices:
        d.use = True
    scene.cycles.device = 'GPU'
except Exception as e:
    print('GPU unavailable, using CPU:', e)
scene.cycles.samples = SAMPLES
scene.cycles.use_denoising = True
scene.cycles.volume_step_rate = 1.0
scene.cycles.max_bounces = 12
scene.render.resolution_x = scene.render.resolution_y = SIZE
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = OUT
scene.view_settings.view_transform = 'AgX'
for look in ('AgX - Medium High Contrast', 'AgX - Punchy', 'AgX - Base Contrast'):
    try:
        scene.view_settings.look = look
        break
    except TypeError:
        pass
coll = scene.collection


def link(obj):
    coll.objects.link(obj)
    return obj


def node_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    return m, nt, out


def metal(name, hexstr, rough=0.22, aniso=0.0):
    m, nt, out = node_mat(name)
    b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    b.inputs['Base Color'].default_value = lin(hexstr)
    b.inputs['Metallic'].default_value = 1.0
    b.inputs['Roughness'].default_value = rough
    if aniso:
        b.inputs['Anisotropic'].default_value = aniso
    nt.links.new(b.outputs[0], out.inputs['Surface'])
    return m


def glossy(name, hexstr, rough=0.3, coat=1.0):
    m, nt, out = node_mat(name)
    b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    b.inputs['Base Color'].default_value = lin(hexstr)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Coat Weight'].default_value = coat
    b.inputs['Coat Roughness'].default_value = 0.06
    nt.links.new(b.outputs[0], out.inputs['Surface'])
    return m


def emissive(name, hexstr, strength):
    m, nt, out = node_mat(name)
    e = nt.nodes.new('ShaderNodeEmission')
    e.inputs['Color'].default_value = lin(hexstr)
    e.inputs['Strength'].default_value = strength
    nt.links.new(e.outputs[0], out.inputs['Surface'])
    return m


def to_mesh(obj):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    return bpy.context.view_layer.objects.active


def nimbus_hull(name, length=3.0, h=0.7, loc=(0, 0, 0), rot=0.0, res=0.035):
    """The cloud's envelope from metaballs: round, high crown at the front, thinning to a tail behind.
    The volume material erodes it into vapour; displacement breaks the silhouette."""
    mb = bpy.data.metaballs.new(name)
    mb.resolution = res
    mb.threshold = 0.6
    ob = link(bpy.data.objects.new(name, mb))
    n = 14
    for i in range(n):
        t = i / (n - 1)
        r = h * (0.16 + 0.84 * math.sin(math.pi * (0.06 + 0.6 * t)))
        e = mb.elements.new(); e.co = (-length / 2 + length * t, 0, r * 0.35); e.radius = r * 1.25
    for t, k in ((0.5, 0.9), (0.72, 1.15), (0.9, 0.85)):
        e = mb.elements.new(); e.co = (-length / 2 + length * t, rng.uniform(-.1, .1), h * 0.62 + h * k * 0.4); e.radius = h * k * 1.2
    ob = to_mesh(ob)
    tex = bpy.data.textures.new(name + '-clouds', 'CLOUDS'); tex.noise_scale = 0.35; tex.noise_depth = 4
    d = ob.modifiers.new('break', 'DISPLACE'); d.texture = tex; d.strength = 0.22; d.mid_level = 0.5
    ob.location = loc
    ob.rotation_euler = (0, rot, 0)  # Z is up, the camera looks along +Y, so Y rotation tilts it in the picture
    bpy.context.view_layer.update()
    return ob


def vapour(hull, name, density=6.0, glow=0.5, push=0.22, voxel=0.025, scale=1.6, detail=2.4):
    """Turns a hull mesh into a real cloud: mesh-to-volume, then displaced by a cloud texture so the edges
    tear into wisps; the shader multiplies the voxel density by fine noise for billowing detail."""
    vol = link(bpy.data.objects.new(name, bpy.data.volumes.new(name)))
    m2v = vol.modifiers.new('fill', 'MESH_TO_VOLUME'); m2v.object = hull
    m2v.resolution_mode = 'VOXEL_SIZE'; m2v.voxel_size = voxel; m2v.interior_band_width = 0.2; m2v.density = 1.0
    tex = bpy.data.textures.new(name + '-billow', 'CLOUDS'); tex.noise_scale = 0.45; tex.noise_depth = 5
    dsp = vol.modifiers.new('tear', 'VOLUME_DISPLACE'); dsp.texture = tex; dsp.strength = push; dsp.texture_mid_level = (0.5, 0.5, 0.5)
    hull.hide_render = True
    m, nt, out = node_mat(name + '-m')
    at = nt.nodes.new('ShaderNodeAttribute'); at.attribute_name = 'density'
    tc = nt.nodes.new('ShaderNodeTexCoord')
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = scale * detail; nz.inputs['Detail'].default_value = 14; nz.inputs['Roughness'].default_value = 0.6
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    ramp = nt.nodes.new('ShaderNodeMapRange'); ramp.inputs['From Min'].default_value = 0.38; ramp.inputs['From Max'].default_value = 0.66
    nt.links.new(nz.outputs['Fac'], ramp.inputs['Value'])
    a = nt.nodes.new('ShaderNodeMath'); a.operation = 'MULTIPLY'; nt.links.new(at.outputs['Fac'], a.inputs[0]); nt.links.new(ramp.outputs[0], a.inputs[1])
    b = nt.nodes.new('ShaderNodeMath'); b.operation = 'MULTIPLY'; b.inputs[1].default_value = density; nt.links.new(a.outputs[0], b.inputs[0])
    v = nt.nodes.new('ShaderNodeVolumePrincipled')
    v.inputs['Color'].default_value = lin('#F2C46A')
    v.inputs['Anisotropy'].default_value = 0.4
    v.inputs['Emission Color'].default_value = lin(COL['gold'])
    nt.links.new(b.outputs[0], v.inputs['Density'])
    e = nt.nodes.new('ShaderNodeMath'); e.operation = 'MULTIPLY'; e.inputs[1].default_value = glow; nt.links.new(a.outputs[0], e.inputs[0])
    nt.links.new(e.outputs[0], v.inputs['Emission Strength'])
    nt.links.new(v.outputs[0], out.inputs['Volume'])
    vol.data.materials.append(m)
    return vol


def tube_mesh(name, pts, radii, bevel):
    """A tapered tube as a mesh, used as a hull for vapour trails."""
    ob = tube(name, pts, radii, emissive(name + '-x', '#000000', 0), bevel=bevel, res=8)
    ob = to_mesh(ob)
    return ob


def tube(name, pts, radii, mat, bevel=1.0, res=6):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'
    cu.bevel_depth = bevel; cu.bevel_resolution = res; cu.use_fill_caps = True
    sp = cu.splines.new('NURBS'); sp.points.add(len(pts) - 1)
    for p, co, r in zip(sp.points, pts, radii):
        p.co = (*co, 1.0); p.radius = r
    sp.use_endpoint_u = True; sp.order_u = 4
    ob = link(bpy.data.objects.new(name, cu)); ob.data.materials.append(mat)
    return ob


def world(stars=True):
    w = bpy.data.worlds.new('night'); scene.world = w; w.use_nodes = True
    nt = w.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputWorld')
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Generated'], sep.inputs[0])
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = lin(COL['forest'], 0.5); ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[1].color = lin(COL['night'], 0.6); ramp.color_ramp.elements[1].position = 0.75
    nt.links.new(sep.outputs['Z'], ramp.inputs['Fac'])
    bg = nt.nodes.new('ShaderNodeBackground'); bg.inputs['Strength'].default_value = 0.6
    nt.links.new(ramp.outputs['Color'], bg.inputs['Color'])
    if stars:
        vor = nt.nodes.new('ShaderNodeTexVoronoi'); vor.inputs['Scale'].default_value = 260
        nt.links.new(tc.outputs['Generated'], vor.inputs['Vector'])
        st = nt.nodes.new('ShaderNodeMath'); st.operation = 'LESS_THAN'; st.inputs[1].default_value = 0.018
        nt.links.new(vor.outputs['Distance'], st.inputs[0])
        sb = nt.nodes.new('ShaderNodeBackground'); sb.inputs['Color'].default_value = (1, .95, .85, 1); sb.inputs['Strength'].default_value = 1.4
        add = nt.nodes.new('ShaderNodeMixShader')
        nt.links.new(st.outputs[0], add.inputs['Fac']); nt.links.new(bg.outputs[0], add.inputs[1]); nt.links.new(sb.outputs[0], add.inputs[2])
        nt.links.new(add.outputs[0], out.inputs['Surface'])
    else:
        nt.links.new(bg.outputs[0], out.inputs['Surface'])


def area(name, loc, target, power, hexstr, size=3.0, shape='DISK'):
    li = bpy.data.lights.new(name, 'AREA'); li.energy = power; li.color = lin(hexstr)[:3]; li.size = size; li.shape = shape
    ob = link(bpy.data.objects.new(name, li)); ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return ob


def point(name, loc, power, hexstr, radius=0.2):
    li = bpy.data.lights.new(name, 'POINT'); li.energy = power; li.color = lin(hexstr)[:3]; li.shadow_soft_size = radius
    ob = link(bpy.data.objects.new(name, li)); ob.location = loc
    return ob


def camera(loc, target, lens=60):
    cam = bpy.data.cameras.new('cam'); cam.lens = lens
    ob = link(bpy.data.objects.new('cam', cam)); ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    scene.camera = ob


def poly_curve(name, polys, extrude, bevel, mat, res=8):
    """Flat outlines (outer + nested holes) extruded and bevelled like cast metal."""
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '2D'; cu.fill_mode = 'BOTH'
    cu.extrude = extrude; cu.bevel_depth = bevel; cu.bevel_resolution = res
    for poly in polys:
        sp = cu.splines.new('POLY'); sp.points.add(len(poly) - 1)
        for p, (x, y) in zip(sp.points, poly):
            p.co = (x, y, 0, 1)
        sp.use_cyclic_u = True
    ob = link(bpy.data.objects.new(name, cu)); ob.data.materials.append(mat)
    return ob


def medallion(r=2.25):
    bpy.ops.mesh.primitive_cylinder_add(vertices=256, radius=r, depth=0.2, location=(0, 0, 0))
    disc = bpy.context.active_object
    bv = disc.modifiers.new('b', 'BEVEL'); bv.width = 0.05; bv.segments = 6
    bpy.ops.object.shade_smooth()
    disc.data.materials.append(glossy('lacquer', '#04140C', 0.32, 1.0))
    bpy.ops.mesh.primitive_torus_add(major_radius=r - 0.19, minor_radius=0.05, major_segments=256, minor_segments=24, location=(0, 0, 0.1))
    bpy.ops.object.shade_smooth()
    bpy.context.active_object.data.materials.append(metal('gold', COL['gold'], 0.16))



def sph(lat, lon, r):
    la, lo = math.radians(lat), math.radians(lon)
    return Vector((r * math.cos(la) * math.sin(lo), -r * math.cos(la) * math.cos(lo), r * math.sin(la)))


def arc_pts(a, b, r, lift, n=48):
    """A great-circle arc from a to b over a sphere of radius r, lifted in the middle like a thrown thread."""
    out = []
    for i in range(n + 1):
        t = i / n
        p = a.normalized().slerp(b.normalized(), t) if hasattr(Vector, 'slerp') else (a.normalized() * (1 - t) + b.normalized() * t).normalized()
        out.append(tuple(p.normalized() * (r * (1 + lift * math.sin(math.pi * t)))))
    return out


def thread(name, pts, hexstr, strength, width):
    """A thread of hostile ki: thin at its origin, full where it lands."""
    n = len(pts)
    return tube(name, pts, [0.15 + 0.85 * (i / (n - 1)) ** 1.2 for i in range(n)], emissive(name, hexstr, strength), bevel=width, res=4)




def glow_shell(loc, r, hexstr, density=0.25):
    """A soft halo: a slightly larger sphere of thin scattering haze around a light."""
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=r, location=loc)
    o = bpy.context.active_object
    m, nt, out = node_mat('halo')
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sc = nt.nodes.new('ShaderNodeVectorMath'); sc.operation = 'SCALE'; sc.inputs['Scale'].default_value = 1 / r
    nt.links.new(tc.outputs['Object'], sc.inputs[0])
    gr = nt.nodes.new('ShaderNodeTexGradient'); gr.gradient_type = 'SPHERICAL'
    nt.links.new(sc.outputs['Vector'], gr.inputs['Vector'])
    pw = nt.nodes.new('ShaderNodeMath'); pw.operation = 'POWER'; pw.inputs[1].default_value = 2.2
    nt.links.new(gr.outputs['Fac'], pw.inputs[0])
    mul = nt.nodes.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = density
    nt.links.new(pw.outputs[0], mul.inputs[0])
    v = nt.nodes.new('ShaderNodeVolumePrincipled'); v.inputs['Color'].default_value = lin(hexstr)
    v.inputs['Emission Color'].default_value = lin(hexstr)
    nt.links.new(mul.outputs[0], v.inputs['Density'])
    em = nt.nodes.new('ShaderNodeMath'); em.operation = 'MULTIPLY'; em.inputs[1].default_value = 3.0
    nt.links.new(pw.outputs[0], em.inputs[0]); nt.links.new(em.outputs[0], v.inputs['Emission Strength'])
    nt.links.new(v.outputs[0], out.inputs['Volume']); o.data.materials.append(m)
    return o


def bead(loc, hexstr, strength, r=0.04):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=r, location=loc)
    bpy.context.active_object.data.materials.append(emissive('bead', hexstr, strength))


if D == 'gather':
    # A "Lend Your Light": the Spirit Bomb as observability. Every service below raises one thread of light;
    # they all rise into a single sphere: one view, made of everyone's signal.
    world()
    core = Vector((0, 0, 1.25))
    bpy.ops.mesh.primitive_uv_sphere_add(segments=96, ring_count=48, radius=0.78, location=core)
    bpy.ops.object.shade_smooth(); bpy.context.active_object.data.materials.append(emissive('core', COL['goldLight'], 3.2))
    glow_shell(tuple(core), 2.0, COL['gold'], 1.2)
    point('heart', tuple(core), 900, COL['goldLight'], 0.8)
    n = 11
    for i in range(n):
        a = math.pi * (0.08 + 0.84 * i / (n - 1))
        base = Vector((math.cos(a) * 3.0, 0.6 + math.sin(a) * 1.4, -1.9 + 0.25 * math.sin(a)))
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.2, depth=0.16, location=tuple(base))
        bpy.context.active_object.data.materials.append(metal('svc', COL['gold'], 0.25))
        bead(tuple(base + Vector((0, 0, 0.1))), COL['goldLight'], 25, 0.05)
        top = core + (base - core).normalized() * 0.8
        mid = base.lerp(top, 0.5) + Vector((0, 0, 0.5))
        pts = [tuple(base * (1 - t) ** 2 + mid * 2 * t * (1 - t) + top * t * t) for t in (k / 30 for k in range(31))]
        tube(f'r{i}', pts, [0.3 + 0.7 * (k / 30) for k in range(31)], emissive(f'r{i}', COL['gold'], 6), bevel=0.012, res=4)
    bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, -1.97))
    bpy.context.active_object.data.materials.append(glossy('ground', '#041510', 0.55, 0.0))
    camera((0, -10.5, -0.6), (0, 0, 0.15), 48)

elif D == 'mesh':
    # B "The Mesh Map": the product's own signature. Services are places, calls are roads, each request is a
    # point of light on its way; one road has turned amber because it got slow.
    world(stars=False)
    gold_m = metal('gold', COL['gold'], 0.22)
    places = {'ingest': (-2.2, -0.6), 'kafka': (-0.6, 0.6), 'rabbit': (-0.4, -1.4), 'quest': (1.3, 0.9), 'ranks': (1.6, -0.9), 'push': (2.9, 0.1)}
    heights = {'ingest': 0.5, 'kafka': 0.8, 'rabbit': 0.6, 'quest': 0.7, 'ranks': 0.55, 'push': 0.45}
    for k, (x, y) in places.items():
        h = heights[k]
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.34, depth=h, location=(x, y, h / 2))
        o = bpy.context.active_object; bv = o.modifiers.new('b', 'BEVEL'); bv.width = 0.02; bv.segments = 3
        o.data.materials.append(glossy('stone', '#0B2A1F', 0.4, 0.5))
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.3, depth=0.03, location=(x, y, h + 0.015))
        bpy.context.active_object.data.materials.append(gold_m)
    roads = [('ingest', 'kafka', 'gold'), ('ingest', 'rabbit', 'gold'), ('kafka', 'quest', 'gold'), ('rabbit', 'ranks', 'amber'), ('quest', 'push', 'gold'), ('ranks', 'push', 'gold'), ('kafka', 'ranks', 'gold')]
    for i, (a, b, c) in enumerate(roads):
        A, B_ = Vector((*places[a], 0.03)), Vector((*places[b], 0.03))
        mid = A.lerp(B_, 0.5) + Vector((0, 0, 0.0))
        pts = [tuple(A.lerp(B_, t)) for t in (k / 10 for k in range(11))]
        tube(f'road{i}', pts, [1] * 11, emissive(f'road{i}', COL[c], 1.8 if c == 'gold' else 5), bevel=0.025, res=3)
        for t in ([0.3, 0.7] if c == 'gold' else [0.5]):
            bead(tuple(A.lerp(B_, t) + Vector((0, 0, 0.06))), COL['goldLight'] if c == 'gold' else COL['amber'], 40, 0.05)
    bpy.ops.mesh.primitive_plane_add(size=400)
    bpy.context.active_object.data.materials.append(glossy('ground', '#05170F', 0.7, 0.0))
    area('key', (-4, -5, 7), (0, 0, 0), 900, COL['goldLight'], 4)
    camera((0.2, -7.0, 4.4), (0.35, 0.0, 0.25), 44)

elif D == 'trace':
    # C "One Thread Through All": distributed tracing. One request is a single gold thread that passes through
    # every service on its way, each service a ring it threads, and the light at its tip is where it is now.
    world()
    gold_m = metal('gold', COL['gold'], 0.18)
    path = [Vector((-3.0 + 6.0 * t, 0, 0.9 * math.sin(math.pi * t * 1.3 - 0.4) - 0.2)) for t in (k / 80 for k in range(81))]
    rings = [0.1, 0.27, 0.44, 0.61, 0.78]
    for i, t in enumerate(rings):
        k = int(t * 80); p = path[k]; tan = (path[k + 1] - path[k - 1]).normalized()
        r = 0.55 - 0.05 * (i % 2)
        bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=0.075, major_segments=128, minor_segments=24, location=tuple(p))
        o = bpy.context.active_object; o.rotation_euler = tan.to_track_quat('Z', 'Y').to_euler(); o.data.materials.append(gold_m)
    reach = 0.9
    pts = [tuple(p) for p in path[:int(reach * 80) + 1]]
    tube('thread', pts, [0.4 + 0.6 * (k / (len(pts) - 1)) for k in range(len(pts))], emissive('thread', COL['goldLight'], 14), bevel=0.018, res=4)
    bead(pts[-1], COL['goldLight'], 80, 0.07)
    point('tip', pts[-1], 80, COL['goldLight'], 0.1)
    area('key', (-4, -6, 5), (0, 0, 0), 1200, COL['goldLight'], 3)
    area('rim', (3, 5, 3), (0, 0, 0), 800, COL['sky'], 3)
    camera((-0.35, -10.5, 1.6), (-0.3, 0, 0.1), 60)

elif D == 'kintsugi':
    # D "Broken on Purpose": chaos engineering as kintsugi. The sphere was cracked deliberately and every crack
    # is mended in gold: you only trust a system you have watched break and recover.
    world(stars=False)
    R = 1.5
    bpy.ops.mesh.primitive_uv_sphere_add(segments=192, ring_count=96, radius=R)
    bpy.ops.object.shade_smooth(); bpy.context.active_object.data.materials.append(glossy('glaze', '#0A2A1E', 0.45, 0.25))
    gold_m = metal('seam', COL['gold'], 0.2)
    def walk(start, steps, seed_dir):
        p = start.normalized(); d = seed_dir.normalized(); pts = []
        for s in range(steps):
            pts.append(tuple(p * R * 1.004))
            d = (d + Vector((rng.uniform(-.35, .35), rng.uniform(-.35, .35), rng.uniform(-.35, .35)))).normalized()
            d = (d - p * d.dot(p)).normalized()
            p = (p + d * 0.045).normalized()
        return pts
    starts = [(Vector((-0.2, -1, 0.5)), Vector((1, 0, -0.3)), 40), (Vector((0.3, -1, -0.2)), Vector((-0.4, 0, 1)), 34), (Vector((0.6, -1, 0.3)), Vector((0.3, 0, -1)), 30),
              (Vector((-0.6, -1, -0.4)), Vector((1, 0, 0.4)), 36), (Vector((-0.1, -1, -0.7)), Vector((0.2, 0, 1)), 28)]
    for i, (s, d, n) in enumerate(starts):
        pts = walk(s, n, d)
        tube(f'c{i}', pts, [0.35 + 0.65 * math.sin(math.pi * k / (n - 1)) for k in range(n)], gold_m, bevel=0.013, res=4)
        b = pts[n // 2]
        sub = walk(Vector(b), n // 2, Vector((rng.uniform(-1, 1), 0, rng.uniform(-1, 1))))
        tube(f'b{i}', sub, [1 - k / len(sub) for k in range(len(sub))], gold_m, bevel=0.01, res=4)
    area('key', (-4, -5, 6), (0, 0, 0), 1100, COL['goldLight'], 6)
    area('strip', (5, -2, 1), (0, 0, 0), 500, COL['ivory'], 0.8, 'RECTANGLE')
    area('rim', (2, 6, 3), (0, 0, 0), 700, COL['sky'], 4)
    camera((0, -9.5, 1.2), (0, 0, 0), 66)

bpy.ops.render.render(write_still=True)
print('rendered', OUT)
