import bpy
import bmesh
import os
import math
from math import *
import mathutils
from mathutils import Vector
import shutil
import struct

# Simple wrapper on IO to handle indentation
class PBRTWriter: 
    def __init__(self, file):
        self.indent = ''
        self.file = open(file, 'w')

    def write(self, s):
        self.file.write(self.indent)
        self.file.write(s)

    def inc_indent(self):
        self.indent = self.indent + '\t'
    def dec_indent(self):
        self.indent = self.indent[:-1]
    
    def attr_begin(self):
        self.write("AttributeBegin\n")
        self.inc_indent()
    def attr_end(self):
        self.dec_indent()
        self.write("AttributeEnd\n")

    def close(self):
        self.file.close()

def write_ply(file, mesh, indices, normals, i):

    # Pack U,V
    uvs = []
    for uv_layer in mesh.uv_layers:
        for tri in mesh.loop_triangles:
            if tri.material_index == i:
                for loop_index in tri.loops:
                    uvs.append((
                        uv_layer.data[loop_index].uv[0],
                        uv_layer.data[loop_index].uv[1]
                    ))

    out = open(file, 'w')
    out.write("ply\n")
    out.write("format binary_little_endian 1.0\n")
    out.write(f"element vertex {len(indices)}\n")
    out.write("property float x\n")
    out.write("property float y\n")
    out.write("property float z\n")
    out.write("property float nx\n")
    out.write("property float ny\n")
    out.write("property float nz\n")
    # TODO: Check UV have same size than indices, normals
    if len(uvs) != 0:
        out.write("property float u\n")
        out.write("property float v\n")
    out.write(f"element face {len(indices) // 3}\n")
    # TODO: Check size and switch to proper precision
    out.write("property list uint int vertex_indices\n")
    out.write("end_header\n")

    # Now switch to binary writing
    out.close()
    out = open(file, "ab")
    # Position & Normals & UVs
    for (id,(id_vertex,n)) in enumerate(zip(indices, normals)):
        out.write(struct.pack('<f', mesh.vertices[id_vertex].co.x))
        out.write(struct.pack('<f', mesh.vertices[id_vertex].co.y))
        out.write(struct.pack('<f', mesh.vertices[id_vertex].co.z))
        
        out.write(struct.pack('<f', n[0]))
        out.write(struct.pack('<f', n[1]))
        out.write(struct.pack('<f', n[2]))

        if len(uvs) != 0:
            out.write(struct.pack('<f', uvs[id][0]))
            out.write(struct.pack('<f', uvs[id][1]))

    # Indices
    for i in range(0, len(indices), 3):
        out.write(struct.pack('<I', 3))
        out.write(struct.pack('<I', i))
        out.write(struct.pack('<I', i+1))
        out.write(struct.pack('<I', i+2))
    out.close()

#render engine custom begin
class PBRTRenderEngine(bpy.types.RenderEngine):
    bl_idname = 'Pbrt_v4_renderer'
    bl_label = 'Pbrt_v4_renderer'
    bl_use_preview = False
    bl_use_material = True
    bl_use_shading_nodes = False
    bl_use_shading_nodes_custom = False
    bl_use_texture_preview = True
    bl_use_texture = True
    
    def render(self, scene):
        self.report({'ERROR'}, "Use export function in PBRT panel.")
        
from bl_ui import properties_render
from bl_ui import properties_material
for member in dir(properties_render):
    subclass = getattr(properties_render, member)
    try:
        subclass.COMPAT_ENGINES.add('Pbrt_v4_renderer')
    except:
        pass

for member in dir(properties_material):
    subclass = getattr(properties_material, member)
    try:
        subclass.COMPAT_ENGINES.add('Pbrt_v4_renderer')
    except:
        pass

bpy.utils.register_class(PBRTRenderEngine)

#Camera code:
#https://blender.stackexchange.com/questions/16472/how-can-i-get-the-cameras-projection-matrix
def measure(first, second):
    locx = second[0] - first[0]
    locy = second[1] - first[1]
    locz = second[2] - first[2]

    distance = sqrt((locx)**2 + (locy)**2 + (locz)**2)
    return distance

def export_spot_lights(pbrt_file, scene):
    for ob in scene.objects:
            print('OB TYPE: ' + ob.type)
            if ob.type == "LIGHT" :
                la = ob.data
                print('Light type: ' + la.type)
                if la.type == "SPOT" :
                    print('\n\nexporting light: ' + la.name + ' - type: ' + la.type)
                    from_point=ob.matrix_world.col[3]
                    at_point=ob.matrix_world.col[2]
                    at_point=at_point * -1
                    at_point=at_point + from_point
                    pbrt_file.attr_begin()
                    pbrt_file.write(" LightSource \"spot\"\n \"point3 from\" [%s %s %s]\n \"point3 to\" [%s %s %s]\n" % (from_point.x, from_point.y, from_point.z,at_point.x, at_point.y, at_point.z))
                    
                    #TODO: Parse the values from the light \ color and so on. also add falloff etc.
                    pbrt_file.write("\"blackbody I\" [5500]\n")

                    pbrt_file.write("AttributeEnd\n\n")
    return ''

def export_point_lights(pbrt_file, scene):
    for object in scene.objects:
            if object.type == "LIGHT" :
                la = object.data
                print('Light type: ' + la.type)
                if la.type == "POINT" :
                    print('\n\nexporting lamp: ' + object.name + ' - type: ' + object.type)
                    print('\nExporting point light: ' + object.name)
                    pbrt_file.attr_begin()
                    from_point=object.matrix_world.col[3]
                    pbrt_file.write("Translate\t%s %s %s\n" % (from_point.x, from_point.y, from_point.z))
                    pbrt_file.write("LightSource \"point\"\n\"rgb I\" [%s %s %s]\n" % (bpy.data.objects[object.name].color[0], bpy.data.objects[object.name].color[1], bpy.data.objects[object.name].color[2]))
                    pbrt_file.attr_end()
                    pbrt_file.write("\n\n")

    return ''

def export_camera(pbrt_file):
    print("Fetching camera..")
    cam_ob = bpy.context.scene.camera
    if cam_ob is None:
        print("no scene camera,aborting")
        self.report({'ERROR'}, "No camera in scene, aborting")
    elif cam_ob.type == 'CAMERA':
        print("regular scene cam")
        print("render res: ", bpy.data.scenes['Scene'].render.resolution_x , " x ", bpy.data.scenes['Scene'].render.resolution_y)
        print("Exporting camera: ", cam_ob.name)

        pbrt_file.write("Scale -1 1 1 #avoid the 'flipped image' bug..\n")

        # https://blender.stackexchange.com/questions/13738/how-to-calculate-camera-direction-and-up-vector/13739#13739
        # https://www.randelshofer.ch/jpbrt/javadoc/org/jpbrt/io/package-summary.html#Cameras
        # https://blender.stackexchange.com/questions/16493/is-there-a-way-to-fit-the-viewport-to-the-current-field-of-view
        # https://blender.stackexchange.com/questions/16472/how-can-i-get-the-cameras-projection-matrix
        # https://github.com/Volodymyrk/pbrtMayaPy/blob/master/PBRT/ExportModules/Camera.py
        # https://github.com/mmp/pbrt-v2/blob/master/exporters/blender/pbrtBlend.py
        # https://blenderartists.org/forum/showthread.php?268039-Converting-camera-orientation-to-up-vector-and-line-of-sight-vector


        cameramatrix = cam_ob.matrix_world.copy()
        matrixTransposed = cameramatrix.transposed()
        up_point = matrixTransposed[1]

        from_point=cam_ob.matrix_world.col[3]
        at_point=cam_ob.matrix_world.col[2]
        at_point=at_point * -1
        at_point=at_point + from_point

        pbrt_file.write("LookAt\t%s %s %s\n\t%s %s %s\n\t%s %s %s\n\n" % \
                        (from_point.x, from_point.y, from_point.z, \
                         at_point.x, at_point.y, at_point.z, \
                         up_point[0],up_point[1],up_point[2]))

        #https://blender.stackexchange.com/questions/14745/how-do-i-change-the-focal-length-of-a-camera-with-python
        # compute fov according to ratio and angle (Blender uses max angle whereas pbrt uses min angle)
        ratio = bpy.data.scenes['Scene'].render.resolution_y / bpy.data.scenes['Scene'].render.resolution_x
        angle_rad = bpy.data.cameras[0].angle 
        fov = 2.0 * math.atan ( ratio * math.tan( angle_rad / 2.0 )) * 180.0 / math.pi 
        pbrt_file.write('Camera "perspective"\n')
        pbrt_file.write('"float fov" [%s]\n' % (fov))

        if bpy.data.scenes['Scene'].dofLookAt is not None:
            pbrt_file.write('"float lensradius" [%s]\n' % (bpy.data.scenes['Scene'].lensradius))
            pbrt_file.write('"float focaldistance" [%s]\n\n' % (measure(cam_ob.matrix_world.translation, bpy.data.scenes['Scene'].dofLookAt.matrix_world.translation)))
    return ''

def export_film(pbrt_file, frameNumber):
    outputFileName = os.path.splitext(os.path.basename(bpy.data.scenes[0].outputfilename))
    print("Outputfilename:")
    print(outputFileName[0])
    print(outputFileName[1])

    finalFileName = outputFileName[0] + frameNumber  + outputFileName[1]
    pbrt_file.write(r'Film "rgb" "integer xresolution" [%s] "integer yresolution" [%s] "string filename" "%s"' % (bpy.data.scenes[0].resolution_x, bpy.data.scenes[0].resolution_y, finalFileName))
    pbrt_file.write("\n")

    pbrt_file.write(r'PixelFilter "%s" "float xradius" [%s] "float yradius" [%s] ' % (bpy.data.scenes[0].filterType, bpy.data.scenes[0].filter_x_width, bpy.data.scenes[0].filter_y_width))
    if bpy.data.scenes[0].filterType == 'sinc':
        pbrt_file.write(r'"float tau" [%s]' % (bpy.data.scenes[0].filter_tau))
    if bpy.data.scenes[0].filterType == 'mitchell':
        pbrt_file.write(r'"float B" [%s]' % (bpy.data.scenes[0].filter_b))
        pbrt_file.write(r'"float C" [%s]' % (bpy.data.scenes[0].filter_c))
    if bpy.data.scenes[0].filterType == 'gaussian':
        pbrt_file.write(r'"float alpha" [%s]' % (bpy.data.scenes[0].filter_alpha))
    pbrt_file.write("\n")

    pbrt_file.write(r'Accelerator "%s" ' % (bpy.data.scenes[0].accelerator))
    pbrt_file.write("\n")
    if  bpy.data.scenes[0].accelerator == 'kdtree':
        pbrt_file.write('"integer intersectcost" [%s]\n' % (bpy.data.scenes['Scene'].kdtreeaccel_intersectcost))
        pbrt_file.write('"integer traversalcost" [%s]\n' % (bpy.data.scenes['Scene'].kdtreeaccel_traversalcost))
        pbrt_file.write('"float emptybonus" [%s]\n' % (bpy.data.scenes['Scene'].kdtreeaccel_emptybonus))
        pbrt_file.write('"integer maxprims" [%s]\n' % (bpy.data.scenes['Scene'].kdtreeaccel_maxprims))
        pbrt_file.write('"integer maxdepth" [%s]\n' % (bpy.data.scenes['Scene'].kdtreeaccel_maxdepth))
    if bpy.data.scenes[0].accelerator == 'bvh':
        pbrt_file.write(r'"string splitmethod" "%s"' % (bpy.data.scenes[0].splitmethod))
        pbrt_file.write("\n")
        pbrt_file.write('"integer maxnodeprims" [%s]\n' % (bpy.data.scenes['Scene'].maxnodeprims))
    return ''

def export_sampler(pbrt_file):
    pbrt_file.write(r'Sampler "%s"'% (bpy.data.scenes[0].sampler))
    pbrt_file.write("\n")

    if bpy.data.scenes[0].sampler == 'halton':
        pbrt_file.write(r'"integer pixelsamples" [%s]'% (bpy.data.scenes[0].spp))
        pbrt_file.write("\n")
        #if bpy.data.scenes[0].samplepixelcenter:
            #pbrt_file.write(r'"bool samplepixelcenter" "true"')
        #else:
        #    pbrt_file.write(r'"bool samplepixelcenter" "false"')
        pbrt_file.write("\n")

    if bpy.data.scenes[0].sampler == 'maxmin':
        pbrt_file.write(r'"integer pixelsamples" [%s]'% (bpy.data.scenes[0].spp))
        pbrt_file.write("\n")
        pbrt_file.write(r'"integer dimensions" [%s]'% (bpy.data.scenes[0].dimension))
        pbrt_file.write("\n")

    if bpy.data.scenes[0].sampler == 'random':
        pbrt_file.write(r'"integer pixelsamples" [%s]'% (bpy.data.scenes[0].spp))
        pbrt_file.write("\n")

    if bpy.data.scenes[0].sampler == 'sobol':
        pbrt_file.write(r'"integer pixelsamples" [%s]'% (bpy.data.scenes[0].spp))
        pbrt_file.write("\n")

    if bpy.data.scenes[0].sampler == 'lowdiscrepancy':
        pbrt_file.write(r'"integer pixelsamples" [%s]'% (bpy.data.scenes[0].spp))
        pbrt_file.write("\n")
        pbrt_file.write(r'"integer dimensions" [%s]'% (bpy.data.scenes[0].dimension))
        pbrt_file.write("\n")

    if bpy.data.scenes[0].sampler == 'stratified':
        pbrt_file.write(r'"integer xsamples" [%s]'% (bpy.data.scenes[0].xsamples))
        pbrt_file.write("\n")
        pbrt_file.write(r'"integer ysamples" [%s]'% (bpy.data.scenes[0].ysamples))
        pbrt_file.write("\n")
        pbrt_file.write(r'"integer dimensions" [%s]'% (bpy.data.scenes[0].dimension))
        pbrt_file.write("\n")
        if bpy.data.scenes[0].jitter:
            pbrt_file.write(r'"bool jitter" "true"')
        else:
            pbrt_file.write(r'"bool jitter" "false"')
        pbrt_file.write("\n")

    return ''

def export_integrator(pbrt_file, scene):
    pbrt_file.write(r'Integrator "%s"' % (bpy.data.scenes[0].integrators))
    pbrt_file.write("\n")
    pbrt_file.write(r'"integer maxdepth" [%s]' % (bpy.data.scenes[0].maxdepth))
    pbrt_file.write("\n")

    if scene.integrators == 'path':
        #pbrt_file.write(r'"float rrthreshold" [%s]' % (bpy.data.scenes[0].rrthreshold))
        pbrt_file.write("\n")
        if scene.regularize:
            pbrt_file.write(r'"bool regularize" "true"')
            pbrt_file.write("\n")
    
    if scene.integrators == 'bdpt':
        if scene.bdpt_visualizestrategies :
            pbrt_file.write(r'"bool visualizestrategies" "true"')
            pbrt_file.write("\n")
        if scene.bdpt_visualizeweights :
            pbrt_file.write(r'"bool visualizeweights" "true"')
            pbrt_file.write("\n")

    if scene.integrators == 'mlt':
        pbrt_file.write(r'"integer bootstrapsamples" [%s]' % (bpy.data.scenes[0].mlt_bootstrapsamples))
        pbrt_file.write("\n")
        pbrt_file.write(r'"integer chains" [%s]' % (bpy.data.scenes[0].mlt_chains))
        pbrt_file.write("\n")
        pbrt_file.write(r'"integer mutationsperpixel" [%s]' % (bpy.data.scenes[0].mlt_mutationsperpixel))
        pbrt_file.write("\n")
        pbrt_file.write(r'"float largestepprobability" [%s]' % (bpy.data.scenes[0].mlt_largestepprobability))
        pbrt_file.write("\n")
        pbrt_file.write(r'"float sigma" [%s]' % (bpy.data.scenes[0].mlt_sigma))
        pbrt_file.write("\n")

    if scene.integrators == 'sppm':
        pbrt_file.write(r'"integer numiterations" [%s]' % (bpy.data.scenes[0].sppm_numiterations))
        pbrt_file.write("\n")
        pbrt_file.write(r'"integer photonsperiteration" [%s]' % (bpy.data.scenes[0].sppm_photonsperiteration))
        pbrt_file.write("\n")
        pbrt_file.write(r'"integer imagewritefrequency" [%s]' % (bpy.data.scenes[0].sppm_imagewritefrequency))
        pbrt_file.write("\n")
        pbrt_file.write(r'"float radius" [%s]' % (bpy.data.scenes[0].sppm_radius))
        pbrt_file.write("\n")
    
        

    return ''

def export_LightSampleDistribution(pbrt_file, scene):
    pbrt_file.write(r'"string lightsamplestrategy" "%s"' % (bpy.data.scenes[0].lightsamplestrategy))
    pbrt_file.write("\n")
    return ''

def world_begin(pbrt_file):
    pbrt_file.write("WorldBegin")
    pbrt_file.write("\n\n")
    return ''

def export_EnviromentMap(pbrt_file):
    if bpy.data.scenes[0].environmentmaptpath != "":
        environmentMapFileName= getTextureInSlotName(bpy.data.scenes[0].environmentmaptpath)
        
        #Copy the file by getting the full filepath:
        srcfile = bpy.path.abspath(bpy.data.scenes[0].environmentmaptpath)
        dstdir = bpy.path.abspath(bpy.data.scenes[0].exportpath + 'textures/' + environmentMapFileName)
        print("os.path.dirname...")
        print(os.path.dirname(srcfile))
        print("\n")
        print("srcfile: ")
        print(srcfile)
        print("\n")
        print("dstdir: ")
        print(dstdir)
        print("\n")
        print("File name is :")
        print(environmentMapFileName)
        print("Copying environment texture from source directory to destination directory.")
        shutil.copyfile(srcfile, dstdir)

        environmentmapscaleValue = bpy.data.scenes[0].environmentmapscale
        pbrt_file.attr_begin()
        pbrt_file.write(r'LightSource "infinite" "string mapname" "%s" "color scale" [%s %s %s]' % ("textures/" + environmentMapFileName,environmentmapscaleValue,environmentmapscaleValue,environmentmapscaleValue))
        pbrt_file.write("\n")
        pbrt_file.attr_end()
        pbrt_file.write("\n\n")

def export_environmentLight(pbrt_file):
    print("image texture type: ")
    pbrt_file.write("\n")
    environmenttype = bpy.data.worlds['World'].node_tree.nodes['Background'].inputs['Color'].links[0].from_node.type
    environmentMapPath = ""
    environmentMapFileName = ""
    print(environmenttype)
    pbrt_file.attr_begin()

    if environmenttype == "TEX_IMAGE":
        print(environmenttype)
        environmentMapPath = bpy.data.worlds['World'].node_tree.nodes['Background'].inputs['Color'].links[0].from_node.image.filepath
        environmentMapFileName= getTextureInSlotName(environmentMapPath)
        print(environmentMapPath)
        print(environmentMapFileName)
        print("background strength: value:")
        backgroundStrength = bpy.data.worlds['World'].node_tree.nodes['Background'].inputs[1].default_value
        print(backgroundStrength)
        pbrt_file.write(r'LightSource "infinite" "string mapname" "%s" "spectrum scale" [%s %s %s]' % ("textures/" + environmentMapFileName,backgroundStrength,backgroundStrength,backgroundStrength))


    pbrt_file.write("\n")
    #pbrt_file.write(r'Rotate 10 0 0 1 Rotate -110 1 0 0 LightSource "infinite" "string mapname" "textures/20060807_wells6_hd.exr" "spectrum scale" [2.5 2.5 2.5]')
    if environmenttype == "RGB":
        print(bpy.data.worlds['World'].node_tree.nodes['Background'].inputs['Color'].default_value[0])
        pbrt_file.write(r'LightSource "infinite" "spectrum L" [%s %s %s] "spectrum scale" [%s %s %s]' %(bpy.data .worlds['World'].node_tree.nodes['Background'].inputs['Color'].default_value[0],bpy.data .worlds['World'].node_tree.nodes['Background'].inputs['Color'].default_value[1],bpy.data .worlds['World'].node_tree.nodes['Background'].inputs['Color'].default_value[2],backgroundStrength,backgroundStrength,backgroundStrength))

    pbrt_file.write("\n")
    pbrt_file.attr_end()
    pbrt_file.write("\n\n")
    return ''

def export_defaultMaterial(pbrt_file):
    pbrt_file.write(r'Material "plastic"')
    pbrt_file.write("\n")
    pbrt_file.write(r'"spectrum Kd" [.1 .1 .1]')
    pbrt_file.write("\n")
    pbrt_file.write(r'"spectrum Ks" [.7 .7 .7] "float roughness" .1')
    pbrt_file.write("\n\n")
    return ''

def exportTextureInSlotNew(pbrt_file,textureSlotParam,isFloatTexture):
    pbrt_file.write("\n")
    srcfile = bpy.path.abspath(textureSlotParam)
    texturefilename = getTextureInSlotName(srcfile)
    if isFloatTexture :
        pbrt_file.write(r'Texture "%s" "float" "imagemap" "string filename" ["%s"]' % (texturefilename, ("textures/" + texturefilename)))
    else:
        pbrt_file.write(r'Texture "%s" "spectrum" "imagemap" "string filename" ["%s"]' % (texturefilename, ("textures/" + texturefilename)))

    pbrt_file.write("\n")
    dstdir = bpy.path.abspath(bpy.data.scenes[0].exportpath + 'textures/' + texturefilename)
    print("os.path.dirname...")
    print(os.path.dirname(srcfile))
    print("\n")
    print("srcfile: ")
    print(srcfile)
    print("\n")
    print("dstdir: ")
    print(dstdir)
    print("\n")
    print("File name is :")
    print(texturefilename)
    print("Copying texture from source directory to destination directory.")
    shutil.copyfile(srcfile, dstdir)
    return ''

def export_texture_from_input (pbrt_file, inputSlot, mat, isFloatTexture):
    textureName = ""
    links = inputSlot.links
    print('Number of links: ')
    print(len(links))
    for x in inputSlot.links:
        textureName = x.from_node.image.name
        exportTextureInSlotNew(pbrt_file,x.from_node.image.filepath,isFloatTexture)
    return textureName

def export_Pbrt_V4_Diffuse (pbrt_file, mat):
    print('Currently exporting Pbrt Diffuse material')
    print (mat.name)

    reflectanceTextureName = export_texture_from_input(pbrt_file,mat.inputs[0],mat, False)

    pbrt_file.write(r'Material "diffuse"')
    pbrt_file.write("\n")
    #pbrt_file.write(r'"float sigma" [%s]' %(mat.inputs[1].default_value))
    pbrt_file.write("\n")
    if reflectanceTextureName != "" :
        pbrt_file.write(r'"texture %s" "%s"' % ("reflectance", reflectanceTextureName))
    else:
        pbrt_file.write(r'"rgb reflectance" [ %s %s %s]' %(mat.inputs[0].default_value[0],mat.inputs[0].default_value[1],mat.inputs[0].default_value[2]))
    pbrt_file.write("\n")

    return ''

def export_Pbrt_V4_Dielectric(pbrt_file, mat):
    etaTextureName = export_texture_from_input(pbrt_file,mat.inputs[0],mat, True)
    vRoughnessTextureName = export_texture_from_input(pbrt_file,mat.inputs[1],mat, True)
    uRoughnessTextureName = export_texture_from_input(pbrt_file,mat.inputs[2],mat, True)
    
    pbrt_file.write(r'Material "dielectric"')
    pbrt_file.write("\n")

    if etaTextureName != "":
        pbrt_file.write(r'"texture %s" "%s"' % ("eta", etaTextureName))
    else:
        pbrt_file.write(r'"float eta" [%s]' %(mat.inputs[0].default_value))
        pbrt_file.write("\n")

    if vRoughnessTextureName != "" :
        pbrt_file.write(r'"texture %s" "%s"' % ("vroughness", vRoughnessTextureName))
    else:
        pbrt_file.write(r'"float vroughness" [%s]' %(mat.inputs[1].default_value))
    pbrt_file.write("\n")

    if uRoughnessTextureName != "" :
        pbrt_file.write(r'"texture %s" "%s"' % ("vroughness", uRoughnessTextureName))
    else:
        pbrt_file.write(r'"float uroughness" [%s]' %(mat.inputs[2].default_value))
    pbrt_file.write("\n")

    if (mat.remaproughness):
        pbrt_file.write(r'"bool remaproughness" [true]')
    else:
        pbrt_file.write(r'"bool remaproughness" [false]')
    pbrt_file.write("\n")

    return ''

def export_Pbrt_V4_Thin_Dielectric(pbrt_file, mat):
    print('Currently exporting Pbrt thin dielectric material')

    #vRoughnessTextureName = export_texture_from_input(pbrt_file,mat.inputs[4],mat, False)
    #uRoughnessTextureName = export_texture_from_input(pbrt_file,mat.inputs[5],mat, False)
    
    # TODO: There seems to be a bug here if textur is not defined twice,
    # one as 'float' and one as 'spectrum', pbrt cannot find the textuer
    # if only one is specified, investigate this.
    displacementTextureName = export_texture_from_input(pbrt_file,mat.inputs[1],mat, False)
    etaTextureName = export_texture_from_input(pbrt_file,mat.inputs[0],mat, True)

    pbrt_file.write(r'Material "thindielectric"')
    pbrt_file.write("\n")
    
    
    #if (etaTextureName != ""):
    #    pbrt_file.write(r'"texture %s" "%s"' % ("eta", etaTextureName))
    #else:
    pbrt_file.write(r'"float eta" [%s]' %(mat.inputs[1].default_value))
    pbrt_file.write("\n")

    #TODO: Look into the following parameters, PBRT says they are unused.
    #pbrt_file.write(r'"float etaF" [%s]' %(mat.inputs[2].default_value))
    #pbrt_file.write("\n")
    #pbrt_file.write(r'"float etaS" [%s]' %(mat.inputs[3].default_value))
    #pbrt_file.write("\n")
    #if vRoughnessTextureName != "" :
    #    pbrt_file.write(r'"texture %s" "%s"' % ("vroughness", vRoughnessTextureName))
    #else:
    #    pbrt_file.write(r'"float vroughness" [%s]' %(mat.inputs[4].default_value))
    #pbrt_file.write("\n")

    #if uRoughnessTextureName != "" :
    #    pbrt_file.write(r'"texture %s" "%s"' % ("vroughness", uRoughnessTextureName))
    #else:
    #    pbrt_file.write(r'"float uroughness" [%s]' %(mat.inputs[5].default_value))
    #pbrt_file.write("\n")

    if displacementTextureName != "":
        pbrt_file.write(r'"texture %s" "%s"' % ("displacement", displacementTextureName))
    pbrt_file.write("\n")
    return ''

def export_Pbrt_V4_CoatedDiffuse(pbrt_file, mat):
    
    reflectanceTextureName = export_texture_from_input(pbrt_file,mat.inputs[0],mat, False)
    vRoughnessTextureName = export_texture_from_input(pbrt_file,mat.inputs[1],mat, False)
    uRoughnessTextureName = export_texture_from_input(pbrt_file,mat.inputs[2],mat, False)
    thicknessTextureName = export_texture_from_input(pbrt_file,mat.inputs[3],mat, False)
    etaTextureName = export_texture_from_input(pbrt_file,mat.inputs[4],mat, False)
    displacementTextureName = export_texture_from_input(pbrt_file,mat.inputs[5],mat, False)
    
    pbrt_file.write(r'Material "coateddiffuse"')
    pbrt_file.write("\n")
    #pbrt_file.write(r'"float maxdepth" [%s]' %(mat.maxdepth))
    #pbrt_file.write("\n")
    #pbrt_file.write(r'"float nsamples" [%s]' %(mat.nsamples))
    pbrt_file.write("\n")
    
    if (mat.twosided):
        pbrt_file.write(r'"bool twosided" [true]')
    else:
        pbrt_file.write(r'"bool twosided" [false]')

    pbrt_file.write("\n")
    if (mat.remaproughness):
        pbrt_file.write(r'"bool remaproughness" [true]')
    else:
        pbrt_file.write(r'"bool remaproughness" [false]')

    pbrt_file.write("\n")

    if reflectanceTextureName != "" :
        pbrt_file.write(r'"texture %s" "%s"' % ("reflectance", reflectanceTextureName))
    else:
        pbrt_file.write(r'"rgb reflectance" [%s %s %s]' %(mat.inputs[0].default_value[0],mat.inputs[0].default_value[1],mat.inputs[0].default_value[2]))
    pbrt_file.write("\n")
    
    if vRoughnessTextureName != "" :
        pbrt_file.write(r'"texture %s" "%s"' % ("vroughness", vRoughnessTextureName))
    else:
        pbrt_file.write(r'"float vroughness" [%s]' %(mat.inputs[1].default_value))
    pbrt_file.write("\n")

    if uRoughnessTextureName != "" :
        pbrt_file.write(r'"texture %s" "%s"' % ("uroughness", uRoughnessTextureName))
    else:
        pbrt_file.write(r'"float uroughness" [%s]' %(mat.inputs[2].default_value))
    pbrt_file.write("\n")

    if thicknessTextureName != "" :
        pbrt_file.write(r'"texture %s" "%s"' % ("thickness", thicknessTextureName))
    else:
        pbrt_file.write(r'"float thickness" [%s]' %(mat.inputs[3].default_value))
    pbrt_file.write("\n")

    if etaTextureName != "" :
        pbrt_file.write(r'"texture %s" "%s"' % ("eta", etaTextureName))
    else:
        pbrt_file.write(r'"float eta" [%s]' %(mat.inputs[4].default_value))
    pbrt_file.write("\n")

    if displacementTextureName != "" :
        pbrt_file.write(r'"texture %s" "%s"' % ("displacement", displacementTextureName))
    #else:
        #pbrt_file.write(r'"float displacement" [%s]' %(mat.inputs[5].default_value))
    pbrt_file.write("\n")
    return ''
    
def export_Pbrt_V4_DiffuseTransmission(pbrt_file, mat):
    reflectanceTextureName = export_texture_from_input(pbrt_file,mat.inputs[0],mat, False)
    displacementTextureName = export_texture_from_input(pbrt_file,mat.inputs[1],mat, False)
    sigmaTextureName = export_texture_from_input(pbrt_file,mat.inputs[2],mat, False)

    pbrt_file.write(r'Material "diffusetransmission"')
    pbrt_file.write("\n")
    if reflectanceTextureName != "" :
        pbrt_file.write(r'"texture %s" "%s"' % ("reflectance", reflectanceTextureName))
    else:
        pbrt_file.write(r'"rgb reflectance" [%s %s %s]' %(mat.inputs[0].default_value[1],mat.inputs[0].default_value[1],mat.inputs[0].default_value[2]))
    pbrt_file.write("\n")

    if displacementTextureName != "" :
        pbrt_file.write(r'"texture %s" "%s"' % ("displacement", displacementTextureName))
        pbrt_file.write("\n")
    #else:
        #pbrt_file.write(r'"float displacement" [%s]' %(mat.inputs[1].default_value))
        

    if sigmaTextureName != "" :
        pbrt_file.write(r'"texture %s" "%s"' % ("sigma", sigmaTextureName))
    else:
        pbrt_file.write(r'"float sigma" [%s]' %(mat.inputs[2].default_value))
    pbrt_file.write("\n")
    
    if (mat.remaproughness):
        pbrt_file.write(r'"bool remaproughness" [true]')
    else:
        pbrt_file.write(r'"bool remaproughness" [false]')
    
    pbrt_file.write("\n")
    pbrt_file.write(r'"float scale" [%s]' %(mat.scale))
    pbrt_file.write("\n")

    return ''

def export_Pbrt_V4_Conductor(pbrt_file, mat):
    etaTextureName = export_texture_from_input(pbrt_file,mat.inputs[0],mat, False)
    kTextureName = export_texture_from_input(pbrt_file,mat.inputs[1],mat, False)
    vRoughnessTextureName = export_texture_from_input(pbrt_file,mat.inputs[2],mat, False)
    uRoughnessTextureName = export_texture_from_input(pbrt_file,mat.inputs[3],mat, False)
    displacementTextureName = export_texture_from_input(pbrt_file,mat.inputs[4],mat, False)

    pbrt_file.write(r'Material "conductor"')
    pbrt_file.write("\n")

    if etaTextureName != "" :
        pbrt_file.write(r'"texture %s" "%s"' % ("eta", etaTextureName))
    #else:
        #pbrt_file.write(r'"float eta" [%s]' %(mat.inputs[0].default_value))
    pbrt_file.write("\n")

    if kTextureName != "" :
        pbrt_file.write(r'"texture %s" "%s"' % ("k", kTextureName))
    else:
       pbrt_file.write(r'"rgb k" [%s %s %s]' %(mat.inputs[1].default_value[1],mat.inputs[1].default_value[1],mat.inputs[1].default_value[2]))
    pbrt_file.write("\n")

    if vRoughnessTextureName != "" :
        pbrt_file.write(r'"texture %s" "%s"' % ("vroughness", vRoughnessTextureName))
    else:
        pbrt_file.write(r'"float vroughness" [%s]' %(mat.inputs[2].default_value))
    pbrt_file.write("\n")

    if uRoughnessTextureName != "" :
        pbrt_file.write(r'"texture %s" "%s"' % ("uroughness", uRoughnessTextureName))
    else:
        pbrt_file.write(r'"float uroughness" [%s]' %(mat.inputs[3].default_value))
    pbrt_file.write("\n")

    if displacementTextureName != "" :
        pbrt_file.write(r'"texture %s" "%s"' % ("displacement", displacementTextureName))

    if (mat.remaproughness):
        pbrt_file.write(r'"bool remaproughness" [true]')
    else:
        pbrt_file.write(r'"bool remaproughness" [false]')
    pbrt_file.write("\n")
    return ''

def export_Pbrt_V4_Coated_Conductor(pbrt_file, mat):
    pbrt_file.write(r'Material "coatedconductor"')
    pbrt_file.write("\n")

    etaTextureName = export_texture_from_input(pbrt_file,mat.inputs[0],mat, False)
    kTextureName = export_texture_from_input(pbrt_file,mat.inputs[1],mat, False)
    interfaceURoughnessTextureName = export_texture_from_input(pbrt_file,mat.inputs[2],mat, False)
    interfaceVRoughnessTextureName = export_texture_from_input(pbrt_file,mat.inputs[3],mat, False)
    conductorVRoughnessTextureName = export_texture_from_input(pbrt_file,mat.inputs[4],mat, False)
    conductorURoughnessTextureName = export_texture_from_input(pbrt_file,mat.inputs[5],mat, False)
    displacementTextureName = export_texture_from_input(pbrt_file,mat.inputs[6],mat, False)

    if etaTextureName != "" :
        pbrt_file.write(r'"texture %s" "%s"' % ("eta", etaTextureName))
    else:
        pbrt_file.write(r'"float eta" [%s]' %(mat.inputs[0].default_value))
    pbrt_file.write("\n")

    if kTextureName != "" :
        pbrt_file.write(r'"texture %s" "%s"' % ("k", kTextureName))
    else:
        pbrt_file.write(r'"float k" [%s]' %(mat.inputs[1].default_value))
    pbrt_file.write("\n")

    if interfaceURoughnessTextureName != "" :
        pbrt_file.write(r'"texture %s" "%s"' % ("interface.uroughness", interfaceURoughnessTextureName))
    else:
        pbrt_file.write(r'"float interface.uroughness" [%s]' %(mat.inputs[2].default_value))
    pbrt_file.write("\n")

    if interfaceVRoughnessTextureName != "" :
        pbrt_file.write(r'"texture %s" "%s"' % ("interface.uroughness", interfaceVRoughnessTextureName))
    else:
        pbrt_file.write(r'"float interface.vroughness" [%s]' %(mat.inputs[3].default_value))
    pbrt_file.write("\n")

    if conductorURoughnessTextureName != "" :
        pbrt_file.write(r'"texture %s" "%s"' % ("conductor.uroughness", interfaceVRoughnessTextureName))
    else:
        pbrt_file.write(r'"float conductor.uroughness" [%s]' %(mat.inputs[4].default_value))
    pbrt_file.write("\n")

    if conductorVRoughnessTextureName != "" :
        pbrt_file.write(r'"texture %s" "%s"' % ("conductor.vroughness", interfaceVRoughnessTextureName))
    else:
        pbrt_file.write(r'"float conductor.vroughness" [%s]' %(mat.inputs[5].default_value))
    pbrt_file.write("\n")

    if displacementTextureName != "":
        pbrt_file.write(r'"texture %s" "%s"' % ("displacement", displacementTextureName))
    pbrt_file.write("\n")

    pbrt_file.write(r'"float thickness" [%s]' %(mat.thickness))
    if (mat.remaproughness):
        pbrt_file.write(r'"bool remaproughness" [true]')
    else:
        pbrt_file.write(r'"bool remaproughness" [false]')
    pbrt_file.write("\n")
    return ''

#TODO: Consider how we should define this light, either through a shader node, or possibly through a custom light widget.
#export_Pbrt_V4_Diffuse_Area_Light(pbrt_file, currentMaterial)
#    return StringPrintf("[ DiffuseAreaLight %s Lemit: %s scale: %f shape: %s alpha: %s "
#                        "twoSided: %s area: %f image: %s ]",
#                        BaseToString(), Lemit, scale, shape, alpha,
#                        twoSided ? "true" : "false", area, image);
def export_Pbrt_V4_Diffuse_Area_Light(pbrt_file, inputNode, objectName):
    pbrt_file.write(r'DiffuseAreaLight "%s"' %(inputNode.name))
    pbrt_file.write("\n")
    pbrt_file.write(r'"float scale" [ %s ]' % (1.0))
    pbrt_file.write("\n")
    pbrt_file.write(r'"shape" [ "%s" ]' % (objectName))
    pbrt_file.write("\n")
    return ''

def export_medium(pbrt_file, inputNode):
    if inputNode is not None:
         for node_links in inputNode.links:
            if node_links.from_node.bl_idname == "CustomNodeTypeMedium":
                mediumNode = node_links.from_node
                print('We have a node connected to medium slot.')
                print('The name of the connected node is: ')
                print(mediumNode.name)
                pbrt_file.write(r'MakeNamedMedium "%s"' % (mediumNode.name))
                pbrt_file.write("\n")
                pbrt_file.write(r'"string type" ["%s"]' % (mediumNode.Type))
                pbrt_file.write("\n")
                sigma_a = mediumNode.inputs[0].default_value
                pbrt_file.write(r'"rgb sigma_a" [ %s %s %s]' %(sigma_a[0],sigma_a[1],sigma_a[2]))
                pbrt_file.write("\n")
                sigma_s = mediumNode.inputs[1].default_value
                pbrt_file.write(r'"rgb sigma_s" [ %s %s %s]' %(sigma_s[0],sigma_s[1],sigma_s[2]))
                pbrt_file.write("\n")
                pbrt_file.write(r'"float g" [ %s ]' % (mediumNode.g))
                pbrt_file.write("\n")
                pbrt_file.write(r'"float scale" [ %s ]' % (mediumNode.Scale))
                pbrt_file.write("\n")
                pbrt_file.write("\n")
                return mediumNode.name
    return None

def export_pbrt_blackbody_material (pbrt_file, mat):
    print('Currently exporting Pbrt BlackBody material')
    print (mat.name)

    pbrt_file.write(r'AreaLightSource "diffuse" "blackbody L" [%s]' %(mat.Temperature))
    #pbrt_file.write(r'%s]' %(mat.Lambda))
    pbrt_file.write("\n")
    return ''

def hastexturenewcode(mat, slotname):
    foundTex = False
    print ("checking texture for : ")
    print(mat.name)
    print("checking slot named new code:")
    print(slotname)
    nodes = mat.node_tree.nodes
    #print(mat.[slotname])
    #if mat.slotname == !"":
        #print("Found filepath stored in slot:")
        #foundTex = True
    #print(mat.slotname)
    #print(mat.[slotname])
    print(len(mat.node_tree.links))
    if (len(mat.node_tree.links) > 1):
        socket = nodes[mat.node_tree.nodes[1].name].inputs[slotname]
        print("socket type:")
        print(socket.type)
        print("data stored in slot:")
        print(nodes[mat.node_tree.nodes[1].name].inputs[slotname])
        #links = mat.node_tree.links
        #link = next(l for l in links if l.to_socket == socket)
        #if link.from_node.type == 'TEX_IMAGE':
    return foundTex

def hastextureInSlot (mat,index):
    foundTex = False
    if getTextureInSlotName(index) != "":
        foundTex = True

    return foundTex

def getTextureInSlotName(textureSlotParam):
    srcfile = textureSlotParam
    head, tail = os.path.split(srcfile)
    print("File name is :")
    print(tail)

    return tail

def exportFloatTextureInSlotNew(pbrt_file,textureSlotParam):
    pbrt_file.write("\n")
    srcfile = bpy.path.abspath(textureSlotParam)
    texturefilename = getTextureInSlotName(srcfile)
    pbrt_file.write(r'Texture "%s" "float" "imagemap" "string filename" ["%s"]' % (texturefilename, ("textures/" + texturefilename)))
    pbrt_file.write("\n")
    dstdir = bpy.path.abspath('//pbrtExport/textures/' + texturefilename)
    print("os.path.dirname...")
    print(os.path.dirname(srcfile))
    print("\n")
    print("srcfile: ")
    print(srcfile)
    print("\n")
    print("dstdir: ")
    print(dstdir)
    print("\n")
    print("File name is :")
    print(texturefilename)
    print("!!!!! skipping copying for now..")
    #shutil.copyfile(srcfile, dstdir)
#    foundTex = True
    return ''


    ##TODO: write out the path to the file and call function from where we check if texture is in slot.
    ## send the filepath, slot name from there.
def exportTextureInSlot(pbrt_file,index,mat,slotname):
    nodes = mat.node_tree.nodes
    slot = index
#    foundTex = False
    socket = nodes[mat.node_tree.nodes[1].name].inputs[slot]
    links = mat.node_tree.links
    link = next(l for l in links if l.to_socket == socket)
    if link:
        image = link.from_node.image
        pbrt_file.write(r'Texture "%s" "spectrum" "imagemap" "string filename" ["%s"]' % (image.name, ("textures/" + image.name))) #.replace("\\","/")
        pbrt_file.write("\n")
        srcfile = bpy.path.abspath(image.filepath)
        dstdir = bpy.path.abspath('//pbrtExport/textures/' + image.name)
        print("os.path.dirname...")
        print(os.path.dirname(srcfile) + image.name)
        print("srcfile: ")
        print(srcfile)
        print("\n")
        print("dstdir: ")
        print(dstdir)
        print("\n")

        shutil.copyfile(srcfile, dstdir)
#        foundTex = True
    return ''

# Here we should check what material type is being exported.
def export_material(pbrt_file, object, slotIndex):
    # https://blender.stackexchange.com/questions/51782/get-material-and-color-of-material-on-a-face-of-an-object-in-python
    # https://blender.stackexchange.com/questions/36587/how-to-define-customized-property-in-material

    #context = bpy.context
    #obj = context.object
    print("Material slots:")
    print(len(object.material_slots))
    if len(object.material_slots) == 0:
        print("no material on object")
        return ''

    mat = object.data.materials[slotIndex]
    if mat == None:
        return''
    print ('Exporting material named: ',mat.name)

    global hastexture
    hastexture = False
    #textureName = ""
    # check if this code can be used so get the socket the image is plugged into:
    # https://blender.stackexchange.com/questions/77365/getting-the-image-of-a-texture-node-that-feeds-into-a-node-group

    #   Begin new texture code


    #Later we should loop through all 'slots' to write out all materials applied.

    mat = object.material_slots[slotIndex].material #Get the material from the material slot you want
    print ('Fetched material in slot 0 named: ', mat.name)
    if mat and mat.use_nodes: #if it is using nodes
        print('Mat name: ', mat.name)
        #print ('mat.node_tree.nodes[0].name:', mat.node_tree.nodes[0].name)
        #print ('mat.node_tree.nodes[1].name:', mat.node_tree.nodes[1].name)

        #We have the material, now find the output slot:
        for node in mat.node_tree.nodes:
            if node.name == 'Material Output':
                for input in node.inputs:
                    for node_links in input.links:
                        currentMaterial =  node_links.from_node
                        print("Current mat id name:")
                        print(currentMaterial.bl_idname)
                        if currentMaterial.bl_idname == 'Pbrt_V4_Diffuse':
                            export_Pbrt_V4_Diffuse(pbrt_file,currentMaterial)
                        if currentMaterial.bl_idname == 'Pbrt_V4_Dielectric':
                            export_Pbrt_V4_Dielectric(pbrt_file, currentMaterial)
                        if currentMaterial.bl_idname == 'Pbrt_V4_Thin_Dielectric':
                            export_Pbrt_V4_Thin_Dielectric(pbrt_file, currentMaterial)
                        if currentMaterial.bl_idname == 'Pbrt_V4_CoatedDiffuse':
                            export_Pbrt_V4_CoatedDiffuse(pbrt_file, currentMaterial)
                        if currentMaterial.bl_idname == 'Pbrt_V4_DiffuseTransmission':
                            export_Pbrt_V4_DiffuseTransmission(pbrt_file, currentMaterial)
                        if currentMaterial.bl_idname == 'Pbrt_V4_Conductor' :
                            export_Pbrt_V4_Conductor(pbrt_file, currentMaterial)
                        if currentMaterial.bl_idname == 'Pbrt_V4_Coated_Conductor' :
                            export_Pbrt_V4_Coated_Conductor(pbrt_file, currentMaterial)
                        if currentMaterial.bl_idname == 'Pbrt_V4_Diffuse_Area_Light' :
                            export_Pbrt_V4_Diffuse_Area_Light(pbrt_file, currentMaterial, object.name)


    return''

    # matrix to string
def matrixtostr(matrix):
    return '%f %f %f %f %f %f %f %f %f %f %f %f %f %f %f %f '%(matrix[0][0],matrix[0][1],matrix[0][2],matrix[0][3],matrix[1][0],matrix[1][1],matrix[1][2],matrix[1][3],matrix[2][0],matrix[2][1],matrix[2][2],matrix[2][3],matrix[3][0],matrix[3][1],matrix[3][2],matrix[3][3])

def createDefaultExportDirectories(pbrt_file, scene):
    texturePath = bpy.path.abspath(bpy.data.scenes[0].exportpath + 'textures')
    print("Exporting textures to: ")
    print(texturePath)

    if not os.path.exists(texturePath):
        print('Texture directory did not exist, creating: ')
        print(texturePath)
        os.makedirs(texturePath)


def export_geometry(pbrt_file, scene, frameNumber):
    
    # We now export the mesh as pbrt's triangle meshes.
    # Development documentation :
    # https://docs.blender.org/api/current/bpy.types.MeshLoopTriangle.html
    # https://wiki.blender.org/wiki/Reference/Release_Notes/2.80/Python_API/Mesh_API

    for object in scene.objects:
        print("exporting:")
        print(object.name)

        if object is not None and object.type != 'CAMERA' and object.type == 'MESH':
            bpy.ops.object.mode_set(mode='OBJECT')
            print('exporting object: ' + object.name)
            bpy.context.view_layer.update()
            object.data.update()
            dg = bpy.context.evaluated_depsgraph_get()
            eval_obj = object.evaluated_get(dg)
            mesh = eval_obj.to_mesh()
            if not mesh.loop_triangles and mesh.polygons:
                mesh.calc_loop_triangles()

            # Compute normals
            mesh.calc_normals_split()

            for i in range(max(len(object.material_slots), 1)):
                pbrt_file.attr_begin()
                pbrt_file.write( "Transform [" + matrixtostr( object.matrix_world.transposed() ) + "]\n" )
                if len(object.material_slots) != 0: export_material(pbrt_file, object, i)
                
                # TODO: This can be optimized further by computing the multiple list of vertices indices
                #   One for each material. However, this might not be a big deal as it is not too often 
                #   Than a single mesh have a lot of different material applied to it.

                # Generate the list of vertex index associated to the given material
                # These index will be used to export vertex position.
                # Moreover, depending on the number of indices, we will decide to generate a PLY
                # or not
                indices = []
                normals = []
                for tri in mesh.loop_triangles:
                    if tri.material_index == i:
                        indices.extend(tri.vertices)
                        normals.extend(tri.split_normals)
                print("Nb Tri: ", len(indices) // 3) 

                if len(indices) // 3 > 10:
                    # Prefer to export as separated file
                    # TODO: Detect if the object move across frames.
                    #   This might save a lot if we only export one geometry
                    objFolderPath = bpy.path.abspath(bpy.data.scenes[0].exportpath + 'meshes/' + frameNumber + '/')
                    if not os.path.exists(objFolderPath):
                        print('Meshes directory did not exist, creating: ')
                        print(objFolderPath)
                        os.makedirs(objFolderPath)

                    # Include the file that will be created
                    objFilePath = objFolderPath + object.name + f'_mat{i}.ply' 
                    objFilePathRel = 'meshes/' + frameNumber + '/' + object.name + f'_mat{i}.ply'


                    pbrt_file.write(f'Shape "plymesh" "string filename" ["{objFilePathRel}"]\n')
                    write_ply(objFilePath, mesh, indices, normals, i)
                else:
                    pbrt_file.write( "Shape \"trianglemesh\"\n")
                    pbrt_file.write( '\"point3 P\" [\n' )
                    pbrt_file.write(" ".join([str(item) for id_vertex in indices 
                                                            for item in [mesh.vertices[id_vertex].co.x, 
                                                                        mesh.vertices[id_vertex].co.y, 
                                                                        mesh.vertices[id_vertex].co.z]]))
                    pbrt_file.write( "\n" )
                    pbrt_file.write( "]\n" )

                    pbrt_file.write( "\"normal N\" [\n" )
                    pbrt_file.write(" ".join([str(item) for n in normals 
                                                            for item in n]))
                    pbrt_file.write( "\n" )
                    pbrt_file.write( "]\n" )

                    
                    pbrt_file.write( "\"point2 uv\" [\n" )
                    for uv_layer in mesh.uv_layers:
                        for tri in mesh.loop_triangles:
                            if tri.material_index == i:
                                for loop_index in tri.loops:
                                    pbrt_file.write("%s %s \n" % (uv_layer.data[loop_index].uv[0], uv_layer.data[loop_index].uv[1]))
                    pbrt_file.write( "]\n" )

                    pbrt_file.write( "\"integer indices\" [\n" )
                    pbrt_file.write("%s \n" % " ".join([str(i) for i in range(len(indices))]))
                    pbrt_file.write( "]\n" )

                pbrt_file.attr_end()
                pbrt_file.write("\n\n")

    return ''
    
def export_pbrt(filepath, scene , frameNumber):
    out = os.path.join(filepath, "test" + frameNumber +".pbrt")
    if not os.path.exists(filepath):
        print('Output directory did not exist, creating: ')
        print(filepath)
        os.makedirs(filepath)

    pbrt_file = PBRTWriter(out)
    createDefaultExportDirectories(pbrt_file,scene)
    export_film(pbrt_file, frameNumber)
    export_sampler(pbrt_file)
    export_integrator(pbrt_file,scene)
    export_camera(pbrt_file)
    
    world_begin(pbrt_file)
    pbrt_file.inc_indent()

    export_EnviromentMap(pbrt_file)
    print('Begin export lights:')
    export_point_lights(pbrt_file,scene)
    export_spot_lights(pbrt_file,scene)
    print('End export lights.')
    export_geometry(pbrt_file,scene,frameNumber)
    pbrt_file.dec_indent()
    pbrt_file.close()
