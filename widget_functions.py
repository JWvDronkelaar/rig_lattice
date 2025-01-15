import math, mathutils

import bpy

from .constants import Widget


# Function to scale coordinates around a given origin and along a specific axis
def scale_around_origin(coords, origin=mathutils.Vector((0,0,0)), axis="X", scale=1.0):
    # Create a scaling matrix
    scaling_matrix = mathutils.Matrix.Identity(4)
    if axis == 'X':
        scaling_matrix[0][0] = scale
    elif axis == 'Y':
        scaling_matrix[1][1] = scale
    elif axis == 'Z':
        scaling_matrix[2][2] = scale

    scaled_coords = []
    for coord in coords:
        # Translate the coordinate to the origin
        translated_coord = coord - origin
        # Scale the translated coordinate
        scaled_coord = scaling_matrix @ translated_coord
        # Translate back to the original position
        final_coord = scaled_coord + origin
        scaled_coords.append(final_coord)
    return scaled_coords


# Function to rotate coordinates around a given origin
def rotate_around_origin(coords, origin, axis, angle):
    rotation_matrix = mathutils.Matrix.Rotation(math.radians(angle), 4, axis)

    rotated_coords = []
    for coord in coords:
        # Translate the coordinate to the origin
        translated_coord = coord - origin
        # Rotate the translated coordinate
        rotated_coord = rotation_matrix @ translated_coord
        # Translate back to the original position
        final_coord = rotated_coord + origin
        rotated_coords.append(final_coord)
    return rotated_coords


def set_orientation(vertices, origin, orientation):
    if orientation == "X":
        vertices = rotate_around_origin(vertices, origin, mathutils.Vector((0, 1, 0)), 90)
    elif orientation == "Y":
        vertices = rotate_around_origin(vertices, origin, mathutils.Vector((1, 0, 0)), 90)
    else:
        pass # Z orientation is default

    return vertices


def create_mesh_circle(radius=1, resolution=16, orientation="Z"):
    vertices = []
    for i in range(resolution):
        angle = (2.0 * math.pi * i) / resolution
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        z = 0
        vertices.append(mathutils.Vector((x, y, z)))
    
    origin = mathutils.Vector((0, 0, 0))
    vertices = set_orientation(vertices, origin, orientation)

    edges = [(i, (i + 1) % resolution) for i in range(resolution)]
    faces = []  # No faces for an open circle

    return vertices, edges, faces


def create_cube_widget(name, size=1.0):
    vertices = [
        mathutils.Vector((size / 2, size / 2, size / 2)),
        mathutils.Vector((size / 2, -size / 2, size / 2)),
        mathutils.Vector((-size / 2, -size / 2, size / 2)),
        mathutils.Vector((-size / 2, size / 2, size / 2)),
        mathutils.Vector((size / 2, size / 2, -size / 2)),
        mathutils.Vector((size / 2, -size / 2, -size / 2)),
        mathutils.Vector((-size / 2, -size / 2, -size / 2)),
        mathutils.Vector((-size / 2, size / 2, -size / 2))
    ]

    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7)
    ]
    faces = []
    
    # Create a new mesh and object
    widget_name = Widget.CUBE
    mesh = bpy.data.meshes.new(widget_name)
    obj = bpy.data.objects.new(widget_name, mesh)

    # Link the object to the active collection
    bpy.context.collection.objects.link(obj)

    # Create mesh from data
    mesh.from_pydata(vertices, edges, faces)
    mesh.update()

    return obj


def create_rectangle_widget(name, size=mathutils.Vector((1.0, 1.0)), orientation="Z"):
    vertices = [
        mathutils.Vector((.5, .5, 0)),
        mathutils.Vector((.5, -.5, 0)),
        mathutils.Vector((-.5, -.5, 0)),
        mathutils.Vector((-.5, .5, 0))
    ]

    origin = mathutils.Vector((0, 0, 0))
    vertices = set_orientation(vertices, origin, orientation)
    vertices = scale_around_origin(vertices, origin, "X", size.x)
    vertices = scale_around_origin(vertices, origin, "Y", size.y)

    edges = [(0, 1), (1, 2), (2, 3), (3, 0)]
    faces = []

    # Create a new mesh and object
    widget_name = Widget.SQUARE
    mesh = bpy.data.meshes.new(widget_name)
    obj = bpy.data.objects.new(widget_name, mesh)

    # Link the object to the active collection
    bpy.context.collection.objects.link(obj)

    # Create mesh from data
    mesh.from_pydata(vertices, edges, faces)
    mesh.update()

    return obj


def create_circle_widget(name, radius=1.0, resolution=16, orientation='Z'):
    # Create a new mesh and object
    widget_name = Widget.CIRCLE
    mesh = bpy.data.meshes.new(widget_name)
    obj = bpy.data.objects.new(widget_name, mesh)

    # Link the object to the active collection
    bpy.context.collection.objects.link(obj)

    vertices, edges, faces = create_mesh_circle(radius, resolution, orientation)

    # Create mesh from data
    mesh.from_pydata(vertices, edges, faces)
    mesh.update()

    return obj


def create_sphere_widget(name, radius=1.0, resolution=16):
    # Create a new mesh and object
    widget_name = Widget.SPHERE
    mesh = bpy.data.meshes.new(widget_name)
    obj = bpy.data.objects.new(widget_name, mesh)

    # Link the object to the active collection
    bpy.context.collection.objects.link(obj)
    all_vertices = []
    all_edges = []

    for circle_index, orientation in enumerate(["X", "Y", "Z"]):
        offset = circle_index * resolution
        vertices, edges, faces = create_mesh_circle(radius, resolution, orientation)
        
        # Adjust edges to new vertex indices for each circle
        edges = [(v1 + offset, v2 + offset) for v1, v2 in edges]

        all_vertices.extend(vertices)
        all_edges.extend(edges)
        offset += resolution

    # Create mesh from data
    mesh.from_pydata(all_vertices, all_edges, [])
    mesh.update()

    return obj
