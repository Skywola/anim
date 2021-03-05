import bpy
from bpy.types import Panel
from bpy.types import Operator
from bpy.types import Menu
import bpy, math
import mathutils
from rna_prop_ui import PropertyPanel
from bpy.props import FloatProperty, BoolProperty, StringProperty
context = bpy.context
from collections import deque
import numpy as np
from mathutils import Vector

sin = math.sin; cos = math.cos; tan = math.tan
asin = math.asin; acos = math.acos; atan = math.atan
fmod = math.fmod; ceil = math.ceil; floor = math.floor
radians = math.radians
cwmPanel = bpy.context.window_manager # cwmPanel PanelProperty
genProp = bpy.types.WindowManager # genProp General Wm Property

# Initializations
bpy.context.scene.frame_start = 0

class Util():
    def __init__(self):
        self.character_count = 0

util = Util()

class Character(): 
    def __init__(self, type):
        util.character_count +=1 
        self.type = type
        self.number = getSceneObjectNumber() # Critical for initial positioning
        self.str_n = str(self.number)
        self.name = type + self.str_n
        self.obs = []  # for objects attached to char, like legs, arms, etc.
        # This is a very special string that produces zero at frame Zero
        self.ZeroAtFrame0 = '*(frame * (1/(frame+.0001)))'
        # Movement settings
        self.cycle = 1.0
        self.speed = 0.0
        self.bounce = 1.2
        self.hip_rotate = 0.0   # 2.0
        self.sway_LR = 1.0 
        self.sway_FB = 1.0
        self.hip_UD = 2.0 
        self.shoulder_FB = 1.2
        self.shoulder_UD = 1.0
        self.rotateRangeBack = 1.0
        self.rotateRangeNeck = 1.0
        #
        self.z = 1.32  # Character location height, constant
        self.y = -.4 * self.number   # y-axis  Get a non-occupied location for character
        mod = fmod(self.number, 2)
        self.x = .5 * -self.number - mod
        if(mod == 0):
            self.x = .5 * self.number - mod
        self.location = Vector((self.x,self.y,self.z))
        # Properties for specific character build, initial listing is for biped
        self.hip_width = .12
        self.leg_left = self.location.y + self.hip_width
        self.leg_right = self.location.y -self.hip_width
        self.backbone_length = 0.1
        self.leg_height = self.location.z  - (self.backbone_length * 2)
        self.shoulder_width = .3
        self.shoulder_left = self.location.y + self.shoulder_width
        self.shoulder_right = self.location.y -self.shoulder_width
        self.shoulder_height = self.location.z  + (self.backbone_length * 3)
        if(type == "quadruped"):
            self.backbone_length = .14
            self.shoulder_width = .2  # shoulder = hip width in this case
        # It's a bird!
        if(type == "avian"):
            self.backbone_length = .09 # Shorter backbones
            self.shoulder_width = .12
            

class Torso():
    def __init__(self, char):
        location = char.location
        self.J1 = None
        self.J2 = None
        self.J3 = None
        self.armature_number = str(getSceneObjectNumber())
        # START BUILD
        deselectAll() 
        # For leg connect hip
        self.hipL = Vector((0, char.hip_width, 0))
        self.hipR = Vector((0, -char.hip_width, 0))
        # Relative locations for connections
        self.name = 'at_torso' + str(char.number)
        self.armature = new_armature(self.name, location.x, location.y, location.z)
        bonehead = Vector((0, 0, 0)) # At armature
        bonetail = Vector((0,0,char.backbone_length)) 
        self.J1 = createBone('J1', bonehead, bonetail)
        #
        # Calculate hip location
        hip_point_z = char.backbone_length * 3
        hipLocation = Vector((location.x, location.y+char.hip_width, location.z-hip_point_z))
        self.hipLocationL = hipLocation
        hipLocation = Vector((location.x, location.y-char.hip_width, location.z-hip_point_z))
        self.hipLocationR = hipLocation
        #
        # Calculate shoulder location for arms
        zloc = location.z + (char.backbone_length * 3)
        shoulder = Vector((location.x, location.y+char.shoulder_width, zloc))
        self.shoulderlocationL = shoulder
        shoulder = Vector((location.x, -location.y+char.shoulder_width, zloc))
        self.shoulderlocationR = shoulder
        #
        #self.neckbase_location = [location.x+self.handle_tail, location.y, zloc + .03]
        self.neckbase_location = [location.x, location.y, zloc + .03]
        #
        # Start back build
        deselectAll()
        self.J2 = boneExtrude([0,0,char.backbone_length], "J2")  
        self.J3 = boneExtrude([0,0,char.backbone_length], "J3")
        #
        self.shoulderJ7L = boneExtrude([0,char.shoulder_width,0], "shoulder.L")
        self.shoulderJ7L_tail = bpy.context.active_bone.tail # Save location for arm connections
        #
        bpy.ops.armature.select_all(action='DESELECT')
        self.J3.select_tail = True
        self.J3.select_head = False
        char.shoulder_width = char.shoulder_width * -1 # Other way for right
        self.shoulderJ7R = boneExtrude([0,char.shoulder_width,0], "shoulder.R")
        self.shoulderJ7R_tail = bpy.context.active_bone.tail # Save location for arm connections
        #
        bpy.ops.object.mode_set(mode='POSE')
        self.bones = []
        for bone in self.armature.pose.bones:
            self.bones.append(bone)

class Pelvis():
    def __init__(self, char):
        location = char.location
        type = char.type
        self.J1 = None
        self.J2 = None
        self.J3 = None
        self.armature_number = str(getSceneObjectNumber())
        # START BUILD
        deselectAll()
        # Relative locations for connections
        self.name = 'at_pelvis' + str(char.number)
        self.armature = new_armature(self.name, location.x, location.y, location.z)
        bonehead = Vector((0, 0, 0)) # At armature
        bonetail = Vector((0,0,-char.backbone_length))
        self.J1 = createBone('J1', bonehead, bonetail)
        # Calculate hip location
        self.hip_width = .12
        hip_point_z = char.backbone_length * 3
        hipLocation = Vector((location.x, location.y+self.hip_width, location.z-hip_point_z))
        self.hipLocationL = hipLocation
        hipLocation = Vector((location.x, location.y-self.hip_width, location.z-hip_point_z))
        self.hipLocationR = hipLocation
        #
        # Start back build
        deselectAll()
        bpy.ops.armature.select_all(action='DESELECT')
        self.J1.select_tail = False
        self.J1.select_head = True
        # Reverse direction of build backbones below (behind) handle
        char.backbone_length = char.backbone_length * -1
        self.J2 = boneExtrude([0,0,char.backbone_length], "J2")
        self.J3 = boneExtrude([0,0,char.backbone_length], "J3")
        self.hipL = boneExtrude([0,self.hip_width,0], "hipL")
        self.hipL_tail = bpy.context.active_bone.tail  # Save location for arm connections
        bpy.ops.armature.select_all(action='DESELECT')
        self.J3.select_tail = True
        self.J3.select_head = False
        self.hipR = boneExtrude([0,-self.hip_width,0], "hipR")
        self.shoulderJ7R_tail = bpy.context.active_bone.tail # Save location for arm connections
        #
        self.shouldersupport_number = 0
        self.rump_support_number = 0
        bpy.ops.armature.select_all(action='DESELECT') 
        #
        bpy.ops.object.mode_set(mode='POSE')
        self.bones = []
        for bone in self.armature.pose.bones:
            self.bones.append(bone)

class Leg():
    def __init__(self, char, leftright='left', frontback='front'):
        self.str_n = str(char.number)
        self.armature_number = str(getSceneObjectNumber())
        self.cycledir = 1 # 1 or -1 to sync with opposite leg
        self.cyclephase = 0  # 0.0 - 1.0  Not yet used
        # This is a very special string that produces zero at frame Zero
        self.ZeroAtFrame0 = '*(frame * (1/(frame+.0001)))'
        #
        #self.y = .12  # y sets for left or right leg
        self.gait = 0  #  gait pose=0, walk=1, trot=2, run=3, pace=4
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
        self.name = 'at_leg' + str(char.number)
        #
        if((char.type == 'biped') or (char.type == 'quadruped')):
            y = char.leg_left
            if(side == "R"):
                y = char.leg_right
            self.armature = new_armature(self.name, char.location.x, y, char.leg_height)
            start = Vector((0, 0, 0)) # Start at armature location
            J1 = Vector((0, 0, -.32)) # Relative to armature location
        if(char.type == 'biped'):
            biped = [start, J1, Vector((0, 0, -.24)), Vector((0, 0, -.2)), Vector((0, 0, -.14)), Vector((.18, 0, -.06)), Vector((.08, 0, 0)), Vector((.08, 0, 0)), Vector((-.2, 0, -.01))]
            self.J1 = createBone("legJ1" + side, start, J1)
            self.J2 = boneExtrude(biped[2], "legJ2" + side)
            self.J3 = boneExtrude(biped[3], "legJ3" + side)
            self.J4 = boneExtrude(biped[4], "legJ4" + side)
            self.J5 = boneExtrude(biped[5], "legJ5" + side)
            self.J6 = boneExtrude(biped[6], "legJ6" + side)
            bpy.ops.armature.select_all(action='DESELECT')
            self.J5.select_tail = True    
            self.J5.select_head = False
            self.J7 = boneExtrude(biped[7], "legJ7" + side)
            bpy.ops.armature.select_all(action='DESELECT')
            self.J5.select_tail = True    # Build heal reinforce
            self.J5.select_head = False        
            self.J8 = boneExtrude(biped[8], "legJ8" + side)
            deselectAll()  #bpy.ops.armature.select_all(action='DESELECT')
        if(char.type == 'quadruped'):
            leg = [start, J1, Vector((-.12, 0, -.27)), Vector((.06, 0, -.25)), Vector((.04, 0, -.08)), Vector((.05, 0, -.05)), Vector((.03, 0, -.054)),Vector((.07, 0, -.05))]
            if(frontback=='front'):
                leg[2] = Vector((0, 0, -.27))
                leg[3] = Vector((0, 0, -.25))
            self.J1 = createBone("legJ1" + side, start, J1)
            self.J2 = boneExtrude(leg[2], "legJ2" + side)
            self.J3 = boneExtrude(leg[3], "legJ3" + side)
            self.J4 = boneExtrude(leg[4], "legJ4" + side)
            self.J5 = boneExtrude(leg[5], "legJ5" + side)
        #
        if(char.type == 'avian'):
            # Set initial Armature location
            x = char.location.x -.194
            y = char.location.y + .18
            z = char.location.z -.569
            if(leftright == 'right'):
                y = char.location.y - .18
            self.armature = new_armature(self.name, x,y,z)
            birdleg = [Vector((0,0,0)), Vector((.01, 0, -0.12)),Vector((-0.02, 0, -0.12)),Vector((-0.02, 0, -0.12)),Vector((-0.02, 0, -0.12)),Vector((.01, 0, -.1)),Vector((.01, 0, -.1)),Vector((.01, 0, -.1)),Vector((0.003, 0, -.06))]
            self.hip = createBone("legJ1" + side, birdleg[0], birdleg[1])
            self.J1 = boneExtrude(birdleg[2], "legJ1" + side)
            self.J2 = boneExtrude(birdleg[3], "legJ2" + side)
            self.J3 = boneExtrude(birdleg[4], "legJ3" + side)
            self.J4 = boneExtrude(birdleg[5], "legJ4" + side)
            self.J5 = boneExtrude(birdleg[6], "legJ5" + side)
            self.J6 = boneExtrude(birdleg[7], "legJ6" + side)
            self.J7 = boneExtrude(birdleg[8], "legJ7" + side)
            spur = [Vector((-0.07, -.016, .01)),Vector((-0.07, -.015, 0)),Vector((-0.07, -.015, 0)),Vector((-0.07, -.015, 0))]
            if(leftright == 'right'):
                spur = [Vector((-0.07, .016, .01)),Vector((-0.07, .015, 0)),Vector((-0.07, .015, 0)),Vector((-0.07, .015, 0))]
                self.spurJ1 = boneExtrude(spur.x, "leg_spurJ1")
                self.spurJ2 = boneExtrude(spur.y, "leg_spurJ2")
                self.spurJ3 = boneExtrude(spur.z, "leg_spurJ3")
                self.spurJ4 = boneExtrude(spur[3], "leg_spurJ4")
                bpy.ops.armature.select_all(action='DESELECT')
                self.J7.select_tail = True
                self.toeJ1 = boneExtrude([.07, 0, 0], "leg_toeJ1") # Center toe
                self.toeJ2 = boneExtrude([.07, 0, 0], "leg_toeJ2")
                self.toeJ3 = boneExtrude([.07, 0, 0], "leg_toeJ3")
                self.toeJ4 = boneExtrude([.07, 0, 0], "leg_toeJ4")
                bpy.ops.armature.select_all(action='DESELECT')
                self.J7.select_tail = True
                y = -.0358
            if(leftright == 'right'):
                y = y * -1
                self.toeJ1L = boneExtrude([.066, y, 0], "leg_toeJ1L")
                self.toeJ2L = boneExtrude([.066, y, 0], "leg_toeJ2L")
                self.toeJ3L = boneExtrude([.066, y, 0], "leg_toeJ3L")
                self.toeJ4L = boneExtrude([.066, y, 0], "leg_toeJ4L")
                bpy.ops.armature.select_all(action='DESELECT')
                self.J7.select_tail = True
                y = .0358
            if(leftright == 'right'):
                y = y * -1
            self.toeJ1R = boneExtrude([.066, y, 0], "leg_toeJ1R")
            self.toeJ2R = boneExtrude([.066, y, 0], "leg_toeJ2R")
            self.toeJ3R = boneExtrude([.066, y, 0], "leg_toeJ3R")
            self.toeJ4R = boneExtrude([.066, y, 0], "leg_toeJ4R")
        #
        bpy.ops.object.mode_set(mode='POSE')
        self.bones = []
        for bone in self.armature.pose.bones:
            self.bones.append(bone)
 

# creeteBone(name="boneName", VHead=(0, 0, 0), VTail=(.1, 0, .1), roll=0, con=False):
class Arm():
    def __init__(self, char, leftright='left'):
        self.str_n = str(char.number)
        self.armature_number = str(getSceneObjectNumber())
        self.type = type
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
        deselectAll()
        side = "L"
        x = char.location.x; y = char.shoulder_left; z = char.location.z
        if(self.leftright == 'right'):
            side = "R"
            y = char.shoulder_right
        self.name = 'at_arm' + str(char.number)
        self.armature = new_armature(self.name, char.location.x, y, char.shoulder_height)
        start = Vector((0, 0, 0)) # Start at armature location
        J1 = Vector((0, .2, 0)) # Relative to armature location  # [.3, .1, .5],[.3, .22, .5]
        arm = [start, J1,Vector((0, .2, 0)),Vector((0, .08, 0)),Vector((0, .1, 0)),
              Vector((0, .1, 0)),Vector((0, .098, 0)),Vector((0, .05, 0)),Vector((0, .044, 0)),Vector((0, .02, 0)),      # MiddleJ1-4
              Vector((.03, .098, -.006)),Vector((.011, .032, 0)),Vector((.01, .024, 0)),Vector((.008, .02, 0)),  # IndexJ1-4
              Vector((-.02, .098, -.006)),Vector((-.01, .042, 0)),Vector((-.007, .032, 0)),Vector((-.004, .02, 0)),  # RingJ1-4 
              Vector((-.046, .095, -.006)),Vector((-.016, .024, 0)),Vector((-.012, .02, 0)),Vector((-.01, .02, 0)),  # PinkyJ1-4 
              Vector((.008, .002, 0)),Vector((.044, .038, -0.01)),Vector((.02, .032, -0.006)),Vector((.01, .02, 0))] # ThumbJ1-4
        #
        if(self.leftright == 'right'):
            for coord in arm:      # Right arm has to grow in the opposite direction
                coord.y = coord.y * -1
        self.J1 = createBone("armJ1" + side, start, J1)
        self.J2 = boneExtrude([arm[2].x,arm[2].y,arm[2].z], "armJ2")
        self.J3 = boneExtrude([arm[3].x,arm[3].y,arm[3].z], "armJ3")
        self.J4 = boneExtrude([arm[4].x,arm[4].y,arm[4].z], "armJ4")
        self.J5 = boneExtrude([arm[5].x,arm[5].y,arm[5].z], "armJ5")
        self.J6 = boneExtrude([arm[6].x,arm[6].y,arm[6].z], "armJ6")
        self.J7 = boneExtrude([arm[7].x,arm[7].y,arm[7].z], "middleJ7")
        self.J8 = boneExtrude([arm[8].x,arm[8].y,arm[8].z], "middleJ8")
        self.J9 = boneExtrude([arm[9].x,arm[9].y,arm[9].z], "middleJ9")
        bpy.ops.armature.select_all(action='DESELECT')
        self.J5.select_tail = True
        self.J5.select_head = False
        self.IJ1 = boneExtrude([arm[10].x,arm[10].y,arm[10].z], "indexJ1")
        self.IJ2 = boneExtrude([arm[11].x,arm[11].y,arm[11].z], "indexJ2")
        self.IJ3 = boneExtrude([arm[12].x,arm[12].y,arm[12].z], "indexJ3")
        self.IJ4 = boneExtrude([arm[13].x,arm[13].y,arm[13].z], "indexJ4")
        bpy.ops.armature.select_all(action='DESELECT')
        self.J5.select_tail = True
        self.J5.select_head = False
        self.RJ1 = boneExtrude([arm[14].x,arm[14].y,arm[14].z], "ringJ1")
        self.RJ2 = boneExtrude([arm[15].x,arm[15].y,arm[15].z], "ringJ2")
        self.RJ3 = boneExtrude([arm[16].x,arm[16].y,arm[16].z], "ringJ3")
        self.RJ4 = boneExtrude([arm[17].x,arm[17].y,arm[17].z], "ringJ4")
        bpy.ops.armature.select_all(action='DESELECT')
        self.J5.select_tail = True
        self.J5.select_head = False
        self.PJ1 = boneExtrude([arm[18].x,arm[18].y,arm[18].z], "pinkyJ1")
        self.PJ2 = boneExtrude([arm[19].x,arm[19].y,arm[19].z], "pinkyJ2")
        self.PJ3 = boneExtrude([arm[20].x,arm[20].y,arm[20].z], "pinkyJ3")
        self.PJ4 = boneExtrude([arm[21].x,arm[21].y,arm[21].z], "pinkyJ4")
        bpy.ops.armature.select_all(action='DESELECT')
        self.J5.select_tail = True
        self.J5.select_head = False
        self.TJ1 = boneExtrude([arm[22].x,arm[22].y,arm[22].z], "thumbJ1")
        self.TJ2 = boneExtrude([arm[23].x,arm[23].y,arm[23].z], "thumbJ2")
        self.TJ3 = boneExtrude([arm[24].x,arm[24].y,arm[24].z], "thumbJ3")
        self.TJ4 = boneExtrude([arm[25].x,arm[25].y,arm[25].z], "thumbJ4")
        #
        bpy.ops.object.mode_set(mode='POSE')
        self.bones = []
        for bone in self.armature.pose.bones:
            self.bones.append(bone)
        #
        deselectAll()

# Head and neck are considered one unit
class Head():
    def __init__(self, char):
        if(bpy.context.mode != 'OBJECT'):
            bpy.ops.object.mode_set(mode='OBJECT')
        self.str_n = str(char.number)
        self.armature_number = str(getSceneObjectNumber())
        self.type = char.type
        self.headbase = ""
        self.location = char.location
        self.cycledir = 1 # 1 or -1 to sync with opposite arm
        self.cyclephase = 0  # 0.0 - 1.0  Not yet used
        # This is a very special string that produces zero at frame Zero
        self.ZeroAtFrame0 = '*(frame * (1/(frame+.0001)))'
        #
        deselectAll()
        self.name = 'at_head' + str(char.number)
        if(("biped" in self.type) or ("quadruped" in self.type)):
            y = char.location.y
            self.armature = new_armature(self.name, char.location.x, y, char.shoulder_height)
            #
            start = Vector((0, 0, 0)) # Start at armature location
            J1 = Vector((0, 0, .12)) # Relative to armature location  # [.3, 0, .5],[.3, 0, .54],
            head = [start, J1,Vector((.01, 0, .03)),Vector((.01, 0, .03)),Vector((0, 0, .024)),
                 Vector((0, 0, .09)),Vector((.12, 0, .0)), Vector((.02, 0, -.02)),Vector((0, 0, .04)),Vector((-.05, 0, 0)),
                 Vector((.08, 0, .09)),Vector((.1, .03, 0)),Vector((.03, 0, 0)), Vector((.1, -.03, 0)),Vector((.03, 0, 0)),
                 Vector((.02, 0, .04)),Vector((.04, .05, 0)),Vector((.07, -.04, 0)),Vector((.04, -.05, 0)),Vector((.07, .04, 0)),
                 Vector((.02, 0, 0)),Vector((.04, .05, 0)),Vector((.07, -.04, 0)),Vector((.04, -.05, 0)),Vector((.07, .04, 0))]
        #
        if("quadruped" in self.type):
            head.x = start
            head[1] = Vector((.22, 0, .18)) # non-relative
            head[2] = Vector((.12, 0, .12))
            head[3] = Vector((.12, 0, .12))
        if(("biped" in self.type) or ("quadruped" in self.type)):
            self.J1 = createBone("neckJ1", start, head[2])
            self.J2 = boneExtrude(head[2], "neckJ2")
            self.J3 = boneExtrude(head[3], "neckJ3")
            self.J4 = boneExtrude(head[4], "headJ4")
            self.J5 = boneExtrude(head[5], "headJ5")
            bpy.ops.armature.select_all(action='DESELECT')
            self.J5.select_tail = True 
            self.J5.select_head = False
            self.J6 = boneExtrude(head[6], "headJ6")
            self.J7 = boneExtrude(head[7], "noseJ7")
            bpy.ops.armature.select_all(action='DESELECT')
            self.J5.select_tail = True 
            self.J5.select_head = False
            self.J8 = boneExtrude(head[8], "headJ8")
            self.J9 = boneExtrude(head[9], "headJ9")
            self.J10 = boneExtrude(head[10], "headJ10")
            bpy.ops.armature.select_all(action='DESELECT')
            self.J8.select_tail = True
            self.J8.select_head = False
            self.J11 = boneExtrude(head[11], "headJ11")
            self.J12 = boneExtrude(head[12], "eyeJ12")
            bpy.ops.armature.select_all(action='DESELECT')
            self.J8.select_tail = True
            self.J8.select_head = False
            self.J13 = boneExtrude(head[13], "headJ13")
            self.J14 = boneExtrude(head[14], "eyeJ14")
            bpy.ops.armature.select_all(action='DESELECT')
            self.J4.select_tail = True
            self.J4.select_head = False
            # Upper Jaw L
            self.J15 = boneExtrude(head[15], "headJ15")
            self.J16 = boneExtrude(head[16], "headJ16")
            self.J17 = boneExtrude(head[17], "headJ17")
            bpy.ops.armature.select_all(action='DESELECT')
            self.J15.select_tail = True
            self.J15.select_head = False
            # Upper Jaw R
            self.J18 = boneExtrude(head[18], "headJ18")
            self.J19 = boneExtrude(head[19], "headJ19")       
            bpy.ops.armature.select_all(action='DESELECT')
            self.J4.select_tail = True
            self.J4.select_head = False
            # Upper Jaw L
            self.J20 = boneExtrude(head[20], "headJ20")
            self.J21 = boneExtrude(head[21], "jawBaseJ21")
            self.J22 = boneExtrude(head[22], "jawJ22")
            bpy.ops.armature.select_all(action='DESELECT')
            self.J20.select_tail = True
            self.J20.select_head = False
            # Upper Jaw R
            self.J23 = boneExtrude(head[23], "jawBaseJ23")
            self.J24 = boneExtrude(head[24], "jawJ24") 
            bpy.ops.armature.select_all(action='DESELECT')
        #
        #
        if("avian" in self.type):
            deselectAll()
            x = xyz.x + .132
            y = xyz.y
            z = xyz.z - .382
            armature_number = str(getSceneObjectNumber())
            self.armature = new_armature('armature_head' + armature_number, x,y,z)
            #
            start = [0, 0, 0]
            neckbase = [.06,0,.02]
            neck = [start, neckbase, [0.06,0,.02],[0.06,0,.02],[0.026,0,.032],[0.020,0,.039],[0,0,.04],[-.03,0,.052],[.16,0,.03],[-.1,0,.07]]
            self.neckbase = createBone(start, neckbase, 'neckbase')
            self.neckJ1 = boneExtrude(neck.z, "neckJ1")
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
            self.jawbase = boneExtrude(jaw.x, "jawbase")
            self.beakbasetop = boneExtrude(jaw.y, "beakbasetop")
            self.beakbacktop = boneExtrude(jaw.z, "beakbacktop")
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
            self.eyebaseL = boneExtrude(eyes.x, "eyebaseL")
            self.eyeL = boneExtrude(eyes.y, "eyeL")
            bpy.ops.armature.select_all(action='DESELECT')
            self.neckJ6.select_tail = True
            self.eyebaseR = boneExtrude(eyes.z, "eyebaseR")
            self.eyeR = boneExtrude(eyes.y, "eyeR")
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
        self.str_n = str(char.number)
        self.type = type
        self.name = self.type + str(self.n) + 'tail'
        self.armature_number = str(getSceneObjectNumber())
        self.xyz = xyz
        self.location = xyz
        self.location = None
        # This is a very special string that produces zero at frame Zero
        self.ZeroAtFrame0 = '*(frame * (1/(frame+.0001)))'
        #
        deselectAll()
        x = self.xyz.x - .253
        y = self.xyz.y
        z = self.xyz.z - .461
        self.name = 'at_tail' + str(char.number)
        self.armature = new_armature(self.name, x,y,z)
        #
        start = [0, 0, 0]
        tailJ0 = [-.11  , 0, -.05]
        tail = [[-0.1, 0, -.04],[-.1, 0, 0],[-.06, 0, 0],[-.08, 0, 0]]
        #
        self.J0 = createBone(start, tailJ0, "tailJ0")
        self.J1 = boneExtrude(tail.x, "tailJ1")
        self.J2 = boneExtrude(tail.y, "tailJ2")
        self.J3 = boneExtrude(tail.z, "tailJ3")
        self.featherC = boneExtrude(tail[3], "tailfeatherC")
        bpy.ops.armature.select_all(action='DESELECT')
        self.J3.select_tail = True
        featherbase = [[0.025, .022, 0],[0.025, -.022, 0]]
        self.fb1L = boneExtrude(featherbase.x, "tail_fb1L")
        self.fb2L = boneExtrude(featherbase.x, "tail_fb2L")
        self.fb3L = boneExtrude(featherbase.x, "tail_fb3L")
        self.fb4L = boneExtrude(featherbase.x, "tail_fb4L")
        bpy.ops.armature.select_all(action='DESELECT')
        self.J3.select_tail = True
        self.fb1R = boneExtrude(featherbase.y, "tail_fb1R")
        self.fb2R = boneExtrude(featherbase.y, "tail_fb2R")
        self.fb3R = boneExtrude(featherbase.y, "tail_fb3R")
        self.fb4R = boneExtrude(featherbase.y, "tail_fb4R")
        self.feather4R = boneExtrude([-.08, 0, 0], "tailfeather4R")
        bpy.ops.armature.select_all(action='DESELECT')
        self.fb3R.select_tail = True  
        self.feather3R = boneExtrude([-.08, 0, 0], "tailfeather3R")
        bpy.ops.armature.select_all(action='DESELECT')
        self.fb2R.select_tail = True  
        self.feather2R = boneExtrude([-.08, 0, 0], "tailfeather2R")
        bpy.ops.armature.select_all(action='DESELECT')
        self.fb1R.select_tail = True  
        self.feather1R = boneExtrude([-.08, 0, 0], "tailfeather1R")
        #
        bpy.ops.armature.select_all(action='DESELECT')
        self.fb4L.select_tail = True
        self.feather4L = boneExtrude([-.08, 0, 0], "tailfeather4L")
        bpy.ops.armature.select_all(action='DESELECT')
        self.fb3L.select_tail = True
        self.feather3L = boneExtrude([-.08, 0, 0], "tailfeather3L")
        bpy.ops.armature.select_all(action='DESELECT')
        self.fb2L.select_tail = True  
        self.feather2L = boneExtrude([-.08, 0, 0], "tailfeather2L")
        bpy.ops.armature.select_all(action='DESELECT')
        self.fb1L.select_tail = True  
        self.feather1L = boneExtrude([-.08, 0, 0], "tailfeather1L")
        bpy.ops.armature.select_all(action='DESELECT')
        deselectAll()

        
class Wing():
    def __init__(self, type, xyz, leftright='left', frontback='front'):
        self.str_n = str(char.number)
        self.armature_number = str(getSceneObjectNumber())
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
        x = self.xyz.x + .132
        y = self.xyz.y + .12
        z = self.xyz.z - .082
        if(leftright == 'right'):
            y = self.xyz.y - .12
        self.name = 'at_wing' + str(char.number)
        self.armature = new_armature(self.name, x,y,z)
        wing = [[0,0,0],[0, .036, 0],[0, .03, 0],[0, .02, 0],[0, .08, 0]]
        if(leftright == 'right'):
            wing = [[0,0,0],[0, -.036, 0],[0, -.03, 0],[0, -.02, 0],[0, -.08, 0]]
        self.wingJ0 = createBone(wing.x, wing.y, "wingJ0")
        self.wingJ1 = boneExtrude(wing.y, "wingJ1")
        self.wingJ2 = boneExtrude(wing.y, "wingJ2")
        self.wingJ3 = boneExtrude(wing.z, "wingJ3")
        self.wingJ4 = boneExtrude(wing.z, "wingJ4")
        self.wingJ5 = boneExtrude(wing.z, "wingJ5")
        self.wingJ6 = boneExtrude(wing.z, "wingJ6")
        self.wingJ7 = boneExtrude(wing.z, "wingJ7")
        self.wingJ8 = boneExtrude(wing.z, "wingJ8")
        self.wingJ9 = boneExtrude(wing.z, "wingJ9")
        self.wingJ10 = boneExtrude(wing[3], "wingJ10")
        self.wingJ11 = boneExtrude(wing[3], "wingJ11")
        self.wingJ12 = boneExtrude(wing[3], "wingJ12")
        self.wingJ13 = boneExtrude(wing[3], "wingJ13")
        self.wingJ14 = boneExtrude(wing[3], "wingJ14")
        self.wingJ15 = boneExtrude(wing[4], "wingJ15")
        #
        # Feathers
        feathers = [[-.05, 0, 0],[-.05, .002, 0],[-.05, .004, 0],[-.05, .006, 0],[-.05, .008, 0],
[-.05, .01, 0],[-.05, .012, 0],[-.05, .014, 0],[-.05, .018, 0],[-.05, .022, 0],[-.05, .026, 0],
[-.05, .03, 0],[-.05, .044, 0],[-.04, .06, 0],[-.03, .075, 0]]
        if(leftright == 'right'):
            for item in feathers:
            item.y = item.y * -1
        bpy.ops.armature.select_all(action='DESELECT')
        self.wingJ0.select_tail = True
        self.feather1 = boneExtrude(feathers.x, "feather1")
        bpy.ops.armature.select_all(action='DESELECT')
        self.wingJ1.select_tail = True
        self.feather2 = boneExtrude(feathers.y, "feather2")
        bpy.ops.armature.select_all(action='DESELECT')
        self.wingJ2.select_tail = True
        self.feather3 = boneExtrude(feathers.z, "feather3")
        bpy.ops.armature.select_all(action='DESELECT')
        self.wingJ3.select_tail = True
        self.feather4 = boneExtrude(feathers[3], "feather4")
        bpy.ops.armature.select_all(action='DESELECT')
        self.wingJ4.select_tail = True
        self.feather5 = boneExtrude(feathers[4], "feather5")
        bpy.ops.armature.select_all(action='DESELECT')
        self.wingJ5.select_tail = True
        self.feather6 = boneExtrude(feathers[5], "feather6")
        bpy.ops.armature.select_all(action='DESELECT')
        self.wingJ6.select_tail = True
        self.feather7 = boneExtrude(feathers[6], "feather7")
        bpy.ops.armature.select_all(action='DESELECT')
        self.wingJ7.select_tail = True
        self.feather8 = boneExtrude(feathers[7], "feather8")
        bpy.ops.armature.select_all(action='DESELECT')
        self.wingJ8.select_tail = True
        self.feather9 = boneExtrude(feathers[8], "feather9")
        bpy.ops.armature.select_all(action='DESELECT')
        self.wingJ9.select_tail = True
        self.feather10 = boneExtrude(feathers[9], "feather10")
        bpy.ops.armature.select_all(action='DESELECT')
        self.wingJ10.select_tail = True
        self.feather11 = boneExtrude(feathers[10], "feather11")
        bpy.ops.armature.select_all(action='DESELECT')
        self.wingJ11.select_tail = True
        self.feather12 = boneExtrude(feathers[11], "feather12")
        bpy.ops.armature.select_all(action='DESELECT')
        self.wingJ12.select_tail = True
        self.feather13 = boneExtrude(feathers[12], "feather13")
        bpy.ops.armature.select_all(action='DESELECT')
        self.wingJ13.select_tail = True
        self.feather14 = boneExtrude(feathers[13], "feather14")
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


# Reference for building characters:
'''
# Biped
char = Character(b)
armL = Arm(b, char.shoulderlocationL, left)
armL = Arm(b, char.shoulderlocationR, right)
legL = Leg(b, char.hipLocationL, left)
legR = Leg(b, char.hipLocationR, right)
head = Head(b, char.neckbase_location)

# Quadruped
quad = Character(q)
legL = Leg(q, quad.hiplocation_frontL, left)
legR = Leg(q, quad.hiplocation_frontR, right)
legL = Leg(q, quad.hiplocation_backL, left, back)
legL = Leg(q, quad.hiplocation_backR, right, back)
qhead = Head(q, quad.necklocation)

# Centaur
quad = Character(q)
legL = Leg(q, quad.hiplocation_frontL, left)
legR = Leg(q, quad.hiplocation_frontR, right)
legL = Leg(q, quad.hiplocation_backL, left, back)
legL = Leg(q, quad.hiplocation_backR, right, back)
char = Character(b)
armL = Arm(b, char.shoulderlocationL, left)
armL = Arm(b, char.shoulderlocationR, right)
head = Head(b, char.neckbase_location)

# Avian - bird
avian = Character(a)
ahead = Head(a, avian.neckbase_location)
xyz = avian.location
legL = Leg(a, xyz, left)
legR = Leg(a, xyz, right)
tail = Tail(a, xyz)
wing = Wing(a, xyz, left)
wing = Wing(a, xyz, right)
'''

