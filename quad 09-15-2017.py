# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Start with a generalized header code section
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
import bpy, math

# Stabilization bones
def reinforce():  # TODO Fudge up .32 before use, or adapt to variables passed in
   VShoulderFrntR = (0.02, .27, 0.484)
   VShoulderFrntL = (0.02, -.27, 0.484)
   ShoulderFrntR = createBone("ShoulderFrntR", VTorsoJoint, (VShoulderFrntR))
   ShoulderFrntR.parent = at.edit_bones['upperBack']  
   ShoulderFrntL = createBone("ShoulderFrntL", VTorsoJoint, (VShoulderFrntL))   
   ShoulderFrntL.parent = at.edit_bones['upperBack']
#
   VShoulderBackR = (-0.02, .27, 0.484)
   VShoulderBackL = (-0.02, -.27, 0.484)
   ShoulderBackR = createBone("ShoulderBackR", VTorsoJoint, (VShoulderBackR))
   ShoulderBackR.parent = at.edit_bones['upperBack']  
   ShoulderBackL = createBone("ShoulderBackL", VTorsoJoint, (VShoulderBackL))
   ShoulderBackL.parent = at.edit_bones['upperBack']
#
   VShoulderTopR = (0, .27, 0.52)
   VShoulderTopL = (0, -.27, 0.52)
   ShoulderTopR = createBone("ShoulderTopR", VTorsoJoint, (VShoulderTopR))
   ShoulderTopR.parent = at.edit_bones['upperBack']  
   ShoulderTopL = createBone("ShoulderTopL", VTorsoJoint, (VShoulderTopL))   
   ShoulderTopL.parent = at.edit_bones['upperBack']
#
   VShoulderBottomR = (0, .27, 0.464)
   VShoulderBottomL = (0, -.27, 0.464)
   ShoulderBottomR = createBone("ShoulderBottomR", VTorsoJoint, (VShoulderBottomR))
   ShoulderBottomR.parent = at.edit_bones['upperBack']  
   ShoulderBottomL = createBone("ShoulderBottomL", VTorsoJoint, (VShoulderBottomL))
   ShoulderBottomL.parent = at.edit_bones['upperBack']
#
   VRibsR = (0, 0.16, .2)
   VRibsL = (0, -0.16, .2)
   RibsR = createBone("RibsR", (VShoulderBottomR), (VRibsR))
   RibsR.parent = at.edit_bones['ShoulderBottomR']  
   RibsL = createBone("RibsL", (VShoulderBottomL), (VRibsL))
   RibsL.parent = at.edit_bones['ShoulderBottomL']



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
character = 'quadruped' # Option -  biped, quadruped, bird, spider, kangaroo
show_axes = False    # Option - Show armature axis

height = 1.14
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
x =  .3 * n; y = 1 * n; z = height;
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
bone.head = [0, 0, 0]   # LOCAL COORDINATE, [0,0,0] places bone directly on armature.
bone.tail = [-0.2, 0, 0]   # You can use parenthesis or brackets () []
# The remaining code builds the character starting from the
# head of the handle, that is, at the origin.

# THINGS ABOVE THAT MAY VARY BASED ON THE CHARACTER:
# 1. rig location x =  .3 * n; y = 3.2 * n; z = height;
#   This can set the initial location of the character. 
#   This may also be set at the end of the code.
# 2. bone.tail sets the general orientation of the
#   handle created for moving the character - this
#   could vary, based  on the type of character.
# 3. Character name - biped, quadruped, bird, spider, kangaroo

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# End generalized header code section
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%  CREATE LOWER BODY   %%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

#Parameters listed in next line:     
#           name     Vhead       Vtail    roll   Use_connect
V_pelvis = (0, 0, -.13)
pelvis = createBone("pelvis", bone.head, V_pelvis, 0)
pelvis.parent = at.edit_bones[baseName + '_bone']
hipWidth = .12


V_hipR = (0, hipWidth, -.13)
V_hipL = (0, -hipWidth, -.13)
hipR = createBone("hipR", V_pelvis, V_hipR, 0)
hipR.parent = at.edit_bones['pelvis']
hipL = createBone("hipL", V_pelvis, V_hipL, 0)
hipL.parent = at.edit_bones['pelvis']


V_femurR = (0, hipWidth, -.6)
V_femurL = (0, -hipWidth, -.6)    
femurR = createBone("femurR", V_hipR, V_femurR, 0)
femurR.parent = at.edit_bones['hipR']
femurL = createBone("femurL", V_hipL, V_femurL, 0)
femurL.parent = at.edit_bones['hipL']

V_tibiaR = (0, hipWidth, -.94)
V_tibiaL = (0, -hipWidth, -.94)
tibiaR = createBone("tibiaR", V_femurR, V_tibiaR, 0)
tibiaR.parent = at.edit_bones['femurR']
tibiaL = createBone("tibiaL", V_femurL, V_tibiaL, 0)
tibiaL.parent = at.edit_bones['femurL']

# XXXXX  Change to orthogonal, then rotate.  09-12-2017
V_ankleR = (0, hipWidth, -1.02)
V_ankleL = (0, -hipWidth, -1.02)
ankleR = createBone("ankleR", (V_tibiaR), (V_ankleR), 0)
ankleR.parent = at.edit_bones['tibiaR']
ankleL = createBone("ankleL", (V_tibiaL), (V_ankleL), 0)
ankleL.parent = at.edit_bones['tibiaL']  
# XXXXX  Change to orthogonal, then rotate.  09-12-2017
V_toeR = (0, hipWidth, -1.1)
V_toeL = (0, -hipWidth, -1.1)
toeR = createBone("toeR", (V_ankleR), (V_toeR), 0)
toeR.parent = at.edit_bones['ankleR']
toeL = createBone("toeL", (V_ankleL), (V_toeL), 0)
toeL.parent = at.edit_bones['ankleL']
#
#  End Of Lower Body Build %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


# Create Horse Back  
# bpy.context.scene.cursor_location = VRigArmatHead
# "h" Prefix for all horse parts
V_horseUpperBack = (-0.38, 0, .02)
hUpperBack = createBone("hUpperBack", bone.tail, V_horseUpperBack)
hUpperBack.parent = at.edit_bones[baseName + '_bone']

V_horseMidBack = (-.52, 0, -.02)
hMidBack = createBone("hMidBack", V_horseUpperBack, V_horseMidBack)
hMidBack.parent = at.edit_bones['hUpperBack']

V_horseBackSway = (-.72, 0, -0.04)
hBackSway = createBone("hBackSway", V_horseMidBack, V_horseBackSway)
hBackSway.parent = at.edit_bones['hMidBack']

V_horseHipCenter = (-.84, 0, .04)
hHipCenter = createBone("hHipCenter", V_horseBackSway, V_horseHipCenter)
hHipCenter.parent = at.edit_bones['hBackSway']

hRearHipWidth = .13
V_horseLHip = (-.84, -hRearHipWidth, -0.08)
hHipL = createBone("hHipL", V_horseHipCenter, V_horseLHip)
hHipL.parent = at.edit_bones['hHipCenter']

V_horseRHip = (-.84, hRearHipWidth, -0.08)
hHipR = createBone("hHipR", V_horseHipCenter, V_horseRHip)
hHipR.parent = at.edit_bones['hHipCenter']

V_horseHipExtL = (-.78, -hRearHipWidth, -.2)
V_horseHipExtR = (-.78, hRearHipWidth, -.2)
hHipExtL = createBone("hHipExtL", V_horseLHip, V_horseHipExtL)
hHipExtL.parent = at.edit_bones['hHipL']
hHipextR = createBone("hHipExtR", V_horseRHip, V_horseHipExtR)
hHipextR.parent = at.edit_bones['hHipR']

V_horseFemurL = (-.88, -hRearHipWidth, -.6)
V_horseFemurR = (-.88, hRearHipWidth, -.6)
hFemurL = createBone("hFemurL", V_horseHipExtL, V_horseFemurL)
hFemurL.parent = at.edit_bones['hHipExtL']
hFemurR = createBone("hFemurR", V_horseHipExtR, V_horseFemurR)
hFemurR.parent = at.edit_bones['hHipExtR']

V_horseTibiaL = (-.82, -hRearHipWidth, -.94)
V_horseTibiaR = (-.82, hRearHipWidth, -.94)
hTibiaL = createBone("hTibiaL", V_horseFemurL, V_horseTibiaL)
hTibiaL.parent = at.edit_bones['hFemurL']
hTibiaR = createBone("hTibiaR", V_horseFemurR, V_horseTibiaR)
hTibiaR.parent = at.edit_bones['hFemurR']

# XXXXX  Changed to orthogonal, then rotate.  09-12-2017
V_horseLAnkle = (-.82, -hRearHipWidth, -1.02)
V_horseRAnkle = (-.82, hRearHipWidth, -1.02)
hAnkleL = createBone("hAnkleL", V_horseTibiaL, V_horseLAnkle)
hAnkleL.parent = at.edit_bones['hTibiaL']
hAnkleR = createBone("hAnkleR", V_horseTibiaR, V_horseRAnkle)
hAnkleR.parent = at.edit_bones['hTibiaR']
# XXXXX  Changed to orthogonal, then rotate.  09-12-2017
V_horseLToe = (-.82, -hRearHipWidth, -1.1)
V_horseRToe = (-.82, hRearHipWidth, -1.1)
hToeL = createBone("hToeL", V_horseLAnkle, V_horseLToe)
hToeL.parent = at.edit_bones['hAnkleL']
hToeR = createBone("hToeR", V_horseRAnkle, V_horseRToe)
hToeR.parent = at.edit_bones['hAnkleR']

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%  END CREATE HORSE BACK   %%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%  END CREATE NECK AND HEAD  %%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

V_neckBase = (0.22, 0, 0.12)
neckBase = createBone("neckBase", bone.head, (V_neckBase))
neckBase.parent = at.edit_bones[baseName + '_bone']

V_lowerNeck = (0.26, 0, 0.18)
lowerNeck = createBone("lowerNeck", (V_neckBase), V_lowerNeck)   
lowerNeck.parent = at.edit_bones['neckBase']    

V_midNeck = (0.31, 0, 0.26)   
midNeck = createBone("midNeck", V_lowerNeck, (V_midNeck))   
midNeck.parent = at.edit_bones['lowerNeck']

V_upperNeck = (0.35, 0, 0.30)
upperNeck = createBone("upperNeck", (V_midNeck), (V_upperNeck))   
upperNeck.parent = at.edit_bones['midNeck']

V_skullBase = (0.39, 0, 0.34)
skullBase = createBone("skullBase", (V_upperNeck), V_skullBase)   
skullBase.parent = at.edit_bones['upperNeck']    

V_jawBase = (0.43, 0, 0.38)    
jawBase = createBone("jawBase", V_skullBase, (V_jawBase))   
jawBase.parent = at.edit_bones['skullBase']

V_jaw = (0.52, 0, .38)
jaw = createBone("jaw", (V_jawBase), (V_jaw))   
jaw.parent = at.edit_bones['jawBase']

# 
V_headBase = (0.40, 0, 0.44)   
headBase = createBone("headBase", V_skullBase, (V_headBase))   
headBase.parent = at.edit_bones['skullBase']

V_mouthTop = (0.52, 0, .44)  
mouthTop = createBone("mouthTop", (V_headBase), (V_mouthTop))   
mouthTop.parent = at.edit_bones['headBase']

V_headTop = (0.40, 0, 0.52)
headMid = createBone("headMid", (V_headBase), V_headTop)   
headMid.parent = at.edit_bones['headBase']

V_eyeR = (0.52, -0.034, 0.52)   
V_eyeL = (0.52, 0.034, 0.52)      
eyeR = createBone("eyeR", V_headTop, (V_eyeR))   
eyeR.parent = at.edit_bones['headMid']   
eyeL = createBone("eyeL", V_headTop, (V_eyeL))   
eyeL.parent = at.edit_bones['headMid']

V_headTopTail = (0.40, 0, 0.58)
headTop = createBone("headTop", V_headTop, (V_headTopTail))
headTop.parent = at.edit_bones['headMid']

V_headBack = (0.34, 0, 0.52)
headBack = createBone("headBack", V_headTop, (V_headBack))
headBack.parent = at.edit_bones['headMid']

V_NoseBase = (0.526, 0, 0.49)
noseBase = createBone("noseBase", V_headTop, (V_NoseBase))
noseBase.parent = at.edit_bones['headMid']
V_Nose = (.54, 0, .46)
nose = createBone("nose", (V_NoseBase), (V_Nose))
nose.parent = at.edit_bones['noseBase']


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%  END CREATE NECK AND HEAD  %%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
bpy.ops.object.mode_set(mode='POSE')

# getEuler output represents:
# bpy.data.objects['rg00spider'].pose.bones["backCenter"]
def getEuler(str_bone_name):
    bpy.ops.object.mode_set(mode='POSE')
    ob = bpy.context.object
    out = ob.pose.bones[str_bone_name]
    out.rotation_mode = 'XYZ'
    return out


# Set Euler on rotated joints
jaw_euler = getEuler('jaw')
jawBase_euler = getEuler('jawBase')
headBase_euler = getEuler('headBase')
skullBase_euler= getEuler('skullBase')
neckBase_euler = getEuler('neckBase')
upperNeck_euler = getEuler('upperNeck')
midNeck_euler = getEuler('midNeck')
lowerNeck_euler = getEuler('lowerNeck')
# Hips, legs
pelvis_euler = getEuler('pelvis')
femurL_euler = getEuler('femurL')
tibiaL_euler = getEuler('tibiaL')
ankleL_euler = getEuler('ankleL')
toeL_euler = getEuler('toeL')
femurL_euler = getEuler('femurL')
femurR_euler = getEuler('femurR')
tibiaR_euler = getEuler('tibiaR')
ankleR_euler = getEuler('ankleR')
toeR_euler = getEuler('toeR')
# Horse back parts
hUpperBack_euler = getEuler('hUpperBack')
hMidBack_euler = getEuler('hMidBack')
hBackSway_euler = getEuler('hBackSway')
hHipCenter_euler = getEuler('hHipCenter')
hHipL_euler = getEuler('hHipL')
hHipR_euler = getEuler('hHipR')
hHipExtL_euler = getEuler('hHipExtL')
hHipExtR_euler = getEuler('hHipExtR')
hFemurL_euler = getEuler('hFemurL')
hFemurR_euler = getEuler('hFemurR')
hTibiaL_euler = getEuler('hTibiaL')
hTibiaR_euler = getEuler('hTibiaR')
hAnkleL_euler = getEuler('hAnkleL')
hAnkleR_euler = getEuler('hAnkleR')
hToeL_euler = getEuler('hToeL')
hToeR_euler = getEuler('hToeR')




# To get the rotation to work correctly, the bones must be created orthographically (aligned with x, y, z axis.)
# then rotated afterwards.
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# %%%%%%%%%%%%%% SET DRIVERS %%%%%%%%%%%%%
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
bpy.ops.object.mode_set(mode='POSE')
# Frame must start at zero for pose at start to work
bpy.context.scene.frame_start = 0

# Equation for bone joints, with euler transform
def equation(euler, fn="0", axis=0):
    edriver = euler.driver_add('rotation_euler', axis)
    edriver.driver.type = 'SCRIPTED'
    edriver.driver.expression = fn
    return edriver



# Left hip
# Left
fn = "(asin(sin(radians(7.07 * frame))) * 1)/3.14"
femurLDriver = equation(femurL_euler, fn, 2)

# Right
fn = "-(asin(sin(radians(7.07 * frame))) * 1)/3.14"
femurRDriver = equation(femurR_euler, fn, 2)


# Knee rotate
# Left
fn = "((asin(sin(radians(7.07 * frame))) * 1.2)/3.14 + .4) * (frame*(1/(frame+.0001)))"
tibiaLDriver = equation(tibiaL_euler, fn, 2)

# Right
fn = "(-(asin(sin(radians(7.07 * frame))) * 1.2)/3.14 + .4) * (frame*(1/(frame+.0001)))"
tibiaRDriver = equation(tibiaR_euler, fn, 2)

# Ankle rotation
# Left
fn = "((asin(sin(radians(7.07 * frame))) * 2)/3.14 + .9) * (frame*(1/(frame+.0001)))-.8"
ankleLDriver = equation(ankleL_euler, fn, 2)  # 2 is z-axis

# Right
fn = "(-(asin(sin(radians(7.07 * frame))) * 2)/3.14 + .9) * (frame*(1/(frame+.0001)))-.8"
ankleRDriver = equation(ankleR_euler, fn, 2)


# Toe rotation
# Left
fn = "((asin(sin(radians(7.07 * frame))) * 1.2)/3.14 + .4) * (frame*(1/(frame+.0001)))+.4"
toeLDriver = equation(toeL_euler, fn, 2)

# Right
fn = "(-(asin(sin(radians(7.07 * frame))) * 1.2)/3.14 + .4) * (frame*(1/(frame+.0001)))+.4"
toeRDriver = equation(toeR_euler, fn, 2)


# Horse back legs
# Femur
fn = "(asin(sin(radians(7.07 * frame))) * .8)/3.14"
hFemurLDriver = equation(hFemurL_euler, fn, 2)

fn = "-(asin(sin(radians(7.07 * frame))) * .8)/3.14"
hFemurRDriver = equation(hFemurR_euler, fn, 2)



# Tibia
fn = "(asin(sin(radians(7.07 * frame))) * 1.0)/3.14 + .2"
hTibiaLDriver = equation(hTibiaL_euler, fn, 2)
fn = "-(asin(sin(radians(7.07 * frame))) * 1.0)/3.14 + .2"
hTibiaRDriver = equation(hTibiaR_euler, fn, 2)


# Rear Ankle
fn = "((asin(sin(radians(7.07 * frame))) * 2)/3.14 + 1.4) * (frame*(1/(frame+.0001)))-1.0"
hAnkleLDriver = equation(hAnkleL_euler, fn, 2)
fn = "(-(asin(sin(radians(7.07 * frame))) * 2)/3.14 + 1.4) * (frame*(1/(frame+.0001)))-1.0"
hAnkleRDriver = equation(hAnkleR_euler, fn, 2)


fn = "((asin(sin(radians(7.07 * frame))) * 1.2)/3.14 + .2) * (frame*(1/(frame+.0001)))+.4"
hToeLDriver = equation(hToeL_euler, fn, 2)

fn = "(-(asin(sin(radians(7.07 * frame))) * 1.2)/3.14 + .2) * (frame*(1/(frame+.0001)))+.4"
hToeRDriver = equation(hToeR_euler, fn, 2)



# Head side to side sway
fn = "(asin(sin(radians(7.07 * frame))) * .6)/3.14"
lowerNeckDriver = equation(lowerNeck_euler, fn, 1)

# Head forward-backward sway
fn = "(asin(sin(radians(7.07 * frame))) * .4)/3.14"
lowerNeckDriver = equation(lowerNeck_euler, fn, 0)

fn = "(asin(sin(radians(7.07 * frame))) * .4)/3.14"
lowerNeckDriver = equation(lowerNeck_euler, fn, 2)




# Compensate for shoulder rotate by rotating neck and head in opposite direction, in two parts
fn = "-(asin(sin(radians(7.07 * frame))) * .3)/3.14"
upperNeckDriver = equation(upperNeck_euler, fn, 1)

fn = "-(asin(sin(radians(7.07 * frame))) * .3)/3.14"
skullBaseDriver = equation(skullBase_euler, fn, 1)




# at.show_axes = 