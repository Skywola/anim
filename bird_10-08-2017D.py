# https://blender.stackexchange.com/questions/52503/is-it-possible-to-drive-other-properties-in-realtime-with-a-single-float-or-int
import bpy

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Start with a generalized header code section
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
import bpy, math
import bpy
from bpy.types import Panel, Menu
from rna_prop_ui import PropertyPanel

context = bpy.context
# Rotate the easy way, changes to pose mode and back
# name a string i.e., rotate('backCenter', .2, 1)
def rotate(name, rad, axis=0):
    currentMode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='POSE')
    bpy.context.object.data.bones[name].select = True
    Vector = (1, 0, 0)
    cAxis = (True, False, False)
    if(axis==1):
        Vector = (0, 1, 0)
        cAxis = (False, True, False)
    if(axis==2):
        Vector = (0, 0, 1)
        cAxis = (False, False, True)
    bpy.ops.transform.rotate(value=rad, axis=Vector, constraint_axis=cAxis, constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, release_confirm=True)
    bpy.context.object.data.bones[name].select = False

# Link objects to scene
def linkObjectsToScene(rig):
    scn = bpy.context.scene
    scn.objects.link(rig)
    scn.objects.active = rig
    scn.update()

# Make bone creation easy
def createBone(name="boneName", Vhead=(0, 0, 0), Vtail= (.1, 0, .1), roll= 0, con=False):
    bData = bpy.context.active_object.data
    bone = bData.edit_bones.new(name)
    bone.head[:] = Vhead
    bone.tail[:] = Vtail
    bone.roll = roll
    bone.use_connect = con
    return bone
    

    
# Initialization variables.  
reinforce = True     # Option - Add extra bones for stabilization
showNames = False    # Option - show bone names - for build only
show_x_ray = True    # Option
show_axes = False    # Option - Show armature axis - for build only
n = 0

# Do not remove spaces below, they correspond to command line entries
for ob in list(bpy.data.objects):
    if ob.name.startswith('rg') == True:
        n = n + 1   # increment rig number each time  one  is built.

# increment rig name each time  one  is built.
character = 'bird' # Option -  biped, quadruped, bird, spider, kangaroo
baseName="rg" + character + "0" + str(n+1)  # Assume n < 10 
if(n > 9):                    # Change baseName if assumption is wrong
    baseName="rg" + character + str(n+1)

  
# Do not remove spaces above, they correspond to command line entries
at = bpy.data.armatures.new(baseName + '_at') # at = Armature 
rig = bpy.data.objects.new(baseName, at)  # rig = Armature object
# rg00 (or the one in a series we are building) is now bpy.context.active_object
at.show_names = showNames
at.show_axes = show_axes

# Each new object created will be placed in a new location
height = 1.4  # Sets the height of the character handle
x =  .3 * n; y = 3.2 * n; z = height;
rig.location = (x, y, z)    # Set armature location
rig.show_x_ray = show_x_ray
linkObjectsToScene(rig)

bpy.ops.object.mode_set(mode='EDIT')
# The lines below create the handle for moving the character
bone = at.edit_bones.new(baseName + '_bone')
bone.head = [0.0, 0.0, 0.0]   # LOCAL COORDINATE, [0,0,0] places bone directly on armature.
bone.tail = [0, 0.0, 0.3]   # x - horizontal handle   z - vertical handle

baseName_bone = baseName + '_bone'
# THINGS ABOVE THAT MAY VARY BASED ON THE CHARACTER:
# 1. rig location x =  .3 * n; y = 3.2 * n; z = 0.1;
#   This can set the initial location of the character. 
#   This may also be set at the end of the code.
# 2. bone.tail sets the general orientation of the
#   handle created for moving the character - this
#   could vary, based  on the type of character.
# 3. Character name - biped, quadruped, bird, spider, kangaroo

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# End generalized header code section
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%




# The remaining code builds the character starting from the
# head of the handle, that is, at the origin.

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# INITIAL PROPERTIES 
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Declaration blank: 
# bpy.types.Object. = bpy.props.FloatProperty(name = "", min = -100.0, max = 100.0, default = 0.0)
# Options -  biped, quadruped, bird, spider, kangaroo
bpy.types.Object.p_character = bpy.props.StringProperty(name = "p_character", default = "bird")
# Option - Sets the height of the character handle or up and down motion
bpy.types.Object.p_height = bpy.props.FloatProperty(name = "p_height", min = -1000.0, max = 1000.0, default = 1.4)

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# END INITIAL PROPERTIES
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%



# Template
# Vpart = (x, y, z)  #  V for vector
# bone = createBone('name', Vhead, Vtail)
# parent to name of last bone created
# bpy.context.object.pose.bones["backCenter"].rotation_euler[0] = 0.785398

VbackCenterTip = (-0.12, 0, 0)
backCenter = createBone("backCenter", bone.head, VbackCenterTip)
backCenter.parent = at.edit_bones[baseName + '_bone']

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
VbackU1 = (0.15, 0, 0)
b = createBone("backU1", bone.head, VbackU1)
b.parent = at.edit_bones['backCenter']

VbackU2 = (0.25, 0, 0)
b = createBone("backU2", VbackU1, VbackU2)
b.parent = at.edit_bones['backU1']

VbackU3 = (0.35, 0, 0)
b = createBone("backU3", VbackU2, VbackU3)
b.parent = at.edit_bones['backU2']

VbackU4 = (0.45, 0, 0)
b = createBone("backU4", VbackU3, VbackU4)
b.parent = at.edit_bones['backU3']

VbackU5 = (0.55, 0, 0)
b = createBone("backU5", VbackU4, VbackU5)
b.parent = at.edit_bones['backU4']

VbackU6 = (0.64, 0, 0)
b = createBone("backU6", VbackU5, VbackU6)
b.parent = at.edit_bones['backU5']

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Start Bird Head
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
VjawBase = (0.55, 0, -0.11)
b = createBone("jawBase", VbackU5, VjawBase)
b.parent = at.edit_bones['backU5']

Vjaw = (0.55, 0, -0.2)
b = createBone("jaw", VjawBase, Vjaw)
b.parent = at.edit_bones['jawBase']

# Beak base
VoffJoint = (.576, 0, 0)
VbeakBase = (0.576, 0, -0.11)
b = createBone("beakBase", VoffJoint, VbeakBase)
b.parent = at.edit_bones['backU6']

Vbeak = (0.576, 0, -0.2)
b = createBone("beak", VbeakBase, Vbeak)
b.parent = at.edit_bones['beakBase']

# Head Top
Vheadtop = (0.7, 0, 0)
b = createBone("headtop", VbackU6, Vheadtop)
b.parent = at.edit_bones['backU6']

# Head L - R
VheadL = (0.64, 0.07, 0)
b = createBone("headL", VbackU6, VheadL)
b.parent = at.edit_bones['backU6']
VheadR = (0.64, -0.07, 0)
b = createBone("headR", VbackU6, VheadR)
b.parent = at.edit_bones['backU6']

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
b = createBone("wingL_J1", bone.head, VwingL_J1)
b.parent = at.edit_bones[baseName + '_bone']

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
b = createBone("wingR_J1", bone.head, VwingR_J1)
b.parent = at.edit_bones[baseName + '_bone']

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
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# DONE DRAWING CHARACTER !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!









# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# Animation Rotations
# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# getEuler output represents:
# bpy.data.objects['rg00bird'].pose.bones["backCenter"]
def getEuler(str_bone_name):
    bpy.ops.object.mode_set(mode='POSE')
    ob = bpy.context.object
    out = ob.pose.bones[str_bone_name]
    out.rotation_mode = 'XYZ'
    return out


# All walk cycle motions.
bpy.context.scene.frame_start = 0
# Speed of walk cycle
bpy.context.object["cycleSpeed"] = 8.0
# The line below yields: 'sin(radians(8.0*frame))'
strSpeed = "sin(radians("+str(bpy.context.object["cycleSpeed"])+"*frame))" 
# Cut cycle speed in half for lower leg motions
strHalfSpeed = "sin(radians(" + str(bpy.context.object["cycleSpeed"]/2) + "*frame))"
# Yields: 'sin(radians(4.0*frame))'

# Equation for bone joints, with euler transform, axis 0=x 1=y 2=z
# Note also that fn must be inserted as a STRING in the expression!
def equation(euler, fn="0", axis=0, movementType='rotation_euler'):
    edriver = euler.driver_add(movementType, axis)
    edriver.driver.type = 'SCRIPTED'
    edriver.driver.expression = fn
    return edriver

# Static setting, important for orientation so the below items are set correctly 
backCenterDriver = equation(getEuler('backCenter'), "-0.7854")
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# Drivers  equation(___euler, fn="0" axis=0)  # axis 0=x 1=y 2=z
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
hipLDriver = equation(getEuler('hipL'), "0")
hipRDriver = equation(getEuler('hipR'), "0")

# Pose at frame zero - Override function on frame zero, allowing for posing. 
strZeroMovement = " * (frame * (1/(frame+.0001)))" # Includes outside math operator *
strZeroOutPose = " * abs((frame/(frame + .0001))-1)"  # Override posePosition when frame NOT zero


# For the following equations:
# Property (posePosition) effects only the pose  position.
# Property (rotPosition) effects only the z-axis location of the leg movement
# strZeroMovement zeros out the movement equation when frame = 0, so pose position can be set independently
# strZeroOutPose zeros out the  pose position when frame > 0
# eqL, eqR isolates the walk equation so that parenthesis problems are easier to deal with
# NOTE: It is very important to maintain the parenthesis balance on each isolated equation
# Hip R and L movement
def setHipWalkMovement(posePosition=0.72, rotPosition = 0.1, rotRange = 1.0):
    eqL = "(" + str(rotPosition) + "+.94-(asin("+strSpeed+"))* .3 * "+ str(rotRange) + ")"
    fnL = eqL + strZeroMovement + "+(" + str(posePosition) + strZeroOutPose + ")"
    hipExtLDriver = equation(getEuler('hipExtL'), fnL, 2) # z-axis fwd-bkwd movement
    eqR = "(" + str(rotPosition) + "+.94+(asin("+strSpeed+"))* .3 * "+ str(rotRange) + ")"
    fnR = eqR + strZeroMovement + "+(" + str(posePosition) + strZeroOutPose + ")"
    hipExtRDriver = equation(getEuler('hipExtR'), fnR, 2)

setHipWalkMovement()

# Femur R and L movement
def setFemurWalkMovement(posePosition=0, rotPosition = 0, rotRange = 1.0):
    eqL = "(" + str(rotPosition) + "-.26-asin("+strSpeed+") * .3 * "+ str(rotRange) + ")"
    fnL = eqL + strZeroMovement + "+(" + str(posePosition) + strZeroOutPose + ")"
    femurLDriver = equation(getEuler('femurL'), fnL, 2) # z-axis fwd-bkwd movement
    eqR = "(" + str(rotPosition) + "-.26+asin("+strSpeed+") * .3 * "+ str(rotRange) + ")"
    fnR = eqR + strZeroMovement + "+(" + str(posePosition) + strZeroOutPose + ")"
    femurRDriver = equation(getEuler('femurR'), fnR, 2)


setFemurWalkMovement()

# Special function for tibia: foot is higher as it moves  forward, lower as it moves back
# USES strHalfSpeed IN FUNCTIONS INSTEAD OF strSpeed.
def setTibiaWalkMovement(posePosition=0, rotPosition = 0, rotRange = 1.0):
    eqL1 = str(rotPosition) + " + pow(atan("+strHalfSpeed+"),2)"
    eqL2 = "pow(-atan("+strHalfSpeed+"),2)/8*" + str(rotRange)
    eqL3 = "(-1.2 + " + eqL1 + " * 2.2 - " + eqL2 + ")" 
    fnL = eqL3 + strZeroMovement + "+(" + str(posePosition) + strZeroOutPose + ")"
    tibiaLDriver = equation(getEuler('tibiaL'), fnL, 2) # z-axis fwd-bkwd movement
    eqR1 = str(rotPosition) + " - pow(atan("+strHalfSpeed+"),2)" # For normal movement
    eqR2 = "pow(-atan("+strHalfSpeed+"),2)/8*" + str(rotRange)
    eqR3 = "(.04 + " + eqR1 + " * 2.2 - " + eqR2 + ")" 
    fnR = eqR3 + strZeroMovement + "+(" + str(posePosition) + strZeroOutPose + ")"
    tibiaRDriver = equation(getEuler('tibiaR'), fnR, 2)

setTibiaWalkMovement()


def setAnkleWalkMovement(posePosition=0, rotPosition = 1.4, rotRange = .9):
    eqL1 = str(rotPosition) + " - pow(atan("+strHalfSpeed+"),2)"
    eqL2 = "pow(-atan("+strHalfSpeed+"),2)/8*" + str(rotRange)  # Forward lift higher than backward lift
    eqL3 = "(" + eqL1 + " * 2.2 + " + eqL2 + ")"
    fnL = eqL3 + strZeroMovement + "+(" + str(posePosition) + strZeroOutPose + ")"
    ankleJointLDriver = equation(getEuler('ankleJointL'), fnL, 2)
    # Right
    eqR1 = str(rotPosition) + " + -1.26 + pow(atan("+strHalfSpeed+"),2)"
    eqR2 = "pow(-atan("+strHalfSpeed+"),2)/8*" + str(rotRange)
    eqR3 = "(" + eqR1 + " * 2.2 + " + eqR2 + ")"
    fnR = eqR3 + strZeroMovement + "+(" + str(posePosition) + strZeroOutPose + ")"
    ankleJointRDriver = equation(getEuler('ankleJointR'), fnR, 2)

setAnkleWalkMovement()

# These functions all share these parameters, with the defaults as listed:
# posePosition=0, rotPosition = 0, rotRange = 1.0
# As you can see, they are initially called with no parameters, that is, using
# the default settings.



# R and L Feet
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# All tarsals move together, these will be static, unmodifiable
# x-axis, Front center tarsal grab movement
def setTarsalWalkMovement(): # static, non-modifiable, other than right here
    fn = "-.14" 
    LLegFrontCenterTarsalDriver = equation(getEuler('LLegFrontCenterTarsal'), fn)
    LLegInsideTarsalDriver = equation(getEuler('LLegInsideTarsal'), fn)
    LLegOutsideTarsalDriver = equation(getEuler('LLegOutsideTarsal'), fn)
    RLegFrontCenterTarsalDriver = equation(getEuler('RLegFrontCenterTarsal'), fn)
    RLegInsideTarsalDriver = equation(getEuler('RLegInsideTarsal'), fn)
    RLegOutsideTarsalDriver = equation(getEuler('RLegOutsideTarsal'), fn)
   
setTarsalWalkMovement()



# All joint LLegFrontCenterExtDriver, LLegOutsideClawDriver, LLegInsideClawDriver, move together
# All joint RLegFrontCenterExtDriver, RLegOutsideClawDriver, RLegInsideClawDriver, move together
# Center has an extra joint called Ext.    x-axis, Front center ext grab movement
def set2ndJointToesWalkMovement(posePosition=-.3, rotPosition = -0.2, rotRange = 1.8):
    eqL = str(rotPosition) + "+.5-atan("+strSpeed+") * .4 * "+ str(rotRange)
    fn = eqL + strZeroMovement + "+(" + str(posePosition) + strZeroOutPose + ")"
    LLegFrontCenterExtDriver = equation(getEuler('LLegFrontCenterExt'), fn)
    LLegOutsideClawDriver = equation(getEuler('LLegOutsideClaw'), fn)
    LLegInsideClawDriver = equation(getEuler('LLegInsideClaw'), fn)
    eqR = str(rotPosition) + "+.5+atan("+strSpeed+") * .4 * "+ str(rotRange)
    fn = eqR + strZeroMovement + "+(" + str(posePosition) + strZeroOutPose + ")"
    RLegFrontCenterExtDriver = equation(getEuler('RLegFrontCenterExt'), fn)
    RLegOutsideClawDriver = equation(getEuler('RLegOutsideClaw'), fn)
    RLegInsideClawDriver = equation(getEuler('RLegInsideClaw'), fn)

set2ndJointToesWalkMovement()



# x-axis, Front center claw grab movement
def set3rdJointToesMovement(posePosition=0, rotPosition = 0):
    fn = str(rotPosition) + " + (" + str(posePosition) + strZeroOutPose + ")"
    LLegFrontCenterClawDriver = equation(getEuler('LLegFrontCenterClaw'), fn)
    RLegFrontCenterClawDriver = equation(getEuler('RLegFrontCenterClaw'), fn)

set3rdJointToesMovement()  

# Rear tarsal and claw, x-axis rear tarsal grab movement
def setRearTarsalandClawMovement(posePosition=0, rotPosition = 0):
    fn = str(rotPosition) + " + (" + str(posePosition) + strZeroOutPose + ")"
    # 2nd Joint
    LLegRearCenterTarsalDriver = equation(getEuler('LLegRearCenterTarsal'), fn)
    RLegRearCenterTarsalDriver = equation(getEuler('RLegRearCenterTarsal'), fn)
    # Claw
    LLegRearCenterClawDriver = equation(getEuler('LLegRearCenterClaw'), fn)
    RLegRearCenterClawDriver = equation(getEuler('RLegRearCenterClaw'), fn)

setRearTarsalandClawMovement()


fn = ".3"
backU3Driver = equation(getEuler('backU3'), fn)
backU4Driver = equation(getEuler('backU4'), fn)

fn = "0"
backU5Driver = equation(getEuler('backU5'), fn)
backU6Driver = equation(getEuler('backU6'), fn)

# Lower Back, same above fn = 0
backL1Driver = equation(getEuler('backL1'), fn)
backL2Driver = equation(getEuler('backL2'), fn)
backL3Driver = equation(getEuler('backL3'), fn)
backL4Driver = equation(getEuler('backL4'), fn)

# Tail
fn = "0.3"  # Up - down action
backL5Driver = equation(getEuler('backL5'), fn)
fn = "0"  # Left(+) to right(-) action
backL5Driver = equation(getEuler('backL5'), fn, 2)

fn = "0.1"  # Up - down action
backL6Driver = equation(getEuler('backL6'), fn)
fn = "0"  # Left(+) to right(-) action
backL6Driver = equation(getEuler('backL6'), fn, 2)

fn = "0"
tailL1Driver = equation(getEuler('tailL1'), fn)

fn = "0"
tailL2Driver = equation(getEuler('tailL2'), fn)


# Head
fn = ".4"
jawDriver = equation(getEuler('jaw'), fn, 2) # rotate z

fn = "0"  # Generally would not move
beakDriver = equation(getEuler('beak'), fn, 2) # rotate z

# If centered at rear joint, parented, 
# can be used  for eye movements
fn = "0" 
eyeLDriver = equation(getEuler('eyeL'), fn)
fn = "0"
eyeRDriver = equation(getEuler('eyeR'), fn)

# If the bird has a crest
fn = "0"
crestDriver = equation(getEuler('crest'), fn)


# Left and Right Wing
def setWingUpDownFlap(posePosition=0, rotPosition = 0.1, rotRange = 1.6):
    eqL = "(" + str(rotPosition) + "-(asin("+strSpeed+"))* .3 * "+ str(rotRange) + ")"
    fnL = eqL + strZeroMovement + "+(" + str(posePosition) + strZeroOutPose + ")"
    wingL_J2Driver = equation(getEuler('wingL_J2'), fnL, 0)
    eqR = "(" + str(rotPosition) + "-(asin("+strSpeed+"))* .3 * "+ str(rotRange) + ")"
    fnR = eqR + strZeroMovement + "+(" + str(posePosition) + strZeroOutPose + ")"
    wingR_J2Driver = equation(getEuler('wingR_J2'), fnR, 0)

setWingUpDownFlap()
 

fn = ".2"; fn = "-.2"
wingL_J6Driver = equation(getEuler('wingL_J6'), fn, 2) # z-axis fwd-bkwd movement
wingR_J6Driver = equation(getEuler('wingR_J6'), fn, 2) # z-axis fwd-bkwd movement

fn = ".3"; fn = "-.3"
wingL_J7Driver = equation(getEuler('wingL_J7'), fn, 2) # z-axis fwd-bkwd movement
wingR_J7Driver = equation(getEuler('wingR_J7'), fn, 2) # z-axis fwd-bkwd movement

fn = ".3"; fn = "-.3"
wingL_J8Driver = equation(getEuler('wingL_J8'), fn, 2) # z-axis fwd-bkwd movement
wingR_J8Driver = equation(getEuler('wingR_J8'), fn, 2) # z-axis fwd-bkwd movement

# deselect all objects, then select baseName_bone
bpy.ops.object.mode_set(mode='OBJECT')
for ob in bpy.context.selected_objects:
    ob.select = False


bpy.ops.object.mode_set(mode='POSE') # Blender seems to fail to catch this first line.
bpy.ops.object.mode_set(mode='POSE')
bpy.data.objects[baseName].data.bones[baseName + '_bone'].select = True

# Lights, Camera, Action!
# Get the current vector coordinates of the bird
bird_x = bpy.context.scene.objects.active.location.x
bird_y = bpy.context.scene.objects.active.location.y
bird_z = bpy.context.scene.objects.active.location.z

strRotateEuler_y = str(bpy.data.objects[baseName].pose.bones[baseName_bone].rotation_euler.y)

# ALL go_____ FUNCTIONS ARE UPDATE FUNCTIONS
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Speed Function controls the horizontal position of the bird based on the rotational orientation
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def goSpeed(self, context):
    strPosition = str(bpy.context.scene.frame_current/1200 * bpy.context.window_manager.speed)
    fnx = strPosition + "*frame* cos(" + strRotateEuler_y + ")"
    fny = strPosition + "*frame*-sin(" + strRotateEuler_y + ")"
    drx = equation(getEuler(baseName + '_bone'), fnx, 0, 'location')
    dry = equation(getEuler(baseName + '_bone'), fny, 2, 'location')

def goCycle(self, context):
    bpy.context.object["cycleSpeed"] = bpy.context.window_manager.cycle
    # The line below yields: 'sin(radians(8.0*frame))'
    strSpeed = "sin(radians("+str(bpy.context.object["cycleSpeed"])+"*frame))" 
    # Cut cycle speed in half for lower leg motions
    strHalfSpeed = "sin(radians(" + str(bpy.context.object["cycleSpeed"]/2) + "*frame))"
    posePosition=0.72; rotPosition = 0.1; rotRange = 1.0
    eqL = "(" + str(rotPosition) + "+.94-(asin("+strSpeed+"))* .3 * "+ str(rotRange) + ")"
    fnL = eqL + strZeroMovement + "+(" + str(posePosition) + strZeroOutPose + ")"
    hipExtLDriver = equation(getEuler('hipExtL'), fnL, 2) # z-axis fwd-bkwd movement
    eqR = "(" + str(rotPosition) + "+.94+(asin("+strSpeed+"))* .3 * "+ str(rotRange) + ")"
    fnR = eqR + strZeroMovement + "+(" + str(posePosition) + strZeroOutPose + ")"
    hipExtRDriver = equation(getEuler('hipExtR'), fnR, 2)
    #
    posePosition=0; rotPosition = 0
    eqL = "(" + str(rotPosition) + "-.26-asin("+strSpeed+") * .3 * "+ str(rotRange) + ")"
    fnL = eqL + strZeroMovement + "+(" + str(posePosition) + strZeroOutPose + ")"
    femurLDriver = equation(getEuler('femurL'), fnL, 2) # z-axis fwd-bkwd movement
    eqR = "(" + str(rotPosition) + "-.26+asin("+strSpeed+") * .3 * "+ str(rotRange) + ")"
    fnR = eqR + strZeroMovement + "+(" + str(posePosition) + strZeroOutPose + ")"
    femurRDriver = equation(getEuler('femurR'), fnR, 2)
    #
    eqL1 = str(rotPosition) + " + pow(atan("+strHalfSpeed+"),2)"
    eqL2 = "pow(-atan("+strHalfSpeed+"),2)/8*" + str(rotRange)
    eqL3 = "(-1.2 + " + eqL1 + " * 2.2 - " + eqL2 + ")" 
    fnL = eqL3 + strZeroMovement + "+(" + str(posePosition) + strZeroOutPose + ")"
    tibiaLDriver = equation(getEuler('tibiaL'), fnL, 2) # z-axis fwd-bkwd movement
    eqR1 = str(rotPosition) + " - pow(atan("+strHalfSpeed+"),2)" # For normal movement
    eqR2 = "pow(-atan("+strHalfSpeed+"),2)/8*" + str(rotRange)
    eqR3 = "(.04 + " + eqR1 + " * 2.2 - " + eqR2 + ")" 
    fnR = eqR3 + strZeroMovement + "+(" + str(posePosition) + strZeroOutPose + ")"
    tibiaRDriver = equation(getEuler('tibiaR'), fnR, 2)
    #
    posePosition=0, rotPosition = 1.4, rotRange = .9
    eqL1 = str(rotPosition) + " - pow(atan("+strHalfSpeed+"),2)"
    eqL2 = "pow(-atan("+strHalfSpeed+"),2)/8*" + str(rotRange)  # Forward lift higher than backward lift
    eqL3 = "(" + eqL1 + " * 2.2 + " + eqL2 + ")"
    fnL = eqL3 + strZeroMovement + "+(" + str(posePosition) + strZeroOutPose + ")"
    ankleJointLDriver = equation(getEuler('ankleJointL'), fnL, 2)
    eqR1 = str(rotPosition) + " + -1.26 + pow(atan("+strHalfSpeed+"),2)"
    eqR2 = "pow(-atan("+strHalfSpeed+"),2)/8*" + str(rotRange)
    eqR3 = "(" + eqR1 + " * 2.2 + " + eqR2 + ")"
    fnR = eqR3 + strZeroMovement + "+(" + str(posePosition) + strZeroOutPose + ")"
    ankleJointRDriver = equation(getEuler('ankleJointR'), fnR, 2)
    #
    posePosition=-.3, rotPosition = -0.2, rotRange = 1.8
    eqL = str(rotPosition) + "+.5-atan("+strSpeed+") * .4 * "+ str(rotRange)
    fn = eqL + strZeroMovement + "+(" + str(posePosition) + strZeroOutPose + ")"
    LLegFrontCenterExtDriver = equation(getEuler('LLegFrontCenterExt'), fn)
    LLegOutsideClawDriver = equation(getEuler('LLegOutsideClaw'), fn)
    LLegInsideClawDriver = equation(getEuler('LLegInsideClaw'), fn)
    eqR = str(rotPosition) + "+.5+atan("+strSpeed+") * .4 * "+ str(rotRange)
    fn = eqR + strZeroMovement + "+(" + str(posePosition) + strZeroOutPose + ")"
    RLegFrontCenterExtDriver = equation(getEuler('RLegFrontCenterExt'), fn)
    RLegOutsideClawDriver = equation(getEuler('RLegOutsideClaw'), fn)
    RLegInsideClawDriver = equation(getEuler('RLegInsideClaw'), fn)
    
    

bpy.types.WindowManager.speed = bpy.props.FloatProperty(update=goSpeed, name="Speed", default=0.0)
bpy.types.WindowManager.cycle = bpy.props.FloatProperty(update=goCycle, name="Cycle", default=1.0)

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


def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)


bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.mode_set(mode='OBJECT')
# bpy.context.object.data.bones[baseName_bone].select  = True
# bpy.ops.object.mode_set(mode='POSE')


if __name__ == "__main__":
    register()

