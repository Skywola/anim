# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Start with a generalized header code section
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
import bpy, math

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
character = 'spider' # Option -  biped, quadruped, bird, spider, kangaroo
show_axes = False    # Option - Show armature axis

height = .2
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
bone.tail = [0, 0, 0.6]   # You can use parenthesis or brackets () []
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

bpy.ops.object.mode_set(mode='EDIT')
# Start Frame
# Create Legs 1 and 8, branching off  from radius1 
# radius is 1 - 4, these are the inner frame supports
Vradius1 = (.554, 0, 0)
radius1 = createBone('radius1', bone.head, Vradius1) # Horizontal radius  base of T-shape
radius1.parent = at.edit_bones[baseName + '_bone']
Vframe1 = (.554, -.223, 0)
Vframe8 = (.554, .223, 0)
frame1 = createBone('frame1', radius1.tail, Vframe1) # Top of T-shape
frame8 = createBone('frame8', radius1.tail, Vframe8) # Top of T-shape
frame1.parent = at.edit_bones['radius1']
frame8.parent = at.edit_bones['radius1']
# Add .16 to z-axis
VsideToSide1 = (.554, -.223, 0.16)
sideToSide1 = createBone('sideToSide1', frame1.tail, VsideToSide1) 
sideToSide1.parent = at.edit_bones['frame1']
VsideToSide8 = (.554, .223, 0.16)
sideToSide8 = createBone('sideToSide8', frame8.tail, VsideToSide8)  #  Vertical sideToSide
sideToSide8.parent = at.edit_bones['frame8']
# Create legs in a orthogonal position so rotate will work correctly
Vleg1 = (.94, -.223, 0.16)
leg1 = createBone('leg1', sideToSide1.tail, Vleg1)  # leg1 base
leg1.parent = at.edit_bones['sideToSide1']
Vleg8 = (.94, .223, 0.16)
leg8 = createBone('leg8', sideToSide8.tail, Vleg8)  # leg8 base
leg8.parent = at.edit_bones['sideToSide8']

Vtibia1 = (1.5, -.223, 0.16)
tibia1 = createBone('tibia1', leg1.tail, Vtibia1)  # tibia1
tibia1.parent = at.edit_bones['leg1']
Vtibia8 = (1.5, .223, 0.16)
tibia8 = createBone('tibia8', leg8.tail, Vtibia8)  # tibia8
tibia8.parent = at.edit_bones['leg8']

# Add .2 to x-coordinate
Vtoe1 = (1.7, -.223, 0.16)
toe1 = createBone('toe1', tibia1.tail, Vtoe1)  # toe1
toe1.parent = at.edit_bones['tibia1']
Vtoe8 = (1.7, .223, 0.16)
toe8 = createBone('toe8', tibia8.tail, Vtoe8)  # toe8 
toe8.parent = at.edit_bones['tibia8']


# Create Legs 2 and 3, branching off  from radius2
# radius is 1 - 4, these are the inner frame supports
Vradius2 = (0, -.554, 0)
radius2 = createBone('radius2', bone.head, Vradius2)  # Horizontal radius  base of T-shape
radius2.parent = at.edit_bones[baseName + '_bone']
Vframe2 = (.223, -.554, 0)
Vframe3 = (-.223, -.554, 0)
frame2 = createBone('frame2', radius2.tail, Vframe2)  # Top of T-shape
frame3 = createBone('frame3', radius2.tail, Vframe3)  # Top of T-shape
frame2.parent = at.edit_bones['radius2']
frame3.parent = at.edit_bones['radius2']
# Add .16 to z-axis
VsideToSide2 = (.223, -.554, 0.16)
sideToSide2 = createBone('sideToSide2', frame2.tail, VsideToSide2)  #  Vertical sideToSide
sideToSide2.parent = at.edit_bones['frame2']
VsideToSide3 = (-.223, -.554, 0.16)
sideToSide3 = createBone('sideToSide3', frame3.tail, VsideToSide3)  #  Vertical sideToSide
sideToSide3.parent = at.edit_bones['frame3']

Vleg2 = (.223, -.94, 0.16)
leg2 = createBone('leg2', sideToSide2.tail, Vleg2)  # leg2 base
leg2.parent = at.edit_bones['sideToSide2']
Vleg3 = (-.223, -.94, 0.16)
leg3 = createBone('leg3', sideToSide3.tail, Vleg3)  # leg3 base
leg3.parent = at.edit_bones['sideToSide3']
# subtract (.6) from y-axis, subtract (.6) z-axis to get 45-degree angle
Vtibia2 = (.223, -1.5, 0.16)
tibia2 = createBone('tibia2', leg2.tail, Vtibia2)  # tibia2 
tibia2.parent = at.edit_bones['leg2']
Vtibia3 = (-.223, -1.5, 0.16)
tibia3 = createBone('tibia3', leg3.tail, Vtibia3)  # tibia3
tibia3.parent = at.edit_bones['leg3']
# Add .2 to y-coordinate
Vtoe2 = (.223, -1.7, 0.16)
toe2 = createBone('toe2', tibia2.tail, Vtoe2)  # toe2
toe2.parent = at.edit_bones['tibia2']
Vtoe3 = (-.223, -1.7, 0.16)
toe3 = createBone('toe3', tibia3.tail, Vtoe3)  # toe3
toe3.parent = at.edit_bones['tibia3']



# Create Legs 4 and 5, branching off  from radius3
# radius is 1 - 4, these are the inner frame supports
Vradius3 = (-.554, 0, 0)
radius3 = createBone('radius3', bone.head, Vradius3)  # Horizontal radius  base of T-shape
radius3.parent = at.edit_bones[baseName + '_bone']
Vframe4 = (-.554, -.223, 0)
Vframe5 = (-.554, .223, 0)
frame4 = createBone('frame4', radius3.tail, Vframe4)  # Top of T-shape
frame5 = createBone('frame5', radius3.tail, Vframe5)  # Top of T-shape
frame4.parent = at.edit_bones['radius3']
frame5.parent = at.edit_bones['radius3']
# Add .16 to z-axis
VsideToSide4 = (-.554, -.223, 0.16)
sideToSide4 = createBone('sideToSide4', frame4.tail, VsideToSide4)  #  Vertical sideToSide
sideToSide4.parent = at.edit_bones['frame4']
VsideToSide5 = (-.554, .223, 0.16)
sideToSide5 = createBone('sideToSide5', frame5.tail, VsideToSide5)  #  Vertical sideToSide
sideToSide5.parent = at.edit_bones['frame5']

Vleg4 = (-.94, -.223, 0.16)
leg4 = createBone('leg4', sideToSide4.tail, Vleg4)  # leg4 base
leg4.parent = at.edit_bones['sideToSide4']
Vleg5 = (-.94, .223, 0.16)
leg5 = createBone('leg5', sideToSide5.tail, Vleg5)  # leg5 base
leg5.parent = at.edit_bones['sideToSide5']

Vtibia4 = (-1.5, -.223, 0.16)
tibia4 = createBone('tibia4', leg4.tail, Vtibia4)  # tibia4 
tibia4.parent = at.edit_bones['leg4']
Vtibia5 = (-1.5, .223, 0.16)
tibia5 = createBone('tibia5', leg5.tail, Vtibia5)  # tibia5
tibia5.parent = at.edit_bones['leg5']

Vtoe4 = (-1.7, -.223, 0.16)
toe4 = createBone('toe4', tibia4.tail, Vtoe4)  # toe4
toe4.parent = at.edit_bones['tibia4']
Vtoe5 = (-1.7, .223, 0.16)
toe5 = createBone('toe5', tibia5.tail, Vtoe5)  # toe5
toe5.parent = at.edit_bones['tibia5']


# Create Legs 6 and 7, branching off  from radius4
# radius is 1 - 4, these are the inner frame supports
Vradius4 = (0, .554, 0)
radius4 = createBone('radius4', bone.head, Vradius4)  # Horizontal radius  base of T-shape
radius4.parent = at.edit_bones[baseName + '_bone']
Vframe6 = (-.223, .554, 0)
Vframe7 = (.223, .554, 0)
frame6 = createBone('frame6', radius4.tail, Vframe6)  # Top of T-shape
frame7 = createBone('frame7', radius4.tail, Vframe7)  # Top of T-shape
frame6.parent = at.edit_bones['radius4']
frame7.parent = at.edit_bones['radius4']
# Add .16 to z-axis
VsideToSide6 = (-.223, .554, 0.16)
sideToSide6 = createBone('sideToSide6', frame6.tail, VsideToSide6)  #  Vertical sideToSide
sideToSide6.parent = at.edit_bones['frame6']
VsideToSide7 = (.223, .554, 0.16)
sideToSide7 = createBone('sideToSide7', frame7.tail, VsideToSide7)  #  Vertical sideToSide
sideToSide7.parent = at.edit_bones['frame7']
# add same amount (.4) to y-axis as z-axis to get 45-degree angle
Vleg6 = (-.223, .94, 0.16)
leg6 = createBone('leg6', sideToSide6.tail, Vleg6)  # leg6 base
leg6.parent = at.edit_bones['sideToSide6']
Vleg7 = (.223, .94, 0.16)
leg7 = createBone('leg7', sideToSide7.tail, Vleg7)  # leg7 base
leg7.parent = at.edit_bones['sideToSide7']
# subtract (.6) from y-axis, subtract (.6) z-axis to get 45-degree angle
Vtibia6 = (-.223, 1.5, 0.16)
tibia6 = createBone('tibia6', leg6.tail, Vtibia6)  # tibia6 
tibia6.parent = at.edit_bones['leg6']
Vtibia7 = (.223, 1.5, 0.16)
tibia7 = createBone('tibia7', leg7.tail, Vtibia7)  # tibia7
tibia7.parent = at.edit_bones['leg7']
# Add .2 to y-coordinate
Vtoe6 = (-.223, 1.7, 0.16)
toe6 = createBone('toe6', tibia6.tail, Vtoe6)  # toe6
toe6.parent = at.edit_bones['tibia6']
Vtoe7 = (.223, 1.7, 0.16)
toe7 = createBone('toe7', tibia7.tail, Vtoe7)  # toe7
toe7.parent = at.edit_bones['tibia7']





bpy.ops.object.mode_set(mode='POSE')
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# %%%%%%%%%%%%%% SET DRIVERS %%%%%%%%%%%%%
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# Template:
# __Driver = __.driver_add('rotation_euler', 0)
# __Driver.driver.type = 'SCRIPTED'
# __Driver.driver.expression = "(asin(sin(radians(7.07 * frame))) * .8)/3.14"
# bpy.context.scene.frame_current

# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# Rotations
# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
bpy.ops.object.mode_set(mode='POSE')
# getEuler output represents:
# bpy.data.objects['rg00spider'].pose.bones["backCenter"]
def getEuler(str_bone_name):
    bpy.ops.object.mode_set(mode='POSE')
    ob = bpy.context.object
    out = ob.pose.bones[str_bone_name]
    out.rotation_mode = 'XYZ'
    return out

    
leg1_euler = getEuler('leg1')
sideToSide1_euler = getEuler('sideToSide1')
tibia1_euler = getEuler('tibia1')
toe1_euler = getEuler('toe1')

leg2_euler = getEuler('leg2')
tibia2_euler = getEuler('tibia2')
sideToSide2_euler = getEuler('sideToSide2')
toe2_euler = getEuler('toe2')

leg3_euler = getEuler('leg3')
sideToSide3_euler = getEuler('sideToSide3')
tibia3_euler = getEuler('tibia3')
toe3_euler = getEuler('toe3')

leg4_euler = getEuler('leg4')
sideToSide4_euler = getEuler('sideToSide4')
tibia4_euler = getEuler('tibia4')
toe4_euler = getEuler('toe4')

leg5_euler = getEuler('leg5')
sideToSide5_euler = getEuler('sideToSide5')
tibia5_euler = getEuler('tibia5')
toe5_euler = getEuler('toe5')

leg6_euler = getEuler('leg6')
sideToSide6_euler = getEuler('sideToSide6')
tibia6_euler = getEuler('tibia6')
toe6_euler = getEuler('toe6')

leg7_euler = getEuler('leg7')
sideToSide7_euler = getEuler('sideToSide7')
tibia7_euler = getEuler('tibia7')
toe7_euler = getEuler('toe7')

leg8_euler = getEuler('leg8')
sideToSide8_euler = getEuler('sideToSide8')
tibia8_euler = getEuler('tibia8')
toe8_euler = getEuler('toe8')

spider_x_translate_euler = getEuler(baseName + '_bone')


# ******  THIS IS A VERY SPECIAL FUNCTION FOR SIDE LEGS *******
# See http://mathworld.wolfram.com/TriangleWave.html
# .6366 IS  2/PI    MIN = -1  MAX = +1    fabs is subtracted to get a flat line  at zero during only half
# of the cycle, keeping the spider's feet on the floor for half a cycle.
#    "((.6366*asin(sin(radians(7.07*frame)))+ fabs((.6366*asin(sin(radians(7.07*frame)))))))*.2+.4"
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# Drivers  equation(euler, fn="0" axis=0)  # axis 0=x 1=y 2=z
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
bpy.ops.object.mode_set(mode='POSE')

# Equation for bone joints, with euler transform
def equation(euler, fn="0", axis=0, movementType='rotation_euler'):
    edriver = euler.driver_add(movementType, axis)
    edriver.driver.type = 'SCRIPTED'
    edriver.driver.expression = fn
    return edriver



# LEG 1 Movement %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Up-Down motion -****** SEE NOTE ABOVE *******
fn = "(((.6366*asin(sin(radians(7.07*frame)))*.2 + (fabs((.6366*asin(sin(radians(7.07*frame)))))))*.2)+.22)"
leg1Driver = equation(leg1_euler, fn, 0)

fn = "-(asin(sin(radians(7.07 * frame))) * .6)/3.14 - .66"  # Femur Side to side motion  
sideToSide1Driver = equation(sideToSide1_euler, fn, 1)  # Femur Side to side motion

# Tibia Up - Down motion
fn = "-(asin(sin(radians(7.07 * frame))) * .8)/3.14 - 1.1"  # Tibia Up - Down motion
tibia1Driver = equation(tibia1_euler, fn, 0)   # Tibia Up-down motion

# Toe rotational position
fn = "(asin(sin(radians(7.07 * frame))) * .7)/3.14 + .8"  # Toe rotational position
toe1Driver = equation(toe1_euler, fn, 0)  # Toe position
# End LEG 1 Movement %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# LEG 2 Movement %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
fn = "((.6366*asin(sin(radians(7.07*frame)))) + (fabs(.6366*asin(sin(radians(7.07*frame))))))*.16+.28"
leg2Driver = equation(leg2_euler, fn, 0)  # Up-Down motion -****** SEE NOTE ABOVE *******

# Side to side motion
fn = "(asin(sin(radians(7.07 * frame))) * 1.3)/3.14 + .5"  # Side to side Femur
sideToSide2Driver = equation(sideToSide2_euler, fn, 1)  # Femur Side to side motion

fn = "(asin(sin(radians(7.07 * frame))) * .2)/3.14 - 1.1"  # Up - Down Tibia
tibia2Driver = equation(tibia2_euler, fn, 0)   # Tibia Up-down motion

fn = "-(asin(sin(radians(7.07 * frame))) * .4)/3.14 + .7"  # foot rotation
toe2Driver = equation(toe2_euler, fn, 0)  # Foot rotational position
# End LEG 2 Movement %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%



#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# LEG 3 Movement %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Femur Up-Down motion -****** SEE NOTE ABOVE *******
fn = "(((.6366*asin(sin(radians(7.07*frame)))*.2 + (fabs((.6366*asin(sin(radians(7.07*frame)))))))*.2)+.22)"
leg3Driver = equation(leg3_euler, fn, 0)  # Up-Down motion -****** SEE NOTE ABOVE *******

# Femur Side to side motion
fn = "-(asin(sin(radians(7.07 * frame))) * 1.8)/3.14 - .66" 
sideToSide3Driver = equation(sideToSide3_euler, fn, 1)  # Femur Side to side motion

# Tibia Up - Down motion
fn = "(asin(sin(radians(7.07 * frame))) * .8)/3.14 - 1.02"  # Tibia Up - Down motion
tibia3Driver = equation(tibia3_euler, fn, 0)   # Tibia Up-down motion

# Toe rotational position
fn = "-(asin(sin(radians(7.07 * frame))) * 1)/3.14 + .6"  # Toe rotational position
toe3Driver = equation(toe3_euler, fn, 0)  # Toe position
# End LEG 3 Movement %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%



#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# LEG 4 Movement %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
fn = "(asin(sin(radians(7.07 * frame))) * 1.3)/3.14 + .28"
leg4Driver = equation(leg4_euler, fn, 0)

fn = "-(asin(sin(radians(7.07 * frame))) * 2.4)/3.14 - 1.14"  # Tibia Up - Down motion
tibia4Driver = equation(tibia4_euler, fn, 0)

fn = "(asin(sin(radians(7.07 * frame))) * .88)/3.14 + .8"    # Toe rotational position
toe4Driver = equation(toe4_euler, fn, 0)

bpy.context.object.pose.bones["leg4"].rotation_euler[2] = .34
# End LEG 4 Movement %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%




#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# LEG 5 Movement %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
fn = "-(asin(sin(radians(7.07 * frame))) * 1.3)/3.14 + .28"
leg5Driver = equation(leg5_euler, fn, 0)

fn = "(asin(sin(radians(7.07 * frame))) * 2.4)/3.14 - 1.14"   # Tibia Up - Down motion
tibia5Driver = equation(tibia5_euler, fn, 0)

fn = "-(asin(sin(radians(7.07 * frame))) * .88)/3.14 + .8"     # Toe rotational position
toe5Driver = equation(toe5_euler, fn, 0)

bpy.context.object.pose.bones["leg5"].rotation_euler[2] = -.34
# End LEG 5 Movement %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# LEG 6 Movement %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
fn = "(((.6366*asin(sin(radians(7.07*frame)))*.2 + (fabs((.6366*asin(sin(radians(7.07*frame)))))))*.2)+.22)"
leg6Driver = equation(leg6_euler, fn, 0)  # Up-Down motion -****** SEE NOTE ABOVE *******

# Side to side motion
fn = "(asin(sin(radians(7.07 * frame))) * 1.8)/3.14 + .66"  # Side to side Femur
sideToSide6Driver = equation(sideToSide6_euler, fn, 1)  # Femur Side to side motion

fn = "(asin(sin(radians(7.07 * frame))) * .8)/3.14 - 1.02"  # Tibia Up - Down motion
tibia6Driver = equation(tibia6_euler, fn, 0)   # Tibia Up-down motion

fn = "(asin(sin(radians(7.07 * frame))) * .3)/3.14 + .7"  # foot rotation
toe6Driver = equation(toe6_euler, fn, 0)  # Foot rotational position
# End LEG 6 Movement %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%




#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# LEG 7 Movement %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
fn = "((.6366*asin(sin(radians(7.07*frame)))) + (fabs(.6366*asin(sin(radians(7.07*frame))))))*.16+.28"
leg7Driver = equation(leg7_euler, fn, 0)  # Up-Down motion -****** SEE NOTE ABOVE *******

# Side to side motion
fn = "-(asin(sin(radians(7.07 * frame))) * 1.8)/3.14 - .66"  # Side to side Femur
sideToSide7Driver = equation(sideToSide7_euler, fn, 1)  # Femur Side to side motion

fn = "(asin(sin(radians(7.07 * frame))) * .2)/3.14 - 1.1"  # Up - Down Tibia
tibia7Driver = equation(tibia7_euler, fn, 0)   # Tibia Up-down motion

fn = "-(asin(sin(radians(7.07 * frame))) * .4)/3.14 + .7"  # foot rotation
toe7Driver = equation(toe7_euler, fn, 0)  # Foot rotational position
# End LEG 7 Movement %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%




#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# LEG 8 Movement %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
fn = "(((.6366*asin(sin(radians(7.07*frame)))*.2 + (fabs((.6366*asin(sin(radians(7.07*frame)))))))*.2)+.22)"
leg8Driver = equation(leg8_euler, fn, 0)  # Up-Down motion -****** SEE NOTE ABOVE *******

# Side to side motion
fn = "(asin(sin(radians(7.07 * frame))) * .8)/3.14 + .4"  # Femur Side to side motion
sideToSide8Driver = equation(sideToSide8_euler, fn, 1)  # Femur Side to side motion

fn = "-(asin(sin(radians(7.07 * frame))) * .8)/3.14 - 1.02"  # Tibia Up - Down motion
tibia8Driver = equation(tibia8_euler, fn, 0)   # Tibia Up-down motion

fn = "(asin(sin(radians(7.07 * frame))) * 1)/3.14 + .6"
toe8Driver = equation(toe8_euler, fn, 0)  # Foot rotational position
# End LEG 8 Movement %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%



# Move spider on play button click
fn = "frame * .5"
equation(spider_x_translate_euler, fn, 0, 'location')



'''
# Add Plane for checking accuracy of leg movement
bpy.ops.mesh.primitive_plane_add(radius=1, view_align=False, enter_editmode=False, location=(0.0, 0.0, 0.0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
bpy.ops.transform.resize(value=(3.89046, 3.89046, 3.89046), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
'''

bpy.ops.object.mode_set(mode='OBJECT')


# at.show_axes = True
