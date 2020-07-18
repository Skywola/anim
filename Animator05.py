# Important notes for programmers:  You will find deliberate misspellings
# in comments, for example, you may see something like "biiped", with a 
# doubled vowel.  That has a purpose.  When you are troubleshooting via
# a search, you do not want to find or count comments, you want to see
# strictly what the code is doing, so that is the purpose of the misspelling.

import bpy, math
from bpy.types import Panel, Menu
from rna_prop_ui import PropertyPanel
from bpy.props import FloatProperty, BoolProperty, StringProperty
context = bpy.context
import mathutils

sin = math.sin; cos = math.cos; tan = math.tan
asin = math.asin; acos = math.acos; atan = math.atan
fmod = math.fmod; ceil = math.ceil; floor = math.floor
radians = math.radians
cwmPanel = bpy.context.window_manager # cwmPanel PanelProperty
genProp = bpy.types.WindowManager # genProp General Wm Property
#Vector = mathutils.Vector

# This is the magic fn for troubleshooting only
def getTypeAndString(elem):
    print("Type = ", type(elem))
    print(">>>>>>>",elem,"<<<<<<<")
    print(">>>>>>>",elem,"<<<<<<<")
    print(">>>>>>>",elem,"<<<<<<<")

# Checks based on selected objects.  This list would need to be
# updated if a new character type is added.
def characterExists():
    charTypes = ["rgbiped","rgcentaur","rgquadruped","rgbird","rgadWings"]
    for character in bpy.context.selected_objects:
        if(character.name[:-2] in charTypes):
            return True
    return False

# Get name from whatever bone is selected in whatever mode
# Important to use this fn to detect which character is selected
# this also runs up the tree if a non-root bone is selected
def getSelectedCharacterName():
    obj = bpy.context.object
    if(characterExists()):
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        return obj.name
    if(obj.parent):  # If user is not in OBJECT MODE, search 
        parent = obj.parent  # up the tree to the root bone.
        if(parent.name.startswith("rg")): # TODO should use character type list
            obj.select_set(False)
            bpy.context.view_layer.objects.active = parent
            parent.select_set(True)
            return obj.name
    return 0

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# genProp COMMON PROPERTIES
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
genProp.toggleArmAction = BoolProperty(name="toggleArmAction", default=True)
genProp.toggleLegAction = BoolProperty(name="toggleLegAction", default=True)
#Set to Zero at frame 0, otherwise a one
genProp.str_0AtFrame0 = StringProperty(name="str_0AtFrame0", default="*(frame * (1/(frame+.0001)))")
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# END: genProp COMMON PROPERTIES
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# BIPED FUNCTIONS with update= PROPERTIES
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def update(self, context):
    bpy.ops.object.mode_set(mode='POSE')
    bpy.context.scene.frame_current = 1
    bpy.ops.object.mode_set(mode='OBJECT')

def setDirection(self, context):
    name = getSelectedCharacterName()
    ob = bpy.data.objects.get(name)
    if(hasattr(bpy.types.WindowManager, "direction")):
        direction = math.radians(cwmPanel.direction)
    bpy.data.objects[name].rotation_euler.z = direction

def setSwayLR(self, context): # left-right sway movement
    fn = "-(asin(clock())* " + str(cwmPanel.Sway_LR) + "*.02)"
    setDriver(getEuler('bBackJ1'), fn, 2, 'rotation_euler')

def setSwayFB(self, context):  # forward - backward sway movement
    fn = "-(asin(" + 'clock()' + ")* " + str(cwmPanel.Sway_FB) + "*.01)"
    setDriver(getEuler('bBackJ1'), fn, 0, 'rotation_euler')

def setBounce(self, context):  # Bounce
    ob = bpy.context.object
    fn = "-(asin(clock())*" + str(cwmPanel.bounce) + "*.01)"
    setAxisDriver(getEuler(ob.name + '_bone'), fn, 2, 'location')

def setShoulder(self, context):
    Shoulder_Rotation = str(cwmPanel.Shoulder_Rotation*.04)
    fn = "(asin(clock()) * " + Shoulder_Rotation + ")/3.14"
    setDriver(getEuler('bBackJ4'), fn, 1)
    # Compensate for rotation by r0tating neck and head in opposite directiion, in three parts
    fn = "-(asin(clock()) * " + Shoulder_Rotation + "/3)/3.14"
    setDriver(getEuler('neckJ2'), fn, 1)
    setDriver(getEuler('neckJ3'), fn, 1)
    setDriver(getEuler('neckJ4'), fn, 1)
    # Shoulder up - down movement
    Shoulder_UD = str(cwmPanel.Shoulder_UD*.06)
    fn = "-(asin(clock()) * " + Shoulder_UD + ")/3.14"
    setAxisDriver(getEuler('shoulder.L'), fn, 2)
    fn = "-(asin(clock()) * " + Shoulder_UD + ")/3.14"
    setAxisDriver(getEuler('shoulder.R'), fn, 2)

def unsetWalk(self, context):
    for b in bpy.data.objects[getSelectedCharacterName()].pose.bones:
        b.driver_remove('rotation_euler', -1)

def setRun(self, context):
    unsetWalk(self, context)
    #genProp.cycle = 12    #genProp.Hip_Rotate = 2.0
    #genProp.Sway_LR = 2.0   
    #genProp.Sway_FB = 4.0
    #genProp.bounce = 1.2
    #genProp.Hip_UD = 2.0 
    #genProp.Shoulder_Rotation = 8.0 
    #genProp.Shoulder_UD = 4.0 
    #genProp.Arm_Rotation = 3.0 
    #genProp.rotateRange = 2.6
    #genProp.tibiaJ1RP = .6 
    #genProp.tibiaJ1RR = 1.0
    #genProp.ankleRP = 0.0
    #genProp.toesRP = -.1
    #etCharacterWalk(self, context)
    bpy.ops.object.mode_set(mode='OBJECT')
    #
def unSetLegRotation(self, context):
    name = getSelectedCharacterName()
    undo = bpy.data.objects[name].pose.bones['femurJ1.L']
    undo.driver_remove('rotation_euler', -1)
    undo = bpy.data.objects[name].pose.bones['femurJ1.R']
    undo.driver_remove('rotation_euler', -1)
    undo = bpy.data.objects[name].pose.bones['tibiaJ1.L']
    undo.driver_remove('rotation_euler', -1)
    undo = bpy.data.objects[name].pose.bones['tibiaJ1.R']
    undo.driver_remove('rotation_euler', -1)
    undo = bpy.data.objects[name].pose.bones['ankle.L']
    undo.driver_remove('rotation_euler', -1)
    undo = bpy.data.objects[name].pose.bones['ankle.R']
    undo.driver_remove('rotation_euler', -1)
    undo = bpy.data.objects[name].pose.bones['toe.L']
    undo.driver_remove('rotation_euler', -1)
    undo = bpy.data.objects[name].pose.bones['toe.R']
    undo.driver_remove('rotation_euler', -1)
    #
# This is for restoring advanced control defaults for each bone in the leg: 
# RP = Rotate Position   # RR = Rotate Range
def revertAdvancedControls(self, context):
    #genProp.rotatePosition = 0.1  # TODO
    genProp.rotateRange = 1.0
    genProp.tibiaJ1RP = 0.0
    genProp.tibiaJ1RR = 1.0
    genProp.ankleRP = 0.0
    genProp.ankleRR = 1.0
    genProp.toesRP = 0.0
    genProp.toesRR = 1.0
    #etCharacterWalk()
    #
def unSetArmRotation(self, context):
    name = getSelectedCharacterName()
    undo = bpy.data.objects[name].pose.bones['armJ1.L']
    undo.driver_remove('rotation_euler', -1)
    undo = bpy.data.objects[name].pose.bones['armJ1.R']
    undo.driver_remove('rotation_euler', -1)
    undo = bpy.data.objects[name].pose.bones['armJ3.L']
    undo.driver_remove('rotation_euler', -1)
    undo = bpy.data.objects[name].pose.bones['armJ3.R']
    undo.driver_remove('rotation_euler', -1)
    undo = bpy.data.objects[name].pose.bones['bBackJ4']
    undo.driver_remove('rotation_euler', -1)

def setLegArch(self, context):
    fn = cwmPanel.Leg_Arch * .02  # Leg Arch
    setAxisDriver(getEuler('femurJ1.L'), str(-fn), 1)
    setAxisDriver(getEuler('femurJ1.R'), str(fn), 1)

def setArms(self, context):  # TODO This roars slider
    name = getSelectedCharacterName()
    UD = math.radians(cwmPanel.Arms_UD)
    rotate(name, 'armJ1.L', UD, 2)
    rotate(name, 'armJ1.R', -UD, 2)
    bpy.context.object.data.bones['armJ1.L'].select  = True
    bpy.context.object.data.bones['armJ1.R'].select  = True
    #bpy.ops.object.mode_set(mode='POSE')

def setArmTwistL(self, context):
    name = getSelectedCharacterName()
    LArm_Twist = cwmPanel.LArm_Twist  * -.1
    rotate(name, 'armJ2.L', LArm_Twist, 1)
    rotate(name, 'armJ3.L', LArm_Twist, 1)
    rotate(name, 'armJ4.L', LArm_Twist, 1)
    rotate(name, 'armJ5.L', LArm_Twist, 1)
    bpy.context.object.data.bones['armJ2.L'].select  = True
    bpy.context.object.data.bones['armJ3.L'].select  = True
    bpy.context.object.data.bones['armJ4.L'].select  = True
    bpy.context.object.data.bones['armJ5.L'].select  = True
    bpy.ops.object.mode_set(mode='POSE')

def setArmTwistR(self, context):
    name = getSelectedCharacterName()
    RArm_Twist = cwmPanel.RArm_Twist   * .1
    rotate(name, 'armJ2.R', RArm_Twist, 1)
    rotate(name, 'armJ3.R', RArm_Twist, 1)
    rotate(name, 'armJ4.R', RArm_Twist, 1)
    rotate(name, 'armJ5.R', RArm_Twist, 1)
    bpy.context.object.data.bones['armJ2.R'].select  = True
    bpy.context.object.data.bones['armJ3.R'].select  = True
    bpy.context.object.data.bones['armJ4.R'].select  = True
    bpy.context.object.data.bones['armJ5.R'].select  = True
    bpy.ops.object.mode_set(mode='POSE')

def setArmRotation(self, context):
    Arm_Rotation = '3.0'
    if(hasattr(cwmPanel, "Arm_Rotation")):
        Arm_Rotation = str(cwmPanel.Arm_Rotation * .2)
    # Arms rotation
    fn = "-(asin(" + 'clock()' + ") * " + Arm_Rotation + ")/3.14"
    armJLDriver = setAxisDriver(getEuler('armJ1.L'), fn, 1)
    fn = "-(asin(" + 'clock()' + ") * " + Arm_Rotation + ")/3.14"
    armJRDriver = setAxisDriver(getEuler('armJ1.R'), fn, 1)
    # Elbows
    fn = "-((asin(" + 'clock()' + ") * " + Arm_Rotation + ")/3.14 + .3) * (frame*(1/(frame+.0001)))"
    radiusLDriver = setAxisDriver(getEuler('armJ3.L'), fn, 2)
    fn = "-((asin(" + 'clock()' + ") * " + Arm_Rotation + ")/3.14 - .3) * (frame*(1/(frame+.0001)))"
    radiusRDriver = setAxisDriver(getEuler('armJ3.R'), fn, 2)
    bpy.ops.object.mode_set(mode='OBJECT')

# Rotate the easy way
def rotate(bipedStrName, str_bone_name, rad=0, axis=0):
    bpy.ops.object.mode_set(mode='POSE')
    ob = bpy.context.object
    euler = ob.pose.bones[str_bone_name]
    euler.rotation_mode = 'XYZ'
    bpy.data.objects[bipedStrName].pose.bones[str_bone_name].rotation_euler[axis] = rad

def LHandOpenClose(self, context): # Light hand open - close
    name = getSelectedCharacterName()
    LHand_OC = cwmPanel.LHand_OC   * .1
    for i in range(1, 4):
        rotate(name, 'indexJ' + str(i) + '.L', LHand_OC, 2)
        rotate(name, 'midJ' + str(i) + '.L', LHand_OC, 2)
        rotate(name, 'ringJ' + str(i) + '.L', LHand_OC, 2)
        rotate(name, 'pinkyJ' + str(i) + '.L', LHand_OC, 2)
    for i in range(1, 4):
        bpy.context.object.data.bones['indexJ' + str(i) + '.L'].select  = True       
        bpy.context.object.data.bones['midJ' + str(i) + '.L'].select  = True
        bpy.context.object.data.bones['ringJ' + str(i) + '.L'].select  = True
        bpy.context.object.data.bones['pinkyJ' + str(i) + '.L'].select  = True
    bpy.ops.object.mode_set(mode='POSE')
    
def LHandSpread(self, context): # Light hand spread
    name = getSelectedCharacterName()
    LHand_Spread = cwmPanel.LHand_Spread - 30
    index = (LHand_Spread) * -.04 - .8 # Light hand spread
    rotate(name, 'indexJ1.L', index, 0)
    ring = (LHand_Spread) * .017 + .36 # Light hand spread
    rotate(name, 'ringJ1.L', ring, 0)
    pinky = (LHand_Spread) * .052 + 1.0 # Light hand spread
    rotate(name, 'pinkyJ1.L', pinky, 0)
    for i in range(1, 4):
        bpy.context.object.data.bones['indexJ' + str(i) + '.L'].select  = True       
        bpy.context.object.data.bones['midJ' + str(i) + '.L'].select  = True
        bpy.context.object.data.bones['ringJ' + str(i) + '.L'].select  = True
        bpy.context.object.data.bones['pinkyJ' + str(i) + '.L'].select  = True
    bpy.ops.object.mode_set(mode='POSE')

def RHandOpenClose(self, context): # Right hand open - close
    name = getSelectedCharacterName()
    RHand_OC = cwmPanel.RHand_OC   * -.1
    for i in range(1, 4):
        rotate(name, 'indexJ' + str(i) + '.R', RHand_OC, 2)
        rotate(name, 'midJ' + str(i) + '.R', RHand_OC, 2)
        rotate(name, 'ringJ' + str(i) + '.R', RHand_OC, 2)
        rotate(name, 'pinkyJ' + str(i) + '.R', RHand_OC, 2)
    for i in range(1, 4):
        bpy.context.object.data.bones['indexJ' + str(i) + '.R'].select  = True       
        bpy.context.object.data.bones['midJ' + str(i) + '.R'].select  = True
        bpy.context.object.data.bones['ringJ' + str(i) + '.R'].select  = True
        bpy.context.object.data.bones['pinkyJ' + str(i) + '.R'].select  = True
    bpy.ops.object.mode_set(mode='POSE')
    
def RHandSpread(self, context): # Right hand spread
    name = getSelectedCharacterName()
    RHand_Spread = cwmPanel.RHand_Spread - 30
    index = (RHand_Spread) * -.04 - .8 # Right hand spread
    rotate(name, 'indexJ1.R', index, 0)
    ring = (RHand_Spread) * .017 + .36 # Right hand spread
    rotate(name, 'ringJ1.R', ring, 0)
    pinky = (RHand_Spread) * .052 + 1.0 # Right hand spread
    rotate(name, 'pinkyJ1.R', pinky, 0)
    for i in range(1, 4):
        bpy.context.object.data.bones['indexJ' + str(i) + '.R'].select  = True       
        bpy.context.object.data.bones['midJ' + str(i) + '.R'].select  = True
        bpy.context.object.data.bones['ringJ' + str(i) + '.R'].select  = True
        bpy.context.object.data.bones['pinkyJ' + str(i) + '.R'].select  = True
    bpy.ops.object.mode_set(mode='POSE')

def setHead(self, context):
    # Up - Down turn motion 
    if(hasattr(cwmPanel, "Head_UD")):
        Head_UD = str(cwmPanel.Head_UD * .06)
    fn = str(Head_UD)
    setAxisDriver(getEuler('neckJ2'), fn, 0)
    setAxisDriver(getEuler('neckJ3'), fn, 0)
    setAxisDriver(getEuler('neckJ4'), fn, 0)
    # Sideways motion 
    if(hasattr(cwmPanel, "Head_LR")):
        Head_LR = str(cwmPanel.Head_LR)
    fn = str(Head_LR) + "* -.1"  
    setAxisDriver(getEuler('neckJ2'), fn, 2)
    setAxisDriver(getEuler('neckJ3'), fn, 2)
    setAxisDriver(getEuler('neckJ4'), fn, 2)
    # head turn
    if(hasattr(cwmPanel, "Head_Turn")):
        Head_Turn = str(cwmPanel.Head_Turn * .06)
    fn = "-(asin(" + 'clock()' + ") * .2)/3.14 + " + Head_Turn
    neckJ2Driver = setAxisDriver(getEuler('neckJ2'), fn, 1)
    neckJ3Driver = setAxisDriver(getEuler('neckJ3'), fn, 1)
    neckJ4Driver = setAxisDriver(getEuler('neckJ4'), fn, 1)
    bpy.ops.object.mode_set(mode='OBJECT')

def setJaw(self, context): # Jaw open - close
    name = getSelectedCharacterName()
    Jaw_OC = cwmPanel.Jaw_OC * -.1
    rotate(name, 'jaw', Jaw_OC, 0)
    bpy.context.object.data.bones['jaw'].select  = True
    bpy.ops.object.mode_set(mode='POSE')

# If centered at rear joint, parented, can be used  for eye movements
def setEye(self, context):
    name = getSelectedCharacterName()
    Eye_LR = cwmPanel.Eye_LR * .1    # Left - Right turn motion 
    rotate(name, 'eye.L', Eye_LR, 2)
    rotate(name, 'eye.R', Eye_LR, 2)
    #
    Eye_UD = cwmPanel.Eye_UD * .1   # Eye up - down
    rotate(name, 'eye.L', Eye_UD, 0)
    rotate(name, 'eye.R', Eye_UD, 0)
    bpy.context.object.data.bones['eye.L'].select  = True
    bpy.context.object.data.bones['eye.R'].select  = True
    bpy.ops.object.mode_set(mode='POSE')

def setCharacterWalk(self, context):
    ob = bpy.context.object
    bpy.ops.object.mode_set(mode='OBJECT')
    name = getSelectedCharacterName()
    #
    z = radians(bpy.data.objects[name].pose.bones[name + '_bone'].rotation_euler.z)
    fnx = "setHorizontalSpeed() * cos(" + str(z) + ")"
    setAxisDriver(getEuler(name+'_bone'), fnx, 1, 'location')
    fny = "setHorizontalSpeed() * sin(" + str(z) + ")"
    setAxisDriver(getEuler(name+'_bone'), fny, 0, 'location')
    #
    # KEY: RP = Rotate Position  RR = Rotate Range   
    femurJ1PP = "0.0" # Static pose position
    #
    RP = "+" + str(cwmPanel.rotatePosition) + " " # Default = .1 which is added
    RR = str(cwmPanel.rotateRange) + " * "     # Default = 1  which is multiplied
    ZeroAtFrame0 = getSpecialString(genProp.str_0AtFrame0)
    fnL = RR + "(" + 'clock()' + RP + ")*" + ZeroAtFrame0
    setAxisDriver(getEuler('femurJ1.L'), fnL, 0, 'rotation_euler')
    fnR = RR + "(-1*" + 'clock()' + RP + ")*" + ZeroAtFrame0
    setAxisDriver(getEuler('femurJ1.R'), fnR, 0, 'rotation_euler')
    # tibiaJ1
    RPa = "+" + str(cwmPanel.rotatePosition-.4) + " " # Adjusted
    fnL = RR + "(" + 'clock()' + RPa + ")*" + ZeroAtFrame0
    setAxisDriver(getEuler('tibiaJ1.L'), fnL, 0, 'rotation_euler')
    fnR = RR + "(-1*" + 'clock()' + RPa + ")*" + ZeroAtFrame0
    setAxisDriver(getEuler('tibiaJ1.R'), fnR, 0, 'rotation_euler')
    # Ankles
    fnL = RR + "(-1*" + 'clock()' + RP + ")*" + ZeroAtFrame0
    setAxisDriver(getEuler('ankle.L'), fnL, 0, 'rotation_euler')
    fnR = RR + "(" + 'clock()' + RP + ")*" + ZeroAtFrame0
    setAxisDriver(getEuler('ankle.R'), fnR, 0, 'rotation_euler')
    # Toes
    fnL = RR + "(-1*" + 'clock()' + RP + ")*" + ZeroAtFrame0
    setAxisDriver(getEuler('toe.L'), fnL, 0, 'rotation_euler')
    fnR = RR + "(" + 'clock()' + RP + ")*" + ZeroAtFrame0
    setAxisDriver(getEuler('toe.R'), fnR, 0, 'rotation_euler')
    #
    # Upper Back
    BR = .6  # Back Rotate
    RRa = str(cwmPanel.rotateRange*BR) + "*" # Adjusted
    fn = RRa + "(" + 'clock()' + RP + ")*" + ZeroAtFrame0
    bBackJ4Driver = setDriver(getEuler('bBackJ4'), fn, 1, 'rotation_euler')
    # Compensate for shoulder r0tate by rotating neck and head in opposite directiion, in three parts
    #RR = "*" + str(.13)
    NR = -BR/3.8  # Neck Rotate is 1/3 (3 joints) with deviation
    RRa = str(cwmPanel.rotateRange * NR) + "*" # Adjusted
    fn = RRa + "(clock())*" + ZeroAtFrame0
    neckJ2Driver = setDriver(getEuler('neckJ2'), fn, 1, 'rotation_euler')
    neckJ3Driver = setDriver(getEuler('neckJ3'), fn, 1,'rotation_euler')
    neckJ4Driver = setDriver(getEuler('neckJ4'), fn, 1, 'rotation_euler')
    # Arms rotation
    Arm_Rotation = str(cwmPanel.Arm_Rotation * .2)
    RR = "*" + str(1)
    fnL = "(" + 'clock()' + RR + ")*" + ZeroAtFrame0
    setAxisDriver(getEuler('armJ1.L'), fnL, 0)
    fnR = "(-1*" + 'clock()' + RR + ")*" + ZeroAtFrame0
    setAxisDriver(getEuler('armJ1.R'), fnR, 0)
    # Elbows
    RP = "-" + str(1.4)
    RR = "*" + str(.2)
    fnL = "(" + 'clock()' + RP + RR + ")*" + ZeroAtFrame0
    setAxisDriver(getEuler('armJ3.L'), fnL, 0)
    fnR = "(-1*" + 'clock()' + RP + RR + ")*" + ZeroAtFrame0
    setAxisDriver(getEuler('armJ3.R'), fnR, 0)
    #
    bpy.context.object.pose.bones["armJ1.L"].rotation_euler[2] = 1.57
    bpy.context.object.pose.bones["armJ1.R"].rotation_euler[2] = -1.57
    ob = bpy.data.objects.get(name)        
    ob.select_set(True)
    bpy.context.scene.frame_set(1)
    bpy.ops.object.mode_set(mode='OBJECT')

def setHip(self, context):
    # Hip sway
    if(hasattr(cwmPanel, "Hip_Sway")):
        Hip_Sway = str(cwmPanel.Hip_Sway*.1)
    fn = "(asin(clock()) * " + Hip_Sway + ")/3.14"
    setAxisDriver(getEuler('hipC'), fn, 2) # was 0
    # Pelvis / Hip rotation    
    if(hasattr(cwmPanel, "Hip_Rotate")):
        Hip_Rotate = str(cwmPanel.Hip_Rotate*.1)
    fn = "(asin(clock()) * " + Hip_Rotate + ")/3.14"
    setAxisDriver(getEuler('hipC'), fn, 1)
    # hip up - down movement
    if(hasattr(cwmPanel, "Hip_UD")):
        Hip_UD = str(cwmPanel.Hip_UD*.04)
    fn = "(asin(clock()) * " + Hip_UD + ")/3.14"
    setAxisDriver(getEuler('hip.L'), fn, 2)
    setAxisDriver(getEuler('hip.R'), fn, 2)
    # femurJ1.L
    fn = "(asin(clock()) * " + Hip_UD + ")/-3.14"
    setAxisDriver(getEuler('femurJ1.L'), fn, 2)
    setAxisDriver(getEuler('femurJ1.R'), fn, 2)
    bpy.ops.object.mode_set(mode='OBJECT')
    ob = bpy.data.objects.get(getSelectedCharacterName())
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# CHARACTER PROPERTIES (with update= ), THEIR FUNCTIONS MUST PRECEED THEM
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# These ARE required, despite appearing rarely with the genProp prefix
# PopUp Window Properties declared strictly for class WM_OT_controol window
genProp.speed = FloatProperty(update=update, default=0.0)
genProp.cycle = FloatProperty(update=update, default=1.0)
genProp.direction = FloatProperty(update=setDirection, default=0.0)
genProp.X_Location = FloatProperty(update=update, default=0.0)
genProp.Y_Location = FloatProperty(update=update, default=0.0)
genProp.Z_Location = FloatProperty(update=update, default=1.18)
genProp.Sway_LR = FloatProperty(update=setSwayLR, default=1.0)
genProp.Sway_FB = FloatProperty(update=setSwayFB, default=1.0)
genProp.bounce = FloatProperty(update=setBounce, default=1.2)
genProp.Shoulder_Rotation = FloatProperty(update=setBounce, default=1.2)
genProp.Shoulder_UD = FloatProperty(update=setBounce, default=1.0)
genProp.Leg_Spread = FloatProperty(update=setHip, default=0.0)
#genProp.skate = FloatProperty(update=setSkate, default=0.0)#
genProp.Hip_Sway = FloatProperty(update=setHip, default=0.0)
genProp.Hip_Rotate = FloatProperty(update=setHip, default=0.0)
genProp.Hip_UD = FloatProperty(update=setHip, default=2.0)
genProp.Leg_Arch = FloatProperty(update=setLegArch, default=0.0)
# End  PopUp Window Properties declared strictly for class WM_OT_controol window
#
# Sliders?
genProp.Arms_UD = FloatProperty(update=setArms, name="Arms_UD", default=0.0)
genProp.LArm_Twist = FloatProperty(update= setArmTwistL, name="LArm_Twist", default=0.0)
genProp.RArm_Twist = FloatProperty(update= setArmTwistR, name="RArm_Twist", default=0.0)
genProp.Arm_Rotation = FloatProperty(update=setArmRotation, name="Arm_Rotation", default=3.0)
genProp.LHand_OC = FloatProperty(update=LHandOpenClose, name="LHand_OC", default=0.0)
genProp.LHand_Spread = FloatProperty(update=LHandSpread, name="LHand_Spread", default=0.0)
genProp.RHand_OC = FloatProperty(update=RHandOpenClose, name="RHand_OC", default=0.0)
genProp.RHand_Spread = FloatProperty(update=RHandSpread, name="RHand_Spread", default=0.0)
genProp.Head_UD = FloatProperty(update=setHead, name="Head_UD", default=0.0)
genProp.Head_LR = FloatProperty(update=setHead, name="Head_LR", default=0.0)
genProp.Head_Turn = FloatProperty(update=setHead, name="Head_Turn", default=0.0)
genProp.Jaw_OC = FloatProperty(update=setJaw, name="Jaw_OC", default=0.0)
genProp.Eye_LR = FloatProperty(update=setEye, name="Eye_LR", default=0.0)
genProp.Eye_UD = FloatProperty(update=setEye, name="Eye_UD", default=0.0)
#
genProp.rotatePosition = FloatProperty(update=setCharacterWalk, default=0.1)
genProp.rotateRange = FloatProperty(update=setCharacterWalk, default=1.0)
genProp.tibiaJ1RP = FloatProperty(update=setCharacterWalk, default=0.0)
genProp.tibiaJ1RR = FloatProperty(update=setCharacterWalk, default=1.0)
genProp.ankleRP = FloatProperty(update=setCharacterWalk, default=0.0)
genProp.ankleRR = FloatProperty(update=setCharacterWalk, default=1.0)
genProp.toesRP = FloatProperty(update=setCharacterWalk, default=-0.0)
genProp.toesRR = FloatProperty(update=setCharacterWalk, default=1.0)
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# END: CHARACTER PROPERTIES (with update= ) AND THEIR FUNCTIONS PRECEEDING THEM
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# PANELS CLASS
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class Pose_Btn(bpy.types.Operator):
    bl_idname = "object.pose_btn"
    bl_label = "Pose Character"
    bl_description = "Pose Character"
    bl_options = {"REGISTER", "UNDO"}
    hidden = False
    def execute(self, context):
        bpy.ops.screen.animation_cancel(restore_frame=True)
        bpy.context.scene.frame_set(0)
        bpy.ops.object.mode_set(mode='OBJECT')
        return{'FINISHED'}

class Character_Panel_Btn(bpy.types.Operator): 
    # Because this is a floating panel, it is
    # not entered as a standard _P T_ panel
    bl_idname = "object.Character_Panel_Btn"
    bl_label = "Get Character Control Panel"
    bl_description = "Get Character Control Panel"
    bl_options = {"REGISTER", "UNDO"}
    hidden = False
    def execute(self, context):    
        getSelectedCharacterName()
        bpy.ops.object.mode_set(mode='OBJECT')
        return{'FINISHED'}

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# END of Common panel for all characters and appendages.
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# |
class Character(bpy.types.Operator):
    bl_idname = "object.character"
    bl_label = "characterPanel"
    bl_description = "character"
    bl_options = {"REGISTER", "UNDO"}
    #
    show_in_front = True  # bpy.data.objects[character.name].show_in_front
    # BEGIN WITH BIPED PARTS
    name = ""
    armature = ""
    armatureName = ""
    x = 0
    y = 0
    z = 0
    n = 0
    #
    rotatePosition: FloatProperty(default=0.1)
    rotateRange: FloatProperty(default=1.0)
    Arm_Rotation: FloatProperty(default=3.0)
    #
    cycle = FloatProperty(update=update, default=1.0)
    speed = FloatProperty(update=update, default=0.0)
    direction = FloatProperty(update=setDirection, default=0.0)
    X_Location = FloatProperty(update=update, default=0.0) # TODO x_axis already exists
    Y_Location = FloatProperty(update=update, default=0.0) # TODO y_axis already exists
    Z_Location = FloatProperty(update=update, default=1.18) # TODO z_axis already exists
    Sway_LR = FloatProperty(update=setSwayLR, default=1.0)
    Sway_FB = FloatProperty(update=setSwayFB, default=1.0)
    bounce = FloatProperty(update=setBounce, default=1.2)
    Shoulder_Rotation = FloatProperty(update=setBounce, default=1.2)
    Shoulder_UD = FloatProperty(update=setBounce, default=1.0)
    Leg_Spread = FloatProperty(update=setHip, default=0.0)
    #skate = FloatProperty(update=setSkate, default=0.0)
    Hip_Sway = FloatProperty(update=setHip, default=0.0)
    Hip_Rotate = FloatProperty(update=setHip, default=0.0)
    Hip_UD = FloatProperty(update=setHip, default=2.0)
    # End  PopUp Window Properties declared strictly for class WM_OT_controol window
    tibiaJ1RP = FloatProperty(update=setCharacterWalk, default=0.0)
    tibiaJ1RR = FloatProperty(update=setCharacterWalk, default=1.0)
    ankleRP = FloatProperty(update=setCharacterWalk, default=0.0)
    ankleRR = FloatProperty(update=setCharacterWalk, default=1.0)
    toesRP = FloatProperty(update=setCharacterWalk, default=-0.0)
    toesRR = FloatProperty(update=setCharacterWalk, default=1.0)
    # Sliders?
    Arms_UD = FloatProperty(update=setArms, default=0.0)
    LArm_Twist = FloatProperty(update= setArmTwistL, default=0.0)
    RArm_Twist = FloatProperty(update= setArmTwistR, default=0.0)
    LHand_OC = FloatProperty(update=LHandOpenClose, default=0.0)
    LHand_Spread = FloatProperty(update=LHandSpread, default=0.0)
    RHand_OC = FloatProperty(update=RHandOpenClose, default=0.0)
    RHand_Spread = FloatProperty(update=RHandSpread, default=0.0)
    Head_UD = FloatProperty(update=setHead, default=0.0)
    Head_LR = FloatProperty(update=setHead, default=0.0)
    Head_Turn = FloatProperty(update=setHead, default=0.0)
    Jaw_OC = FloatProperty(update=setJaw, default=0.0)
    Eye_LR = FloatProperty(update=setEye, default=0.0)
    Eye_UD = FloatProperty(update=setEye, default=0.0)
    #
    V_origin = (0, 0, 0)
    VHead = [0, 0, 0]   # always a zero vector
    VTail = [0, -.3, 0] # default value
    rgRootBone = "root"
    V_angle = (0, 0, 0)
    angle = "angle"
    V_hipC = (0, .1, -.1)
    hipc = "hipc"
    V_next = (0, 0, -.14)
    next = "next"
    V_hip = (.12, 0, 0)
    hipL = "hip.L"
    hipR = "hip.R"
    V_femurJ1 = (0, 0, -.23)
    femurJ1L = "femurJ1.L"
    femurJ1R = "femurJ1.R"
    V_femurJ2 = (0, 0, -.24)
    femurJ2L = "femurJ2.L"
    femurJ2R = "femurJ2.R"
    V_tibiaJ1 = (0, 0, -.2)
    tibiaJ1L = "tibiaJ1.L"
    tibiaJ1R = "tibiaJ1.R"
    V_tibiaJ2 = (0, 0, -.14)
    tibiaJ2L = "tibiaJ2.L"
    tibiaJ2R = "tibiaJ2.R"
    V_ankle = (0, .18, -.06)
    ankleL = "ankle.L"
    ankleR = "ankle.R"
    V_toe = (0, .08, 0)
    toeL = "toe.L"
    toeR = "toe.R"
    #
    V_heel = (0, -.2, -.01)
    heelL = "heel.L"
    heelR = "heel.R"
    #
    V_posterior = (0, -.1, -.04)
    posteriorL = "posterior.L"
    posteriorR = "posterior.R"
    V_posterior1 = (-.12, 0, -.01)
    posterior1L = "posterior1.L"
    posterior1R = "posterior1.R"
    V_posterior2 = (0, 0, -.14)
    posterior2L = "posterior2.L"
    posterior2R = "posterior2.R"
    #
    V_tailBone = (0, 0, -.14)
    tailBone = "tailBone"
    #
    V_bBackJ1 = (0, 0, 0.1)
    bBackJ1 = "bBackJ1"
    V_bBackJ2 = (0, 0, 0.1)
    bBackJ2 = "bBackJ2"
    V_bBackJ3 = (0, 0, 0.14)
    bBackJ3 = "bBackJ3"
    V_bBackJ4 = (0, 0, 0.1)
    bBackJ4 = "bBackJ4"
    V_bBackJ5 = (0, 0, 0.1)
    #
    V_clavicle = (.11, 0, -.02)
    clavicleL = "clavicle.L"
    clavicleR = "clavicle.R"
    V_shoulder = (.19, 0, -.03)
    shoulderL = "shoulder.L"
    shoulderR = "shoulder.R"
    V_armJ1 = (.12, 0, 0)
    armJ1L = "armJ1.L"
    armJ1R = "armJ1.R"
    V_armJ2 = (.14, 0, -.01)
    armJ2L = "armJ2.L"
    armJ2R = "armJ2.R"
    V_armJ3 = (.08, 0, 0)
    armJ3L = "armJ3.L"
    armJ3R = "armJ3.R"
    V_armJ4 = (.1, 0, 0)
    armJ4L = "armJ4.L"
    armJ4R = "armJ4.R"
    V_armJ5 = (.1, 0, 0)
    armJ5L = "armJ5.L"
    armJ5R = "armJ5.R"
    #
    V_wristBase2 = (0.098, .002, -.006)
    wristBase2L = "wristBase2.L"
    wristBase2R = "wristBase2.R"
    V_midJ1 = (.046, 0, 0)
    midJ1L = "midJ1.L"
    midJ1R = "midJ1.R"
    V_midJ2 = (.04, 0, 0)
    midJ2L = "midJ2.L"
    midJ2R = "midJ2.R"
    V_midJ3 = (.02, 0, 0)
    midJ3L = "midJ3.L"
    midJ3R = "midJ3.R"
    #
    V_wristBase1 = (.098, .03, -.006)
    wristBase1L = "wristBase1.L"
    wristBase1R = "wristBase1.R"
    V_indexJ1 = (.032, .011, 0)
    indexJ1L = "indexJ1.L"
    indexJ1R = "indexJ1.R"
    V_indexJ2 = (.024, .01, 0)
    indexJ2L = "indexJ2.L"
    indexJ2R = "indexJ2.R"
    V_indexJ3 = (.02, .008, 0)
    indexJ3L = "indexJ3.L"
    indexJ3R = "indexJ3.R"
    V_wristBase3 = (.098, -.02, -.006)
    wristBase3L = "wristBase3.L"
    wristBase3R = "wristBase3.R"
    V_ringJ1 = (.042, -.01, 0)
    ringJ1L = "ringJ1.L"
    ringJ1R = "ringJ1.R"
    V_ringJ2 = (.032, -.007, 0)
    ringJ2L = "ringJ2.L"
    ringJ2R = "ringJ2.R"
    V_ringJ3 = (.02, -.004, 0)
    ringJ3L = "ringJ3.L"
    ringJ3R = "ringJ3.R"
    V_pinkyBase = (.095, -.046, -.006)
    pinkyBaseL = "pinkyBase.L"
    pinkyBaseR = "pinkyBase.R"
    V_pinkyJ1 = (.024, -.016, 0)
    pinkyJ1L = "pinkyJ1.L"
    pinkyJ1R = "pinkyJ1.R"
    V_pinkyJ2 = (.02, -.012, 0)
    pinkyJ2L = "pinkyJ2.L"
    pinkyJ2R = "pinkyJ2.R"
    V_pinkyJ3 = (.02, -.01, 0)
    pinkyJ3L = "pinkyJ3.L"
    pinkyJ3R = "pinkyJ3.R"
    #
    V_thumbBase = (.002, .008, 0)
    thumbBaseL = "thumbBase.L"
    thumbBaseR = "thumbBase.R"
    V_thumbJ1 = (.038, .044, -0.01)
    thumbJ1L = "thumbJ1.L"
    thumbJ1R = "thumbJ1.R"
    V_thumbJ2 = (.032, .02, -0.006)
    thumbJ2L = "thumbJ2.L"
    thumbJ2R = "thumbJ2.R"
    V_thumbJ3 = (.02, .01, 0)
    thumbJ3L = "thumbJ3.L"
    thumbJ3R = "thumbJ3.R"
    #
    V_neckJ1 = (0, 0, 0.03)
    neckJ1 = "neckJ1"
    V_neckJ2 = (0, 0, 0.03)
    neckJ2 = "neckJ2"
    V_neckJ3 = (0, 0, 0.03)
    neckJ3 = "neckJ3"
    V_neckJ4 = (0, 0, 0.03)
    neckJ4 = "neckJ4"
    Vneck05 = (0, 0, .04)
    neck05 = "neck05"
    Vneck06 = (0, 0, .04)
    neck06 = "neck06"
    V_headBase = (0, 0, 0.09)
    headBase = "headBase"
    VHeadTop = (0, 0.17, .03)
    headTop = "headTop"
    Vcrest = (0, -.1, .08)
    crest = "crest"
    V_eyeLevel = (0, 0, .04)
    eyeLevel = "eyeLevel"
    V_headTop = (0, -.05, 0)
    headTop = "headTop"
    V_headFore = (0, .08, .09)
    headFore = "headFore"
    #
    V_jaw = (0, .026, -.004)
    jaw = "jaw"
    V_jaw1 = (.06, .02, 0)
    jaw1L = "jaw1.L"
    jaw1R = "jaw1.R"
    V_jaw2 = (-.05, .1, 0)
    jaw2L = "jaw2.L"
    jaw2R = "jaw2.R"
    Vjaw3 = (0, 0.109, .053)  # no mirror
    jaw3 = "jaw3"
    Vjaw4 = (0, 0.13, -.028)
    jaw4 = "jaw4"
    Vjaw4 = (0, 0.12, -.026)
    #
    V_baseMouth1 = (0, .026, 0.046)
    baseMouth1 = "baseMouth1"
    V_baseMouth2 = (.06, .02, 0)
    baseMouth2L = "baseMouth2.L"
    baseMouth2R = "baseMouth2.R"
    V_baseMouth3 = (-.05, .11, -.004)
    baseMouth3L = "baseMouth3.L"
    baseMouth3R = "baseMouth3.R"
    #
    V_eyebase = (-.03, 0.1, 0)
    eyebaseL = "eyebase.L"
    eyebaseR = "eyebase.R"
    V_eye = (0, 0.03, 0)
    eyeL = "eye.L"
    eyeR = "eye.R"
    V_noseBase = (0, .138, 0)
    noseBase = "noseBase"
    V_nose = (0, 0.02, -.02)
    nose = "nose"
    #
    V_fixChestFront = (0, .06, -.03)
    fixChestFront = "fixChestFront"
    V_fixChestFront1 = (0.185, 0, -.1)
    fixChestFront1L = "fixChestFront1.L"
    fixChestFront1R = "fixChestFront1.R"
    V_fixChestFront2 = (-.04, 0, -.12)
    fixChestFront2L = "fixChestFront2.L"
    fixChestFront2R = "fixChestFront2.R"
    #
    V_fixChestCenter1 = (0.19, 0, -.13)
    fixChestCenter1L = "fixChestCenter1.L"
    fixChestCenter1R = "fixChestCenter1.R"
    V_fixChestCenter2 = (-.05, 0, -.12)
    fixChestCenter2L = "fixChestCenter2.L"
    fixChestCenter2R = "fixChestCenter2.R"
    #
    V_fixChestBack = (0, -.06, 0)
    fixChestBack = "fixChestBack"
    V_fixChestBack1 = (0.195, 0, -.02)
    fixChestBack1L = "fixChestBack1.L"
    fixChestBack1R = "fixChestBack1.R"
    V_fixChestBack2 = (-.06, 0, -.12)
    fixChestBack2L = "fixChestBack2.L"
    fixChestBack2R = "fixChestBack2.R"
    V_fixUpperShoulder1 = (0, -.06, -.03)
    fixUpperShoulder1L = "fixUpperShoulder1L"
    V_fixUpperShoulder2 = (0.195, 0, -.02)
    fixUpperShoulder2L = "fixUpperShoulder2.L"
    fixUpperShoulder2R = "fixUpperShoulder2.R"
    # END BIPED PARTS, start quadruped:
    V_join = (0, 0, -.12)
    join = "join"
    V_drop = (0, 0, -.17)
    drop = "drop"
    V_pelvis = (0, 0, -.15)
    pelvis = "pelvis"
    #
    # Name will be bBackJ0, bBackJ1, bBackJ2, etc
    #V_qBackJ1 = (0, -0.14, -.06)
    #V_qBackJ2 = (0, -.11, 0)
    #V_qBackJ3 = (0, -.12, .02)
    #V_qBackJ4 = (0, -.12, .02)
    #V_qBackJ5 = (0, -.14, .01)
    V_fixRib1Top = (.1, 0, -.04)  # Removed the q (quadruped)
    fixRib1TopL = "fixRib1Top.L"
    fixRib1TopR = "fixRib1Top.R"
    V_qfixRib1B = (0, -.06, -0.4)
    fixRib1BL = "fixRib1B.L"
    fixRib1BR = "fixRib1B.R"
    V_qfixRib2Top = (.1, .02, 0)
    fixRib2TopL = "fixRib2Top.L"
    fixRib2TopR = "fixRib2Top.R"
    V_qfixRib2B = (0, -.06, -.4)
    fixRib2BL = "fixRib2B.L"
    fixRib2BR = "fixRib2B.R"
    V_qfixRib3Top = (.1, 0, 0)
    fixRib3TopL = "fixRib3Top.L"
    fixRib3TopR = "fixRib3Top.R"
    V_qfixRib3B = (0, 0, -.38)
    fixRib3BL = "fixRib3B.L"
    fixRib3BR = "fixRib3B.R"
    V_qfixRib4Top = (.1, 0, 0)
    fixRib4TopL = "fixRib4Top.L"
    fixRib4TopR = "fixRib4Top.R"
    V_qfixRib4B = (0, 0, -.36)
    fixRib4BL = "fixRib4B.L"
    fixRib4BR = "fixRib4B.R"
    #
    V_hRumpJ1 = (0, -.16, -.004)
    hRumpJ1 = "hRumpJ1"
    V_hRumpJ2 = (0, -.12, -.004)
    hRumpJ2 = "hRumpJ2"
    V_hRumpJ3 = (0, -.05, 0)
    hRumpJ3 = "hRumpJ3"
    #
    V_hTailJ1 = (0, -.04, .0146)
    hTailJ1 = "hTailJ1"
    V_hTailJ2 = (0, -.06, .012)
    hTailJ2 = "hTailJ2"
    V_hTailJ3 = (0, -.06, .01)
    hTailJ3 = "hTailJ3"
    V_hTailJ4 = (0, -.06, 0)
    hTailJ4 = "hTailJ4"
    V_hTailJ5 = (0, -.06, 0)
    hTailJ5 = "hTailJ5"
    V_hTailJ6 = (0, -.06, 0)
    hTailJ6 = "hTailJ6"
    V_hTailJ7 = (0, -.06, 0)
    hTailJ7 = "hTailJ7"
    V_hTailJ8 = (0, -.06, 0)
    hTailJ8 = "hTailJ8"
    V_hTailJ9 = (0, -.06, 0)
    hTailJ9 = "hTailJ8"
    #
    V_hRumpfix1 = (0, -.04, -.2)
    hRumpfix1 = "hRumpfix1"
    V_hRumpfix2 = (0, .12, -.06)
    hRumpfix2 = "hRumpfix2"
    V_hRumpfix3 = (0, .15, -.07)
    hRumpfix3 = "hRumpfix3"
    V_hRumpfix4 = (0, .2, .04)
    hRumpfix4 = "hRumpfix4"
    #
    V_rearHip = (.16, 0, 0)
    rearHipL = "rearHip.L"
    rearHipR = "rearHip.R"
    V_fix4 = (0, -.16, -.11)
    fix4L = "fix4.L"
    fix4R = "fix4.R"
    V_qfix5 = (0, 0, -.12)
    fix5L = "fix5.L"
    fix5R = "fix5.R"
    #
    V_rearHipJ1 = (0, -.08, -.27)
    rearHipJ1L = "rearHipJ1.L"
    rearHipJ1R = "rearHipJ1.R"
    V_rearFemurJ1 = (0, -.08, -.2)
    rearFemurJ1L = "rearFemurJ1.L"
    rearFemurJ1R = "rearFemurJ1.R"
    V_rearFemurJ2 = (0, -.08, -.2)
    rearFemurJ2L = "rearFemurJ2.L"
    rearFemurJ2R = "rearFemurJ2.R"
    V_rearTibiaJ1 = (0, 0, -.15)
    rearTibiaJ1L = "rearTibiaJ1.L"
    rearTibiaJ1R = "rearTibiaJ1.R"
    V_rearTibiaJ2 = (0, 0, -.15)
    rearTibiaJ2L = "rearTibiaJ2.L"
    rearTibiaJ2R = "rearTibiaJ2.R"
    V_horseRRearAnkle = (0, .06, -.07)
    horseRRearAnkleL = "horseRRearAnkle.L"
    horseRRearAnkleR = "horseRRearAnkle.R"
    V_horseRToe = (0, .04, -.06)
    horseRToeL = "horseRToe.L"
    horseRToeR = "horseRToe.R"
    #
    # already exist as bNeckJ1. Left over from when each
    # character had its own class.
    #V_qNeckJ1 = (0, .05, 0.1)
    #V_qNeckJ2 = (0, .05, 0.1)
    #V_qNeckJ3 = (0, .05, 0.14)
    #V_qNeckJ4 = (0, .05, .1)
    #V_qNeckJ5 = (0, .05, .1)
    #V_qNeckJ6 = (0, .05, .1)
    # Already exist, not mirrored
    #V_headBase = (0, 0, 0.09)
    #V_eyeLevel = (0, 0, .04)
    #V_headTop = (0, -.05, 0)
    #V_headFore = (0, .08, .09)
    #
    # Already exist, mirrored 
    #V_earRoot = (.05, -.06, .06)
    #V_earBase = (0, -.02, .02)
    #V_earJ1 = (0, -.015, .015)
    #V_earJ2 = (0, -.015, .015)
    #V_earJ3 = (0, -.015, .015)
    #V_earJ4 = (0, -.015, .015)
    #V_earJ5 = (0, -.015, .015)
    #
    # Already exist
    #V_baseJaw = (0, .02, 0) not mirrored
    #V_jaw = (0, .02, 0)     not mirrored
    #V_jaw1 = (.03, .01, 0)  mirrored
    #V_jaw2 = (-.02, .07, 0) mirrored
    #
    #V_eyebase = (-.03, 0.1, 0) mirrored
    #V_eye = (0, 0.03, 0)       mirrored
    #
    #V_noseBase = (0, .138, 0) not mirrored
    #V_nose = (0, 0.02, -.02)  not mirrored
    #
    VbackL1 = (0, -0.15, -.15)
    VbackL1 = "VbackL1"
    VbackL2 = (0, -0.1, -.1)
    VbackL2 = "VbackL2"
    VbackL3 = (0, -0.1, -.04)
    VbackL3 = "VbackL3"
    VTailJ1 = (0, -0.1, -.04)
    VTailJ1 = "tailJ1"
    VTailJ2 = (0, -.1, 0)
    tailJ2 = "tailJ2"
    VTailJ3 = (0, -.06, 0)
    tailJ3 = "tailJ3"
    #
    Vfb1 = (0.022, .024, 0)
    fb1L = "fb1.L"
    fb1R = "fb1.R"
    Vfb2 = (0.022, .024, 0)
    fb2L = "fb2.L"
    fb2R = "fb2.R"
    Vfb3 = (0.022, .024, 0)
    fb3L = "fb1.L"
    fb3R = "fb1.R"
    Vfb4 = (0.022, .024, 0)
    fb4L = "fb4.L"
    fb4R = "fb4.R"
    #
    Vfa1 = (0, -.08, 0)  
    fa1L = "fa1.L"
    fa1R = "fa1.R"
    Vfa2 = (0, -.08, 0)
    fa2L = "fa2.L"
    fa2R = "fa2.R"
    Vfa3 = (0, -.08, 0)
    fa3L = "fa3.L"
    fa3R = "fa3.R"
    Vfa4 = (0, -.08, 0)
    fa4L = "fa4.L"
    fa4R = "fa4.R"
    Vfa4 = (0, -.08, 0) # This one may be extra
    fa5L = "fa5.L" 
    fa5R = "fa5.R"
    #
    #V_neckJ1, not Vneck01 = (0, .12, -.02)
    #V_neckJ2, not Vneck02 = (0, .04, 0.04)
    #V_neckJ3, not Vneck03 = (0, .03, .04)
    #V_neckJ4, not Vneck04 = (0, .02, .04)
    #V_neckJ5, not Vneck05 = (0, 0, .04)
    #V_neckJ6, not Vneck06 = (0, 0, .04)
    #VHeadBase = (0, -.03, .05)
    #VHeadTop = (0, 0.17, .03)
    #Vcrest = (0, -.1, .08)
    #
    VbeakBase = (0, 0.08, .07)
    beakBase = "beakBase"
    Vbeak1 = (0, 0.16, 0)
    beak1 = "beak1"
    Vbeak2 = (0, 0.18, -.05)
    beak1 = "beak1"
    #
    Vffix1 = (0, 0.06, -.1)
    ffix1 = "ffix1"
    Vffix2 = (0, -.05, -.1)
    ffix2 = "ffix2"
    Vffix3 = (0, -.07, -.1)
    ffix3 = "ffix3"
    Vffix4 = (0, -.08, -.1)
    ffix4 = "ffix4"
    Vffix5 = (0, -.09, -.1)
    ffix5 = "ffix5"
    #
    VrearToeJ1 = (-.016, -0.07, .01)
    rearToeJ1L = "rearToeJ1.L"
    rearToeJ1R = "rearToeJ1.R"
    VrearToeJ2 = (-.015, -0.07, 0)
    rearToeJ2L = "rearToeJ2.L"
    rearToeJ2R = "rearToeJ2.R"
    VrearToeJ3 = (-.015, -0.07, 0)
    rearToeJ3L = "rearToeJ3.L"
    rearToeJ3R = "rearToeJ3.R"
    VrearToeJ4 = (-.015, -0.07, 0)
    rearToeJ4L = "rearToeJ4.L"
    rearToeJ4R = "rearToeJ4.R"    
    #
    #VcenterToe = (0, .07, 0) Setting only
    #
    VouterToe = (-.0358, .066, 0)
    outerToeL = "outerToe.L"
    outerToeR = "outerToe.R"
    VinnerToe = (.034, .065, 0)
    innerToe = "innerToe"
    # Wings
    Vbase = (-.12, 0, 0)
    base = "base"
    Vwings_J1 = (-.06, 0, 0)
    wings_J1L = "wings_J1.L"
    wings_J1R = "wings_J1.R"
    Vwings_J2 = (-.03, 0, 0)
    wings_J2L = "wings_J2.L"
    wings_J2R = "wings_J2.R"
    Vwings_J3 = (-.03, 0, 0)
    wings_J3L = "wings_J3.L"
    wings_J3R = "wings_J3.R"
    Vwings_J4 = (-.03, 0, 0)
    wings_J4L = "wings_J4.L"
    wings_J4R = "wings_J4.R"
    Vwings_J5 = (-.03, 0, 0)
    wings_J5L = "wings_J5.L"
    wings_J5R = "wings_J5.R"
    Vwings_J6 = (-.03, 0, 0)
    wings_J6L = "wings_J6.L"
    wings_J6R = "wings_J6.R"
    Vwings_J7 = (-.03, 0, 0)
    wings_J7L = "wings_J7.L"
    wings_J7R = "wings_J7.R"
    Vwings_J8 = (-.03, 0, 0)
    wings_J8L = "wings_J8.L"
    wings_J8R = "wings_J8.R"
    Vwings_J9 = (-.03, 0, 0)
    wings_J9L = "wings_J9.L"
    wings_J9R = "wings_J9.R"
    Vwings_J10 = (-.03, 0, 0)
    wings_J10L = "wings_J10.L"
    wings_J10R = "wings_J10.R"
    Vwings_J11 = (-.015, 0, 0)
    wings_J11L = "wings_J11.L"
    wings_J11R = "wings_J11.R"
    Vwings_J12 = (-.015, 0, 0)
    wings_J12L = "wings_J12.L"
    wings_J12R = "wings_J12.R"
    Vwings_J13 = (-.015, 0, 0)
    wings_J13L = "wings_J13.L"
    wings_J13R = "wings_J13.R"
    Vwings_J14 = (-.015, 0, 0)
    wings_J14L = "wings_J14.L"
    wings_J14R = "wings_J14.R"
    Vwings_J15 = (-.015, 0, 0)
    wings_J15L = "wings_J15.L"
    wings_J15R = "wings_J15.R"
    Vwings_J16 = (-0.06, 0, 0)
    wings_J16L = "wings_J16.L"
    wings_J16R = "wings_J16.R"
    #
    Vfeathers1 = (0, -.04, 0) # Vfeathers originally
    feathers1L = "feathers1.L"
    feathers1R = "feathers1.R"
    Vfeathers2 = (0, -.04, 0)
    feathers2L = "feathers2.L"
    feathers23R = "feathers2.R"
    Vfeathers3 = (0, -.04, 0)
    feathers3L = "feathers3.L"
    feathers3R = "feathers3.R"
    Vfeathers4 = (0, -.04, 0)
    feathers4L = "feathers4.L"
    feathers4R = "feathers4.R"
    Vfeathers5 = (0, -.04, 0)
    feathers5L = "feathers5.L"
    feathers5R = "feathers5.R"
    Vfeathers6 = (0, -.04, 0)
    feathers6L = "feathers6.L"
    feathers6R = "feathers6.R"
    Vfeathers7 = (0, -.04, 0)
    feathers7L = "feathers7.L"
    feathers7R = "feathers7.R"
    Vfeathers8 = (0, -.04, 0)
    feathers8L = "feathers8.L"
    feathers8R = "feathers8.R"
    Vfeathers9 = (0, -.04, 0)
    feathers9L = "feathers9.L"
    feathers9R = "feathers9.R"
    Vfeathers10 = (0, -.04, 0)
    feathers10L = "feathers10.L"
    feathers10R = "feathers10.R"
    Vfeathers11 = (0, -.04, 0)
    feathers11L = "feathers11.L"
    feathers11R = "feathers11.R"
    Vfeathers12 = (0, -.04, 0)
    feathers12L = "feathers12.L"
    feathers12R = "feathers12.R"
    Vfeathers13 = (0, -.04, 0)
    feathers13L = "feathers13.L"
    feathers13R = "feathers13.R"
    Vfeathers14 = (0, -.04, 0)
    feathers14L = "feathers14.L"
    feathers14R = "feathers14.R"
    Vfeathers15 = (0, -.04, 0)
    feathers15L = "feathers15.L"
    feathers15R = "feathers15.R"
    #
    Vframe1F = (0, .254, 0)
    frame1FL = "frame1F.L"  # F for front
    frame1FR = "frame1F.R"
    VsideToSide2F = (.2, 0, 0) # was frame
    sideToSide2F = "sideToSide2F.L"
    sideToSide2F = "sideToSide2F.R"
    VsideToSide1F = (0, 0, .062)
    sideToSide1F = "sideToSide1F.L"
    sideToSide1F = "sideToSide1F.R"
    Vleg2J1F = (.2, 0, .082)
    leg2J1F = "leg2J1F.L"
    leg2J1F = "leg2J1F.R"
    Vleg2J2F = (.4, 0, -.2)
    leg2J2F = "leg2J2F.L"
    leg2J2F = "leg2J2F.R"
    Vleg2J3F = (.1, 0, 0)
    leg2J3F = "leg2J3F.L"
    leg2J3F = "leg2J3F.R"
    #
    Vframe5 = (0, -.25, 0)
    frame5L = "frame5.L"
    frame5R = "frame5.R"
    VsideToSide5 = (.22, 0, 0)
    sideToSide5L = "sideToSide5.L"
    sideToSide5R = "sideToSide5.R"
    Vleg5J1 = (0, 0, .062) # Spiders have many legs
    leg5J1L = "leg5J1.L"
    leg5J1R = "leg5J1.R"
    Vleg5J2 = (.2, 0, .082)
    leg5J2L = "leg5J2.L"
    leg5J2R = "leg5J2.R"
    Vleg5J3 = (.4, 0, -.2)
    leg5J3L = "leg5J3.L"
    leg5J3R = "leg5J3.R"
    Vleg5J4 = (.1, 0, 0)
    leg5J4L = "leg5J4.L"
    leg5J4R = "leg5J4.R"
    #
    Vframe3 = (.254, 0, 0)
    frame3 = "frame3"
    VsideToSide2 = (0, .082, 0)
    sideToSide2 = "sideToSide2"
    Vleg4J1 = (0, -.082, 0)
    leg4J1 = "leg4J1"
    Vleg4J2 = (0, 0, .062)
    leg4J2 = "leg4J2"
    Vframe = (.2, 0, .082)
    sideToSide3 = "sideToSide3"
    Vframe = (.4, 0, -.2)
    leg3J1 = "leg3J1"
    Vframe = (.1, 0, 0)
    leg3J2 = "leg3J2"
    Vframe = (0, 0, .062)
    leg3J3 = "leg3J3"
    # unknowns:
    Vframe = (.2, 0, .082)
    Vframe = (.4, 0, -.2)
    Vframe = (.1, 0, 0)
    #
    Vframe8LF = (-.254, 0, 0)
    frame8LF = "frame8L.F"  # Left Front
    VsideToSide8LF = (0, .082, 0)
    sideToSide8LF = "sideToSide8L.F"
    Vleg8J1LF = (0, 0, .062)
    leg8J1LF = "leg8J1L.F"
    Vleg8J2LF = (-.2, 0, .082)
    leg8J2LF = "leg8J2L.F"
    Vleg8J3LF = (-.4, 0, -.2)
    leg8J3LF = "leg8J3L.F"
    Vframe7LB = (-.1, 0, 0)
    frame7LB = "frame7L.B"   # Left Back
    VsideToSide7LB = (0, -.082, 0)
    sideToSide7LB = "sideToSide7L.B"
    Vleg7J1LB = (0, 0, .062)
    leg7J1LB = "leg7J1L.B"
    Vleg7J2LB = (-.2, 0, .082)
    leg7J2LB = "leg7J2L.B"
    Vleg7J3B = (-.4, 0, -.2)
    leg7J3B = "leg7J3L.B"
    # unknown
    # V = (-.1, 0, 0)
    #
    #
    VTail1 = (0, -.12, .08)
    tail1 = "tail1"
    VTail2 = (0, -.26, 0)
    tail2 = "tail2"
    VTail3 = (0, -.26, 0)
    tail3 = "tail3"
    VTail4 = (0, -.26, 0)
    tail4 = "tail4"
    #
    def setCharPropertiesPanel():
        CONTROL_PT_Panel


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# CHARACTERS CLASSES: Character Creation Panel
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class CONTROL_PT_Panel(bpy.types.Panel):
    #bl_idname = "object.CONTROL_PT_Panel"
    bl_label = "Character Control"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Animator'
    bl_context = "objectmode"
    #
    def draw(self, context):
        layout = self.layout
        layout.row().operator("object.biped_build_btn")
        layout.row().operator("object.centaur_build_btn")
        layout.row().operator("object.quadruped_build_btn")
        layout.row().operator("object.bird_build_btn")
        layout.row().operator("object.spider_build_btn")
        layout.row().operator("object.wings_build_btn")
        layout.row().separator()
        #layout.row().operator("object.pose_btn")  # (Common to all)
        #layout.row().operator("object.drop_arms_btn")
        layout.row().operator("object.walk_btn")
        #layout.row().operator("object.run_btn")
        layout.row().operator("object.control1_btn") # Character controls
        layout.row().operator("object.control2_btn") # Character controls
        #layout.row().operator("object.arm_action_btn")  # Arm action toggle
        #layout.row().operator("object.leg_action_btn")  # Leg action toggle
        #layout.row().operator("object.reset_btn")  # Revert Advanced Controls

class CHARACTER_OT_control_I(bpy.types.Operator):
    bl_idname = "object.control1_btn"
    """Control Dialog box"""
    bl_label = "Character Controls I"
    #
    speed : bpy.props.FloatProperty(default=0.0)
    cycle : FloatProperty(default=1.0)
    direction : FloatProperty(default=0.0)
    X_Location : FloatProperty(default=0.0)
    Y_Location : FloatProperty(default=0.0)
    Z_Location : FloatProperty(default=0.0)
    Sway_LR : FloatProperty(default=6.0)
    Sway_FB : FloatProperty(default=6.0)
    bounce : FloatProperty(default=0.0)
    Shoulder_Rotation : FloatProperty(default=10.0)
    Shoulder_UD : FloatProperty(default=10.0)
    Leg_Spread : FloatProperty(default=0.0)
    Hip_Sway : FloatProperty(default=5.0)
    Hip_Rotate : FloatProperty(default=5.0)
    Hip_UD : FloatProperty(default=1.0)
    Leg_Arch : FloatProperty(default=0.0)
    rotatePosition : FloatProperty(default=0.1)
    rotateRange : FloatProperty(default=1.0)
    #
    def execute(self, context): # What is here is STATIC
        ob = bpy.context.object
        cwmPanel.speed = self.speed
        cwmPanel.cycle = self.cycle
        ob.location = (self.X_Location, self.Y_Location, self.Z_Location + 1.18)
        ob.rotation_euler.z = radians(self.direction-90)
        cwmPanel.Sway_LR = self.Sway_LR
        cwmPanel.Sway_FB = self.Sway_FB
        cwmPanel.bounce = self.bounce
        cwmPanel.Shoulder_Rotation = self.Shoulder_Rotation
        cwmPanel.Shoulder_UD = self.Shoulder_UD
        cwmPanel.Leg_Spread = self.Leg_Spread
        #cwmPanel.skate = self.skate
        cwmPanel.Hip_Sway = self.Hip_Sway
        cwmPanel.Hip_Rotate = self.Hip_Rotate
        cwmPanel.Hip_UD = self.Hip_UD
        cwmPanel.Leg_Arch = self.Leg_Arch
        cwmPanel.rotatePosition = self.rotatePosition
        cwmPanel.rotateRange = self.rotateRange
        getSelectedCharacterName()
        bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}
    #
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

class CHARACTER_OT_control_II(bpy.types.Operator):
    bl_idname = "object.control2_btn"
    """Control Dialog box"""
    bl_label = "Character Controls II"
    #
    Arms_UD : FloatProperty(default=0.0) # slider=True, 
    LArm_Twist : FloatProperty(default=0.0)
    RArm_Twist : FloatProperty(default=0.0)
    Arm_Rotation : FloatProperty(default=0.0)
    LHand_Spread : FloatProperty(default=0.0)
    LHand_OC : FloatProperty(default=0.0)
    RHand_Spread : FloatProperty(default=0.0)
    RHand_OC : FloatProperty(default=0.0)
    Head_UD : FloatProperty(default=0.0)
    Head_LR : FloatProperty(default=0.0)
    Head_Turn : FloatProperty(default=0.0)
    Jaw_OC : FloatProperty(default=0.0)
    Eye_LR : FloatProperty(default=0.0)
    Eye_UD : FloatProperty(default=0.0)
    #
    def execute(self, context): # What is here is STATIC
        ob = bpy.context.object
        cwmPanel.Arms_UD = self.Arms_UD
        cwmPanel.LArm_Twist = self.LArm_Twist
        cwmPanel.RArm_Twist = self.RArm_Twist
        cwmPanel.Arm_Rotation = self.Arm_Rotation
        cwmPanel.LHand_Spread = self.LHand_Spread
        cwmPanel.LHand_OC = self.LHand_OC
        cwmPanel.RHand_Spread = self.RHand_Spread
        cwmPanel.RHand_OC = self.RHand_OC
        cwmPanel.Head_UD = self.Head_UD
        cwmPanel.Head_LR = self.Head_LR
        cwmPanel.Head_Turn = self.Head_Turn
        cwmPanel.Jaw_OC = self.Jaw_OC
        cwmPanel.Eye_LR = self.Eye_LR
        cwmPanel.Eye_UD = self.Eye_UD
        getSelectedCharacterName()
        bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}
    #
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class Biped_Build_Btn(bpy.types.Operator):  # Button
    bl_idname = "object.biped_build_btn"
    bl_label = "Build Biped"
    bl_description = "Build Biped"
    bl_options = {"REGISTER", "UNDO"}
    hidden = False
    def execute(self, context):
        buildBipedSkeleton()
        bpy.context.scene.frame_set(0)
        bpy.ops.object.mode_set(mode='OBJECT')
        return{'FINISHED'}

class Centaur_Build_Btn(bpy.types.Operator):
    bl_idname = "object.centaur_build_btn"
    bl_label = "Build Centaur"
    bl_description = "Build Centaur"
    bl_options = {"REGISTER", "UNDO"}
    hidden = False
    def execute(self, context):
        buildCentaurSkeleton()
        bpy.context.scene.frame_set(0)
        bpy.ops.object.mode_set(mode='OBJECT')
        return{'FINISHED'}

class Quadruped_Build_Button(bpy.types.Operator):
    bl_idname = "object.quadruped_build_btn"
    bl_label = "Build Quadruped"
    bl_description = "Build Quadruped"
    hidden = False
    def execute(self, context):
        buildQuadrupedSkeleton()
        bpy.context.scene.frame_set(0)
        bpy.ops.object.mode_set(mode='OBJECT')
        return{'FINISHED'}

class Bird_Build_Button(bpy.types.Operator):
    bl_idname = "object.bird_build_btn"
    bl_label = "Build Bird"
    bl_description = "Build Bird"
    hidden = False
    def execute(self, context):
        buildBirdSkeleton()
        bpy.context.scene.frame_set(0)
        bpy.ops.object.mode_set(mode='OBJECT')
        return{'FINISHED'}

class Spider_Build_Button(bpy.types.Operator):
    bl_idname = "object.spider_build_btn"
    bl_label = "Build Spider"
    bl_description = "Build Spider"
    hidden = False
    def execute(self, context):
        buildSpiderSkeleton()
        bpy.context.scene.frame_set(0)
        bpy.ops.object.mode_set(mode='OBJECT')
        return{'FINISHED'}

class Wings_Build_Button(bpy.types.Operator):  
    bl_idname = "object.wings_build_btn"
    bl_label = "Build Wings"
    bl_description = "Build Wings"
    hidden = False
    def execute(self, context):
        buildWings()
        bpy.context.scene.frame_set(0)
        bpy.ops.object.mode_set(mode='OBJECT')
        return{'FINISHED'}

class Drop_Arms_Btn(bpy.types.Operator):
    bl_idname = "object.drop_arms_btn"
    bl_label = "Drop Arms"
    bl_description = "Drop Character Arms"
    bl_options = {"REGISTER", "UNDO"}
    hidden = False
    def execute(self, context):
        bpy.ops.object.mode_set(mode='POSE')
        bpy.context.object.pose.bones["armJ1.L"].rotation_euler[2] = 1.57
        bpy.context.object.pose.bones["armJ1.R"].rotation_euler[2] = -1.57
        bpy.ops.object.mode_set(mode='OBJECT')
        return{'FINISHED'}

class Pose_Btn(bpy.types.Operator):
    bl_idname = "object.pose_btn"
    bl_label = "Pose Character"
    bl_description = "Pose Character"
    bl_options = {"REGISTER", "UNDO"}
    hidden = False
    def execute(self, context):
        bpy.context.object.pose.bones["armJ1.R"].rotation_euler[0] = 0
        bpy.context.object.pose.bones["armJ1.L"].rotation_euler[0] = 0
        bpy.ops.screen.animation_cancel(restore_frame=True)
        bpy.ops.object.mode_set(mode='OBJECT')
        return{'FINISHED'}

class Walk_Btn(bpy.types.Operator):
    bl_idname = "object.walk_btn"
    bl_label = "Set Walk"
    bl_description = "Set Walk"
    bl_options = {"REGISTER", "UNDO"}
    hidden = False
    def execute(self, context):
        setWalk(self, context)
        bpy.ops.object.mode_set(mode='OBJECT')
        return{'FINISHED'}

class Run_Btn(bpy.types.Operator):
    bl_idname = "object.run_btn"
    bl_label = "Set Run"
    bl_description = "Set Run"
    bl_options = {"REGISTER", "UNDO"}
    hidden = False
    def execute(self, context):
        setRun(self, context)
        bpy.ops.object.mode_set(mode='OBJECT')
        return{'FINISHED'}        

class Arm_Action_Btn(bpy.types.Operator):
    bl_idname = "object.arm_action_btn"
    bl_label = "Toggle Arm Movement ON/OFF"
    bl_description = "Toggle Arm Movement ON/OFF"
    bl_options = {"REGISTER", "UNDO"}
    hidden = False
    def execute(self, context):
        if(genProp(genProp.toggleArmAction) == True):
            setArmRotation(self, context)
        else:
            unSetArmRotation(self, context)
        genProp.toggleArmAction = not genProp.toggleArmAction
        bpy.ops.object.mode_set(mode='OBJECT')
        return{'FINISHED'}

class Leg_Action_Btn(bpy.types.Operator):
    bl_idname = "object.leg_action_btn"
    bl_description = "Toggle Leg Movement ON/OFF"
    bl_label = "Toggle Leg Movement ON/OFF"
    bl_options = {"REGISTER", "UNDO"}
    hidden = False
    def execute(self, context):
        if(genProp.toggleLegAction == True):
            setWalk(self, context)
        else:
            unSetLegRotation(self, context)
        bpy.ops.object.mode_set(mode='OBJECT')
        genProp.toggleLegAction = not genProp.toggleLegAction
        return{'FINISHED'}

class Reset_btn(bpy.types.Operator):
    bl_idname = "object.reset_btn"
    bl_label = "Reset Advanced Controls"
    bl_description = "Reset Advanced Controls"
    bl_options = {"REGISTER", "UNDO"}
    hidden = False
    def execute(self, context):
        revertAdvancedControls(self, context)
        bpy.ops.object.mode_set(mode='OBJECT')
        return{'FINISHED'}

class CharacterPanel():
    bl_label = "characterpanel"
    bl_description = "characterpanel"
    bl_options = {"REGISTER", "UNDO"}
    def setCharacterPropertiesPanel():
        CONTROL_PT_Panel

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# END PANELS CLASS
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|
# cycle control
def clock(freq=9, amp=.5):  # Sets the pace
    cycle = cwmPanel.cycle
    frame = bpy.context.scene.frame_current
    stp = amp * abs((cycle*frame)/freq % 4 - 2) - amp
    return round(stp, 2)

# add to namespace
bpy.app.driver_namespace['clock'] = clock

def setLegArch(self, context):
    fn = cwmPanel.Leg_Arch * .02  # Leg Arch
    setAxisDriver(getEuler('femurJ1.L'), str(-fn), 1)
    setAxisDriver(getEuler('femurJ1.R'), str(fn), 1)

def getSpecialString(atFrame):
    s = str(atFrame[1])
    n = s.find('default')
    s = s[n+12:]
    n = s.find("'")
    s = s[:-n]
    return s

def setDriver(bone, fn="0", axis=0, movementType='rotation_euler'):
    eulerDriver = bone.driver_add(movementType)
    eulerDriver[axis].driver.type = 'SCRIPTED'
    eulerDriver[axis].driver.expression = fn
    return eulerDriver

def getSceneObjectNumber():
    n = 0
    for ob in list(bpy.data.objects):
        if ob.name.startswith('rg') == True:
            n = n + 1
    return n

# Create character base for Armature and Character Class
def buildRootArmature(charName, x=0, y=0, z=0):
    char = Character
    char.armature = bpy.data.armatures.new(charName + '_at')  # at = Armature
    char.name = charName # rgbiped01
    char.armatureName = charName + '_at' # rgbiped01_at
    bpy.context.scene.frame_start = 0
    char.rig = bpy.data.objects.new(charName, char.armature) # rig = Armature object
    char.rig.show_in_front = True
    char.x = x; char.y = y; char.z = z
    char.rig.location = (x, y, z)  # Set armature point locatioon
    # Link to scene
    coll = bpy.context.view_layer.active_layer_collection.collection
    coll.objects.link(char.rig)
    bpy.context.view_layer.objects.active = char.rig
    bpy.context.view_layer.update()
    return char

def setName(type, n):
    name = "rg" + type + "0" + str(n + 1)  # Assume n < 10 
    if (n > 9):  # Change x.name if previous assumption is wrong
        name = "rg" + type + str(n + 1)
    return name

# AttributeError: 'Armature' object has no attribute 'armature'
def setHandle(char, VHead, VTail):
    bpy.ops.object.editmode_toggle()
    bone = char.armature.edit_bones.new(char.name + '_bone')
    bone.head = VTail
    bone.tail = VHead
    return bone

def boneMirror(char, vector, mirror = False):
    bpy.data.armatures[char.name + '_at'].use_mirror_x = mirror
    x = vector[0]; y = vector[1]; z = vector[2]
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.armature.extrude_forked(ARMATURE_OT_extrude={"forked":True}, TRANSFORM_OT_translate={"value":(x, y, z)})
    bone = bpy.context.object.data.bones.active
    return bone

def getActiveBoneName():
    s = str(bpy.context.active_bone)
    n = s.find('"')
    s = s[n+1:]
    s = s[:-3]
    return s 

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

def deselectAll():
    bpy.ops.armature.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    for ob in bpy.context.selected_objects:
        ob.select_set(False)

# Set Driver For Single Axis Only:
def setAxisDriver(euler, fn="0", axis=0, movementType='rotation_euler'):
    edriver = euler.driver_add(movementType, axis)
    edriver.driver.type = 'SCRIPTED'
    edriver.driver.expression = fn
    return edriver

# getEuler output represents:
# bpy.data.objects['rg00biped'].pose.bones["backCenter"]
def getEuler(str_bone_name):  # *** Switching to pose mode must be external
    ob = bpy.context.object
    bone = ob.pose.bones[str_bone_name]
    bone.rotation_mode = 'XYZ'
    return bone

def checkMode():
    if(bpy.context.object == 'None'):
        return 'N'
    current_mode = bpy.context.object.mode
    if(current_mode == 'OBJECT'):
        return 'O'
    if(current_mode == 'POSE'):
        return 'P'
    if(current_mode == 'EDIT'):
        return 'E'

def setWalk(self, context):
    name = getSelectedCharacterName()
    if(name.startswith("rgbiped")):
        setCharacterWalk(self, context)

# walk speed control
def setHorizontalSpeed():
    spd = cwmPanel.speed
    frame = bpy.context.scene.frame_current
    spd = frame * .04 * spd
    return round(spd, 2)

# add this function to the namespace
bpy.app.driver_namespace['setHorizontalSpeed'] = setHorizontalSpeed

# Make bone creation easy
def createBone(name="boneName", VHead=(0, 0, 0), VTail=(.1, 0, .1), roll=0, con=False):
    bpy.ops.object.mode_set(mode='EDIT')
    bData = bpy.context.active_object.data
    bone = bData.edit_bones.new(name)
    bone.head[:] = VHead
    bone.tail[:] = VTail
    bone.roll = roll
    bone.use_connect = con
    return bone

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# setEnve1opeWeights - COMMON FUNCTION 
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def setEnvelopeWeights(char):
    # The position of the following two for loops is important;
    # it initializes all bones to have a specific envelope weight
    # in case the bone has not been set manually as below. It 
    # cannot be placed afterwards, or it will override the settings.
    for b in bpy.data.objects[char.name].pose.bones:
        b.rotation_mode = 'XYZ'
    for b in bpy.context.object.data.edit_bones:
        b.envelope_distance = 0.05  # Default envelope distance
        b.head_radius = 0.02
        b.tail_radius = 0.02
        #b.envelope_weight = 2.0
    #
    for b in bpy.context.object.data.edit_bones:
        # Set weights for biped lower body
        if(char.name.startswith("rgbiped")):
            if(b.name.startswith("femur")):
                b.envelope_distance = 0.08
                b.head_radius = 0.08
                b.tail_radius = 0.08
            if(b.name.startswith("tibia")):
                b.envelope_distance = 0.048
                b.head_radius = 0.048
                b.tail_radius = 0.048
            if(b.name.startswith("ankle")):
                b.envelope_distance = 0.05
                b.head_radius = 0.05
                b.tail_radius = 0.05
            if(b.name.startswith("toe")):
                b.envelope_distance = 0.05
                b.head_radius = 0.05
                b.tail_radius = 0.05
            if(b.name.startswith("heel")):
                b.envelope_distance = 0.04
                b.head_radius = 0.02
                b.tail_radius = 0.04
            if(b.name.startswith("fixPosterior2")):
                b.envelope_distance = 0.08
    #
        # Set weights for upper human parts
        if(char.name.startswith("rgbiped")) or (char.name.startswith("rgcentaur")):
            if(b.name.startswith("eye")):    # eye must be set first or it cancels
                b.envelope_distance = 0      # out other settings on eyebones
                b.envelope_weight = 0.0
                b.envelope_distance = 0.0
            if(b.name.startswith("pinky")):
                b.envelope_distance = 0.014
            if(b.name.startswith("ring")):
                b.envelope_distance = 0.014
            if(b.name.startswith("mid")):
                b.envelope_distance = 0.01
            if(b.name.startswith("index")):
                b.envelope_distance = 0.014
            if(b.name.startswith("wrist")):
                b.envelope_distance = 0.01
            if(b.name.startswith("thumb")):
                b.envelope_distance = 0.016
            if(b.name.startswith("radius")):
                b.envelope_distance = 0.05
            if(b.name.startswith("neck")):
                b.envelope_distance = 0.06
            if(b.name.startswith("jaw")):
                b.envelope_distance = 0.06
            if(b.name.startswith("baseMouth2")):
                b.envelope_distance = 0.08
            if(b.name.startswith("baseMouth3")):
                b.envelope_distance = 0.013
            if(b.name.startswith("mouth")):
                b.envelope_distance = 0.02
            if(b.name.startswith("nose")):
                b.envelope_distance = 0.01
            if(b.name.startswith("noseBase")):
                b.envelope_distance = 0.054
            if(b.name.startswith("eyeLevel")):
                b.envelope_distance = 0.12
            if(b.name.startswith("noseLevel")):
                b.envelope_distance = 0.09
            if(b.name == "nose") or (b.name == "noseTip"):
                b.envelope_distance = 0.02
            if(b.name == "eyeR") or (b.name == "eyeL"):
                b.envelope_distance = 0.0
            if(b.name.startswith("eyeBase")):
                b.envelope_distance = .08
            if(b.name == "headFore"):
                b.envelope_distance = 0.14
            if(b.name == "neckJ4"):
                b.envelope_distance = .05
            if(b.name.startswith("fixChestFront2")):
                b.envelope_distance = 0.09
            if(b.name.startswith("fixChestCenter2")):
                b.envelope_distance = 0.09
            if(b.name.startswith("fixChestBack2")):
                b.envelope_distance = 0.09
            if(b.name.startswith("shoulder")):
                b.envelope_distance = 0.07
            if(b.name.startswith("arm")):
                b.envelope_distance = 0.07
            if(b.name == "bBackJ1"):
                b.envelope_distance = 0.2
            if(b.name == "bBackJ2"):
                b.envelope_distance = 0.2
            if(b.name == "bBackJ3"):
                b.envelope_distance = 0.22
            if(b.name == "bBackJ4"):
                b.envelope_distance = 0.14
            if(b.name == "bBackJ5"):
                b.envelope_distance = 0.0
                b.envelope_weight = 0.0

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# END COMMON FUNCTION - setEnve1opeWeights
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Start Biped Skeleton LOWER BODY BUILD
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def buildBipedSkeleton():
    n = getSceneObjectNumber() #Each character name is numbered sequentially.
    name = setName('biped', n)
    mod = fmod(n, 2)
    if(mod == 0):
        x = 1.0 * n - mod
    else:
        x = 1.0 * -n - mod
    #
    y = -.4 * n; z = 1.2  # y = Head of handle (Armature point)
    char = buildRootArmature(name, x, y, z) #creates point
    print("biped line - 1787")
    getTypeAndString(name) # gives rgbiped01 with line 1569, in setHandle Character' has no attribute 'VHead'
    char.name = name
    char.x = x; char.y = y; char.z = z
    # %%% FIRST BONE %%% FIRST CHARACTER WILL BE NAMED rgbiped01
    VHead = [0, 0, 0]
    VTail = [0, -.3, 0] # Tail of Handle  
    bone = setHandle(char, VHead, VTail)
    bpy.data.objects[char.name].show_in_front = True
    #
    char.V_angle = (0, 0, 0) # Bottom (Tail)
    char.angle = boneMirror(char, char.V_angle, False)
    char.V_hipC = (0, .1, -.1)
    boneMirror(char, char.V_hipC, False)
    #
    #*** Active bone is NOT right above, but next bone above ***
    bone_name = getActiveBoneName()
    char.armature.edit_bones[bone_name].name = "angle"
    #
    boneMirror(char, char.V_next, False)
    bone_name = getActiveBoneName()
    char.armature.edit_bones[bone_name].name = "hipC"
    # start mirroring! Can't use naming above on mirrored bones
    boneMirror(char, char.V_hip, True)
    boneMirror(char, char.V_femurJ1, True)
    boneMirror(char, char.V_femurJ2, True)
    boneMirror(char, char.V_tibiaJ1, True)
    boneMirror(char, char.V_tibiaJ2, True)
    boneMirror(char, char.V_ankle, True)
    boneMirror(char, char.V_toe, True)
    char.armature.edit_bones["hipC_L"].name = "hip.R"
    char.armature.edit_bones['hipC_R'].name = "hip.L"
    char.armature.edit_bones['hipC_R.001'].name = "femurJ1.L"
    char.armature.edit_bones['hipC_L.001'].name = "femurJ1.R"
    char.armature.edit_bones['hipC_R.002'].name = "femurJ2.L"
    char.armature.edit_bones['hipC_L.002'].name = "femurJ2.R"
    char.armature.edit_bones['hipC_R.003'].name = "tibiaJ1.L"
    char.armature.edit_bones['hipC_L.003'].name = "tibiaJ1.R"    
    char.armature.edit_bones['hipC_R.004'].name = "tibiaJ2.L"
    char.armature.edit_bones['hipC_L.004'].name = "tibiaJ2.R"    
    char.armature.edit_bones['hipC_R.005'].name = "ankle.L"
    char.armature.edit_bones['hipC_L.005'].name = "ankle.R"
    char.armature.edit_bones['hipC_R.006'].name = "toe.L"
    char.armature.edit_bones['hipC_L.006'].name = "toe.R"
    #
    # Heel starts were the tibia ends, same place as the ankle bone
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones["ankle.L"].select_tail=True
    char.armature.edit_bones["ankle.R"].select_tail=True
    boneMirror(char, char.V_heel, True)
    char.armature.edit_bones['ankle.L.001'].name = "heel.L"
    char.armature.edit_bones['ankle.R.001'].name = "heel.R"
    #
    # Reinforce rear
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones["angle"].select_tail=True
    boneMirror(char, char.V_posterior, False)
    boneMirror(char, char.V_posterior1, True)
    boneMirror(char, char.V_posterior2, True)
    #
    bpy.ops.armature.select_all(action='DESELECT')
    selectBonePartByName("angle.001", True) # Tail=True
    V_tailBone = (0, 0, -.14)
    boneMirror(char, char.V_tailBone, False)
    char.armature.edit_bones['angle.001'].name = "Posterior1"
    char.armature.edit_bones['angle.001_L'].name = "fixPosterior1.L"
    char.armature.edit_bones['angle.001_R'].name = "fixPosterior1.R"
    char.armature.edit_bones['angle.001_L.001'].name = "fixPosterior2.L"
    char.armature.edit_bones['angle.001_R.001'].name = "fixPosterior2.R"
    char.armature.edit_bones['angle.002'].name = "fixPosterior2.C"
    #
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # END OF Biped Skeleton LOWER BODY BUILD
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    buildHumanUpperBody(char)
    ob = bpy.data.objects.get(char.name)
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    setEnvelopeWeights(char)
    #
    deselectAll()
    ob = bpy.data.objects.get(char.name)
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.context.object.rotation_euler[2] = -1.5708
    return char

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#  END BIPED SKELETON BUILD
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# COMMON FUNCTION - bui1dHumanUpperBody     To 1779
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def buildHumanUpperBody(char, boneName="angle", V_bBackJ1 = (0, 0, 0.1)):
    bpy.ops.armature.select_all(action='DESELECT')
    getTypeAndString(boneName)
    char.armature.edit_bones[boneName].select_tail=True
    boneMirror(char, char.V_bBackJ1, False)
    boneMirror(char, char.V_bBackJ2, False)
    boneMirror(char, char.V_bBackJ3, False)
    boneMirror(char, char.V_bBackJ4, False)
    boneMirror(char, char.V_bBackJ5, False)
    char.armature.edit_bones[boneName + ".001"].name = "bBackJ1"
    char.armature.edit_bones[boneName + ".002"].name = "bBackJ2"
    char.armature.edit_bones[boneName + ".003"].name = "bBackJ3"
    char.armature.edit_bones[boneName + ".004"].name = "bBackJ4"
    char.armature.edit_bones[boneName + ".005"].name = "bBackJ5"
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Start arms  
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Shoulder area  
    boneMirror(char, char.V_clavicle, True)
    boneMirror(char, char.V_shoulder, True)
    boneMirror(char, char.V_armJ1, True)
    boneMirror(char, char.V_armJ2, True)
    boneMirror(char, char.V_armJ3, True)
    boneMirror(char, char.V_armJ4, True)
    boneMirror(char, char.V_armJ5, True)
    char.armature.edit_bones['bBackJ5_L'].name = "clavicle.R"
    char.armature.edit_bones['bBackJ5_R'].name = "clavicle.L"
    char.armature.edit_bones['bBackJ5_L.001'].name = "shoulder.R"
    char.armature.edit_bones['bBackJ5_R.001'].name = "shoulder.L"
    char.armature.edit_bones['bBackJ5_L.002'].name = "armJ1.R"
    char.armature.edit_bones['bBackJ5_R.002'].name = "armJ1.L"
    char.armature.edit_bones['bBackJ5_L.003'].name = "armJ2.R"
    char.armature.edit_bones['bBackJ5_R.003'].name = "armJ2.L"
    char.armature.edit_bones['bBackJ5_L.004'].name = "armJ3.R"
    char.armature.edit_bones['bBackJ5_R.004'].name = "armJ3.L"
    char.armature.edit_bones['bBackJ5_L.005'].name = "armJ4.R"
    char.armature.edit_bones['bBackJ5_R.005'].name = "armJ4.L"
    char.armature.edit_bones['bBackJ5_L.006'].name = "armJ5.R"
    char.armature.edit_bones['bBackJ5_R.006'].name = "armJ5.L"
    # Middle finger  
    boneMirror(char, char.V_wristBase2, True)
    boneMirror(char, char.V_midJ1, True)
    boneMirror(char, char.V_midJ2, True)
    boneMirror(char, char.V_midJ3, True)
    char.armature.edit_bones['armJ5.L.001'].name = "wristBase2.L"
    char.armature.edit_bones['armJ5.R.001'].name = "wristBase2.R"
    char.armature.edit_bones['armJ5.L.002'].name = "midJ1.L"
    char.armature.edit_bones['armJ5.R.002'].name = "midJ1.R"
    char.armature.edit_bones['armJ5.L.003'].name = "midJ2.L"
    char.armature.edit_bones['armJ5.R.003'].name = "midJ2.R"
    char.armature.edit_bones['armJ5.L.004'].name = "midJ3.L"
    char.armature.edit_bones['armJ5.R.004'].name = "midJ3.R"
    # Shift back to wrist
    # Index Finger bones   
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones["armJ5.R"].select_tail=True
    boneMirror(char, char.V_wristBase1, True)
    boneMirror(char, char.V_indexJ1, True)
    boneMirror(char, char.V_indexJ2, True)
    boneMirror(char, char.V_indexJ3, True)
    char.armature.edit_bones['armJ5.L.001'].name = "wristBase1.L"
    char.armature.edit_bones['armJ5.R.001'].name = "wristBase1.R"
    char.armature.edit_bones['armJ5.L.002'].name = "indexJ1.L"
    char.armature.edit_bones['armJ5.R.002'].name = "indexJ1.R"
    char.armature.edit_bones['armJ5.L.003'].name = "indexJ2.L"
    char.armature.edit_bones['armJ5.R.003'].name = "indexJ2.R"
    char.armature.edit_bones['armJ5.L.004'].name = "indexJ3.L"
    char.armature.edit_bones['armJ5.R.004'].name = "indexJ3.R"
    #
    # Shift back to wrist
    # Ring Finger bones
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones["armJ5.R"].select_tail=True
    boneMirror(char, char.V_wristBase3, True)
    boneMirror(char, char.V_ringJ1, True)
    boneMirror(char, char.V_ringJ2, True)
    boneMirror(char, char.V_ringJ3, True)
    char.armature.edit_bones['armJ5.L.001'].name = "wristBase3.L"
    char.armature.edit_bones['armJ5.R.001'].name = "wristBase3.R"
    char.armature.edit_bones['armJ5.L.002'].name = "ringJ1.L"
    char.armature.edit_bones['armJ5.R.002'].name = "ringJ1.R"
    char.armature.edit_bones['armJ5.L.003'].name = "ringJ2.L"
    char.armature.edit_bones['armJ5.R.003'].name = "ringJ2.R"
    char.armature.edit_bones['armJ5.L.004'].name = "ringJ3.L"
    char.armature.edit_bones['armJ5.R.004'].name = "ringJ3.R"
    # Shift back to wrist
    # Pinky Finger bones  
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones["armJ5.R"].select_tail=True
    boneMirror(char, char.V_pinkyBase, True)
    boneMirror(char, char.V_pinkyJ1, True)
    boneMirror(char, char.V_pinkyJ2, True)
    boneMirror(char, char.V_pinkyJ3, True)
    char.armature.edit_bones['armJ5.L.001'].name = "wristBase4.L"
    char.armature.edit_bones['armJ5.R.001'].name = "wristBase4.R"
    char.armature.edit_bones['armJ5.L.002'].name = "pinkyJ1.L"
    char.armature.edit_bones['armJ5.R.002'].name = "pinkyJ1.R"
    char.armature.edit_bones['armJ5.L.003'].name = "pinkyJ2.L"
    char.armature.edit_bones['armJ5.R.003'].name = "pinkyJ2.R"
    char.armature.edit_bones['armJ5.L.004'].name = "pinkyJ3.L"
    char.armature.edit_bones['armJ5.R.004'].name = "pinkyJ3.R"
    #
    # Shift back to wrist
    # Thumb Finger bones
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones["armJ5.R"].select_tail=True
    boneMirror(char, char.V_thumbBase, True)
    boneMirror(char, char.V_thumbJ1, True)
    boneMirror(char, char.V_thumbJ2, True)
    boneMirror(char, char.V_thumbJ3, True)
    char.armature.edit_bones['armJ5.L.001'].name = "thumbBase.L"
    char.armature.edit_bones['armJ5.R.001'].name = "thumbBase.R"
    char.armature.edit_bones['armJ5.L.002'].name = "thumbJ1.L"
    char.armature.edit_bones['armJ5.R.002'].name = "thumbJ1.R"
    char.armature.edit_bones['armJ5.L.003'].name = "thumbJ2.L"
    char.armature.edit_bones['armJ5.R.003'].name = "thumbJ2.R"
    char.armature.edit_bones['armJ5.L.004'].name = "thumbJ3.L"
    char.armature.edit_bones['armJ5.R.004'].name = "thumbJ3.R"
    # End arm and hand creation
    #
    # Resume spine
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones["bBackJ5"].select_tail=True
    boneMirror(char, char.V_neckJ1, False)
    boneMirror(char, char.V_neckJ2, False)
    boneMirror(char, char.V_neckJ3, False)
    boneMirror(char, char.V_neckJ4, False)
    boneMirror(char, char.V_headBase, False)
    boneMirror(char, char.V_eyeLevel, False)
    boneMirror(char, char.V_headTop, False)
    boneMirror(char, char.V_headFore, False)
    char.armature.edit_bones['bBackJ5.001'].name = "neckJ1"
    char.armature.edit_bones['bBackJ5.002'].name = "neckJ2"
    char.armature.edit_bones['bBackJ5.003'].name = "neckJ3"
    char.armature.edit_bones['bBackJ5.004'].name = "neckJ4"
    char.armature.edit_bones['bBackJ5.005'].name = "headBase"
    char.armature.edit_bones['bBackJ5.006'].name = "eyeLevel"
    char.armature.edit_bones['bBackJ5.007'].name = "headTop"
    char.armature.edit_bones['bBackJ5.008'].name = "headFore"
    # jaw
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones["neckJ4"].select_tail=True
    boneMirror(char, char.V_jaw, False)
    boneMirror(char, char.V_jaw1, True)
    boneMirror(char, char.V_jaw2, True)
    char.armature.edit_bones['neckJ4.001'].name = "jaw"
    char.armature.edit_bones['neckJ4.001_R'].name = "jaw1.L"
    char.armature.edit_bones['neckJ4.001_L'].name = "jaw1.R"
    char.armature.edit_bones['neckJ4.001_R.001'].name = "jaw2.L"
    char.armature.edit_bones['neckJ4.001_L.001'].name = "jaw2.R"
    # upperMouth
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones["neckJ4"].select_tail=True
    boneMirror(char, char.V_baseMouth1, False)
    boneMirror(char, char.V_baseMouth2, True)
    boneMirror(char, char.V_baseMouth3, True)
    char.armature.edit_bones['neckJ4.001'].name = "baseMouth1"
    char.armature.edit_bones['neckJ4.001_R'].name = "baseMouth2.L"
    char.armature.edit_bones['neckJ4.001_L'].name = "baseMouth2.R"
    char.armature.edit_bones['neckJ4.001_R.001'].name = "baseMouth3.L"
    char.armature.edit_bones['neckJ4.001_L.001'].name = "baseMouth3.R"
    #
    # Eye Level
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones["eyeLevel"].select_tail=True
    boneMirror(char, char.V_eyebase, True)
    boneMirror(char, char.V_eye, True)
    char.armature.edit_bones['eyeLevel_L'].name = "eyeBase.L"
    char.armature.edit_bones['eyeLevel_R'].name = "eyeBase.R"
    char.armature.edit_bones['eyeLevel_L.001'].name = "eye.L"
    char.armature.edit_bones['eyeLevel_R.001'].name = "eye.R"
    # nose
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones["headBase"].select_tail=True
    boneMirror(char, char.V_noseBase, False)
    boneMirror(char, char.V_nose, False)
    char.armature.edit_bones['headBase.001'].name = "noseBase"
    char.armature.edit_bones['headBase.002'].name = "nose"
    #
    # Add front fix
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones["bBackJ5"].select_tail=True
    boneMirror(char, char.V_fixChestFront, False)    
    boneMirror(char, char.V_fixChestFront1, True)
    boneMirror(char, char.V_fixChestFront2, True)
    char.armature.edit_bones['bBackJ5.001'].name = "fixChestFront"
    char.armature.edit_bones['bBackJ5.001_R'].name = "fixChestFront1.L"
    char.armature.edit_bones['bBackJ5.001_L'].name = "fixChestFront1.R"
    char.armature.edit_bones['bBackJ5.001_R.001'].name = "fixChestFront2.L"
    char.armature.edit_bones['bBackJ5.001_L.001'].name = "fixChestFront2.R"
    # Add center fix
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones["bBackJ5"].select_tail=True
    boneMirror(char, char.V_fixChestCenter1, True)
    boneMirror(char, char.V_fixChestCenter2, True)
    char.armature.edit_bones['bBackJ5_R'].name = "fixChestCenter1.L"
    char.armature.edit_bones['bBackJ5_L'].name = "fixChestCenter1.R"
    char.armature.edit_bones['bBackJ5_R.001'].name = "fixChestCenter2.L"
    char.armature.edit_bones['bBackJ5_L.001'].name = "fixChestCenter2.R"
    # Add rear fix
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones["bBackJ5"].select_head=True
    boneMirror(char, char.V_fixChestBack, False)    
    boneMirror(char, char.V_fixChestBack1, True)
    boneMirror(char, char.V_fixChestBack2, True)
    char.armature.edit_bones['bBackJ5.001'].name = "fixChestBack"
    char.armature.edit_bones['bBackJ5.001_R'].name = "fixChestBack1.L"
    char.armature.edit_bones['bBackJ5.001_L'].name = "fixChestBack1.R"
    char.armature.edit_bones['bBackJ5.001_R.001'].name = "fixChestBack2.L"
    char.armature.edit_bones['bBackJ5.001_L.001'].name = "fixChestBack2.R"
    #
    # Upper shoulder
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones["bBackJ5"].select_tail=True
    boneMirror(char, char.V_fixUpperShoulder1, False)
    boneMirror(char, char.V_fixUpperShoulder2, True)
    char.armature.edit_bones['bBackJ5.001'].name = "fixShoulderBack.L"
    char.armature.edit_bones['bBackJ5.001_R'].name = "fixShoulderBack1.L"
    char.armature.edit_bones['bBackJ5.001_L'].name = "fixShoulderBack1.R"

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# END COMMON FUNCTION - bui1dHumanUpperBody
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|
#|
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# BEGIN CENTAUR SECTION
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def buildCentaurSkeleton():
    n = getSceneObjectNumber()  # Each character name is numbered sequentially.
    name = setName('centaur', n) #biped, centaur, bird, centaur, spider. kangaroo?
    mod = math.fmod(n, 2)
    if(mod == 0):
        x = 1.1 * n - mod
    else:
        x = 1.1 * -n - mod
    y = -.4 * n; z = 1.14  # For Armature
    char = buildRootArmature(name, x, y, z) # Start character armature and bones
    char.name = name # gives rgcentaur02
    char.x = x; char.y = y; char.z = z
    #addCharactersProperties() # TODO this may need to be created after call to buildRoootArmature
    # Build root bone
    VHead = [0, 0, 0] # TODO check
    VTail = [0, 0, 0.3]  # End location of handle relative to armature origin - this effects coordinate system
    bone = setHandle(char, VHead, VTail)
    #
    buildQuadrupedBase(char) # Start building base of Centaur from the quadruped code
    #
    V_bBackJ1 = (0, .032, 0.1)
    buildHumanUpperBody(char, "qBackJ0", V_bBackJ1) # Steal the code from the biped
    setEnvelopeWeights(char) # WAS char.armature.name[:-3]) 
    #
    ob = bpy.context.object
    deselectAll()
    bpy.data.objects[name].location[2] = z  # 1.14               # WAS char.armature.name[:-3]].location[2] = z  # 1.14
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.view_layer.objects.active = ob
    bpy.data.objects[name].select_set(True)   # WAS char.armature.name[:-3]].select_set(True)
    context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.context.object.rotation_euler[2] = -1.5708

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# COMMON FUNCTION - buildQuadrupedBaase (shared between Centaur and quadruped)
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def buildQuadrupedBase(char):
    bpy.ops.object.mode_set(mode='EDIT')
    V_origin = (0, 0, 0)
    V_qBackJ0 = (0, .2, 0)
    qBackJ0 = createBone("qBackJ0", V_origin, V_qBackJ0, 0)
    deselectAll()
    selectBonePartByName("qBackJ0", tail=True)
    boneMirror(char, char.V_join, False)
    boneMirror(char, char.V_drop, False)
    boneMirror(char, char.V_pelvis, False)
    char.armature.edit_bones["qBackJ0.001"].name = "join"
    char.armature.edit_bones["qBackJ0.002"].name = "drop"
    char.armature.edit_bones["qBackJ0.003"].name = "pelvis"
    # 
    # Start mirroring
    V_hip = (0.12, 0, 0)
    boneMirror(char, V_hip, True)
    V_femurJ1 = (0, 0, -.18)
    boneMirror(char, V_femurJ1, True)
    V_femurJ2 = (0, 0, -.16)
    boneMirror(char, V_femurJ2, True)
    V_tibiaJ1 = (0, 0, -.1)
    boneMirror(char, V_tibiaJ1, True)
    V_tibiaJ2 = (0, 0, -.1)
    boneMirror(char, V_tibiaJ2, True)
    V_ankle = (0, .046, -.08)
    boneMirror(char, V_ankle, True)
    V_toe = (0, .09, -.07)
    boneMirror(char, V_toe, True)
    char.armature.edit_bones["pelvis_R"].name = "hip.L"
    char.armature.edit_bones['pelvis_L'].name = "hip.R"
    char.armature.edit_bones['pelvis_R.001'].name = "femurJ1.L"
    char.armature.edit_bones['pelvis_L.001'].name = "femurJ1.R"
    char.armature.edit_bones['pelvis_R.002'].name = "femurJ2.L"
    char.armature.edit_bones['pelvis_L.002'].name = "femurJ2.R"
    char.armature.edit_bones['pelvis_R.003'].name = "tibiaJ1.L"
    char.armature.edit_bones['pelvis_L.003'].name = "tibiaJ1.R"    
    char.armature.edit_bones['pelvis_R.004'].name = "tibiaJ2.L"
    char.armature.edit_bones['pelvis_L.004'].name = "tibiaJ2.R"    
    char.armature.edit_bones['pelvis_R.005'].name = "ankle.L"
    char.armature.edit_bones['pelvis_L.005'].name = "ankle.R"
    char.armature.edit_bones['pelvis_R.006'].name = "toe.L"
    char.armature.edit_bones['pelvis_L.006'].name = "toe.R"
    #
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones["qBackJ0"].select_head=True
    V_qBackJ1 = (0, -0.14, -.06)
    boneMirror(char, V_qBackJ1, False)
    V_qBackJ2 = (0, -.11, 0)
    boneMirror(char, V_qBackJ2, False)
    V_qBackJ3 = (0, -.12, .02)
    boneMirror(char, V_qBackJ3, False)
    V_qBackJ4 = (0, -.12, .02)
    boneMirror(char, V_qBackJ4, False)
    V_qBackJ5 = (0, -.14, .01)
    boneMirror(char, V_qBackJ5, False)
    char.armature.edit_bones['qBackJ0.001'].name = "qBackJ1"
    char.armature.edit_bones['qBackJ0.002'].name = "qBackJ2"
    char.armature.edit_bones['qBackJ0.003'].name = "qBackJ3"
    char.armature.edit_bones['qBackJ0.004'].name = "qBackJ4"
    char.armature.edit_bones['qBackJ0.005'].name = "qBackJ5"
    #
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones["qBackJ1"].select_head=True
    V_qfixRib1Top = (.1, 0, -.04)
    boneMirror(char, V_qfixRib1Top, True)
    V_qfixRib1B = (0, -.06, -0.4)
    boneMirror(char, V_qfixRib1B, True)
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones["qBackJ1"].select_tail=True
    V_qfixRib2Top = (.1, .02, 0)
    boneMirror(char, V_qfixRib2Top, True)
    V_qfixRib2B = (0, -.06, -.4)
    boneMirror(char, V_qfixRib2B, True)
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones["qBackJ3"].select_tail=True
    V_qfixRib3Top = (.1, 0, 0)
    boneMirror(char, V_qfixRib3Top, True)
    V_qfixRib3B = (0, 0, -.38)
    boneMirror(char, V_qfixRib3B, True)
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones["qBackJ4"].select_tail=True
    V_qfixRib4Top = (.1, 0, 0)
    boneMirror(char, V_qfixRib4Top, True)
    V_qfixRib4B = (0, 0, -.36)
    boneMirror(char, V_qfixRib4B, True)  
    char.armature.edit_bones['qBackJ1_R'].name = "qfixRib1Top.L"
    char.armature.edit_bones['qBackJ1_L'].name = "qfixRib1Top.R"
    char.armature.edit_bones['qBackJ1_R.001'].name = "qfixRib1B.L"
    char.armature.edit_bones['qBackJ1_L.001'].name = "qfixRib1B.R"
    char.armature.edit_bones['qBackJ1_R.002'].name = "qfixRib2Top.L"
    char.armature.edit_bones['qBackJ1_L.002'].name = "qfixRib2Top.R"
    char.armature.edit_bones['qBackJ1_R.003'].name = "qfixRib2B.L"
    char.armature.edit_bones['qBackJ1_L.003'].name = "qfixRib2B.R"
    char.armature.edit_bones['qBackJ3_R'].name = "qfixRib3Top.L"
    char.armature.edit_bones['qBackJ3_L'].name = "qfixRib3Top.R"
    char.armature.edit_bones['qBackJ3_R.001'].name = "qfixRib3B.L"
    char.armature.edit_bones['qBackJ3_L.001'].name = "qfixRib3B.R"
    char.armature.edit_bones['qBackJ4_R'].name = "qfixRib4Top.L"
    char.armature.edit_bones['qBackJ4_L'].name = "qfixRib4Top.R"
    char.armature.edit_bones['qBackJ4_R.001'].name = "qfixRib4B.L"
    char.armature.edit_bones['qBackJ4_L.001'].name = "qfixRib4B.R"
    #  
    # Create Rump with more fixs
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones["qBackJ5"].select_tail=True
    V_hRumpJ1 = (0, -.16, -.004)
    boneMirror(char, V_hRumpJ1, False)
    V_hRumpJ2 = (0, -.12, -.004)
    boneMirror(char, V_hRumpJ2, False)
    V_hRumpJ3 = (0, -.05, 0)
    boneMirror(char, V_hRumpJ3, False)
    char.armature.edit_bones['qBackJ5.001'].name = "hRumpJ1"
    char.armature.edit_bones['qBackJ5.002'].name = "hRumpJ2"
    char.armature.edit_bones['qBackJ5.003'].name = "hRumpJ3"
    #
    V_hTailJ1 = (0, -.04, .0146)
    boneMirror(char, V_hTailJ1, False)
    V_hTailJ2 = (0, -.06, .012)
    boneMirror(char, V_hTailJ2, False)
    V_hTailJ3 = (0, -.06, .01)
    boneMirror(char, V_hTailJ3, False)
    V_hTailJ4 = (0, -.06, 0)
    boneMirror(char, V_hTailJ4, False)
    V_hTailJ5 = (0, -.06, 0)
    boneMirror(char, V_hTailJ5, False)
    V_hTailJ6 = (0, -.06, 0)
    boneMirror(char, V_hTailJ6, False)
    V_hTailJ7 = (0, -.06, 0)
    boneMirror(char, V_hTailJ7, False)
    V_hTailJ8 = (0, -.06, 0)
    boneMirror(char, V_hTailJ8, False)
    V_hTailJ9 = (0, -.06, 0)
    boneMirror(char, V_hTailJ9, False)
    char.armature.edit_bones['hRumpJ3.001'].name = "hTailJ1"
    char.armature.edit_bones['hRumpJ3.002'].name = "hTailJ2"
    char.armature.edit_bones['hRumpJ3.003'].name = "hTailJ3"
    char.armature.edit_bones['hRumpJ3.004'].name = "hTailJ4"
    char.armature.edit_bones['hRumpJ3.005'].name = "hTailJ5"
    char.armature.edit_bones['hRumpJ3.006'].name = "hTailJ6"
    char.armature.edit_bones['hRumpJ3.007'].name = "hTailJ7"
    char.armature.edit_bones['hRumpJ3.008'].name = "hTailJ8"
    char.armature.edit_bones['hRumpJ3.009'].name = "hTailJ9"
    # Add rear stabilization
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones["hRumpJ1"].select_tail=True
    V_hRumpfix1 = (0, -.04, -.2)
    boneMirror(char, V_hRumpfix1, False)
    V_hRumpfix2 = (0, .12, -.06)
    boneMirror(char, V_hRumpfix2, False)
    V_hRumpfix3 = (0, .15, -.07)
    boneMirror(char, V_hRumpfix3, False)
    char.armature.edit_bones['hRumpJ1.001'].name = "fixRump1"
    char.armature.edit_bones['hRumpJ1.002'].name = "fixRump2"
    char.armature.edit_bones['hRumpJ1.003'].name = "fixRump3"
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones["hRumpJ2"].select_tail=True
    V_hRumpfix3 = (0, .14, .05)
    boneMirror(char, V_hRumpfix3, False)
    V_hRumpfix4 = (0, .2, .04)
    boneMirror(char, V_hRumpfix4, False)
    char.armature.edit_bones['hRumpJ2.001'].name = "fixSacrum1"
    char.armature.edit_bones['hRumpJ2.002'].name = "fixSacrum2"
    #
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones["qBackJ5"].select_tail=True
    V_rearHip = (.16, 0, 0)
    boneMirror(char, V_rearHip, True)
    V_qfix4 = (0, -.16, -.11)
    boneMirror(char, V_qfix4, True)
    V_qfix5 = (0, 0, -.12)
    boneMirror(char, V_qfix5, True)
    char.armature.edit_bones['qBackJ5_L'].name = "rearHip.R"
    char.armature.edit_bones['qBackJ5_R'].name = "rearHip.L"
    char.armature.edit_bones['qBackJ5_R.001'].name = "qfixHind1.L"
    char.armature.edit_bones['qBackJ5_L.001'].name = "qfixHind1.R"
    char.armature.edit_bones['qBackJ5_R.002'].name = "qfixHind2.L"
    char.armature.edit_bones['qBackJ5_L.002'].name = "qfixHind2.R"
    #
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones["rearHip.L"].select_tail=True
    V_rearHipJ1 = (0, -.08, -.27)
    boneMirror(char, V_rearHipJ1, True)
    V_rearFemurJ1 = (0, -.08, -.2)
    boneMirror(char, V_rearFemurJ1, True)
    V_rearFemurJ2 = (0, -.08, -.2)
    boneMirror(char, V_rearFemurJ2, True)
    V_rearTibiaJ1 = (0, 0, -.15)
    boneMirror(char, V_rearTibiaJ1, True)
    V_rearTibiaJ2 = (0, 0, -.15)
    boneMirror(char, V_rearTibiaJ2, True)
    V_horseRRearAnkle = (0, .06, -.07)
    boneMirror(char, V_horseRRearAnkle, True)
    V_horseRToe = (0, .04, -.06)
    boneMirror(char, V_horseRToe, True)
    char.armature.edit_bones['rearHip.L.001'].name = "rearHipJ1.L"
    char.armature.edit_bones['rearHip.R.001'].name = "rearHipJ1.R"
    char.armature.edit_bones['rearHip.L.002'].name = "rearFemurJ1.L"
    char.armature.edit_bones['rearHip.R.002'].name = "rearFemurJ1.R"
    char.armature.edit_bones['rearHip.L.003'].name = "rearFemurJ2.L"
    char.armature.edit_bones['rearHip.R.003'].name = "rearFemurJ2.R"
    char.armature.edit_bones['rearHip.L.004'].name = "rearTibiaJ1.L"
    char.armature.edit_bones['rearHip.R.004'].name = "rearTibiaJ1.R"
    char.armature.edit_bones['rearHip.L.005'].name = "rearTibiaJ2.L"
    char.armature.edit_bones['rearHip.R.005'].name = "rearTibiaJ2.R"
    char.armature.edit_bones['rearHip.L.006'].name = "rearAnkle.L"
    char.armature.edit_bones['rearHip.R.006'].name = "rearAnkle.R"
    char.armature.edit_bones['rearHip.L.007'].name = "rearToe.L"
    char.armature.edit_bones['rearHip.R.007'].name = "rearToe.R"
    #
    deselectAll()
    selectBonePartByName("qBackJ0", tail=True)

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# END COMMON FUNCTION - buildQuadrupedBaase
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# END CENTAUR SECTION
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# BEGIN QUADRUPED SECTION
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def buildQuadrupedSkeleton():
    n = getSceneObjectNumber()
    name = setName('quadruped', n) 
    mod = math.fmod(n, 2)
    if(mod == 0):
        x = 1.1 * n - mod
    else:
        x = 1.1 * -n - mod
    y = -.4 * n; z = 1.04  # For Armature
    char = buildRootArmature(name, x, y, z) 
    char.name = name # gives rgcentaur02
    char.x = x; char.y = y; char.z = z
    #addCharactersProperties() # TODO this may need to be created after call to buildRoootArmature
    # Build root bone
    VHead = [0, 0, 0] # TODO check
    VTail = [0, 0, 0.3]  # End location of handle relative to armature origin - this effects coordinate system
    bone = setHandle(char, VHead, VTail)
    #
    buildQuadrupedBase(char) # Start building base of Centaur from the quadruped code
    # charClass.rig.show_in_front = True
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # BUILD HEAD AND NECK
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones["qBackJ0"].select_tail=True
    V_qNeckJ1 = (0, .05, 0.1)
    boneMirror(char, V_qNeckJ1, False)   # boneMirror(char, V_rearTibiaJ2, True)
    V_qNeckJ2 = (0, .05, 0.1)
    boneMirror(char, V_qNeckJ2, False)
    V_qNeckJ3 = (0, .05, 0.14)
    boneMirror(char, V_qNeckJ3, False)
    V_qNeckJ4 = (0, .05, .1)
    boneMirror(char, V_qNeckJ4, False)
    V_qNeckJ5 = (0, .05, .1)
    boneMirror(char, V_qNeckJ5, False)
    V_qNeckJ6 = (0, .05, .1)
    boneMirror(char, V_qNeckJ6, False)
    char.armature.edit_bones['qBackJ0.001'].name = "bNeckJ1"
    char.armature.edit_bones['qBackJ0.002'].name = "bNeckJ2"
    char.armature.edit_bones['qBackJ0.003'].name = "bNeckJ3"
    char.armature.edit_bones['qBackJ0.004'].name = "bNeckJ4"
    char.armature.edit_bones['qBackJ0.005'].name = "bNeckJ5"
    char.armature.edit_bones['qBackJ0.006'].name = "bNeckJ6"
    #
    # Start head
    V_headBase = (0, 0, 0.09)
    boneMirror(char, V_headBase, False)
    V_eyeLevel = (0, 0, .04)
    boneMirror(char, V_eyeLevel, False)
    V_headTop = (0, -.05, 0)
    boneMirror(char, V_headTop, False)
    V_headFore = (0, .08, .09)
    boneMirror(char, V_headFore, False)
    char.armature.edit_bones['bNeckJ6.001'].name = "headBase"
    char.armature.edit_bones['bNeckJ6.002'].name = "eyeLevel"
    char.armature.edit_bones['bNeckJ6.003'].name = "headTop"
    char.armature.edit_bones['bNeckJ6.004'].name = "headFore"
    # ears
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones["eyeLevel"].select_tail=True
    V_earRoot = (.05, -.06, .06)
    boneMirror(char, V_earRoot, True)
    V_earBase = (0, -.02, .02)
    boneMirror(char, V_earBase, True)
    V_earJ1 = (0, -.015, .015)
    boneMirror(char, V_earJ1, True)
    V_earJ2 = (0, -.015, .015)
    boneMirror(char, V_earJ2, True)
    V_earJ3 = (0, -.015, .015)
    boneMirror(char, V_earJ3, True)
    V_earJ4 = (0, -.015, .015)
    boneMirror(char, V_earJ4, True)
    V_earJ5 = (0, -.015, .015)
    boneMirror(char, V_earJ5, True)
    char.armature.edit_bones['eyeLevel_R'].name = "earRoot.L"
    char.armature.edit_bones['eyeLevel_L'].name = "earRoot.R"
    char.armature.edit_bones['eyeLevel_R.001'].name = "earBase.L"
    char.armature.edit_bones['eyeLevel_L.001'].name = "earBase.R"
    char.armature.edit_bones['eyeLevel_R.002'].name = "earJ1.L"
    char.armature.edit_bones['eyeLevel_L.002'].name = "earJ1.R"
    char.armature.edit_bones['eyeLevel_R.003'].name = "earJ2.L"
    char.armature.edit_bones['eyeLevel_L.003'].name = "earJ2.R"
    char.armature.edit_bones['eyeLevel_R.004'].name = "earJ3.L"
    char.armature.edit_bones['eyeLevel_L.004'].name = "earJ3.R"
    char.armature.edit_bones['eyeLevel_R.005'].name = "earJ4.L"
    char.armature.edit_bones['eyeLevel_L.005'].name = "earJ4.R"
    char.armature.edit_bones['eyeLevel_R.006'].name = "earJ5.L"
    char.armature.edit_bones['eyeLevel_L.006'].name = "earJ5.R"
    # jaw
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones["bNeckJ6"].select_tail=True
    V_baseJaw = (0, .02, 0) 
    boneMirror(char, V_baseJaw, False)
    V_jaw = (0, .02, 0)
    boneMirror(char, V_jaw, False)
    V_jaw1 = (.03, .01, 0)
    boneMirror(char, V_jaw1, True)
    V_jaw2 = (-.02, .07, 0)
    boneMirror(char, V_jaw2, True)
    char.armature.edit_bones['bNeckJ6.001'].name = "baseJaw"
    char.armature.edit_bones['bNeckJ6.002'].name = "jaw"
    char.armature.edit_bones['bNeckJ6.002_R'].name = "jaw1.L"
    char.armature.edit_bones['bNeckJ6.002_L'].name = "jaw1.R"
    #
    # Eye Level
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones["eyeLevel"].select_tail=True
    V_eyebase = (-.03, 0.1, 0)
    boneMirror(char, V_eyebase, True)
    V_eye = (0, 0.03, 0)
    boneMirror(char, V_eye, True)
    char.armature.edit_bones['eyeLevel_L'].name = "eyeBase.L"
    char.armature.edit_bones['eyeLevel_R'].name = "eyeBase.R"
    char.armature.edit_bones['eyeLevel_L.001'].name = "eye.L"
    char.armature.edit_bones['eyeLevel_R.001'].name = "eye.R"
    # nose
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones["headBase"].select_tail=True
    V_noseBase = (0, .138, 0)
    boneMirror(char, V_noseBase, False)
    V_nose = (0, 0.02, -.02)
    boneMirror(char, V_nose, False)
    char.armature.edit_bones['headBase.001'].name = "noseBase"
    char.armature.edit_bones['headBase.002'].name = "nose"
    #
    setEnvelopeWeights(char)
    #
    deselectAll()
    bpy.data.objects[name].location[2] = 1.14  # z
    bpy.ops.object.mode_set(mode='OBJECT')
    ob = bpy.data.objects.get(char.name)
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.context.object.rotation_euler[2] = -1.5708

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# END QUADRUPED SECTION
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# BEGIN BIRD SECTION
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def buildBirdSkeleton():
    n = getSceneObjectNumber()
    name = setName('bird', n) 
    mod = math.fmod(n, 2)
    if(mod == 0):
        x = 1.1 * n - mod
    else:
        x = 1.1 * -n - mod
    y = -.4 * n; z = 1.39  # For Armature
    char = buildRootArmature(name, x, y, z) 
    char.name = name # gives rgcentaur02
    char.x = x; char.y = y; char.z = z
    #addCharactersProperties()
    # Build root bone
    VHead = [0, 0, 0]
    VTail = [0.0, -0.3, 0]  # End location of handle relative to armature origin - this effects coordinate system
    bone = setHandle(char, VHead, VTail)
    # charClass.rig.show_in_front = True
    #
    V_origin = (0, 0, 0)
    VbackCenterTip = (0, -0.1, -.15)
    backCenter = createBone("backCenter", V_origin, VbackCenterTip)
    backCenter.parent = char.armature.edit_bones[char.name + '_bone']
    VbackL1 = (0, -0.15, -.15)
    boneMirror(char, VbackL1, False)
    VbackL2 = (0, -0.1, -.1)
    boneMirror(char, VbackL2, False)
    VbackL3 = (0, -0.1, -.04)
    boneMirror(char, VbackL3, False)
    VTailJ1 = (0, -0.1, -.04)
    boneMirror(char, VTailJ1, False)    
    VTailJ2 = (0, -.1, 0)
    boneMirror(char, VTailJ2, False)
    VTailJ3 = (0, -.06, 0)
    boneMirror(char, VTailJ3, False)
    char.armature.edit_bones['backCenter.001'].name = "backL1"
    char.armature.edit_bones['backCenter.002'].name = "backL2"
    char.armature.edit_bones['backCenter.003'].name = "backL3"
    char.armature.edit_bones['backCenter.004'].name = "tailJ1"
    char.armature.edit_bones['backCenter.005'].name = "tailJ2"
    char.armature.edit_bones['backCenter.006'].name = "tailJ3"
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones["tailJ3"].select_tail=True
    Vfb1 = (0.022, .024, 0)
    boneMirror(char, Vfb1, True)
    Vfb2 = (0.022, .024, 0)
    boneMirror(char, Vfb2, True)
    Vfb3 = (0.022, .024, 0)
    boneMirror(char, Vfb3, True)
    Vfb4 = (0.022, .024, 0)
    boneMirror(char, Vfb4, True)
    char.armature.edit_bones['tailJ3_R'].name = "fb1.L" # fb = feather base
    char.armature.edit_bones['tailJ3_L'].name = "fb1.R"
    char.armature.edit_bones['tailJ3_R.001'].name = "fb2.L"
    char.armature.edit_bones['tailJ3_L.001'].name = "fb2.R"
    char.armature.edit_bones['tailJ3_R.002'].name = "fb3.L"
    char.armature.edit_bones['tailJ3_L.002'].name = "fb3.R"
    char.armature.edit_bones['tailJ3_R.003'].name = "fb4.L"
    char.armature.edit_bones['tailJ3_L.003'].name = "fb4.R"
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones["tailJ3"].select_tail=True
    Vfa1 = (0, -.08, 0)  
    boneMirror(char, Vfa1, False)  # fa = Feather attach
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones["fb1.R"].select_tail=True
    Vfa2 = (0, -.08, 0)  
    boneMirror(char, Vfa2, True)
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones["fb2.R"].select_tail=True
    Vfa3 = (0, -.08, 0)  
    boneMirror(char, Vfa3, True)
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones["fb3.R"].select_tail=True
    Vfa3 = (0, -.08, 0)  
    boneMirror(char, Vfa3, True)
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones["fb4.R"].select_tail=True
    Vfa4 = (0, -.08, 0)  
    boneMirror(char, Vfa4, True)
    char.armature.edit_bones['tailJ3.001'].name = "faMiddle"
    char.armature.edit_bones['fb1.L.001'].name = "fa1.L"
    char.armature.edit_bones['fb1.R.001'].name = "fa1.R"
    char.armature.edit_bones['fb2.L.001'].name = "fa2.L"
    char.armature.edit_bones['fb2.R.001'].name = "fa2.R"
    char.armature.edit_bones['fb3.L.001'].name = "fa3.L"
    char.armature.edit_bones['fb3.R.001'].name = "fa3.R"
    char.armature.edit_bones['fb4.L.001'].name = "fa4.L"
    char.armature.edit_bones['fb4.R.001'].name = "fa4.R"
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Start Top part of spine  
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    bpy.ops.armature.select_all(action='DESELECT')
    V_origin = (0, 0, 0)
    Vneck01 = (0, .12, -.02)
    b = createBone("neck01", V_origin, Vneck01)
    b.parent = char.armature.edit_bones['backCenter']
    Vneck02 = (0, .04, 0.04)
    boneMirror(char, Vneck02, False)
    Vneck03 = (0, .03, .04)
    boneMirror(char, Vneck03, False)
    Vneck04 = (0, .02, .04)
    boneMirror(char, Vneck04, False)
    Vneck05 = (0, 0, .04)
    boneMirror(char, Vneck05, False)
    Vneck06 = (0, 0, .04)
    boneMirror(char, Vneck06, False)
    VheadBase = (0, -.03, .05)
    boneMirror(char, VheadBase, False)
    char.armature.edit_bones['neck01.001'].name = "neck02"
    char.armature.edit_bones['neck01.002'].name = "neck03"
    char.armature.edit_bones['neck01.003'].name = "neck04"
    char.armature.edit_bones['neck01.004'].name = "neck05"
    char.armature.edit_bones['neck01.005'].name = "neck06"
    char.armature.edit_bones['neck01.006'].name = "headBase"
    #
    VheadTop = (0, 0.17, .03)
    boneMirror(char, VheadTop, False)
    Vcrest = (0, -.1, .08)
    boneMirror(char, Vcrest, False)
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones['headBase.001'].name = "headTop"
    char.armature.edit_bones['headBase.002'].name = "crest"
    #
    char.armature.edit_bones["neck06"].select_tail=True
    Vjaw1 = (0, .08, -.03)
    boneMirror(char, Vjaw1, False)
    Vjaw2 = (0, .03, -.05)
    boneMirror(char, Vjaw2, False)
    Vjaw3 = (0, 0.109, .053)
    boneMirror(char, Vjaw3, False)
    Vjaw4 = (0, 0.13, -.028)
    boneMirror(char, Vjaw4, False)
    Vjaw4 = (0, 0.12, -.026)
    boneMirror(char, Vjaw4, False)
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones['neck06.001'].name = "jaw1"
    char.armature.edit_bones['neck06.002'].name = "jaw2"
    char.armature.edit_bones['neck06.003'].name = "jaw3"
    char.armature.edit_bones['neck06.004'].name = "jaw4"
    char.armature.edit_bones['neck06.005'].name = "jaw5"
    #
    char.armature.edit_bones["jaw1"].select_tail=True
    VbeakBase = (0, 0.08, .07)
    boneMirror(char, VbeakBase, False)
    Vbeak1 = (0, 0.16, 0)
    boneMirror(char, Vbeak1, False)
    Vbeak2 = (0, 0.18, -.05)
    boneMirror(char, Vbeak2, False)
    char.armature.edit_bones['jaw1.001'].name = "beak1"
    char.armature.edit_bones['jaw1.002'].name = "beak2"
    char.armature.edit_bones['jaw1.003'].name = "beak3"
    #
    char.armature.edit_bones['headBase'].parent = char.armature.edit_bones['neck06']
    char.armature.edit_bones['jaw1'].parent = char.armature.edit_bones['neck06']
    bpy.ops.armature.select_all(action='DESELECT')
    #
    char.armature.edit_bones["headBase"].select_tail=True
    VeyeBase = (0.06, .104, -.02)
    boneMirror(char, VeyeBase, True)
    Veye = (0, .02, 0)
    boneMirror(char, Veye, True)
    char.armature.edit_bones['headBase_L'].name = "baseEye.L"
    char.armature.edit_bones['headBase_R'].name = "baseEye.R"
    char.armature.edit_bones['headBase_L.001'].name = "eye.L"
    char.armature.edit_bones['headBase_R.001'].name = "eye.R"
    bpy.ops.armature.select_all(action='DESELECT')
    #
    char.armature.edit_bones["neck01"].select_tail=True
    Vffix1 = (0, 0.06, -.1)
    boneMirror(char, Vffix1, False)
    Vffix2 = (0, -.05, -.1)
    boneMirror(char, Vffix2, False)
    Vffix3 = (0, -.07, -.1)
    boneMirror(char, Vffix3, False)
    Vffix4 = (0, -.08, -.1)
    boneMirror(char, Vffix4, False)
    Vffix5 = (0, -.09, -.1)
    boneMirror(char, Vffix5, False)
    char.armature.edit_bones['neck01.001'].name = "ffix1"
    char.armature.edit_bones['neck01.002'].name = "ffix2"
    char.armature.edit_bones['neck01.003'].name = "ffix3"
    char.armature.edit_bones['neck01.004'].name = "ffix4"
    char.armature.edit_bones['neck01.005'].name = "ffix5"
    bpy.ops.armature.select_all(action='DESELECT')
    #
    createWings(char)
    #
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones["backL2"].select_tail=True
    VhipBase = (0, 0.06, -0.1)
    boneMirror(char, VhipBase, False)
    char.armature.edit_bones['backL2.001'].name = "hipBase"
    Vhip = (.18, 0, 0)
    boneMirror(char, Vhip, True)
    VhipBone = (0, .01, -0.12)
    boneMirror(char, VhipBone, True)
    VfemurJ1 = (0, -0.02, -0.12)
    boneMirror(char, VfemurJ1, True)
    VfemurJ2 = (0, -0.02, -0.12)
    boneMirror(char, VfemurJ2, True)
    VfemurJ3 = (0, 0, -0.12)
    boneMirror(char, VfemurJ3, True)
    VlegJ5 = (0, .01, -.1)
    boneMirror(char, VlegJ5, True)
    VtibiaJ2 = (0, .01, -.1)
    boneMirror(char, VtibiaJ2, True)
    VtibiaJ3 = (0, .01, -.11)
    boneMirror(char, VtibiaJ3, True)
    Vankle = (0, .01, -.05)
    boneMirror(char, Vankle, True)
    VrearToeJ1 = (-.016, -0.07, .01)
    boneMirror(char, VrearToeJ1, True)
    VrearToeJ2 = (-.015, -0.07, 0)
    boneMirror(char, VrearToeJ2, True)
    VrearToeJ3 = (-.015, -0.07, 0)
    boneMirror(char, VrearToeJ3, True)
    VrearToeJ4 = (-.015, -0.07, 0)
    boneMirror(char, VrearToeJ4, True)
    #
    char.armature.edit_bones['hipBase_R'].name = "hip.L"
    char.armature.edit_bones['hipBase_L'].name = "hip.R"
    char.armature.edit_bones['hipBase_R.001'].name = "hipBone.L"
    char.armature.edit_bones['hipBase_L.001'].name = "hipBone.R"
    char.armature.edit_bones['hipBase_R.002'].name = "femurJ1.L"
    char.armature.edit_bones['hipBase_L.002'].name = "femurJ1.R"    
    char.armature.edit_bones['hipBase_R.003'].name = "femurJ2.L"
    char.armature.edit_bones['hipBase_L.003'].name = "femurJ2.R"
    char.armature.edit_bones['hipBase_R.004'].name = "femurJ3.L"
    char.armature.edit_bones['hipBase_L.004'].name = "femurJ3.R"
    char.armature.edit_bones['hipBase_R.005'].name = "tibiaJ1.L"
    char.armature.edit_bones['hipBase_L.005'].name = "tibiaJ1.R"
    char.armature.edit_bones['hipBase_R.006'].name = "tibiaJ2.L"
    char.armature.edit_bones['hipBase_L.006'].name = "tibiaJ2.R"
    char.armature.edit_bones['hipBase_R.007'].name = "tibiaJ3.L"
    char.armature.edit_bones['hipBase_L.007'].name = "tibiaJ3.R"
    char.armature.edit_bones['hipBase_R.008'].name = "ankle.L"
    char.armature.edit_bones['hipBase_L.008'].name = "ankle.R"
    char.armature.edit_bones['hipBase_R.009'].name = "rearToeJ1.L"
    char.armature.edit_bones['hipBase_L.009'].name = "rearToeJ1.R"
    char.armature.edit_bones['hipBase_R.010'].name = "rearToeJ2.L"
    char.armature.edit_bones['hipBase_L.010'].name = "rearToeJ2.R"
    char.armature.edit_bones['hipBase_R.011'].name = "rearToeJ3.L"
    char.armature.edit_bones['hipBase_L.011'].name = "rearToeJ3.R"
    char.armature.edit_bones['hipBase_R.012'].name = "rearToeJ4.L"
    char.armature.edit_bones['hipBase_L.012'].name = "rearToeJ4.R"
    bpy.ops.armature.select_all(action='DESELECT')
    # Center Claw
    char.armature.edit_bones["ankle.L"].select_tail=True
    VcenterToe = (0, .07, 0)
    boneMirror(char, VcenterToe, True)
    boneMirror(char, VcenterToe, True)
    boneMirror(char, VcenterToe, True)
    boneMirror(char, VcenterToe, True)
    char.armature.edit_bones['ankle.L.001'].name = "centerToeJ1.L"
    char.armature.edit_bones['ankle.R.001'].name = "centerToeJ1.R"
    char.armature.edit_bones['ankle.L.002'].name = "centerToeJ2.L"
    char.armature.edit_bones['ankle.R.002'].name = "centerToeJ2.R"
    char.armature.edit_bones['ankle.L.003'].name = "centerToeJ3.L"
    char.armature.edit_bones['ankle.R.003'].name = "centerToeJ3.R"
    char.armature.edit_bones['ankle.L.004'].name = "centerToeJ4.L"
    char.armature.edit_bones['ankle.R.004'].name = "centerToeJ4.R"
    bpy.ops.armature.select_all(action='DESELECT')
    #
    char.armature.edit_bones["ankle.L"].select_tail=False
    bpy.ops.armature.select_all(action='DESELECT')
    # Left Claw
    char.armature.edit_bones["ankle.L"].select_tail=True
    VouterToe = (-.0358, .066, 0)
    boneMirror(char, VouterToe, True)
    boneMirror(char, VouterToe, True)
    boneMirror(char, VouterToe, True)
    boneMirror(char, VouterToe, True)
    char.armature.edit_bones['ankle.L.001'].name = "outerToeJ1.L"
    char.armature.edit_bones['ankle.R.001'].name = "outerToeJ1.R"
    char.armature.edit_bones['ankle.L.002'].name = "outerToeJ2.L"
    char.armature.edit_bones['ankle.R.002'].name = "outerToeJ2.R"
    char.armature.edit_bones['ankle.L.003'].name = "outerToeJ3.L"
    char.armature.edit_bones['ankle.R.003'].name = "outerToeJ3.R"
    char.armature.edit_bones['ankle.L.004'].name = "outerToeJ4.L"
    char.armature.edit_bones['ankle.R.004'].name = "outerToeJ4.R"
    bpy.ops.armature.select_all(action='DESELECT')
    # Right Claw
    char.armature.edit_bones["ankle.L"].select_tail=True
    VinnerToe = (.034, .065, 0)
    boneMirror(char, VinnerToe, True)
    boneMirror(char, VinnerToe, True)
    boneMirror(char, VinnerToe, True)
    boneMirror(char, VinnerToe, True)
    char.armature.edit_bones['ankle.L.001'].name = "innerToeJ1.L"
    char.armature.edit_bones['ankle.R.001'].name = "innerToeJ1.R"
    char.armature.edit_bones['ankle.L.002'].name = "innerToeJ2.L"
    char.armature.edit_bones['ankle.R.002'].name = "innerToeJ2.R"
    char.armature.edit_bones['ankle.L.003'].name = "innerToeJ3.L"
    char.armature.edit_bones['ankle.R.003'].name = "innerToeJ3.R"
    char.armature.edit_bones['ankle.L.004'].name = "innerToeJ4.L"
    char.armature.edit_bones['ankle.R.004'].name = "innerToeJ4.R"
    #
    #setEnvelopeWeights()
    deselectAll()
    ob = bpy.data.objects.get(char.name)
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    #
    setEnvelopeWeights(char)
    bpy.data.objects[char.name].location[2] = z  # z height
    bpy.ops.object.mode_set(mode='OBJECT')
    ob = bpy.data.objects.get(char.name)
    context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.context.object.rotation_euler[2] = -1.5708

def createWings(char):
    if(char.name.startswith("rgbird")):
        root = "backCenter"
    if(char.name.startswith("rgadWings")):
        root = char.name + "_bone"
    # BuildWings
    char.armature.edit_bones[root].select_head=True
    Vbase = (-.12, 0, 0)
    boneMirror(char, Vbase, True)
    Vwings_J1 = (-.06, 0, 0)
    boneMirror(char, Vwings_J1, True)
    Vwings_J2 = (-.03, 0, 0)
    boneMirror(char, Vwings_J2, True)
    Vwings_J3 = (-.03, 0, 0)
    boneMirror(char, Vwings_J3, True)
    Vwings_J4 = (-.03, 0, 0)
    boneMirror(char, Vwings_J4, True)
    Vwings_J5 = (-.03, 0, 0)
    boneMirror(char, Vwings_J5, True)
    Vwings_J6 = (-.03, 0, 0)
    boneMirror(char, Vwings_J6, True)
    Vwings_J7 = (-.03, 0, 0)
    boneMirror(char, Vwings_J7, True)
    Vwings_J8 = (-.03, 0, 0)
    boneMirror(char, Vwings_J8, True)
    Vwings_J9 = (-.03, 0, 0)
    boneMirror(char, Vwings_J9, True)
    Vwings_J10 = (-.03, 0, 0)
    boneMirror(char, Vwings_J10, True)
    Vwings_J11 = (-.015, 0, 0)
    boneMirror(char, Vwings_J11, True)
    Vwings_J12 = (-.015, 0, 0)
    boneMirror(char, Vwings_J12, True)
    Vwings_J13 = (-.015, 0, 0)
    boneMirror(char, Vwings_J13, True)
    Vwings_J14 = (-.015, 0, 0)
    boneMirror(char, Vwings_J14, True)
    Vwings_J15 = (-.015, 0, 0)
    boneMirror(char, Vwings_J15, True)
    Vwings_J16 = (-0.06, 0, 0)
    boneMirror(char, Vwings_J16, True)
    # 
    prefix = ""
    if(char.name.startswith("rgbird")):  # Start with "wings" for bird
        prefix = "rgwings"
    if(char.name.startswith("rgadWings")): # Start with "adWings" for solo wings
        prefix = "rgadWings"
    char.armature.edit_bones[root + '_L'].name = prefix + "Base1.L"
    char.armature.edit_bones[root + '_R'].name = prefix + "Base1.R"
    char.armature.edit_bones[root + '_L.001'].name = prefix + "_J1.L"
    char.armature.edit_bones[root + '_R.001'].name = prefix + "_J1.R"
    char.armature.edit_bones[root + '_L.002'].name = prefix + "_J2.L"
    char.armature.edit_bones[root + '_R.002'].name = prefix + "_J2.R"
    char.armature.edit_bones[root + '_L.003'].name = prefix + "_J3.L"
    char.armature.edit_bones[root + '_R.003'].name = prefix + "_J3.R"
    char.armature.edit_bones[root + '_L.004'].name = prefix + "_J4.L"
    char.armature.edit_bones[root + '_R.004'].name = prefix + "_J4.R"
    char.armature.edit_bones[root + '_L.005'].name = prefix + "_J5.L"
    char.armature.edit_bones[root + '_R.005'].name = prefix + "_J5.R"
    char.armature.edit_bones[root + '_L.006'].name = prefix + "_J6.L"
    char.armature.edit_bones[root + '_R.006'].name = prefix + "_J6.R"
    char.armature.edit_bones[root + '_L.007'].name = prefix + "_J7.L"
    char.armature.edit_bones[root + '_R.007'].name = prefix + "_J7.R"
    char.armature.edit_bones[root + '_L.008'].name = prefix + "_J8.L"
    char.armature.edit_bones[root + '_R.008'].name = prefix + "_J8.R"
    char.armature.edit_bones[root + '_L.009'].name = prefix + "_J9.L"
    char.armature.edit_bones[root + '_R.009'].name = prefix + "_J9.R"
    char.armature.edit_bones[root + '_L.010'].name = prefix + "_J10.L"
    char.armature.edit_bones[root + '_R.010'].name = prefix + "_J10.R"
    char.armature.edit_bones[root + '_L.011'].name = prefix + "_J11.L"
    char.armature.edit_bones[root + '_R.011'].name = prefix + "_J11.R"
    char.armature.edit_bones[root + '_L.012'].name = prefix + "_J12.L"
    char.armature.edit_bones[root + '_R.012'].name = prefix + "_J12.R"
    char.armature.edit_bones[root + '_L.013'].name = prefix + "_J13.L"
    char.armature.edit_bones[root + '_R.013'].name = prefix + "_J13.R"
    char.armature.edit_bones[root + '_L.014'].name = prefix + "_J14.L"
    char.armature.edit_bones[root + '_R.014'].name = prefix + "_J14.R"
    char.armature.edit_bones[root + '_L.015'].name = prefix + "_J15.L"
    char.armature.edit_bones[root + '_R.015'].name = prefix + "_J15.R"
    char.armature.edit_bones[root + '_L.016'].name = prefix + "_J16.L"
    char.armature.edit_bones[root + '_R.016'].name = prefix + "_J16.R"
    bpy.ops.armature.select_all(action='DESELECT')
    #
    char.armature.edit_bones[prefix + "_J1.L"].select_tail=True
    n = 0
    offset = .0046
    Vfeathers = (0, -.04, 0) # All of these  are the  same size
    boneMirror(char, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones[prefix + "_J2.L"].select_tail=True
    Vfeathers = (n, -.04, 0)
    boneMirror(char, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones[prefix + "_J3.L"].select_tail=True
    n = n - offset
    Vfeathers = (n, -.04, 0)
    boneMirror(char, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones[prefix + "_J4.L"].select_tail=True
    n = n - offset
    Vfeathers = (n, -.04, 0)
    boneMirror(char, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones[prefix + "_J5.L"].select_tail=True
    n = n - offset
    Vfeathers = (n, -.04, 0)
    boneMirror(char, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones[prefix + "_J6.L"].select_tail=True
    n = n - offset
    Vfeathers = (n, -.04, 0)
    boneMirror(char, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones[prefix + "_J7.L"].select_tail=True
    n = n - offset
    Vfeathers = (n, -.04, 0)
    boneMirror(char, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones[prefix + "_J8.L"].select_tail=True
    n = n - offset
    Vfeathers = (n, -.04, 0)
    boneMirror(char, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones[prefix + "_J9.L"].select_tail=True
    n = n - offset
    Vfeathers = (n, -.04, 0)
    boneMirror(char, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones[prefix + "_J10.L"].select_tail=True
    n = n - offset
    Vfeathers = (n, -.034, 0)
    boneMirror(char, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones[prefix + "_J11.L"].select_tail=True
    offset = .002
    n = n - offset
    Vfeathers = (n, -.026, 0)
    boneMirror(char, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones[prefix + "_J12.L"].select_tail=True
    n = n - offset
    Vfeathers = (n, -.024, 0)
    boneMirror(char, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones[prefix + "_J13.L"].select_tail=True
    n = n - offset
    Vfeathers = (n, -.018, 0)
    boneMirror(char, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones[prefix + "_J14.L"].select_tail=True
    Vfeathers = (n, -.012, 0)
    boneMirror(char, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones[prefix + "_J15.L"].select_tail=True
    Vfeathers = (n, -.009, 0)
    boneMirror(char, Vfeathers, True)
    char.armature.edit_bones[prefix + '_J1.L.001'].name = prefix + "Feathers1.L"
    char.armature.edit_bones[prefix + '_J1.R.001'].name = prefix + "Feathers1.R"
    char.armature.edit_bones[prefix + '_J2.L.001'].name = prefix + "Feathers2.L"
    char.armature.edit_bones[prefix + '_J2.R.001'].name = prefix + "Feathers2.R"
    char.armature.edit_bones[prefix + '_J3.L.001'].name = prefix + "Feathers3.L"
    char.armature.edit_bones[prefix + '_J3.R.001'].name = prefix + "Feathers3.R"
    char.armature.edit_bones[prefix + '_J4.L.001'].name = prefix + "Feathers4.L"
    char.armature.edit_bones[prefix + '_J4.R.001'].name = prefix + "Feathers4.R"
    char.armature.edit_bones[prefix + '_J5.L.001'].name = prefix + "Feathers5.L"
    char.armature.edit_bones[prefix + '_J5.R.001'].name = prefix + "Feathers5.R"
    char.armature.edit_bones[prefix + '_J6.L.001'].name = prefix + "Feathers6.L"
    char.armature.edit_bones[prefix + '_J6.R.001'].name = prefix + "Feathers6.R"
    char.armature.edit_bones[prefix + '_J7.L.001'].name = prefix + "Feathers7.L"
    char.armature.edit_bones[prefix + '_J7.R.001'].name = prefix + "Feathers7.R"
    char.armature.edit_bones[prefix + '_J8.L.001'].name = prefix + "Feathers8.L"
    char.armature.edit_bones[prefix + '_J8.R.001'].name = prefix + "Feathers8.R"
    char.armature.edit_bones[prefix + '_J9.L.001'].name = prefix + "Feathers9.L"
    char.armature.edit_bones[prefix + '_J9.R.001'].name = prefix + "Feathers9.R"
    char.armature.edit_bones[prefix + '_J10.L.001'].name = prefix + "Feathers10.L"
    char.armature.edit_bones[prefix + '_J10.R.001'].name = prefix + "Feathers10.R"
    char.armature.edit_bones[prefix + '_J11.L.001'].name = prefix + "Feathers11.L"
    char.armature.edit_bones[prefix + '_J11.R.001'].name = prefix + "Feathers11.R"
    char.armature.edit_bones[prefix + '_J12.L.001'].name = prefix + "Feathers12.L"
    char.armature.edit_bones[prefix + '_J12.R.001'].name = prefix + "Feathers12.R"
    char.armature.edit_bones[prefix + '_J13.L.001'].name = prefix + "Feathers13.L"
    char.armature.edit_bones[prefix + '_J13.R.001'].name = prefix + "Feathers13.R"
    char.armature.edit_bones[prefix + '_J14.L.001'].name = prefix + "Feathers14.L"
    char.armature.edit_bones[prefix + '_J14.R.001'].name = prefix + "Feathers14.R"
    char.armature.edit_bones[prefix + '_J15.L.001'].name = prefix + "Feathers15.L"
    char.armature.edit_bones[prefix + '_J15.R.001'].name = prefix + "Feathers15.R"
    bpy.ops.armature.select_all(action='DESELECT')
    #
    for b in bpy.data.objects[char.name].pose.bones:
        b.rotation_mode = 'XYZ'
    for b in bpy.context.object.data.edit_bones:
        # Set weights for adWings
        if(b.name == char.name + '_bone'):
            b.envelope_distance = .001
            b.envelope_weight = 0.0
            b.head_radius = 0.02
            b.tail_radius = 0.04
        if(b.name == prefix + "Base1.L") or (b.name == prefix + "Base1.R"):
            b.envelope_distance = .02
            b.head_radius = 0.02
            b.tail_radius = 0.02
        if(b.name.startswith(prefix + "_J1")):
            b.envelope_distance = 0.08
            b.head_radius = 0.001
            b.tail_radius = 0.2
        if(b.name.startswith(prefix + "_J2")):
            b.envelope_distance = 0.2
            b.head_radius = 0.2
            b.tail_radius = 0.2
        if(b.name.startswith(prefix + "_J3")):
            b.envelope_distance = 0.2
            b.head_radius = 0.2
            b.tail_radius = 0.2

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# END BIRD SECTION
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# BEGIN SPIDER SECTION
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def buildSpiderSkeleton():  # START BUILDING SKELETON %%%%%%%%%%%%%%%%%%%%%
    n = getSceneObjectNumber()
    name = setName('spider', n) 
    mod = math.fmod(n, 2)
    if(mod == 0):
        x = 1.1 * n - mod
    else:
        x = 1.1 * -n - mod
    y = -.4 * n; z = .1  # For Armature
    char = buildRootArmature(name, x, y, z) 
    char.name = name # gives rgcentaur02
    char.x = x; char.y = y; char.z = z
    #addCharactersProperties()
    # Build root bone
    VHead = [0, 0, 0]
    VTail = [0, 0.0, 0.6] 
    bone = setHandle(char, VHead, VTail)
    # charClass.rig.show_in_front = True
    #
    V_origin = (0, 0, 0)
    Vradius1 = (0, .254, 0)
    radius1 = createBone("radius1", V_origin, Vradius1)
    radius1.parent = char.armature.edit_bones[char.name + '_bone']
    Vframe = (.2, 0, 0)
    boneMirror(char, Vframe, mirror=True)
    Vframe = (0, 0, .062)
    boneMirror(char, Vframe, mirror=True)
    Vframe = (.2, 0, .082)
    boneMirror(char, Vframe, mirror=True)
    Vframe = (.4, 0, -.2)
    boneMirror(char, Vframe, mirror=True)
    Vframe = (.1, 0, 0)
    boneMirror(char, Vframe, mirror=True)
    char.armature.edit_bones['radius1_L'].name = "frame2F"  # F for front
    char.armature.edit_bones['radius1_R'].name = "frame1F"
    char.armature.edit_bones['radius1_L.001'].name = "sideToSide2F"
    char.armature.edit_bones['radius1_R.001'].name = "sideToSide1F"
    char.armature.edit_bones['radius1_L.002'].name = "leg2J1F.R"
    char.armature.edit_bones['radius1_R.002'].name = "leg1J1F.L"
    char.armature.edit_bones['radius1_L.003'].name = "leg2J2F.R"
    char.armature.edit_bones['radius1_R.003'].name = "leg1J2F.L"
    char.armature.edit_bones['radius1_L.004'].name = "leg2J3F.R"
    char.armature.edit_bones['radius1_R.004'].name = "leg1J3F.L"
    bpy.ops.armature.select_all(action='DESELECT')
    #
    Vradius3 = (0, -.25, 0)
    radius3 = createBone("radius3", V_origin, Vradius3)
    radius3.parent = char.armature.edit_bones[char.name + '_bone']
    Vframe = (.22, 0, 0)
    boneMirror(char, Vframe, mirror=True)
    Vframe = (0, 0, .062)
    boneMirror(char, Vframe, mirror=True)
    Vframe = (.2, 0, .082)
    boneMirror(char, Vframe, mirror=True)
    Vframe = (.4, 0, -.2)
    boneMirror(char, Vframe, mirror=True)
    Vframe = (.1, 0, 0)
    boneMirror(char, Vframe, mirror=True)
    char.armature.edit_bones['radius3_L'].name = "frame5.R"
    char.armature.edit_bones['radius3_R'].name = "frame6.L"
    char.armature.edit_bones['radius3_L.001'].name = "sideToSide5.R"
    char.armature.edit_bones['radius3_R.001'].name = "sideToSide6.L"
    char.armature.edit_bones['radius3_L.002'].name = "leg5J1.R"
    char.armature.edit_bones['radius3_R.002'].name = "leg6J1.L"
    char.armature.edit_bones['radius3_L.003'].name = "leg5J2.R"
    char.armature.edit_bones['radius3_R.003'].name = "leg6J2.L"
    char.armature.edit_bones['radius3_L.004'].name = "leg5J3.R"
    char.armature.edit_bones['radius3_R.004'].name = "leg6J3.L"
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones[char.name + '_bone'].select_tail=True
    bpy.ops.object.mode_set(mode='POSE')
    #bpy.data.objects[strName].pose.bones[strName + '_bone'].rotation_euler[1] = 1.5708
    #rotate(strName, strName + '_bone', 1.5708, 1)
    #x = y = 2.0 * n;
    VOrigin = (0, 0, .02)
    Vradius2 = (.254, 0, 0)
    radius2 = createBone("radius2", VOrigin, Vradius2)
    radius2.parent = char.armature.edit_bones[char.name + '_bone']
    Vframe = (0, .082, 0)
    boneMirror(char, Vframe, mirror=False)
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones["radius2"].select_tail=True
    Vframe = (0, -.082, 0)
    boneMirror(char, Vframe, mirror=False)
    Vframe = (0, 0, .062)
    boneMirror(char, Vframe, mirror=False)
    Vframe = (.2, 0, .082)
    boneMirror(char, Vframe, mirror=False)
    Vframe = (.4, 0, -.2)
    boneMirror(char, Vframe, mirror=False)
    Vframe = (.1, 0, 0)
    boneMirror(char, Vframe, mirror=False)
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones["radius2.001"].select_tail=True
    Vframe = (0, 0, .062)
    boneMirror(char, Vframe, mirror=False)
    Vframe = (.2, 0, .082)
    boneMirror(char, Vframe, mirror=False)
    Vframe = (.4, 0, -.2)
    boneMirror(char, Vframe, mirror=False)
    Vframe = (.1, 0, 0)
    boneMirror(char, Vframe, mirror=False)
    char.armature.edit_bones['radius2.001'].name = "frame3R.F"  # Right Front
    char.armature.edit_bones['radius2.002'].name = "frame4R.B"  # Right Back
    char.armature.edit_bones['radius2.003'].name = "sideToSide4R.B"
    char.armature.edit_bones['radius2.004'].name = "leg4J1R.B"
    char.armature.edit_bones['radius2.005'].name = "leg4J2R.B"
    char.armature.edit_bones['radius2.006'].name = "leg4J3R.B"
    char.armature.edit_bones['radius2.007'].name = "sideToSide3R.F"
    char.armature.edit_bones['radius2.008'].name = "leg3J1R.F"
    char.armature.edit_bones['radius2.009'].name = "leg3J2R.F"
    char.armature.edit_bones['radius2.010'].name = "leg3J3R.F"
    #
    bpy.ops.armature.select_all(action='DESELECT')
    Vradius4 = (-.254, 0, 0)
    radius4 = createBone("radius4", VOrigin, Vradius4)
    radius4.parent = char.armature.edit_bones[char.name + '_bone']
    Vframe = (0, .082, 0)
    boneMirror(char, Vframe, mirror=False)
    Vframe = (0, 0, .062)
    boneMirror(char, Vframe, mirror=False)
    Vframe = (-.2, 0, .082)
    boneMirror(char, Vframe, mirror=False)
    Vframe = (-.4, 0, -.2)
    boneMirror(char, Vframe, mirror=False)
    Vframe = (-.1, 0, 0)
    boneMirror(char, Vframe, mirror=False)
    bpy.ops.armature.select_all(action='DESELECT')
    char.armature.edit_bones["radius4"].select_tail=True
    Vframe = (0, -.082, 0)
    boneMirror(char, Vframe, mirror=False) # frame
    Vframe = (0, 0, .062)
    boneMirror(char, Vframe, mirror=False) # sideToSide
    Vframe = (-.2, 0, .082)
    boneMirror(char, Vframe, mirror=False)
    Vframe = (-.4, 0, -.2)
    boneMirror(char, Vframe, mirror=False)
    Vframe = (-.1, 0, 0)
    boneMirror(char, Vframe, mirror=False)
    char.armature.edit_bones['radius4.001'].name = "frame8L.F"  # Left Front
    char.armature.edit_bones['radius4.002'].name = "sideToSide8L.F"  
    char.armature.edit_bones['radius4.003'].name = "leg8J1L.F"
    char.armature.edit_bones['radius4.004'].name = "leg8J2L.F"
    char.armature.edit_bones['radius4.005'].name = "leg8J3L.F"
    char.armature.edit_bones['radius4.006'].name = "frame7L.B"   # Left Back
    char.armature.edit_bones['radius4.007'].name = "sideToSide7L.B"
    char.armature.edit_bones['radius4.008'].name = "leg7J1L.B"
    char.armature.edit_bones['radius4.009'].name = "leg7J2L.B"
    char.armature.edit_bones['radius4.010'].name = "leg7J3L.B"
    bpy.ops.armature.select_all(action='DESELECT')
    #
    # ADD TAIL
    char.armature.edit_bones["radius3"].select_tail=True
    Vframe = (0, -.12, .08)
    boneMirror(char, Vframe, mirror=False)
    Vframe = (0, -.26, 0)
    boneMirror(char, Vframe, mirror=False)
    Vframe = (0, -.26, 0)
    boneMirror(char, Vframe, mirror=False)
    Vframe = (0, -.26, 0)
    boneMirror(char, Vframe, mirror=False)
    char.armature.edit_bones['radius3.001'].name = "tail1"
    char.armature.edit_bones['radius3.002'].name = "tail2"
    char.armature.edit_bones['radius3.003'].name = "tail3"
    char.armature.edit_bones['radius3.004'].name = "tail4"
    #
    for b in bpy.data.objects[char.name].pose.bones:
        b.rotation_mode = 'XYZ'
    for b in bpy.context.object.data.edit_bones:
        b.envelope_distance = 0.064
        b.head_radius = 0.02
        b.tail_radius = 0.02
        #b.envelope_weight = 1.0
    #
    #
    # Set weights for specific parts
    for b in bpy.context.object.data.edit_bones:
        if(b.name == "radius1") or (b.name == "radius3"):
            b.envelope_distance = 0.2
        if(b.name.startswith("tail1")):
            b.envelope_distance = 0.06
        if(b.name == "tail2"):
            b.envelope_distance = 0.06
        if(b.name == "tail3") or (b.name == "tail4"):
            b.envelope_distance = 0.28
        if(b.name.startswith("frame")):
            b.envelope_distance = 0
    deselectAll()
    ob = bpy.data.objects.get(char.name)
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.object.mode_set(mode='OBJECT')

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# END SPIDER SECTION
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# SOLO WINGS SECTION
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def buildWings():  # START BUILDING WINGS %%%%%%%%%%%%%%%%%%%%%
    n = getSceneObjectNumber()
    name = setName('adWings', n) 
    mod = math.fmod(n, 2)
    if(mod == 0):
        x = 1.1 * n - mod
    else:
        x = 1.1 * -n - mod
    y = -.8 * n; z = 1.9  # For Armature
    char = buildRootArmature(name, x, y, z) 
    char.name = name # gives rgcentaur02
    char.x = x; char.y = y; char.z = z
    VHead = [0, 0, 0]
    VTail = [0.0, 0.1, 0]  # End location of handle relative to armature origin - this effects coordinate system
    bone = setHandle(char, VHead, VTail)
    # Build wings shared part between bird and solo wings
    createWings(char)
    deselectAll()
    ob = bpy.data.objects.get(char.name)
    context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.context.object.rotation_euler[2] = -1.5708
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# END SOLO WINGS SECTION
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%



def register():
    from bpy.utils import register_class
    register_class(Biped_Build_Btn)
    register_class(Centaur_Build_Btn)
    register_class(Quadruped_Build_Button)
    register_class(Bird_Build_Button)
    register_class(Spider_Build_Button)
    register_class(Wings_Build_Button)
    #
    register_class(Pose_Btn)
    register_class(Drop_Arms_Btn)
    register_class(Walk_Btn)
    register_class(Run_Btn)
    #register_class(Arm_Action_Btn)
    #register_class(Leg_Action_Btn)
    #register_class(Reset_btn)
    #
    register_class(CONTROL_PT_Panel)
    bpy.utils.register_class(CHARACTER_OT_control_I)
    bpy.utils.register_class(CHARACTER_OT_control_II)

def unregister():
    from bpy.utils import unregister_class
    unregister_class(Biped_Build_Btn)
    unregister_class(Centaur_Build_Btn)
    unregister_class(Quadruped_Build_Button)
    unregister_class(Bird_Build_Button)
    unregister_class(Spider_Build_Button)
    unregister_class(Wings_Build_Button)
    #
    unregister_class(Pose_Btn)
    unregister_class(Drop_Arms_Btn)
    unregister_class(Walk_Btn)
    unregister_class(Run_Btn)
    #unregister_class(Arm_Action_Btn)
    #unregister_class(Leg_Action_Btn)
    #unregister_class(Reset_btn)
    #
    unregister_class(CONTROL_PT_Panel)
    bpy.utils.unregister_class(CHARACTER_OT_control_I)
    bpy.utils.unregister_class(CHARACTER_OT_control_II)

if __name__ == "__main__":
    register()

