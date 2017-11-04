# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Generalized header code section
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# THINGS THAT MAY VARY BASED ON THE CHARACTER:
# 1. Character name - biped, quadruped, bird, spider, dragon, kangaroo.
#    Line: 125
# 2. rig location 
#    Example: char.height = 1.4, char.x = .3 * n; char.y = 3.2 * n; char.z = 0.1;
#    This can set the initial height of the character, and 
#    n is used to offset characters when more than one are created
#    Lines: 136 - 139
# 3. bone.tail sets the general orientation of the handle created for 
#    moving the character - this could vary, based  on the type of character.
#    Line: 151
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
import bpy, math
from bpy.types import Panel, Menu
from rna_prop_ui import PropertyPanel
from abc import ABCMeta, abstractmethod

# General Use Functions. Rotate the easy way, changes to pose mode and back
# name a string i.e., rotate('backCenter', .2, 1)
def rotate(name, rad, axis=0):
    bpy.ops.object.mode_set(mode='POSE')
    bpy.context.object.data.bones[name].select = True
    Vector = (1, 0, 0)
    cAxis = (True, False, False)
    if (axis == 1):
        Vector = (0, 1, 0)
        cAxis = (False, True, False)
    if (axis == 2):
        Vector = (0, 0, 1)
        cAxis = (False, False, True)
    bpy.ops.transform.rotate(value=rad, axis=Vector, constraint_axis=cAxis, constraint_orientation='GLOBAL',
                             mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH',
                             proportional_size=1, release_confirm=True)
    bpy.context.object.data.bones[name].select = False


# Link objects to scene
def linkObjectsToScene(rig):
    scn = bpy.context.scene
    scn.objects.link(rig)
    scn.objects.active = rig
    scn.update()

# Make bone creation easy
def createBone(name="boneName", Vhead=(0, 0, 0), Vtail=(.1, 0, .1), roll=0, con=False):
    bpy.ops.object.mode_set(mode='EDIT')
    bData = bpy.context.active_object.data
    bone = bData.edit_bones.new(name)
    bone.head[:] = Vhead
    bone.tail[:] = Vtail
    bone.roll = roll
    bone.use_connect = con
    return bone

# Options for character types -  biped, quadruped, bird, spider, dragon, kangaroo
def setCharacterName(type, n):
    name = "rg" + type + "0" + str(n + 1)  # Assume n < 10 
    if (n > 9):  # Change char.name if previous assumption is wrong
        name = "rg" + type + str(n + 1)
    return name

# getEuler output represents:
# bpy.data.objects['rg00centaur'].pose.bones["backCenter"]
def getEuler(str_bone_name):
    bpy.ops.object.mode_set(mode='POSE')
    ob = bpy.context.object
    euler = ob.pose.bones[str_bone_name]
    euler.rotation_mode = 'XYZ'
    return euler


# Equation for bone joints, with euler transform, axis 0=x 1=y 2=z
# Note also that fn must be inserted as a STRING in the expression!
# Example: setDriver(getEuler(centaur.strName + '_bone'), equationFB, 2)
def setDriver(euler, fn="0", axis=0, movementType='rotation_euler'):
    eulerDriver = euler.driver_add(movementType)
    eulerDriver[axis].driver.type = 'SCRIPTED'
    eulerDriver[axis].driver.expression = fn
    return eulerDriver


# Set Driver For Single Axis Only:
def setAxisDriver(euler, fn="0", axis=0, movementType='rotation_euler'):
    edriver = euler.driver_add(movementType, axis)
    edriver.driver.type = 'SCRIPTED'
    edriver.driver.expression = fn
    return edriver

    
context = bpy.context
bpy.context.scene.frame_start = 0
class Character(object):
    __metaclass__ = ABCMeta
    n = 0  # Character number
    strName = ""
    armmature = 'None'
    rig = 'None'
    rootBone = 'None'
    rootBoneHead = 'None'
    rootBoneTail = 'None'
    reinforce = True  # Option - Add extra bones for stabilization
    showNames = False  # Option - show bone names - for build only
    show_xray = True  # Option
    show_axes = False  # Option - Show armature axis - for build only
    rig = None
    height = 0
    x = 0
    y = 0
    z = 0
    frame = bpy.context.scene.frame_current
    cycleSpeed = 8.0  # This is the speed of leg movement
    # For Pose at frame zero - Override function on frame zero, allowing for posing.
    strZeroMovement = " * (frame * (1/(frame+.0001)))"  # This includes outside math operator *
    strZeroOutPose = " * abs((frame/(frame + .0001))-1)"  # Override posePosition when frame NOT zero
    @abstractmethod
    def character_type(self):
        return 'centaur'


char = Character
# Do not remove spaces below, they correspond to command line entries
for ob in list(bpy.data.objects):
    if ob.name.startswith('rg') == True:
        char.n = char.n + 1  # increment rig number each time  one  is built.

char.strName = setCharacterName('centaur', char.n)  # biped, quadruped, bird, spider, dragon, kangaroo
# Start character armature and bones
# Do not remove spaces above, they correspond to command line entries
at = bpy.data.armatures.new(char.strName + '_at')  # at = Armature 
char.rig = bpy.data.objects.new(char.strName, at)  # rig = Armature object
# rg00 (or the one in a series we are building) is now bpy.context.active_object
at.show_names = char.showNames
at.show_axes = char.show_axes

# Each new object created will be placed in a new location
char.height = 1.14  # Sets the height of the character handle
char.x = .3 * char.n;
char.y = char.n;
char.z = char.height;
char.rig.location = (char.x, char.y, char.height)  # Set armature location
char.rig.show_x_ray = char.show_xray
linkObjectsToScene(char.rig)

bpy.ops.object.mode_set(mode='EDIT')
# The lines below create the handle for moving the character
bone = at.edit_bones.new(char.strName + '_bone')

bone.head = [0.0, 0.0, 0.0]  # LOCAL COORDINATE, [0,0,0] places bone directly on armature.
bone.tail = [-0.2, 0, 0]  # x - horizontal handle   z - vertical handle
char.rootBoneHead = bone.head
char.rootBoneTail = bone.tail
char.rootBone = bone

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# End generalized header code section
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


class Centaur(Character):
    anklePP = 0.0
    #
    def buildSkeleton(self):
        V_pelvis = (0, 0, -.13)
        pelvis = createBone("pelvis", bone.head, V_pelvis, 0)
        pelvis.parent = at.edit_bones[centaur.strName + '_bone']
        hipWidth = .12
        # 
        V_hipR = (0, hipWidth, -.13)
        V_hipL = (0, -hipWidth, -.13)
        hipR = createBone("hipR", V_pelvis, V_hipR, 0)
        hipR.parent = at.edit_bones['pelvis']
        hipL = createBone("hipL", V_pelvis, V_hipL, 0)
        hipL.parent = at.edit_bones['pelvis']
        # 
        V_femurR = (0, hipWidth, -.6)
        V_femurL = (0, -hipWidth, -.6)    
        femurR = createBone("femurR", V_hipR, V_femurR, 0)
        femurR.parent = at.edit_bones['hipR']
        femurL = createBone("femurL", V_hipL, V_femurL, 0)
        femurL.parent = at.edit_bones['hipL']
        # 
        V_tibiaR = (0, hipWidth, -.94)
        V_tibiaL = (0, -hipWidth, -.94)
        tibiaR = createBone("tibiaR", V_femurR, V_tibiaR, 0)
        tibiaR.parent = at.edit_bones['femurR']
        tibiaL = createBone("tibiaL", V_femurL, V_tibiaL, 0)
        tibiaL.parent = at.edit_bones['femurL']
        #
        V_ankleR = (0, hipWidth, -1.02)
        V_ankleL = (0, -hipWidth, -1.02)
        ankleR = createBone("ankleR", (V_tibiaR), (V_ankleR), 0)
        ankleR.parent = at.edit_bones['tibiaR']
        ankleL = createBone("ankleL", (V_tibiaL), (V_ankleL), 0)
        ankleL.parent = at.edit_bones['tibiaL']  
        #
        V_toeR = (0, hipWidth, -1.1)
        V_toeL = (0, -hipWidth, -1.1)
        toeR = createBone("toeR", (V_ankleR), (V_toeR), 0)
        toeR.parent = at.edit_bones['ankleR']
        toeL = createBone("toeL", (V_ankleL), (V_toeL), 0)
        toeL.parent = at.edit_bones['ankleL']
        # END OF LOWER BODY BUILD
        #
        # Create Upper Body  
        V_lowBack = (0, 0, 0.1)
        lowBack = createBone("lowBack", bone.head, V_lowBack)
        lowBack.parent = at.edit_bones[centaur.strName + '_bone']
        # 
        V_midBack = (0, 0, 0.22)
        midBack = createBone("midBack", V_lowBack, V_midBack)
        midBack.parent = at.edit_bones['lowBack']
        # 
        V_cBack = (0, 0, 0.34)
        cBack = createBone("cBack", V_midBack, V_cBack)
        cBack.parent = at.edit_bones['midBack']
        # 
        V_upperBack = (0, 0, 0.54)
        upperBack = createBone("upperBack", V_cBack, V_upperBack)   
        upperBack.parent = at.edit_bones['cBack']    
        # 
        V_neckBase = (0, 0, 0.59)   
        neckBase = createBone("neckBase", V_upperBack, V_neckBase)   
        neckBase.parent = at.edit_bones['upperBack']
        # 
        V_lowerNeck = (0, 0, 0.63)
        lowerNeck = createBone("lowerNeck", V_neckBase, V_lowerNeck) 
        lowerNeck.parent = at.edit_bones['neckBase']
        # 
        V_midNeck = (0, 0, 0.66)
        midNeck = createBone("midNeck", V_lowerNeck, V_midNeck) 
        midNeck.parent = at.edit_bones['lowerNeck']
        #
        V_upperNeck = (0, 0, 0.69)
        upperNeck = createBone("upperNeck", (V_midNeck), V_upperNeck)   
        upperNeck.parent = at.edit_bones['midNeck']    
        # 
        V_jawBase = (0.06, 0, 0.69)    
        jawBase = createBone("jawBase", V_upperNeck, V_jawBase)
        jawBase.parent = at.edit_bones['upperNeck']
        # 
        V_jaw = (0.106, 0, .69)
        jaw = createBone("jaw", V_jawBase, V_jaw)   
        jaw.parent = at.edit_bones['jawBase']
        # 
        V_headBase = (0, 0, 0.73)   
        headBase = createBone("headBase", V_upperNeck, V_headBase) 
        headBase.parent = at.edit_bones['upperNeck']
        # 
        V_mouthTop = (0.106, 0, .72)  
        mouthTop = createBone("mouthTop", V_headBase, V_mouthTop) 
        mouthTop.parent = at.edit_bones['headBase']
        # 
        V_headTop = (0, 0, 0.76)
        headTop = createBone("headTop", V_headBase, V_headTop)
        headTop.parent = at.edit_bones['headBase']
        # 
        V_eyebaseR = (0.08, -0.03, 0.76)   
        V_eyebaseL = (0.08, 0.03, 0.76)      
        eyebaseR = createBone("eyebaseR", V_headTop, V_eyebaseR)
        eyebaseR.parent = at.edit_bones['headTop']   
        eyebaseL = createBone("eyebaseL", V_headTop, V_eyebaseL)  
        eyebaseL.parent = at.edit_bones['headTop']
        # 
        V_eyeR = (0.102, -0.03, 0.76)
        V_eyeL = (0.102, 0.03, 0.76)
        eyeR = createBone("eyeR", V_eyebaseR, V_eyeR) 
        eyeR.parent = at.edit_bones['eyebaseR']   
        eyeL = createBone("eyeL", V_eyebaseL, V_eyeL) 
        eyeL.parent = at.edit_bones['eyebaseL']
        # 
        V_NoseBase = (0.11, 0, 0.75)
        noseBase = createBone("noseBase", V_headTop, V_NoseBase)
        noseBase.parent = at.edit_bones['headTop']
        # 
        V_Nose = (.11, 0, .73)
        nose = createBone("nose", V_NoseBase, V_Nose)   
        nose.parent = at.edit_bones['noseBase']
        #
        V_NoseTip = (.13, 0, .73)
        noseTip = createBone("noseTip", V_Nose, V_NoseTip)   
        noseTip.parent = at.edit_bones['nose']
        # 
        # Shoulder area
        V_scapulaR = (0, .30, 0.48)
        V_scapulaL = (0, -.30, 0.48) 
        scapulaR = createBone("scapulaR", V_upperBack, V_scapulaR) 
        scapulaR.parent = at.edit_bones['upperBack']  
        scapulaL = createBone("scapulaL", V_upperBack, V_scapulaL)
        scapulaL.parent = at.edit_bones['upperBack']
        # 
        V_humerus1R = (0, .45, 0.47)
        V_humerus1L = (0, -.45, 0.47)
        humerus1R = createBone("humerus1R", (V_scapulaR), V_humerus1R)  
        humerus1R.parent = at.edit_bones['scapulaR']  
        humerus1L = createBone("humerus1L", V_scapulaL, V_humerus1L)
        humerus1L.parent = at.edit_bones['scapulaL']
        #
        V_humerus2R = (0, .60, 0.47)
        V_humerus2L = (0, -.60, 0.47)
        humerus2R = createBone("humerus2R", (V_humerus1R), V_humerus2R)  
        humerus2R.parent = at.edit_bones['humerus1R']  
        humerus2L = createBone("humerus2L", V_humerus1L, V_humerus2L)
        humerus2L.parent = at.edit_bones['humerus1L']
        # 
        V_radius1R = (0, .70, .47)  
        V_radius1L = (0, -.70, .47) 
        radius1R = createBone("radius1R", V_humerus2R, V_radius1R)
        radius1R.parent = at.edit_bones['humerus2R']
        radius1L = createBone("radius1L", V_humerus2L, V_radius1L)
        radius1L.parent = at.edit_bones['humerus2L']
        #
        V_radius2R = (0, .80, .47)  
        V_radius2L = (0, -.80, .47) 
        radius2R = createBone("radius2R", V_radius1R, V_radius2R)
        radius2R.parent = at.edit_bones['radius1R']
        radius2L = createBone("radius2L", V_radius1L, V_radius2L)
        radius2L.parent = at.edit_bones['radius1L']
        #
        V_radius3R = (0, .90, .47)  
        V_radius3L = (0, -.90, .47) 
        radius3R = createBone("radius3R", V_radius2R, V_radius3R)
        radius3R.parent = at.edit_bones['radius2R']
        radius3L = createBone("radius3L", V_radius2L, V_radius3L)
        radius3L.parent = at.edit_bones['radius2L']
        # 
        # Hand
        # Middle Finger bones
        mid_x = 0
        mid_z = .47
        V_wristBase3R = (mid_x, 1.0, mid_z)
        V_wristBase3L = (mid_x, -1.0, mid_z)
        wristBase3R = createBone("wristBase3R", V_radius3R, (V_wristBase3R))
        wristBase3R.parent = at.edit_bones['radius3R']
        wristBase3L = createBone("wristBase3L", V_radius3L, (V_wristBase3L))
        wristBase3L.parent = at.edit_bones['radius3L']
        # 
        V_midJ1R = (mid_x, 1.068, mid_z)
        V_midJ1L = (mid_x, -1.068, mid_z)
        midJ1R = createBone("midJ1R", (V_wristBase3R), (V_midJ1R))
        midJ1R.parent = at.edit_bones['wristBase3R']
        midJ1L = createBone("midJ1L", (V_wristBase3L), (V_midJ1L))
        midJ1L.parent = at.edit_bones['wristBase3L']
        # 
        V_midJ2R = (mid_x, 1.108, mid_z)
        V_midJ2L = (mid_x, -1.108, mid_z)
        midJ2R = createBone("midJ2R", (V_midJ1R), (V_midJ2R))
        midJ2R.parent = at.edit_bones['midJ1R']
        midJ2L = createBone("midJ2L", (V_midJ1L), (V_midJ2L))
        midJ2L.parent = at.edit_bones['midJ1L']    
        # 
        V_midJ3R = (mid_x, 1.132, mid_z)
        V_midJ3L = (mid_x, -1.132, mid_z)
        midJ3R = createBone("midJ3R", (V_midJ2R), (V_midJ3R))
        midJ3R.parent = at.edit_bones['midJ2R']
        midJ3L = createBone("midJ3L", (V_midJ2L), (V_midJ3L))
        midJ3L.parent = at.edit_bones['midJ2L']
        #
        # Index Finger bones
        index_x = .034
        index_z = .47
        V_wristBase4R = (index_x, 1.0, index_z)
        V_wristBase4L = (index_x, -1.0, index_z)
        wristBase4R = createBone("wristBase4R", V_radius3R, (V_wristBase4R))
        wristBase4R.parent = at.edit_bones['radius3R']
        wristBase4L = createBone("wristBase4L", V_radius3L, (V_wristBase4L))
        wristBase4L.parent = at.edit_bones['radius3L']
        # 
        V_indexJ1R = (index_x, 1.054, index_z)
        V_indexJ1L = (index_x, -1.054, index_z)
        indexJ1R = createBone("indexJ1R", (V_wristBase4R), (V_indexJ1R))
        indexJ1R.parent = at.edit_bones['wristBase4R']
        indexJ1L = createBone("indexJ1L", (V_wristBase4L), (V_indexJ1L))
        indexJ1L.parent = at.edit_bones['wristBase4L']
        # 
        V_indexJ2R = (index_x, 1.088, index_z)
        V_indexJ2L = (index_x, -1.088, index_z)
        indexJ2R = createBone("indexJ2R", (V_indexJ1R), (V_indexJ2R))
        indexJ2R.parent = at.edit_bones['indexJ1R']
        indexJ2L = createBone("indexJ2L", (V_indexJ1L), (V_indexJ2L))
        indexJ2L.parent = at.edit_bones['indexJ1L']    
        # 
        V_indexJ3R = (index_x, 1.118, index_z)
        V_indexJ3L = (index_x, -1.118, index_z)
        indexJ3R = createBone("indexJ3R", (V_indexJ2R), (V_indexJ3R))
        indexJ3R.parent = at.edit_bones['indexJ2R']
        indexJ3L = createBone("indexJ3L", (V_indexJ2L), (V_indexJ3L))
        indexJ3L.parent = at.edit_bones['indexJ2L']   
        #        
        # Ring Finger bones
        ring_x = -.034
        ring_z = .47
        V_WristBase2R = (ring_x, 1.0, ring_z)
        V_WristBase2L = (ring_x, -1.0, ring_z)
        wristBase2R = createBone("wristBase2R", V_radius3R, (V_WristBase2R))
        wristBase2R.parent = at.edit_bones['radius3R']
        wristBase2L = createBone("wristBase2L", V_radius3L, (V_WristBase2L))
        wristBase2L.parent = at.edit_bones['radius3L']
        # 
        V_ringJ1R = (ring_x, 1.054, ring_z)
        V_ringJ1L = (ring_x, -1.054, ring_z)
        ringJ1R = createBone("ringJ1R", V_WristBase2R, (V_ringJ1R))
        ringJ1R.parent = at.edit_bones['wristBase2R']
        ringJ1L = createBone("ringJ1L", V_WristBase2L, (V_ringJ1L))
        ringJ1L.parent = at.edit_bones['wristBase2L']
        # 
        V_ringJ2R = (ring_x, 1.088, ring_z)
        V_ringJ2L = (ring_x, -1.088, ring_z)
        ringJ2R = createBone("ringJ2R", (V_ringJ1R), (V_ringJ2R))
        ringJ2R.parent = at.edit_bones['ringJ1R']
        ringJ2L = createBone("ringJ2L", (V_ringJ1L), (V_ringJ2L))
        ringJ2L.parent = at.edit_bones['ringJ1L']
        # 
        V_ringJ3R = (ring_x, 1.118, ring_z)
        V_ringJ3L = (ring_x, -1.118, ring_z)
        ringJ3R = createBone("ringJ3R", (V_ringJ2R), (V_ringJ3R))
        ringJ3R.parent = at.edit_bones['ringJ2R']
        ringJ3L = createBone("ringJ3L", (V_ringJ2L), (V_ringJ3L))
        ringJ3L.parent = at.edit_bones['ringJ2L']
        #
        # Create Pinky bones
        pinky_x = -.068
        pinky_z =.47
        V_wristBaseR = (-.05, .92, pinky_z)
        V_wristBaseL = (-.05, -.92, pinky_z)    
        wristBase1R = createBone("wristBase1R", V_radius3R, V_wristBaseR)
        wristBase1R.parent = at.edit_bones['radius3R']
        wristBase1L = createBone("wristBase1L", V_radius3L, V_wristBaseL)
        wristBase1L.parent = at.edit_bones['radius3L']
        # 
        V_pinkyBaseR = (pinky_x, .99, pinky_z)
        V_pinkyBaseL = (pinky_x, -.99, pinky_z)
        pinkyBaseR = createBone("pinkyBaseR", (V_wristBaseR), (V_pinkyBaseR))
        pinkyBaseR.parent = at.edit_bones['wristBase1R']
        pinkyBaseL = createBone("pinkyBaseL", (V_wristBaseL), (V_pinkyBaseL))
        pinkyBaseL.parent = at.edit_bones['wristBase1L']
        # 
        V_pinkyJ1R = (pinky_x, 1.037, pinky_z)
        V_pinkyJ1L = (pinky_x, -1.037, pinky_z)
        pinkyJ1R = createBone("pinkyJ1R", (V_pinkyBaseR), (V_pinkyJ1R))
        pinkyJ1R.parent = at.edit_bones['pinkyBaseR']
        pinkyJ1L = createBone("pinkyJ1L", (V_pinkyBaseL), (V_pinkyJ1L))
        pinkyJ1L.parent = at.edit_bones['pinkyBaseL']
        # 
        V_pinkyJ2R = (pinky_x, 1.06, pinky_z)
        V_pinkyJ2L = (pinky_x, -1.06, pinky_z)
        pinkyJ2R = createBone("pinkyJ2R", (V_pinkyJ1R), (V_pinkyJ2R))
        pinkyJ2R.parent = at.edit_bones['pinkyJ1R']
        pinkyJ2L = createBone("pinkyJ2L", (V_pinkyJ1L), (V_pinkyJ2L))
        pinkyJ2L.parent = at.edit_bones['pinkyJ1L']
        # 
        V_pinkyJ3R = (pinky_x, 1.08, pinky_z)
        V_pinkyJ3L = (pinky_x, -1.08, pinky_z)
        pinkyJ3R = createBone("pinkyJ3R", (V_pinkyJ2R), (V_pinkyJ3R))
        pinkyJ3R.parent = at.edit_bones['pinkyJ2R']
        pinkyJ3L = createBone("pinkyJ3L", (V_pinkyJ2L), (V_pinkyJ3L))
        pinkyJ3L.parent = at.edit_bones['pinkyJ2L']
        # 
        # Thumb bones
        thumb_z = .47
        V_thumbBaseR = (.06, .94, thumb_z)
        V_thumbBaseL = (.06, -.94, thumb_z)
        thumbBaseR = createBone("thumbBaseR", V_radius3R, V_thumbBaseR)
        thumbBaseR.parent = at.edit_bones['radius3R']
        thumbBaseL = createBone("thumbBaseL", V_radius3L, V_thumbBaseL)
        thumbBaseL.parent = at.edit_bones['radius3L']
        # 
        V_thumbJ1R = (.08, .98, thumb_z-.002)
        V_thumbJ1L = (.08, -.98, thumb_z-.002)
        thumbJ1R = createBone("thumbJ1R", (V_thumbBaseR), (V_thumbJ1R))
        thumbJ1R.parent = at.edit_bones['thumbBaseR']
        thumbJ1L = createBone("thumbJ1L", (V_thumbBaseL), (V_thumbJ1L))
        thumbJ1L.parent = at.edit_bones['thumbBaseL']    
        # 
        V_thumbJ2R = (.1, 1.01, thumb_z-.004)
        V_thumbJ2L = (.1, -1.01, thumb_z-.004)
        thumbJ2R = createBone("thumbJ2R", (V_thumbJ1R), (V_thumbJ2R))
        thumbJ2R.parent = at.edit_bones['thumbJ1R']
        thumbJ2L = createBone("thumbJ2L", (V_thumbJ1L), (V_thumbJ2L))
        thumbJ2L.parent = at.edit_bones['thumbJ1L']        
        # 
        rotate('humerus1L', 1.57, 0)
        rotate('humerus1R', -1.57, 0)
        #
        # Create horse back  and  hind legs.
        # bpy.context.scene.cursor_location = VRigArmatHead
        # "h" Prefix for all horse parts
        V_horseUpperBack = (-0.4, 0, 0)
        V_bonetail = [-0.2, 0, 0]  # From above header section
        hUpperBack = createBone("hUpperBack", V_bonetail, V_horseUpperBack)
        hUpperBack.parent = at.edit_bones[centaur.strName + '_bone']
        #
        V_horseMidBack = (-.6, 0, 0)
        hMidBack = createBone("hMidBack", V_horseUpperBack, V_horseMidBack)
        hMidBack.parent = at.edit_bones['hUpperBack']
        #
        V_horseBackLower = (-.8, 0, 0)
        hBackSway = createBone("hBackSway", V_horseMidBack, V_horseBackLower)
        hBackSway.parent = at.edit_bones['hMidBack']
        #
        V_horseHipCenter = (-1, 0, 0)
        hHipCenter = createBone("hHipCenter", V_horseBackLower, V_horseHipCenter)
        hHipCenter.parent = at.edit_bones['hBackSway']
        #
        hRearHipWidth = .13
        V_horseLHip = (-1, -hRearHipWidth, 0)
        hHipL = createBone("hHipL", V_horseHipCenter, V_horseLHip)
        hHipL.parent = at.edit_bones['hHipCenter']

        V_horseRHip = (-1, hRearHipWidth, 0)
        hHipR = createBone("hHipR", V_horseHipCenter, V_horseRHip)
        hHipR.parent = at.edit_bones['hHipCenter']
        #
        V_horseHipExtL = (-.94, -hRearHipWidth, -.2)
        V_horseHipExtR = (-.94, hRearHipWidth, -.2)
        hHipExtL = createBone("hHipExtL", V_horseLHip, V_horseHipExtL)
        hHipExtL.parent = at.edit_bones['hHipL']
        hHipextR = createBone("hHipExtR", V_horseRHip, V_horseHipExtR)
        hHipextR.parent = at.edit_bones['hHipR']

        V_horseFemurL = (-1.04, -hRearHipWidth, -.6)
        V_horseFemurR = (-1.04, hRearHipWidth, -.6)
        hFemurL = createBone("hFemurL", V_horseHipExtL, V_horseFemurL)
        hFemurL.parent = at.edit_bones['hHipExtL']
        hFemurR = createBone("hFemurR", V_horseHipExtR, V_horseFemurR)
        hFemurR.parent = at.edit_bones['hHipExtR']

        V_horseTibiaL = (-.98, -hRearHipWidth, -.94)
        V_horseTibiaR = (-.98, hRearHipWidth, -.94)
        hTibiaL = createBone("hTibiaL", V_horseFemurL, V_horseTibiaL)
        hTibiaL.parent = at.edit_bones['hFemurL']
        hTibiaR = createBone("hTibiaR", V_horseFemurR, V_horseTibiaR)
        hTibiaR.parent = at.edit_bones['hFemurR']
        #
        V_horseLAnkle = (-.98, -hRearHipWidth, -1.02)
        V_horseRAnkle = (-.98, hRearHipWidth, -1.02)
        hAnkleL = createBone("hAnkleL", V_horseTibiaL, V_horseLAnkle)
        hAnkleL.parent = at.edit_bones['hTibiaL']
        hAnkleR = createBone("hAnkleR", V_horseTibiaR, V_horseRAnkle)
        hAnkleR.parent = at.edit_bones['hTibiaR']
        # 
        V_horseLToe = (-.98, -hRearHipWidth, -1.1)
        V_horseRToe = (-.98, hRearHipWidth, -1.1)
        hToeL = createBone("hToeL", V_horseLAnkle, V_horseLToe)
        hToeL.parent = at.edit_bones['hAnkleL']
        hToeR = createBone("hToeR", V_horseRAnkle, V_horseRToe)
        hToeR.parent = at.edit_bones['hAnkleR']
        #
    def character_type(self):
        return 'centaur'

        
centaur = Centaur
centaur.buildSkeleton(char)
bpy.ops.object.mode_set(mode='OBJECT')
# Do rotations
# 
bpy.ops.object.mode_set(mode='EDIT')

# ###############################################################################
# NEW SPEED FUNCTION   no rate = normal speed   1 = 1/2 rate    2 = double rate
# ###############################################################################
def getCycleRate(rate=0):
    if(hasattr(bpy.types.WindowManager, "cycle")):
        cycleRate = bpy.context.window_manager.cycle + 8
    else:
        cycleRate = 8.0  # Default cycleSpeed
    strRateEquation = "sin(radians(" + str(cycleRate) + "*frame))"
    if(rate == 1):
        strRateEquation = "sin(radians(" + str(cycleRate / 2) + "*frame))"  # Half cycle rate
    if(rate == 2):
        strRateEquation = "sin(radians(" + str(cycleRate * 2) + "*frame))" # Double cycle rate 
    return strRateEquation


def setWalkMovement(self, context):
    if(hasattr(bpy.types.WindowManager, "cycle")):
        cycleSpeed = bpy.context.window_manager.cycle + 8
    else:
        cycleSpeed = 8.0  # Default cycleSpeed
    # Left hip
    fn = "(asin(" + getCycleRate() + ") * 1)/3.14"
    femurLDriver = setAxisDriver(getEuler('femurL'), fn, 2)
    # Right hip
    fn = "-(asin(" + getCycleRate() + ") * 1)/3.14"
    femurRDriver = setAxisDriver(getEuler('femurR'), fn, 2)
    # Left Knee rotate
    fn = "((asin(" + getCycleRate() + ") * 1.2)/3.14 + .4) * (frame*(1/(frame+.0001)))"
    tibiaLDriver = setDriver(getEuler('tibiaL'), fn, 2)
    # Right Knee rotate
    fn = "(-(asin(" + getCycleRate() + ") * 1.2)/3.14 + .4) * (frame*(1/(frame+.0001)))"
    tibiaRDriver = setDriver(getEuler('tibiaR'), fn, 2)
    # Ankle rotation
    # Left
    fn = "((asin(" + getCycleRate() + ") * 2)/3.14 + .9) * (frame*(1/(frame+.0001)))-.8"
    ankleLDriver = setDriver(getEuler('ankleL'), fn, 2)  # 2 is z-axis
    # Right
    fn = "(-(asin(" + getCycleRate() + ") * 2)/3.14 + .9) * (frame*(1/(frame+.0001)))-.8"
    ankleRDriver = setDriver(getEuler('ankleR'), fn, 2)
    # Toe rotation
    # Left
    fn = "((asin(" + getCycleRate() + ") * 1.2)/3.14 + .4) * (frame*(1/(frame+.0001)))+.4"
    toeLDriver = setDriver(getEuler('toeL'), fn, 2)
    # Right
    fn = "((-asin(" + getCycleRate() + ") * 1.2)/3.14 + .4) * (frame*(1/(frame+.0001)))+.4"
    toeRDriver = setDriver(getEuler('toeR'), fn, 2)
    #
    # Upper Back
    fn = "(asin(" + getCycleRate() + ") * .6)/3.14"
    upperBackDriver = setDriver(getEuler('upperBack'), fn, 1)
    # Compensate for shoulder rotate by rotating neck and head in opposite direction, in three parts
    fn = "-(asin(" + getCycleRate() + ") * .2)/3.14"
    lowerNeckDriver = setDriver(getEuler('lowerNeck'), fn, 1)
    midNeckDriver = setDriver(getEuler('midNeck'), fn, 1)
    upperNeckDriver = setDriver(getEuler('upperNeck'), fn, 1)
    # Arms rotation
    # humerus
    bpy.context.object.pose.bones["humerus1L"].rotation_euler[0] = 1.5708
    fn = "(asin(" + getCycleRate() + ") * .8)/3.14"
    humerusLDriver = setAxisDriver(getEuler('humerus1L'), fn, 1)
    bpy.context.object.pose.bones["humerus1R"].rotation_euler[0] = -1.5708
    fn = "(asin(" + getCycleRate() + ") * .8)/3.14"
    humerusRDriver = setAxisDriver(getEuler('humerus1R'), fn, 1)
    # Elbows
    fn = "((asin(" + getCycleRate() + ") * .7)/3.14 + .3) * (frame*(1/(frame+.0001)))"
    radiusLDriver = setDriver(getEuler('radius1L'), fn, 2)
    fn = "((asin(" + getCycleRate() + ") * .7)/3.14 - .3) * (frame*(1/(frame+.0001)))"
    radiusRDriver = setDriver(getEuler('radius1R'), fn, 2)
    bpy.ops.object.mode_set(mode='OBJECT')
    #
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Horse part of body functionality
    # hip
    fn = "-(asin(" + getCycleRate() + ") * .8)/3.14"
    hFemurLDriver = setAxisDriver(getEuler('hFemurL'), fn, 2)
    fn = "(asin(" + getCycleRate() + ") * .8)/3.14"
    hFemurRDriver = setAxisDriver(getEuler('hFemurR'), fn, 2)
    # Knee rotate
    fn = "-(asin(" + getCycleRate() + ") * 1.0)/3.14 + .2"
    hTibiaLDriver = setDriver(getEuler('hTibiaL'), fn, 2)
    fn = "(asin(" + getCycleRate() + ") * 1.0)/3.14 + .2"
    hTibiaRDriver = setDriver(getEuler('hTibiaR'), fn, 2)
    # Ankle rotation
    fn = "(-(asin(" + getCycleRate() + ") * 2)/3.14 + 1.4) * (frame*(1/(frame+.0001)))-1.0"
    hAnkleLDriver = setDriver(getEuler('hAnkleL'), fn, 2)  # 2 is z-axis
    fn = "((asin(" + getCycleRate() + ") * 2)/3.14 + 1.4) * (frame*(1/(frame+.0001)))-1.0"
    hAnkleRDriver = setDriver(getEuler('hAnkleR'), fn, 2)
    # Toe rotation
    fn = "(-(asin(" + getCycleRate() + ") * 1.2)/3.14 + .2) * (frame*(1/(frame+.0001)))+.4"
    hToeLDriver = setDriver(getEuler('hToeL'), fn, 2)
    fn = "((asin(" + getCycleRate() + ") * 1.2)/3.14 + .2) * (frame*(1/(frame+.0001)))+.4"
    hToeRDriver = setDriver(getEuler('hToeR'), fn, 2)    

    
setWalkMovement(centaur, context)

def setArmRotation(centaur, context):
    if(hasattr(bpy.types.WindowManager, "armRotation")):
        armRotation = str(bpy.context.window_manager.armRotation * .2)
    else:
        armRotation = '3.0'
    # Arms rotation
    # humerus
    fn = "(asin(" + getCycleRate() + ") * (" + armRotation + " + .1))/3.14"
    humerusLDriver = setAxisDriver(getEuler('humerus1L'), fn, 1)
    bpy.context.object.pose.bones["humerus1R"].rotation_euler[0] = -1.5708
    fn = "(asin(" + getCycleRate() + ") * (" + armRotation + " + .1))/3.14"
    humerusRDriver = setAxisDriver(getEuler('humerus1R'), fn, 1)
    # Elbows
    fn = "((asin(" + getCycleRate() + ") * " + armRotation + ")/3.14 + .3) * (frame*(1/(frame+.0001)))"
    radiusLDriver = setDriver(getEuler('radius1L'), fn, 2)
    fn = "((asin(" + getCycleRate() + ") * " + armRotation + ")/3.14 - .3) * (frame*(1/(frame+.0001)))"
    radiusRDriver = setDriver(getEuler('radius1R'), fn, 2)
    bpy.ops.object.mode_set(mode='OBJECT')


# setHorizontalSpeed Function controls the horizontal position of the centaur based z-axis rotational orientation
# Not associated with getCycleRate.  Speed is horizontal speed.  Rate is walk cycle frequency.
def setHorizontalSpeed(self, context):
    if(hasattr(bpy.types.WindowManager, "speed")):
        horizontalSpeed = bpy.context.window_manager.speed
    else:
        horizontalSpeed = 0.0  # Default speed
    strPosition = str(bpy.context.scene.frame_current / 2800 * horizontalSpeed)
    strRotateZ = str(bpy.context.scene.objects.active.rotation_euler.z)
    fnx = strPosition + "*frame*-sin(" + strRotateZ + ")"
    fny = strPosition + "*frame*-cos(" + strRotateZ + ")"
    setDriver(getEuler(centaur.strName + '_bone'), fny, 1, 'location')  # bird is 0
    dr_loc = setDriver(getEuler(centaur.strName + '_bone'), fnx, 0, 'location')  # bird is 2 
    bpy.ops.object.mode_set(mode='OBJECT')

  
    
    
def setSwayLR(self, context):  # left - right sway movement
    if(hasattr(bpy.types.WindowManager, "swayLR")):
        swayLR = str(bpy.context.window_manager.swayLR)
    else:
        swayLR = "1.0"
    fn = "-(asin(" + getCycleRate() + ")* " + swayLR + "*.01)"
    setDriver(getEuler(centaur.strName + '_bone'), fn, 1)
    bpy.ops.object.mode_set(mode='OBJECT')

def setSwayFB(self, context):  # forward - backward sway movement
    if(hasattr(bpy.types.WindowManager, "swayFB")):
        swayFB = str(bpy.context.window_manager.swayFB)
    else:
        swayFB = "1.0"
    fn = "-(asin(" + getCycleRate() + ")* " + swayFB + "*.01)"
    dr_SwayFB = setDriver(getEuler(centaur.strName + '_bone'), fn, 0)
    bpy.ops.object.mode_set(mode='OBJECT')
    
def setBounce(self, context):  # Bounce
    if(hasattr(bpy.types.WindowManager, "bounce")):
        bounce = str(bpy.context.window_manager.bounce)
    else:
        bounce = "1.0"
    eqBounce = "-(asin(" + getCycleRate(2) + ")* " + bounce + "*.01)"
    dr_Bounce = setDriver(getEuler(centaur.strName + '_bone'), eqBounce, 2, 'location') # Bounce
    bpy.ops.object.mode_set(mode='OBJECT')

# Head
def setJaw(centaur, context): # Jaw open - close    
    if(hasattr(bpy.types.WindowManager, "jawOC")):
        jawOC = str(bpy.context.window_manager.jawOC)
    else:
        jawOC = "0.0"
    fn = jawOC + " * -.1"  # Jaw open - close
    setDriver(getEuler('jaw'), fn, 0)
    bpy.ops.object.mode_set(mode='OBJECT')


# If centered at rear joint, parented,
# can be used  for eye movements
def setEye(centaur, context):     
    # Left - Right turn motion 
    if(hasattr(bpy.types.WindowManager, "eyeLR")):
        eyeLR = str(bpy.context.window_manager.eyeLR)
    else:
        eyeLR = "0.0"
    fn = str(eyeLR) + "* .1"  # eye left - right
    setDriver(getEuler('eyeR'), fn, 2)
    fn = str(eyeLR) + "* .1"  # eye left - right
    setDriver(getEuler('eyeL'), fn, 2)
    # Up - Down turn motion 
    eyeUD = str(centaur.eyeUD)  # Eye left - right
    if(hasattr(bpy.types.WindowManager, "eyeUD")):
        eyeUD = str(bpy.context.window_manager.eyeUD)
    else:
        eyeUD = "0.0"
    fn = str(eyeUD) + "* .1"  # eye left - right
    setDriver(getEuler('eyeL'), fn, 0)
    fn = str(eyeUD) + "* .1"  # eye left - right
    setDriver(getEuler('eyeR'), fn, 0)
    bpy.ops.object.mode_set(mode='OBJECT')


# Set Head Up - Down
def setHead(centaur, context):
    # Up - Down turn motion 
    if(hasattr(bpy.types.WindowManager, "headUD")):
        headUD = str(bpy.context.window_manager.headUD)
    else:
        headUD = "0.0"
    fn = str(headUD) + "* -.1"  
    setAxisDriver(getEuler('lowerNeck'), fn, 2)
    setAxisDriver(getEuler('midNeck'), fn, 2)
    setAxisDriver(getEuler('upperNeck'), fn, 2)
    # Sideways motion 
    if(hasattr(bpy.types.WindowManager, "headLR")):
        headLR = str(bpy.context.window_manager.headLR)
    else:
        headLR = "0.0"
    fn = str(headLR) + "* -.1"  
    setAxisDriver(getEuler('lowerNeck'), fn, 0)
    setAxisDriver(getEuler('midNeck'), fn, 0)
    setAxisDriver(getEuler('upperNeck'), fn, 0)
    # Left - Right turn motion 
    eyeUD = str(centaur.eyeUD)  # left - right
    if(hasattr(bpy.types.WindowManager, "headTurn")):
        headTurn = str(bpy.context.window_manager.headTurn)
    else:
        headTurn = "0.0"
    LR = str(headTurn) + "* .1"  # head left - right
    fn = "-(asin(" + getCycleRate() + ") * .2)/3.14 + " + LR
    lowerNeckDriver = setAxisDriver(getEuler('lowerNeck'), fn, 1)
    midNeckDriver = setAxisDriver(getEuler('midNeck'), fn, 1)
    upperNeckDriver = setAxisDriver(getEuler('upperNeck'), fn, 1)
    bpy.ops.object.mode_set(mode='OBJECT')

   

def setArms(centaur, context):
    if(hasattr(bpy.types.WindowManager, "armsUD")):
        armsUD = bpy.context.window_manager.armsUD
    else:
        armsUD = 0.0
    bpy.context.object.pose.bones["humerus1R"].rotation_euler[0] = -.1 * armsUD + 6.3
    bpy.context.object.pose.bones["humerus1L"].rotation_euler[0] = .1 * armsUD + 6.3
    bpy.ops.object.mode_set(mode='OBJECT')


def setArmLTwist(centaur, context):
    if(hasattr(bpy.types.WindowManager, "armLTwist")):
        armLTwist = bpy.context.window_manager.armLTwist
    else:
        armLTwist =  0.0
    fn =  "(asin(" + getCycleRate() + ") * .8)/3.14 + .1 * " + str(armLTwist)
    humerusLDriver = setAxisDriver(getEuler('humerus1L'), fn, 1)
    bpy.context.object.pose.bones["humerus2L"].rotation_euler[1] = .1 * armLTwist
    radiusLDriver = setAxisDriver(getEuler('radius1L'), fn, 1)
    bpy.context.object.pose.bones["radius2L"].rotation_euler[1] = .1 * armLTwist
    bpy.context.object.pose.bones["radius3L"].rotation_euler[1] = .1 * armLTwist
    bpy.ops.object.mode_set(mode='OBJECT')
    

def setArmRTwist(centaur, context):
    if(hasattr(bpy.types.WindowManager, "armRTwist")):
        armRTwist = bpy.context.window_manager.armRTwist
    else:
        armRTwist =  0.0
    fn =  "(asin(" + getCycleRate() + ") * .8)/3.14 + .1 * " + str(armRTwist)
    humerusRDriver = setAxisDriver(getEuler('humerus1R'), fn, 1)
    bpy.context.object.pose.bones["humerus2R"].rotation_euler[1] = -.1 * armRTwist
    radiusRDriver = setAxisDriver(getEuler('radius1R'), fn, 1)
    bpy.context.object.pose.bones["radius2R"].rotation_euler[1] = -.1 * armRTwist
    bpy.context.object.pose.bones["radius3R"].rotation_euler[1] = -.1 * armRTwist
    bpy.ops.object.mode_set(mode='OBJECT')
    

    
def setLHand(centaur, context): # Left hand open - close    
    if(hasattr(bpy.types.WindowManager, "LHandOC")):
        LHandOC = str(bpy.context.window_manager.LHandOC)
    else:
        LHandOC = "0.0"
    fn = LHandOC + " * -.1"  # hand open - close
    setDriver(getEuler('indexJ1L'), fn, 0)
    setDriver(getEuler('indexJ2L'), fn, 0)
    setDriver(getEuler('indexJ3L'), fn, 0)
    setDriver(getEuler('midJ1L'), fn, 0)
    setDriver(getEuler('midJ2L'), fn, 0)
    setDriver(getEuler('midJ3L'), fn, 0)
    setDriver(getEuler('ringJ1L'), fn, 0)
    setDriver(getEuler('ringJ2L'), fn, 0)
    setDriver(getEuler('ringJ3L'), fn, 0)
    setDriver(getEuler('pinkyJ1L'), fn, 0)
    setDriver(getEuler('pinkyJ2L'), fn, 0)
    setDriver(getEuler('pinkyJ3L'), fn, 0)
    if(hasattr(bpy.types.WindowManager, "LHandSpread")):
        LHandSpread = str(bpy.context.window_manager.LHandSpread)
    else:
        LHandSpread = "0.0"
    fn = LHandSpread + " * .1"  # Left hand spread
    setDriver(getEuler('indexJ1L'), fn, 2)
    fn = LHandSpread + " * -.1"  # Left hand spread
    setDriver(getEuler('ringJ1L'), fn, 2)
    fn = LHandSpread + " * -.2"  # Left hand spread
    setDriver(getEuler('pinkyJ1L'), fn, 2)
    bpy.ops.object.mode_set(mode='OBJECT')

def setRHand(centaur, context): # Right hand open - close    
    if(hasattr(bpy.types.WindowManager, "RHandOC")):
        RHandOC = str(bpy.context.window_manager.RHandOC)
    else:
        RHandOC = "0.0"
    fn = RHandOC + " * -.1"  # hand open - close
    setDriver(getEuler('indexJ1R'), fn, 0)
    setDriver(getEuler('indexJ2R'), fn, 0)
    setDriver(getEuler('indexJ3R'), fn, 0)
    setDriver(getEuler('midJ1R'), fn, 0)
    setDriver(getEuler('midJ2R'), fn, 0)
    setDriver(getEuler('midJ3R'), fn, 0)
    setDriver(getEuler('ringJ1R'), fn, 0)
    setDriver(getEuler('ringJ2R'), fn, 0)
    setDriver(getEuler('ringJ3R'), fn, 0)
    setDriver(getEuler('pinkyJ1R'), fn, 0)
    setDriver(getEuler('pinkyJ2R'), fn, 0)
    setDriver(getEuler('pinkyJ3R'), fn, 0)
    if(hasattr(bpy.types.WindowManager, "RHandSpread")):
        RHandSpread = str(bpy.context.window_manager.RHandSpread)
    else:
        RHandSpread = "0.0"
    fn = RHandSpread + " * -.1"  # Right hand spread
    setDriver(getEuler('indexJ1R'), fn, 2)
    fn = RHandSpread + " * .1"  # Right hand spread
    setDriver(getEuler('ringJ1R'), fn, 2)
    fn = RHandSpread + " * .2"  # Right hand spread
    setDriver(getEuler('pinkyJ1R'), fn, 2)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    
    
def setShoulder(centaur, context):
    if(hasattr(bpy.types.WindowManager, "shoulderRotate")):
        shoulderRotate = str(bpy.context.window_manager.shoulderRotate*.1)
    else:
        shoulderRotate = '0.0'
    # Upper Back
    fn = "(asin(" + getCycleRate() + ") * " + shoulderRotate + ")/3.14"
    upperBackDriver = setDriver(getEuler('upperBack'), fn, 1)
    # Compensate for shoulder rotate by rotating neck and head in opposite direction, in three parts
    fn = "-(asin(" + getCycleRate() + ") * " + shoulderRotate + "/3)/3.14"
    lowerNeckDriver = setDriver(getEuler('lowerNeck'), fn, 1)
    midNeckDriver = setDriver(getEuler('midNeck'), fn, 1)
    upperNeckDriver = setDriver(getEuler('upperNeck'), fn, 1)
    # Shoulder up - down movement
    if(hasattr(bpy.types.WindowManager, "shoulderUD")):
        shoulderUD = str(bpy.context.window_manager.shoulderUD*.06)
    else:
        shoulderUD = '0.0'
    fn = "(asin(" + getCycleRate() + ") * " + shoulderUD + ")/3.14"
    scapulaLDriver = setDriver(getEuler('scapulaL'), fn, 0)
    fn = "(asin(" + getCycleRate() + ") * " + shoulderUD + ")/3.14"
    scapulaRDriver = setDriver(getEuler('scapulaR'), fn, 0)
    bpy.ops.object.mode_set(mode='OBJECT')

    
def setHip(centaur, context):
    # Pelvis / Hip rotation    
    if(hasattr(bpy.types.WindowManager, "hipRotate")):
        hipRotate = str(bpy.context.window_manager.hipRotate*.1)
    else:
        hipRotate = '0.0'
    fn = "(asin(" + getCycleRate() + ") * " + hipRotate + ")/3.14"
    pelvisDriver = setAxisDriver(getEuler('pelvis'), fn, 1)
    # hip up - down movement
    if(hasattr(bpy.types.WindowManager, "hipUD")):
        hipUD = str(bpy.context.window_manager.hipUD*.06)
    else:
        hipUD = '0.0'
    fn = "(asin(" + getCycleRate() + ") * " + hipUD + ")/3.14"
    scapulaLDriver = setDriver(getEuler('hipL'), fn, 0)
    fn = "-(asin(" + getCycleRate() + ") * " + hipUD + ")/3.14"
    scapulaRDriver = setDriver(getEuler('hipR'), fn, 0)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    
# deselect all objects.
bpy.ops.object.mode_set(mode='OBJECT')
for ob in bpy.context.selected_objects:
    ob.select = False

# Get the current vector coordinates of the centaur
centaur.x = bpy.context.scene.objects.active.location.x
centaur.y = bpy.context.scene.objects.active.location.y
centaur.z = bpy.context.scene.objects.active.location.z

bpy.types.WindowManager.speed = bpy.props.FloatProperty(update=setHorizontalSpeed, name="Speed", default=0.0)
bpy.types.WindowManager.cycle = bpy.props.FloatProperty(update=setWalkMovement, name="Cycle", default=1.0)
bpy.types.WindowManager.swayLR = bpy.props.FloatProperty(update=setSwayLR, name="Sway LR", default=1.0)
bpy.types.WindowManager.swayFB = bpy.props.FloatProperty(update=setSwayFB, name="Sway FB", default=0.0)
bpy.types.WindowManager.bounce = bpy.props.FloatProperty(update=setBounce, name="Bounce", default=1.0)
bpy.types.WindowManager.hipRotate = bpy.props.FloatProperty(update=setHip, name="Hip Rotate", default=2.0)
bpy.types.WindowManager.hipUD = bpy.props.FloatProperty(update=setHip, name="HipUD", default=2.0)
bpy.types.WindowManager.armsUD = bpy.props.FloatProperty(update=setArms, name="ArmsUD", default=0.0)
bpy.types.WindowManager.shoulderRotate = bpy.props.FloatProperty(update=setShoulder, name="Shoulder Rotate", default=3.0)
bpy.types.WindowManager.shoulderUD = bpy.props.FloatProperty(update=setShoulder, name="ShoulderUD", default=3.0)
bpy.types.WindowManager.armLTwist = bpy.props.FloatProperty(update= setArmLTwist, name="L Arm Twist", default=0.0)
bpy.types.WindowManager.armRTwist = bpy.props.FloatProperty(update= setArmRTwist, name="R Arm Twist", default=0.0)
bpy.types.WindowManager.armRotation = bpy.props.FloatProperty(update=setArmRotation, name="Arm Rotation", default=3.0)
bpy.types.WindowManager.LHandSpread = bpy.props.FloatProperty(update=setLHand, name="LHand Spread", default=0.0)
bpy.types.WindowManager.LHandOC = bpy.props.FloatProperty(update=setLHand, name="LHandOC", default=0.0)
bpy.types.WindowManager.RHandSpread = bpy.props.FloatProperty(update=setRHand, name="RHand Spread", default=0.0)
bpy.types.WindowManager.RHandOC = bpy.props.FloatProperty(update=setRHand, name="RHandOC", default=0.0)
bpy.types.WindowManager.headUD = bpy.props.FloatProperty(update=setHead, name="HeadUD", default=0.0)
bpy.types.WindowManager.headLR = bpy.props.FloatProperty(update=setHead, name="HeadLR", default=0.0)
bpy.types.WindowManager.headTurn = bpy.props.FloatProperty(update=setHead, name="HeadTurn", default=0.0)
bpy.types.WindowManager.jawOC = bpy.props.FloatProperty(update=setJaw, name="JawOC", default=0.0)
bpy.types.WindowManager.eyeLR = bpy.props.FloatProperty(update=setEye, name="EyeLR", default=0.0)
bpy.types.WindowManager.eyeUD = bpy.props.FloatProperty(update=setEye, name="EyeUD", default=0.0)



class Pose_Button(bpy.types.Operator):
    bl_idname = "pose.button"
    bl_label = "Pose Character"
    bl_description = "Pose Character"
    hidden = False
    def execute(self, context):
        bpy.context.object.pose.bones["humerus1R"].rotation_euler[0] = 0
        bpy.context.object.pose.bones["humerus1L"].rotation_euler[0] = 0
        bpy.context.scene.frame_set(0)
        bpy.ops.object.mode_set(mode='OBJECT')
        return{'FINISHED'}

        
class DropArms_Button(bpy.types.Operator):
    bl_idname = "drop_arms.button"
    bl_label = "Drop Arms"
    bl_description = "Drop Character Arms"
    hidden = False
    def execute(self, context):
        bpy.context.object.pose.bones["humerus1R"].rotation_euler[0] = -1.57
        bpy.context.object.pose.bones["humerus1L"].rotation_euler[0] = 1.57
        bpy.ops.object.mode_set(mode='OBJECT')
        return{'FINISHED'}

        
class OBPanel(bpy.types.Panel):
    bl_label = "centaur Control"
    bl_idname = "selected_object"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "UI"
    bl_context = "objectmode"
    def draw(self, context):
        layout = self.layout
        layout.row().prop(context.window_manager, 'speed')
        layout.row().prop(context.window_manager, 'cycle')
        layout.row().prop(context.window_manager, 'swayLR')
        layout.row().prop(context.window_manager, 'swayFB')
        layout.row().prop(context.window_manager, 'bounce')
        layout.row().prop(context.window_manager, 'hipRotate')
        layout.row().prop(context.window_manager, 'hipUD')
        layout.row().prop(context.window_manager, 'armsUD')
        layout.row().prop(context.window_manager, 'shoulderRotate')
        layout.row().prop(context.window_manager, 'shoulderUD')
        layout.row().prop(context.window_manager, 'armLTwist')
        layout.row().prop(context.window_manager, 'armRTwist')
        layout.row().prop(context.window_manager, 'armRotation')
        layout.row().prop(context.window_manager, 'LHandSpread')
        layout.row().prop(context.window_manager, 'LHandOC')
        layout.row().prop(context.window_manager, 'RHandSpread')
        layout.row().prop(context.window_manager, 'RHandOC')
        layout.row().prop(context.window_manager, 'headUD')
        layout.row().prop(context.window_manager, 'headLR')
        layout.row().prop(context.window_manager, 'headTurn')
        layout.row().prop(context.window_manager, 'jawOC')
        layout.row().prop(context.window_manager, 'eyeLR')
        layout.row().prop(context.window_manager, 'eyeUD')
        layout.row().operator("pose.button")
        layout.row().operator("drop_arms.button")
        

def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.mode_set(mode='OBJECT')

if __name__ == "__main__":
    register()
