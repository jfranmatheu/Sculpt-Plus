from . import GPU_SHADER_INTERFACE_INFO, GPU_SHADER_CREATE_INFO, Type


MAX_PARAM = 12
MAX_INSTANCE = 6


GPU_SHADER_INTERFACE_INFO('WIDGET_IFACE') \
    .flat(Type.FLOAT, "discardFac") \
    .flat(Type.FLOAT, "lineWidth") \
    .flat(Type.VEC2, "outRectSize") \
    .flat(Type.VEC4, "borderColor") \
    .flat(Type.VEC4, "embossColor") \
    .flat(Type.VEC4, "outRoundCorners") \
    .no_perspective(Type.FLOAT, "butCo") \
    .no_perspective(Type.VEC2, "uvInterp")\
    .no_perspective(Type.VEC4, "innerColor")


GPU_SHADER_CREATE_INFO('WIDGET_SHARED', record=True) \
    .define("MAX_PARAM", str(MAX_PARAM)) \
    .push_constant(Type.MAT4, "ModelViewProjectionMatrix") \
    .push_constant(Type.VEC3, "checkerColorAndSize") \
    .vertex_out('WIDGET_IFACE') \
    .fragment_out(0, Type.VEC4, "fragColor") \
    .vertex_source("gpu_shader_2D_widget_base_vert.glsl") \
    .fragment_source("gpu_shader_2D_widget_base_frag.glsl")
    # .additional_info("gpu_srgb_to_framebuffer_space") # BLENDER ADDS IT INTERNALLY.


# .do_static_compilation(true)
# /* gl_InstanceID is supposed to be 0 if not drawing instances, but this seems
#  * to be violated in some drivers. For example, macOS 10.15.4 and Intel Iris
#  * causes T78307 when using gl_InstanceID outside of instance. */
GPU_SHADER_CREATE_INFO('WIDGET_BASE', based_on='WIDGET_SHARED') \
    .define("widgetID", "0") \
    .push_constant(Type.VEC4, "parameters", MAX_PARAM) \
    .compile()
    # .additional_info("gpu_shader_2D_widget_shared") # TODO: replicate this, copy from the other shader info or whatever..


# .do_static_compilation(true)
GPU_SHADER_CREATE_INFO('WIDGET_BASE_INST', based_on='WIDGET_SHARED') \
    .define("widgetID", "gl_InstanceID") \
    .push_constant(Type.VEC4, "parameters", (MAX_PARAM * MAX_INSTANCE)) \
    .compile()
    # .additional_info("gpu_shader_2D_widget_shared"); # TODO.


GPU_SHADER_INTERFACE_INFO('WIDGET_SHADOW_IFACE') \
    .smooth(Type.FLOAT, "shadowFalloff")


# .do_static_compilation(true) \
GPU_SHADER_CREATE_INFO('WIDGET_SHADOW') \
    .push_constant(Type.MAT4, "ModelViewProjectionMatrix") \
    .push_constant(Type.VEC4, "parameters", 4) \
    .push_constant(Type.FLOAT, "alpha") \
    .vertex_in(0, Type.UINT, "vflag") \
    .vertex_out('WIDGET_SHADOW_IFACE') \
    .fragment_out(0, Type.VEC4, "fragColor") \
    .vertex_source("gpu_shader_2D_widget_shadow_vert.glsl") \
    .fragment_source("gpu_shader_2D_widget_shadow_frag.glsl") \
    .compile()
