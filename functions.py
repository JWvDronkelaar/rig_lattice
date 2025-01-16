
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


def find_objects_that_reference_lattice(lattice_name):
    # Get the lattice object
    target_lattice = bpy.data.objects.get(lattice_name)

    if target_lattice:
        # Generator to filter mesh objects with the desired lattice modifier
        meshes_with_lattice = (
            obj.name for obj in bpy.data.objects if obj.type == 'MESH' and any(
                mod.type == 'LATTICE' and mod.object == target_lattice for mod in obj.modifiers
            )
        )

        # Convert generator to a list and check if any meshes were found
        meshes_with_lattice_list = list(meshes_with_lattice)

        # Print the names of the mesh objects with the lattice modifier
        if meshes_with_lattice_list:
            print("Mesh objects with Lattice modifier referencing 'my_lattice':")
            for object_name in meshes_with_lattice_list:
                print(object_name)
        else:
            print("No mesh objects found with a Lattice modifier referencing 'my_lattice'.")
    else:
        print(f"Lattice object named '{lattice_name}' not found.")

    return meshes_with_lattice_list
