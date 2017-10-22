# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Generalized header code section
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
import bpy, math
from bpy.types import Panel, Menu
from rna_prop_ui import PropertyPanel
from abc import ABCMeta, abstractmethod


# General Use Functions.  Rotate the easy way, changes to pose mode and back
# name a string i.e., rotate('backCenter', .2, 1)
def rotate(name, rad, axis=0):
    currentMode = bpy.context.object.mode
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
# bpy.data.objects['rg00bird'].pose.bones["backCenter"]
def getEuler(str_bone_name):
    bpy.ops.object.mode_set(mode='POSE')
    ob = bpy.context.object
    euler = ob.pose.bones[str_bone_name]
    euler.rotation_mode = 'XYZ'
    return euler


# Equation for bone joints, with euler transform, axis 0=x 1=y 2=z
# Note also that fn must be inserted as a STRING in the expression!
def setDriver(euler, fn="0", axis=0, movementType='rotation_euler'):
    eulerDriver = euler.driver_add(movementType)
    eulerDriver[axis].driver.type = 'SCRIPTED'
    eulerDriver[axis].driver.expression = fn
    return eulerDriver
    # setDriver(getEuler(bird.strName + '_bone'), eqBodySwayFB, 2)
    
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
    strSpeed = "sin(radians(" + str(cycleSpeed) + "*frame))"  # String form of cyclespeed equation
    strHalfSpeed = "sin(radians(" + str(cycleSpeed / 2) + "*frame))"  # String form of halfcyclespeed equation
    strDoubleSpeed = "sin(radians(" + str(cycleSpeed * 2) + "*frame))" # Double Speed
    bodySwayRL = 1.0  # Initialize Right - left body sway 
    bodySwayFB = 0.0  # Initialize forward - backward body sway
    bounce = 1.0
    # For Pose at frame zero - Override function on frame zero, allowing for posing.
    strZeroMovement = " * (frame * (1/(frame+.0001)))"  # This includes outside math operator *
    strZeroOutPose = " * abs((frame/(frame + .0001))-1)"  # Override posePosition when frame NOT zero
    @abstractmethod
    def character_type(self):
        """" For returning a string representing the type of character this is."""
        pass


char = Character
# Do not remove spaces below, they correspond to command line entries
for ob in list(bpy.data.objects):
    if ob.name.startswith('rg') == True:
        char.n = char.n + 1  # increment rig number each time  one  is built.

char.strName = setCharacterName('bird', char.n)  # biped, quadruped, bird, spider, kangaroo
# Start character armature and bones
# Do not remove spaces above, they correspond to command line entries
at = bpy.data.armatures.new(char.strName + '_at')  # at = Armature 
char.rig = bpy.data.objects.new(char.strName, at)  # rig = Armature object
# rg00 (or the one in a series we are building) is now bpy.context.active_object
at.show_names = char.showNames
at.show_axes = char.show_axes

# Each new object created will be placed in a new location
char.height = 1.4  # Sets the height of the character handle
char.x = .3 * char.n;
char.y = 3.2 * char.n;
char.z = char.height;
char.rig.location = (char.x, char.y, char.height)  # Set armature location
char.rig.show_x_ray = char.show_xray
linkObjectsToScene(char.rig)

bpy.ops.object.mode_set(mode='EDIT')
# The lines below create the handle for moving the character
bone = at.edit_bones.new(char.strName + '_bone')

bone.head = [0.0, 0.0, 0.0]  # LOCAL COORDINATE, [0,0,0] places bone directly on armature.
bone.tail = [0, 0.0, 0.3]  # x - horizontal handle   z - vertical handle
char.rootBoneHead = bone.head
char.rootBoneTail = bone.tail
char.rootBone = bone


# THINGS ABOVE THAT MAY VARY BASED ON THE CHARACTER:
# 1. rig location x =  .3 * n; y = 3.2 * n; z = 0.1;
#   This can set the initial height of the character. 
# 2. bone.tail sets the general orientation of the
#   handle created for moving the character - this
#   could vary, based  on the type of character.
# 3. Character name - biped, quadruped, bird, spider, kangaroo

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# End generalized header code section
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%




class Bird(Character):
    # PP = Pose Position
    hipPP = 0.72
    femurPP = 0.0
    tibiaPP = 0
    anklePP = 0
    toesJoint2PP = -.3
    toesJoint3PP = 0
    rearTarsalandClawPP = 0
    #
    # Walk Settings
    # RP = Rotate Position
    hipWalkRP = 0.1
    femurWalkRP = 0
    tibiaWalkRP = 0
    ankleWalkRP = 1.4
    toesWalkJoint2RP = -0.2
    # RR = Rotate Range
    hipWalkRR = 1.0
    femurWalkRR = 1.0
    tibiaWalkRR = 1.0
    ankleWalkRR = .9
    toesWalkJoint2RR = 1.8
    #
    # Claw Grip
    toes3rdJointRP = 0  # Direct control, not related to walk
    rearTarsalandClawRP = 0  # Direct control, not related to walk
    #
    # Wings
    wingPP = 0.0  # PP = Pose Position
    wingRP = 0.0  # RP = Rotate Position
    wingRR = 3.0  # RR = Rotate Range
    wingFB = 0.0     # Wing forward - backward position
    wingMidFB = 0.0  # Mid wing forward - backward position
    wingSpeed = 1.0  # This is the speed of wing movement
    strWingSpeed = "sin(radians(" + str(wingSpeed) + "*frame))"
    #
    # Neck movement
    neckFB = 1.0
    #
    def buildSkeleton(self):
        # START BUILDING SKELETON %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # Vpart = (x, y, z)  #  V for vector
        # bone = createBone('name', Vhead, Vtail)
        # parent to name of last bone created
        # bpy.context.object.pose.bones["backCenter"].rotation_euler[0] = 0.785398
        VbackCenterTip = (-0.12, 0, 0)
        backCenter = createBone("backCenter", bird.rootBoneHead, VbackCenterTip)
        backCenter.parent = at.edit_bones[bird.strName + '_bone']
        # add roughly (0, .06, .03) respectfully on L-series
        VbackL1 = (-0.24, 0, 0)
        b = createBone("backL1", VbackCenterTip, VbackL1)
        b.parent = at.edit_bones['backCenter']
        VbackL2 = (-0.36, 0, 0)
        b = createBone("backL2", VbackL1, VbackL2)
        b.parent = at.edit_bones['backL1']
        VbackL3 = (-0.48, 0, 0)
        b = createBone("backL3", VbackL2, VbackL3)
        b.parent = at.edit_bones['backL2']
        VbackL4 = (-0.6, 0, 0)
        b = createBone("backL4", VbackL3, VbackL4)
        b.parent = at.edit_bones['backL3']
        # straight, non-flexible part of rear back
        VbackL5 = (-0.76, 0, 0)
        b = createBone("backL5", VbackL4, VbackL5)
        b.parent = at.edit_bones['backL4']
        # straight, non-flexible part of rear back
        VbackL6 = (-0.92, 0, 0)
        b = createBone("backL6", VbackL5, VbackL6)
        b.parent = at.edit_bones['backL5']
        # Tail Base
        VtailL1 = (-1.04, 0, 0)
        b = createBone("tailL1", VbackL6, VtailL1)
        b.parent = at.edit_bones['backL6']
        VtailL2 = (-1.16, 0, 0)
        b = createBone("tailL2", VtailL1, VtailL2)
        b.parent = at.edit_bones['tailL1']
        # End Bottom part of spine
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # Start Top part of spine
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        Vneck01 = (0.1, 0, 0)
        b = createBone("neck01", bird.rootBoneHead, Vneck01)
        b.parent = at.edit_bones['backCenter']
        Vneck02 = (0.18, 0, 0)
        b = createBone("neck02", Vneck01, Vneck02)
        b.parent = at.edit_bones['neck01']
        Vneck03 = (0.24, 0, 0)
        b = createBone("neck03", Vneck02, Vneck03)
        b.parent = at.edit_bones['neck02']
        Vneck04 = (0.30, 0, 0)
        b = createBone("neck04", Vneck03, Vneck04)
        b.parent = at.edit_bones['neck03']
        Vneck05 = (0.36, 0, 0)
        b = createBone("neck05", Vneck04, Vneck05)
        b.parent = at.edit_bones['neck04']
        Vneck06 = (0.42, 0, 0)
        b = createBone("neck06", Vneck05, Vneck06)
        b.parent = at.edit_bones['neck05']
        Vneck07 = (0.48, 0, 0)
        b = createBone("neck07", Vneck06, Vneck07)
        b.parent = at.edit_bones['neck06']
        Vneck08 = (0.56, 0, 0)
        b = createBone("neck08", Vneck07, Vneck08)
        b.parent = at.edit_bones['neck07']
        VheadBase = (0.66, 0, 0)
        b = createBone("headBase", Vneck08, VheadBase)
        b.parent = at.edit_bones['neck08']
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # Start Bird Head
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        VjawBase = (0.55, 0, -0.11)
        b = createBone("jawBase", Vneck08, VjawBase)
        b.parent = at.edit_bones['headBase']
        Vjaw = (0.55, 0, -0.2)
        b = createBone("jaw", VjawBase, Vjaw)
        b.parent = at.edit_bones['jawBase']
        # Beak base
        VoffJoint = (.58, 0, 0)
        VbeakBase = (0.588, 0, -0.11)
        b = createBone("beakBase", VoffJoint, VbeakBase)
        b.parent = at.edit_bones['headBase']
        Vbeak = (0.588, 0, -0.2)
        b = createBone("beak", VbeakBase, Vbeak)
        b.parent = at.edit_bones['beakBase']
        # Head Top
        Vheadtop = (0.7, 0, 0)
        b = createBone("headtop", VheadBase, Vheadtop)
        b.parent = at.edit_bones['headBase']
        # Head L - R
        VheadL = (0.64, 0.07, 0)
        b = createBone("headL", VheadBase, VheadL)
        b.parent = at.edit_bones['headBase']
        VheadR = (0.64, -0.07, 0)
        b = createBone("headR", VheadBase, VheadR)
        b.parent = at.edit_bones['headBase']
        VeyeBaseL = (0.64, 0.07, -0.1)
        b = createBone("eyeBaseL", VheadL, VeyeBaseL)
        b.parent = at.edit_bones['headL']
        VeyeBaseR = (0.64, -0.07, -0.1)
        b = createBone("eyeBaseR", VheadR, VeyeBaseR)
        b.parent = at.edit_bones['headR']
        # Eye Left and Right
        VeyeL = (0.64, 0.07, -0.13)
        b = createBone("eyeL", VeyeBaseL, VeyeL)
        b.parent = at.edit_bones['eyeBaseL']
        VeyeR = (0.64, -0.07, -0.13)
        b = createBone("eyeR", VeyeBaseR, VeyeR)
        b.parent = at.edit_bones['eyeBaseR']
        # Crest
        Vcrest = (0.84, 0, 0)
        b = createBone("crest", Vheadtop, Vcrest)
        b.parent = at.edit_bones['headtop']
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # Start wings
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        VwingL_J1 = (0, 0.3, 0)
        b = createBone("wingL_J1", bird.rootBoneHead, VwingL_J1)
        b.parent = at.edit_bones[bird.strName + '_bone']
        VwingL_J2 = (0, 0.6, 0)
        b = createBone("wingL_J2", VwingL_J1, VwingL_J2)
        b.parent = at.edit_bones['wingL_J1']
        VwingL_J3 = (0, 0.9, 0)
        b = createBone("wingL_J3", VwingL_J2, VwingL_J3)
        b.parent = at.edit_bones['wingL_J2']
        VwingL_J4 = (0, 1.2, 0)
        b = createBone("wingL_J4", VwingL_J3, VwingL_J4)
        b.parent = at.edit_bones['wingL_J3']
        VwingL_J5 = (0, 1.5, 0)
        b = createBone("wingL_J5", VwingL_J4, VwingL_J5)
        b.parent = at.edit_bones['wingL_J4']
        VwingL_J6 = (0, 1.7, 0)
        b = createBone("wingL_J6", VwingL_J5, VwingL_J6)
        b.parent = at.edit_bones['wingL_J5']
        VwingL_J7 = (0, 1.9, 0)
        b = createBone("wingL_J7", VwingL_J6, VwingL_J7)
        b.parent = at.edit_bones['wingL_J6']
        VwingL_J8 = (0, 2.0, 0)
        b = createBone("wingL_J8", VwingL_J7, VwingL_J8)
        b.parent = at.edit_bones['wingL_J7']
        VwingR_J1 = (0, -0.3, 0)
        b = createBone("wingR_J1", bird.rootBoneHead, VwingR_J1)
        b.parent = at.edit_bones[bird.strName + '_bone']
        VwingR_J2 = (0, -0.6, 0)
        b = createBone("wingR_J2", VwingR_J1, VwingR_J2)
        b.parent = at.edit_bones['wingR_J1']
        VwingR_J3 = (0, -0.9, 0)
        b = createBone("wingR_J3", VwingR_J2, VwingR_J3)
        b.parent = at.edit_bones['wingR_J2']
        VwingR_J4 = (0, -1.2, 0)
        b = createBone("wingR_J4", VwingR_J3, VwingR_J4)
        b.parent = at.edit_bones['wingR_J3']
        VwingR_J5 = (-0, -1.5, 0)
        b = createBone("wingR_J5", VwingR_J4, VwingR_J5)
        b.parent = at.edit_bones['wingR_J4']
        VwingR_J6 = (0, -1.7, 0)
        b = createBone("wingR_J6", VwingR_J5, VwingR_J6)
        b.parent = at.edit_bones['wingR_J5']
        VwingR_J7 = (0, -1.9, 0)
        b = createBone("wingR_J7", VwingR_J6, VwingR_J7)
        b.parent = at.edit_bones['wingR_J6']
        VwingR_J8 = (0, -2.0, 0)
        b = createBone("wingR_J8", VwingR_J7, VwingR_J8)
        b.parent = at.edit_bones['wingR_J7']
        # Relative to VbackL4 = (-0.6, 0, 0)
        VhipBase = (-0.6, 0, -0.12)
        b = createBone("hipBase", VbackL3, VhipBase)
        b.parent = at.edit_bones['backL3']
        VhipL = (-0.6, 0.22, -0.12)
        b = createBone("hipL", VhipBase, VhipL)
        b.parent = at.edit_bones['hipBase']
        VhipR = (-0.6, -0.22, -.12)
        b = createBone("hipR", VhipBase, VhipR)
        b.parent = at.edit_bones['hipBase']
        # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        # Legs
        # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        VhipExtL = (-0.6, 0.22, -0.4)
        b = createBone("hipExtL", VhipL, VhipExtL)
        b.parent = at.edit_bones['hipL']
        VhipExtR = (-0.6, -0.22, -0.4)
        b = createBone("hipExtR", VhipR, VhipExtR)
        b.parent = at.edit_bones['hipR']
        VfemurL = (-0.6, 0.22, -0.7)
        b = createBone("femurL", VhipExtL, VfemurL)
        b.parent = at.edit_bones['hipExtL']
        VfemurR = (-0.6, -0.22, -0.7)
        b = createBone("femurR", VhipExtR, VfemurR)
        b.parent = at.edit_bones['hipExtR']
        VtibiaL = (-0.6, 0.22, -.96)
        b = createBone("tibiaL", VfemurL, VtibiaL)
        b.parent = at.edit_bones['femurL']
        VtibiaR = (-0.6, -0.22, -.96)
        b = createBone("tibiaR", VfemurR, VtibiaR)
        b.parent = at.edit_bones['femurR']
        VankleJointL = (-0.6, 0.22, -1)
        b = createBone("ankleJointL", VtibiaL, VankleJointL)
        b.parent = at.edit_bones['tibiaL']
        VankleJointR = (-0.6, -0.22, -1)
        b = createBone("ankleJointR", VtibiaR, VankleJointR)
        b.parent = at.edit_bones['tibiaR']
        # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        # Left Foot
        # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        # Rear Claw
        # Rear Claw
        VLLegRearCenterTarsal = (-0.7, 0.22, -1.0)
        b = createBone("LLegRearCenterTarsal", VankleJointL, VLLegRearCenterTarsal)
        b.parent = at.edit_bones['ankleJointL']
        VLLegRearCenterClaw = (-0.8, 0.22, -1.0)
        b = createBone("LLegRearCenterClaw", VLLegRearCenterTarsal, VLLegRearCenterClaw)
        b.parent = at.edit_bones['LLegRearCenterTarsal']
        # Center Claw
        VLLegFrontCenterTarsal = (-0.5, 0.22, -1.0)
        b = createBone("LLegFrontCenterTarsal", VankleJointL, VLLegFrontCenterTarsal)
        b.parent = at.edit_bones['ankleJointL']
        VLLegFrontCenterExt = (-0.4, 0.22, -1.0)
        b = createBone("LLegFrontCenterExt", VLLegFrontCenterTarsal, VLLegFrontCenterExt)
        b.parent = at.edit_bones['LLegFrontCenterTarsal']
        VLLegFrontCenterClaw = (-0.34, 0.22, -1.0)
        b = createBone("LLegFrontCenterClaw", VLLegFrontCenterExt, VLLegFrontCenterClaw)
        b.parent = at.edit_bones['LLegFrontCenterExt']
        # Left Claw Left Leg
        VLLegInsideTarsal = (-0.6, 0.08, -1.0)
        b = createBone("LLegInsideTarsal", VankleJointL, VLLegInsideTarsal)
        b.parent = at.edit_bones['ankleJointL']
        VLLegInsideClaw = (-0.6, 0, -1.0)
        b = createBone("LLegInsideClaw", VLLegInsideTarsal, VLLegInsideClaw)
        b.parent = at.edit_bones['LLegInsideTarsal']
        # Right Claw Left Leg
        VLLegOutsideTarsal = (-0.6, 0.32, -1.0)
        b = createBone("LLegOutsideTarsal", VankleJointL, VLLegOutsideTarsal)
        b.parent = at.edit_bones['ankleJointL']
        VLLegOutsideClaw = (-0.6, 0.4, -1.0)
        b = createBone("LLegOutsideClaw", VLLegOutsideTarsal, VLLegOutsideClaw)
        b.parent = at.edit_bones['LLegOutsideTarsal']
        # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        # Right Foot
        # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        # Rear Claw
        VRLegRearCenterTarsal = (-0.7, -0.22, -1.0)
        b = createBone("RLegRearCenterTarsal", VankleJointR, VRLegRearCenterTarsal)
        b.parent = at.edit_bones['ankleJointR']
        VRLegRearCenterClaw = (-0.8, -0.22, -1.0)
        b = createBone("RLegRearCenterClaw", VRLegRearCenterTarsal, VRLegRearCenterClaw)
        b.parent = at.edit_bones['RLegRearCenterTarsal']
        # Center Claw
        VRLegFrontCenterTarsal = (-0.5, -0.22, -1.0)
        b = createBone("RLegFrontCenterTarsal", VankleJointR, VRLegFrontCenterTarsal)
        b.parent = at.edit_bones['ankleJointR']
        VRLegFrontCenterExt = (-0.4, -0.22, -1.0)
        b = createBone("RLegFrontCenterExt", VRLegFrontCenterTarsal, VRLegFrontCenterExt)
        b.parent = at.edit_bones['RLegFrontCenterTarsal']
        VRLegFrontCenterClaw = (-0.34, -0.22, -1.0)
        b = createBone("RLegFrontCenterClaw", VRLegFrontCenterExt, VRLegFrontCenterClaw)
        b.parent = at.edit_bones['RLegFrontCenterExt']
        # Left Claw Right Leg
        VRLegInsideTarsal = (-0.6, -0.08, -1.0)
        b = createBone("RLegInsideTarsal", VankleJointR, VRLegInsideTarsal)
        b.parent = at.edit_bones['ankleJointR']
        VRLegInsideClaw = (-0.6, 0, -1.0)
        b = createBone("RLegInsideClaw", VRLegInsideTarsal, VRLegInsideClaw)
        b.parent = at.edit_bones['RLegInsideTarsal']
        # Right Claw Right Leg
        VRLegOutsideTarsal = (-0.6, -0.32, -1.0)
        b = createBone("RLegOutsideTarsal", VankleJointR, VRLegOutsideTarsal)
        b.parent = at.edit_bones['ankleJointR']
        VRLegOutsideClaw = (-0.6, -0.4, -1.0)
        b = createBone("RLegOutsideClaw", VRLegOutsideTarsal, VRLegOutsideClaw)
        b.parent = at.edit_bones['RLegOutsideTarsal']
        # This MAY need to be done using function,
        # Need to test this.
        # rotate(name, rad, axis=0)
        rotate('RLegOutsideTarsal', 1, 2)
        rotate('RLegInsideTarsal', -1, 2)
        rotate('LLegOutsideTarsal', -1, 2)
        rotate('LLegInsideTarsal', 1, 2)
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # DONE DRAWING CHARACTER !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    def character_type(self):
        return 'bird'



bird = Bird
bird.buildSkeleton(char)

# rotate(name, rad, axis=0)
bpy.ops.object.mode_set(mode='OBJECT')
rotate('backCenter', -0.7854, 1)
rotate('LLegFrontCenterTarsal', -0.14, 0)
rotate('LLegInsideTarsal', -0.14, 0)
rotate('LLegOutsideTarsal', -0.14, 0)
rotate('RLegFrontCenterTarsal', -0.14, 0)
rotate('RLegInsideTarsal', -0.14, 0)
rotate('RLegOutsideTarsal', -0.14, 0)
bpy.ops.object.mode_set(mode='EDIT')


# Start dynamic (changeable) drivers
# For the following equations:
# Property (posePosition) effects only the pose  position.
# Property (rotPosition) effects only the z-axis location of the leg movement
# strZeroMovement zeros out the movement equation when frame = 0, so pose position can be set independently
# strZeroOutPose zeros out the  pose position when frame > 0
# eqL, eqR isolates the walk equation so that parenthesis problems are easier to deal with
# NOTE: It is very important to maintain the parenthesis balance on each isolated equation


def setWalkMovement(self, context):
    if(hasattr(bpy.types.WindowManager, "cycle")):
        cycleSpeed = bpy.context.window_manager.cycle + 8
    else:
        cycleSpeed = 8.0  # Default cycleSpeed
    bird.strSpeed = "sin(radians(" + str(cycleSpeed) + "*frame))"  # String form of cyclespeed equation
    bird.strHalfSpeed = "sin(radians(" + str(cycleSpeed / 2) + "*frame))"  # String form of halfcyclespeed equation
    #
    # Side to side sway
    eqBodySwayRL = "-(asin(" + bird.strSpeed + ")* " + str(bird.bodySwayRL) + "*.04)"
    setDriver(getEuler(bird.strName + '_bone'), eqBodySwayRL, 0) # left - right sway movement
    #
    # Forward - Backward sway
    eqBodySwayFB = "-(asin(" + bird.strSpeed + ")* " + str(bird.bodySwayFB) + "*.04)"
    dr_SwayFB = setDriver(getEuler(bird.strName + '_bone'), eqBodySwayFB, 2) # Forward - Backward rotational sway
    #
    # Bounce     strDoubleSpeed - For walk bounce
    eqBounce = "-(asin(" + bird.strSpeed + ")* " + str(bird.bounce) + "*.01)"
    dr_Bounce = setDriver(getEuler(bird.strName + '_bone'), eqBounce, 1, 'location') # Bounce
    #
    # KEY: RP = Rotate Position  RR = Rotate Range   PP = Pose Position
    # Hip
    RP = str(bird.hipWalkRP);
    RR = str(bird.hipWalkRR);
    PP = str(bird.hipPP)
    eqL = "(" + RP + "+.94-(asin(" + bird.strSpeed + "))* .3 * " + RR + ")"
    fnL = eqL + bird.strZeroMovement + "+(" + PP + bird.strZeroOutPose + ")"
    setDriver(getEuler('hipExtL'), fnL, 2)  # z-axis fwd-bkwd movement
    eqR = "(" + RP + "+.94+(asin(" + bird.strSpeed + "))* .3 * " + RR + ")"
    fnR = eqR + bird.strZeroMovement + "+(" + PP + bird.strZeroOutPose + ")"
    setDriver(getEuler('hipExtR'), fnR, 2)
    # Femur
    RP = str(bird.femurWalkRP);
    RR = str(bird.femurWalkRR);
    PP = str(bird.femurPP)
    eqL = "(" + RP + "-.26-asin(" + bird.strSpeed + ") * .3 * " + RR + ")"
    fnL = eqL + bird.strZeroMovement + "+(" + PP + bird.strZeroOutPose + ")"
    setDriver(getEuler('femurL'), fnL, 2)  # z-axis fwd-bkwd movement
    eqR = "(" + RP + "-.26+asin(" + bird.strSpeed + ") * .3 * " + RR + ")"
    fnR = eqR + bird.strZeroMovement + "+(" + PP + bird.strZeroOutPose + ")"
    setDriver(getEuler('femurR'), fnR, 2)
    # Tibia
    RP = str(bird.tibiaWalkRP);
    RR = str(bird.tibiaWalkRR);
    PP = str(bird.tibiaPP)
    eqL1 = RP + " + pow(atan(" + bird.strHalfSpeed + "),2)"
    eqL2 = "pow(-atan(" + bird.strHalfSpeed + "),2)/8*" + RR
    eqL3 = "(-1.2 + " + eqL1 + " * 2.2 - " + eqL2 + ")"
    fnL = eqL3 + bird.strZeroMovement + "+(" + PP + bird.strZeroOutPose + ")"
    setDriver(getEuler('tibiaL'), fnL, 2)
    eqR1 = RP + " - pow(atan(" + bird.strHalfSpeed + "),2)"
    eqR2 = "pow(-atan(" + bird.strHalfSpeed + "),2)/8*" + RR
    eqR3 = "(.04 + " + eqR1 + " * 2.2 - " + eqR2 + ")"
    fnR = eqR3 + bird.strZeroMovement + "+(" + PP + bird.strZeroOutPose + ")"
    setDriver(getEuler('tibiaR'), fnR, 2)
    # Ankle
    RP = str(bird.ankleWalkRP);
    RR = str(bird.tibiaWalkRR);
    PP = str(bird.anklePP)
    eqL1 = RP + " - pow(atan(" + bird.strHalfSpeed + "),2)"
    eqL2 = "pow(-atan(" + bird.strHalfSpeed + "),2)/8*" + RR  # Fwd lift higher than bkwd lift
    eqL3 = "(" + eqL1 + " * 2.2 + " + eqL2 + ")"
    fnL = eqL3 + bird.strZeroMovement + "+(" + PP + bird.strZeroOutPose + ")"
    setDriver(getEuler('ankleJointL'), fnL, 2)
    eqR1 = RP + " + -1.26 + pow(atan(" + bird.strHalfSpeed + "),2)"
    eqR2 = "pow(-atan(" + bird.strHalfSpeed + "),2)/8*" + RR
    eqR3 = "(" + eqR1 + " * 2.2 + " + eqR2 + ")"
    fnR = eqR3 + bird.strZeroMovement + "+(" + PP + bird.strZeroOutPose + ")"
    setDriver(getEuler('ankleJointR'), fnR, 2)
    # Foot Joint2 Toes Walk Movement
    RP = str(bird.toesWalkJoint2RP);
    RR = str(bird.toesWalkJoint2RR);
    PP = str(bird.toesJoint2PP)
    eqL = RP + "+.5-atan(" + bird.strSpeed + ") * .4 * " + RR
    fn = eqL + bird.strZeroMovement + "+(" + PP + bird.strZeroOutPose + ")"
    setDriver(getEuler('LLegFrontCenterExt'), fn)
    setDriver(getEuler('LLegOutsideClaw'), fn)
    setDriver(getEuler('LLegInsideClaw'), fn)
    eqR = RP + "+.5+atan(" + bird.strSpeed + ") * .4 * " + RR
    fn = eqR + bird.strZeroMovement + "+(" + PP + bird.strZeroOutPose + ")"
    setDriver(getEuler('RLegFrontCenterExt'), fn)
    setDriver(getEuler('RLegOutsideClaw'), fn)
    setDriver(getEuler('RLegInsideClaw'), fn)
    # END of setWalkMovement()

setWalkMovement(bird, context)
    

def set3rdJointToesMovement():  # Direct control, not related to walk
    RP = str(bird.toes3rdJointRP);
    PP = str(bird.toesJoint3PP)
    fn = RP + " + (" + PP + bird.strZeroOutPose + ")"
    setDriver(getEuler('LLegFrontCenterClaw'), fn)
    setDriver(getEuler('RLegFrontCenterClaw'), fn)


def setRearTarsalandClawMovement():  # Claw Grip
    RP = str(bird.rearTarsalandClawRP);
    PP = str(bird.rearTarsalandClawPP)
    fn = RP + " + (" + PP + bird.strZeroOutPose + ")"
    # 2nd Joint
    setDriver(getEuler('LLegRearCenterTarsal'), fn)
    setDriver(getEuler('RLegRearCenterTarsal'), fn)
    # Claw
    setDriver(getEuler('LLegRearCenterClaw'), fn)
    setDriver(getEuler('RLegRearCenterClaw'), fn)



# Tail
rotate('backL5', -0.3, 0)
rotate('backL6', 0.1, 0)

def setTail(bird, context):     
    if(hasattr(bpy.types.WindowManager, "tailUD")):
        tailUD = str(bpy.context.window_manager.tailUD)
    else:
        tailUD = "0.0"
    fn = tailUD + "* .1"  # Tail left - right
    setDriver(getEuler('tailL1'), fn, 0)  
    #
    if(hasattr(bpy.types.WindowManager, "tailLR")):
        tailLR = str(bpy.context.window_manager.tailLR)
    else:
        tailLR = "0.0"
    fn = tailLR + "* .1"  # Mid-wing fwd-bkwd position
    setDriver(getEuler('tailL1'), fn, 2)
    bpy.ops.object.mode_set(mode='OBJECT')


def setHipLegSpread(bird, context):
    if(hasattr(bpy.types.WindowManager, "hipExtSpread")):
        hipExtSpread = str(bpy.context.window_manager.hipExtSpread)  # Hip Leg Spread
    else:
        hipExtSpread = "0.0"
    fn = hipExtSpread + " * .1"
    setDriver(getEuler('hipExtL'), fn, 0)
    fn = str(hipExtSpread) + "* -.1"
    setDriver(getEuler('hipExtR'), fn, 0)


# Head
def setJaw(bird, context): # Jaw open - close    
    if(hasattr(bpy.types.WindowManager, "jawOC")):
        jawOC = str(bpy.context.window_manager.jawOC)
    else:
        jawOC = "0.0"
    fn = jawOC + " * .1"  # Jaw open - close
    setDriver(getEuler('jaw'), fn, 2)


# If centered at rear joint, parented,
# can be used  for eye movements
def setEye(bird, context):     
    # Left - Right turn motion 
    if(hasattr(bpy.types.WindowManager, "eyeLR")):
        eyeLR = str(bpy.context.window_manager.eyeLR)
        fn = str(eyeLR) + "* .1"  # eye left - right
        setDriver(getEuler('eyeL'), fn, 0)
        fn = str(eyeLR) + "* .1"  # eye left - right
        setDriver(getEuler('eyeR'), fn, 0)
    # Up - Down turn motion 
    eyeUD = str(bird.eyeUD)  # Eye left - right
    if(hasattr(bpy.types.WindowManager, "eyeUD")):
        eyeUD = str(bpy.context.window_manager.eyeUD)
        fn = str(eyeUD) + "* .1"  # eye left - right
        setDriver(getEuler('eyeL'), fn, 2)
        fn = str(eyeUD) + "* .1"  # eye left - right
        setDriver(getEuler('eyeR'), fn, 2)

# If the bird has a crest
def setCrest(bird, context):     
    # Crest Forward - Backward
    if(hasattr(bpy.types.WindowManager, "crestFB")):
        crestFB = str(bpy.context.window_manager.crestFB)
        fn = str(crestFB) + "* .1"  
        setDriver(getEuler('crest'), fn, 0)
    # Crest LEft - Right
    if(hasattr(bpy.types.WindowManager, "crestLR")):
        crestLR = str(bpy.context.window_manager.crestLR)
        fn = str(crestLR) + "* .1"  
        setDriver(getEuler('crest'), fn, 2)


# bird.wingFlapSpeed controls the speed of wing movement, strWingSpeed is the equation.
def setWing(self, context):  # Wings
    if(hasattr(bpy.types.WindowManager, "wingSpeed")):
        wingSpeed = bpy.context.window_manager.wingSpeed * 11
    else:
        wingSpeed = 11.0   # Default wind speed
    bird.strWingSpeed = "sin(radians(" + str(wingSpeed) + "*frame))"
    RP = str(bird.wingRP)  # Rotate position
    RR = str(bird.wingRR)  # Rotate Range
    if(hasattr(bpy.types.WindowManager, "wingRP")):
        RP = str(bpy.context.window_manager.wingRP)
    if(hasattr(bpy.types.WindowManager, "wingRR")):
        RR = str(bpy.context.window_manager.wingRR)
    PP = str(bird.wingPP)   # Pose position
    eqL = "(" + RP + "-(asin(" + bird.strWingSpeed + "))* .2 * " + RR + ")"
    fnL = eqL + bird.strZeroMovement + "+(" + PP + bird.strZeroOutPose + ")"
    setDriver(getEuler('wingL_J2'), fnL, 0)
    eqR = "(" + RP + "-(asin(" + bird.strWingSpeed + "))* .2 * " + RR + ")"
    fnR = eqR + bird.strZeroMovement + "+(" + PP + bird.strZeroOutPose + ")"
    setDriver(getEuler('wingR_J2'), fnR, 0)
    FB = str(bird.wingRP)  # Wing fwd-bkwd position
    if(hasattr(bpy.types.WindowManager, "wingFB")):
        FB = str(bpy.context.window_manager.wingFB)
    fn = ".2 - " + str(FB) + "* .1"  # Wing fwd-bkwd position
    setDriver(getEuler('wingL_J2'), fn, 2) 
    fn = "-.2 + " + str(FB) + "* .1"  # Wing fwd-bkwd position
    setDriver(getEuler('wingR_J2'), fn, 2)
    # Mid-wing fwd-bkwd position
    WMFB = str(bird.wingMidFB)
    if(hasattr(bpy.types.WindowManager, "wingMidFB")):
        WMFB = str(bpy.context.window_manager.wingMidFB)
    fn = ".2 - " + str(WMFB) + "* .1"  # Mid-wing fwd-bkwd position
    setDriver(getEuler('wingL_J5'), fn, 2)  
    fn = "-.2 + " + str(WMFB) + "* .1"  # Mid-wing fwd-bkwd position
    setDriver(getEuler('wingR_J5'), fn, 2)
    bpy.ops.object.mode_set(mode='OBJECT')
    
setWing(bird, context)

fn = ".2"  # wingL_J6-8 Wing tip control  
setDriver(getEuler('wingL_J6'), fn, 2)  # z-axis fwd-bkwd movement
fn = "-.2"
setDriver(getEuler('wingR_J6'), fn, 2)  # z-axis fwd-bkwd movement
fn = ".3"
setDriver(getEuler('wingL_J7'), fn, 2)  # z-axis fwd-bkwd movement
fn = "-.3"
setDriver(getEuler('wingR_J7'), fn, 2)  # z-axis fwd-bkwd movement
fn = ".3"
setDriver(getEuler('wingL_J8'), fn, 2)  # z-axis fwd-bkwd movement
fn = "-.3"
setDriver(getEuler('wingR_J8'), fn, 2)  # z-axis fwd-bkwd movement


# Speed Function controls the horizontal position of the bird based on the rotational orientation
def setHorizontalSpeed(self, context):
    if(hasattr(bpy.types.WindowManager, "speed")):
        speed = bpy.context.window_manager.speed
    else:
        speed = 0.0  # Default speed
    bird.strPosition = str(bpy.context.scene.frame_current / 2800 * speed)
    strRotateY = str(bpy.context.scene.objects.active.rotation_euler.y)
    fnx = bird.strPosition + "*frame* cos(" + strRotateY + ")"
    fny = bird.strPosition + "*frame*-sin(" + strRotateY + ")"
    setDriver(getEuler(bird.strName + '_bone'), fnx, 0, 'location')
    dr_loc = setDriver(getEuler(bird.strName + '_bone'), fny, 2, 'location')
    bpy.ops.object.mode_set(mode='OBJECT')

def setSwayRL(self, context):  # left - right sway movement
    if(hasattr(bpy.types.WindowManager, "sway")):
        sway = str(bpy.context.window_manager.sway)
    else:
        sway = "1.0"
    eqBodySwayRL = "-(asin(" + bird.strSpeed + ")* " + sway + "*.04)"
    setDriver(getEuler(bird.strName + '_bone'), eqBodySwayRL, 0)
    bpy.ops.object.mode_set(mode='OBJECT')

def setSwayFB(self, context):  # forward - backward sway movement
    if(hasattr(bpy.types.WindowManager, "swayFB")):
        sway = str(bpy.context.window_manager.swayFB)
    else:
        swayFB = "1.0"
    eqBodySwayFB = "-(asin(" + bird.strSpeed + ")* " + swayFB + "*.04)"
    dr_SwayFB = setDriver(getEuler(bird.strName + '_bone'), eqBodySwayFB, 2)
    bpy.ops.object.mode_set(mode='OBJECT')
    
def setBounce(self, context):  # Bounce
    if(hasattr(bpy.types.WindowManager, "bounce")):
        bounce = str(bpy.context.window_manager.bounce)
    else:
        bounce = "1.0"
    eqBounce = "-(asin(" + bird.strSpeed + ")* " + bounce + "*.01)"
    dr_Bounce = setDriver(getEuler(bird.strName + '_bone'), eqBounce, 1, 'location') # Bounce
    bpy.ops.object.mode_set(mode='OBJECT')

    
    
def setNeck(self, context):
    # Neck FB movement
    if(hasattr(bpy.types.WindowManager, "neckFB")):
        neckFB = str(bpy.context.window_manager.neckFB)
    else:
        neckFB = "6.0"
    fn = "-(asin(" + bird.strDoubleSpeed + ")* " + neckFB + "*.01)"  
    setDriver(getEuler('neck02'), fn)
    fn = ".3-(asin(" + bird.strDoubleSpeed + ")* " + neckFB + "*.01)"
    setDriver(getEuler('neck03'), fn)
    setDriver(getEuler('neck04'), fn)
    setDriver(getEuler('neck05'), fn)
    fn = "-(asin(" + bird.strDoubleSpeed + ")* " + neckFB + "*.01)"
    dr_neck06 = setDriver(getEuler('neck06'), fn)
    setDriver(getEuler('neck07'), fn)
    fn = "-0.1-(asin(" + bird.strDoubleSpeed + ")* " + neckFB + "*.01)"
    setDriver(getEuler('neck08'), fn)
    fn = "-(asin(" + bird.strDoubleSpeed + ")* -" + neckFB + "*.06)"
    setDriver(getEuler('headBase'), fn)
    bpy.ops.object.mode_set(mode='OBJECT')

setNeck(bird, context)
    
    
    
# deselect all objects.
bpy.ops.object.mode_set(mode='OBJECT')
for ob in bpy.context.selected_objects:
    ob.select = False

# Get the current vector coordinates of the bird
bird.x = bpy.context.scene.objects.active.location.x
bird.y = bpy.context.scene.objects.active.location.y
bird.z = bpy.context.scene.objects.active.location.z



bpy.types.WindowManager.speed = bpy.props.FloatProperty(update=setHorizontalSpeed, name="Speed", default=0.0)
bpy.types.WindowManager.cycle = bpy.props.FloatProperty(update=setWalkMovement, name="Cycle", default=1.0)
bpy.types.WindowManager.sway = bpy.props.FloatProperty(update=setSwayRL, name="Sway RL", default=1.0)
bpy.types.WindowManager.swayFB = bpy.props.FloatProperty(update=setSwayFB, name="Sway FB", default=0.0)
bpy.types.WindowManager.bounce = bpy.props.FloatProperty(update=setBounce, name="Bounce", default=1.0)
bpy.types.WindowManager.hipExtSpread = bpy.props.FloatProperty(update=setHipLegSpread, name="hipExtSpread", default=0.0)
bpy.types.WindowManager.wingSpeed = bpy.props.FloatProperty(update=setWing, name="Wing Speed", default=1.0)
bpy.types.WindowManager.wingRP = bpy.props.FloatProperty(update=setWing, name="Wing Position", default=0.0)
bpy.types.WindowManager.wingRR = bpy.props.FloatProperty(update=setWing, name="Wing Rot Range", default=3.0, min=0.0)
bpy.types.WindowManager.wingFB = bpy.props.FloatProperty(update=setWing, name="WingFB", default=0.0)
bpy.types.WindowManager.wingMidFB = bpy.props.FloatProperty(update=setWing, name="WingMidFB", default=0.0)
bpy.types.WindowManager.neckFB = bpy.props.FloatProperty(update=setNeck, name="neckFB", default=6.0)
bpy.types.WindowManager.tailUD = bpy.props.FloatProperty(update=setTail, name="tailUD", default=0.0)
bpy.types.WindowManager.tailLR = bpy.props.FloatProperty(update=setTail, name="tailLR", default=0.0)
bpy.types.WindowManager.jawOC = bpy.props.FloatProperty(update=setJaw, name="jawOC", default=0.0)
bpy.types.WindowManager.eyeLR = bpy.props.FloatProperty(update=setEye, name="eyeLR", default=0.0)
bpy.types.WindowManager.eyeUD = bpy.props.FloatProperty(update=setEye, name="eyeUD", default=0.0)



bpy.types.WindowManager.crestFB = bpy.props.FloatProperty(update=setCrest, name="crestFB", default=0.0)
bpy.types.WindowManager.crestLR = bpy.props.FloatProperty(update=setCrest, name="crestLR", default=0.0)



class OBPanel(bpy.types.Panel):
    bl_label = "Bird Control"
    bl_idname = "selected_object"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "UI"
    bl_context = "objectmode"
    def draw(self, context):
        layout = self.layout
        layout.row().prop(context.window_manager, 'speed')
        layout.row().prop(context.window_manager, 'cycle')
        layout.row().prop(context.window_manager, 'sway')
        layout.row().prop(context.window_manager, 'swayFB')
        layout.row().prop(context.window_manager, 'bounce')
        layout.row().prop(context.window_manager, 'hipExtSpread')
        layout.row().prop(context.window_manager, 'wingSpeed')
        layout.row().prop(context.window_manager, 'wingRP')
        layout.row().prop(context.window_manager, 'wingRR')
        layout.row().prop(context.window_manager, 'wingFB')
        layout.row().prop(context.window_manager, 'wingMidFB')
        layout.row().prop(context.window_manager, 'neckFB')
        layout.row().prop(context.window_manager, 'tailUD')
        layout.row().prop(context.window_manager, 'tailLR')
        layout.row().prop(context.window_manager, 'jawOC')
        layout.row().prop(context.window_manager, 'eyeLR')
        layout.row().prop(context.window_manager, 'eyeUD')
        layout.row().prop(context.window_manager, 'crestFB')
        layout.row().prop(context.window_manager, 'crestLR')
        
        

def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.mode_set(mode='OBJECT')

if __name__ == "__main__":
    register()
