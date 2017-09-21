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
character = 'centaur' # Option -  biped, quadruped, bird, spider, kangaroo
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

# Create Upper Body  
V_lowBack = (0, 0, 0.1)
lowBack = createBone("lowBack", bone.head, V_lowBack)
lowBack.parent = at.edit_bones[baseName + '_bone']

V_midBack = (0, 0, 0.22)
midBack = createBone("midBack", V_lowBack, V_midBack)
midBack.parent = at.edit_bones['lowBack']

V_cBack = (0, 0, 0.34)
cBack = createBone("cBack", V_midBack, V_cBack)
cBack.parent = at.edit_bones['midBack']

V_upperBack = (0, 0, 0.54)
upperBack = createBone("upperBack", V_cBack, V_upperBack)   
upperBack.parent = at.edit_bones['cBack']    

V_lowerNeck = (0, 0, 0.6)   
lowerNeck = createBone("lowerNeck", V_upperBack, V_lowerNeck)   
lowerNeck.parent = at.edit_bones['upperBack']

V_midNeck = (0, 0, 0.64)
midNeck = createBone("midNeck", (V_lowerNeck), V_midNeck) 
midNeck.parent = at.edit_bones['lowerNeck']

V_upperNeck = (0, 0, 0.68)
upperNeck = createBone("upperNeck", (V_midNeck), V_upperNeck)   
upperNeck.parent = at.edit_bones['midNeck']    

V_jawBase = (0.06, 0, 0.68)    
jawBase = createBone("jawBase", V_upperNeck, V_jawBase)
jawBase.parent = at.edit_bones['upperNeck']

V_jaw = (0.12, 0, .676)
jaw = createBone("jaw", V_jawBase, V_jaw)   
jaw.parent = at.edit_bones['jawBase']

# 
V_headBase = (0, 0, 0.72)   
headBase = createBone("headBase", V_upperNeck, V_headBase) 
headBase.parent = at.edit_bones['upperNeck']

V_mouthTop = (0.12, 0, .72)  
mouthTop = createBone("mouthTop", V_headBase, V_mouthTop) 
mouthTop.parent = at.edit_bones['headBase']

V_headMid = (0, 0, 0.77)
headMid = createBone("headMid", V_headBase, V_headMid)
headMid.parent = at.edit_bones['mouthTop']

V_headTop = (0, 0, 0.82)
headTop = createBone("headMid", V_headMid, V_headTop)
headTop.parent = at.edit_bones['headMid']


V_eyebaseR = (0.1, -0.04, 0.82)   
V_eyebaseL = (0.1, 0.04, 0.82)      
eyebaseR = createBone("eyebaseR", V_headTop, V_eyebaseR)
eyebaseR.parent = at.edit_bones['headMid']   
eyebaseL = createBone("eyebaseL", V_headTop, V_eyebaseL)  
eyebaseL.parent = at.edit_bones['headMid']

V_eyeRotR = (0.12, -0.04, 0.82)
V_eyeRotL = (0.12, 0.04, 0.82)
eyeRotR = createBone("eyeRotR", V_eyebaseR, V_eyeRotR) 
eyeRotR.parent = at.edit_bones['eyebaseR']   
eyeRotL = createBone("eyeRotL", V_eyebaseL, V_eyeRotL) 
eyeRotL.parent = at.edit_bones['eyebaseL']


V_NoseBase = (0.12, 0, 0.77)
noseBase = createBone("noseBase", V_headMid, V_NoseBase)
noseBase.parent = at.edit_bones['headMid']

V_Nose = (.13, 0, .75)
nose = createBone("nose", V_NoseBase, V_Nose)   
nose.parent = at.edit_bones['noseBase']





# Shoulder area
V_scapulaR = (0, .31, 0.48)
V_scapulaL = (0, -.31, 0.48) 
scapulaR = createBone("scapulaR", V_upperBack, V_scapulaR) 
scapulaR.parent = at.edit_bones['upperBack']  
scapulaL = createBone("scapulaL", V_upperBack, V_scapulaL)
scapulaL.parent = at.edit_bones['upperBack']

V_humerusR = (0, .59, 0.47)
V_humerusL = (0, -.59, 0.47)
humerusR = createBone("humerusR", (V_scapulaR), V_humerusR)  
humerusR.parent = at.edit_bones['scapulaR']  
humerusL = createBone("humerusL", V_scapulaL, V_humerusL)
humerusL.parent = at.edit_bones['scapulaL']

V_WristR = (0, .85, .47)
V_WristL = (0, -.85, .47)
radiusR = createBone("radiusR", V_humerusR, V_WristR)
radiusR.parent = at.edit_bones['humerusR']
radiusL = createBone("radiusL", V_humerusL, V_WristL)
radiusL.parent = at.edit_bones['humerusL']



# Reinforce - Adds bones that improve the meshes response
# and lessens the amount of skinning needed.
#if reinforce == True:
#    reinforce()




# Hand
# Create Pinky bones
pinky_x = -.08
pinky_z =.47
V_wristBaseR = (-.05, .87, pinky_z)
V_wristBaseL = (-.05, -.87, pinky_z)    
wristBase1R = createBone("wristBase1R", V_WristR, (V_wristBaseR))
wristBase1R.parent = at.edit_bones['radiusR']
wristBase1L = createBone("wristBase1L", V_WristL, (V_wristBaseL))
wristBase1L.parent = at.edit_bones['radiusL']

V_pinkyBaseR = (pinky_x, .958, pinky_z)
V_pinkyBaseL = (pinky_x, -.958, pinky_z)
pinkyBaseR = createBone("pinkyBaseR", (V_wristBaseR), (V_pinkyBaseR))
pinkyBaseR.parent = at.edit_bones['wristBase1R']
pinkyBaseL = createBone("pinkyBaseL", (V_wristBaseL), (V_pinkyBaseL))
pinkyBaseL.parent = at.edit_bones['wristBase1L']

V_pinkyJ1R = (pinky_x, .987, pinky_z)
V_pinkyJ1L = (pinky_x, -.987, pinky_z)
pinkyJ1R = createBone("pinkyJ1R", (V_pinkyBaseR), (V_pinkyJ1R))
pinkyJ1R.parent = at.edit_bones['pinkyBaseR']
pinkyJ1L = createBone("pinkyJ1L", (V_pinkyBaseL), (V_pinkyJ1L))
pinkyJ1L.parent = at.edit_bones['pinkyBaseL']

V_pinkyJ2R = (pinky_x, 1.01, pinky_z)
V_pinkyJ2L = (pinky_x, -1.01, pinky_z)
pinkyJ2R = createBone("pinkyJ2R", (V_pinkyJ1R), (V_pinkyJ2R))
pinkyJ2R.parent = at.edit_bones['pinkyJ1R']
pinkyJ2L = createBone("pinkyJ2L", (V_pinkyJ1L), (V_pinkyJ2L))
pinkyJ2L.parent = at.edit_bones['pinkyJ1L']

V_pinkyJ3R = (pinky_x, 1.03, pinky_z)
V_pinkyJ3L = (pinky_x, -1.03, pinky_z)
pinkyJ3R = createBone("pinkyJ3R", (V_pinkyJ2R), (V_pinkyJ3R))
pinkyJ3R.parent = at.edit_bones['pinkyJ2R']
pinkyJ3L = createBone("pinkyJ3L", (V_pinkyJ2L), (V_pinkyJ3L))
pinkyJ3L.parent = at.edit_bones['pinkyJ2L']




# Ring Finger bones
ring_x = -.04
ring_z = .47
V_WristBase2R = (ring_x, .952, ring_z)
V_WristBase2L = (ring_x, -.952, ring_z)
wristBase2R = createBone("wristBase2R", V_WristR, (V_WristBase2R))
wristBase2R.parent = at.edit_bones['radiusR']
wristBase2L = createBone("wristBase2L", V_WristL, (V_WristBase2L))
wristBase2L.parent = at.edit_bones['radiusL']

V_ringJ1R = (ring_x, .986, ring_z)
V_ringJ1L = (ring_x, -.986, ring_z)
ringJ1R = createBone("ringJ1R", V_WristBase2R, (V_ringJ1R))
ringJ1R.parent = at.edit_bones['wristBase2R']
ringJ1L = createBone("ringJ1L", V_WristBase2L, (V_ringJ1L))
ringJ1L.parent = at.edit_bones['wristBase2L']

V_ringJ2R = (ring_x, 1.02, ring_z)
V_ringJ2L = (ring_x, -1.02, ring_z)
ringJ2R = createBone("ringJ2R", (V_ringJ1R), (V_ringJ2R))
ringJ2R.parent = at.edit_bones['ringJ1R']
ringJ2L = createBone("ringJ2L", (V_ringJ1L), (V_ringJ2L))
ringJ2L.parent = at.edit_bones['ringJ1L']

V_ringJ3R = (ring_x, 1.06, ring_z)
V_ringJ3L = (ring_x, -1.06, ring_z)
ringJ3R = createBone("ringJ3R", (V_ringJ2R), (V_ringJ3R))
ringJ3R.parent = at.edit_bones['ringJ2R']
ringJ3L = createBone("ringJ3L", (V_ringJ2L), (V_ringJ3L))
ringJ3L.parent = at.edit_bones['ringJ2L']




# Middle Finger bones
mid_x = 0
mid_z = .47
V_wristBase3R = (mid_x, .952, mid_z)
V_wristBase3L = (mid_x, -.952, mid_z)
wristBase3R = createBone("wristBase3R", V_WristR, (V_wristBase3R))
wristBase3R.parent = at.edit_bones['radiusR']
wristBase3L = createBone("wristBase3L", V_WristL, (V_wristBase3L))
wristBase3L.parent = at.edit_bones['radiusL']

V_midJ1R = (mid_x, 1.00, mid_z)
V_midJ1L = (mid_x, -1.00, mid_z)
midJ1R = createBone("midJ1R", (V_wristBase3R), (V_midJ1R))
midJ1R.parent = at.edit_bones['wristBase3R']
midJ1L = createBone("midJ1L", (V_wristBase3L), (V_midJ1L))
midJ1L.parent = at.edit_bones['wristBase3L']
    
V_midJ2R = (mid_x, 1.04, mid_z)
V_midJ2L = (mid_x, -1.04, mid_z)
midJ2R = createBone("midJ2R", (V_midJ1R), (V_midJ2R))
midJ2R.parent = at.edit_bones['midJ1R']
midJ2L = createBone("midJ2L", (V_midJ1L), (V_midJ2L))
midJ2L.parent = at.edit_bones['midJ1L']    

V_midJ3R = (mid_x, 1.08, mid_z)
V_midJ3L = (mid_x, -1.08, mid_z)
midJ3R = createBone("midJ3R", (V_midJ2R), (V_midJ3R))
midJ3R.parent = at.edit_bones['midJ2R']
midJ3L = createBone("midJ3L", (V_midJ2L), (V_midJ3L))
midJ3L.parent = at.edit_bones['midJ2L']






# Index Finger bones
index_x = .04
index_z = .47
V_wristBase4R = (index_x, .952, index_z)
V_wristBase4L = (index_x, -.952, index_z)
wristBase4R = createBone("wristBase4R", V_WristR, (V_wristBase4R))
wristBase4R.parent = at.edit_bones['radiusR']
wristBase4L = createBone("wristBase4L", V_WristL, (V_wristBase4L))
wristBase4L.parent = at.edit_bones['radiusL']

V_indexBaseR = (index_x, .986, index_z)
V_indexBaseL = (index_x, -.986, index_z)
indexBaseR = createBone("indexBaseR", (V_wristBase4R), (V_indexBaseR))
indexBaseR.parent = at.edit_bones['wristBase4R']
indexBaseL = createBone("indexBaseL", (V_wristBase4L), (V_indexBaseL))
indexBaseL.parent = at.edit_bones['wristBase4L']

V_indexJ1R = (index_x, 1.02, index_z)
V_indexJ1L = (index_x, -1.02, index_z)
indexJ1R = createBone("indexJ1R", (V_indexBaseR), (V_indexJ1R))
indexJ1R.parent = at.edit_bones['indexBaseR']
indexJ1L = createBone("indexJ1L", (V_indexBaseL), (V_indexJ1L))
indexJ1L.parent = at.edit_bones['indexBaseL']    

V_indexJ2R = (index_x, 1.05, index_z)
V_indexJ2L = (index_x, -1.05, index_z)
indexJ2R = createBone("indexJ2R", (V_indexJ1R), (V_indexJ2R))
indexJ2R.parent = at.edit_bones['indexJ1R']
indexJ2L = createBone("indexJ2L", (V_indexJ1L), (V_indexJ2L))
indexJ2L.parent = at.edit_bones['indexJ1L']   







# Thumb bones
thumb_z = .47
V_thumbBaseR = (.06, .9, thumb_z)
V_thumbBaseL = (.06, -.9, thumb_z)
thumbBaseR = createBone("thumbBaseR", V_WristR, V_thumbBaseR)
thumbBaseR.parent = at.edit_bones['radiusR']
thumbBaseL = createBone("thumbBaseL", V_WristL, V_thumbBaseL)
thumbBaseL.parent = at.edit_bones['radiusL']

V_thumbJ1R = (.1, .94, thumb_z-.002)
V_thumbJ1L = (.1, -.94, thumb_z-.002)
thumbJ1R = createBone("thumbJ1R", (V_thumbBaseR), (V_thumbJ1R))
thumbJ1R.parent = at.edit_bones['thumbBaseR']
thumbJ1L = createBone("thumbJ1L", (V_thumbBaseL), (V_thumbJ1L))
thumbJ1L.parent = at.edit_bones['thumbBaseL']    

V_thumbJ2R = (.13, .96, thumb_z-.004)
V_thumbJ2L = (.13, -.96, thumb_z-.004)
thumbJ2R = createBone("thumbJ2R", (V_thumbJ1R), (V_thumbJ2R))
thumbJ2R.parent = at.edit_bones['thumbJ1R']
thumbJ2L = createBone("thumbJ2L", (V_thumbJ1L), (V_thumbJ2L))
thumbJ2L.parent = at.edit_bones['thumbJ1L']        



# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%  END CREATE UPPER BODY  %%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%



# Set Euler on rotated joints
ob = bpy.context.object
bpy.ops.object.mode_set(mode='POSE')

jaw_euler = ob.pose.bones['jaw']
jaw_euler.rotation_mode = 'XYZ'
jawBase_euler = ob.pose.bones['jawBase']
jawBase_euler.rotation_mode = 'XYZ'

headBase_euler = ob.pose.bones['headBase']
headBase_euler.rotation_mode = 'XYZ'
upperNeck_euler = ob.pose.bones['upperNeck']
upperNeck_euler.rotation_mode = 'XYZ'
midNeck_euler = ob.pose.bones['midNeck']
midNeck_euler.rotation_mode = 'XYZ'
upperBack_euler = ob.pose.bones['upperBack']
upperBack_euler.rotation_mode = 'XYZ'

#arms
humerusL_euler = ob.pose.bones['humerusL']
humerusL_euler.rotation_mode = 'XYZ'
humerusR_euler = ob.pose.bones['humerusR']
humerusR_euler.rotation_mode = 'XYZ'
radiusL_euler = ob.pose.bones['radiusL']
radiusL_euler.rotation_mode = 'XYZ'
radiusR_euler = ob.pose.bones['radiusR']
radiusR_euler.rotation_mode = 'XYZ'

# hands
pinkyBaseL_euler = ob.pose.bones['pinkyBaseL']
pinkyBaseL_euler.rotation_mode = 'XYZ'
pinkyBaseR_euler = ob.pose.bones['pinkyBaseR']
pinkyBaseR_euler.rotation_mode = 'XYZ'
pinkyJ1L_euler = ob.pose.bones['pinkyJ1L']
pinkyJ1L_euler.rotation_mode = 'XYZ'
pinkyJ1R_euler = ob.pose.bones['pinkyJ1R']
pinkyJ1R_euler.rotation_mode = 'XYZ'
pinkyJ2L_euler = ob.pose.bones['pinkyJ2L']
pinkyJ2L_euler.rotation_mode = 'XYZ'
pinkyJ2R_euler = ob.pose.bones['pinkyJ2R']
pinkyJ2R_euler.rotation_mode = 'XYZ'
pinkyJ3L_euler = ob.pose.bones['pinkyJ3L']
pinkyJ3L_euler.rotation_mode = 'XYZ'
pinkyJ3R_euler = ob.pose.bones['pinkyJ3R']
pinkyJ3R_euler.rotation_mode = 'XYZ'

ringJ1L_euler = ob.pose.bones['ringJ1L']
ringJ1L_euler.rotation_mode = 'XYZ'
ringJ1R_euler = ob.pose.bones['ringJ1R']
ringJ1R_euler.rotation_mode = 'XYZ'
ringJ2L_euler = ob.pose.bones['ringJ2L']
ringJ2L_euler.rotation_mode = 'XYZ'
ringJ2R_euler = ob.pose.bones['ringJ2R']
ringJ2R_euler.rotation_mode = 'XYZ'
ringJ3L_euler = ob.pose.bones['ringJ3L']
ringJ3L_euler.rotation_mode = 'XYZ'
ringJ3R_euler = ob.pose.bones['ringJ3R']
ringJ3R_euler.rotation_mode = 'XYZ'

midJ1L_euler = ob.pose.bones['midJ1L']
midJ1L_euler.rotation_mode = 'XYZ'
midJ1R_euler = ob.pose.bones['midJ1R']
midJ1R_euler.rotation_mode = 'XYZ'
midJ2L_euler = ob.pose.bones['midJ2L']
midJ2L_euler.rotation_mode = 'XYZ'
midJ2R_euler = ob.pose.bones['midJ2R']
midJ2R_euler.rotation_mode = 'XYZ'
midJ3L_euler = ob.pose.bones['midJ3L']
midJ3L_euler.rotation_mode = 'XYZ'
midJ3R_euler = ob.pose.bones['midJ3R']
midJ3R_euler.rotation_mode = 'XYZ'

indexBaseL_euler = ob.pose.bones['indexBaseL']
indexBaseL_euler.rotation_mode = 'XYZ'
indexBaseR_euler = ob.pose.bones['indexBaseR']
indexBaseR_euler.rotation_mode = 'XYZ'
indexJ1L_euler = ob.pose.bones['indexJ1L']
indexJ1L_euler.rotation_mode = 'XYZ'
indexJ1R_euler = ob.pose.bones['indexJ1R']
indexJ1R_euler.rotation_mode = 'XYZ'
indexJ2L_euler = ob.pose.bones['indexJ2L']
indexJ2L_euler.rotation_mode = 'XYZ'
indexJ2R_euler = ob.pose.bones['indexJ2R']
indexJ2R_euler.rotation_mode = 'XYZ'

thumbBaseL_euler = ob.pose.bones['thumbBaseL']
thumbBaseL_euler.rotation_mode = 'XYZ'
thumbBaseR_euler = ob.pose.bones['thumbBaseR']
thumbBaseR_euler.rotation_mode = 'XYZ'
thumbJ1L_euler = ob.pose.bones['thumbJ1L']
thumbJ1L_euler.rotation_mode = 'XYZ'
thumbJ1R_euler = ob.pose.bones['thumbJ1R']
thumbJ1R_euler.rotation_mode = 'XYZ'
thumbJ2L_euler = ob.pose.bones['thumbJ2L']
thumbJ2L_euler.rotation_mode = 'XYZ'
thumbJ2R_euler = ob.pose.bones['thumbJ2R']
thumbJ2R_euler.rotation_mode = 'XYZ'



# Hips, legs
pelvis_euler = ob.pose.bones['pelvis']
pelvis_euler.rotation_mode = 'XYZ'
femurL_euler = ob.pose.bones['femurL']
femurL_euler.rotation_mode = 'XYZ'
tibiaL_euler = ob.pose.bones['tibiaL']
tibiaL_euler.rotation_mode = 'XYZ'
ankleL_euler = ob.pose.bones['ankleL']
ankleL_euler.rotation_mode = 'XYZ'
toeL_euler = ob.pose.bones['toeL']
toeL_euler.rotation_mode = 'XYZ'

femurL_euler = ob.pose.bones['femurL']
femurL_euler.rotation_mode = 'XYZ'

femurR_euler = ob.pose.bones['femurR']
femurR_euler.rotation_mode = 'XYZ'
tibiaR_euler = ob.pose.bones['tibiaR']
tibiaR_euler.rotation_mode = 'XYZ'
ankleR_euler = ob.pose.bones['ankleR']
ankleR_euler.rotation_mode = 'XYZ'
toeR_euler = ob.pose.bones['toeR']
toeR_euler.rotation_mode = 'XYZ'


# Horse back parts
hUpperBack_euler = ob.pose.bones['hUpperBack']
hUpperBack_euler.rotation_mode = 'XYZ'
hMidBack_euler = ob.pose.bones['hMidBack']
hMidBack_euler.rotation_mode = 'XYZ'
hBackSway_euler = ob.pose.bones['hBackSway']
hBackSway_euler.rotation_mode = 'XYZ'
hHipCenter_euler = ob.pose.bones['hHipCenter']
hHipCenter_euler.rotation_mode = 'XYZ'
hHipL_euler = ob.pose.bones['hHipL']
hHipL_euler.rotation_mode = 'XYZ'
hHipR_euler = ob.pose.bones['hHipR']
hHipR_euler.rotation_mode = 'XYZ'
hHipExtL_euler = ob.pose.bones['hHipExtL']
hHipExtL_euler.rotation_mode = 'XYZ'
hHipExtR_euler = ob.pose.bones['hHipExtR']
hHipExtR_euler.rotation_mode = 'XYZ'
hFemurL_euler = ob.pose.bones['hFemurL']
hFemurL_euler.rotation_mode = 'XYZ'
hFemurR_euler = ob.pose.bones['hFemurR']
hFemurR_euler.rotation_mode = 'XYZ'
hTibiaL_euler = ob.pose.bones['hTibiaL']
hTibiaL_euler.rotation_mode = 'XYZ'
hTibiaR_euler = ob.pose.bones['hTibiaR']
hTibiaR_euler.rotation_mode = 'XYZ'
hAnkleL_euler = ob.pose.bones['hAnkleL']
hAnkleL_euler.rotation_mode = 'XYZ'
hAnkleR_euler = ob.pose.bones['hAnkleR']
hAnkleR_euler.rotation_mode = 'XYZ'
hToeL_euler = ob.pose.bones['hToeL']
hToeL_euler.rotation_mode = 'XYZ'
hToeR_euler = ob.pose.bones['hToeR']
hToeR_euler.rotation_mode = 'XYZ'



# To get the rotation to work correctly, the bones must be created orthographically (aligned with x, y, z axis.)
# then rotated afterward.
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# %%%%%%%%%%%%%% SET DRIVERS %%%%%%%%%%%%%
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
bpy.ops.object.mode_set(mode='POSE')

# Frame must start at zero for pose at start to work
bpy.context.scene.frame_start = 0
#  Set Drivers
# Left hip
# Left
femurLDriver = femurL_euler.driver_add('rotation_euler', 2)
femurLDriver.driver.type = 'SCRIPTED'
femurLDriver.driver.expression = "(asin(sin(radians(7.07 * frame))) * 1)/3.14"
# Right
femurRDriver = femurR_euler.driver_add('rotation_euler', 2)
femurRDriver.driver.type = 'SCRIPTED'
femurRDriver.driver.expression = "-(asin(sin(radians(7.07 * frame))) * 1)/3.14"

# Knee rotate
# Left
tibiaLDriver = tibiaL_euler.driver_add('rotation_euler', 2)
tibiaLDriver.driver.type = 'SCRIPTED'
tibiaLDriver.driver.expression = "((asin(sin(radians(7.07 * frame))) * 1.2)/3.14 + .4) * (frame*(1/(frame+.0001)))"
# Right
tibiaRDriver = tibiaR_euler.driver_add('rotation_euler', 2)
tibiaRDriver.driver.type = 'SCRIPTED'
tibiaRDriver.driver.expression = "(-(asin(sin(radians(7.07 * frame))) * 1.2)/3.14 + .4) * (frame*(1/(frame+.0001)))"

# Ankle rotation
# Left
bpy.ops.object.mode_set(mode='POSE')
ankleLDriver = ankleL_euler.driver_add('rotation_euler', 2)  # 2 is z-axis
ankleLDriver.driver.type = 'SCRIPTED'
ankleLDriver.driver.expression = "((asin(sin(radians(7.07 * frame))) * 2)/3.14 + .9) * (frame*(1/(frame+.0001)))-.8"
# Right
ankleRDriver = ankleR_euler.driver_add('rotation_euler', 2)
ankleRDriver.driver.type = 'SCRIPTED'
ankleRDriver.driver.expression = "(-(asin(sin(radians(7.07 * frame))) * 2)/3.14 + .9) * (frame*(1/(frame+.0001)))-.8"

# Toe rotation
# Left
toeLDriver = toeL_euler.driver_add('rotation_euler', 2)
toeLDriver.driver.type = 'SCRIPTED'
toeLDriver.driver.expression = "((asin(sin(radians(7.07 * frame))) * 1.2)/3.14 + .4) * (frame*(1/(frame+.0001)))+.4"
# Right
toeRDriver = toeR_euler.driver_add('rotation_euler', 2)
toeRDriver.driver.type = 'SCRIPTED'
toeRDriver.driver.expression = "(-(asin(sin(radians(7.07 * frame))) * 1.2)/3.14 + .4) * (frame*(1/(frame+.0001)))+.4"




# Horse back legs
# Femur
hFemurLDriver = hFemurL_euler.driver_add('rotation_euler', 2)
hFemurLDriver.driver.type = 'SCRIPTED'
hFemurLDriver.driver.expression = "(asin(sin(radians(7.07 * frame))) * .8)/3.14"
hFemurRDriver = hFemurR_euler.driver_add('rotation_euler', 2)
hFemurRDriver.driver.type = 'SCRIPTED'
hFemurRDriver.driver.expression = "-(asin(sin(radians(7.07 * frame))) * .8)/3.14"

# Tibia
hTibiaLDriver = hTibiaL_euler.driver_add('rotation_euler', 2)
hTibiaLDriver.driver.type = 'SCRIPTED'
hTibiaLDriver.driver.expression = "(asin(sin(radians(7.07 * frame))) * 1.0)/3.14 + .2"
hTibiaRDriver = hTibiaR_euler.driver_add('rotation_euler', 2)
hTibiaRDriver.driver.type = 'SCRIPTED'
hTibiaRDriver.driver.expression = "-(asin(sin(radians(7.07 * frame))) * 1.0)/3.14 + .2"

# Rear Ankle
hAnkleLDriver = hAnkleL_euler.driver_add('rotation_euler', 2)
hAnkleLDriver.driver.type = 'SCRIPTED'
hAnkleLDriver.driver.expression = "((asin(sin(radians(7.07 * frame))) * 2)/3.14 + 1.4) * (frame*(1/(frame+.0001)))-1.0"
hAnkleRDriver = hAnkleR_euler.driver_add('rotation_euler', 2)
hAnkleRDriver.driver.type = 'SCRIPTED'
hAnkleRDriver.driver.expression = "(-(asin(sin(radians(7.07 * frame))) * 2)/3.14 + 1.4) * (frame*(1/(frame+.0001)))-1.0"


hToeLDriver = hToeL_euler.driver_add('rotation_euler', 2)
hToeLDriver.driver.type = 'SCRIPTED'
hToeLDriver.driver.expression = "((asin(sin(radians(7.07 * frame))) * 1.2)/3.14 + .2) * (frame*(1/(frame+.0001)))+.4"
hToeRDriver = hToeR_euler.driver_add('rotation_euler', 2)
hToeRDriver.driver.type = 'SCRIPTED'
hToeRDriver.driver.expression = "(-(asin(sin(radians(7.07 * frame))) * 1.2)/3.14 + .2) * (frame*(1/(frame+.0001)))+.4"




# Upper Back
upperBackDriver = upperBack_euler.driver_add('rotation_euler', 1)
upperBackDriver.driver.type = 'SCRIPTED'
upperBackDriver.driver.expression = "(asin(sin(radians(7.07 * frame))) * .6)/3.14"

# Compensate for shoulder rotate by rotating neck and head in opposite direction, in two parts
midNeckDriver = midNeck_euler.driver_add('rotation_euler', 1)
midNeckDriver.driver.type = 'SCRIPTED'
midNeckDriver.driver.expression = "-(asin(sin(radians(7.07 * frame))) * .3)/3.14"
upperNeckDriver = upperNeck_euler.driver_add('rotation_euler', 1)
upperNeckDriver.driver.type = 'SCRIPTED'
upperNeckDriver.driver.expression = "-(asin(sin(radians(7.07 * frame))) * .3)/3.14"


# Arms rotation
bpy.context.object.pose.bones["humerusL"].rotation_euler[0] = 1.5708
humerusLDriver = humerusL_euler.driver_add('rotation_euler', 1)
humerusLDriver.driver.type = 'SCRIPTED'
humerusLDriver.driver.expression = "(asin(sin(radians(7.07 * frame))) * .8)/3.14"

bpy.context.object.pose.bones["humerusR"].rotation_euler[0] = -1.5708
humerusRDriver = humerusR_euler.driver_add('rotation_euler', 1)
humerusRDriver.driver.type = 'SCRIPTED'
humerusRDriver.driver.expression = "(asin(sin(radians(7.07 * frame))) * .8)/3.14"


# Elbows
radiusLDriver = radiusL_euler.driver_add('rotation_euler', 2)
radiusLDriver.driver.type = 'SCRIPTED'
radiusLDriver.driver.expression = "((asin(sin(radians(7.07 * frame))) * .7)/3.14 + .3) * (frame*(1/(frame+.0001)))"

radiusRDriver = radiusR_euler.driver_add('rotation_euler', 2)
radiusRDriver.driver.type = 'SCRIPTED'
radiusRDriver.driver.expression = "((asin(sin(radians(7.07 * frame))) * .7)/3.14 - .3) * (frame*(1/(frame+.0001)))"


# at.show_axes = 