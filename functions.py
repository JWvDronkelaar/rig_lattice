
import bpy

from .constants import ArmatureCollection
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


def setup_bone_collections(armature, custom_collection_names=None):
    # Default bone collection names
    collection_names = [collection.value for collection in ArmatureCollection]
    if custom_collection_names:
        collection_names.extend(custom_collection_names)    

    for collection_name in collection_names:
        if not collection_name in [col.name for col in armature.data.collections]:
            bone_collection = armature.data.collections.new(collection_name)

        if collection_name == ArmatureCollection.DEFORM.value:
            bone_collection.is_visible = False


class TemporaryObjectMode:
    def __init__(self, object_name, mode):
        self.object_name = object_name
        self.mode = mode
        self.original_object = None
        self.original_mode = None
        self.do_nothing = False

    def __enter__(self):
        # Store the original active object and mode
        self.original_object = bpy.context.active_object
        self.original_mode = bpy.context.mode

        if self.original_mode.startswith('EDIT'):
            self.original_mode = 'EDIT'

        # Check if the current active object and mode already match the specified ones
        if self.original_object.name == self.object_name and self.original_mode == self.mode:
            self.do_nothing = True
            return

        # Switch to the specified object and mode if they don't match
        bpy.context.view_layer.objects.active = bpy.data.objects[self.object_name]
        bpy.ops.object.mode_set(mode=self.mode)

    def __exit__(self, exc_type, exc_value, traceback):
        if self.do_nothing:
            return  # Do nothing if already in the correct state

        bpy.ops.object.mode_set(mode='OBJECT')

        # Revert to the original active object
        bpy.context.view_layer.objects.active = self.original_object

        # Revert to the original mode
        bpy.ops.object.mode_set(mode=self.original_mode)

