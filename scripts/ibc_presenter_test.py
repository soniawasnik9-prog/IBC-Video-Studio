"""
IBC presenter-led quality-test scene.
Run:
  blender --background --python scripts/ibc_presenter_test.py -- --output output/test_landscape.mp4 --format landscape
  blender --background --python scripts/ibc_presenter_test.py -- --output output/test_vertical.mp4 --format vertical
Note: presenter is a stylized procedural 3D placeholder, not a rigged cinematic character.
Replace it with a properly licensed rigged character model for production.
"""
import bpy, math, os, sys
from mathutils import Vector

FPS = 12
DURATION = 15
END = FPS * DURATION

def arg_value(flag, default):
    args = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    return args[args.index(flag)+1] if flag in args else default

OUTPUT = os.path.abspath(arg_value("--output", "output/ibc_test.mp4"))
FORMAT = arg_value("--format", "landscape").lower()
VERTICAL = FORMAT == "vertical"
W, H = (540, 960) if VERTICAL else (960, 540)
os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x, scene.render.resolution_y = W, H
scene.render.resolution_percentage = 100
scene.render.fps = FPS
scene.frame_start, scene.frame_end = 1, END
scene.render.image_settings.file_format = "FFMPEG"
scene.render.ffmpeg.format = "MPEG4"
scene.render.ffmpeg.codec = "H264"
scene.render.ffmpeg.constant_rate_factor = "HIGH"
scene.render.ffmpeg.ffmpeg_preset = "GOOD"
scene.render.filepath = OUTPUT
scene.render.image_settings.color_mode = "RGB"
scene.render.film_transparent = False
scene.view_settings.view_transform = "Standard"
scene.world.color = (0.015, 0.025, 0.05)
try:
    scene.eevee.taa_render_samples = 8
except Exception:
    pass

def mat(name, color, metallic=0.0, rough=0.45, emission=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Metallic"].default_value = metallic
    p.inputs["Roughness"].default_value = rough
    if emission:
        es = p.inputs.get("Emission Color") or p.inputs.get("Emission")
        if es: es.default_value = (*color, 1)
        st = p.inputs.get("Emission Strength")
        if st: st.default_value = emission
    return m

navy = mat("IBC midnight navy", (0.012,0.035,0.085), rough=.6)
blue = mat("Ocean blue", (0.025,0.16,0.28), rough=.5)
cyan = mat("IBC cyan", (0.02,0.65,0.9), metallic=.25, emission=.25)
gold = mat("IBC gold", (0.95,0.52,0.12), metallic=.3)
white = mat("Warm white", (0.95,0.96,0.98))
skin = mat("Warm skin", (0.68,0.36,0.22), rough=.6)
hair = mat("Dark brown hair", (0.055,0.022,0.018), rough=.8)
suit = mat("Presenter navy blazer", (0.025,0.075,0.18), rough=.5)
shirt = mat("Presenter ivory shirt", (0.88,0.84,0.72), rough=.65)
container_red = mat("Container rust", (0.58,0.12,0.075), metallic=.15)
container_blue = mat("Container blue", (0.035,0.19,0.38), metallic=.2)
container_gold = mat("Container ochre", (0.8,0.38,0.07), metallic=.15)
dark = mat("Ship hull", (0.012,0.045,0.09), metallic=.3)

def cube(name, loc, scale, material, bevel=0.04):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    if bevel:
        mod=o.modifiers.new("Soft industrial edges","BEVEL"); mod.width=bevel; mod.segments=2
        o.modifiers.new("Weighted normals","WEIGHTED_NORMAL")
    return o

def sphere(name, loc, scale, material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale; o.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    return o

def cylinder_between(name, a, b, radius, material):
    mid=(Vector(a)+Vector(b))/2
    d=Vector(b)-Vector(a)
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=radius, depth=d.length, location=mid)
    o=bpy.context.object; o.name=name; o.data.materials.append(material)
    o.rotation_mode='QUATERNION'; o.rotation_quaternion=d.to_track_quat('Z','Y')
    return o

def text_obj(body, loc, size, material, align='CENTER'):
    cu=bpy.data.curves.new("Text_"+body[:16], "FONT"); cu.body=body; cu.size=size
    cu.align_x=align; cu.extrude=0.001
    ob=bpy.data.objects.new("Text_"+body[:16], cu); scene.collection.objects.link(ob)
    ob.location=loc; ob.data.materials.append(material)
    return ob

# Port set: sea, quay, ship hull, container stacks, cranes.
cube("Ocean", (0,0,-1.0),(30,30,.25),blue,0)
cube("Quay", (0,-1.3,-.72),(25,4,.45),mat("Concrete quay",(.19,.23,.27)),.03)
cube("Cargo ship hull", (0,1.1,-.45),(8.0,1.35,.8),dark,.15)
for x in [-2.8,-1.4,0,1.4,2.8]:
    cube("Ship container", (x,1.05,.15),(1.25,.95,.75), container_blue if x%2 else container_red,.035)
for x in [-7,-5.6,5.6,7]:
    for row in range(2):
        cube("Quayside container", (x,1.5+row*.78,.0),(1.25,.68,.7),
             [container_red,container_blue,container_gold][(int(abs(x)*2)+row)%3],.03)
# Crane structures
for x in [-6.6,6.6]:
    cylinder_between("Crane upright",(x,1.4,-.5),(x,1.4,4.1),.075,gold)
    cylinder_between("Crane boom",(x,1.4,4.05),(x+(-1.5 if x>0 else 1.5),1.4,4.05),.07,gold)
    cylinder_between("Crane cable",(x+(-1.2 if x>0 else 1.2),1.4,4.0),(x+(-1.2 if x>0 else 1.2),1.4,2.5),.025,white)

# Stylized female presenter made from 3D forms. Arms are animated as gesture placeholders.
cx = -2.15 if not VERTICAL else -0.15
cy = -0.1
# legs, torso, blazer, shirt, neck, head, hair
for x in [cx-.22,cx+.22]:
    cube("Presenter trouser leg",(x,cy,-.1),(.24,.28,1.0),suit,.07)
    cube("Presenter shoe",(x,cy-.07,-.62),(.34,.42,.16),dark,.05)
sphere("Presenter torso",(cx,cy,.95),(.52,.32,.72),suit)
sphere("Ivory blouse",(cx,cy-.27,1.02),(.25,.08,.53),shirt)
cylinder_between("Neck",(cx,cy,1.55),(cx,cy,1.78),.13,skin)
sphere("Presenter head",(cx,cy,2.03),(.38,.34,.48),skin)
sphere("Presenter hair cap",(cx,cy+.06,2.28),(.4,.35,.31),hair)
# hair sides
for x in [cx-.34,cx+.34]:
    sphere("Long hair",(x,cy+.03,1.96),(.13,.2,.52),hair)
# eyes and smile
for x in [cx-.14,cx+.14]:
    sphere("Eye",(x,cy-.315,2.08),(.045,.025,.06),dark)
    sphere("Eye shine",(x-.01,cy-.34,2.10),(.014,.012,.018),white)
# smile as slim curve
def curve_line(name, points, material, radius=.018):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.bevel_depth=radius; cu.bevel_resolution=2
    sp=cu.splines.new('POLY'); sp.points.add(len(points)-1)
    for p,co in zip(sp.points,points): p.co=(*co,1)
    ob=bpy.data.objects.new(name,cu); scene.collection.objects.link(ob); ob.data.materials.append(material)
    return ob
curve_line("Presenter smile",[(cx-.105,cy-.342,1.91),(cx,cy-.36,1.875),(cx+.105,cy-.342,1.91)],dark,.018)
# arms and hands, keyed gestures
arms=[]
for side in [-1,1]:
    shoulder=(cx+side*.42,cy,1.35)
    elbow=(cx+side*.68,cy-.03,1.05)
    hand=(cx+side*.84,cy-.08,.9)
    arm=cylinder_between("Presenter upper arm",shoulder,elbow,.105,suit)
    fore=cylinder_between("Presenter forearm",elbow,hand,.08,suit)
    palm=sphere("Presenter hand",hand,(.13,.09,.08),skin)
    arms.extend([arm,fore,palm])
# Subtle gesture: arms rotate around local Y in a few keyframes
for idx,obj in enumerate(arms):
    obj.rotation_mode='XYZ'
    base=obj.rotation_euler.copy()
    for frame,delta in [(1,0),(36,0.10 if idx%2 else -0.12),(72,-0.10 if idx%2 else 0.12),(END,0)]:
        obj.rotation_euler=base
        obj.rotation_euler[1]+=delta
        obj.keyframe_insert(data_path="rotation_euler",frame=frame)

# Backdrop branding panels and text. Composition shifts per aspect ratio.
if VERTICAL:
    text_x=0.0; title_y=5.5; subtitle_y=4.75
    title_size=.52; subtitle_size=.20
    cube("Brand title backing",(0,5.05,2.6),(5.8,1.6,.16),navy,.1)
    text_obj("INTERNATIONAL BUSINESS",(0,5.35,2.75),.34,white)
    text_obj("CONSULTANT",(0,4.85,2.75),.45,gold)
    text_obj("Your partner in global trade",(0,4.25,2.75),.23,white)
    # presenter moved central-ish in vertical frame; adjust camera later
    for y,label in [(2.8,"INDIAN SUPPLIERS"),(2.1,"EXPORT DOCUMENTS"),(1.4,"SHIPPING & CUSTOMS")]:
        cube("Service label background",(0,y,2.5),(5.4,.48,.12),navy,.06)
        text_obj(label,(0,y,2.59),.22,white)
    cube("CTA backing",(0,-2.4,2.5),(5.3,.85,.12),navy,.08)
    text_obj("MESSAGE IBC ON WHATSAPP",(0,-2.35,2.62),.21,cyan)
else:
    cube("Brand title backing",(2.35,2.5,2.5),(5.8,1.65,.16),navy,.1)
    text_obj("INTERNATIONAL BUSINESS",(2.35,2.85,2.65),.34,white)
    text_obj("CONSULTANT",(2.35,2.35,2.65),.48,gold)
    text_obj("Your partner in global trade",(2.35,1.8,2.65),.23,white)
    cube("Service label backing",(2.35,.65,2.5),(5.8,.8,.14),navy,.08)
    text_obj("SUPPLIERS  •  DOCUMENTS  •  SHIPPING",(2.35,.7,2.62),.22,white)
    cube("CTA backing",(2.35,-.3,2.5),(5.8,.6,.14),navy,.08)
    text_obj("MESSAGE IBC ON WHATSAPP",(2.35,-.28,2.62),.24,cyan)

# Camera and lighting
bpy.ops.object.camera_add(location=(0,-15,4.0))
cam=bpy.context.object; cam.data.type='ORTHO'
cam.data.ortho_scale=10.5 if VERTICAL else 12.5
target=Vector((0,0,1.2))
cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler()
scene.camera=cam
for loc,power,size in [((-5,-7,9),1200,7),((4,1,7),800,5)]:
    bpy.ops.object.light_add(type='AREA',location=loc)
    l=bpy.context.object; l.data.energy=power; l.data.shape='DISK'; l.data.size=size
    l.rotation_euler=(-l.location).to_track_quat('-Z','Y').to_euler()

# Add gentle camera drift for a living scene.
cam.location.x=-.25
cam.keyframe_insert(data_path="location",frame=1)
cam.location.x=.25
cam.keyframe_insert(data_path="location",frame=END)
for obj in scene.objects:
    if obj.animation_data and obj.animation_data.action:
        try:
            for fc in obj.animation_data.action.fcurves:
                for kp in fc.keyframe_points: kp.interpolation='BEZIER'
        except Exception: pass

scene.render.filepath=OUTPUT
scene.frame_set(1)
bpy.ops.render.render(animation=True)
print("IBC presenter test rendered:",OUTPUT,FORMAT)
