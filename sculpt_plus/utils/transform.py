import bpy
import mathutils


def get_local_axis_direction(obj: bpy.types.Object, axis: str):
    """ Gets object direction in given local axis.
        - `obj`: bpy.types.Object
        - `axis`: string value in {'X', '-X', 'Y', '-Y', 'Z', '-Z'}
    """
    # Ensure the input is valid
    valid_inputs = {'X', '-X', 'Y', '-Y', 'Z', '-Z'}
    if axis not in valid_inputs:
        raise ValueError(f"Invalid axis. Must be one of {valid_inputs}")

    # Get the object's local-to-world matrix
    local_to_world = obj.matrix_world

    # Determine the axis index and sign
    axis_index = 'XYZ'.index(axis[-1])
    sign = -1 if axis.startswith('-') else 1

    # Extract the axis direction from the matrix
    axis_vector = local_to_world.to_3x3().col[axis_index].normalized()

    # Apply the sign
    return axis_vector * sign
