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
character = 'biped' # Option -  biped, quadruped, bird, spider, kangaroo
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
#           name     V_head       V_tail    roll   Use_connect
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
V_ankleR = (0, hipWidth, -1.06)
V_ankleL = (0, -hipWidth, -1.06)
ankleR = createBone("ankleR", (V_tibiaR), (V_ankleR), 0)
ankleR.parent = at.edit_bones['tibiaR']
ankleL = createBone("ankleL", (V_tibiaL), (V_ankleL), 0)
ankleL.parent = at.edit_bones['tibiaL']  
# XXXXX  Change to orthogonal, then rotate.  09-12-2017
V_toeR = (0, hipWidth, -1.28)
V_toeL = (0, -hipWidth, -1.28)
toeR = createBone("toeR", (V_ankleR), (V_toeR), 0)
toeR.parent = at.edit_bones['ankleR']
toeL = createBone("toeL", (V_ankleL), (V_toeL), 0)
toeL.parent = at.edit_bones['ankleL']
#
#  End Of Lower Body Build %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%  CREATE UPPER BODY   %%%%%%%%%%
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

# getEuler output represents:
# bpy.data.objects['rg00spider'].pose.bones["backCenter"]
def getEuler(str_bone_name):
    bpy.ops.object.mode_set(mode='POSE')
    ob = bpy.context.object
    out = ob.pose.bones[str_bone_name]
    out.rotation_mode = 'XYZ'
    return out



jaw_euler = getEuler('jaw')
jawBase_euler = getEuler('jawBase')
headBase_euler = getEuler('headBase')
upperNeck_euler = getEuler('upperNeck')
midNeck_euler = getEuler('midNeck')
upperBack_euler = getEuler('upperBack')
humerusL_euler = getEuler('humerusL')#arms
humerusR_euler = getEuler('humerusR')
radiusL_euler = getEuler('radiusL')
radiusR_euler = getEuler('radiusR')

pinkyBaseL_euler = getEuler('pinkyBaseL')# hands
pinkyBaseR_euler = getEuler('pinkyBaseR')
pinkyJ1L_euler = getEuler('pinkyJ1L')
pinkyJ1R_euler = getEuler('pinkyJ1R')
pinkyJ2L_euler = getEuler('pinkyJ2L')
pinkyJ2R_euler = getEuler('pinkyJ2R')
pinkyJ3L_euler = getEuler('pinkyJ3L')
pinkyJ3R_euler = getEuler('pinkyJ3R')

ringJ1L_euler = getEuler('ringJ1L')
ringJ1R_euler = getEuler('ringJ1R')
ringJ2L_euler = getEuler('ringJ2L')
ringJ2R_euler = getEuler('ringJ2R')
ringJ3L_euler = getEuler('ringJ3L')
ringJ3R_euler = getEuler('ringJ3R')

midJ1L_euler = getEuler('midJ1L')
midJ1R_euler = getEuler('midJ1R')
midJ2L_euler = getEuler('midJ2L')
midJ2R_euler = getEuler('midJ2R')
midJ3L_euler = getEuler('midJ3L')
midJ3R_euler = getEuler('midJ3R')

indexBaseL_euler = getEuler('indexBaseL')
indexBaseR_euler = getEuler('indexBaseR')
indexJ1L_euler = getEuler('indexJ1L')
indexJ1R_euler = getEuler('indexJ1R')
indexJ2L_euler = getEuler('indexJ2L')
indexJ2R_euler = getEuler('indexJ2R')

thumbBaseL_euler = getEuler('thumbBaseL')
thumbBaseR_euler = getEuler('thumbBaseR')
thumbJ1L_euler = getEuler('thumbJ1L')
thumbJ1R_euler = getEuler('thumbJ1R')
thumbJ2L_euler = getEuler('thumbJ2L')
thumbJ2R_euler = getEuler('thumbJ2R')

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



# To get the rotation to work correctly, the bones must be created 
# orthographically (aligned with x, y, z axis.) then rotated afterword.
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# Drivers  equation(euler, fn="0" axis=0)  # axis 0=x 1=y 2=z
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
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
fn = "-((asin(sin(radians(7.07 * frame))) * 2)/3.14 + .4) * (frame*(1/(frame+.0001)))-.8"
ankleLDriver = equation(ankleL_euler, fn, 2)  # 2 is z-axis
# Right
fn = "((asin(sin(radians(7.07 * frame))) * 2)/3.14 - .4) * (frame*(1/(frame+.0001)))-.8"
ankleRDriver = equation(ankleR_euler, fn, 2)

# Toe rotation
# Left
fn = "((asin(sin(radians(7.07 * frame))) * .4)/3.14+.1) * (frame*(1/(frame+.0001)))-.7"
toeLDriver = equation(toeL_euler, fn, 2)
# Right
fn = "(-(asin(sin(radians(7.07 * frame))) * .4)/3.14+.1) * (frame*(1/(frame+.0001)))-.7"
toeRDriver = equation(toeR_euler, fn, 2)


# Upper Back
fn = "(asin(sin(radians(7.07 * frame))) * .6)/3.14"
upperBackDriver = equation(upperBack_euler, fn, 1)


# Compensate for shoulder rotate by rotating neck and head in opposite direction, in two parts
fn = "-(asin(sin(radians(7.07 * frame))) * .3)/3.14"
midNeckDriver = equation(midNeck_euler, fn, 1)
fn = "-(asin(sin(radians(7.07 * frame))) * .3)/3.14"
upperNeckDriver = equation(upperNeck_euler, fn, 1)


# Arms rotation
bpy.context.object.pose.bones["humerusL"].rotation_euler[0] = 1.5708
fn = "(asin(sin(radians(7.07 * frame))) * .8)/3.14"
humerusLDriver = equation(humerusL_euler, fn, 1)

bpy.context.object.pose.bones["humerusR"].rotation_euler[0] = -1.5708
fn = "(asin(sin(radians(7.07 * frame))) * .8)/3.14"
humerusRDriver = equation(humerusR_euler, fn, 1)

# Elbows
fn = "((asin(sin(radians(7.07 * frame))) * .7)/3.14 + .3) * (frame*(1/(frame+.0001)))"
radiusLDriver = equation(radiusL_euler, fn, 2)
fn = "((asin(sin(radians(7.07 * frame))) * .7)/3.14 - .3) * (frame*(1/(frame+.0001)))"
radiusRDriver = equation(radiusR_euler, fn, 2)


# at.show_axes = 
