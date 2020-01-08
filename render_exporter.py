import bpy
import bmesh
import os
import math
from math import *
import mathutils
from mathutils import Vector
import shutil

#render engine custom begin
class PBRTRenderEngine(bpy.types.RenderEngine):
    bl_idname = 'PBRT_Renderer'
    bl_label = 'PBRT_Renderer'
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
        subclass.COMPAT_ENGINES.add('PBRT_Renderer')
    except:
        pass

for member in dir(properties_material):
    subclass = getattr(properties_material, member)
    try:
        subclass.COMPAT_ENGINES.add('PBRT_Renderer')
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
                print('LA TYPE: ' + la.type)
                if la.type == "SPOT" :
                    # Example:
                    # LightSource "spot" "point from" [0 5 9] "point to" [-5 2.75 0] "blackbody I" [5500 125]
                    print('\n\nexporting light: ' + la.name + ' - type: ' + la.type)
                    #spotmatrix = ob.matrix_world.copy()
                    #matrixTransposed = spotmatrix.transposed()
                    from_point=ob.matrix_world.col[3]
                    at_point=ob.matrix_world.col[2]
                    at_point=at_point * -1
                    at_point=at_point + from_point
                    pbrt_file.write("AttributeBegin\n")
                    pbrt_file.write(" LightSource \"spot\"\n \"point from\" [%s %s %s]\n \"point to\" [%s %s %s]\n" % (from_point.x, from_point.y, from_point.z,at_point.x, at_point.y, at_point.z))
                    
                    #TODO: Parse the values from the light \ color and so on. also add falloff etc.
                    pbrt_file.write("\"blackbody I\" [5500 125]\n")

                    pbrt_file.write("AttributeEnd\n\n")
    return ''

def export_point_lights(pbrt_file, scene):
    for object in scene.objects:
        if object is not None and object.type == 'POINT':
            print('\n\nexporting lamp: ' + object.name + ' - type: ' + object.type)
            print('\nExporting point light: ' + object.name)
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.scene.objects.active = object
            pbrt_file.write("AttributeBegin")
            pbrt_file.write("\n")
            from_point=object.matrix_world.col[3]
            pbrt_file.write("Translate\t%s %s %s\n" % (from_point.x, from_point.y, from_point.z))
            pbrt_file.write("LightSource \"point\"\n\"rgb I\" [%s %s %s]\n" % (bpy.data.objects[object.name].color[0], bpy.data.objects[object.name].color[1], bpy.data.objects[object.name].color[2]))
            #pbrt_file.write("LightSource \"point\"\n\"rgb I\" [%s %s %s]\n" % (nodes["Emission"].inputs[0].default_value[0], nodes["Emission"].inputs[0].default_value[1], nodes["Emission"].inputs[0].default_value[2]))
            pbrt_file.write("AttributeEnd")
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
        fov = bpy.data.cameras[0].angle * 180 / 3.14
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
    pbrt_file.write(r'Film "image" "integer xresolution" [%s] "integer yresolution" [%s] "string filename" "%s"' % (bpy.data.scenes[0].resolution_x, bpy.data.scenes[0].resolution_y, finalFileName))
    pbrt_file.write("\n")

    pbrt_file.write(r'PixelFilter "%s" "float xwidth" [%s] "float ywidth" [%s] ' % (bpy.data.scenes[0].filterType, bpy.data.scenes[0].filter_x_width, bpy.data.scenes[0].filter_y_width))
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
    pbrt_file.write(r'Sampler "halton" "integer pixelsamples" [%s]'% (bpy.data.scenes[0].spp))
    pbrt_file.write("\n")
    return ''

def export_integrator(pbrt_file, scene):
    pbrt_file.write(r'Integrator "%s"' % (bpy.data.scenes[0].integrators))
    pbrt_file.write("\n")
    pbrt_file.write(r'"integer maxdepth" [%s]' % (bpy.data.scenes[0].maxdepth))
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

def world_end(pbrt_file):
    pbrt_file.write("WorldEnd")
    pbrt_file.write("\n")
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
        pbrt_file.write("AttributeBegin\n")
        pbrt_file.write(r'LightSource "infinite" "string mapname" "%s" "color scale" [%s %s %s]' % ("textures/" + environmentMapFileName,environmentmapscaleValue,environmentmapscaleValue,environmentmapscaleValue))
        pbrt_file.write("\n")
        pbrt_file.write("AttributeEnd")
        pbrt_file.write("\n\n")

def export_environmentLight(pbrt_file):
    print("image texture type: ")
    pbrt_file.write("\n")
    environmenttype = bpy.data.worlds['World'].node_tree.nodes['Background'].inputs['Color'].links[0].from_node.type
    environmentMapPath = ""
    environmentMapFileName = ""
    print(environmenttype)
    pbrt_file.write("AttributeBegin\n")

    if environmenttype == "TEX_IMAGE":
        print(environmenttype)
        environmentMapPath = bpy.data.worlds['World'].node_tree.nodes['Background'].inputs['Color'].links[0].from_node.image.filepath
        environmentMapFileName= getTextureInSlotName(environmentMapPath)
        print(environmentMapPath)
        print(environmentMapFileName)
        print("background strength: value:")
        backgroundStrength = bpy.data.worlds['World'].node_tree.nodes['Background'].inputs[1].default_value
        print(backgroundStrength)
        pbrt_file.write(r'LightSource "infinite" "string mapname" "%s" "color scale" [%s %s %s]' % ("textures/" + environmentMapFileName,backgroundStrength,backgroundStrength,backgroundStrength))


    pbrt_file.write("\n")
    #pbrt_file.write(r'Rotate 10 0 0 1 Rotate -110 1 0 0 LightSource "infinite" "string mapname" "textures/20060807_wells6_hd.exr" "color scale" [2.5 2.5 2.5]')
    if environmenttype == "RGB":
        print(bpy.data.worlds['World'].node_tree.nodes['Background'].inputs['Color'].default_value[0])
        pbrt_file.write(r'LightSource "infinite" "color L" [%s %s %s] "color scale" [%s %s %s]' %(bpy.data .worlds['World'].node_tree.nodes['Background'].inputs['Color'].default_value[0],bpy.data .worlds['World'].node_tree.nodes['Background'].inputs['Color'].default_value[1],bpy.data .worlds['World'].node_tree.nodes['Background'].inputs['Color'].default_value[2],backgroundStrength,backgroundStrength,backgroundStrength))

    pbrt_file.write("\n")
    pbrt_file.write("AttributeEnd")
    pbrt_file.write("\n\n")
    return ''

def export_defaultMaterial(pbrt_file):
    pbrt_file.write(r'Material "plastic"')
    pbrt_file.write("\n")
    pbrt_file.write(r'"color Kd" [.1 .1 .1]')
    pbrt_file.write("\n")
    pbrt_file.write(r'"color Ks" [.7 .7 .7] "float roughness" .1')
    pbrt_file.write("\n\n")
    return ''

def exportTextureInSlotNew(pbrt_file,textureSlotParam,isFloatTexture):
    pbrt_file.write("\n")
    srcfile = bpy.path.abspath(textureSlotParam)
    texturefilename = getTextureInSlotName(srcfile)
    if isFloatTexture :
        pbrt_file.write(r'Texture "%s" "float" "imagemap" "string filename" ["%s"]' % (texturefilename, ("textures/" + texturefilename)))
    else:
        pbrt_file.write(r'Texture "%s" "color" "imagemap" "string filename" ["%s"]' % (texturefilename, ("textures/" + texturefilename)))

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
    kdTextureName = ""
    slot = inputSlot
    
    matnodes = mat.node_tree.nodes
    imgnodes = 0
    imgnodes = [n for n in matnodes if n.type == 'TEX_IMAGE']
    if (len(imgnodes) == 0):
        print("We have no texture defined, exporting RGB")
        return ""
    else:
        print('number of image nodes connected:')
        print(len(imgnodes))
        print('image nodes')
        print(imgnodes)


    links = mat.node_tree.links
    print('Number of links: ')
    print(len(links))

    #link = next(l for l in links if l.to_socket == slot)
    link = None
    for currentLink in links:
        print(currentLink)
        if currentLink.to_socket == slot:
            print('Found the texture')
            link = currentLink
    
    if link is None:
        return ""
    
    if link:
        print('Current link type:')
        print(link.from_node.type)
        if link.from_node.type == 'TEX_IMAGE':
            image = link.from_node.image
            print('Found image!')
            print(image.name)
            print('At index:')
            kdTextureName  = image.name
            exportTextureInSlotNew(pbrt_file,image.filepath,isFloatTexture)
    return kdTextureName

def export_pbrt_matte_material (pbrt_file, mat):
    print('Currently exporting Pbrt Matte material')
    print (mat.name)

    #New code begin
    nodes = mat.node_tree.nodes
    #Export used textures BEFORE we define the material itself.
    kdTextureName = ""
    kdTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Matte"].inputs[0],mat, False)

    pbrt_file.write(r'Material "matte"')
    pbrt_file.write("\n")
    pbrt_file.write(r'"float sigma" [%s]' %(nodes["Pbrt Matte"].Sigma))
    pbrt_file.write("\n")
    
    if kdTextureName != "" :
       pbrt_file.write(r'"texture %s" "%s"' % ("Kd", kdTextureName))
    else:
        pbrt_file.write(r'"color Kd" [ %s %s %s]' %(nodes["Pbrt Matte"].Kd[0],nodes["Pbrt Matte"].Kd[1],nodes["Pbrt Matte"].Kd[2]))

    pbrt_file.write("\n")
    return ''

def export_pbrt_mirror_material (pbrt_file, mat):
    print('Currently exporting Pbrt mirror material')
    print (mat.name)
    nodes = mat.node_tree.nodes
    
    krTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Mirror"].inputs[0],mat,False)

    pbrt_file.write(r'Material "mirror"')
    pbrt_file.write("\n")

    if krTextureName != "":
       pbrt_file.write(r'"texture %s" "%s"' % ("Kr", krTextureName))
    else:
        pbrt_file.write(r'"color Kr" [ %s %s %s]' %(nodes["Pbrt Mirror"].Kr[0],nodes["Pbrt Mirror"].Kr[1],nodes["Pbrt Mirror"].Kr[2]))
    
    pbrt_file.write("\n")
    return ''

def export_principled_bsdf_material(pbrt_file, mat):
    print('Currently exporting principled_bsdf material, converting the material to pbrt disney on export.')
    print (mat.name)
    nodes = mat.node_tree.nodes
    pbrt_file.write(r'Material "disney"')
    pbrt_file.write("\n")
    
    pbrt_file.write(r'"color color" [%s %s %s]' %(nodes["Principled BSDF"].inputs[0].default_value[0], nodes["Principled BSDF"].inputs[0].default_value[1], nodes["Principled BSDF"].inputs[0].default_value[2]))
    pbrt_file.write("\n")
    pbrt_file.write(r'"float metallic" [%s]' %(nodes["Principled BSDF"].inputs[4].default_value))
    pbrt_file.write("\n")
    pbrt_file.write(r'"float speculartint" [%s]' %(nodes["Principled BSDF"].inputs[6].default_value))
    pbrt_file.write("\n")
    pbrt_file.write(r'"float roughness" [%s]' %(nodes["Principled BSDF"].inputs[7].default_value))
    pbrt_file.write("\n")
    pbrt_file.write(r'"float sheen" [%s]' %(nodes["Principled BSDF"].inputs[10].default_value))
    pbrt_file.write("\n")
    pbrt_file.write(r'"float sheentint" [%s]' %(nodes["Principled BSDF"].inputs[11].default_value))
    pbrt_file.write("\n")
    pbrt_file.write(r'"float clearcoat" [%s]' %(nodes["Principled BSDF"].inputs[12].default_value))
    pbrt_file.write("\n")
    pbrt_file.write(r'"float difftrans" [%s]' %(nodes["Principled BSDF"].inputs[15].default_value))
    pbrt_file.write("\n")

    return ''

def export_pbrt_translucent_material(pbrt_file, mat):
    print('Currently exporting Pbrt Translucent material')
    print (mat.name)

    nodes = mat.node_tree.nodes
    kdTextureName = ""
    kdTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Translucent"].inputs[0],mat, False)
    ksTextureName = ""
    ksTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Translucent"].inputs[1],mat, False)
    ReflectTextureName = ""
    ReflectTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Translucent"].inputs[2],mat, False)
    TransmitTextureName = ""
    TransmitTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Translucent"].inputs[3],mat, False)
    
    pbrt_file.write(r'Material "translucent"')
    pbrt_file.write("\n")
    pbrt_file.write(r'"float roughness" [%s]' %(nodes["Pbrt Translucent"].Roughness))
    pbrt_file.write("\n")
    
    if kdTextureName != "" :
       pbrt_file.write(r'"texture %s" "%s"' % ("Kd", kdTextureName))
       pbrt_file.write("\n")
    else:
        pbrt_file.write(r'"color Kd" [ %s %s %s]' %(nodes["Pbrt Translucent"].Kd[0],nodes["Pbrt Translucent"].Kd[1],nodes["Pbrt Translucent"].Kd[2]))
        pbrt_file.write("\n")
    if ksTextureName != "" :
       pbrt_file.write(r'"texture %s" "%s"' % ("Ks", ksTextureName))
       pbrt_file.write("\n")
    else:
        pbrt_file.write(r'"color Ks" [ %s %s %s]' %(nodes["Pbrt Translucent"].Ks[0],nodes["Pbrt Translucent"].Ks[1],nodes["Pbrt Translucent"].Ks[2]))
        pbrt_file.write("\n")
    if ReflectTextureName != "" :
        pbrt_file.write(r'"texture %s" "%s"' % ("reflect", ReflectTextureName))
        pbrt_file.write("\n")
    else:
        pbrt_file.write(r'"color reflect" [ %s %s %s]' %(nodes["Pbrt Translucent"].Reflect[0],nodes["Pbrt Translucent"].Reflect[1],nodes["Pbrt Translucent"].Reflect[2]))
        pbrt_file.write("\n")
    if TransmitTextureName != "" :
        pbrt_file.write(r'"texture %s" "%s"' % ("transmit", TransmitTextureName))
        pbrt_file.write("\n")
    else:
        pbrt_file.write(r'"color transmit" [ %s %s %s]' %(nodes["Pbrt Translucent"].Transmit[0],nodes["Pbrt Translucent"].Transmit[1],nodes["Pbrt Translucent"].Transmit[2]))
    if nodes["Pbrt Translucent"].Remaproughness == True :
        pbrt_file.write(r'"bool remaproughness" "true"')
        pbrt_file.write("\n")
    else:
        pbrt_file.write(r'"bool remaproughness" "false"')
        pbrt_file.write("\n")
    return ''

def export_medium(pbrt_file, inputNode ,nodes):
    if inputNode is not None:
        mediumNode = nodes.get("Pbrt Medium")
        if mediumNode:
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

def export_pbrt_glass_material (pbrt_file, mat):
    print('Currently exporting Pbrt Glass material')
    print (mat.name)
    nodes = mat.node_tree.nodes
    
    krTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Glass"].inputs[2],mat,False)
    ktTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Glass"].inputs[3],mat,False)
    uRoughnessTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Glass"].inputs[0],mat,True)
    vRoughnessTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Glass"].inputs[1],mat, True)

    mediumNodeName = export_medium(pbrt_file,nodes["Pbrt Glass"].inputs[4],nodes)
    if mediumNodeName is not None:
        pbrt_file.write(r'MediumInterface "%s" ""' % (mediumNodeName))
        pbrt_file.write("\n")

    pbrt_file.write(r'Material "glass"')
    pbrt_file.write("\n")

    if krTextureName != "":
       pbrt_file.write(r'"texture %s" "%s"' % ("Kr", krTextureName))
    else:
        pbrt_file.write(r'"color Kr" [ %s %s %s]' %(nodes["Pbrt Glass"].kr[0],nodes["Pbrt Glass"].kr[1],nodes["Pbrt Glass"].kr[2]))
    pbrt_file.write("\n")
    
    if ktTextureName != "":
       pbrt_file.write(r'"texture %s" "%s"' % ("Kt", ktTextureName))
    else:
        pbrt_file.write(r'"color Kt" [ %s %s %s]' %(nodes["Pbrt Glass"].kt[0],nodes["Pbrt Glass"].kt[1],nodes["Pbrt Glass"].kt[2]))
    pbrt_file.write("\n")
    
    if(uRoughnessTextureName != ""):
        pbrt_file.write(r'"texture %s" "%s"' % ("uroughness", uRoughnessTextureName))
    else:
        pbrt_file.write(r'"float uroughness" [%s]' %(nodes["Pbrt Glass"].uRoughness))
    pbrt_file.write("\n")
    
    if (vRoughnessTextureName != ""):
        pbrt_file.write(r'"texture %s" "%s"' % ("vroughness", vRoughnessTextureName))
    else:
        pbrt_file.write(r'"float vroughness" [%s]' %(nodes["Pbrt Glass"].vRoughness))
    pbrt_file.write("\n")

    pbrt_file.write(r'"float index" [%s]' %(nodes["Pbrt Glass"].Index))
    pbrt_file.write("\n")

    return ''

def export_pbrt_substrate_material (pbrt_file, mat):

    print('Currently exporting Pbrt Substrate material')
    print (mat.name)
    nodes = mat.node_tree.nodes

    uRoughnessTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Substrate"].inputs[0],mat,True)
    vRoughnessTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Substrate"].inputs[1],mat, True)
    kdTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Substrate"].inputs[2],mat,False)
    ksTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Substrate"].inputs[3],mat,False)

    pbrt_file.write(r'Material "substrate"')
    pbrt_file.write("\n")

    if(uRoughnessTextureName != ""):
        pbrt_file.write(r'"texture %s" "%s"' % ("uroughness", uRoughnessTextureName))
    else:
        pbrt_file.write(r'"float uroughness" [%s]'\
        %(nodes["Pbrt Substrate"].uRoughness))
    pbrt_file.write("\n")

    if (vRoughnessTextureName != ""):
        pbrt_file.write(r'"texture %s" "%s"' % ("vroughness", vRoughnessTextureName))
    else:
        pbrt_file.write(r'"float vroughness" [%s]'\
        %(nodes["Pbrt Substrate"].vRoughness))
    pbrt_file.write("\n")

    if (kdTextureName != ""):
        pbrt_file.write(r'"texture %s" "%s"' % ("Kd", kdTextureName))
    else :
        pbrt_file.write(r'"color Kd" [ %s %s %s]' %(nodes["Pbrt Substrate"].Kd[0],nodes["Pbrt Substrate"].Kd[1],nodes["Pbrt Substrate"].Kd[2]))
    pbrt_file.write("\n")

    if (ksTextureName != ""):
        pbrt_file.write(r'"texture %s" "%s"' % ("Ks", ksTextureName))
    else :
        pbrt_file.write(r'"color Ks" [ %s %s %s]' %(nodes["Pbrt Substrate"].Ks[0],nodes["Pbrt Substrate"].Ks[1],nodes["Pbrt Substrate"].Ks[2]))
    pbrt_file.write("\n")
    return ''


#TODO: export sigma_a sigma_s texture and color

def export_pbrt_subsurface_material (pbrt_file, mat):
    print('Currently exporting Pbrt Subsurface material.')
    print (mat.name)
    nodes = mat.node_tree.nodes

    uRoughnessTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Subsurface"].inputs[0],mat,True)
    vRoughnessTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Subsurface"].inputs[1],mat, True)
    krTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Subsurface"].inputs[2],mat,False)
    ktTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Subsurface"].inputs[3],mat,False)

    sigma_aTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Subsurface"].inputs[4],mat,False)
    sigma_sTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Subsurface"].inputs[5],mat,False)

    mediumNodeName = export_medium(pbrt_file,nodes["Pbrt Subsurface"].inputs[6],nodes)

    if mediumNodeName is not None:
        pbrt_file.write(r'MediumInterface "%s" ""' % (mediumNodeName))
        pbrt_file.write("\n")

    pbrt_file.write(r'Material "subsurface"')
    pbrt_file.write("\n")
    if (nodes["Pbrt Subsurface"].presetName != "None"):
        pbrt_file.write(r'"string name" ["%s"]' % (nodes["Pbrt Subsurface"].presetName))
        pbrt_file.write("\n")

    pbrt_file.write(r'"float scale" [%s]'\
    %(nodes["Pbrt Subsurface"].scale))
    pbrt_file.write("\n")
    pbrt_file.write(r'"float eta" [%s]'\
    %(nodes["Pbrt Subsurface"].eta))
    pbrt_file.write("\n")

    if(uRoughnessTextureName != ""):
        pbrt_file.write(r'"texture %s" "%s"' % ("uroughness", uRoughnessTextureName))
    else:
        pbrt_file.write(r'"float uroughness" [%s]'\
        %(nodes["Pbrt Subsurface"].uRoughness))
    pbrt_file.write("\n")
    if (vRoughnessTextureName != ""):
        pbrt_file.write(r'"texture %s" "%s"' % ("vroughness", vRoughnessTextureName))
    else:
        pbrt_file.write(r'"float vroughness" [%s]'\
        %(nodes["Pbrt Subsurface"].vRoughness))
    pbrt_file.write("\n")

    if (krTextureName != ""):
        pbrt_file.write(r'"texture %s" "%s"' % ("Kr", krTextureName))
    else :
            if (nodes["Pbrt Subsurface"].presetName == "None"):
                pbrt_file.write(r'"color Kr" [ %s %s %s]' %(nodes["Pbrt Subsurface"].kr[0],nodes["Pbrt Subsurface"].kr[1],nodes["Pbrt Subsurface"].kr[2]))
    pbrt_file.write("\n")

    if (ktTextureName != ""):
        pbrt_file.write(r'"texture %s" "%s"' % ("Kt", ktTextureName))
    else :
            if (nodes["Pbrt Subsurface"].presetName == "None"):
                pbrt_file.write(r'"color Kt" [ %s %s %s]' %(nodes["Pbrt Subsurface"].kt[0],nodes["Pbrt Subsurface"].kt[1],nodes["Pbrt Subsurface"].kt[2]))
    pbrt_file.write("\n")
    
    if (nodes["Pbrt Subsurface"].presetName == "None"):
        if (sigma_aTextureName != ""):
            pbrt_file.write(r'"texture %s" "%s"' % ("Sigma_a", sigma_aTextureName))
        else:
            pbrt_file.write(r'"color sigma_a" [ %s %s %s]' %(nodes["Pbrt Subsurface"].sigma_a[0],nodes["Pbrt Subsurface"].sigma_a[1],nodes["Pbrt Subsurface"].sigma_a[2]))
        pbrt_file.write("\n")
        if (sigma_sTextureName != ""):
            pbrt_file.write(r'"texture %s" "%s"' % ("Sigma_s", sigma_sTextureName))
        else:
            pbrt_file.write(r'"color sigma_s" [ %s %s %s]' %(nodes["Pbrt Subsurface"].sigma_s[0],nodes["Pbrt Subsurface"].sigma_s[1],nodes["Pbrt Subsurface"].sigma_a[2]))
        pbrt_file.write("\n")

        if nodes["Pbrt Subsurface"].remaproughness == True :
            pbrt_file.write(r'"bool remaproughness" "true"')
            pbrt_file.write("\n")
        else:
            pbrt_file.write(r'"bool remaproughness" "false"')
            pbrt_file.write("\n")

        

    return ''

def export_pbrt_uber_material (pbrt_file, mat):
    print('Currently exporting Pbrt Uber material.')
    print (mat.name)
    nodes = mat.node_tree.nodes
    
    kdTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Uber"].inputs[0],mat,False)
    ksTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Uber"].inputs[1],mat,False)
    krTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Uber"].inputs[2],mat,False)
    ktTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Uber"].inputs[3],mat,False)
    uRoughnessTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Uber"].inputs[4],mat,True)
    vRoughnessTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Uber"].inputs[5],mat, True)
    opacityTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Uber"].inputs[6],mat, True)

    pbrt_file.write(r'Material "uber"')
    pbrt_file.write("\n")
    if (kdTextureName != ""):
        pbrt_file.write(r'"texture %s" "%s"' % ("Kd", kdTextureName))
    else :
        pbrt_file.write(r'"color Kd" [ %s %s %s]' %(nodes["Pbrt Uber"].kd[0],nodes["Pbrt Uber"].kd[1],nodes["Pbrt Uber"].kd[2]))
    pbrt_file.write("\n")

    if (ksTextureName != ""):
        pbrt_file.write(r'"texture %s" "%s"' % ("Ks", ksTextureName))
    else :
        pbrt_file.write(r'"color Ks" [ %s %s %s]' %(nodes["Pbrt Uber"].ks[0],nodes["Pbrt Uber"].ks[1],nodes["Pbrt Uber"].ks[2]))
    pbrt_file.write("\n")
    if (krTextureName != ""):
        pbrt_file.write(r'"texture %s" "%s"' % ("Kr", krTextureName))
    else :
        pbrt_file.write(r'"color Kr" [ %s %s %s]' %(nodes["Pbrt Uber"].kr[0],nodes["Pbrt Uber"].kr[1],nodes["Pbrt Uber"].kr[2]))
    pbrt_file.write("\n")
    if (ktTextureName != ""):
        pbrt_file.write(r'"texture %s" "%s"' % ("Kt", ktTextureName))
    else :
        pbrt_file.write(r'"color Kt" [ %s %s %s]' %(nodes["Pbrt Uber"].kt[0],nodes["Pbrt Uber"].kt[1],nodes["Pbrt Uber"].kt[2]))
    pbrt_file.write("\n")
    if(uRoughnessTextureName != ""):
        pbrt_file.write(r'"texture %s" "%s"' % ("uroughness", uRoughnessTextureName))
    else:
        pbrt_file.write(r'"float uroughness" [%s]'\
        %(nodes["Pbrt Uber"].uRoughness))
    pbrt_file.write("\n")
    if (vRoughnessTextureName != ""):
        pbrt_file.write(r'"texture %s" "%s"' % ("vroughness", vRoughnessTextureName))
    else:
        pbrt_file.write(r'"float vroughness" [%s]' %(nodes["Pbrt Uber"].vRoughness))
    pbrt_file.write("\n")
    if nodes["Pbrt Uber"].eta != 0.0:
        pbrt_file.write(r'"float eta" [%s]' %(nodes["Pbrt Uber"].eta))
    pbrt_file.write("\n")
    if (opacityTextureName != ""):
        pbrt_file.write(r'"texture %s" "%s"' % ("opacity", opacityTextureName))
        pbrt_file.write("\n")
    return ''


def export_pbrt_plastic_material (pbrt_file, mat):
    print('Currently exporting Pbrt Plastic material.')
    print (mat.name)
    nodes = mat.node_tree.nodes
    
    kdTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Plastic"].inputs[0],mat,False)
    ksTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Plastic"].inputs[1],mat,False)
    roughnessTextureName=export_texture_from_input(pbrt_file,nodes["Pbrt Plastic"].inputs[2],mat,True)

    pbrt_file.write(r'Material "plastic"')
    pbrt_file.write("\n")

    if (kdTextureName != ""):
        pbrt_file.write(r'"texture %s" "%s"' % ("Kd", kdTextureName))
    else :
        pbrt_file.write(r'"color Kd" [ %s %s %s]' %(nodes["Pbrt Plastic"].Kd[0],nodes["Pbrt Plastic"].Kd[1],nodes["Pbrt Plastic"].Kd[2]))
    pbrt_file.write("\n")

    if (ksTextureName != ""):
        pbrt_file.write(r'"texture %s" "%s"' % ("Ks", ksTextureName))
    else :
        pbrt_file.write(r'"color Ks" [ %s %s %s]' %(nodes["Pbrt Plastic"].Ks[0],nodes["Pbrt Plastic"].Ks[1],nodes["Pbrt Plastic"].Ks[2]))
    pbrt_file.write("\n")

    if (roughnessTextureName != ""):
        pbrt_file.write(r'"texture %s" "%s"' % ("Roughness", roughnessTextureName))
    else:
        pbrt_file.write(r'"float roughness" [%s]' %(nodes["Pbrt Plastic"].Roughness))
    pbrt_file.write("\n")

    return ''

def export_pbrt_metal_material (pbrt_file, mat):
    print('Currently exporting Pbrt Metal material')
    print (mat.name)
    nodes = mat.node_tree.nodes
    etaTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Metal"].inputs[0],mat,False)
    kTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Metal"].inputs[1],mat,False)
    uRoughnessTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Metal"].inputs[2],mat,True)
    vRoughnessTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Metal"].inputs[3],mat, True)
    bumpTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Metal"].inputs[4],mat, True)

    pbrt_file.write(r'Material "metal"')
    pbrt_file.write("\n")

    if (etaTextureName != ""):
        pbrt_file.write(r'"texture %s" "%s"' % ("eta", etaTextureName))
    else :
        pbrt_file.write(r'"color eta" [ %s %s %s]' %(nodes["Pbrt Metal"].eta[0],nodes["Pbrt Metal"].eta[1],nodes["Pbrt Metal"].eta[2]))
    pbrt_file.write("\n")

    if (kTextureName != ""):
        pbrt_file.write(r'"texture %s" "%s"' % ("k", kTextureName))
    else :
        pbrt_file.write(r'"color k" [ %s %s %s]' %(nodes["Pbrt Metal"].kt[0],nodes["Pbrt Metal"].kt[1],nodes["Pbrt Metal"].kt[2]))
    pbrt_file.write("\n")

    pbrt_file.write(r'"float roughness" [%s]' %(nodes["Pbrt Metal"].roughness))
    pbrt_file.write("\n")
    
    if(uRoughnessTextureName != ""):
        pbrt_file.write(r'"texture %s" "%s"' % ("uroughness", uRoughnessTextureName))
    else:
        pbrt_file.write(r'"float uroughness" [%s]'\
        %(nodes["Pbrt Metal"].uRoughness))
    pbrt_file.write("\n")

    if (vRoughnessTextureName != ""):
        pbrt_file.write(r'"texture %s" "%s"' % ("vroughness", vRoughnessTextureName))
    else:
        pbrt_file.write(r'"float vroughness" [%s]'\
        %(nodes["Pbrt Metal"].vRoughness))
    pbrt_file.write("\n")

    if (bumpTextureName != ""):
        pbrt_file.write(r'"texture %s" "%s"' % ("bumpmap", bumpTextureName))

    return ''

def export_pbrt_disney_material (pbrt_file, mat):
    print('Currently exporting Pbrt Disney material.')
    print (mat.name)
    nodes = mat.node_tree.nodes

    colorTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Disney"].inputs[0],mat,False)
    metallicTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Disney"].inputs[1],mat,True)
    etaTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Disney"].inputs[2],mat,True)
    roughnessTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Disney"].inputs[3],mat,True)
    speculartintTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Disney"].inputs[4],mat,True)
    anisotropicTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Disney"].inputs[5],mat,True)
    sheenTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Disney"].inputs[6],mat,True)
    sheenTintTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Disney"].inputs[7],mat,True)
    clearCoatTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Disney"].inputs[8],mat,True)
    clearCoatGlossTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Disney"].inputs[9],mat,True)
    specTransTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Disney"].inputs[10],mat,True)
    flatnessTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Disney"].inputs[11],mat,True)
    diffTransTextureName = export_texture_from_input(pbrt_file,nodes["Pbrt Disney"].inputs[12],mat,True)

    pbrt_file.write(r'Material "disney"')
    pbrt_file.write("\n")
    
    if (colorTextureName != ""):
        pbrt_file.write(r'"texture %s" "%s"' % ("color", colorTextureName))
    else :    
        pbrt_file.write(r'"color color" [%s %s %s]' %(nodes["Pbrt Disney"].color[0], nodes["Pbrt Disney"].color[1], nodes["Pbrt Disney"].color[2]))
    pbrt_file.write("\n")

    if (metallicTextureName != ""):
        pbrt_file.write(r'"texture %s" "%s"' % ("metallic", metallicTextureName))
    else :
        pbrt_file.write(r'"float metallic" [%s]' %(nodes["Pbrt Disney"].metallic))
    pbrt_file.write("\n")

    if (etaTextureName != ""):
        pbrt_file.write(r'"texture %s" "%s"' % ("eta", etaTextureName))
    else :
        pbrt_file.write(r'"float eta" [%s]' %(nodes["Pbrt Disney"].eta))
    pbrt_file.write("\n")

    if (roughnessTextureName != ""):
        pbrt_file.write(r'"texture %s" "%s"' % ("roughness", roughnessTextureName))
    else :
        pbrt_file.write(r'"float roughness" [%s]' %(nodes["Pbrt Disney"].roughness))
    pbrt_file.write("\n")
    
    if (speculartintTextureName != ""):
        pbrt_file.write(r'"texture %s" "%s"' % ("speculartint", speculartintTextureName))
    else :
        pbrt_file.write(r'"float speculartint" [%s]' %(nodes["Pbrt Disney"].specularTint))
    pbrt_file.write("\n")
    
    if (anisotropicTextureName != ""):
        pbrt_file.write(r'"texture %s" "%s"' % ("anisotropic", anisotropicTextureName))
    else :
        pbrt_file.write(r'"float anisotropic" [%s]' %(nodes["Pbrt Disney"].anisotropic))
    pbrt_file.write("\n")

    if (sheenTextureName != ""):
        pbrt_file.write(r'"texture %s" "%s"' % ("sheen", sheenTextureName))
    else :
        pbrt_file.write(r'"float sheen" [%s]' %(nodes["Pbrt Disney"].sheen))
    pbrt_file.write("\n")

    if (sheenTintTextureName != ""):
        pbrt_file.write(r'"texture %s" "%s"' % ("sheentint", sheenTintTextureName))
    else :
        pbrt_file.write(r'"float sheentint" [%s]' %(nodes["Pbrt Disney"].sheenTint))
    pbrt_file.write("\n")
    
    if (clearCoatTextureName != ""):
        pbrt_file.write(r'"texture %s" "%s"' % ("clearcoat", clearCoatTextureName))
    else :
        pbrt_file.write(r'"float clearcoat" [%s]' %(nodes["Pbrt Disney"].clearCoat))
    pbrt_file.write("\n")

    if (clearCoatGlossTextureName != ""):
        pbrt_file.write(r'"texture %s" "%s"' % ("clearcoatgloss", clearCoatGlossTextureName))
    else :
        pbrt_file.write(r'"float clearcoatgloss" [%s]' %(nodes["Pbrt Disney"].clearCoatGloss))
    pbrt_file.write("\n")

    if (specTransTextureName != ""):
        pbrt_file.write(r'"texture %s" "%s"' % ("spectrans", specTransTextureName))
    else :
        pbrt_file.write(r'"float spectrans" [%s]' %(nodes["Pbrt Disney"].specTrans))
    pbrt_file.write("\n")

    if (flatnessTextureName != ""):
        pbrt_file.write(r'"texture %s" "%s"' % ("flatness", flatnessTextureName))
    else :
        pbrt_file.write(r'"float flatness" [%s]' %(nodes["Pbrt Disney"].flatness))
    pbrt_file.write("\n")
    
    if (diffTransTextureName != ""):
        pbrt_file.write(r'"texture %s" "%s"' % ("difftrans", diffTransTextureName))
    else :
        pbrt_file.write(r'"float difftrans" [%s]' %(nodes["Pbrt Disney"].diffTrans))
    pbrt_file.write("\n")

    #TODO: scatter distance causes crash for some stupid reason.
    #r = nodes["Pbrt Disney"].inputs[11].default_value[0]
    #g = nodes["Pbrt Disney"].inputs[11].default_value[1]
    #b = nodes["Pbrt Disney"].inputs[11].default_value[2]
    #pbrt_file.write(r'"color scatterdistance" [%s %s %s]' %(r,g,b))
    #pbrt_file.write("\n")
    return ''

    # https://blender.stackexchange.com/questions/80773/how-to-get-the-name-of-image-of-image-texture-with-python

def export_pbrt_blackbody_material (pbrt_file, mat):
    print('Currently exporting Pbrt BlackBody material')
    print (mat.name)
    nodes = mat.node_tree.nodes
    pbrt_file.write(r'AreaLightSource "diffuse" "blackbody L" [%s ' %(nodes["Pbrt BlackBody"].Temperature))
    pbrt_file.write(r'%s]' %(nodes["Pbrt BlackBody"].Lambda))
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
        pbrt_file.write(r'Texture "%s" "color" "imagemap" "string filename" ["%s"]' % (image.name, ("textures/" + image.name))) #.replace("\\","/")
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
def export_material(pbrt_file, object):
    # https://blender.stackexchange.com/questions/51782/get-material-and-color-of-material-on-a-face-of-an-object-in-python
    # https://blender.stackexchange.com/questions/36587/how-to-define-customized-property-in-material

    #context = bpy.context
    #obj = context.object
    print("Material slots:")
    print(len(object.material_slots))
    if len(object.material_slots) == 0:
        print("no material on object")
        return ''

    mat = object.data.materials[0]
    print ('Exporting material named: ',mat.name)
    #nodes = mat.node_tree.nodes
    global hastexture
    hastexture = False
    #textureName = ""
    # check if this code can be used so get the socket the image is plugged into:
    # https://blender.stackexchange.com/questions/77365/getting-the-image-of-a-texture-node-that-feeds-into-a-node-group

    #   Begin new texture code


    #Later we should loop through all 'slots' to write out all materials applied.

    mat = object.material_slots[0].material #Get the material from the material slot you want
    print ('Fetched material in slot 0 named: ',mat.name)
    if mat and mat.use_nodes: #if it is using nodes
        print('Mat name: ', mat.name)
        print ('mat.node_tree.nodes[0].name:', mat.node_tree.nodes[0].name)
        print ('mat.node_tree.nodes[1].name:', mat.node_tree.nodes[1].name)

        if mat.node_tree.nodes[1].name == 'Pbrt Matte':
            export_pbrt_matte_material(pbrt_file,mat)

        if mat.node_tree.nodes[1].name == 'Pbrt Glass':
             export_pbrt_glass_material(pbrt_file,mat)

        if mat.node_tree.nodes[1].name == 'Pbrt Subsurface':
            export_pbrt_subsurface_material(pbrt_file,mat)

        if mat.node_tree.nodes[1].name == 'Pbrt Uber':
            export_pbrt_uber_material(pbrt_file,mat)

        if mat.node_tree.nodes[1].name == 'Pbrt Metal':
            export_pbrt_metal_material(pbrt_file,mat)

        if mat.node_tree.nodes[1].name == 'Pbrt Substrate':
            export_pbrt_substrate_material(pbrt_file,mat)

        if mat.node_tree.nodes[1].name == 'Pbrt Plastic':
            export_pbrt_plastic_material(pbrt_file,mat)

        if mat.node_tree.nodes[1].name == 'Pbrt Disney':
            export_pbrt_disney_material(pbrt_file,mat)

        if mat.node_tree.nodes[1].name == 'Pbrt BlackBody':
            export_pbrt_blackbody_material(pbrt_file,mat)

        if mat.node_tree.nodes[1].name == 'Pbrt Mirror':
            export_pbrt_mirror_material(pbrt_file,mat)

        if mat.node_tree.nodes[1].name == 'Principled BSDF':
            export_principled_bsdf_material(pbrt_file,mat)

        if mat.node_tree.nodes[1].name == 'Pbrt Translucent':
            export_pbrt_translucent_material(pbrt_file,mat)

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


def export_geometry(pbrt_file, scene):
    
    # We now export the mesh as pbrt's triangle meshes.
    # Development documentation :
    # https://docs.blender.org/api/current/bpy.types.MeshLoopTriangle.html
    # https://wiki.blender.org/wiki/Reference/Release_Notes/2.80/Python_API/Mesh_API

    for object in scene.objects:
        print("exporting:")
        print(object.name)

        if object is not None and object.type != 'CAMERA' and object.type == 'MESH':
            
            # Going into edit mode first, then object mode seems to internally update the mesh.
            # This is to prevent a bug where the indicies are messed up, need to be investigated more later on.
            #bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.object.mode_set(mode='OBJECT')

            print('exporting object: ' + object.name)
            pbrt_file.write("AttributeBegin\n")
            pbrt_file.write( "Transform [" + matrixtostr( object.matrix_world.transposed() ) + "]\n" )
            
            export_material(pbrt_file, object)
            #bpy.context.scene.update()
            bpy.context.view_layer.update()

            object.data.update()
            mesh = object.data

            if not mesh.loop_triangles and mesh.polygons:
                mesh.calc_loop_triangles()

            pbrt_file.write( "Shape \"trianglemesh\"\n")

            pbrt_file.write( '\"point P\" [\n' )
            for tri in mesh.loop_triangles:
                for vert_index in tri.vertices:
                    pbrt_file.write("%s %s %s\n" % (mesh.vertices[vert_index].co.x, mesh.vertices[vert_index].co.y, mesh.vertices[vert_index].co.z))
            pbrt_file.write( "]\n" )
            
            mesh.calc_normals_split()
            pbrt_file.write( "\"normal N\" [\n" )
            for tri in mesh.loop_triangles:
                for vert_index in tri.split_normals:
                    pbrt_file.write("%s %s %s\n" % (vert_index[0],vert_index[1],vert_index[2]))
            pbrt_file.write( "]\n" )
            
            pbrt_file.write( "\"float st\" [\n" )
            for uv_layer in mesh.uv_layers:
                for tri in mesh.loop_triangles:
                    for loop_index in tri.loops:
                        pbrt_file.write("%s %s \n" % (uv_layer.data[loop_index].uv[0], uv_layer.data[loop_index].uv[1]))
            pbrt_file.write( "]\n" )

            pbrt_file.write( "\"integer indices\" [\n" )
            faceIndex = 0
            for tri in mesh.loop_triangles:
                for vert_index in tri.vertices:
                    pbrt_file.write("%s " % (faceIndex))
                    faceIndex +=1
                pbrt_file.write("\n")
            pbrt_file.write( "]\n" )
                
            pbrt_file.write("AttributeEnd\n\n")

    return ''

def export_dummymesh(pbrt_file):
    pbrt_file.write(r'AttributeBegin')
    pbrt_file.write("\n")
    pbrt_file.write(r'Material "plastic"')
    pbrt_file.write("\n")
    pbrt_file.write(r'"color Kd" [.1 .1 .1]')
    pbrt_file.write("\n")
    pbrt_file.write(r'"color Ks" [.7 .7 .7] "float roughness" .1')
    pbrt_file.write("\n")
    pbrt_file.write(r'Translate 0 0 0')
    pbrt_file.write("\n")
    pbrt_file.write(r'Shape "trianglemesh"')
    pbrt_file.write("\n")
    pbrt_file.write(r'"point P" [ -1000 -1000 0   1000 -1000 0   1000 1000 0 -1000 1000 0 ]')
    pbrt_file.write("\n")
    pbrt_file.write(r'"integer indices" [ 0 1 2 2 3 0]')
    pbrt_file.write("\n")
    pbrt_file.write("AttributeEnd")
    pbrt_file.write("\n\n")
    return ''

def export_pbrt(filepath, scene , frameNumber):
    out = os.path.join(filepath, "test" + frameNumber +".pbrt")
    if not os.path.exists(filepath):
        print('Output directory did not exist, creating: ')
        print(filepath)
        os.makedirs(filepath)

    with open(out, 'w') as pbrt_file:
        createDefaultExportDirectories(pbrt_file,scene)
        export_film(pbrt_file, frameNumber)
        export_sampler(pbrt_file)
        export_integrator(pbrt_file,scene)
        export_camera(pbrt_file)
        world_begin(pbrt_file)
        export_EnviromentMap(pbrt_file)
        #export_environmentLight(pbrt_file)
        print('Begin export lights:')
        export_point_lights(pbrt_file,scene)
        export_spot_lights(pbrt_file,scene)
        print('End export lights.')
        export_geometry(pbrt_file,scene)
        #export_dummymesh(pbrt_file)
        world_end(pbrt_file)
        pbrt_file.close()
