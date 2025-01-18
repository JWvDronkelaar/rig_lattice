# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
from bpy.types import Operator
from bpy.props import BoolProperty
import mathutils

from .constants import ArmatureCollection, Widget

from .functions import find_objects_that_reference_lattice, setup_bone_collections, setup_widgets
from .armature_functions import align_bone_roll, assign_bone_shape_to_list, assign_bones_to_collection, assign_transform_constraint, assign_copy_scale_constraint, create_bone, duplicate_bone, get_bone_tail


def main(context, align_with_lattice, root_to_bottom, bone_name, def_prefix, def_collection_name, lattice_collection_name):
    bone_length = 0.3
    lat_point_count = 0

    lattice = [obj for obj in bpy.context.selected_objects if obj.type == "LATTICE"][0]
    lattice_name = lattice.name
    
    armature = [obj for obj in bpy.context.selected_objects if obj.type == "ARMATURE"][0]
    armature_name = armature.name
    
    lat_point_count = len(lattice.data.points)
    lat_vertical_res = lattice.data.points_w
    lat_group_count = int(lat_point_count/lat_vertical_res)
    lattice_matrix_world = lattice.matrix_world

    # Set armature to active object and go to edit mode
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='EDIT')

    # Create root bone at lattice origin
    def_bone_name = f"{def_prefix}-{bone_name}_root"
    lattice_world_location = lattice_matrix_world.translation
    root_offset = lattice.scale.z / 2
    bone_head = lattice_world_location
    if root_to_bottom:
        bone_head = lattice_world_location + (lattice_matrix_world.to_3x3() @ mathutils.Vector((0, 0, -1))).normalized() * root_offset
    local_tail_offset = mathutils.Vector((0, bone_length * 3, 0))

    bone_tail = get_bone_tail(align_with_lattice, lattice_matrix_world, bone_head, local_tail_offset)

    root_bone = create_bone(armature, def_bone_name, bone_head, bone_tail)
    align_bone_roll(align_with_lattice, lattice_matrix_world, root_bone)
    root_bone.use_deform = False
    root_bone_name = root_bone.name

    # Create bones at each vertex of the lattice
    def_bones = []
    master_bones = []
    control_bones = []

    for group_index in range(0, lat_point_count, lat_group_count):
        print(f"Main loop iteration starting at group_index {group_index}")
        global_index = group_index
        group_center = mathutils.Vector((0, 0, 0))
        group_parent_bone = None

        # Calculate group center
        for local_index in range(group_index, min(group_index + lat_group_count, lat_point_count)):
            local_point = lattice.data.points[local_index]
            group_center += lattice_matrix_world @ local_point.co
        group_center = group_center / lat_group_count
        
        def_bone_name = f"parent_{bone_name}_{group_index}"
        bone_head = group_center
        bone_tail_offset = mathutils.Vector((0, bone_length * 2, 0))
        bone_tail = get_bone_tail(align_with_lattice, lattice_matrix_world, bone_head, bone_tail_offset)

        group_parent_bone = create_bone(armature, def_bone_name, bone_head, bone_tail)
        align_bone_roll(align_with_lattice, lattice_matrix_world, group_parent_bone)
        master_bones.append(group_parent_bone.name)
        group_parent_bone.use_deform = False
        group_parent_bone.parent = root_bone
        
        for local_index in range(group_index, min(group_index + lat_group_count, lat_point_count)):
            point = lattice.data.points[local_index]

            # Create deform bone
            def_bone_name = f"DEF-{bone_name}_{global_index}"
            bone_head = lattice.matrix_world @ point.co
            bone_tail_offset = mathutils.Vector((0, bone_length, 0))
            bone_tail = get_bone_tail(align_with_lattice, lattice_matrix_world, bone_head, bone_tail_offset)

            # Create a deform bone in edit mode
            def_bone = create_bone(armature, def_bone_name, bone_head, bone_tail)
            align_bone_roll(align_with_lattice, lattice_matrix_world, def_bone)
            def_bone.parent = root_bone
            def_bones.append(def_bone_name)

            # create control bone for deformation bone and setup constraints
            control_bone_name = f"{bone_name}_{global_index}"
            control_bone = duplicate_bone(armature, def_bone_name, control_bone_name, keep_parent=False)
            control_bone.parent = group_parent_bone
            control_bones.append(control_bone_name)

            global_index += 1

    # Assign constraints    
    bpy.ops.object.mode_set(mode='POSE')
    for index, def_bone in enumerate(def_bones):
        assign_transform_constraint(armature, def_bone, control_bones[index])
        assign_copy_scale_constraint(armature, control_bones[index], root_bone_name)
    
    # Create widget collection and widget shapes
    setup_widgets()

    # assign bone shapes
    square_custom_scale = mathutils.Vector((lattice.scale.x, lattice.scale.y, 1))
    assign_bone_shape_to_list(armature, Widget.SPHERE, control_bones)
    assign_bone_shape_to_list(armature, Widget.SQUARE, master_bones, custom_scale=square_custom_scale)
    assign_bone_shape_to_list(armature, Widget.CUBE, [root_bone_name,])

    # assign bones to collections
    setup_bone_collections(armature, [def_collection_name, lattice_collection_name,])
    assign_bones_to_collection(armature, def_bones, def_collection_name)
    assign_bones_to_collection(armature, control_bones + master_bones + [root_bone_name,], lattice_collection_name)

    armature.update_tag()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    depsgraph.update()

    bpy.context.view_layer.objects.active = lattice
    bpy.ops.object.mode_set(mode='OBJECT')

    # Add vertex groups and assign weights for each bone
    for vertex_index, def_bone_name in enumerate(def_bones):
        print(f"vertex_index: '{vertex_index}', bone_name: '{def_bone_name}'.")
        vertex_group = lattice.vertex_groups.new(name=def_bone_name)
        vertex_group.add([vertex_index], 1.0, 'REPLACE')

    # Add armature modifier to the lattice
    modifier = lattice.modifiers.new(name="Armature", type='ARMATURE')
    modifier.object = armature

    # Parent lattice and meshes referencing the lattice to the armature
    lattice.parent = armature
    referenced_mesh_objects = find_objects_that_reference_lattice(lattice_name)
    for mesh_object_name in referenced_mesh_objects:
        mesh_object = bpy.data.objects.get(mesh_object_name)
        mesh_object.parent = armature

    # Restore starting conditions so the redo panel works
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[armature_name].select_set(True)
    bpy.data.objects[lattice_name].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects[armature_name]
    bpy.ops.object.mode_set(mode='OBJECT')

    print("Bones have been created and weighted to the lattice vertices.")


class ARMATURE_OT_rig_lattice(Operator):
    """Tooltip"""
    bl_idname = "armature.rig_lattice"
    bl_label = "Rig lattice so it is controlled with bones"
    bl_options = {'REGISTER', 'UNDO'}

    align_with_lattice: bpy.props.BoolProperty(
        name="Align with lattice",
        description="Aligns the bones with the lattices orientation",
        default=False
    )
    root_to_bottom: bpy.props.BoolProperty(
        name="Root to bottom",
        description="Set Root bone to the bottom of the lattice",
        default=False
    )

    bone_name: bpy.props.StringProperty(
        name="Bone Name",
        description="The name of the bones to be created",
        default="lattice"
    )
    def_bones_prefix: bpy.props.StringProperty(
        name="Deform Bone Prefix",
        description="The prefix for the deform bones",
        default="DEF"
    )

    def_collection_name: bpy.props.StringProperty(
        name="Deform Collection Name",
        description="The name of the collection for deform bones",
        default="Deform Bones"
    )
    lattice_collection_name: bpy.props.StringProperty(
        name="Lattice Collection Name",
        description="The name of the collection for lattice bones",
        default="Lattice"
    )

    @classmethod
    def poll(cls, context):
        selected_objects_amount = len(bpy.context.selected_objects)
        if not selected_objects_amount >= 2:
            return False
        if not len([obj for obj in bpy.context.selected_objects if obj.type == 'ARMATURE']) == 1:
            return False
        if not len([obj for obj in bpy.context.selected_objects if obj.type == 'LATTICE']) == selected_objects_amount - 1:
            return False
        if active_object := bpy.context.active_object:
            if not (active_object.type == 'ARMATURE'):
                return False
        return True

    def execute(self, context):
        main(context, 
             self.align_with_lattice,
             self.root_to_bottom,
             self.bone_name,
             self.def_bones_prefix,
             self.def_collection_name,
             self.lattice_collection_name
             )
        return {'FINISHED'}

def rig_lattice_button(self, context):
    self.layout.operator(
        ARMATURE_OT_rig_lattice.bl_idname,
        text="Rig Lattice")

def register():
    bpy.utils.register_class(ARMATURE_OT_rig_lattice)
    bpy.types.VIEW3D_MT_object.append(rig_lattice_button)

def unregister():
    bpy.utils.unregister_class(ARMATURE_OT_rig_lattice)
    bpy.types.VIEW3D_MT_object.remove(rig_lattice_button)

if __name__ == "__main__":
    try:
        unregister()
    except:
        pass

    register()
