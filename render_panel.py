import bpy
from . import render_exporter

class ExportScene(bpy.types.Operator):
    bl_idname = 'scene.export'
    bl_label = 'Export Scene'
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        print("Starting calling pbrt_export")
        print("Output path:")
        print(bpy.data.scenes[0].exportpath)
        for frameNumber in range(bpy.data.scenes['Scene'].batch_frame_start, bpy.data.scenes['Scene'].batch_frame_end +1):
            bpy.data.scenes['Scene'].frame_set(frameNumber)
            print("Exporting frame: %s" % (frameNumber))
            render_exporter.export_pbrt(bpy.data.scenes['Scene'].exportpath, bpy.data.scenes['Scene'], '{0:05d}'.format(frameNumber))
        self.report({'INFO'}, "Export complete.")
        return {"FINISHED"}

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

        layout.label(text=" Render output filename")
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
        row.prop(scene, "batch_frame_start")
        row.prop(scene, "batch_frame_end")

        layout.label(text="Resolution:")
        row = layout.row()
        row.prop(scene, "resolution_x")
        row.prop(scene, "resolution_y")
       
        layout.label(text="Integrator settings:")
        row = layout.row()

        row.prop(scene,"integrators")
        row.prop(scene,"maxdepth")
        
        if scene.integrators == 'bdpt':
            row = layout.row()
            row.prop(scene,"bdpt_visualizestrategies")
            row.prop(scene,"bdpt_visualizeweights")
        
        if scene.integrators == 'mlt':
            row = layout.row()
            row.prop(scene,"mlt_bootstrapsamples")
            row = layout.row()
            row.prop(scene,"mlt_chains")
            row = layout.row()
            row.prop(scene,"mlt_mutationsperpixel")
            row = layout.row()
            row.prop(scene,"mlt_largestepprobability")
            row = layout.row()
            row.prop(scene,"mlt_sigma")


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
        layout.operator("scene.export", icon='MESH_CUBE', text="Export scene")
        #print ("updating panel")
        
        


        

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
    
    bpy.types.Scene.batch_frame_start = bpy.props.IntProperty(name = "Frame start", description = "Frame start", default = 1, min = 1, max = 9999999)
    bpy.types.Scene.batch_frame_end = bpy.props.IntProperty(name = "Frame end", description = "Frame end", default = 1, min = 1, max = 9999999)

    bpy.types.Scene.bdpt_visualizestrategies = bpy.props.BoolProperty(
    name="visualize strategies",
    description="visualize strategies",
    default = False)

    bpy.types.Scene.bdpt_visualizeweights = bpy.props.BoolProperty(
    name="visualize weights",
    description="visualize weights",
    default = False)

    bpy.types.Scene.mlt_bootstrapsamples = bpy.props.IntProperty(name = "bootstrap samples", description = "bootstrap samples", default = 100000, min = 1, max = 9999999)
    bpy.types.Scene.mlt_chains = bpy.props.IntProperty(name = "chains", description = "chains", default = 1000, min = 1, max = 9999999)
    bpy.types.Scene.mlt_mutationsperpixel = bpy.props.IntProperty(name = "mutations per pixel", description = "mutations per pixel", default = 100, min = 1, max = 9999999)
    bpy.types.Scene.mlt_largestepprobability = bpy.props.FloatProperty(name = "large step probability", description = "large step probability", default = 0.3, min = 0.001, max = 1)
    bpy.types.Scene.mlt_sigma = bpy.props.FloatProperty(name = "Sigma", description = "Sigma", default = 0.01, min = 0.001, max = 1)