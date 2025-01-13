from bpy.types import Context, Event, Object
from mathutils import Vector, Matrix
from bpy_extras import view3d_utils


class RaycastInfo:
    result: bool
    location: Vector
    normal: Vector
    index: int
    object: Object
    matrix: Matrix
    active_object: Object

    def update(self, context: Context, coord):
        scene = context.scene
        region = context.region
        rv3d = context.region_data
        viewlayer = context.view_layer

        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

        result, location, normal, index, object, matrix = scene.ray_cast(viewlayer, ray_origin, view_vector)
        self.result = result
        self.location = location
        self.normal = normal
        self.index = index
        self.object = object
        self.matrix = matrix

    @property
    def hit(self) -> bool:
        return self.result

    def get_poly(self, context: Context, target_object: Object = None):
        if not self.result:
            return None
        if target_object is not None and target_object.name != self.object.name:
            return None
        if target_object is None:
            if len(self.object.modifiers) > 0:
                depsgraph = context.evaluated_depsgraph_get()
                eval_obj: Object = self.object.evaluated_get(depsgraph)
                return eval_obj.data.polygons[self.index]
        object = target_object if target_object else self.object
        return object.data.polygons[self.index]

    def get_material(self, context: Context):
        poly = self.get_poly(context)
        if poly is None:
            return None
        return poly.material_index

