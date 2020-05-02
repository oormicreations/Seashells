# Seashells by oormi creations
# A free and open source add-on for Blender
# Creates seashells with a procedural material.
# http://oormi.in


bl_info = {
    "name": "Seashells",
    "description": "Creates Seashells",
    "author": "Oormi Creations",
    "version": (0, 2, 0),
    "blender": (2, 80, 0),
    "location": "3D View > Seashells",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "https://github.com/oormicreations/Seashells",
    "tracker_url": "https://github.com/oormicreations/Seashells/issues",
    "category": "Object"
}

import bpy
from mathutils import *
from bpy import context

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Menu,
                       Operator,
                       PropertyGroup,
                       )



def createbasemat():
    mat = bpy.data.materials.new(name="SeashellMat")
    mat.use_nodes = True
    matnodes = mat.node_tree.nodes
    matnodes["Principled BSDF"].inputs[7].default_value = 0.3

    ramp = matnodes.new('ShaderNodeValToRGB')
    tex = matnodes.new('ShaderNodeTexMusgrave')
    cmap = matnodes.new('ShaderNodeMapping')
    cood = matnodes.new('ShaderNodeTexCoord')

    ramp.location = Vector((-300,300))
    tex.location = Vector((-500,300))
    cmap.location = Vector((-700,300))
    cood.location = Vector((-900,300))

    bump = matnodes.new('ShaderNodeBump')
    btex = matnodes.new('ShaderNodeTexMusgrave')
    bmap = matnodes.new('ShaderNodeMapping')
    bcood = matnodes.new('ShaderNodeTexCoord')

    bump.location = Vector((-300,-50))
    btex.location = Vector((-500,-50))
    bmap.location = Vector((-700,-50))
    bcood.location = Vector((-900,-50))

    dif = matnodes['Principled BSDF']
    mat.node_tree.links.new(ramp.outputs[0], dif.inputs[0])
    mat.node_tree.links.new(tex.outputs[0], ramp.inputs[0])
    mat.node_tree.links.new(cmap.outputs[0], tex.inputs[0])
    mat.node_tree.links.new(cood.outputs[2], cmap.inputs[0])

    mat.node_tree.links.new(bump.outputs[0], dif.inputs[19])
    mat.node_tree.links.new(btex.outputs[0], bump.inputs[2])
    mat.node_tree.links.new(bmap.outputs[0], btex.inputs[0])
    mat.node_tree.links.new(bcood.outputs[2], bmap.inputs[0])
    
    bump.inputs[0].default_value = 0.1

    btex.inputs[2].default_value = 53
    btex.inputs[3].default_value = 2.2
    btex.inputs[4].default_value = 0
    btex.inputs[5].default_value = 2
    btex.musgrave_dimensions = '2D'

    bmap.vector_type = 'POINT'
    bmap.inputs[2].default_value[1] = 1.57254
    bmap.inputs[3].default_value[0] = 17.2
    bmap.inputs[3].default_value[1] = 15.2    

    return mat, ramp, tex, cmap, cood    

def createshellmat1():
    mat, ramp, tex, cmap, cood = createbasemat()
    
    ramp.color_ramp.elements.new(0.0)
    ramp.color_ramp.elements[0].color = (1, 0.292, 0, 1)
    ramp.color_ramp.elements[1].color = (0.08, 0.011, 0, 1)
    ramp.color_ramp.elements[2].color = (1, 0.292, 0, 1)

    cmap.vector_type = 'NORMAL'
    cmap.inputs[3].default_value[1] = 5

    tex.inputs[2].default_value = 38
    tex.inputs[3].default_value = 10
    tex.inputs[4].default_value = 20
    tex.inputs[5].default_value = 4
    tex.musgrave_dimensions = '3D'

    return mat

def createshellmat2():
    mat, ramp, tex, cmap, cood = createbasemat()
    
    ramp.color_ramp.elements[0].color = (0.4, 0, 0, 1)
    ramp.color_ramp.elements[1].color = (1, 0.8, 0.6, 1)
    ramp.color_ramp.elements[1].position = 0.09

    cmap.vector_type = 'POINT'
    cmap.inputs[3].default_value[1] = 5
    cmap.inputs[2].default_value[1] = 1.5708

    tex.inputs[2].default_value = 13
    tex.inputs[3].default_value = 10
    tex.inputs[4].default_value = 20
    tex.inputs[5].default_value = 4
    tex.musgrave_dimensions = '2D'

    return mat

def createshellmat3():
    mat, ramp, tex, cmap, cood = createbasemat()
    
    ramp.color_ramp.elements[0].color = (0.4, 0.085, 0.008, 1)
    ramp.color_ramp.elements[1].color = (1, 0.8, 0.6, 1)
    ramp.color_ramp.elements[1].position = 0.06

    cmap.vector_type = 'TEXTURE'
    cmap.inputs[3].default_value[1] = 0.1

    tex.inputs[2].default_value = 20
    tex.inputs[3].default_value = 10
    tex.inputs[4].default_value = 20
    tex.inputs[5].default_value = 4
    tex.musgrave_dimensions = '3D'

    return mat


def view3d_find( return_area = False ):
    # returns first 3d view, normally we get from context
    for area in bpy.context.window.screen.areas:
        if area.type == 'VIEW_3D':
            v3d = area.spaces[0]
            rv3d = v3d.region_3d
            for region in area.regions:
                if region.type == 'WINDOW':
                    if return_area: return region, rv3d, v3d, area
                    return region, rv3d, v3d
    return None, None


#----------------------------------------------------------------------------------------
# Operators
#----------------------------------------------------------------------------------------

class CRD_OT_CResetDefaults(bpy.types.Operator):
    bl_idname = "reset.defaults"
    bl_label = "Reset Defaults"
    bl_description = "Reset Defaults."

    def execute(self, context):
        scene = context.scene
        sstool = scene.ss_tool
        
        sstool.ss_clean = True
        sstool.ss_mat = "M1"
        sstool.ss_res = "Ready..."
        sstool.ss_segx = 64
        sstool.ss_segy = 240
        sstool.fan_anim = True
        sstool.fan_fend = 100
        sstool.fan_fstart = 1
        sstool.fan_nblades = 5
        sstool.fan_speed = 2
        sstool.fan_subdiv = 20
        
        sstool.ss_res = "Reset to defaults !"
        return{'FINISHED'}  
        


class CCS_OT_CCreateSeaShell(bpy.types.Operator):
    bl_idname = "create.seashell"
    bl_label = "Create Seashell"
    bl_description = "Create Seashell."

    def execute(self, context):
        scene = context.scene
        sstool = scene.ss_tool
        
        bpy.ops.mesh.primitive_cylinder_add(vertices=sstool.ss_segx, radius=1, depth=12, end_fill_type='NOTHING')
        bpy.ops.object.shade_smooth()
        bpy.context.object.name = "Seashell"
        ssname = bpy.context.object.name #because name can change if exists already


        bpy.ops.object.modifier_add(type='SIMPLE_DEFORM')
        bpy.context.object.modifiers["SimpleDeform"].deform_method = 'TAPER'
        bpy.context.object.modifiers["SimpleDeform"].deform_axis = 'Z'
        bpy.context.object.modifiers["SimpleDeform"].factor = -1.99
        bpy.context.object.modifiers["SimpleDeform"].name = "Taper"


        bpy.ops.object.add(type='LATTICE', enter_editmode=False, location=(0, 0, 0))
        bpy.context.object.scale[2] = 12
        bpy.context.object.data.points_w = 4
        bpy.context.object.name = "SeashellLat"
        latname = bpy.context.object.name

        bpy.ops.object.select_all(action='DESELECT')
        seed = bpy.data.objects.get(ssname)
        bpy.context.view_layer.objects.active = seed
        seed.select_set(True)

        bpy.ops.object.modifier_add(type='LATTICE')
        bpy.context.object.modifiers["Lattice"].object = bpy.data.objects[latname]
        bpy.ops.object.editmode_toggle()
        #bpy.ops.mesh.loopcut_slide(MESH_OT_loopcut={"number_cuts":16, "smoothness":0, 
        #"falloff":'INVERSE_SQUARE', "object_index":0, "edge_index":183, "mesh_select_mode_init":(False, False, True)}, TRANSFORM_OT_edge_slide={"value":0, "single_side":False, "use_even":False, "flipped":False, "use_clamp":True, "mirror":True, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "correct_uv":True, "release_confirm":False, "use_accurate":False})


        region, rv3d, v3d, area = view3d_find(True)

        override = {
            'scene'  : bpy.context.scene,
            'region' : region,
            'area'   : area,
            'space'  : v3d
        }

        bpy.ops.mesh.loopcut_slide(
            override, 
            MESH_OT_loopcut = {
                "number_cuts"           : sstool.ss_segy,
                "smoothness"            : 0,     
                "falloff"               : 'SMOOTH', 
                "edge_index"            : 1, #edge 1 should be always a vertical edge
                "object_index"          : 0,
                "mesh_select_mode_init" : (True, False, False)
            },
            TRANSFORM_OT_edge_slide = {
                "value"           : 0,
                "mirror"          : False, 
                "snap"            : False,
                "snap_target"     : 'CLOSEST',
                "snap_point"      : (0, 0, 0),
                "snap_align"      : False,
                "snap_normal"     : (0, 0, 0),
                "correct_uv"      : False,
                "release_confirm" : False
            }
        )

        bpy.ops.object.editmode_toggle()
        bpy.ops.object.select_all(action='DESELECT')

        lat = bpy.data.objects.get(latname)
        bpy.context.view_layer.objects.active = lat
        lat.select_set(True)
        #bpy.ops.object.editmode_toggle()

        #set lattice deformation
        for p in range(12,16):
            ppos = lat.data.points[p].co_deform
            dx = 6.0
            dy = 0.5
            lat.data.points[p].co_deform = Vector((ppos.x + dx, ppos.y + dy, ppos.z))
        for p in range(8,12):
            ppos = lat.data.points[p].co_deform
            dx = 5.0
            dy = 0.5
            lat.data.points[p].co_deform = Vector((ppos.x + dx, ppos.y + dy, ppos.z))
        for p in range(4,8):
            ppos = lat.data.points[p].co_deform
            dx = 4.0
            dy = 0.0
            lat.data.points[p].co_deform = Vector((ppos.x + dx, ppos.y + dy, ppos.z))
            

        #bend
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = seed
        seed.select_set(True)

        bpy.ops.object.modifier_add(type='SIMPLE_DEFORM')
        bpy.context.object.modifiers["SimpleDeform"].deform_method = 'BEND'
        bpy.context.object.modifiers["SimpleDeform"].deform_axis = 'X'
        bpy.context.object.modifiers["SimpleDeform"].angle = (1800 * 3.141592653589793)/180
        bpy.context.object.modifiers["SimpleDeform"].name = "Bend"

        #mat
        bpy.ops.object.material_slot_add()

        if sstool.ss_mat=='M1':
            seed.data.materials[0] = createshellmat1()
        if sstool.ss_mat=='M2':
            seed.data.materials[0] = createshellmat2()
        if sstool.ss_mat=='M3':
            seed.data.materials[0] = createshellmat3()
        if sstool.ss_mat=='M4':
            seed.data.materials[0] = None

        #cleanup
        if sstool.ss_clean:
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Taper")
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Lattice")
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Bend")

            bpy.ops.object.select_all(action='DESELECT')
            bpy.data.objects[latname].select_set(True)
            bpy.ops.object.delete() 

        
        sstool.ss_res = "Seashell created !"
        return{'FINISHED'}  


class CCF_OT_CCreateFan(bpy.types.Operator):
    bl_idname = "create.fan"
    bl_label = "Create Fan"
    bl_description = "Create a paper fan."

    def execute(self, context):
        scene = context.scene
        sstool = scene.ss_tool

        #create triangle and lattice

        #subdiv = 20
        loc = Vector((-1,1,0))
        bpy.ops.object.add(radius=2, type='LATTICE')
        bpy.context.object.data.points_u = 4
        lat = bpy.context.active_object
        lat.scale[2] = 0.1
        lat.location = loc

        bpy.ops.mesh.primitive_plane_add()
        bpy.ops.object.mode_set(mode = 'OBJECT')
        obj = bpy.context.active_object
        bpy.ops.object.mode_set(mode = 'EDIT') 
        bpy.ops.mesh.select_mode(type="VERT")
        bpy.ops.mesh.select_all(action = 'DESELECT')
        bpy.ops.object.mode_set(mode = 'OBJECT')
        obj.data.vertices[2].select = True
        bpy.ops.object.mode_set(mode = 'EDIT') 
        bpy.ops.mesh.dissolve_verts()
        bpy.ops.mesh.select_all(action = 'SELECT')
        bpy.ops.mesh.subdivide(number_cuts=sstool.fan_subdiv)
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.modifier_add(type='LATTICE')
        bpy.context.object.modifiers["Lattice"].object = lat

        obj.location = loc
        bpy.ops.object.shade_smooth()


        #set lattice points

        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = lat
        lat.select_set(True)
        bpy.ops.object.editmode_toggle()

        pts = [3,11,7,15]
        d1 = Vector((0.1,0,-1.5))
        d2 = Vector((0.15,0,7))

        for p in pts:
            ppos = lat.data.points[p].co_deform
            lat.data.points[p-3].co_deform = ppos + d1
            ppos = lat.data.points[p-1].co_deform
            lat.data.points[p-2].co_deform = ppos + d2
         
        bpy.ops.object.editmode_toggle()

        #apply lattice and make array

        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Lattice")
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='BOUNDS')

        bpy.ops.object.select_all(action='DESELECT')
        lat.select_set(True)
        bpy.ops.object.delete()

        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        nblades = sstool.fan_nblades
        blades = [bpy.context.object]
        for n in range(1,nblades):
            bpy.ops.object.duplicate_move()
            bpy.context.object.rotation_euler[2] = (-2 * 3.141592653589793 * n)/nblades
            blades.append(bpy.context.object)

        for b in blades:
            b.select_set(True)
            
        bpy.ops.object.join()
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        bpy.context.object.name = "Fan.001"

        #animate
        #anim = True
        #speed  = 1
        #fstart = 1
        #fend = 100

        if sstool.fan_anim:
            #keyInterp = bpy.context.preferences.edit.keyframe_new_interpolation_type
            #bpy.context.preferences.edit.keyframe_new_interpolation_type ='LINEAR'     #Not working!
            bpy.context.object.keyframe_insert(data_path='rotation_euler', frame=sstool.fan_fstart)
            bpy.context.object.rotation_euler[2] = sstool.fan_speed * 3.141592653589793 * 2
            bpy.context.object.keyframe_insert(data_path='rotation_euler', frame=sstool.fan_fend)
            #bpy.context.preferences.edit.keyframe_new_interpolation_type = keyInterp

        sstool.ss_res = "Fan created !"
        return{'FINISHED'}  

#---------------------------------------------------------------------------------------------------------------------------
# Panels
#---------------------------------------------------------------------------------------------------------------------------

class OBJECT_PT_SSPanel(bpy.types.Panel):

    bl_label = "Seashells 0.2.0"
    bl_idname = "OBJECT_PT_SS_Panel"
    bl_category = "Seashells"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"


    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        sstool = scene.ss_tool
        
        layout.prop(sstool, "ss_segx")
        layout.prop(sstool, "ss_segy")
        layout.prop(sstool, "ss_mat")
        layout.prop(sstool, "ss_clean")
        layout.operator("create.seashell", text = "Create Seashell", icon='HEART')


class OBJECT_PT_FanPanel(bpy.types.Panel):

    bl_label = "Paper Fans"
    bl_idname = "OBJECT_PT_FAN_Panel"
    bl_category = "Seashells"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"

    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        sstool = scene.ss_tool
        
        layout.prop(sstool, "fan_subdiv")
        layout.prop(sstool, "fan_nblades")
        layout.prop(sstool, "fan_anim")
        layout.prop(sstool, "fan_speed")
        
        row = layout.row(align=True)
        row.prop(sstool, "fan_fstart")
        row.prop(sstool, "fan_fend")
        
        layout.operator("create.fan", text = "Create Fan", icon='HEART')


class OBJECT_PT_MiscPanel(bpy.types.Panel):

    bl_label = "Misc"
    bl_idname = "OBJECT_PT_MISC_Panel"
    bl_category = "Seashells"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"

    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        sstool = scene.ss_tool
        
        layout.label(text = sstool.ss_res)
        layout.operator("reset.defaults", text = "Reset Defaults", icon='X')
        layout.operator("wm.url_open", text="Help | Source | Updates", icon='QUESTION').url = "https://github.com/oormicreations/Seashells"
        layout.label(text = sstool.ss_about)
        
        
#---------------------------------------------------------------------------------------------------
# Properties
#---------------------------------------------------------------------------------------------------

class CCProperties(PropertyGroup):
    
    ss_segx: IntProperty(
        name = "Segments X",
        description = "Number of segments in X direction",
        default = 64,
        min=1,
        max=256        
      )   

    ss_segy: IntProperty(
        name = "Segments Y",
        description = "Number of segments in Y direction",
        default = 240,
        min=1,
        max=2048        
      )   
    
    ss_clean: BoolProperty(
        name = "Clean Up",
        description = "Applies all modifiers and deletes deformation lattice",
        default = True
    )
    
    ss_mat: EnumProperty(
        items = [('M1', 'Swirl', 'One'), 
                 ('M2', 'Stripes', 'Two'),
                 ('M3', 'Patchy', 'Three'),
                 ('M4', 'None', "Four")],
        name = "Material")    

    ss_res: StringProperty(
        name = "Result",
        description = "NA",
        default = "Ready..."
      )

    ss_about: StringProperty(
        name = "About",
        description = "NA",
        default = "Oormi Creations | http://oormi.in"
      )

    fan_subdiv: IntProperty(
        name = "Subdivisions",
        description = "Number of subdivisions or mesh resolution",
        default = 20,
        min=1,
        max=100        
      )
       
    fan_nblades: IntProperty(
        name = "Blades",
        description = "Number of fan blades",
        default = 5,
        min=1,
        max=360
      )   

    fan_anim: BoolProperty(
        name = "Animate",
        description = "Animate the fan, make it spin",
        default = True
    )

    fan_speed: IntProperty(
        name = "Speed",
        description = "Number of full rotations in given time range",
        default = 2,
        min=1,
        max=100
      )   

    fan_fstart: IntProperty(
        name = "Start frame",
        description = "Animation start frame",
        default = 1,
        min=1,
        max=100000
      )   

    fan_fend: IntProperty(
        name = "End frame",
        description = "Animation end frame",
        default = 100,
        min=1,
        max=100000
      )   



    
# ------------------------------------------------------------------------
#    Registration
# ------------------------------------------------------------------------

classes = (
    OBJECT_PT_SSPanel,
    OBJECT_PT_FanPanel,
    OBJECT_PT_MiscPanel,
    CCProperties,
    CCS_OT_CCreateSeaShell,
    CCF_OT_CCreateFan,
    CRD_OT_CResetDefaults
)

def register():
    bl_info['blender'] = getattr(bpy.app, "version")
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.ss_tool = PointerProperty(type=CCProperties)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.ss_tool



if __name__ == "__main__":
    register()