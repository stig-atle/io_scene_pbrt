#NOTE: Run this code first then use SHIFT-A, below, to add Custom Float node type.

import bpy
from bpy.types import NodeTree, Node, NodeSocket
import nodeitems_utils
from nodeitems_utils import (
    NodeCategory,
    NodeItem,
    NodeItemCustom,
)

#nodecategory begin
class MyNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        b = False
        # Make your node appear in different node trees by adding their bl_idname type here.
        if context.space_data.tree_type == 'ShaderNodeTree': b = True
        return b

# all categories in a list
node_categories = [
    # identifier, label, items list
    #MyNodeCategory("SOMENODES", "PBRT", items=[
    MyNodeCategory("SHADER", "PBRT", items=[
        NodeItem("CustomNodeType"),
        NodeItem("CustomNodeTypeMirror"),
        NodeItem("CustomNodeTypeGlass"),
        NodeItem("CustomNodeTypeDisney"),
        NodeItem("CustomNodeTypeMetal"),
        NodeItem("CustomNodeTypeUber"),
        NodeItem("CustomNodeTypeSubsurface"),
        NodeItem("CustomNodeTypeSubstrate"),
        NodeItem("CustomNodeTypePlastic"),
        NodeItem("CustomNodeTypeBlackBody"),
        NodeItem("CustomNodeTypeMedium"),
        ]),
    ]

#nodecategory end


# Implementation of custom nodes from Python
# Derived from the NodeTree base type, similar to Menu, Operator, Panel, etc.
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

# Derived from the Node base type.
class PbrtMatte(Node, MyCustomTreeNode):
    '''A custom node'''
    bl_idname = 'CustomNodeType'
    bl_label = 'Pbrt Matte'
    bl_icon = 'INFO'

    def update_value(self, context):
        #self.outputs["Pbrt Matte"].default_value = self.some_value
        self.update ()

    Sigma : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)

    def init(self, context):
        self.outputs.new('NodeSocketFloat', "Pbrt Matte")
        self.inputs.new('NodeSocketColor', "Kd")
        
    def update(self):
        print('Updating matte props..')
        try:
            #this.diffuse_color = this.Kd
            #out = self.outputs["Pbrt Matte"]
            can_continue = True
        except:
            can_continue = False
        if can_continue:
            print("continues in update rutine.")
            #if out.is_linked:
                # I am an ouput node that is linked, try to update my link.
            #    for o in out.links:
            #        if o.is_valid:
            #            o.to_socket.node.inputs[o.to_socket.name].default_value = self.outputs["Pbrt Matte"].default_value   #self.some_value

    def draw_buttons(self, context, layout):
        layout.prop(self, "Sigma",text = 'Sigma')
        #layout.prop(self, "Kd",text = 'Kd')
    
    def draw_buttons_ext(self, context, layout):
        layout.prop(self, "Sigma",text = 'Sigma')
        
    def draw_label(self):
        return "Pbrt Matte"

class PbrtMirror(Node, MyCustomTreeNode):
    bl_idname = 'CustomNodeTypeMirror'
    bl_label = 'Pbrt Mirror'
    bl_icon = 'INFO'

    def update_value(self, context):
        self.update ()

    #uRoughness = bpy.props.FloatProperty(name="uRoughness", default=0.0, min=0.0, max=1.0)
    #vRoughness = bpy.props.FloatProperty(name="vRoughness", default=0.0, min=0.0, max=1.0)
    Index : bpy.props.FloatProperty(name="Index", default=1.333, min=0.0, max=100.0)

    def init(self, context):
        self.inputs.new('NodeSocketColor', "Kr")
		#should have bumpmap also
        self.outputs.new('NodeSocketFloat', "Pbrt Mirror")

    def update(self):
        try:
            out = self.outputs["Pbrt Mirror"]
            can_continue = True
        except:
            can_continue = False
        if can_continue:
            if out.is_linked:
                print("continues in update rutine.")

    # Additional buttons displayed on the node.
    #def draw_buttons(self, context, layout):
        #layout.prop(self, "Index",text='Index')

    # Optional: custom label
    # Explicit user label overrides this, but here we can define a label dynamically.
    def draw_label(self):
        return "Pbrt Mirror"

class PbrtGlass(Node, MyCustomTreeNode):
    bl_idname = 'CustomNodeTypeGlass'
    bl_label = 'Pbrt Glass'
    bl_icon = 'INFO'

    def update_value(self, context):
        self.update ()

    uRoughness : bpy.props.FloatProperty(name="uRoughness", default=0.0, min=0.0, max=1.0)
    vRoughness : bpy.props.FloatProperty(name="vRoughness", default=0.0, min=0.0, max=1.0)
    Index : bpy.props.FloatProperty(name="Index", default=1.333, min=0.0, max=100.0)

    def init(self, context):
        uRoughnessTexture_node = self.inputs.new('NodeSocketColor', "u roughness texture")
        uRoughnessTexture_node.hide_value = True
        vRoughnessTexture_node = self.inputs.new('NodeSocketColor', "v roughness texture")
        vRoughnessTexture_node.hide_value = True
        self.inputs.new('NodeSocketColor', "Kr")
        self.inputs.new('NodeSocketColor', "Kt")
        self.outputs.new('NodeSocketFloat', "Pbrt Glass")
        
        medium_node = self.inputs.new('NodeSocketColor', "medium")
        medium_node.hide_value = True


    def update(self):
        try:
            out = self.outputs["Pbrt Glass"]
            can_continue = True
        except:
            can_continue = False
        if can_continue:
            if out.is_linked:
                print("continues in update rutine.")

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):
        layout.prop(self, "Index",text='Index')
        layout.prop(self, "uRoughness",text = 'uRoughness')
        layout.prop(self, "vRoughness",text = 'vRoughness')


    # Optional: custom label
    # Explicit user label overrides this, but here we can define a label dynamically.
    def draw_label(self):
        return "Pbrt Glass"

class PbrtDisney(Node, MyCustomTreeNode):
    bl_idname = 'CustomNodeTypeDisney'
    bl_label = 'Pbrt Disney'
    bl_icon = 'INFO'

    def update_value(self, context):
        self.update ()

    #Kr : bpy.props.FloatVectorProperty(name='Kr', description='Kr', subtype='COLOR',  min=0.0, max=1.0, default=(0.8, 0.8, 0.8))
    #Kt : bpy.props.FloatVectorProperty(name='Kt', description='Kt', subtype='COLOR',  min=0.0, max=1.0, default=(0.8, 0.8, 0.8))
    #uRoughness : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    #color : bpy.props.FloatVectorProperty(name='color', description='color', subtype='COLOR',  min=0.0, max=1.0, default=(0.8, 0.8, 0.8))
    metallic : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    eta : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    roughness : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    specularTint : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    anisotropic : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    sheen : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    sheenTint : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    clearCoat : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    clearcoatGloss : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    specTrans : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    #scatterDistance : bpy.props.FloatVectorProperty(name='color', description='color', subtype='COLOR',  min=0.0, max=1.0, default=(0.8, 0.8, 0.8))
    flatness : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    diffTrans : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)

    def init(self, context):
        self.outputs.new('NodeSocketFloat', "Pbrt Disney")
        self.inputs.new('NodeSocketColor', "color")
        self.inputs.new('NodeSocketColor', "scatterDistance")

    def update(self):
        try:
            out = self.outputs["Pbrt Disney"]
            can_continue = True
        except:
            can_continue = False
        if can_continue:
            if out.is_linked:
                print("continues in update rutine.")

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):
        #layout.prop(self, "color",text = 'color')
        layout.prop(self, "metallic",text = 'metallic')
        layout.prop(self, "eta",text = 'eta')
        layout.prop(self, "roughness",text = 'roughness')
        layout.prop(self, "specularTint",text = 'specularTint')
        layout.prop(self, "anisotropic",text = 'anisotropic')
        layout.prop(self, "sheen",text = 'sheen')
        layout.prop(self, "sheenTint",text = 'sheenTint')
        layout.prop(self, "clearCoat",text = 'clearCoat')
        layout.prop(self, "clearcoatGloss",text = 'clearcoatGloss')
        layout.prop(self, "specTrans",text = 'specTrans')
        #layout.prop(self, "scatterDistance",text = 'scatterDistance')
        layout.prop(self, "flatness",text = 'flatness')
        layout.prop(self, "diffTrans",text = 'diffTrans')
        

    # Optional: custom label
    # Explicit user label overrides this, but here we can define a label dynamically.
    def draw_label(self):
        return "Pbrt Disney"

class PbrtMetal(Node, MyCustomTreeNode):
    bl_idname = 'CustomNodeTypeMetal'
    bl_label = 'Pbrt Metal'
    bl_icon = 'INFO'
    def update_value(self, context):
        self.update ()
        
    #color_eta : bpy.props.FloatVectorProperty(name='color', description='color', subtype='COLOR',  min=0.0, max=1.0, default=(0.8, 0.8, 0.8))
    #color : bpy.props.FloatVectorProperty(name='color', description='color', subtype='COLOR',  min=0.0, max=1.0, default=(0.8, 0.8, 0.8))
    roughness : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    uRoughness : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    vRoughness : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    bump : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    
    def init(self, context):
        self.outputs.new('NodeSocketFloat', "Pbrt Metal")
        color_eta = self.inputs.new('NodeSocketColor', "color_eta")
        color_node = self.inputs.new('NodeSocketColor', "color")
        uRoughnessTexture_node = self.inputs.new('NodeSocketColor', "u roughness texture")
        uRoughnessTexture_node.hide_value=True
        vRoughnessTexture_node = self.inputs.new('NodeSocketColor', "v roughness texture")
        vRoughnessTexture_node.hide_value=True
        bumpTexture_node = self.inputs.new('NodeSocketColor', "bump texture")
        bumpTexture_node.hide_value=True
    def update(self):
        try:
            out = self.outputs["Pbrt Metal"]
            can_continue = True
        except:
            can_continue = False
        if can_continue:
            if out.is_linked:
                print("continues in update rutine.")
    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):
        #layout.prop(self, "color_eta",text = 'color_eta')
        #layout.prop(self, "color",text = 'color')
        layout.prop(self, "roughness",text = 'roughness')
        layout.prop(self, "uRoughness",text = 'uRoughness')
        layout.prop(self, "vRoughness",text = 'vRoughness')
        layout.prop(self, "bump",text = 'bump')
        
    # Optional: custom label
    # Explicit user label overrides this, but here we can define a label dynamically.
    def draw_label(self):
        return "Pbrt Metal"

class PbrtUber(Node, MyCustomTreeNode):
    bl_idname = 'CustomNodeTypeUber'
    bl_label = 'Pbrt Uber'
    bl_icon = 'INFO'

    def update_value(self, context):
        self.update ()

    roughness : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    uRoughness : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    vRoughness : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    eta : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)

    def init(self, context):
        self.outputs.new('NodeSocketFloat', "Pbrt Uber")
        self.inputs.new('NodeSocketColor', "Kd")
        self.inputs.new('NodeSocketColor', "Ks")
        self.inputs.new('NodeSocketColor', "Kr")
        self.inputs.new('NodeSocketColor', "Kt")
        uRoughnessTexture_node = self.inputs.new('NodeSocketColor', "u roughness texture")
        uRoughnessTexture_node.hide_value=True
        vRoughnessTexture_node = self.inputs.new('NodeSocketColor', "v roughness texture")
        vRoughnessTexture_node.hide_value=True

    def update(self):
        try:
            out = self.outputs["Pbrt Uber"]
            can_continue = True
        except:
            can_continue = False
        if can_continue:
            if out.is_linked:
                print("continues in update rutine.")

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):
        layout.prop(self, "roughness",text = 'roughness')
        layout.prop(self, "uRoughness",text = 'uRoughness')
        layout.prop(self, "vRoughness",text = 'vRoughness')
        layout.prop(self, "eta",text = 'eta')

    def draw_label(self):
        return "Pbrt Uber"

class PbrtSubsurface(Node, MyCustomTreeNode):
    bl_idname = 'CustomNodeTypeSubsurface'
    bl_label = 'Pbrt Subsurface'
    bl_icon = 'INFO'

    def update_value(self, context):
        self.update ()

    uRoughness : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    vRoughness : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)

    def init(self, context):
        self.outputs.new('NodeSocketFloat', "Pbrt Subsurface")
        uRoughnessTexture_node = self.inputs.new('NodeSocketColor', "u roughness texture")
        uRoughnessTexture_node.hide_value=True
        vRoughnessTexture_node = self.inputs.new('NodeSocketColor', "v roughness texture")
        vRoughnessTexture_node.hide_value=True
        self.inputs.new('NodeSocketColor', "Kr")
        self.inputs.new('NodeSocketColor', "Kt")

        
    def update(self):
        try:
            out = self.outputs["Pbrt Subsurface"]
            can_continue = True
        except:
            can_continue = False
        if can_continue:
            if out.is_linked:
                print("continues in update rutine.")

    def draw_buttons(self, context, layout):
        layout.prop(self, "uRoughness",text = 'uRoughness')
        layout.prop(self, "vRoughness",text = 'vRoughness')

    def draw_label(self):
        return "Pbrt Subsurface"

class PbrtSubstrate(Node, MyCustomTreeNode):
    bl_idname = 'CustomNodeTypeSubstrate'
    bl_label = 'Pbrt Substrate'
    bl_icon = 'INFO'

    def update_value(self, context):
        self.update ()

    uRoughness : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    vRoughness : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)


    def init(self, context):
        self.outputs.new('NodeSocketFloat', "Pbrt Substrate")
        uRoughnessTexture_node = self.inputs.new('NodeSocketColor', "u roughness texture")
        uRoughnessTexture_node.hide_value=True
        vRoughnessTexture_node = self.inputs.new('NodeSocketColor', "v roughness texture")
        vRoughnessTexture_node.hide_value=True
        self.inputs.new('NodeSocketColor', "Kd")
        self.inputs.new('NodeSocketColor', "Ks")
        
    def update(self):
        try:
            out = self.outputs["Pbrt Substrate"]
            can_continue = True
        except:
            can_continue = False
        if can_continue:
            if out.is_linked:
                print("continues in update rutine.")

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):
        layout.prop(self, "uRoughness",text = 'uRoughness')
        layout.prop(self, "vRoughness",text = 'vRoughness')

    # Optional: custom label
    # Explicit user label overrides this, but here we can define a label dynamically.
    def draw_label(self):
        return "Pbrt Substrate"

class PbrtPlastic(Node, MyCustomTreeNode):
    bl_idname = 'CustomNodeTypePlastic'
    bl_label = 'Pbrt Plastic'
    bl_icon = 'INFO'

    def update_value(self, context):
        self.update ()


    #Kd : bpy.props.FloatVectorProperty(name='color', description='color', subtype='COLOR',  min=0.0, max=1.0, default=(0.8, 0.8, 0.8))
    #Ks : bpy.props.FloatVectorProperty(name='color', description='color', subtype='COLOR',  min=0.0, max=1.0, default=(0.8, 0.8, 0.8))
    Roughness : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)

    def init(self, context):
        self.outputs.new('NodeSocketFloat', "Pbrt Plastic")
        self.inputs.new('NodeSocketColor', "Kd")
        self.inputs.new('NodeSocketColor', "Ks")
        
    def update(self):
        try:
            out = self.outputs["Pbrt Plastic"]
            can_continue = True
        except:
            can_continue = False
        if can_continue:
            if out.is_linked:
                print("continues in update rutine.")

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):
        #layout.prop(self, "Kd",text = 'Kd')
        #layout.prop(self, "Ks",text = 'Ks')
        layout.prop(self, "Roughness",text = 'Roughness')

    # Optional: custom label
    # Explicit user label overrides this, but here we can define a label dynamically.
    def draw_label(self):
        return "Pbrt Plastic"

    # Derived from the Node base type.
class PbrtBlackBody(Node, MyCustomTreeNode):
    '''A custom node'''
    bl_idname = 'CustomNodeTypeBlackBody'
    bl_label = 'Pbrt BlackBody'
    bl_icon = 'INFO'

    def update_value(self, context):
        self.update ()

    Temperature : bpy.props.IntProperty(default=5500, min=0, max=99999)
    Lambda : bpy.props.IntProperty(default=10, min=1, max=99999)

    def init(self, context):
        self.outputs.new('NodeSocketFloat', "Pbrt BlackBody")
        
    def update(self):
        print('Updating BlackBody props..')
        try:
            can_continue = True
        except:
            can_continue = False
        if can_continue:
            print("continues in update rutine.")
           
    def draw_buttons(self, context, layout):
        layout.prop(self, "Temperature",text = 'Temperature')
        layout.prop(self, "Lambda",text = 'Lambda')

    def draw_buttons_ext(self, context, layout):
        layout.prop(self, "Temperature",text = 'Temperature')
        layout.prop(self, "Lambda",text = 'Lambda')
        
    def draw_label(self):
        return "Pbrt BlackBody"

class PbrtMedium(Node, MyCustomTreeNode):
    '''A custom node'''
    bl_idname = 'CustomNodeTypeMedium'
    bl_label = 'Pbrt Medium'
    bl_icon = 'INFO'

    def update_value(self, context):
        self.update ()

    mediumType = [("homogeneous","homogeneous","",1)]
    Type : bpy.props.EnumProperty(name = "Type", items=mediumType , default="homogeneous")
    Scale : bpy.props.FloatProperty(default=1.0, min=0.0, max=99999.0)
    g : bpy.props.FloatProperty(default=0.0, min=0.0001, max=1.0)

    def init(self, context):
        self.outputs.new('NodeSocketFloat', "Pbrt Medium")
        self.inputs.new('NodeSocketColor', "sigma_a")
        self.inputs.new('NodeSocketColor', "sigma_s")
        
    def update(self):
        print('Updating Pbrt Medium props..')
        try:
            can_continue = True
        except:
            can_continue = False
        if can_continue:
            print("continues in update rutine.")

    def draw_buttons(self, context, layout):
        layout.prop(self, "Type",text = 'Type')
        layout.prop(self, "g",text = 'g')
        layout.prop(self, "Scale",text = 'Scale')

    def draw_buttons_ext(self, context, layout):
        layout.prop(self, "Type",text = 'Type')
        layout.prop(self, "g",text = 'g')
        layout.prop(self, "Scale",text = 'Scale')

    def draw_label(self):
        return "Pbrt Medium"


#@base.register_class
class PbrtTextureSocket(bpy.types.NodeSocket):
    bl_idname = 'PbrtTextureSocket'
    bl_label = 'Pbrt Texture Socket'

    default_color : bpy.props.FloatVectorProperty(
        name='Color',
        description='Color',
        subtype='COLOR',
        min=0.0,
        soft_max=1.0,
        default=(0.8, 0.8, 0.8),
    )

    default_value : bpy.props.FloatProperty(
        name='Value',
        description='Value',
        min=0.0,
        soft_max=1.0,
        default=0.5,
    )

    tex_type : bpy.props.EnumProperty(
        name='Texture Type',
        description='Texture Type',
        items=[
            ('COLOR', 'Color', ''),
            ('VALUE', 'Value', ''),
            ('PURE', 'Pure', ''),
        ],
        default='COLOR',
    )

    def to_scene_data(self, scene):
        if self.is_linked:
            d = self.links[0].from_node.to_scene_data(scene)
            if d:
                return d
        if self.tex_type == 'COLOR':
            return list(self.default_color)
        elif self.tex_type == 'VALUE':
            return self.default_value
        else:
            return 0.0

    def draw_value(self, context, layout, node):
        layout.label(self.name)

    def draw_color(self, context, node):
        return (1.0, 0.1, 0.2, 0.8)

    def draw(self, context, layout, node, text):
        if self.tex_type == 'PURE' or self.is_output or self.is_linked:
            layout.label(self.name)
        else:
            if self.tex_type == 'COLOR':
                layout.prop(self, 'default_color', text=self.name)
            elif self.tex_type == 'VALUE':
                layout.prop(self, 'default_value', text=self.name)


def register():
    nodeitems_utils.register_node_categories("CUSTOM_NODES", node_categories)
    #bpy.utils.register_class(PbrtRenderSettingsPanel)
    # bpy.utils.register_class(PbrtMatte)
    # bpy.utils.register_class(PbrtMirror)
    # bpy.utils.register_class(PbrtGlass)
    # bpy.utils.register_class(PbrtDisney)
    # bpy.utils.register_class(PbrtMetal)
    # bpy.utils.register_class(PbrtUber)
    # bpy.utils.register_class(PbrtSubsurface)
    # bpy.utils.register_class(PbrtSubstrate)
    # bpy.utils.register_class(PbrtPlastic)

def unregister():
    nodeitems_utils.unregister_node_categories("CUSTOM_NODES")
    #bpy.utils.unregister_class(PbrtRenderSettingsPanel)
    # bpy.utils.unregister_class(PbrtMatte)
    # bpy.utils.unregister_class(PbrtMirror)
    # bpy.utils.unregister_class(PbrtGlass)
    # bpy.utils.unregister_class(PbrtDisney)
    # bpy.utils.unregister_class(PbrtMetal)
    # bpy.utils.unregister_class(PbrtUber)
    # bpy.utils.unregister_class(PbrtSubsurface)
    # bpy.utils.unregister_class(PbrtSubstrate)
    # bpy.utils.unregister_class(PbrtPlastic)