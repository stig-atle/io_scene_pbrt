import bpy

class PbrtRenderSettingsPanel(bpy.types.Panel):
    """Creates a Pbrt settings panel in the render context of the properties editor"""
    bl_label = "PBRT Render settings"
    bl_idname = "SCENE_PT_layout"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout

        scene = context.scene

        # Create a simple row.
        layout.label(text="Output folder path")
        row = layout.row()
        
        row.prop(scene, "exportpath")

        layout.label(text="Output filename")
        row = layout.row()
        row.prop(scene,"outputfilename")

        layout.label(text="Environment Map")
        row = layout.row()
        row.prop(scene,"environmentmaptpath")

        layout.label(text="Environment map scale:")
        row = layout.row()
        row.prop(scene, "environmentmapscale")

        layout.label(text="Frame settings:")
        row = layout.row()
        row.prop(scene, "frame_start")
        row.prop(scene, "frame_end")

        layout.label(text="Resolution:")
        row = layout.row()
        row.prop(scene, "resolution_x")
        row.prop(scene, "resolution_y")
       
        layout.label(text="Integrator settings:")
        row = layout.row()

        row.prop(scene,"integrators")
        row.prop(scene,"maxdepth")

        layout.label(text="Sampler settings:")
        row = layout.row()
        row.prop(scene,"spp")

        layout.label(text="Depth of field:")
        row = layout.row()
        row.prop(scene,"dofLookAt")
        row = layout.row()
        row.prop(scene, "lensradius")

        layout.label(text="Light strategy:")
        row = layout.row()
        row.prop(scene,"lightsamplestrategy")

        layout.label(text="Export:")
        row = layout.row()
        row.operator("render.render", text="Export scene")

def register():
    #bpy.utils.register_class(PbrtRenderSettingsPanel)
    bpy.types.Scene.exportpath = bpy.props.StringProperty(
        name="",
        description="Export folder",
        default="",
        maxlen=1024,
        subtype='DIR_PATH')

    bpy.types.Scene.environmentmaptpath = bpy.props.StringProperty(
        name="",
        description="Environment map",
        default="",
        maxlen=1024,
        subtype='FILE_PATH')

    bpy.types.Scene.outputfilename = bpy.props.StringProperty(
        name="",
        description="Image output file name",
        default="output.exr",
        maxlen=1024,
        subtype='FILE_NAME')

    bpy.types.Scene.spp = bpy.props.IntProperty(name = "Halt at samples per pixel", description = "Set spp", default = 100, min = 1, max = 9999)
    bpy.types.Scene.maxdepth = bpy.props.IntProperty(name = "Max depth", description = "Set max depth", default = 10, min = 1, max = 9999)

    integrators = [("path", "path", "", 1), ("volpath", "volpath", "", 2),("bdpt", "bdpt", "", 3),("mlt", "mlt", "", 4)]
    bpy.types.Scene.integrators = bpy.props.EnumProperty(name = "Name", items=integrators , default="path")

    lightsamplestrategy = [("uniform", "uniform", "", 1), ("power", "power", "", 2), ("spatial", "spatial", "", 3)]
    bpy.types.Scene.lightsamplestrategy = bpy.props.EnumProperty(name = "lightsamplestrategy", items=lightsamplestrategy , default="spatial")

    bpy.types.Scene.environmentmapscale = bpy.props.FloatProperty(name = "Env. map scale", description = "Env. map scale", default = 1, min = 0.001, max = 9999)
    
    bpy.types.Scene.resolution_x = bpy.props.IntProperty(name = "X", description = "Resolution x", default = 1366, min = 1, max = 9999)
    bpy.types.Scene.resolution_y = bpy.props.IntProperty(name = "Y", description = "Resolution y", default = 768, min = 1, max = 9999)

    bpy.types.Scene.dofLookAt = bpy.props.PointerProperty(name="Target", type=bpy.types.Object)
    bpy.types.Scene.lensradius = bpy.props.FloatProperty(name = "Lens radius", description = "Lens radius", default = 0, min = 0.001, max = 9999)
    