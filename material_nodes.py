import bpy
from bpy.types import NodeTree, Node, NodeSocket
import nodeitems_utils
from nodeitems_utils import (
    NodeCategory,
    NodeItem,
    NodeItemCustom,
)

class MyNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        # Prevent the shaders from showing up if PBRT is not selected as current renderer.
        engine = context.scene.render.engine
        if engine != 'Pbrt_v4_renderer':
            return False
        else:
            b = False
            if context.space_data.tree_type == 'ShaderNodeTree': b = True
            return b

pbrt_v4_shader_categories = [
    MyNodeCategory("PBRT_V4_SHADER", "PBRT-V4", items=[
        NodeItem("Pbrt_V4_Diffuse"),
        NodeItem("Pbrt_V4_CoatedDiffuse"),
        NodeItem("Pbrt_V4_Subsurface"),
        NodeItem("Pbrt_V4_DiffuseTransmission"),
        NodeItem("Pbrt_V4_Dielectric"),
        NodeItem("Pbrt_V4_Mix"),
        NodeItem("Pbrt_V4_Conductor"),
        NodeItem("Pbrt_V4_Thin_Dielectric"),
        NodeItem("Pbrt_V4_Coated_Conductor"),
        NodeItem("Pbrt_V4_Measured")
        ]),
    ]

class MyCustomTree(NodeTree):
    bl_idname = 'CustomTreeType'
    bl_label = 'Custom Node Tree'
    bl_icon = 'NODETREE'

# Defines a poll function to enable filtering for various node tree types.
class MyCustomTreeNode :
    bl_icon = 'INFO'
    @classmethod
    def poll(cls, ntree):
        b = False
        # Make your node appear in different node trees by adding their bl_idname type here.
        if ntree.bl_idname == 'ShaderNodeTree': b = True
        return b


class Pbrt_V4_Diffuse(Node, MyCustomTreeNode):
    '''A custom node'''
    bl_idname = 'Pbrt_V4_Diffuse'
    bl_label = 'Pbrt V4 Diffuse'
    bl_icon = 'INFO'
    show_texture = True

    def updateViewportColor(self,context):
        mat = bpy.context.active_object.active_material
        if mat is not None:
            bpy.data.materials[mat.name].diffuse_color=self.reflectance
    

    def init(self, context):
        self.outputs.new('NodeSocketFloat', "Pbrt V4 Diffuse")
        Reflectance = self.inputs.new('NodeSocketColor', "Reflectance")
        Reflectance.default_value = (0.8, 0.8, 0.8, 1.0)
        
        sigma = self.inputs.new('NodeSocketFloat', "sigma")
        sigma.default_value = 0.0
        
        displacementTexture = self.inputs.new('NodeSocketColor', "displacement texture")
        displacementTexture.hide_value = True

    def draw_buttons(self, context, layout):
        layout.prop(self, "Sigma",text = 'Sigma')
        layout.prop(self, "reflectance",text = 'reflectance')
        
    def draw_label(self):
        return "Pbrt V4 Diffuse"

class Pbrt_V4_CoatedDiffuse(Node, MyCustomTreeNode):
    '''A custom node'''
    bl_idname = 'Pbrt_V4_CoatedDiffuse'
    bl_label = 'Pbrt V4 CoatedDiffuse'
    bl_icon = 'INFO'
    show_texture = True

    def updateViewportColor(self,context):
        mat = bpy.context.active_object.active_material
        if mat is not None:
            bpy.data.materials[mat.name].diffuse_color=self.reflectance

    #maxdepth : bpy.props.FloatProperty(default=1.5, min=0.0, max=9999.0)
    #nsamples : bpy.props.FloatProperty(default=1.5, min=0.0, max=9999.0)
    twosided : bpy.props.BoolProperty(name="twosided", description="twosided.", default = False)
    remaproughness : bpy.props.BoolProperty(name="remaproughness", description="remaproughness.", default = True)

    def init(self, context):
        self.outputs.new('NodeSocketFloat', "Pbrt V4 CoatedDiffuse")

        reflectance = self.inputs.new('NodeSocketColor', "Reflectance")
        reflectance.default_value = (0.8, 0.8, 0.8, 1.0)

        vRoughness = self.inputs.new('NodeSocketFloat', "VRoughness")
        vRoughness.default_value = 0
        
        uRoughness = self.inputs.new('NodeSocketFloat', "URoughness")
        uRoughness.default_value = 0

        thickness = self.inputs.new('NodeSocketFloat', "thickness")
        thickness.default_value = 0.1

        eta = self.inputs.new('NodeSocketFloat', "eta")
        eta.default_value = 1.5

        displacementTexture = self.inputs.new('NodeSocketColor', "displacement texture")
        displacementTexture.hide_value = True

    def draw_buttons(self, context, layout):
        layout.prop(self, "reflectance",text = 'reflectance')
        layout.prop(self, "roughness",text = 'roughness')
        layout.prop(self, "thickness",text = 'thickness')
        layout.prop(self, "eta",text = 'eta')
        #layout.prop(self, "maxdepth",text = 'maxdepth')
        #layout.prop(self, "nsamples",text = 'nsamples')
        layout.prop(self, "twosided",text = 'twosided')
        
    def draw_label(self):
        return "Pbrt V4 CoatedDiffuse"


class Pbrt_V4_Subsurface(Node, MyCustomTreeNode):
    '''A custom node'''
    bl_idname = 'Pbrt_V4_Subsurface'
    bl_label = 'Pbrt V4 Subsurface'
    bl_icon = 'INFO'
    show_texture = True

    presetName : bpy.props.EnumProperty(
        name='Preset name',
        description='Preset name',
        items=[
            ('None', 'None', ''),
            ('Apple', 'Apple', ''),
            ('Chicken1', 'Chicken1', ''),
            ('Chicken2', 'Chicken2', ''),
            ('Cream', 'Cream', ''),
            ('Ketchup', 'Ketchup', ''),
            ('Marble', 'Marble', ''),
            ('Potato', 'Potato', ''),
            ('Skimmilk', 'Skimmilk', ''),
            ('Skin1', 'Skin1', ''),
            ('Skin2', 'Skin2', ''),
            ('Spectralon', 'Spectralon', ''),
            ('Wholemilk', 'Wholemilk', ''),
            ('Lowfat Milk', 'Lowfat Milk', ''),
            ('Reduced Milk', 'Reduced Milk', ''),
            ('Regular Milk', 'Regular Milk', ''),
            ('Espresso', 'Espresso', ''),
            ('Mint Mocha Coffee', 'Mint Mocha Coffee', ''),
            ('Lowfat Soy Milk', 'Lowfat Soy Milk', ''),
            ('Regular Soy Milk', 'Regular Soy Milk', ''),
            ('Lowfat Chocolate Milk', 'Lowfat Chocolate Milk', ''),
            ('Regular Chocolate Milk', 'Regular Chocolate Milk', ''),
            ('Coke', 'Coke', ''),
            ('Pepsi', 'Pepsi', ''),
            ('Sprite', 'Sprite', ''),
            ('Gatorade', 'Gatorade', ''),
            ('Chardonnay', 'Chardonnay', ''),
            ('White Zinfandel', 'White Zinfandel', ''),
            ('Merlot', 'Merlot', ''),
            ('Budweiser Beer', 'Budweiser Beer', ''),
            ('Coors Light Beer', 'Coors Light Beer', ''),
            ('Clorox', 'Clorox', ''),
            ('Apple Juice', 'Apple Juice', ''),
            ('Cranberry Juice', 'Cranberry Juice', ''),
            ('Grape Juice', 'Grape Juice', ''),
            ('Ruby Grapefruit Juice', 'Ruby Grapefruit Juice', ''),
            ('White Grapefruit Juice', 'White Grapefruit Juice', ''),
            ('Shampoo', 'Shampoo', ''),
            ('Strawberry Shampoo', 'Strawberry Shampoo', ''),
            ('Head & Shoulders Shampoo', 'Head & Shoulders Shampoo', ''),
            ('Lemon Tea Powder', 'Lemon Tea Powder', ''),
            ('Orange Powder', 'Orange Powder', ''),
            ('Pink Lemonade Powder', 'Pink Lemonade Powder', ''),
            ('Cappuccino Powder', 'Cappuccino Powder', ''),
            ('Salt Powder', 'Salt Powder', ''),
            ('Sugar Powder', 'Sugar Powder', ''),
            ('Suisse Mocha Powder', 'Suisse Mocha Powder', ''),
            ('Pacific Ocean Surface Water', 'Pacific Ocean Surface Water', '')
        ],
        default='None',
    )

    remaproughness : bpy.props.BoolProperty(name="remaproughness", description="remaproughness.", default = True)
    g : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    eta : bpy.props.FloatProperty(default=1.33, min=0.0, max=9999.0)
    scale : bpy.props.FloatProperty(default=1.0, min=0.0, max=9999.0)
    roughness: bpy.props.FloatProperty(default=0.0, min=0.0, max=9999.0)

    def init(self, context):
        self.outputs.new('NodeSocketFloat', "Pbrt V4 Subsurface")

        mfpTexture = self.inputs.new('NodeSocketColor', "mfp texture")
        mfpTexture.hide_value = True    
        
        reflectance = self.inputs.new('NodeSocketColor', "reflectance")
        reflectance.default_value = (0.0011, 0.0024, 0.014, 1.0)

        Sigma_a = self.inputs.new('NodeSocketColor', "sigma a")
        Sigma_a.default_value = (0.0011, 0.0024, 0.014, 1.0)

        Sigma_s = self.inputs.new('NodeSocketColor', "sigma s")
        Sigma_s.default_value= (2.55, 3.21, 3.77, 1.0)

        eta = self.inputs.new('NodeSocketFloat', "eta")
        eta.default_value=1.5

        displacementTexture = self.inputs.new('NodeSocketColor', "displacement texture")
        displacementTexture.hide_value = True
        
        uroughness = self.inputs.new('NodeSocketFloat', "uroughness")
        uroughness.default_value = 0.0

        vroughness = self.inputs.new('NodeSocketFloat', "vroughness")
        vroughness.default_value = 0.0
        medium = self.inputs.new('NodeSocketFloat', "medium")
        medium.hide_value = True

    def draw_buttons(self, context, layout):
        layout.prop(self, "presetName", text = 'preset Name')
        layout.prop(self, "roughness",text = 'roughness')
        layout.prop(self, "Sigma",text = 'Sigma')
        layout.prop(self, "g",text = 'g')
        layout.prop(self, "remaproughness",text = 'remaproughness')
        layout.prop(self, "scale",text = 'scale')
        

    def draw_label(self):
        return "Pbrt V4 Subsurface"

class Pbrt_V4_DiffuseTransmission(Node, MyCustomTreeNode):
    '''A custom node'''
    bl_idname = 'Pbrt_V4_DiffuseTransmission'
    bl_label = 'Pbrt V4 DiffuseTransmission'
    bl_icon = 'INFO'
    show_texture = True

    remaproughness : bpy.props.BoolProperty(name="remaproughness", description="remaproughness.", default = True)
    scale : bpy.props.FloatProperty(default=1.0, min=0.0, max=9999.0)

    def init(self, context):
        self.outputs.new('NodeSocketFloat', "Pbrt V4 DiffuseTransmission")
        
        reflectance = self.inputs.new('NodeSocketColor', "Reflectance")
        reflectance.default_value = (0.8, 0.8, 0.8, 1.0)

        displacementTexture = self.inputs.new('NodeSocketColor', "displacement texture")
        displacementTexture.hide_value = True

        Sigma = self.inputs.new('NodeSocketFloat', "Sigma")
        Sigma.default_value = (0.0)

    def draw_buttons(self, context, layout):
        layout.prop(self, "remaproughness",text = 'remaproughness')
        layout.prop(self, "Sigma",text = 'Sigma')
        layout.prop(self, "reflectance",text = 'reflectance')
        layout.prop(self, "scale",text = 'scale')
        
    def draw_label(self):
        return "Pbrt V4 DiffuseTransmission"

class Pbrt_V4_Dielectric(Node, MyCustomTreeNode):
    '''A custom node'''
    bl_idname = 'Pbrt_V4_Dielectric'
    bl_label = 'Pbrt V4 Dielectric'
    bl_icon = 'INFO'
    show_texture = True

    remaproughness : bpy.props.BoolProperty(name="remaproughness", description="remaproughness.", default = True)
    scale : bpy.props.FloatProperty(default=1.0, min=0.0, max=9999.0)
    

    def init(self, context):
        self.outputs.new('NodeSocketFloat', "Pbrt V4 Dielectric")
        
        eta = self.inputs.new('NodeSocketFloat', "eta")
        eta.default_value = 1.5
        
        vRoughness = self.inputs.new('NodeSocketFloat', "VRoughness")
        vRoughness.default_value = 0
        
        uRoughness = self.inputs.new('NodeSocketFloat', "URoughness")
        uRoughness.default_value = 0
 
    def draw_buttons(self, context, layout):
        layout.prop(self, "remaproughness",text = 'remaproughness')
        layout.prop(self, "scale",text = 'scale')

    def draw_label(self):
        return "Pbrt V4 Dielectric"

class Pbrt_V4_Mix(Node, MyCustomTreeNode):
    '''A custom node'''
    bl_idname = 'Pbrt_V4_Mix'
    bl_label = 'Pbrt V4 Mix'
    bl_icon = 'INFO'
    show_texture = True

    def init(self, context):
        self.outputs.new('NodeSocketFloat', "Pbrt V4 Mix")
        amount = self.inputs.new('NodeSocketFloat', "amount")
        amount.default_value = (0.5)
        material1 = self.inputs.new('NodeSocketColor', "material1")
        material1.hide_value = True
        material2 = self.inputs.new('NodeSocketColor', "material2")
        material2.hide_value = True

    def draw_label(self):
        return "Pbrt V4 Mix"
            
class Pbrt_V4_Conductor(Node, MyCustomTreeNode):
    '''A custom node'''
    bl_idname = 'Pbrt_V4_Conductor'
    bl_label = 'Pbrt V4 Conductor'
    bl_icon = 'INFO'
    show_texture = True

    remaproughness : bpy.props.BoolProperty(name="remaproughness", description="remaproughness.", default = True)
    scale : bpy.props.FloatProperty(default=1.0, min=0.0, max=9999.0)
    

    def init(self, context):
        self.outputs.new('NodeSocketFloat', "Pbrt V4 Conductor")
        
        eta = self.inputs.new('NodeSocketFloat', "eta")
        eta.default_value = 1.5
        
        k = self.inputs.new('NodeSocketColor', "k")
        k.default_value = (0.8, 0.8, 0.8, 1.0)

        vRoughness = self.inputs.new('NodeSocketFloat', "VRoughness")
        vRoughness.default_value = 0
        
        uRoughness = self.inputs.new('NodeSocketFloat', "URoughness")
        uRoughness.default_value = 0
        
        displacementTexture = self.inputs.new('NodeSocketColor', "displacement texture")
        displacementTexture.hide_value = True

    def draw_buttons(self, context, layout):
        layout.prop(self, "remaproughness",text = 'remaproughness')
        layout.prop(self, "scale",text = 'scale')

    def draw_label(self):
        return "Pbrt V4 Conductor"

class Pbrt_V4_Thin_Dielectric(Node, MyCustomTreeNode):
    '''A custom node'''
    bl_idname = 'Pbrt_V4_Thin_Dielectric'
    bl_label = 'Pbrt V4 Thin Dielectric'
    bl_icon = 'INFO'
    show_texture = True

    def init(self, context):
        self.outputs.new('NodeSocketFloat', "Pbrt V4 Thin Dielectric")

        eta = self.inputs.new('NodeSocketFloat', "eta")
        eta.default_value = 1.5

        #etaF = self.inputs.new('NodeSocketFloat', "etaF")
        #etaF.default_value = 0.0

        #etaS = self.inputs.new('NodeSocketFloat', "etaS")
        #etaS.default_value = 0.0

        #vRoughness = self.inputs.new('NodeSocketFloat', "VRoughness")
        #vRoughness.default_value = 0
        
        #uRoughness = self.inputs.new('NodeSocketFloat', "URoughness")
        #uRoughness.default_value = 0
        
        displacementTexture = self.inputs.new('NodeSocketColor', "displacement texture")
        displacementTexture.hide_value = True

    #def draw_buttons(self, context, layout):

    def draw_label(self):
        return "Pbrt V4 Thin Dielectric"

class Pbrt_V4_Coated_Conductor(Node, MyCustomTreeNode):
    '''A custom node'''
    bl_idname = 'Pbrt_V4_Coated_Conductor'
    bl_label = 'Pbrt V4 Coated Conductor'
    bl_icon = 'INFO'
    show_texture = True

    remaproughness : bpy.props.BoolProperty(name="remaproughness", description="remaproughness.", default = True)
    thickness : bpy.props.FloatProperty(default=1.0, min=0.0, max=9999.0)
    

    def init(self, context):
        self.outputs.new('NodeSocketFloat', "Pbrt V4 Coated Conductor")
        
        eta = self.inputs.new('NodeSocketFloat', "eta")
        eta.default_value = 1.5

        k = self.inputs.new('NodeSocketFloat', "k")
        k.default_value = 1.5

        interfaceVRoughness = self.inputs.new('NodeSocketFloat', "interfaceVRoughness")
        interfaceVRoughness.default_value = 0

        interfaceURoughness = self.inputs.new('NodeSocketFloat', "interfaceURoughness")
        interfaceURoughness.default_value = 0

        conductorVRoughness = self.inputs.new('NodeSocketFloat', "conductorVRoughness")
        conductorVRoughness.default_value = 0
        
        conductorURoughness = self.inputs.new('NodeSocketFloat', "conductorURoughness")
        conductorURoughness.default_value = 0
        
        displacementTexture = self.inputs.new('NodeSocketColor', "displacement texture")
        displacementTexture.hide_value = True

    def draw_buttons(self, context, layout):
        layout.prop(self, "remaproughness",text = 'remaproughness')
        layout.prop(self, "thickness",text = 'thickness')

    def draw_label(self):
        return "Pbrt V4 Coated Conductor"

class Pbrt_V4_Measured(Node, MyCustomTreeNode):
    '''A custom node'''
    bl_idname = 'Pbrt_V4_Measured'
    bl_label = 'Pbrt V4 Measured'
    bl_icon = 'INFO'
    show_texture = True

    def init(self, context):
        self.outputs.new('NodeSocketFloat', "Pbrt V4 Measured")
        measurement = self.inputs.new('NodeSocketFloat', "Measurement file")
        measurement.hide_value = True

        displacementTexture = self.inputs.new('NodeSocketColor', "displacement texture")
        displacementTexture.hide_value = True

    def draw_label(self):
        return "Pbrt V4 Measured"

def register():
    nodeitems_utils.register_node_categories("CUSTOM_NODES", pbrt_v4_shader_categories)

def unregister():
    nodeitems_utils.unregister_node_categories("CUSTOM_NODES")