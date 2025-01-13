import bpy
import mathutils
from .widget_functions import create_cube_widget, create_sphere_widget, create_circle_widget, create_rectangle_widget


def find_layer_collection(coll_name, layer_coll_root=None):
    if layer_coll_root is None:
        layer_coll_root = bpy.context.view_layer.layer_collection
    
    if layer_coll_root.collection.name == coll_name:
        return layer_coll_root
    for coll_child in layer_coll_root.children:
        if found := find_layer_collection(coll_name, coll_child):
            return found
    return None


def set_active_collection(collection_name):
    view_layer = bpy.context.view_layer
    layer_collection = view_layer.layer_collection

    layer_coll = find_layer_collection(collection_name, layer_collection)

    if layer_coll is not None:
        view_layer.active_layer_collection = layer_coll
        print(f"Collection '{collection_name}' is now active.")
    else:
        print(f"Collection '{collection_name}' not found in view layer.")


def setup_widgets():
    print("setting up widgets...")

    # Check wether widget collection already exists, if so assume widgets are already set up
    if "LAT_WGT" in bpy.data.collections:
        print("Widgets already set up, skipping...")
        return

    initial_collection = bpy.context.view_layer.active_layer_collection.name
    
    # create widget collection
    wgt_collection_name = "LAT_WGT"
    wgt_collection = bpy.data.collections.new(wgt_collection_name)
    bpy.context.scene.collection.children.link(wgt_collection)
    set_active_collection(wgt_collection_name)
    
    create_sphere_widget(name="LAT_WGT_sphere", radius=0.2)
    create_circle_widget(name="LAT_WGT_circle")
    create_rectangle_widget(name="LAT_WGT_square")
    create_cube_widget(name="LAT_WGT_cube")
    find_layer_collection(wgt_collection_name).exclude = True
    
    set_active_collection(initial_collection)


def setup_bone_collections(armature, lattice_collection_name):
    collection_names = ["DEF", lattice_collection_name]

    for collection_name in collection_names:
        if not collection_name in [col.name for col in armature.data.collections]:
            bone_collection = armature.data.collections.new(collection_name)


def assign_bone_to_collection(armature, bone_name, collection_name):
    current_mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='POSE')

    pose_bone = armature.pose.bones[bone_name]
    armature.data.collections[collection_name].assign(pose_bone)

    bpy.ops.object.mode_set(mode=current_mode)


def get_bone_tail(align_with_lattice, lattice_matrix_world, bone_head, bone_tail_offset):
    if align_with_lattice:
        return bone_head + lattice_matrix_world @ bone_tail_offset
    else:
        return bone_head + bone_tail_offset


def align_bone_roll(align_with_lattice, lattice_matrix_world, bone):
        if align_with_lattice:
            bone.align_roll(lattice_matrix_world.to_quaternion() @ mathutils.Vector((0, 0, 1)))
