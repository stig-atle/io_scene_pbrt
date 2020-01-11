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
        #Do not add the PBRT shader category if PBRT is not selected as renderer
        engine = context.scene.render.engine
        if engine != 'PBRT_Renderer':
            return False
        else:
            b = False
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
        NodeItem("CustomNodeTypeTranslucent"),
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

    def updateViewportColor(self,context):
        obj = bpy.context.active_object
        mesh = bpy.context.active_object.data
        for f in mesh.polygons:
            slot = obj.material_slots[f.material_index]
            mat = slot.material
            if mat is not None:
                mat.diffuse_color = self.Kd

    Sigma : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    Kd : bpy.props.FloatVectorProperty(name="Kd", description="Kd",default=(0.8, 0.8, 0.8, 1.0), min=0, max=1, subtype='COLOR', size=4,update=updateViewportColor)
    
    def init(self, context):
        self.outputs.new('NodeSocketFloat', "Pbrt Matte")
        KdTexture_node = self.inputs.new('NodeSocketColor', "Kd Texture")
        KdTexture_node.hide_value = True

    def draw_buttons(self, context, layout):
        layout.prop(self, "Sigma",text = 'Sigma')
        layout.prop(self, "Kd",text = 'Kd')
        
    def draw_label(self):
        return "Pbrt Matte"

class PbrtMirror(Node, MyCustomTreeNode):
    bl_idname = 'CustomNodeTypeMirror'
    bl_label = 'Pbrt Mirror'
    bl_icon = 'INFO'

    def updateViewportColor(self,context):
        obj = bpy.context.active_object
        mesh = bpy.context.active_object.data
        for f in mesh.polygons:
            slot = obj.material_slots[f.material_index]
            mat = slot.material
            if mat is not None:
                mat.diffuse_color = self.Kr

    def update_value(self, context):
        self.update ()

    Kr : bpy.props.FloatVectorProperty(name="Kr", description="Kr",default=(0.8, 0.8, 0.8, 1.0), min=0, max=1, subtype='COLOR', size=4,update=updateViewportColor)
    Index : bpy.props.FloatProperty(name="Index", default=1.333, min=0.0, max=100.0)

    def init(self, context):
        krTexture_node = self.inputs.new('NodeSocketColor', "kr texture")
        krTexture_node.hide_value=True
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
    def draw_buttons(self, context, layout):
        layout.prop(self, "Kr",text='Kr')

    # Optional: custom label
    # Explicit user label overrides this, but here we can define a label dynamically.
    def draw_label(self):
        return "Pbrt Mirror"

class PbrtGlass(Node, MyCustomTreeNode):
    bl_idname = 'CustomNodeTypeGlass'
    bl_label = 'Pbrt Glass'
    bl_icon = 'INFO'

    def updateViewportColor(self,context):
        obj = bpy.context.active_object
        mesh = bpy.context.active_object.data
        for f in mesh.polygons:
            slot = obj.material_slots[f.material_index]
            mat = slot.material
            if mat is not None:
                mat.diffuse_color = self.kr

    def update_value(self, context):
        self.update ()
    kr : bpy.props.FloatVectorProperty(name="Kr", description="Kr",default=(0.8, 0.8, 0.8, 1.0), min=0, max=1, subtype='COLOR', size=4,update=updateViewportColor)
    kt : bpy.props.FloatVectorProperty(name="Kt", description="Kt",default=(0.8, 0.8, 0.8, 1.0), min=0, max=1, subtype='COLOR', size=4)
    uRoughness : bpy.props.FloatProperty(name="uRoughness", default=0.0, min=0.0, max=1.0)
    vRoughness : bpy.props.FloatProperty(name="vRoughness", default=0.0, min=0.0, max=1.0)
    Index : bpy.props.FloatProperty(name="Index", default=1.333, min=0.0, max=100.0)

    def init(self, context):
        uRoughnessTexture_node = self.inputs.new('NodeSocketColor', "u roughness texture")
        uRoughnessTexture_node.hide_value = True
        vRoughnessTexture_node = self.inputs.new('NodeSocketColor', "v roughness texture")
        vRoughnessTexture_node.hide_value = True
        #self.inputs.new('NodeSocketColor', "Kr")
        #self.inputs.new('NodeSocketColor', "Kt")
        krTexture_node = self.inputs.new('NodeSocketColor', "kr texture")
        krTexture_node.hide_value=True
        ktTexture_node = self.inputs.new('NodeSocketColor', "kt texture")
        ktTexture_node.hide_value=True
        medium_node = self.inputs.new('NodeSocketColor', "medium")
        medium_node.hide_value = True
        self.outputs.new('NodeSocketFloat', "Pbrt Glass")


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
        layout.prop(self, "kr",text = 'kr')
        layout.prop(self, "kt",text = 'kt')
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

    def updateViewportColor(self,context):
        obj = bpy.context.active_object
        mesh = bpy.context.active_object.data
        for f in mesh.polygons:
            slot = obj.material_slots[f.material_index]
            mat = slot.material
            if mat is not None:
                mat.diffuse_color = self.color

    def update_value(self, context):
        self.update ()
    color : bpy.props.FloatVectorProperty(name="color", description="color",default=(0.8, 0.8, 0.8, 1.0), min=0, max=1, subtype='COLOR', size=4,update=updateViewportColor)
    #color : bpy.props.FloatVectorProperty(name='color', description='color', subtype='COLOR',  min=0.0, max=1.0, default=(0.8, 0.8, 0.8),update=updateViewportColor)
    metallic : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    eta : bpy.props.FloatProperty(default=1.5, min=0.0, max=9999.0)
    roughness : bpy.props.FloatProperty(default=0.5, min=0.0, max=9999.0)
    specularTint : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    anisotropic : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    sheen : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    sheenTint : bpy.props.FloatProperty(default=0.5, min=0.0, max=1.0)
    clearCoat : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    clearCoatGloss : bpy.props.FloatProperty(default=1.0, min=0.0, max=1.0)
    specTrans : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    scatterDistance : bpy.props.FloatVectorProperty(name='color', description='color', subtype='COLOR',  min=0.0, max=1.0, default=(0.8, 0.8, 0.8))
    flatness : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    diffTrans : bpy.props.FloatProperty(default=1.0, min=0.0, max=1.0)

    def draw_buttons(self, context, layout):
        layout.prop(self, "color",text = 'color')
        layout.prop(self, "metallic",text = 'metallic')
        layout.prop(self, "eta",text = 'eta')
        layout.prop(self, "roughness",text = 'roughness')
        layout.prop(self, "specularTint",text = 'specularTint')
        layout.prop(self, "anisotropic",text = 'anisotropic')
        layout.prop(self, "sheen",text = 'sheen')
        layout.prop(self, "sheenTint",text = 'sheenTint')
        layout.prop(self, "clearCoat",text = 'clearCoat')
        layout.prop(self, "clearCoatGloss",text = 'clearCoatGloss')
        layout.prop(self, "specTrans",text = 'specTrans')
        layout.prop(self, "scatterDistance",text = 'scatterDistance')
        layout.prop(self, "flatness",text = 'flatness')
        layout.prop(self, "diffTrans",text = 'diffTrans')

    def init(self, context):
        self.outputs.new('NodeSocketFloat', "Pbrt Disney")

        colorTexture_node = self.inputs.new('NodeSocketColor', "color texture")
        colorTexture_node.hide_value = True

        metallicTexture_node = self.inputs.new('NodeSocketColor', "Metallic texture")
        metallicTexture_node.hide_value = True

        etaTexture_node = self.inputs.new('NodeSocketColor', "Eta texture")
        etaTexture_node.hide_value = True

        roughnessTexture_node = self.inputs.new('NodeSocketColor', "Roughness texture")
        roughnessTexture_node.hide_value = True

        specularTintTexture_node = self.inputs.new('NodeSocketColor', "SpecularTint texture")
        specularTintTexture_node.hide_value = True

        anisotropicTexture_node = self.inputs.new('NodeSocketColor', "Anisotropic texture")
        anisotropicTexture_node.hide_value = True

        sheenTexture_node = self.inputs.new('NodeSocketColor', "Sheen texture")
        sheenTexture_node.hide_value = True

        sheenTintTexture_node = self.inputs.new('NodeSocketColor', "Sheen tint texture")
        sheenTintTexture_node.hide_value = True

        clearCoatTexture_node = self.inputs.new('NodeSocketColor', "Clear coat texture")
        clearCoatTexture_node.hide_value = True

        clearCoatGlossTexture_node = self.inputs.new('NodeSocketColor', "Clear cloat gloss texture")
        clearCoatGlossTexture_node.hide_value = True

        specTransTexture_node = self.inputs.new('NodeSocketColor', "Spec trans texture")
        specTransTexture_node.hide_value = True

        scatterDistanceTexture_node = self.inputs.new('NodeSocketColor', "Scatter distance texture")
        scatterDistanceTexture_node.hide_value = True

        flatnessTexture_node = self.inputs.new('NodeSocketColor', "Flatness texture")
        flatnessTexture_node.hide_value = True
        
        diffTransTexture_node = self.inputs.new('NodeSocketColor', "Diff trans texture")
        diffTransTexture_node.hide_value = True
        

    def update(self):
        try:
            out = self.outputs["Pbrt Disney"]
            can_continue = True
        except:
            can_continue = False
        if can_continue:
            if out.is_linked:
                print("continues in update rutine.")

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
    
    def updateViewportColor(self,context):
        obj = bpy.context.active_object
        mesh = bpy.context.active_object.data
        for f in mesh.polygons:
            slot = obj.material_slots[f.material_index]
            mat = slot.material
            if mat is not None:
                mat.diffuse_color = self.kt

    roughness : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    uRoughness : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    vRoughness : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    bump : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    kt : bpy.props.FloatVectorProperty(name="Kt", description="Kt",default=(0.8, 0.8, 0.8, 1.0), min=0, max=1, subtype='COLOR', size=4,update=updateViewportColor)
    eta : bpy.props.FloatVectorProperty(name="Eta", description="Eta",default=(0.8, 0.8, 0.8, 1.0), min=0, max=1, subtype='COLOR', size=4)

    def init(self, context):
        self.outputs.new('NodeSocketFloat', "Pbrt Metal")
        etaTextureNode = self.inputs.new('NodeSocketColor', "Eta texture")
        etaTextureNode.hide_value=True
        kTexture_node = self.inputs.new('NodeSocketColor', "Kt texture")
        kTexture_node.hide_value=True
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
        layout.prop(self, "kt",text = 'kt')
        layout.prop(self, "eta",text = 'eta')
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

    def updateViewportColor(self,context):
        obj = bpy.context.active_object
        mesh = bpy.context.active_object.data
        for f in mesh.polygons:
            slot = obj.material_slots[f.material_index]
            mat = slot.material
            if mat is not None:
                mat.diffuse_color = self.kd

    def update_value(self, context):
        self.update ()

    kd : bpy.props.FloatVectorProperty(name="Kd", description="Kd",default=(0.8, 0.8, 0.8, 1.0), min=0, max=1, subtype='COLOR', size=4,update=updateViewportColor)
    ks : bpy.props.FloatVectorProperty(name="Ks", description="Ks",default=(0.8, 0.8, 0.8, 1.0), min=0, max=1, subtype='COLOR', size=4)
    kr : bpy.props.FloatVectorProperty(name="Kr", description="Kr",default=(0.8, 0.8, 0.8, 1.0), min=0, max=1, subtype='COLOR', size=4)
    kt : bpy.props.FloatVectorProperty(name="Kt", description="Kt",default=(0.8, 0.8, 0.8, 1.0), min=0, max=1, subtype='COLOR', size=4)
    roughness : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    uRoughness : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    vRoughness : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    eta : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)

    def init(self, context):
        self.outputs.new('NodeSocketFloat', "Pbrt Uber")
        kdTexture_node = self.inputs.new('NodeSocketColor', "kd texture")
        kdTexture_node.hide_value=True
        ksTexture_node = self.inputs.new('NodeSocketColor', "ks texture")
        ksTexture_node.hide_value=True
        krTexture_node = self.inputs.new('NodeSocketColor', "kr texture")
        krTexture_node.hide_value=True
        ktTexture_node = self.inputs.new('NodeSocketColor', "kt texture")
        ktTexture_node.hide_value=True
        opacityTexture_node = self.inputs.new('NodeSocketColor', "opacity texture")
        opacityTexture_node.hide_value=True
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
        layout.prop(self, "kd",text = 'kd')
        layout.prop(self, "ks",text = 'ks')
        layout.prop(self, "kr",text = 'kr')
        layout.prop(self, "kt",text = 'kt')
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

    def updateViewportColor(self,context):
        obj = bpy.context.active_object
        mesh = bpy.context.active_object.data
        for f in mesh.polygons:
            slot = obj.material_slots[f.material_index]
            mat = slot.material
            if mat is not None:
                mat.diffuse_color = self.kt

    def update_value(self, context):
        self.update ()

    sigma_a : bpy.props.FloatVectorProperty(name="sigma_a", description="sigma_a",default=(0.8, 0.8, 0.8, 1.0), min=0, max=1, subtype='COLOR', size=4)
    sigma_s : bpy.props.FloatVectorProperty(name="sigma_s", description="sigma_s",default=(0.8, 0.8, 0.8, 1.0), min=0, max=1, subtype='COLOR', size=4)
    kr : bpy.props.FloatVectorProperty(name="Kr", description="Kr",default=(0.8, 0.8, 0.8, 1.0), min=0, max=1, subtype='COLOR', size=4)
    kt : bpy.props.FloatVectorProperty(name="Kt", description="Kt",default=(0.8, 0.8, 0.8, 1.0), min=0, max=1, subtype='COLOR', size=4,update=updateViewportColor)
    uRoughness : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    vRoughness : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    scale : bpy.props.FloatProperty(default=1.0, min=0.0001, max=99999.0)
    eta : bpy.props.FloatProperty(default=1.0, min=0.0001, max=99999.0)
    remaproughness : bpy.props.BoolProperty(
    name="remaproughness",
    description="remaproughness",
    default = True)


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
    def init(self, context):
        self.outputs.new('NodeSocketFloat', "Pbrt Subsurface")
        uRoughnessTexture_node = self.inputs.new('NodeSocketColor', "u roughness texture")
        uRoughnessTexture_node.hide_value=True

        vRoughnessTexture_node = self.inputs.new('NodeSocketColor', "v roughness texture")
        vRoughnessTexture_node.hide_value=True
        
        krTexture_node = self.inputs.new('NodeSocketColor', "kr texture")
        krTexture_node.hide_value=True
        ktTexture_node = self.inputs.new('NodeSocketColor', "kt texture")
        ktTexture_node.hide_value=True

        sigma_aTexture_node = self.inputs.new('NodeSocketColor', "sigma_a texture")
        sigma_aTexture_node.hide_value=True
        sigma_sTexture_node = self.inputs.new('NodeSocketColor', "sigma_s texture")
        sigma_sTexture_node.hide_value=True

        medium_node = self.inputs.new('NodeSocketColor', "medium")
        medium_node.hide_value = True
        
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
        layout.prop(self, "eta",text = 'eta')
        layout.prop(self, "scale",text = 'scale')
        layout.prop(self, "uRoughness",text = 'uRoughness')
        layout.prop(self, "vRoughness",text = 'vRoughness')
        layout.prop(self, "remaproughness",text = 'remaproughness')
        layout.prop(self, "kr",text = 'kr')
        layout.prop(self, "kt",text = 'kt')
        layout.prop(self, "sigma_a",text = 'sigma_a')
        layout.prop(self, "sigma_s",text = 'sigma_s')
        layout.prop(self, "presetName", text = 'preset Name')

    def draw_label(self):
        return "Pbrt Subsurface"

class PbrtSubstrate(Node, MyCustomTreeNode):
    bl_idname = 'CustomNodeTypeSubstrate'
    bl_label = 'Pbrt Substrate'
    bl_icon = 'INFO'

    def updateViewportColor(self,context):
        obj = bpy.context.active_object
        mesh = bpy.context.active_object.data
        for f in mesh.polygons:
            slot = obj.material_slots[f.material_index]
            mat = slot.material
            if mat is not None:
                mat.diffuse_color = self.Kd

    def update_value(self, context):
        self.update ()
    Kd : bpy.props.FloatVectorProperty(name="kd", description="kd",default=(0.8, 0.8, 0.8, 1.0), min=0, max=1, subtype='COLOR', size=4,update=updateViewportColor)
    Ks : bpy.props.FloatVectorProperty(name="ks", description="ks",default=(0.8, 0.8, 0.8, 1.0), min=0, max=1, subtype='COLOR', size=4)
    uRoughness : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    vRoughness : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)


    def init(self, context):
        self.outputs.new('NodeSocketFloat', "Pbrt Substrate")
        uRoughnessTexture_node = self.inputs.new('NodeSocketColor', "u roughness texture")
        uRoughnessTexture_node.hide_value=True
        vRoughnessTexture_node = self.inputs.new('NodeSocketColor', "v roughness texture")
        vRoughnessTexture_node.hide_value=True
        kdTexture_node = self.inputs.new('NodeSocketColor', "kd texture")
        kdTexture_node.hide_value=True
        ksTexture_node = self.inputs.new('NodeSocketColor', "ks texture")
        ksTexture_node.hide_value=True
        
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
        layout.prop(self, "Kd",text = 'Kd')
        layout.prop(self, "Ks",text = 'Ks')
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

    def updateViewportColor(self,context):
        obj = bpy.context.active_object
        mesh = bpy.context.active_object.data
        for f in mesh.polygons:
            slot = obj.material_slots[f.material_index]
            mat = slot.material
            if mat is not None:
                mat.diffuse_color = self.Kd

    def update_value(self, context):
        self.update ()

    Kd : bpy.props.FloatVectorProperty(name="kd", description="kd",default=(0.8, 0.8, 0.8, 1.0), min=0, max=1, subtype='COLOR', size=4,update=updateViewportColor)
    Ks : bpy.props.FloatVectorProperty(name="ks", description="ks",default=(0.8, 0.8, 0.8, 1.0), min=0, max=1, subtype='COLOR', size=4)
    Roughness : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)

    def init(self, context):
        self.outputs.new('NodeSocketFloat', "Pbrt Plastic")
        kdTexture_node = self.inputs.new('NodeSocketColor', "kd texture")
        kdTexture_node.hide_value=True
        ksTexture_node = self.inputs.new('NodeSocketColor', "ks texture")
        ksTexture_node.hide_value=True
        roughnessTexture_node = self.inputs.new('NodeSocketColor', "roughness texture")
        roughnessTexture_node.hide_value=True
        
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
        layout.prop(self, "Kd",text = 'Kd')
        layout.prop(self, "Ks",text = 'Ks')
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


class PbrtTranslucent(Node, MyCustomTreeNode):
    '''A custom node'''
    bl_idname = 'CustomNodeTypeTranslucent'
    bl_label = 'Pbrt Translucent'
    bl_icon = 'INFO'

    def updateViewportColor(self,context):
        obj = bpy.context.active_object
        mesh = bpy.context.active_object.data
        for f in mesh.polygons:
            slot = obj.material_slots[f.material_index]
            mat = slot.material
            if mat is not None:
                mat.diffuse_color = self.Kd

    Sigma : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    Kd : bpy.props.FloatVectorProperty(name="Kd", description="Kd",default=(0.25, 0.25, 0.25, 1.0), min=0, max=1, subtype='COLOR', size=4,update=updateViewportColor)
    Ks : bpy.props.FloatVectorProperty(name="Ks", description="Ks",default=(0.25, 0.25, 0.25, 1.0), min=0, max=1, subtype='COLOR', size=4)
    Reflect : bpy.props.FloatVectorProperty(name="Reflect", description="Ks",default=(0.5, 0.5, 0.5, 1.0), min=0, max=1, subtype='COLOR', size=4)
    Transmit : bpy.props.FloatVectorProperty(name="Transmit", description="Ks",default=(0.5, 0.5, 0.5, 1.0), min=0, max=1, subtype='COLOR', size=4)
    Roughness : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    Remaproughness : bpy.props.BoolProperty(name="remaproughness", description="remaproughness", default = True)

    def init(self, context):
        self.outputs.new('NodeSocketFloat', "Pbrt Translucent")
        KdTexture_node = self.inputs.new('NodeSocketColor', "Kd Texture")
        KdTexture_node.hide_value = True
        KsTexture_node = self.inputs.new('NodeSocketColor', "Ks Texture")
        KsTexture_node.hide_value = True
        ReflectTexture_node = self.inputs.new('NodeSocketColor', "Reflect Texture")
        ReflectTexture_node.hide_value = True
        TransmitTexture_node = self.inputs.new('NodeSocketColor', "Transmit Texture")
        TransmitTexture_node.hide_value = True
        RoughnessTexture_node = self.inputs.new('NodeSocketColor', "Roughness Texture")
        RoughnessTexture_node.hide_value = True

    def draw_buttons(self, context, layout):
        layout.prop(self, "Sigma",text = 'Sigma')
        layout.prop(self, "Kd",text = 'Kd')
        layout.prop(self, "Ks",text = 'Ks')
        layout.prop(self, "Reflect",text = 'Reflect')
        layout.prop(self, "Transmit",text = 'Transmit')
        layout.prop(self, "Roughness",text = 'Roughness')
        layout.prop(self, "Remaproughness",text = 'Remaproughness')
        
    def draw_label(self):
        return "Pbrt Translucent"

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