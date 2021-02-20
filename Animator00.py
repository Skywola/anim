import bpy
from bpy.types import Panel
from bpy.types import Operator
from bpy.types import Menu
import bpy, math
import mathutils
from mathutils import Vector
from rna_prop_ui import PropertyPanel
from bpy.props import FloatProperty, BoolProperty, StringProperty
context = bpy.context
from collections import deque
import numpy as np

sin = math.sin; cos = math.cos; tan = math.tan
asin = math.asin; acos = math.acos; atan = math.atan
fmod = math.fmod; ceil = math.ceil; floor = math.floor
radians = math.radians
cwmPanel = bpy.context.window_manager # cwmPanel PanelProperty
genProp = bpy.types.WindowManager # genProp General Wm Property

# Initializations
V = Vector;
bpy.context.scene.frame_start = 0

# cycle control - this is the engine that creates the movement!
def clock(cycle=1.0, freq=9, amp=.5):  # Sets the pace
    frame = bpy.context.scene.frame_current
    stp = amp * abs((cycle*frame)/freq % 4 - 2) - amp
    return round(stp, 2)

# add to namespace
bpy.app.driver_namespace['clock'] = clock  # Important

def getSelectedObjectName():
    obj = bpy.context.object
    if(obj):
        return obj.name
    if(obj.parent):  # If user is not in OBJECT MODE, search 
        parent = obj.parent  # up the tree to the root bone.
        if(parent.name in creatures):
            obj.select_set(False)
            bpy.context.view_layer.objects.active = parent
            parent.select_set(True)
            return obj.name
    return 0

def retrieve_class_ob():
    name = getSelectedObjectName()
    for ob in char_obs:
        if('_at' in ob.name):
           name = name + '_at'
        if(ob.name == name):
            return ob

# getEuler output represents:
# bpy.data.objects['rg00biped'].pose.bones["backCenter"]
def getEuler(str_bone_name):  # *** Switching to pose mode must be external
    ob = bpy.context.object
    bone = ob.pose.bones[str_bone_name]
    bone.rotation_mode = 'XYZ'
    return bone

def setDriver(bone, fn="0", axis=0, movementType='rotation_euler'):
    eulerDriver = bone.driver_add(movementType)
    eulerDriver[axis].driver.type = 'SCRIPTED'
    eulerDriver[axis].driver.expression = fn
    return eulerDriver

# Set Driver For Single Axis Only:
def setAxisDriver(euler, fn="0", axis=0, movementType='rotation_euler'):
    edriver = euler.driver_add(movementType, axis)
    edriver.driver.type = 'SCRIPTED'
    edriver.driver.expression = fn
    return edriver

def deselectAll():
    for obj in bpy.context.selected_objects:
        obj.select_set(False)

def deleteAll():
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def set_pivot(coordinates=Vector()):
    ob = bpy.context.active_object
    mw = ob.matrix_world
    o = mw.inverted() @ Vector(coordinates)
    ob.data.transform(Matrix.Translation(-o))
    mw.translation = coordinates
        
# This new function was created because looking up the bone name every time
# a connection fails is far to tedious and time consuming!
def splitname(name):
    names = []
    names.append(name)
    if '_R' in name:
        Lname = name.replace('_R', '_L')
        names.append(Lname)
    if '_L' in name:
        Rname = name.replace('_L', '_R')
        names.append(Rname)
    #
    return names
        
# This is Only for selecting bone PART, not a bone
def selectBonePartByName(name, tail=True):
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.armature.select_all(action='DESELECT')
    data = bpy.context.active_object.data
    bpy.ops.object.mode_set(mode='OBJECT')
    if(tail):
        data.bones[name].select_tail = True
    else:
        data.bones[name].select_head = True
    bpy.ops.object.mode_set(mode='EDIT')

# First input is Class of character 
# vector
# string
def boneExtrude(vector, name):
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.armature.extrude_forked(TRANSFORM_OT_translate={"value":vector})
    bpy.context.active_bone.name = name
    bone = bpy.context.active_bone
    return bone
    
# Make bone creation easy
def createBone(head, tail, name, con=True):
    bpy.ops.object.mode_set(mode='EDIT')
    bData = bpy.context.active_object.data
    bone = bData.edit_bones.new(name)
    bone.head[:] = head
    bone.tail[:] = tail
    bone.use_connect = con
    return bone

def getSceneObjectNumber():
    n = 0
    for o in bpy.data.objects:
        if("at" in o.name):
            n += 1
    return n

def new_armature(name, x=0, y=0, z=0):
    bpy.context.scene.frame_start = 0
    n = getSceneObjectNumber()
    armature = bpy.data.armatures.new(name + str(n) + '_at')  # at = Armature
    rig = bpy.data.objects.new(name, armature) # rig = Armature object
    rig.show_in_front = True
    rig.location = (x, y, z)  # Set armature point locatioon
    # Link to scene
    coll = bpy.context.view_layer.active_layer_collection.collection
    coll.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    bpy.context.view_layer.update()
    return rig


class Character(): 
    def __init__(self, type):
        self.type = type
        self.number = getSceneObjectNumber() # Critical for initial positioning
        self.str_n = str(self.number)
        self.name = type + self.str_n
        self.obs = []  # for objects attached to char, like legs, arms, etc.
        # This is a very special string that produces zero at frame Zero
        self.ZeroAtFrame0 = '*(frame * (1/(frame+.0001)))'
        #
        self.handle = "handle"
        self.handle_grip = .3
        self.handle_tail = .2
        #
        # Movement settings
        self.cycle = 1.0
        self.speed = 0.0
        self.bounce = 1.2
        self.Hip_Rotate = 0.0   # 2.0
        self.Sway_LR = 1.0   
        self.Sway_FB = 1.0
        self.Hip_UD = 2.0 
        self.Shoulder_Rotation = 1.2
        self.Shoulder_UD = 1.0
        self.rotateRangeBack = 1.0
        self.rotateRangeNeck = 1.0
        #
        z = 1.46  # Character location height, constant
        quadz = z - self.handle_tail
        # Get a non-occupied location for character
        y = -.4 * self.number   # y-axis
        mod = fmod(self.number, 2)
        x = .5 * -self.number - mod
        if(mod == 0):
            x = .5 * self.number - mod
        #
        self.J1 = None
        self.J2 = None
        self.J3 = None
        self.J4 = None
        self.J5 = None
        # START BUILD
        deselectAll()
        if(("biped" in self.name) or ("avian" in self.name)):
            self.biped_location = [x, y, z]
            self.biped_backbone_length = [0, 0, 0.14]
            self.biped_shoulderwidth = [0, .3, 0]  # Must be a tuple
            # It's a bird!
            if("avian" in self.name):
                self.biped_backbone_length = [0, 0, 0.09] # Shorter backbones
                self.biped_shoulderwidth = [0, .12, 0]  # Must be a tuple
            self.biped_hipwidth = .12
            # For leg connect hip
            self.biped_hipL = [0, self.biped_hipwidth, 0]   
            self.biped_hipR = [0, -self.biped_hipwidth, 0]
            # Biped - Relative locations for connections
            self.armature = new_armature('armature' +  self.str_n, x, y, z)
            bonehead = [0,0,0] # At armature
            bonetail = [self.handle_tail,0,0]   # self.name
            self.bone = createBone(bonehead, bonetail, 'handle')
            # Relocate character origin to the handle tail, set connection locations
            self.biped_location[0] = self.biped_location[0] + self.handle_tail
            # Set base limb locations
            self.biped_shoulderlocation = self.biped_location
            self.biped_shoulderlocation[0] = self.biped_location[0] + self.biped_shoulderwidth[0]
            #
            # Calculate hip location
            hip_point_z = self.biped_backbone_length[2] * 3
            biped_hiplocation = [x+self.handle_tail, y+self.biped_hipwidth, z-hip_point_z]
            self.biped_hiplocationL = biped_hiplocation
            biped_hiplocation = [x+self.handle_tail, y-self.biped_hipwidth, z-hip_point_z]
            self.biped_hiplocationR = biped_hiplocation
            #
            # Calculate shoulder location for arms
            zloc = self.biped_location[2] + (self.biped_backbone_length[2] * 3)
            shoulder = [x+self.handle_tail, y+self.biped_shoulderwidth[1], zloc]
            self.biped_shoulderlocationL = shoulder
            shoulder = [x+self.handle_tail, -y+self.biped_shoulderwidth[1], zloc]
            self.biped_shoulderlocationR = shoulder
            #
            self.biped_neckbase_location = [x+self.handle_tail, y, zloc + .03]
            #
            # Start back build
            deselectAll()
            self.J1 = boneExtrude(self.biped_backbone_length, "J1")  # vector, name, mirror=False
            self.J2 = boneExtrude(self.biped_backbone_length, "J2")
            self.J3 = boneExtrude(self.biped_backbone_length, "J3")
            #
            self.shoulderJ7L = boneExtrude(self.biped_shoulderwidth, "shoulder.L")
            self.shoulderJ7L_tail = bpy.context.active_bone.tail # Save location for arm connections
            #
            bpy.ops.armature.select_all(action='DESELECT')
            self.J3.select_tail = True
            self.J3.select_head = False
            self.biped_shoulderwidth[1] = self.biped_shoulderwidth[1] * -1 # Other way for right
            self.shoulderJ7R = boneExtrude(self.biped_shoulderwidth, "shoulder.R")
            self.shoulderJ7R_tail = bpy.context.active_bone.tail # Save location for arm connections
            #
            bpy.ops.armature.select_all(action='DESELECT')
            self.J1.select_tail = False
            self.J1.select_head = True
            # Reverse direction of build backbones below (behind) handle
            self.biped_backbone_length[2] = self.biped_backbone_length[2] * -1
            self.biped_backbone_length[0] = self.biped_backbone_length[0] * -1
            self.J4 = boneExtrude(self.biped_backbone_length, "J4")
            self.J5 = boneExtrude(self.biped_backbone_length, "J5")
            self.biped_hipC = boneExtrude(self.biped_backbone_length, "hipC")
            self.biped_hipL = boneExtrude(self.biped_hipL, "hipL")
            self.biped_hipL_tail = bpy.context.active_bone.tail  # Save location for arm connections
            bpy.ops.armature.select_all(action='DESELECT')
            self.biped_hipC.select_tail = True
            self.biped_hipC.select_head = False
            self.biped_hipR = boneExtrude(self.biped_hipR, "hipR")
            self.shoulderJ7R_tail = bpy.context.active_bone.tail # Save location for arm connections
            #
            self.shouldersupport_number = 0
            self.rump_support_number = 0
            bpy.ops.armature.select_all(action='DESELECT') 
        #
        #
        # For quadruped
        self.quadruped_location = None
        self.quadruped_backbone_length = None
        self.quadruped_width = None
        self.quadruped_necklocation = None
        self.quadruped_frontleg_location = None
        #
        quadruped_hiplocation_frontL = None
        quadruped_hiplocation_frontR = None
        quadruped_hiplocation_backL = None
        quadruped_hiplocation_backR = None
        #
        self.quadruped_backleg_location = None
        self.quadruped_hipL = None
        self.quadruped_hipR = None
        self.quadruped_shoulderlocation = None
        self.quadruped_J1 = None
        self.quadruped_J2 = None
        self.quadruped_J3 = None
        self.quadruped_J7L = None
        self.quadruped_J7L_tail = None
        self.quadruped_J7R = None
        self.quadruped_J4 = None
        self.quadruped_J5 = None
        self.quadruped_hipC = None
        self.quadruped_hipL_tail = None
        self.quadruped_J7R_tail = None
        self.shouldersupport_number = None
        self.rump_support_number = None
        #
        if("quadruped" in self.name):
            self.quadruped_location = [x, y, quadz]
            self.quadruped_backbone_length = [0, 0, 0.14]
            self.quadruped_width = [0,.2,0]  # shoulder and hip width 
            # Quad armature is lower
            armature = new_armature('armature' +  self.str_n, x, y, quadz)
            #
            bonehead = [0,0,0] # At armature
            bonetail = [0,0,-self.handle_tail]    
            self.bone = createBone(bonehead, bonetail, self.name + '_bone')
            #
            # Front legs location
            hip_point_x = self.quadruped_backbone_length[2] * 3
            frontL = [x+hip_point_x, y+self.quadruped_width[1], quadz-.21]
            self.quadruped_hiplocation_frontL = frontL
            frontR = [x+hip_point_x, y-self.quadruped_width[1], quadz-.21]
            self.quadruped_hiplocation_frontR = frontR
            #
            # Back legs location
            hip_point_x = self.quadruped_backbone_length[2] * 3
            backL = [x-hip_point_x, y+self.quadruped_width[1], quadz-.21]
            self.quadruped_hiplocation_backL = backL
            backR = [x-hip_point_x, y-self.quadruped_width[1], quadz-.21]
            self.quadruped_hiplocation_backR = backR
            #
            # quadruped - Relative locations for connections
            self.quadruped_necklocation = [x+hip_point_x, y, quadz-.21]
            #
            # Change to Horizontal orientation
            temp = self.quadruped_backbone_length[2]
            self.quadruped_backbone_length[2] = 0
            self.quadruped_backbone_length[0] = temp
            # Start back build
            deselectAll()
            self.quadruped_J1 = boneExtrude(self.quadruped_backbone_length, self.name + "J1")  # vector, name, mirror=False
            self.quadruped_J2 = boneExtrude(self.quadruped_backbone_length, self.name + "J2")
            self.quadruped_J3 = boneExtrude(self.quadruped_backbone_length, self.name + "J3")
            #
            self.quadruped_J7L = boneExtrude(self.quadruped_width, "shoulder.L")
            self.quadruped_J7L_tail = bpy.context.active_bone.tail # Save location for arm connections
            #
            bpy.ops.armature.select_all(action='DESELECT')
            self.quadruped_J3.select_tail = True
            self.quadruped_J3.select_head = False
            self.quadruped_width[1] = self.quadruped_width[1] * -1
            self.quadruped_J7R = boneExtrude(self.quadruped_width, "shoulder.R")
            self.quadruped_J7R_tail = bpy.context.active_bone.tail # Save location for arm connections
            #
            bpy.ops.armature.select_all(action='DESELECT')
            self.quadruped_J1.select_tail = False
            self.quadruped_J1.select_head = True
            # Reverse direction of build backbones below (behind) handle
            self.quadruped_backbone_length[2] = self.quadruped_backbone_length[2] * -1
            self.quadruped_backbone_length[0] = self.quadruped_backbone_length[0] * -1
            self.quadruped_J4 = boneExtrude(self.quadruped_backbone_length, self.name + "J4")
            self.quadruped_J5 = boneExtrude(self.quadruped_backbone_length, self.name + "J5")
            self.quadruped_hipC = boneExtrude(self.quadruped_backbone_length, "hipC")
            self.quadruped_width[1] = self.quadruped_width[1] * -1
            self.quadruped_hipL = boneExtrude(self.quadruped_width, "hipL")      
            self.quadruped_hipL_tail = bpy.context.active_bone.tail  # Save location for arm connections
            bpy.ops.armature.select_all(action='DESELECT')
            self.quadruped_hipC.select_tail = True
            self.quadruped_hipC.select_head = False
            self.quadruped_width[1] = self.quadruped_width[1] * -1
            self.quadruped_hipR = boneExtrude(self.quadruped_width, "hipR")
            self.quadruped_J7R_tail = bpy.context.active_bone.tail # Save location for arm connections
            bpy.ops.armature.select_all(action='DESELECT')
        #
        # For Bird
        if("avian" in self.name):
            bpy.ops.armature.select_all(action='SELECT')
            context.view_layer.objects.active.rotation_euler.y = 0.791
            context.view_layer.objects.active.location.z = 1.33
            bpy.ops.armature.select_all(action='DESELECT')
            self.biped_hipL.select_tail = True
            #self.biped_hipL.select_head = False
            self.biped_hipL.tail[0] = .312
            self.biped_hipL.tail[1] = .18 
            self.biped_hipL.tail[2] = -.3
            bpy.ops.armature.select_all(action='DESELECT')
            self.biped_hipR.select_tail = True
            self.biped_hipR.select_head = False
            self.biped_hipR.tail[0] = .312
            self.biped_hipR.tail[1] = -.18
            self.biped_hipR.tail[2] = -.31
            bpy.ops.armature.select_all(action='DESELECT')
            self.backJ3.select_tail = True
            breast = [[.08,0,-.08],[-.04,0,-.1],[-.07,0,-.09],[-.07,0,-.08],[-.09,0,-.05]]
            self.collar = boneExtrude(breast[0], "collar")
            self.breast = boneExtrude(breast[1], "breast")
            self.breastbottom = boneExtrude(breast[2], "breastbottom")
            self.stomachtop = boneExtrude(breast[3], "stomachtop")
            self.stomachbottom = boneExtrude(breast[4], "stomachbottom")
        #
        bpy.ops.object.mode_set(mode='POSE')
        self.char_bones = []
        for bone in self.armature.pose.bones:
            self.char_bones.append(bone)

class Leg():
    def __init__(self, type, xyz, leftright='left', frontback='front'):
        self.number = str(getSceneObjectNumber())
        self.str_n = str(self.number)
        self.location = xyz
        self.frontback = frontback  # used for quadruped type creatures
        self.type = type
        self.cycledir = 1 # 1 or -1 to sync with opposite leg
        self.cyclephase = 0  # 0.0 - 1.0  Not yet used
        self.y = .12  # y sets for left or right leg
        #
        # This is a very special string that produces zero at frame Zero
        self.ZeroAtFrame0 = '*(frame * (1/(frame+.0001)))'
        #
        self.gait = 0  #  gait 0-4 pose, walk, run, trot, pace
        #
        # Defaults for walk
        self.rotatePositionFemur = 0.1
        self.rotatePositionTibia = .4
        self.rotatePositionAnkle = 0.1
        self.rotatePositionToe = -.1
        #
        self.rotateRangeFemur = 1.0
        self.rotateRangeTibia = 1.0   
        self.rotateRangeAnkle = 0.8
        self.rotateRangeToe = 1.0
        #
        side = "L"
        if(leftright=='right'):
            side = "R"
        name = self.name = 'leg' + self.str_n
        #
        # deselectAll()
        # bpy.ops.armature.select_all(action='DESELECT')
        if(('biped' in self.type) or ('quadruped' in self.type)):
            # Set initial Armature location
            x = self.location[0]
            y = self.location[1]
            z = self.location[2]
            if(side == "R"):
                y = self.location[1] * -1
            self.armature = new_armature('armature' +  self.str_n, x,y,z)
            start = [0, 0, 0] # Start at armature location
            J1 = [0, 0, -.32] # Relative to armature location
        if('biped' in self.type):
            biped = [start, J1, [0, 0, -.24], [0, 0, -.2], [0, 0, -.14], [.18, 0, -.06], [.08, 0, 0], [.08, 0, 0], [-.2, 0, -.01]]
            self.J1 = createBone(biped[0], biped[1], name + '_J1' + side)
            self.J2 = boneExtrude(biped[2], name + "_J2" + side)
            self.J3 = boneExtrude(biped[3], name + "_J3" + side)
            self.J4 = boneExtrude(biped[4], name + "_J4" + side)
            self.J5 = boneExtrude(biped[5], name + "_J5" + side)
            self.J6 = boneExtrude(biped[6], name + "_J6" + side)
            bpy.ops.armature.select_all(action='DESELECT')
            self.J5.select_tail = True    
            self.J5.select_head = False
            self.J7 = boneExtrude(biped[7], name + "_J7" + side)
            bpy.ops.armature.select_all(action='DESELECT')
            self.J5.select_tail = True    # Build heal reinforce
            self.J5.select_head = False        
            self.J8 = boneExtrude(biped[8], name + "_J8" + side)
            deselectAll()  #bpy.ops.armature.select_all(action='DESELECT')
        if('quadruped' in self.type):
            leg = [start, J1, [-.12, 0, -.27], [.06, 0, -.25], [.04, 0, -.08], [.05, 0, -.05], [.03, 0, -.054],[.07, 0, -.05]]
            if(self.frontback=='front'):
                leg[2] = [0, 0, -.27]
                leg[3] = [0, 0, -.25]
            self.J1 = createBone(leg[0], leg[1], name + '_J1' + side)
            self.J2 = boneExtrude(leg[2], name + "_J2" + side)
            self.J3 = boneExtrude(leg[3], name + "_J3" + side)
            self.J4 = boneExtrude(leg[4], name + "_J4" + side)
            self.J5 = boneExtrude(leg[5], name + "_J5" + side)
        #
        if('avian' in self.type):
            # Set initial Armature location
            x = self.location[0] -.194
            y = self.location[1] + .18
            z = self.location[2] -.569
            if(leftright == 'right'):
                y = self.location[1] - .18
            self.armature = new_armature('armature' +  self.str_n, x,y,z)
            birdleg = [[0,0,0], [.01, 0, -0.12],[-0.02, 0, -0.12],[-0.02, 0, -0.12],[-0.02, 0, -0.12],[.01, 0, -.1],[.01, 0, -.1],[.01, 0, -.1],[0.003, 0, -.06]]
            self.hip = createBone(birdleg[0], birdleg[1], name + 'hip')
            self.J1 = boneExtrude(birdleg[2], name + "_J1" + side)
            self.J2 = boneExtrude(birdleg[3], name + "_J2" + side)
            self.J3 = boneExtrude(birdleg[4], name + "_J3" + side)
            self.J4 = boneExtrude(birdleg[5], name + "_J4" + side)
            self.J5 = boneExtrude(birdleg[6], name + "_J5" + side)
            self.J6 = boneExtrude(birdleg[7], name + "_J6" + side)
            self.J7 = boneExtrude(birdleg[8], name + "_J7" + side)
            spur = [[-0.07, -.016, .01],[-0.07, -.015, 0],[-0.07, -.015, 0],[-0.07, -.015, 0]]
            if(leftright == 'right'):
                spur = [[-0.07, .016, .01],[-0.07, .015, 0],[-0.07, .015, 0],[-0.07, .015, 0]]
            self.spurJ1 = boneExtrude(spur[0], name + "_spurJ1")
            self.spurJ2 = boneExtrude(spur[1], name + "_spurJ2")
            self.spurJ3 = boneExtrude(spur[2], name + "_spurJ3")
            self.spurJ4 = boneExtrude(spur[3], name + "_spurJ4")
            bpy.ops.armature.select_all(action='DESELECT')
            self.J7.select_tail = True
            self.toeJ1 = boneExtrude([.07, 0, 0], name + "_toeJ1") # Center toe
            self.toeJ2 = boneExtrude([.07, 0, 0], name + "_toeJ2")
            self.toeJ3 = boneExtrude([.07, 0, 0], name + "_toeJ3")
            self.toeJ4 = boneExtrude([.07, 0, 0], name + "_toeJ4")
            bpy.ops.armature.select_all(action='DESELECT')
            self.J7.select_tail = True
            y = -.0358
            if(leftright == 'right'):
                y = y * -1
            self.toeJ1L = boneExtrude([.066, y, 0], name + "_toeJ1L")
            self.toeJ2L = boneExtrude([.066, y, 0], name + "_toeJ2L")
            self.toeJ3L = boneExtrude([.066, y, 0], name + "_toeJ3L")
            self.toeJ4L = boneExtrude([.066, y, 0], name + "_toeJ4L")
            bpy.ops.armature.select_all(action='DESELECT')
            self.J7.select_tail = True
            y = .0358
            if(leftright == 'right'):
                y = y * -1
                y = y * -1
            self.toeJ1R = boneExtrude([.066, y, 0], name + "_toeJ1R")
            self.toeJ2R = boneExtrude([.066, y, 0], name + "_toeJ2R")
            self.toeJ3R = boneExtrude([.066, y, 0], name + "_toeJ3R")
            self.toeJ4R = boneExtrude([.066, y, 0], name + "_toeJ4R")
        #
        bpy.ops.object.mode_set(mode='POSE')
        self.leg_bones = []
        for bone in self.armature.pose.bones:
            self.leg_bones.append(bone)
 

# creeteBone(name="boneName", VHead=(0, 0, 0), VTail=(.1, 0, .1), roll=0, con=False):
class Arm():
    def __init__(self, type, xyz, leftright='left'):
        self.number = getSceneObjectNumber()
        self.str_n = str(self.number)
        self.type = type
        self.location = xyz
        self.leftright = leftright
        self.armature = None
        self.cycledir = 1 # 1 or -1 to sync with opposite arm
        self.cyclephase = 0  # 0.0 - 1.0  Not yet used
        # This is a very special string that produces zero at frame Zero
        self.ZeroAtFrame0 = '*(frame * (1/(frame+.0001)))'
        #
        self.rotatePositionHumerus = 0.0
        self.rotateRangeHumerus = 1.0
        self.rotatePositionUlna = .24   #0.0
        self.rotateRangeUlna = 1.0
        #
        side = "L"
        if(leftright=='right'):
            side = "R"
        name = self.name = 'arm' + self.str_n
        #
        deselectAll()
        x = xyz[0]; y = xyz[1]; z = xyz[2]
        if(self.leftright == 'right'):
            y = -y 
        self.armature = new_armature('armature' +  self.str_n, x,y,z)
        start = [0, 0, 0] # Start at armature location
        J1 = [0, .12, 0] # Relative to armature location  # [.3, .1, .5],[.3, .22, .5]
        arm = [start, J1,[0, .14, 0],[0, .08, 0],[0, .1, 0],
              [0, .1, 0],[0, .098, 0],[0, .05, 0],[0, .044, 0],[0, .02, 0],      # MiddleJ1-4
              [.03, .098, -.006],[.011, .032, 0],[.01, .024, 0],[.008, .02, 0],  # IndexJ1-4
              [-.02, .098, -.006],[-.01, .042, 0],[-.007, .032, 0],[-.004, .02, 0],  # RingJ1-4 
              [-.046, .095, -.006],[-.016, .024, 0],[-.012, .02, 0],[-.01, .02, 0],  # PinkyJ1-4 
              [.008, .002, 0],[.044, .038, -0.01],[.02, .032, -0.006],[.01, .02, 0]] # ThumbJ1-4
        #
        if(self.leftright == 'right'):
            for coord in arm:
                coord[1] = coord[1] * -1
        self.J1 = createBone(arm[0], arm[1], self.name + 'J1')
        self.J2 = boneExtrude(arm[2], name + "J2")
        self.J3 = boneExtrude(arm[3], name + "J3")
        self.J4 = boneExtrude(arm[4], name + "J4")
        self.J5 = boneExtrude(arm[5], name + "J5")
        self.J6 = boneExtrude(arm[6], name + "J6")
        self.J7 = boneExtrude(arm[7], name + "J7")
        self.J8 = boneExtrude(arm[8], name + "J8")
        self.J9 = boneExtrude(arm[9], name + "J9")
        bpy.ops.armature.select_all(action='DESELECT')
        self.J5.select_tail = True
        self.J5.select_head = False
        self.IJ1 = boneExtrude(arm[10], name + "IJ1")
        self.IJ2 = boneExtrude(arm[11], name + "IJ2")
        self.IJ3 = boneExtrude(arm[12], name + "IJ3")
        self.IJ4 = boneExtrude(arm[13], name + "IJ4")
        bpy.ops.armature.select_all(action='DESELECT')
        self.J5.select_tail = True
        self.J5.select_head = False
        self.RJ1 = boneExtrude(arm[14], name + "RJ1")
        self.RJ2 = boneExtrude(arm[15], name + "RJ2")
        self.RJ3 = boneExtrude(arm[16], name + "RJ3")
        self.RJ4 = boneExtrude(arm[17], name + "RJ4")
        bpy.ops.armature.select_all(action='DESELECT')
        self.J5.select_tail = True
        self.J5.select_head = False
        self.PJ1 = boneExtrude(arm[18], name + "PJ1")
        self.PJ2 = boneExtrude(arm[19], name + "PJ2")
        self.PJ3 = boneExtrude(arm[20], name + "PJ3")
        self.PJ4 = boneExtrude(arm[21], name + "PJ4")
        bpy.ops.armature.select_all(action='DESELECT')
        self.J5.select_tail = True
        self.J5.select_head = False
        self.TJ1 = boneExtrude(arm[22], name + "TJ1")
        self.TJ2 = boneExtrude(arm[23], name + "TJ2")
        self.TJ3 = boneExtrude(arm[24], name + "TJ3")
        self.TJ4 = boneExtrude(arm[25], name + "TJ4")
        #
        bpy.ops.object.mode_set(mode='POSE')
        self.arm_bones = []
        for bone in self.armature.pose.bones:
            self.arm_bones.append(bone)
        #
        deselectAll()

# Head and neck are considered one unit
class Head():
    def __init__(self, type, xyz):
        if(bpy.context.mode != 'OBJECT'):
            bpy.ops.object.mode_set(mode='OBJECT')
        self.number = getSceneObjectNumber()
        self.str_n = str(self.number)
        self.type = type
        self.name = self.type + self.str_n + 'head'
        self.headbase = ""
        self.xyz = xyz
        self.location = xyz
        self.location = None
        self.cycledir = 1 # 1 or -1 to sync with opposite arm
        self.cyclephase = 0  # 0.0 - 1.0  Not yet used
        # This is a very special string that produces zero at frame Zero
        self.ZeroAtFrame0 = '*(frame * (1/(frame+.0001)))'
        #
        if(("biped" in self.type) or ("quadruped" in self.type)):
            deselectAll()
            x = self.xyz[0]
            y = self.xyz[1]
            z = self.xyz[2]
            self.armature = new_armature('armature' +  self.str_n, x,y,z)
            #
            start = [0, 0, 0] # Start at armature location
            J1 = [0, 0, .12] # Relative to armature location  # [.3, 0, .5],[.3, 0, .54],
            head = [start, J1,[.01, 0, .03],[.01, 0, .03],[0, 0, .024],
                     [0, 0, .09],[.12, 0, .0], [.02, 0, -.02],[0, 0, .04],[-.05, 0, 0],
                     [.08, 0, .09],[.1, .03, 0],[.03, 0, 0], [.1, -.03, 0],[.03, 0, 0],
                     [.02, 0, .04],[.04, .05, 0],[.07, -.04, 0],[.04, -.05, 0],[.07, .04, 0],
                     [.02, 0, 0],[.04, .05, 0],[.07, -.04, 0],[.04, -.05, 0],[.07, .04, 0]]
        #
        if("quadruped" in self.type):
            head[0] = start
            head[1] = [.22, 0, .18] # non-relative
            head[2] = [.12, 0, .12]
            head[3] = [.12, 0, .12]
        if(("biped" in self.type) or ("quadruped" in self.type)):
            self.J1 = createBone(head[0], head[1], self.name + 'J1')
            self.J2 = boneExtrude(head[2], self.name + "J2")
            self.J3 = boneExtrude(head[3], self.name + "J3")
            self.J4 = boneExtrude(head[4], self.name + "J4")
            self.J5 = boneExtrude(head[5], self.name + "J5")
            bpy.ops.armature.select_all(action='DESELECT')
            self.J5.select_tail = True 
            self.J5.select_head = False
            self.J6 = boneExtrude(head[6], self.name + "J6")
            self.J7 = boneExtrude(head[7], self.name + "J7")
            bpy.ops.armature.select_all(action='DESELECT')
            self.J5.select_tail = True 
            self.J5.select_head = False
            self.J8 = boneExtrude(head[8], self.name + "J8")
            self.J9 = boneExtrude(head[9], self.name + "J9")
            self.J10 = boneExtrude(head[10], self.name + "J10")
            bpy.ops.armature.select_all(action='DESELECT')
            self.J8.select_tail = True
            self.J8.select_head = False
            self.J11 = boneExtrude(head[11], self.name + "J11")
            self.J12 = boneExtrude(head[12], self.name + "J12")
            bpy.ops.armature.select_all(action='DESELECT')
            self.J8.select_tail = True
            self.J8.select_head = False
            self.J13 = boneExtrude(head[13], self.name + "J13")
            self.J14 = boneExtrude(head[14], self.name + "J14")
            bpy.ops.armature.select_all(action='DESELECT')
            self.J4.select_tail = True
            self.J4.select_head = False
            # Upper Jaw L
            self.J15 = boneExtrude(head[15], self.name + "J15")
            self.J16 = boneExtrude(head[16], self.name + "J16")
            self.J17 = boneExtrude(head[17], self.name + "J17")
            bpy.ops.armature.select_all(action='DESELECT')
            self.J15.select_tail = True
            self.J15.select_head = False
            # Upper Jaw R
            self.J18 = boneExtrude(head[18], self.name + "J18")
            self.J19 = boneExtrude(head[19], self.name + "J19")       
            bpy.ops.armature.select_all(action='DESELECT')
            self.J4.select_tail = True
            self.J4.select_head = False
            # Upper Jaw L
            self.J20 = boneExtrude(head[20], self.name + "J20")
            self.J21 = boneExtrude(head[21], self.name + "J21")
            self.J22 = boneExtrude(head[22], self.name + "J22")
            bpy.ops.armature.select_all(action='DESELECT')
            self.J20.select_tail = True
            self.J20.select_head = False
            # Upper Jaw R
            self.J23 = boneExtrude(head[23], self.name + "J23")
            self.J24 = boneExtrude(head[24], self.name + "J24") 
            bpy.ops.armature.select_all(action='DESELECT')
        #
        #
        if("avian" in self.type):
            deselectAll()
            x = xyz[0] + .132
            y = xyz[1]
            z = xyz[2] - .382
            self.armature = new_armature('armature_head' + self.str_n, x,y,z)
            #
            start = [0, 0, 0]
            neckbase = [.06,0,.02]
            neck = [start, neckbase, [0.06,0,.02],[0.06,0,.02],[0.026,0,.032],[0.020,0,.039],[0,0,.04],[-.03,0,.052],[.16,0,.03],[-.1,0,.07]]
            self.neckbase = createBone(start, neckbase, 'neckbase')
            self.neckJ1 = boneExtrude(neck[2], "neckJ1")
            self.neckJ2 = boneExtrude(neck[3], "neckJ2")
            self.neckJ3 = boneExtrude(neck[4], "neckJ3")
            self.neckJ4 = boneExtrude(neck[5], "neckJ4")
            self.neckJ5 = boneExtrude(neck[6], "neckJ5")
            self.neckJ6 = boneExtrude(neck[7], "neckJ6")
            self.neckJ7 = boneExtrude(neck[8], "neckJ7")
            self.neckJ8 = boneExtrude(neck[9], "neckJ8")
            bpy.ops.armature.select_all(action='DESELECT')
            self.neckJ5.select_tail = True
            jaw = [[.08,0,-.03],[.08,0,.07],[.16,0,0],[.21,0,-.04],[.03,0,-.05],[.11,0,.058],[.13,0,-.031]]
            self.jawbase = boneExtrude(jaw[0], "jawbase")
            self.beakbasetop = boneExtrude(jaw[1], "beakbasetop")
            self.beakbacktop = boneExtrude(jaw[2], "beakbacktop")
            self.beakfronttop = boneExtrude(jaw[3], "beakfronttop")
            bpy.ops.armature.select_all(action='DESELECT')
            self.jawbase.select_tail = True
            self.jawconnect = boneExtrude(jaw[4], "jawconnect")
            self.basebottom = boneExtrude(jaw[5], "basebottom")
            self.basemidbottom = boneExtrude(jaw[6], "basemidbottom")
            self.beakbasefront = boneExtrude(jaw[6], "beakbasefront")
            bpy.ops.armature.select_all(action='DESELECT')
            self.neckJ6.select_tail = True
            eyes = [[.095,.05,0],[.02,0,0],[.095,-.05,0]]
            self.eyebaseL = boneExtrude(eyes[0], "eyebaseL")
            self.eyeL = boneExtrude(eyes[1], "eyeL")
            bpy.ops.armature.select_all(action='DESELECT')
            self.neckJ6.select_tail = True
            self.eyebaseR = boneExtrude(eyes[2], "eyebaseR")
            self.eyeR = boneExtrude(eyes[1], "eyeR")
        bpy.ops.armature.select_all(action='DESELECT')
        #
        bpy.ops.object.mode_set(mode='POSE')
        self.head_bones = []
        for bone in self.armature.pose.bones:
            self.head_bones.append(bone)
        #
        deselectAll()


class Tail():
    def __init__(self, type, xyz):
        if(bpy.context.mode != 'OBJECT'):
            bpy.ops.object.mode_set(mode='OBJECT')
        self.number = getSceneObjectNumber()
        self.str_n = str(self.number)
        self.type = type
        self.name = self.type + str(self.n) + 'tail'
        self.xyz = xyz
        self.location = xyz
        self.location = None
        # This is a very special string that produces zero at frame Zero
        self.ZeroAtFrame0 = '*(frame * (1/(frame+.0001)))'
        #
        deselectAll()
        x = self.xyz[0] - .253
        y = self.xyz[1]
        z = self.xyz[2] - .461
        self.armature = new_armature('armature_tail' + self.str_n, x,y,z)
        #
        start = [0, 0, 0]
        tailJ0 = [-.11  , 0, -.05]
        tail = [[-0.1, 0, -.04],[-.1, 0, 0],[-.06, 0, 0],[-.08, 0, 0]]
        #
        self.J0 = createBone(start, tailJ0, self.name + 'J0')
        self.J1 = boneExtrude(tail[0], self.name + "J1")
        self.J2 = boneExtrude(tail[1], self.name + "J2")
        self.J3 = boneExtrude(tail[2], self.name + "J3")
        self.featherC = boneExtrude(tail[3], self.name + "featherC")
        bpy.ops.armature.select_all(action='DESELECT')
        self.J3.select_tail = True
        featherbase = [[0.025, .022, 0],[0.025, -.022, 0]]
        self.fb1L = boneExtrude(featherbase[0], self.name + "_fb1L")
        self.fb2L = boneExtrude(featherbase[0], self.name + "_fb2L")
        self.fb3L = boneExtrude(featherbase[0], self.name + "_fb3L")
        self.fb4L = boneExtrude(featherbase[0], self.name + "_fb4L")
        bpy.ops.armature.select_all(action='DESELECT')
        self.J3.select_tail = True
        self.fb1R = boneExtrude(featherbase[1], self.name + "_fb1R")
        self.fb2R = boneExtrude(featherbase[1], self.name + "_fb2R")
        self.fb3R = boneExtrude(featherbase[1], self.name + "_fb3R")
        self.fb4R = boneExtrude(featherbase[1], self.name + "_fb4R")
        self.feather4R = boneExtrude([-.08, 0, 0], self.name + "feather4R")
        bpy.ops.armature.select_all(action='DESELECT')
        self.fb3R.select_tail = True  
        self.feather3R = boneExtrude([-.08, 0, 0], self.name + "feather3R")
        bpy.ops.armature.select_all(action='DESELECT')
        self.fb2R.select_tail = True  
        self.feather2R = boneExtrude([-.08, 0, 0], self.name + "feather2R")
        bpy.ops.armature.select_all(action='DESELECT')
        self.fb1R.select_tail = True  
        self.feather1R = boneExtrude([-.08, 0, 0], self.name + "feather1R")
        #
        bpy.ops.armature.select_all(action='DESELECT')
        self.fb4L.select_tail = True
        self.feather4L = boneExtrude([-.08, 0, 0], self.name + "feather4L")
        bpy.ops.armature.select_all(action='DESELECT')
        self.fb3L.select_tail = True
        self.feather3L = boneExtrude([-.08, 0, 0], self.name + "feather3L")
        bpy.ops.armature.select_all(action='DESELECT')
        self.fb2L.select_tail = True  
        self.feather2L = boneExtrude([-.08, 0, 0], self.name + "feather2L")
        bpy.ops.armature.select_all(action='DESELECT')
        self.fb1L.select_tail = True  
        self.feather1L = boneExtrude([-.08, 0, 0], self.name + "feather1L")
        bpy.ops.armature.select_all(action='DESELECT')
        deselectAll()

        
class Wing():
    def __init__(self, type, xyz, leftright='left', frontback='front'):
        self.number = str(getSceneObjectNumber())
        self.str_n = str(self.number)
        self.armature = None
        self.xyz = xyz
        self.location = xyz
        self.type = type
        self.name = self.type + self.str_n + "_" + leftright + "_" + 'wing'
        self.cycledir = 1 # 1 or -1 to sync with opposite wing
        self.cyclephase = 0  # 0.0 - 1.0  Not yet used
        self.y = .12  # y sets for left or right wing
        # This is a very special string that produces zero at frame Zero
        self.ZeroAtFrame0 = '*(frame * (1/(frame+.0001)))'
        #
        deselectAll()
        bpy.ops.armature.select_all(action='DESELECT')
        # Set initial Armature location
        x = self.xyz[0] + .132
        y = self.xyz[1] + .12
        z = self.xyz[2] - .082
        if(leftright == 'right'):
            y = self.xyz[1] - .12
        self.armature = new_armature('armature_wing' + self.str_n, x,y,z)
        wing = [[0,0,0],[0, .036, 0],[0, .03, 0],[0, .02, 0],[0, .08, 0]]
        if(leftright == 'right'):
            wing = [[0,0,0],[0, -.036, 0],[0, -.03, 0],[0, -.02, 0],[0, -.08, 0]]
        self.wingJ0 = createBone(wing[0], wing[1], self.name + 'wingJ0')
        self.wingJ1 = boneExtrude(wing[1], self.name + "wingJ1")
        self.wingJ2 = boneExtrude(wing[1], self.name + "wingJ2")
        self.wingJ3 = boneExtrude(wing[2], self.name + "wingJ3")
        self.wingJ4 = boneExtrude(wing[2], self.name + "wingJ4")
        self.wingJ5 = boneExtrude(wing[2], self.name + "wingJ5")
        self.wingJ6 = boneExtrude(wing[2], self.name + "wingJ6")
        self.wingJ7 = boneExtrude(wing[2], self.name + "wingJ7")
        self.wingJ8 = boneExtrude(wing[2], self.name + "wingJ8")
        self.wingJ9 = boneExtrude(wing[2], self.name + "wingJ9")
        self.wingJ10 = boneExtrude(wing[3], self.name + "wingJ10")
        self.wingJ11 = boneExtrude(wing[3], self.name + "wingJ11")
        self.wingJ12 = boneExtrude(wing[3], self.name + "wingJ12")
        self.wingJ13 = boneExtrude(wing[3], self.name + "wingJ13")
        self.wingJ14 = boneExtrude(wing[3], self.name + "wingJ14")
        self.wingJ15 = boneExtrude(wing[4], self.name + "wingJ15")
        #
        # Feathers
        feathers = [[-.05, 0, 0],[-.05, .002, 0],[-.05, .004, 0],[-.05, .006, 0],[-.05, .008, 0],
[-.05, .01, 0],[-.05, .012, 0],[-.05, .014, 0],[-.05, .018, 0],[-.05, .022, 0],[-.05, .026, 0],
[-.05, .03, 0],[-.05, .044, 0],[-.04, .06, 0],[-.03, .075, 0]]
        if(leftright == 'right'):
            for item in feathers:
                item[1] = item[1] * -1
        bpy.ops.armature.select_all(action='DESELECT')
        self.wingJ0.select_tail = True
        self.feather1 = boneExtrude(feathers[0], self.name + "feather1")
        bpy.ops.armature.select_all(action='DESELECT')
        self.wingJ1.select_tail = True
        self.feather2 = boneExtrude(feathers[1], self.name + "feather2")
        bpy.ops.armature.select_all(action='DESELECT')
        self.wingJ2.select_tail = True
        self.feather3 = boneExtrude(feathers[2], self.name + "feather3")
        bpy.ops.armature.select_all(action='DESELECT')
        self.wingJ3.select_tail = True
        self.feather4 = boneExtrude(feathers[3], self.name + "feather4")
        bpy.ops.armature.select_all(action='DESELECT')
        self.wingJ4.select_tail = True
        self.feather5 = boneExtrude(feathers[4], self.name + "feather5")
        bpy.ops.armature.select_all(action='DESELECT')
        self.wingJ5.select_tail = True
        self.feather6 = boneExtrude(feathers[5], self.name + "feather6")
        bpy.ops.armature.select_all(action='DESELECT')
        self.wingJ6.select_tail = True
        self.feather7 = boneExtrude(feathers[6], self.name + "feather7")
        bpy.ops.armature.select_all(action='DESELECT')
        self.wingJ7.select_tail = True
        self.feather8 = boneExtrude(feathers[7], self.name + "feather8")
        bpy.ops.armature.select_all(action='DESELECT')
        self.wingJ8.select_tail = True
        self.feather9 = boneExtrude(feathers[8], self.name + "feather9")
        bpy.ops.armature.select_all(action='DESELECT')
        self.wingJ9.select_tail = True
        self.feather10 = boneExtrude(feathers[9], self.name + "feather10")
        bpy.ops.armature.select_all(action='DESELECT')
        self.wingJ10.select_tail = True
        self.feather11 = boneExtrude(feathers[10], self.name + "feather11")
        bpy.ops.armature.select_all(action='DESELECT')
        self.wingJ11.select_tail = True
        self.feather12 = boneExtrude(feathers[11], self.name + "feather12")
        bpy.ops.armature.select_all(action='DESELECT')
        self.wingJ12.select_tail = True
        self.feather13 = boneExtrude(feathers[12], self.name + "feather13")
        bpy.ops.armature.select_all(action='DESELECT')
        self.wingJ13.select_tail = True
        self.feather14 = boneExtrude(feathers[13], self.name + "feather14")
        bpy.ops.armature.select_all(action='DESELECT')
        deselectAll()


a = "avian"  # AKA bird
b = "biped"    # Done
c = "centaur"
q = "quadruped"   # Done
s = "spider"
creatures = [a,b,c,q,s]

# Legs
left = 'left'
right = 'right'
front = 'front'
back = 'back'

# Tail, Default is bird tail
straight = 'straight'  # Straight tail


origin = [0,0,0]
# These are roughly the locations near the origin for 
# various parts for ad hoc building activities.
head = [.2,0, 1.9]
hip = [.2,.12, 1.04]
shoulder = [.2,.31, 1.88]



