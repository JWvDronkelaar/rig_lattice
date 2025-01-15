from enum import StrEnum


class ArmatureCollection(StrEnum):
    DEFORM = "Deform Bones"
    ORIGINAL = "Original Bones"
    LATTICE = "Lattice Bones"


class Widget(StrEnum):
    SPHERE = "LAT_WGT_sphere"
    CIRCLE = "LAT_WGT_circle"
    SQUARE = "LAT_WGT_square"
    CUBE = "LAT_WGT_cube"
