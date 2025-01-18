import bpy
import mathutils

# from .functions import TemporaryObjectMode

def assign_bone_shape(armature, bone_name, widget_name):
    custom_shape = bpy.data.objects.get(widget_name)

    if armature and custom_shape and armature.type == 'ARMATURE':
        # Switch to pose mode to assign the custom shape
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='POSE')
        
        # Get the pose bone
        pose_bone = armature.pose.bones.get(bone_name)
        
        if pose_bone:
            # Assign the custom shape
            pose_bone.custom_shape = custom_shape
            
            # Set the custom shape scale mode to ignore bone length
            pose_bone.custom_shape_scale_xyz = (1.0, 1.0, 1.0)  # Uniform scaling
            
            # Optionally, adjust custom shape transformation to ignore bone orientation
            pose_bone.use_custom_shape_bone_size = False  # Use this to prevent scaling by bone size
            
            print(f"Custom shape '{widget_name}' assigned to bone '{bone_name}'")
        else:
            print(f"Bone '{bone_name}' not found in armature '{armature.name}'.")
        
        # Return to edit mode
        bpy.ops.object.mode_set(mode='EDIT')
    else:
        print("Ensure that the armature and custom shape object exist and are correctly named.")


def assign_bone_shape_to_list(armature, widget_name, bone_names, custom_scale=None):
    custom_shape = bpy.data.objects.get(widget_name)

    if armature and custom_shape and armature.type == 'ARMATURE':
        # Switch to pose mode to assign the custom shape
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='POSE')
        
        # Get the pose bone
        for pose_bone in [bone for bone in armature.pose.bones if bone.name in bone_names]:
            pose_bone.custom_shape = custom_shape
            
            if custom_scale:
                pose_bone.custom_shape_scale_xyz = custom_scale
            
            # Prevent scaling by bone size
            pose_bone.use_custom_shape_bone_size = False  
            
            print(f"Custom shape '{widget_name}' assigned.")
        else:
            print(f"Widget '{widget_name}' not found.")
        
        # Return to edit mode
        bpy.ops.object.mode_set(mode='EDIT')
    else:
        print("Ensure that the armature and custom shape object exist and are correctly named.")


def create_bone(armature, bone_name, head, tail):
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='EDIT')
    
    bone = armature.data.edit_bones.new(bone_name)
    bone.head = head
    bone.tail = tail
    return bone


def assign_bone_to_collection(armature, bone_name, collection_name):
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')

    pose_bone = armature.pose.bones[bone_name]
    armature.data.collections[collection_name].assign(pose_bone)


def assign_bones_to_collection(armature, bone_names, collection_name):
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')
    
    for bone_name in bone_names:
        pose_bone = armature.pose.bones[bone_name]
        armature.data.collections[collection_name].assign(pose_bone)


def get_bone_tail(align_with_lattice, lattice_matrix_world, bone_head, bone_tail_offset):
    if align_with_lattice:
        return bone_head + lattice_matrix_world.to_3x3() @ bone_tail_offset
    else:
        return bone_head + bone_tail_offset


def align_bone_roll(align_with_lattice, lattice_matrix_world, bone):
        if align_with_lattice:
            bone.align_roll(lattice_matrix_world.to_quaternion() @ mathutils.Vector((0, 0, 1)))

# requires armature as active object and edit mode
def duplicate_bone(armature, bone_name, new_name, keep_parent=False):
    original_bone = armature.data.edit_bones[bone_name]
    new_bone = armature.data.edit_bones.new(new_name)
    new_bone.head = original_bone.head
    new_bone.tail = original_bone.tail
    new_bone.roll = original_bone.roll
    new_bone.parent = original_bone.parent if keep_parent else None
    new_bone.use_connect = original_bone.use_connect if keep_parent else False

    return new_bone

# requires armature as active object and pose mode
def assign_transform_constraint(armature, owner_bone, target_bone_name):
    owner_bone = armature.pose.bones[owner_bone]
    constraint = owner_bone.constraints.new('COPY_TRANSFORMS')
    constraint.target = armature
    constraint.subtarget = target_bone_name


def assign_copy_scale_constraint(armature, owner_bone, target_bone_name):
    owner_bone = armature.pose.bones[owner_bone]
    constraint = owner_bone.constraints.new('COPY_SCALE')
    constraint.target = armature
    constraint.subtarget = target_bone_name
