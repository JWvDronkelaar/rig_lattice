import bpy

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


def assign_bone_shape_to_list(armature, widget_name, bone_names):
    custom_shape = bpy.data.objects.get(widget_name)

    if armature and custom_shape and armature.type == 'ARMATURE':
        # Switch to pose mode to assign the custom shape
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='POSE')
        
        # Get the pose bone
        for pose_bone in [bone for bone in armature.pose.bones if bone.name in bone_names]:
            pose_bone.custom_shape = custom_shape
            
            # Uniform scaling (TODO: remove is redundant)
            pose_bone.custom_shape_scale_xyz = (1.0, 1.0, 1.0)
            
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
    bone = armature.data.edit_bones.new(bone_name)
    bone.head = head
    bone.tail = tail
    return bone
