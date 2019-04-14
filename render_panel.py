import bpy

class PbrtRenderSettingsPanel(bpy.types.Panel):
    """Creates a Pbrt settings panel in the render context of the properties editor"""
    bl_label = "PBRT Render settings"
    bl_idname = "SCENE_PT_layout"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"


    # bpy.types.Scene.exportpath = bpy.props.StringProperty(
    #     name="",
    #     description="Export folder",
    #     default="",
    #     maxlen=1024,
    #     subtype='DIR_PATH')
    #     #bpy.props.StringProperty(name = "Export path", default="")

    # bpy.types.Scene.spp : bpy.props.IntProperty(name = "Halt at samples per pixel", description = "Set spp", default = 100, min = 1, max = 9999)
    # bpy.types.Scene.maxdepth : bpy.props.IntProperty(name = "Max depth", description = "Set max depth", default = 10, min = 1, max = 9999)

    # integrators = [("path", "path", "", 1), ("other", "other", "", 2)]
    # bpy.types.Scene.integrators : bpy.props.EnumProperty(name = "Name", items=integrators , default="path")

    # lightsamplestrategy = [("uniform", "uniform", "", 1), ("power", "power", "", 2), ("spatial", "spatial", "", 3)]
    # bpy.types.Scene.lightsamplestrategy : bpy.props.EnumProperty(name = "lightsamplestrategy", items=lightsamplestrategy , default="spatial")

    def draw(self, context):
        layout = self.layout

        scene = context.scene

        # Create a simple row.
        layout.label(text="Output path")
        row = layout.row()
        row.prop(scene, "exportpath")

        layout.label(text="Frame settings:")
        row = layout.row()
        row.prop(scene, "frame_start")
        row.prop(scene, "frame_end")
        
        #row.prop(scene, "SPP")
        #row.label(str(render.spp))
        
        layout.label(text="Integrator settings:")
        row = layout.row()
        #row.label(scene, "Integrator settings:", icon='CONSOLE')
        row.prop(scene,"integrators")
        row.prop(scene,"maxdepth")
        #dropdown menu here..

        layout.label(text="Sampler settings:")
        row = layout.row()
        row.prop(scene,"spp")

        layout.label(text="Light strategy:")
        row = layout.row()
        row.prop(scene,"lightsamplestrategy")
#        row.label(scene, "spp", icon='CONSOLE')
#        row.prop(scene, '["spp"]', slider=True,text="",index=1)
#        row.prop(scene, "spp")
        # Create an row where the buttons are aligned to each other.
#        layout.label(text=" Aligned Row:")

#        row = layout.row(align=True)
#        row.prop(scene, "frame_start")
#        row.prop(scene, "frame_end")

        # Create two columns, by using a split layout.
#        split = layout.split()

        # First column
#        col = split.column()
 #       col.label(text="Column One:")
  #      col.prop(scene, "frame_end")
   #     col.prop(scene, "frame_start")

        # Second column, aligned
#        col = split.column(align=True)
 #       col.label(text="Column Two:")
  #      col.prop(scene, "frame_start")
   #     col.prop(scene, "frame_end")

        # Big render button
        layout.label(text="Export:")
        row = layout.row()
        #row.scale_y = 3.0
        row.operator("render.render", text="Export scene")

        # Different sizes in a row
#        layout.label(text="Different button sizes:")
 #       row = layout.row(align=True)
  #      row.operator("render.render")

#        sub = row.row()
 #       sub.scale_x = 2.0
  #      sub.operator("render.render")

#        row.operator("render.render")

def register():
    #bpy.utils.register_class(PbrtRenderSettingsPanel)
    bpy.types.Scene.exportpath = bpy.props.StringProperty(
        name="",
        description="Export folder",
        default="",
        maxlen=1024,
        subtype='DIR_PATH')
         #bpy.props.StringProperty(name = "Export path", default="")

    bpy.types.Scene.spp = bpy.props.IntProperty(name = "Halt at samples per pixel", description = "Set spp", default = 100, min = 1, max = 9999)
    bpy.types.Scene.maxdepth = bpy.props.IntProperty(name = "Max depth", description = "Set max depth", default = 10, min = 1, max = 9999)

    integrators = [("path", "path", "", 1), ("other", "other", "", 2)]
    bpy.types.Scene.integrators = bpy.props.EnumProperty(name = "Name", items=integrators , default="path")

    lightsamplestrategy = [("uniform", "uniform", "", 1), ("power", "power", "", 2), ("spatial", "spatial", "", 3)]
    bpy.types.Scene.lightsamplestrategy = bpy.props.EnumProperty(name = "lightsamplestrategy", items=lightsamplestrategy , default="spatial")

#def unregister():
#    bpy.utils.unregister_class(PbrtRenderSettingsPanel)
