"""
IBC 30-second vertical 3D introduction.
Run with:
  blender --background --python scripts/ibc_intro.py -- --output output/ibc_intro_silent.mp4
"""
import bpy
import math
import os
import sys
from mathutils import Euler

FPS = 24
DURATION = 30
START = 1
END = FPS * DURATION
WIDTH = 720
HEIGHT = 1280

def cli_output():
    argv = sys.argv
    if "--" in argv:
        args = argv[argv.index("--") + 1:]
        if "--output" in args:
            return os.path.abspath(args[args.index("--output") + 1])
    return os.path.abspath("output/ibc_intro_silent.mp4")

OUTPUT = cli_output()
os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

# Reset scene
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for datablocks in (bpy.data.materials, bpy.data.curves, bpy.data.meshes, bpy.data.cameras, bpy.data.lights):
    # Leave datablocks to Blender's normal orphan cleanup; objects are removed above.
    pass

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = WIDTH
scene.render.resolution_y = HEIGHT
scene.render.resolution_percentage = 100
scene.render.fps = FPS
scene.frame_start = START
scene.frame_end = END
scene.render.image_settings.file_format = "FFMPEG"
scene.render.ffmpeg.format = "MPEG4"
scene.render.ffmpeg.codec = "H264"
scene.render.ffmpeg.constant_rate_factor = "MEDIUM"
scene.render.ffmpeg.ffmpeg_preset = "GOOD"
scene.render.filepath = OUTPUT
scene.render.resolution_percentage = 100
scene.render.image_settings.color_mode = "RGB"
scene.world.color = (0.004, 0.012, 0.035)
scene.view_settings.view_transform = "Standard"

# Eevee settings compatible with common Blender versions.
try:
    scene.eevee.taa_render_samples = 16
except Exception:
    pass

def emission(name, color, strength=1.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1)
        emission_socket = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
        if emission_socket:
            emission_socket.default_value = (*color, 1)
        strength_socket = bsdf.inputs.get("Emission Strength")
        if strength_socket:
            strength_socket.default_value = strength
        bsdf.inputs["Metallic"].default_value = 0.15
        bsdf.inputs["Roughness"].default_value = 0.35
    return mat

NAVY = emission("IBC Navy", (0.008, 0.025, 0.09), 0.8)
BLUE = emission("IBC Electric Blue", (0.02, 0.28, 0.95), 1.8)
CYAN = emission("IBC Cyan", (0.02, 0.85, 1.0), 2.0)
GOLD = emission("IBC Gold", (1.0, 0.52, 0.08), 1.8)
WHITE = emission("IBC White", (0.92, 0.97, 1.0), 1.5)
MUTED = emission("IBC Muted", (0.28, 0.62, 0.8), 1.0)
GREEN = emission("IBC WhatsApp Green", (0.05, 0.8, 0.36), 1.7)

# Background plane
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -4))
bg = bpy.context.object
bg.name = "Deep navy background"
bg.data.materials.append(NAVY)

# Camera looking directly at XY artwork.
bpy.ops.object.camera_add(location=(0, 0, 24))
camera = bpy.context.object
camera.name = "Portrait Camera"
camera.data.type = "ORTHO"
camera.data.ortho_scale = 15.5
scene.camera = camera
camera.rotation_euler = (0, 0, 0)

# Lights for dimensionality
for loc, power, size in [((-5, 5, 10), 1100, 8), ((5, -2, 8), 700, 7)]:
    bpy.ops.object.light_add(type="AREA", location=loc)
    light = bpy.context.object
    light.data.energy = power
    light.data.shape = "DISK"
    light.data.size = size
    direction = - light.location
    light.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

# Procedural globe at center-left; visible behind animated typography.
bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=2.25, location=(0, 1.25, 0))
globe = bpy.context.object
globe.name = "3D Global Trade Globe"
globe.data.materials.append(BLUE)
bpy.ops.object.shade_smooth()
globe.rotation_euler = (math.radians(15), 0, 0)
globe.keyframe_insert(data_path="rotation_euler", frame=1)
globe.rotation_euler[2] = math.radians(360)
globe.keyframe_insert(data_path="rotation_euler", frame=END)
try:
    for fc in globe.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"
except Exception:
    pass

# Globe rings (procedural curves)
def add_ring(name, radius, rotation, bevel, material):
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 2
    curve.bevel_depth = bevel
    curve.bevel_resolution = 2
    spline = curve.splines.new("POLY")
    pts = 96
    spline.points.add(pts - 1)
    rot = Euler(rotation, "XYZ")
    for i, p in enumerate(spline.points):
        a = (2 * math.pi * i) / pts
        v = rot.to_matrix() @ __import__("mathutils").Vector((radius * math.cos(a), radius * math.sin(a), 0))
        p.co = (v.x, v.y, v.z, 1)
    spline.use_cyclic_u = True
    obj = bpy.data.objects.new(name, curve)
    scene.collection.objects.link(obj)
    obj.location = globe.location
    obj.data.materials.append(material)
    return obj

add_ring("Globe Equator", 2.3, (math.radians(70), 0, 0), 0.018, CYAN)
add_ring("Globe Meridian A", 2.3, (0, math.radians(65), 0), 0.014, MUTED)
add_ring("Globe Meridian B", 2.3, (0, math.radians(-65), math.radians(90)), 0.014, MUTED)

# Trade-route arcs in front of globe.
def add_arc(name, x1, y1, x2, y2, z=2.6, material=GOLD):
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = 0.025
    curve.bevel_resolution = 3
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(1)
    midx = (x1 + x2) / 2
    midy = max(y1, y2) + 0.65
    for bp, co in zip(spline.bezier_points, [(x1, y1, z), (x2, y2, z)]):
        bp.co = co
        bp.handle_left_type = "AUTO"
        bp.handle_right_type = "AUTO"
    # Use 3-point polyline with raised midpoint for reliable arc shape.
    curve.splines.clear()
    sp = curve.splines.new("POLY")
    sp.points.add(24)
    for i, p in enumerate(sp.points):
        t = i / 24
        x = (1-t)**2*x1 + 2*(1-t)*t*midx + t*t*x2
        y = (1-t)**2*y1 + 2*(1-t)*t*midy + t*t*y2
        p.co = (x, y, z, 1)
    obj = bpy.data.objects.new(name, curve)
    scene.collection.objects.link(obj)
    obj.data.materials.append(material)
    return obj

add_arc("Global Route One", -1.5, 0.8, 1.6, 0.8)
add_arc("Global Route Two", -1.1, 1.7, 1.15, 1.35, material=CYAN)

# Small glowing trade nodes
for i, (x, y) in enumerate([(-1.5, 0.8), (1.6, 0.8), (-1.1, 1.7), (1.15, 1.35)]):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=0.095, location=(x, y, 2.7))
    node = bpy.context.object
    node.name = f"Trade Node {i+1}"
    node.data.materials.append(GOLD if i % 2 == 0 else CYAN)
    bpy.ops.object.shade_smooth()

def animate_scale(obj, start_s, end_s, peak=1.0):
    # Hide outside active interval by scaling to zero.
    obj.scale = (0.001, 0.001, 0.001)
    obj.keyframe_insert(data_path="scale", frame=max(1, start_s - 2))
    obj.scale = (peak, peak, peak)
    obj.keyframe_insert(data_path="scale", frame=start_s + 6)
    obj.keyframe_insert(data_path="scale", frame=max(start_s + 7, end_s - 5))
    obj.scale = (0.001, 0.001, 0.001)
    obj.keyframe_insert(data_path="scale", frame=end_s)
    try:
        for fc in obj.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"
    except Exception:
        pass

def add_text(name, body, location, size, material, start_s, end_s, align="CENTER"):
    curve = bpy.data.curves.new(name, "FONT")
    curve.body = body
    curve.size = size
    curve.align_x = align
    curve.align_y = "CENTER"
    curve.extrude = 0.006
    curve.bevel_depth = 0.001
    obj = bpy.data.objects.new(name, curve)
    scene.collection.objects.link(obj)
    obj.location = location
    obj.data.materials.append(material)
    animate_scale(obj, start_s, end_s)
    return obj

def add_card(name, location, scale, material, start_s, end_s):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    animate_scale(obj, start_s, end_s)
    return obj

# Title and scene beats. All copy is designed for a phone screen.
add_text("Brand", "IBC", (0, 5.55, 3.2), 0.95, GOLD, 1, 140)
add_text("Tagline", "CONNECTING BUSINESSES TO GLOBAL TRADE", (0, 4.85, 3.2), 0.22, WHITE, 1, 140)

add_text("Hook One", "START YOUR", (0, 3.95, 3.2), 0.58, WHITE, 1, 75)
add_text("Hook Two", "IMPORT-EXPORT BUSINESS", (0, 3.25, 3.2), 0.43, CYAN, 1, 75)
add_text("Hook Three", "WHEREVER YOU ARE", (0, 2.65, 3.2), 0.32, GOLD, 1, 75)

# Service cards across middle timeline.
service_specs = [
    (75, 190, "01  COMPANY REGISTRATION", "Business setup guidance", GOLD),
    (190, 305, "02  INDIAN SUPPLIERS", "Source products in India", CYAN),
    (305, 420, "03  DOCUMENTATION", "Import-export paperwork", GOLD),
    (420, 535, "04  CUSTOMS & LOGISTICS", "India + destination country", CYAN),
]
for start, end, title, sub, mat in service_specs:
    add_card("Service panel " + title, (0, 0.2, 3.0), (6.0, 1.45, 0.12), NAVY, start, end)
    add_text("Service title " + title, title, (0, 0.42, 3.35), 0.29, mat, start, end)
    add_text("Service subtitle " + title, sub, (0, -0.12, 3.35), 0.28, WHITE, start, end)

# Export-from-India message.
add_text("Export line one", "WANT TO SOURCE PRODUCTS", (0, 1.15, 3.2), 0.38, WHITE, 535, 625)
add_text("Export line two", "FROM INDIA TO YOUR COUNTRY?", (0, 0.55, 3.2), 0.34, CYAN, 535, 625)
add_text("Export line three", "LET'S EXPLORE THE NEXT STEPS.", (0, -0.1, 3.2), 0.29, GOLD, 535, 625)

# WhatsApp call-to-action end card.
add_card("CTA panel", (0, 0.35, 3.0), (6.2, 3.0, 0.12), NAVY, 625, 721)
add_text("CTA Brand", "INTERNATIONAL BUSINESS CONSULTANT", (0, 1.35, 3.35), 0.26, GOLD, 625, 721)
add_text("CTA Main", "NEED IMPORT-EXPORT HELP?", (0, 0.65, 3.35), 0.40, WHITE, 625, 721)
add_text("CTA Connect", "CONNECT WITH IBC ON WHATSAPP", (0, -0.05, 3.35), 0.32, GREEN, 625, 721)
add_text("CTA Number", "YOUR_WHATSAPP_NUMBER", (0, -0.65, 3.35), 0.28, WHITE, 625, 721)
add_text("CTA Follow", "FOLLOW FOR GLOBAL TRADE TIPS", (0, -1.45, 3.35), 0.25, CYAN, 625, 721)

# Decorative floating particles around frame edges.
for i in range(32):
    x = ((i * 37) % 100) / 100 * 10 - 5
    y = ((i * 53) % 100) / 100 * 14 - 7
    bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=4, radius=0.025 + (i % 3)*0.012, location=(x, y, -0.5))
    dot = bpy.context.object
    dot.name = f"Background Particle {i+1}"
    dot.data.materials.append(CYAN if i % 2 else GOLD)

# Soft camera DOF is intentionally off for legible text.
scene.camera.data.lens = 50
scene.render.image_settings.color_mode = "RGB"
scene.render.film_transparent = False
scene.frame_set(1)

# Render animation
scene.render.filepath = OUTPUT
bpy.ops.render.render(animation=True)
print("IBC render complete:", OUTPUT)
