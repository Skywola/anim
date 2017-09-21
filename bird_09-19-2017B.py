# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Start with a generalized header code section
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
import bpy, math

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
    


reinforce = True     # Option - Add extra bones for stabilization
showNames = False    # Option - show bone names
show_x_ray = False    # Option
character = 'bird' # Option -  biped, quadruped, bird, spider, kangaroo
show_axes = False    # Option - Show armature axis
height = 1.3        # Option - Sets the height of the character handle
n = 0
# Do not remove spaces below, they correspond to command line entries
for ob in list(bpy.data.objects):
    if ob.name.startswith('rg') == True:
        n = n + 1   # increment rig number each time  one  is built.

# increment rig name each time  one  is built.
baseName="rg" + "0" + str(n)  # Assume n < 10 
if(n > 9):                    # Change baseName if assumption is wrong
    baseName="rg" + str(n)


# Do not remove spaces above, they correspond to command line entries
baseName = baseName + character

at = bpy.data.armatures.new(baseName + '_at') # at = Armature 
rig = bpy.data.objects.new(baseName, at)  # rig = Armature object

# Each new object created will be placed in a new location
x =  .3 * n; y = 3.2 * n; z = height;
rig.location = (x, y, z)    # Set armature location
rig.show_x_ray = show_x_ray
linkObjectsToScene(rig)

# rg00 (or the one in a series we are building) is now bpy.context.active_object
# bpy.context.active_object.data = at = 'rg00_at'
at.show_names = showNames
at.show_axes = show_axes

# BLENDER BUG
# THIS FIRST LINE DOES NOT GO INTO EDIT MODE FOR  SOME REASON.
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.object.mode_set(mode='EDIT')  # GOES INTO EDIT MODE
# The lines below create the handle for moving the character
bone = at.edit_bones.new(baseName + '_bone')
bone.head = [0.0, 0.0, 0.0]   # LOCAL COORDINATE, [0,0,0] places bone directly on armature.
bone.tail = [-0.3, 0.0, 0.3]   # x - horizontal handle   z - vertical handle

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
#
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
backL1 = createBone("backL1", VbackCenterTip, VbackL1)
backL1.parent = at.edit_bones['backCenter']

VbackL2 = (-0.36, 0, 0)
backL2 = createBone("backL2", VbackL1, VbackL2)
backL2.parent = at.edit_bones['backL1']

VbackL3 = (-0.48, 0, 0)
backL3 = createBone("backL3", VbackL2, VbackL3)
backL3.parent = at.edit_bones['backL2']

VbackL4 = (-0.6, 0, 0)
backL4 = createBone("backL4", VbackL3, VbackL4)
backL4.parent = at.edit_bones['backL3']

# straight, non-flexible part of rear back
VbackL5 = (-0.76, 0, 0)
backL5 = createBone("backL5", VbackL4, VbackL5)
backL5.parent = at.edit_bones['backL4']

# straight, non-flexible part of rear back
VbackL6 = (-0.92, 0, 0)
backL6 = createBone("backL6", VbackL5, VbackL6)
backL6.parent = at.edit_bones['backL5']

# Tail Base
VtailL1 = (-1.04, 0, 0)
tailL1 = createBone("tailL1", VbackL6, VtailL1)
tailL1.parent = at.edit_bones['backL6']

VtailL2 = (-1.16, 0, 0)
tailL2 = createBone("tailL2", VtailL1, VtailL2)
tailL2.parent = at.edit_bones['tailL1']

# End Bottom part of spine

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Start Top part of spine
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
VbackU1 = (0.15, 0, 0)
backU1 = createBone("backU1", bone.head, VbackU1)
backU1.parent = at.edit_bones['backCenter']

VbackU2 = (0.25, 0, 0)
backU2 = createBone("backU2", VbackU1, VbackU2)
backU2.parent = at.edit_bones['backU1']

VbackU3 = (0.35, 0, 0)
backU3 = createBone("backU3", VbackU2, VbackU3)
backU3.parent = at.edit_bones['backU2']

VbackU4 = (0.45, 0, 0)
backU4 = createBone("backU4", VbackU3, VbackU4)
backU4.parent = at.edit_bones['backU3']

VbackU5 = (0.55, 0, 0)
backU5 = createBone("backU5", VbackU4, VbackU5)
backU5.parent = at.edit_bones['backU4']

VbackU6 = (0.64, 0, 0)
backU6 = createBone("backU6", VbackU5, VbackU6)
backU6.parent = at.edit_bones['backU5']

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Start Bird Head
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
VjawBase = (0.55, 0, -0.11)
jawBase = createBone("jawBase", VbackU5, VjawBase)
jawBase.parent = at.edit_bones['backU5']

Vjaw = (0.55, 0, -0.2)
jaw = createBone("jaw", VjawBase, Vjaw)
jaw.parent = at.edit_bones['jawBase']

# Beak base
VoffJoint = (.576, 0, 0)
VbeakBase = (0.576, 0, -0.11)
beakBase = createBone("beakBase", VoffJoint, VbeakBase)
beakBase.parent = at.edit_bones['backU6']

Vbeak = (0.576, 0, -0.2)
beak = createBone("beak", VbeakBase, Vbeak)
beak.parent = at.edit_bones['beakBase']

# Head Top
Vheadtop = (0.7, 0, 0)
headtop = createBone("headtop", VbackU6, Vheadtop)
headtop.parent = at.edit_bones['backU6']

# Head L - R
VheadL = (0.64, 0.07, 0)
headL = createBone("headL", VbackU6, VheadL)
headL.parent = at.edit_bones['backU6']
VheadR = (0.64, -0.07, 0)
headR = createBone("headR", VbackU6, VheadR)
headR.parent = at.edit_bones['backU6']

VeyeBaseL = (0.64, 0.07, -0.1)
eyeBaseL = createBone("eyeBaseL", VheadL, VeyeBaseL)
eyeBaseL.parent = at.edit_bones['headL']
VeyeBaseR = (0.64, -0.07, -0.1)
eyeBaseR = createBone("eyeBaseR", VheadR, VeyeBaseR)
eyeBaseR.parent = at.edit_bones['headR']


# Eye Left and Right
VeyeL = (0.64, 0.07, -0.13)
eyeL = createBone("eyeL", VeyeBaseL, VeyeL)
eyeL.parent = at.edit_bones['eyeBaseL']

VeyeR = (0.64, -0.07, -0.13)
eyeR = createBone("eyeR", VeyeBaseR, VeyeR)
eyeR.parent = at.edit_bones['eyeBaseR']

# Crest
Vcrest = (0.84, 0, 0)
crest = createBone("crest", Vheadtop, Vcrest)
crest.parent = at.edit_bones['headtop']






# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Start wings
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
VwingL_J1 = (0, 0.3, 0)
wingL_J1 = createBone("wingL_J1", bone.head, VwingL_J1)
wingL_J1.parent = at.edit_bones[baseName + '_bone']

VwingL_J2 = (0, 0.6, 0)
wingL_J2 = createBone("wingL_J2", VwingL_J1, VwingL_J2)
wingL_J2.parent = at.edit_bones['wingL_J1']

VwingL_J3 = (0, 0.9, 0)
wingL_J3 = createBone("wingL_J3", VwingL_J2, VwingL_J3)
wingL_J3.parent = at.edit_bones['wingL_J2']

VwingL_J4 = (0, 1.2, 0)
wingL_J4 = createBone("wingL_J4", VwingL_J3, VwingL_J4)
wingL_J4.parent = at.edit_bones['wingL_J3']

VwingL_J5 = (0, 1.5, 0)
wingL_J5 = createBone("wingL_J5", VwingL_J4, VwingL_J5)
wingL_J5.parent = at.edit_bones['wingL_J4']

VwingL_J6 = (0, 1.7, 0)
wingL_J6 = createBone("wingL_J6", VwingL_J5, VwingL_J6)
wingL_J6.parent = at.edit_bones['wingL_J5']

VwingL_J7 = (0, 1.9, 0)
wingL_J7 = createBone("wingL_J7", VwingL_J6, VwingL_J7)
wingL_J7.parent = at.edit_bones['wingL_J6']

VwingL_J8 = (0, 2.0, 0)
wingL_J8 = createBone("wingL_J8", VwingL_J7, VwingL_J8)
wingL_J8.parent = at.edit_bones['wingL_J7']


VwingR_J1 = (0, -0.3, 0)
wingR_J1 = createBone("wingR_J1", bone.head, VwingR_J1)
wingR_J1.parent = at.edit_bones[baseName + '_bone']

VwingR_J2 = (0, -0.6, 0)
wingR_J2 = createBone("wingR_J2", VwingR_J1, VwingR_J2)
wingR_J2.parent = at.edit_bones['wingR_J1']

VwingR_J3 = (0, -0.9, 0)
wingR_J3 = createBone("wingR_J3", VwingR_J2, VwingR_J3)
wingR_J3.parent = at.edit_bones['wingR_J2']

VwingR_J4 = (0, -1.2, 0)
wingR_J4 = createBone("wingR_J4", VwingR_J3, VwingR_J4)
wingR_J4.parent = at.edit_bones['wingR_J3']

VwingR_J5 = (-0, -1.5, 0)
wingR_J5 = createBone("wingR_J5", VwingR_J4, VwingR_J5)
wingR_J5.parent = at.edit_bones['wingR_J4']

VwingR_J6 = (0, -1.7, 0)
wingR_J6 = createBone("wingR_J6", VwingR_J5, VwingR_J6)
wingR_J6.parent = at.edit_bones['wingR_J5']

VwingR_J7 = (0, -1.9, 0)
wingR_J7 = createBone("wingR_J7", VwingR_J6, VwingR_J7)
wingR_J7.parent = at.edit_bones['wingR_J6']

VwingR_J8 = (0, -2.0, 0)
wingR_J8 = createBone("wingR_J8", VwingR_J7, VwingR_J8)
wingR_J8.parent = at.edit_bones['wingR_J7']


VhipBase = (-0.6, 0, -0.12)
hipBase = createBone("hipBase", VbackL4, VhipBase)
hipBase.parent = at.edit_bones['backL4']

VhipL = (-0.6, 0.22, -0.12)
hipL = createBone("hipL", VhipBase, VhipL)
hipL.parent = at.edit_bones['hipBase']

VhipR = (-0.6, -0.22, -.12)
hipR = createBone("hipR", VhipBase, VhipR)
hipR.parent = at.edit_bones['hipBase']

# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# Legs
# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
VhipExtL = (-0.6, 0.22, -0.4)
hipExtL = createBone("hipExtL", VhipL, VhipExtL)
hipExtL.parent = at.edit_bones['hipL']
VhipExtR = (-0.6, -0.22, -0.4)
hipExtR = createBone("hipExtR", VhipR, VhipExtR)
hipExtR.parent = at.edit_bones['hipR']

VfemurL = (-0.6, 0.2, -0.7)
femurL = createBone("femurL", VhipExtL, VfemurL)
femurL.parent = at.edit_bones['hipExtL']
VfemurR = (-0.6, -0.2, -0.7)
femurR = createBone("femurR", VhipExtR, VfemurR)
femurR.parent = at.edit_bones['hipExtR']

VtibiaL = (-0.6, 0.2, -.96)
tibiaL = createBone("tibiaL", VfemurL, VtibiaL)
tibiaL.parent = at.edit_bones['femurL']
VtibiaR = (-0.6, -0.2, -.96)
tibiaR = createBone("tibiaR", VfemurR, VtibiaR)
tibiaR.parent = at.edit_bones['femurR']

VankleJointL = (-0.6, 0.2, -1)
ankleJointL = createBone("ankleJointL", VtibiaL, VankleJointL)
ankleJointL.parent = at.edit_bones['tibiaL']
VankleJointR = (-0.6, -0.2, -1)
ankleJointR = createBone("ankleJointR", VtibiaR, VankleJointR)
ankleJointR.parent = at.edit_bones['tibiaR']

# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# Left Foot
# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# Rear Claw
# Rear Claw
VLLegRearCenterTarsal = (-0.7, 0.2, -1.0)
LLegRearCenterTarsal = createBone("LLegRearCenterTarsal", VankleJointL, VLLegRearCenterTarsal)
LLegRearCenterTarsal.parent = at.edit_bones['ankleJointL']

VLLegRearCenterClaw = (-0.8, 0.2, -1.0)
LLegRearCenterClaw = createBone("LLegRearCenterClaw", VLLegRearCenterTarsal, VLLegRearCenterClaw)
LLegRearCenterClaw.parent = at.edit_bones['LLegRearCenterTarsal']

# Center Claw
VLLegFrontCenterTarsal = (-0.5, 0.2, -1.0)
LLegFrontCenterTarsal = createBone("LLegFrontCenterTarsal", VankleJointL, VLLegFrontCenterTarsal)
LLegFrontCenterTarsal.parent = at.edit_bones['ankleJointL']

VLLegFrontCenterExt = (-0.4, 0.2, -1.0)
LLegFrontCenterExt = createBone("LLegFrontCenterExt", VLLegFrontCenterTarsal, VLLegFrontCenterExt)
LLegFrontCenterExt.parent = at.edit_bones['LLegFrontCenterTarsal']

VLLegFrontCenterClaw = (-0.34, 0.2, -1.0)
LLegFrontCenterClaw = createBone("LLegFrontCenterClaw", VLLegFrontCenterExt, VLLegFrontCenterClaw)
LLegFrontCenterClaw.parent = at.edit_bones['LLegFrontCenterExt']

# Left Claw Left Leg
VLLegInsideTarsal = (-0.6, 0.08, -1.0)
LLegInsideTarsal = createBone("LLegInsideTarsal", VankleJointL, VLLegInsideTarsal)
LLegInsideTarsal.parent = at.edit_bones['ankleJointL']

VLLegInsideClaw = (-0.6, 0, -1.0)
LLegInsideClaw = createBone("LLegInsideClaw", VLLegInsideTarsal, VLLegInsideClaw)
LLegInsideClaw.parent = at.edit_bones['LLegInsideTarsal']

# Right Claw Left Leg
VLLegOutsideTarsal = (-0.6, 0.32, -1.0)
LLegOutsideTarsal = createBone("LLegOutsideTarsal", VankleJointL, VLLegOutsideTarsal)
LLegOutsideTarsal.parent = at.edit_bones['ankleJointL']

VLLegOutsideClaw = (-0.6, 0.4, -1.0)
LLegOutsideClaw = createBone("LLegOutsideClaw", VLLegOutsideTarsal, VLLegOutsideClaw)
LLegOutsideClaw.parent = at.edit_bones['LLegOutsideTarsal']



# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# Right Foot
# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# Rear Claw
VRLegRearCenterTarsal = (-0.7, -0.2, -1.0)
RLegRearCenterTarsal = createBone("RLegRearCenterTarsal", VankleJointR, VRLegRearCenterTarsal)
RLegRearCenterTarsal.parent = at.edit_bones['ankleJointR']

VRLegRearCenterClaw = (-0.8, -0.2, -1.0)
RLegRearCenterClaw = createBone("RLegRearCenterClaw", VRLegRearCenterTarsal, VRLegRearCenterClaw)
RLegRearCenterClaw.parent = at.edit_bones['RLegRearCenterTarsal']

# Center Claw
VRLegFrontCenterTarsal = (-0.5, -0.2, -1.0)
RLegFrontCenterTarsal = createBone("RLegFrontCenterTarsal", VankleJointR, VRLegFrontCenterTarsal)
RLegFrontCenterTarsal.parent = at.edit_bones['ankleJointR']

VRLegFrontCenterExt = (-0.4, -0.2, -1.0)
RLegFrontCenterExt = createBone("RLegFrontCenterExt", VRLegFrontCenterTarsal, VRLegFrontCenterExt)
RLegFrontCenterExt.parent = at.edit_bones['RLegFrontCenterTarsal']

VRLegFrontCenterClaw = (-0.34, -0.2, -1.0)
RLegFrontCenterClaw = createBone("RLegFrontCenterClaw", VRLegFrontCenterExt, VRLegFrontCenterClaw)
RLegFrontCenterClaw.parent = at.edit_bones['RLegFrontCenterExt']

# Left Claw Right Leg
VRLegInsideTarsal = (-0.6, -0.08, -1.0)
RLegInsideTarsal = createBone("RLegInsideTarsal", VankleJointR, VRLegInsideTarsal)
RLegInsideTarsal.parent = at.edit_bones['ankleJointR']

VRLegInsideClaw = (-0.6, 0, -1.0)
RLegInsideClaw = createBone("RLegInsideClaw", VRLegInsideTarsal, VRLegInsideClaw)
RLegInsideClaw.parent = at.edit_bones['RLegInsideTarsal']

# Right Claw Right Leg
VRLegOutsideTarsal = (-0.6, -0.32, -1.0)
RLegOutsideTarsal = createBone("RLegOutsideTarsal", VankleJointR, VRLegOutsideTarsal)
RLegOutsideTarsal.parent = at.edit_bones['ankleJointR']

VRLegOutsideClaw = (-0.6, -0.4, -1.0)
RLegOutsideClaw = createBone("RLegOutsideClaw", VRLegOutsideTarsal, VRLegOutsideClaw)
RLegOutsideClaw.parent = at.edit_bones['RLegOutsideTarsal']




# This MAY need to be done using function, 
# Need to test this.
# rotate(name, rad, axis=0)
rotate('RLegOutsideTarsal', 1, 2)
rotate('RLegInsideTarsal', -1, 2)
rotate('LLegOutsideTarsal', -1, 2)
rotate('LLegInsideTarsal', 1, 2)




# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# Rotations
# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# getEuler output represents:
# bpy.data.objects['rg00spider'].pose.bones["backCenter"]
def getEuler(str_bone_name):
    bpy.ops.object.mode_set(mode='POSE')
    ob = bpy.context.object
    out = ob.pose.bones[str_bone_name]
    out.rotation_mode = 'XYZ'
    return out


backCenter_euler = getEuler('backCenter')
backL1_euler = getEuler('backL1')
backL2_euler = getEuler('backL2')
backL3_euler = getEuler('backL3')
backL4_euler = getEuler('backL4')
backL5_euler = getEuler('backL5')
backL6_euler = getEuler('backL6')
tailL1_euler = getEuler('tailL1')
tailL2_euler = getEuler('tailL2')
VbackU1_euler = getEuler('backU1')
backU2_euler = getEuler('backU2')
backU3_euler = getEuler('backU3')
backU4_euler = getEuler('backU4')
backU5_euler = getEuler('backU5')
backU6_euler = getEuler('backU6')

jaw_euler = getEuler('jaw')
beak_euler = getEuler('beak')
eyeL_euler = getEuler('eyeL')
eyeR_euler = getEuler('eyeR')
crest_euler = getEuler('crest')
crest_euler = getEuler('crest')
wingL_J1_euler = getEuler('wingL_J1')

wingL_J2_euler = getEuler('wingL_J2')
wingL_J3_euler = getEuler('wingL_J3')
wingL_J4_euler = getEuler('wingL_J4')

wingL_J5_euler = getEuler('wingL_J5')
wingL_J6_euler = getEuler('wingL_J6')
wingL_J7_euler = getEuler('wingL_J7')
wingL_J8_euler = getEuler('wingL_J8')
wingR_J1_euler = getEuler('wingR_J1')

wingR_J2_euler = getEuler('wingR_J2')
wingR_J3_euler = getEuler('wingR_J3')
wingR_J4_euler = getEuler('wingR_J4')

wingR_J5_euler = getEuler('wingR_J5')
wingR_J6_euler = getEuler('wingR_J6')
wingR_J7_euler = getEuler('wingR_J7')
wingR_J8_euler = getEuler('wingR_J8')

hipL_euler = getEuler('hipL')
hipExtL_euler = getEuler('hipExtL')
femurL_euler = getEuler('femurL')
tibiaL_euler = getEuler('tibiaL')
ankleJointL_euler = getEuler('ankleJointL')

LLegRearCenterTarsal_euler = getEuler('LLegRearCenterTarsal')
LLegRearCenterClaw_euler = getEuler('LLegRearCenterClaw')
LLegFrontCenterTarsal_euler = getEuler('LLegFrontCenterTarsal')
LLegFrontCenterExt_euler = getEuler('LLegFrontCenterExt')
LLegFrontCenterClaw_euler = getEuler('LLegFrontCenterClaw')
LLegInsideTarsal_euler = getEuler('LLegInsideTarsal')
LLegInsideClaw_euler = getEuler('LLegInsideClaw')
LLegOutsideTarsal_euler = getEuler('LLegOutsideTarsal')
LLegOutsideClaw_euler = getEuler('LLegOutsideClaw')

hipR_euler = getEuler('hipR')
hipExtR_euler = getEuler('hipExtR')
femurR_euler = getEuler('femurR')
tibiaR_euler = getEuler('tibiaR')
ankleJointR_euler = getEuler('ankleJointR')


RLegRearCenterTarsal_euler = getEuler('RLegRearCenterTarsal')
RLegRearCenterClaw_euler = getEuler('RLegRearCenterClaw')
RLegFrontCenterTarsal_euler = getEuler('RLegFrontCenterTarsal')
RLegFrontCenterExt_euler = getEuler('RLegFrontCenterExt')
RLegFrontCenterClaw_euler = getEuler('RLegFrontCenterClaw')
RLegInsideTarsal_euler = getEuler('RLegInsideTarsal')
RLegInsideClaw_euler = getEuler('RLegInsideClaw')
RLegOutsideTarsal_euler = getEuler('RLegOutsideTarsal')
RLegOutsideClaw_euler = getEuler('RLegOutsideClaw')

#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# Drivers  equation(euler, fn="0" axis=0)  # axis 0=x 1=y 2=z
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Equation for bone joints, with euler transform
def equation(euler, fn="0", axis=0):
    edriver = euler.driver_add('rotation_euler', axis)
    edriver.driver.type = 'SCRIPTED'
    edriver.driver.expression = fn
    return edriver


# Note fn and axis are optional  fn="0" and axis=0 by default. Axis 0=x 1=y 2=z
# effect position at frame  zero:    * (frame*(1/(frame+.0001)))


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Create Property to control speed of walk (cycle) motion
#bpy.types.Object.speed = bpy.props.StringProperty(name = "speed", default = "7")
#bpy.data.objects[baseName].speed = "7"
strIntialSpeed = rig.data['speed'] = "7"
strModSpeed = str(float(strIntialSpeed)/2)
strHalfSpeed = "radians("+strModSpeed+"*frame)"

# Expanded to include radians and * frame to shorten each expression
strSpeed = "radians("+strIntialSpeed+"*frame)" # Inserted as a string in the expression
# Should  be inserted within the sin function like so: sin("+speed+")
# Example:  hipfnL = "-((asin(sin("+strSpeed+"))* .34) +.1)*(frame*(1/(frame+.0001)))+ .3"

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Pose at frame zero
# Makes function work at all times except on frame zero, allowing for posing the character at frame zero
strPose = "frame*(1/(frame+.0001))"
# Example: fn ="((asin(sin("+strSpeed+"))*.4) +.1)*("+strPose+")+ .3"; 

# Hip 
hipLDriver = equation(hipL_euler, "0")
hipRDriver = equation(hipR_euler, "0")

# The last item is the pose position " *(frame*(1/(frame+.0001)))+ .3'"  AKA "+strPose+"
hipfnL = ".3"
hipfnL = "1.2-(asin(sin("+strSpeed+")))*"+range1
hipExtLDriver = equation(hipExtL_euler, hipfnL, 2)
range1 = ".4"
hipfnR = "1.2+(asin(sin("+strSpeed+")))*"+range1
hipExtRDriver = equation(hipExtR_euler, hipfnR, 2)

# Two axis control %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
fn = "1.2"  # z-axis fwd-bkwd movement
femfnL = "1.2"
femfnL = "-.2-asin(sin("+strSpeed+"))*"+range2
femurLDriver = equation(femurL_euler, femfnL, 2) # z-axis fwd-bkwd movement
range2 = ".2"
femfnR = "-.2+asin(sin("+strSpeed+"))*"+range2
femurRDriver = equation(femurR_euler, femfnR, 2)

# x-axis side to side movement - future property
#femurLDriver = equation(femurL_euler, "-.22")    # x-axis side to side movement
#femurRDriver = equation(femurR_euler, "-.22")    # x-axis side to side movement
# Two axis control %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# Special function for tibia: foot is higher as it moves  forward, lower as it moves back
# USES strHalfSpeed IN FUNCTIONS INSTEAD OF strSpeed
range3 = ".2"
tibfnL = "-1.2+pow(atan(sin("+strHalfSpeed+")),2)*2.2 - pow(-atan(sin("+strHalfSpeed+")),2)/8*"+range3
tibiaLDriver = equation(tibiaL_euler, tibfnL, 2) # z-axis fwd-bkwd movement
range3 = ".2"
fn = "+.2-pow(atan(sin("+strHalfSpeed+")),2)*2.2 + pow(-atan(sin("+strHalfSpeed+")),2)/8*"+range3
tibiaRDriver = equation(tibiaR_euler, fn, 2)

range4 = ".2"
fn = ".54-pow(atan(sin("+strHalfSpeed+")),2)*2.2 + pow(-atan(sin("+strHalfSpeed+")),2)/8*"+range4
ankleJointLDriver = equation(ankleJointL_euler, fn, 2)

range4 = ".2"
fn = "-.9+pow(atan(sin("+strHalfSpeed+")),2)*2.2 + pow(-atan(sin("+strHalfSpeed+")),2)/8*"+range4
ankleJointRDriver = equation(ankleJointR_euler, fn, 2)




# R and L Feet
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# All tarsals move together
# x-axis, Front center tarsal grab movement
fn = "-.8" 
LLegFrontCenterTarsalDriver = equation(LLegFrontCenterTarsal_euler, fn)
LLegInsideTarsalDriver = equation(LLegInsideTarsal_euler, fn)
LLegOutsideTarsalDriver = equation(LLegOutsideTarsal_euler, fn)

fn = "-.8" 
RLegFrontCenterTarsalDriver = equation(RLegFrontCenterTarsal_euler, fn)
RLegInsideTarsalDriver = equation(RLegInsideTarsal_euler, fn)
RLegOutsideTarsalDriver = equation(RLegOutsideTarsal_euler, fn)
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# All joint LLegFrontCenterExtDriver, LLegOutsideClawDriver, LLegInsideClawDriver, move together
# Center has an extra joint called Ext
# x-axis, Front center ext grab movement
fn = "2.84+atan(((-asin(sin("+strSpeed+")* .6)+ 1.6)* .3)+ -.46) *("+strPose+") - 2.6"
LLegFrontCenterExtDriver = equation(LLegFrontCenterExt_euler, fn)
LLegOutsideClawDriver = equation(LLegOutsideClaw_euler, fn)
LLegInsideClawDriver = equation(LLegInsideClaw_euler, fn)

# All joint RLegFrontCenterExtDriver, RLegOutsideClawDriver, RLegInsideClawDriver, move together
# Center has an extra joint called Ext
fn = "2.84+atan(((-asin(sin("+strSpeed+")* .6)+ 1.6)* .3)+ -.46) *("+strPose+") - 2.6"
RLegFrontCenterExtDriver = equation(RLegFrontCenterExt_euler, fn)
RLegOutsideClawDriver = equation(RLegOutsideClaw_euler, fn)
RLegInsideClawDriver = equation(RLegInsideClaw_euler, fn)
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%



# x-axis, Front center claw grab movement
fn = "3.2-atan(((-asin(sin("+strSpeed+"))+ 1.6)* .3)+ -.3) *("+strPose+") - 2.8"
LLegFrontCenterClawDriver = equation(LLegFrontCenterClaw_euler, fn)
fn = "3.2-atan(((-asin(sin("+strSpeed+"))+ 1.6)* .3)+ -.3) *("+strPose+") - 2.8"
RLegFrontCenterClawDriver = equation(RLegFrontCenterClaw_euler, fn)


# Rear tarsal and claw
fn = "2.08" # x-axis rear tarsal grab movement
fn = ".72"
LLegRearCenterTarsalDriver = equation(LLegRearCenterTarsal_euler, fn)
fn = ".72"
RLegRearCenterTarsalDriver = equation(RLegRearCenterTarsal_euler, fn)

fn = "0" # x-axis, Rear claw grab movement
LLegRearCenterClawDriver = equation(LLegRearCenterClaw_euler, fn)
fn = "0"
RLegRearCenterClawDriver = equation(RLegRearCenterClaw_euler, fn)




# Upper Back
fn = "-0.7854"
backCenterDriver = equation(backCenter_euler, fn)

fn = ".3"
backU3Driver = equation(backU3_euler, fn)

fn = ".3"
backU4Driver = equation(backU4_euler, fn)

fn = "0"
backU5Driver = equation(backU5_euler, fn)

fn = "0"
backU6Driver = equation(backU6_euler, fn)

# Lower Back
fn = "0"
backL1Driver = equation(backL1_euler, fn)

fn = "0"
backL2Driver = equation(backL2_euler, fn)

fn = "0"
backL3Driver = equation(backL3_euler, fn)

fn = "0"
backL4Driver = equation(backL4_euler, fn)

# Tail
fn = "0.3"  # Up - down action
backL5Driver = equation(backL5_euler, fn)
fn = "0"  # Left(+) to right(-) action
backL5Driver = equation(backL5_euler, fn, 2)

fn = "0.1"  # Up - down action
backL6Driver = equation(backL6_euler, fn)
fn = "0"  # Left(+) to right(-) action
backL6Driver = equation(backL6_euler, fn, 2)

fn = "0"
tailL1Driver = equation(tailL1_euler, fn)

fn = "0"
tailL2Driver = equation(tailL2_euler, fn)




fn = ".4"
jawDriver = equation(jaw_euler, fn, 2) # rotate z

fn = "0"  # Generally would not move
beakDriver = equation(beak_euler, fn, 2) # rotate z

# If centered at rear joint, parented, 
# can be used  for eye movements
fn = "0" 
eyeLDriver = equation(eyeL_euler, fn)
fn = "0"
eyeRDriver = equation(eyeR_euler, fn)

# If the bird has a crest
fn = "0"
crestDriver = equation(crest_euler, fn)


# Left Wing
fn = ".9"
wingL_J1Driver = equation(wingL_J1_euler, fn, 2) # z-axis fwd-bkwd movement

fn = "-.9"
wingL_J2Driver = equation(wingL_J2_euler, fn, 2) # z-axis fwd-bkwd movement

fn = ".2"
wingL_J6Driver = equation(wingL_J6_euler, fn, 2) # z-axis fwd-bkwd movement

fn = ".3"
wingL_J7Driver = equation(wingL_J7_euler, fn, 2) # z-axis fwd-bkwd movement

fn = ".3"
wingL_J8Driver = equation(wingL_J8_euler, fn, 2) # z-axis fwd-bkwd movement

# Right Wing
# This could possibly just mirror left wing
fn = "-.9"
wingR_J1Driver = equation(wingR_J1_euler, fn, 2) # z-axis fwd-bkwd movement

fn = ".9"
wingR_J2Driver = equation(wingR_J2_euler, fn, 2) # z-axis fwd-bkwd movement

fn = "-.2"
wingR_J6Driver = equation(wingR_J6_euler, fn, 2) # z-axis fwd-bkwd movement

fn = "-.3"
wingR_J7Driver = equation(wingR_J7_euler, fn, 2) # z-axis fwd-bkwd movement

fn = "-.3"
wingR_J8Driver = equation(wingR_J8_euler, fn, 2) # z-axis fwd-bkwd movement
