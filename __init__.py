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
import mathutils

from .functions import setup_widgets
from .armature_functions import assign_bone_shape_to_list, create_bone


def main(context):
    bone_length = 0.3
    bone_prefix = "eye_lat"
    lat_point_count = 0
    wgt_sphere = "LAT_WGT_sphere"
    wgt_circle = "LAT_WGT_circle"
    wgt_square = "LAT_WGT_square"
    wgt_cube = "LAT_WGT_cube"

    lattice = bpy.context.active_object
    lattice_name = lattice.name
    
    armature = [obj for obj in bpy.context.selected_objects if obj.type == "ARMATURE"][0]
    armature_name = armature.name
    
    lat_point_count = len(lattice.data.points)
    lat_vertical_res = lattice.data.points_w
    lat_group_count = int(lat_point_count/lat_vertical_res)

    # Set armature to active object and go to edit mode
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='EDIT')

    # Create root bone at lattice origin
    bone_name = f"{bone_prefix}_root"
    bone_head = lattice.location
    bone_tail = bone_head + mathutils.Vector((0, bone_length * 3, 0)) # align bone with world axis

    root_bone = create_bone(armature, bone_name, bone_head, bone_tail)
    root_bone.use_deform = False
    root_bone_name = root_bone.name

    # Create bones at each vertex of the lattice
    def_bones = []
    parent_bones = []
    for group_index in range(0, lat_point_count, lat_group_count):
        print(f"Main loop iteration starting at group_index {group_index}")
        global_index = group_index
        group_center = mathutils.Vector((0, 0, 0))
        group_parent_bone = None

        # Calculate group center
        for local_index in range(group_index, min(group_index + lat_group_count, lat_point_count)):
            local_point = lattice.data.points[local_index]
            group_center += lattice.matrix_world @ local_point.co
        group_center = group_center / lat_group_count
        
        bone_name = f"parent_{bone_prefix}_{group_index}"
        bone_head = group_center
        bone_tail = bone_head + mathutils.Vector((0, bone_length * 2, 0)) # align bone with world axis

        group_parent_bone = create_bone(armature, bone_name, bone_head, bone_tail)
        parent_bones.append(group_parent_bone.name)
        group_parent_bone.use_deform = False
        group_parent_bone.parent = root_bone
        
        for local_index in range(group_index, min(group_index + lat_group_count, lat_point_count)):
            point = lattice.data.points[local_index]

            # Create a new bone for each vertex
            bone_name = f"{bone_prefix}_{global_index}"
            bone_head = lattice.matrix_world @ point.co
            bone_tail = bone_head + mathutils.Vector((0, bone_length, 0)) # align bone with world axis

            # Create a bone in edit mode
            bone = create_bone(armature, bone_name, bone_head, bone_tail)
            bone.parent = group_parent_bone
            def_bones.append(bone_name)
            global_index += 1

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.view_layer.objects.active = lattice

    # Add vertex groups and assign weights for each bone
    for vertex_index, bone_name in enumerate(def_bones):
        print(f"vertex_index: '{vertex_index}', bone_name: '{bone_name}'.")
        vertex_group = lattice.vertex_groups.new(name=bone_name)
        vertex_group.add([vertex_index], 1.0, 'REPLACE')

    # Create widget collection and widget shapes
    setup_widgets()

    # assign bone shapes
    assign_bone_shape_to_list(armature, wgt_sphere, def_bones)
    assign_bone_shape_to_list(armature, wgt_square, parent_bones)
    assign_bone_shape_to_list(armature, wgt_cube, [root_bone_name,])

    # Add armature modifier to the lattice
    modifier = lattice.modifiers.new(name="Armature", type='ARMATURE')
    modifier.object = armature

    # Optionally, go back to Object mode after everything is set
    bpy.ops.object.mode_set(mode='OBJECT')

    print("Bones have been created and weighted to the lattice vertices.")


class ARMATURE_OT_rig_lattice(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "armature.rig_lattice"
    bl_label = "Rig lattice so it is controlled with bones"
    bl_options = {'REGISTER', 'UNDO'}

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
            if not (active_object.type == 'LATTICE'):
                return False
        return True

    def execute(self, context):
        main(context)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(ARMATURE_OT_rig_lattice)

def unregister():
    bpy.utils.unregister_class(ARMATURE_OT_rig_lattice)


if __name__ == "__main__":
    try:
        unregister()
    except:
        pass

    register()
