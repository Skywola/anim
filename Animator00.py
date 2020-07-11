import bpy, math
from bpy.types import Panel, Menu
from rna_prop_ui import PropertyPanel
from bpy.props import FloatProperty
context = bpy.context
import mathutils

sin = math.sin; cos = math.cos; tan = math.tan
asin = math.asin; acos = math.acos; atan = math.atan
fmod = math.fmod; ceil = math.ceil; floor = math.floor
Vector = mathutils.Vector
radians = math.radians
cwmPanel = bpy.context.window_manager # cwmPanel PanelProperty
genProp = bpy.types.WindowManager # genProp General Wm Property

# This is the magic fn for troubleshooting only
def getTypeAndString(elem):
    print("Type = ", type(elem))
    print(">>>>>>>",elem,">>>>>>>")
    print(">>>>>>>",elem,">>>>>>>")
    print(">>>>>>>",elem,">>>>>>>")

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
genProp.blank = bpy.props.FloatProperty(name="blank", default=0)
genProp.toggleArmAction = bpy.props.BoolProperty(name="toggleArmAction", default=True)
genProp.toggleLegAction = bpy.props.BoolProperty(name="toggleLegAction", default=True)
#Set to Zero at frame 0, otherwise a one
genProp.str_0AtFrame0 = bpy.props.StringProperty(name="str_0AtFrame0", default="*(frame * (1/(frame+.0001)))")
# Set to One at frame zero, otherwise a zero [TODO - THIS IS CURRENTLY NOT USED]
genProp.str_1AtFrame0 = bpy.props.StringProperty(name="str_1AtFrame0", default="*abs((frame/(frame + .0001))-1)")

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# END: genProp COMMON PROPERTIES
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# BIPED FUNCTIONS without update= PROPERTIES
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
    genProp.cycle = 12
    genProp.Hip_Rotate = 2.0
    genProp.Sway_LR = 2.0
    genProp.Sway_FB = 4.0
    genProp.bounce = 1.2
    genProp.Hip_UD = 2.0 
    genProp.Shoulder_Rotation = 8.0 
    genProp.Shoulder_UD = 4.0 
    genProp.Arm_Rotation = 3.0 
    genProp.rotateRange = 2.6
    genProp.tibiaJ1RP = .6 
    genProp.tibiaJ1RR = 1.0
    genProp.ankleRP = 0.0
    genProp.toesRP = -.1
    setBipedWalk(self, context)
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
# RP = Rotate Position
# RR = Rotate Range
def revertAdvancedControls(self, context):
    genProp.rotatePosition = 0.1
    genProp.rotateRange = 1.0
    genProp.tibiaJ1RP = 0.0
    genProp.tibiaJ1RR = 1.0
    genProp.ankleRP = 0.0
    genProp.ankleRR = 1.0
    genProp.toesRP = 0.0
    genProp.toesRR = 1.0
    setBipedWalk(self, context)
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

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# BIPED PROPERTIES (with update= ) AND THEIR FUNCTIONS PRECEEDING THEM
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
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

def setBipedWalk(self, context):
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
    biped = Biped
    biped.setBipedPropertiesPanel()
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


# PopUp Window Properties declared strictly for class WM_OT_controol window
genProp.cycle = bpy.props.FloatProperty(update=update, name="Cycle", default=1.0)
genProp.speed = bpy.props.FloatProperty(update=update, name="Speed")
genProp.direction = bpy.props.FloatProperty(update=setDirection, name="Direction", default=0.0)
genProp.X_Location = bpy.props.FloatProperty(update=update, name="X_Location", default=0.0)
genProp.Y_Location = bpy.props.FloatProperty(update=update, name="Y_Location", default=0.0)
genProp.Z_Location = bpy.props.FloatProperty(update=update, name="Z_Location", default=1.18)
genProp.Sway_LR = bpy.props.FloatProperty(update=setSwayLR, name="Sway_LR", default=1.0)
genProp.Sway_FB = bpy.props.FloatProperty(update=setSwayFB, name="Sway_FB", default=1.0)
genProp.bounce = bpy.props.FloatProperty(update=setBounce, name="Bounce", default=1.2)
genProp.Shoulder_Rotation = bpy.props.FloatProperty(update=setBounce, name="Shoulder_Rotation", default=1.2)
genProp.Shoulder_UD = bpy.props.FloatProperty(update=setBounce, name="Shoulder_UD", default=1.0)
genProp.Leg_Spread = bpy.props.FloatProperty(update=setHip, name="Leg_Spread", default=0.0)
#genProp.skate = bpy.props.FloatProperty(update=setSkate, name="Skate", default=0.0)
genProp.Hip_Sway = bpy.props.FloatProperty(update=setHip, name="Hip_Sway", default=0.0)
genProp.Hip_Rotate = bpy.props.FloatProperty(update=setHip, name="Hip_Rotate", default=0.0)
genProp.Hip_UD = bpy.props.FloatProperty(update=setHip, name="Hip_UD", default=2.0)
genProp.Leg_Arch = bpy.props.FloatProperty(update=setLegArch, name="Leg_Arch", default=0.0)
# End  PopUp Window Properties declared strictly for class WM_OT_controol window

genProp.rotatePosition = bpy.props.FloatProperty(update=setBipedWalk, name="rotatePosition", default=0.1)
genProp.rotateRange = bpy.props.FloatProperty(update=setBipedWalk, name="rotateRange", default=1.0)
genProp.tibiaJ1RP = bpy.props.FloatProperty(update=setBipedWalk, name="tibiaJ1RP", default=0.0)
genProp.tibiaJ1RR = bpy.props.FloatProperty(update=setBipedWalk, name="tibiaJ1RR", default=1.0)
genProp.ankleRP = bpy.props.FloatProperty(update=setBipedWalk, name="ankleRP", default=0.0)
genProp.ankleRR = bpy.props.FloatProperty(update=setBipedWalk, name="ankleRR", default=1.0)
genProp.toesRP = bpy.props.FloatProperty(update=setBipedWalk, name="toesRP", default=-0.0)
genProp.toesRR = bpy.props.FloatProperty(update=setBipedWalk, name="toesRR", default=1.0)
#
# Sliders?
genProp.Arms_UD = bpy.props.FloatProperty(update=setArms, name="Arms_UD", default=0.0)
genProp.LArm_Twist = bpy.props.FloatProperty(update= setArmTwistL, name="LArm_Twist", default=0.0)
genProp.RArm_Twist = bpy.props.FloatProperty(update= setArmTwistR, name="RArm_Twist", default=0.0)
genProp.Arm_Rotation = bpy.props.FloatProperty(update=setArmRotation, name="Arm_Rotation", default=3.0)
genProp.LHand_OC = bpy.props.FloatProperty(update=LHandOpenClose, name="LHand_OC", default=0.0)
genProp.LHand_Spread = bpy.props.FloatProperty(update=LHandSpread, name="LHand_Spread", default=0.0)
genProp.RHand_OC = bpy.props.FloatProperty(update=RHandOpenClose, name="RHand_OC", default=0.0)
genProp.RHand_Spread = bpy.props.FloatProperty(update=RHandSpread, name="RHand_Spread", default=0.0)
genProp.Head_UD = bpy.props.FloatProperty(update=setHead, name="Head_UD", default=0.0)
genProp.Head_LR = bpy.props.FloatProperty(update=setHead, name="Head_LR", default=0.0)
genProp.Head_Turn = bpy.props.FloatProperty(update=setHead, name="Head_Turn", default=0.0)
genProp.Jaw_OC = bpy.props.FloatProperty(update=setJaw, name="Jaw_OC", default=0.0)
genProp.Eye_LR = bpy.props.FloatProperty(update=setEye, name="Eye_LR", default=0.0)
genProp.Eye_UD = bpy.props.FloatProperty(update=setEye, name="Eye_UD", default=0.0)
#
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# END: BIPED PROPERTIES (with update= ) AND THEIR FUNCTIONS PRECEEDING THEM
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
        bpy.ops.object.mode_set(mode='OBJECT')
        return{'FINISHED'}

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# END of Common panel for all characters and appendages.
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# |
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
        layout.row().operator("object.pose_btn")  # (Common to all)
        layout.row().operator("object.drop_arms_btn")  # Drop Arms
        layout.row().operator("object.walk_btn")  # Set Walk
        layout.row().operator("object.run_btn")  # Set Run
        layout.row().operator("object.control1_btn") # Character controls
        layout.row().operator("object.control2_btn") # Character controls
        #layout.row().operator("object.arm_action_btn")  # Arm action
        #layout.row().operator("object.leg_action_btn")  # Leg action
        #layout.row().operator("object.reset_btn")  # Revert Advanced Controls

class BIPED_OT_control_I(bpy.types.Operator):
    bl_idname = "object.control1_btn"
    """Control Dialog box"""
    bl_label = "Controls I"
    #
    speed : bpy.props.FloatProperty(name="Speed", default=0.0)
    cycle : bpy.props.FloatProperty(name="Cycle", default=1.0)
    direction : bpy.props.FloatProperty(name= "Direction")
    X_Location : bpy.props.FloatProperty(name= "X_Location")
    Y_Location : bpy.props.FloatProperty(name= "Y_Location")
    Z_Location : bpy.props.FloatProperty(name= "Z_Location", default=0.0)
    Sway_LR : bpy.props.FloatProperty(name= "Sway_LR", default=6.0)
    Sway_FB : bpy.props.FloatProperty(name= "Sway_FB", default=6.0)
    bounce : bpy.props.FloatProperty(name= "Bounce", default=0.0)
    Shoulder_Rotation : bpy.props.FloatProperty(name= "Shoulder_Rotation", default=10.0)
    Shoulder_UD : bpy.props.FloatProperty(name= "Shoulder_UD", default=10.0)
    Leg_Spread : bpy.props.FloatProperty(name= "Leg_Spread", default=0.0)
    Hip_Sway : bpy.props.FloatProperty(name= "Hip_Sway", default=5.0)
    Hip_Rotate : bpy.props.FloatProperty(name= "Hip_Rotate", default=5.0)
    Hip_UD : bpy.props.FloatProperty(name= "Hip_UD", default=1.0)
    Leg_Arch : bpy.props.FloatProperty(name= "Leg_Arch", default=0.0)
    rotatePosition : bpy.props.FloatProperty(name= "Rotate Position", default=0.1)
    rotateRange : bpy.props.FloatProperty(name= "Rotate Range", default=1.0)
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
        bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}
    #
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

class BIPED_OT_control_II(bpy.types.Operator):
    bl_idname = "object.control2_btn"
    """Control Dialog box"""
    bl_label = "Controls II"
    #
    Arms_UD : bpy.props.FloatProperty(name="Arms_UD", default=0.0) # slider=True, 
    LArm_Twist : bpy.props.FloatProperty(name="LArm_Twist", default=0.0)
    RArm_Twist : bpy.props.FloatProperty(name="RArm_Twist", default=0.0)
    Arm_Rotation : bpy.props.FloatProperty(name="Arm_Rotation", default=0.0)
    LHand_Spread : bpy.props.FloatProperty(name="LHand_Spread", default=0.0)
    LHand_OC : bpy.props.FloatProperty(name="LHand_OC", default=0.0)
    RHand_Spread : bpy.props.FloatProperty(name="RHand_Spread", default=0.0)
    RHand_OC : bpy.props.FloatProperty(name="RHand_OC", default=0.0)
    Head_UD : bpy.props.FloatProperty(name="Head_UD", default=0.0)
    Head_LR : bpy.props.FloatProperty(name="Head_LR", default=0.0)
    Head_Turn : bpy.props.FloatProperty(name="Head_Turn", default=0.0)
    Jaw_OC : bpy.props.FloatProperty(name="Jaw_OC", default=0.0)
    Eye_LR : bpy.props.FloatProperty(name="Eye_LR", default=0.0)
    Eye_UD : bpy.props.FloatProperty(name="Eye_UD", default=0.0)
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
        setBipedWalk(self, context)
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
        if(genProp.toggleArmAction == True):
            #setWalk()  Below is  not likely to work
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
            setBipedWalk()
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

class Biped():
    bl_label = "bipedPanel"
    bl_description = "biped"
    bl_options = {"REGISTER", "UNDO"}
    armatureName = "" # rgbiped01_at for troubleshooting
    armature = ""
    def setBipedPropertiesPanel():
        CONTROL_PT_Panel

biped = Biped

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# END PANELS CLASS
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# cycle control
def clock(freq=9, amp=.5):  # Sets the pace
    cycle = cwmPanel.cycle
    frame = bpy.context.scene.frame_current
    stp = amp * abs((cycle*frame)/freq % 4 - 2) - amp
    return round(stp, 2)

# add to namespace
bpy.app.driver_namespace['clock'] = clock

# walk speed control
def setHorizontalSpeed():
    spd = cwmPanel.speed
    frame = bpy.context.scene.frame_current
    spd = frame * .04 * spd
    return round(spd, 2)

# walk speed control
def setHorizontalYSpeed():
    spd = cwmPanel.speed
    frame = bpy.context.scene.frame_current
    spd = frame * .04 * spd
    return round(spd, 2)

bpy.app.driver_namespace['setHorizontalSpeed'] = setHorizontalSpeed

# getEuler output represents:
# bpy.data.objects['rg00biped'].pose.bones["backCenter"]
def getEuler(str_bone_name):  # *** Switching to pose mode must be external
    ob = bpy.context.object
    bone = ob.pose.bones[str_bone_name]
    bone.rotation_mode = 'XYZ'
    return bone

# Equation for bone joints, with euler transform, axis 0=x 1=y 2=z
# Note also that fn must be inserted as a STLING in the expression!
def setDriver(bone, fn="0", axis=0, movementType='rotation_euler'):
    eulerDriver = bone.driver_add(movementType)
    eulerDriver[axis].driver.type = 'SCRIPTED'
    eulerDriver[axis].driver.expression = fn
    return eulerDriver

# Set Driver For Single Axis Only:
def setAxisDriver(euler, fn="0", axis=0, movementType='rotation_euler'):
    edriver = euler.driver_add(movementType, axis)
    edriver.driver.type = 'SCRIPTED'
    edriver.driver.expression = fn
    return edriver

def boneMirror(armature, vector, mirror = False):
    bpy.data.armatures[biped.armatureName].use_mirror_x = mirror
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

def getSpecialString(atFrame):
    s = str(atFrame[1])
    n = s.find('default')
    s = s[n+12:]
    n = s.find("'")
    s = s[:-n]
    return s
    
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Start Utility Class and its associated functions
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def selectBoneByName(name):
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones[name].select_tail=True

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

def getSceneObjectNumber():
    n = 0
    for ob in list(bpy.data.objects):
        if ob.name.startswith('rg') == True:
            n = n + 1
    return n

def setName(type, n):
    name = "rg" + type + "0" + str(n + 1)  # Assume n < 10 
    if (n > 9):  # Change x.name if previous assumption is wrong
        name = "rg" + type + str(n + 1)
    return name

def buildRootArmature(charClass, strCharName, x, y, z):
    at = bpy.data.armatures.new(strCharName + '_at')  # at = Armature
    biped.armature = at
    biped.armatureName = at.name
    bpy.context.scene.frame_start = 0
    charClass.rig = bpy.data.objects.new(strCharName, at)  # rig = Armature object
    charClass.rig.show_in_front = True
    charClass.x = x
    charClass.y = y
    charClass.rig.location = (x, y, z)  # Set armature point locatioon
    # Link to scene
    coll = bpy.context.view_layer.active_layer_collection.collection
    coll.objects.link(charClass.rig)
    bpy.context.view_layer.objects.active = charClass.rig
    bpy.context.view_layer.update()
    return at

def setHandle(at, strCharName, Vhead, Vtail):
    bpy.ops.object.editmode_toggle()
    bone = at.edit_bones.new(strCharName + '_bone')
    bone.head = Vtail
    bone.tail = Vhead
    return bone

def deselectAll():
    bpy.ops.armature.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    for ob in bpy.context.selected_objects:
        ob.select_set(False)

def characterExists(): # Checks based on selected objects
    charTypes = ["rgbiped","rgcentaur","rgquadruped","rgbird","rgadWings"]
    for character in bpy.context.selected_objects:
        if(character.name[:-2] in charTypes):
            return True
    return False

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

# The only reason for using this function is to get the currently 
# selected character name and apply the correct functions.
def setWalk():
    if(getSelectedCharacterName().startswith("rgbiped")):
        setBipedWalk(self, context)
    else:
        print("A character must be selected to activate it!")

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# setEnve1opeWeights - COMMON FUNCTION 
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def setEnvelopeWeights(name):
    # The position of the following two for loops is important;
    # it initializes all bones to have a specific envelope weight
    # in case the bone has not been set manually as below. It 
    # cannot be placed afterwards, or it will override the settings.
    for b in bpy.data.objects[name].pose.bones:
        b.rotation_mode = 'XYZ'
    for b in bpy.context.object.data.edit_bones:
        b.envelope_distance = 0.05  # Default envelope distance
        b.head_radius = 0.02
        b.tail_radius = 0.02
        #b.envelope_weight = 2.0
    #
    for b in bpy.context.object.data.edit_bones:
        # Set weights for biped lower body
        if(name.startswith("rgbiped")):
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
        if(name.startswith("rgbiped")) or (name.startswith("rgcentaur")):
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
    biped = Biped # instantiated, but does not need to return to any other function
    # Initiate building of bones
    n = getSceneObjectNumber()  # Each character name will be numbered sequentially.
    biped.name = setName('biped', n)
    mod = math.fmod(n, 2)
    if(mod == 0):
        x = 1.0 * n - mod    # Can you build an armature at the origin
    else:                    # then start building bones independent of it?
        x = 1.0 * -n - mod
    y = -.4 * n; z = cwmPanel.Z_Location  # y = Head of handle (Armature point)
    at = buildRootArmature(biped, biped.name, x, y, z) # creates point, no bone yet
    biped.armature = at
    # %%% FIRST BONE %%% FIRST CHARACTER WILL E NAMED rgbiped01
    VHead = [0, 0, 0]
    Vtail = [0, -.3, 0] # Tail of Handle  
    bone = setHandle(at, biped.name, VHead, Vtail) 
    bpy.data.objects[biped.name].show_in_front = True
    #
    V_angle = (0, 0, 0) # Bottom (Tail)
    angle = boneMirror(at, V_angle, False)
    V_hipC = (0, .1, -.1)
    boneMirror(at, V_hipC, False)
    #*** Active bone is NOT right above, but next bone above ***
    bone_name = getActiveBoneName() 
    at.edit_bones[bone_name].name = "angle"
    #
    V_next = (0, 0, -.14)
    boneMirror(at, V_next, False)
    bone_name = getActiveBoneName() 
    at.edit_bones[bone_name].name = "hipC"
    # start mirroring! Can't use naming above on mirrored bones
    V_hip = (.12, 0, 0)
    boneMirror(at, V_hip, True)
    V_femurJ1 = (0, 0, -.23)
    boneMirror(at, V_femurJ1, True)
    V_femurJ2 = (0, 0, -.24)
    boneMirror(at, V_femurJ2, True)
    V_tibiaJ1 = (0, 0, -.2)
    boneMirror(at, V_tibiaJ1, True)
    V_tibiaJ2 = (0, 0, -.14)
    boneMirror(at, V_tibiaJ2, True)
    V_ankle = (0, .18, -.06)
    boneMirror(at, V_ankle, True)
    V_toe = (0, .08, 0)
    boneMirror(at, V_toe, True)
    at.edit_bones["hipC_L"].name = "hip.R"
    at.edit_bones['hipC_R'].name = "hip.L"
    at.edit_bones['hipC_R.001'].name = "femurJ1.L"
    at.edit_bones['hipC_L.001'].name = "femurJ1.R"
    at.edit_bones['hipC_R.002'].name = "femurJ2.L"
    at.edit_bones['hipC_L.002'].name = "femurJ2.R"
    at.edit_bones['hipC_R.003'].name = "tibiaJ1.L"
    at.edit_bones['hipC_L.003'].name = "tibiaJ1.R"    
    at.edit_bones['hipC_R.004'].name = "tibiaJ2.L"
    at.edit_bones['hipC_L.004'].name = "tibiaJ2.R"    
    at.edit_bones['hipC_R.005'].name = "ankle.L"
    at.edit_bones['hipC_L.005'].name = "ankle.R"
    at.edit_bones['hipC_R.006'].name = "toe.L"
    at.edit_bones['hipC_L.006'].name = "toe.R"
    #
    # Heel starts were the tibia ends, same place as the ankle bone
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["ankle.L"].select_tail=True
    at.edit_bones["ankle.R"].select_tail=True
    V_heel = (0, -.2, -.01)
    boneMirror(at, V_heel, True)
    at.edit_bones['ankle.L.001'].name = "heel.L"
    at.edit_bones['ankle.R.001'].name = "heel.R"
    #
    # Reinforce rear
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["angle"].select_tail=True
    V_posterior = (0, -.1, -.04)
    boneMirror(at, V_posterior, False)
    V_posterior1 = (-.12, 0, -.01)
    boneMirror(at, V_posterior1, True)
    V_posterior2 = (0, 0, -.14)
    boneMirror(at, V_posterior2, True)
    #
    bpy.ops.armature.select_all(action='DESELECT')
    selectBonePartByName("angle.001", True) # Tail=True
    V_tailBone = (0, 0, -.14)
    boneMirror(at, V_tailBone, False)
    at.edit_bones['angle.001'].name = "Posterior1"
    at.edit_bones['angle.001_L'].name = "fixPosterior1.L"
    at.edit_bones['angle.001_R'].name = "fixPosterior1.R"
    at.edit_bones['angle.001_L.001'].name = "fixPosterior2.L"
    at.edit_bones['angle.001_R.001'].name = "fixPosterior2.R"
    at.edit_bones['angle.002'].name = "fixPosterior2.C"
    #
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # END OF Biped Skeleton LOWER BODY BUILD
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    biped.armature = at  
    buildHumanUpperBody()
    ob = bpy.data.objects.get(at.name[:-3])
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    setEnvelopeWeights(at.name[:-3])
    #
    deselectAll()
    ob = bpy.data.objects.get(biped.name)
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.context.object.rotation_euler[2] = -1.5708

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#  END BIPED SKELETON BUILD
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# COMMON FUNCTION - bui1dHumanUpperBody     To 1779
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def buildHumanUpperBody(boneName="angle", V_bBackJ1 = (0, 0, 0.1)):
    biped = Biped
    at = biped.armature
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones[boneName].select_tail=True
    boneMirror(at, V_bBackJ1, False)
    V_bBackJ2 = (0, 0, 0.1)
    boneMirror(at, V_bBackJ2, False)
    V_bBackJ3 = (0, 0, 0.14)
    boneMirror(at, V_bBackJ3, False)
    V_bBackJ4 = (0, 0, 0.1)
    boneMirror(at, V_bBackJ4, False)
    V_bBackJ5 = (0, 0, 0.1)
    boneMirror(at, V_bBackJ5, False)
    at.edit_bones[boneName + ".001"].name = "bBackJ1"
    at.edit_bones[boneName + ".002"].name = "bBackJ2"
    at.edit_bones[boneName + ".003"].name = "bBackJ3"
    at.edit_bones[boneName + ".004"].name = "bBackJ4"
    at.edit_bones[boneName + ".005"].name = "bBackJ5"
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Start arms  
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Shoulder area  
    V_clavicle = (.11, 0, -.02)
    boneMirror(at, V_clavicle, True)
    V_shoulder = (.19, 0, -.03)
    boneMirror(at, V_shoulder, True)
    V_armJ1 = (.12, 0, 0)
    boneMirror(at, V_armJ1, True)
    V_armJ2 = (.14, 0, -.01)
    boneMirror(at, V_armJ2, True)
    V_armJ3 = (.08, 0, 0)
    boneMirror(at, V_armJ3, True)
    V_armJ4 = (.1, 0, 0)
    boneMirror(at, V_armJ4, True)
    V_armJ5 = (.1, 0, 0)
    boneMirror(at, V_armJ5, True)
    at.edit_bones['bBackJ5_L'].name = "clavicle.R"
    at.edit_bones['bBackJ5_R'].name = "clavicle.L"
    at.edit_bones['bBackJ5_L.001'].name = "shoulder.R"
    at.edit_bones['bBackJ5_R.001'].name = "shoulder.L"
    at.edit_bones['bBackJ5_L.002'].name = "armJ1.R"
    at.edit_bones['bBackJ5_R.002'].name = "armJ1.L"
    at.edit_bones['bBackJ5_L.003'].name = "armJ2.R"
    at.edit_bones['bBackJ5_R.003'].name = "armJ2.L"
    at.edit_bones['bBackJ5_L.004'].name = "armJ3.R"
    at.edit_bones['bBackJ5_R.004'].name = "armJ3.L"
    at.edit_bones['bBackJ5_L.005'].name = "armJ4.R"
    at.edit_bones['bBackJ5_R.005'].name = "armJ4.L"
    at.edit_bones['bBackJ5_L.006'].name = "armJ5.R"
    at.edit_bones['bBackJ5_R.006'].name = "armJ5.L"
    # Middle finger  
    V_wristBase2 = (0.098, .002, -.006)
    boneMirror(at, V_wristBase2, True)
    V_midJ1 = (.046, 0, 0)
    boneMirror(at, V_midJ1, True)
    V_midJ2 = (.04, 0, 0)
    boneMirror(at, V_midJ2, True)
    V_midJ3 = (.02, 0, 0)
    boneMirror(at, V_midJ3, True)
    at.edit_bones['armJ5.L.001'].name = "wristBase2.L"
    at.edit_bones['armJ5.R.001'].name = "wristBase2.R"
    at.edit_bones['armJ5.L.002'].name = "midJ1.L"
    at.edit_bones['armJ5.R.002'].name = "midJ1.R"
    at.edit_bones['armJ5.L.003'].name = "midJ2.L"
    at.edit_bones['armJ5.R.003'].name = "midJ2.R"
    at.edit_bones['armJ5.L.004'].name = "midJ3.L"
    at.edit_bones['armJ5.R.004'].name = "midJ3.R"
    # Shift back to wrist
    # Index Finger bones   
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["armJ5.R"].select_tail=True
    V_wristBase1 = (.098, .03, -.006)
    boneMirror(at, V_wristBase1, True)
    V_indexJ1 = (.032, .011, 0)
    boneMirror(at, V_indexJ1, True)
    V_indexJ2 = (.024, .01, 0)
    boneMirror(at, V_indexJ2, True)
    V_indexJ3 = (.02, .008, 0)
    boneMirror(at, V_indexJ3, True)
    at.edit_bones['armJ5.L.001'].name = "wristBase1.L"
    at.edit_bones['armJ5.R.001'].name = "wristBase1.R"
    at.edit_bones['armJ5.L.002'].name = "indexJ1.L"
    at.edit_bones['armJ5.R.002'].name = "indexJ1.R"
    at.edit_bones['armJ5.L.003'].name = "indexJ2.L"
    at.edit_bones['armJ5.R.003'].name = "indexJ2.R"
    at.edit_bones['armJ5.L.004'].name = "indexJ3.L"
    at.edit_bones['armJ5.R.004'].name = "indexJ3.R"
    #
    # Shift back to wrist
    # Ring Finger bones
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["armJ5.R"].select_tail=True
    V_wristBase3 = (.098, -.02, -.006)
    boneMirror(at, V_wristBase3, True)
    V_ringJ1 = (.042, -.01, 0)
    boneMirror(at, V_ringJ1, True)
    V_ringJ2 = (.032, -.007, 0)
    boneMirror(at, V_ringJ2, True)
    V_ringJ3 = (.02, -.004, 0)
    boneMirror(at, V_ringJ3, True)
    at.edit_bones['armJ5.L.001'].name = "wristBase3.L"
    at.edit_bones['armJ5.R.001'].name = "wristBase3.R"
    at.edit_bones['armJ5.L.002'].name = "ringJ1.L"
    at.edit_bones['armJ5.R.002'].name = "ringJ1.R"
    at.edit_bones['armJ5.L.003'].name = "ringJ2.L"
    at.edit_bones['armJ5.R.003'].name = "ringJ2.R"
    at.edit_bones['armJ5.L.004'].name = "ringJ3.L"
    at.edit_bones['armJ5.R.004'].name = "ringJ3.R"
    # Shift back to wrist
    # Pinky Finger bones  
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["armJ5.R"].select_tail=True
    V_pinkyBase = (.095, -.046, -.006)
    boneMirror(at, V_pinkyBase, True)
    V_pinkyJ1 = (.024, -.016, 0)
    boneMirror(at, V_pinkyJ1, True)
    V_pinkyJ2 = (.02, -.012, 0)
    boneMirror(at, V_pinkyJ2, True)
    V_pinkyJ3 = (.02, -.01, 0)
    boneMirror(at, V_pinkyJ3, True)
    at.edit_bones['armJ5.L.001'].name = "wristBase4.L"
    at.edit_bones['armJ5.R.001'].name = "wristBase4.R"
    at.edit_bones['armJ5.L.002'].name = "pinkyJ1.L"
    at.edit_bones['armJ5.R.002'].name = "pinkyJ1.R"
    at.edit_bones['armJ5.L.003'].name = "pinkyJ2.L"
    at.edit_bones['armJ5.R.003'].name = "pinkyJ2.R"
    at.edit_bones['armJ5.L.004'].name = "pinkyJ3.L"
    at.edit_bones['armJ5.R.004'].name = "pinkyJ3.R"
    #
    # Shift back to wrist
    # Thumb Finger bones
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["armJ5.R"].select_tail=True
    V_thumbBase = (.002, .008, 0)
    boneMirror(at, V_thumbBase, True)
    V_thumbJ1 = (.038, .044, -0.01)
    boneMirror(at, V_thumbJ1, True)
    V_thumbJ2 = (.032, .02, -0.006)
    boneMirror(at, V_thumbJ2, True)
    V_thumbJ3 = (.02, .01, 0)
    boneMirror(at, V_thumbJ3, True)
    at.edit_bones['armJ5.L.001'].name = "thumbBase.L"
    at.edit_bones['armJ5.R.001'].name = "thumbBase.R"
    at.edit_bones['armJ5.L.002'].name = "thumbJ1.L"
    at.edit_bones['armJ5.R.002'].name = "thumbJ1.R"
    at.edit_bones['armJ5.L.003'].name = "thumbJ2.L"
    at.edit_bones['armJ5.R.003'].name = "thumbJ2.R"
    at.edit_bones['armJ5.L.004'].name = "thumbJ3.L"
    at.edit_bones['armJ5.R.004'].name = "thumbJ3.R"
    # End arm and hand creation
    #
    # Resume spine
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["bBackJ5"].select_tail=True
    V_neckJ1 = (0, 0, 0.03)
    boneMirror(at, V_neckJ1, False)
    V_neckJ2 = (0, 0, 0.03)
    boneMirror(at, V_neckJ2, False)
    V_neckJ3 = (0, 0, 0.03)
    boneMirror(at, V_neckJ3, False)
    V_neckJ4 = (0, 0, 0.03)
    boneMirror(at, V_neckJ4, False)
    V_headBase = (0, 0, 0.09)
    boneMirror(at, V_headBase, False)
    V_eyeLevel = (0, 0, .04)
    boneMirror(at, V_eyeLevel, False)
    V_headTop = (0, -.05, 0)
    boneMirror(at, V_headTop, False)
    V_headFore = (0, .08, .09)
    boneMirror(at, V_headFore, False)
    at.edit_bones['bBackJ5.001'].name = "neckJ1"
    at.edit_bones['bBackJ5.002'].name = "neckJ2"
    at.edit_bones['bBackJ5.003'].name = "neckJ3"
    at.edit_bones['bBackJ5.004'].name = "neckJ4"
    at.edit_bones['bBackJ5.005'].name = "headBase"
    at.edit_bones['bBackJ5.006'].name = "eyeLevel"
    at.edit_bones['bBackJ5.007'].name = "headTop"
    at.edit_bones['bBackJ5.008'].name = "headFore"
    # jaw
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["neckJ4"].select_tail=True
    V_jaw = (0, .026, -.004)
    boneMirror(at, V_jaw, False)
    V_jaw1 = (.06, .02, 0)
    boneMirror(at, V_jaw1, True)
    V_jaw2 = (-.05, .1, 0)
    boneMirror(at, V_jaw2, True)
    at.edit_bones['neckJ4.001'].name = "jaw"
    at.edit_bones['neckJ4.001_R'].name = "jaw1.L"
    at.edit_bones['neckJ4.001_L'].name = "jaw1.R"
    at.edit_bones['neckJ4.001_R.001'].name = "jaw2.L"
    at.edit_bones['neckJ4.001_L.001'].name = "jaw2.R"
    # upperMouth
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["neckJ4"].select_tail=True
    V_baseMouth1 = (0, .026, 0.046) 
    boneMirror(at, V_baseMouth1, False)
    V_baseMouth2 = (.06, .02, 0)
    boneMirror(at, V_baseMouth2, True)
    V_baseMouth3 = (-.05, .11, -.004)
    boneMirror(at, V_baseMouth3, True)
    at.edit_bones['neckJ4.001'].name = "baseMouth1"
    at.edit_bones['neckJ4.001_R'].name = "baseMouth2.L"
    at.edit_bones['neckJ4.001_L'].name = "baseMouth2.R"
    at.edit_bones['neckJ4.001_R.001'].name = "baseMouth3.L"
    at.edit_bones['neckJ4.001_L.001'].name = "baseMouth3.R"
    #
    # Eye Level
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["eyeLevel"].select_tail=True
    V_eyebase = (-.03, 0.1, 0)
    boneMirror(at, V_eyebase, True)
    V_eye = (0, 0.03, 0)
    boneMirror(at, V_eye, True)
    at.edit_bones['eyeLevel_L'].name = "eyeBase.L"
    at.edit_bones['eyeLevel_R'].name = "eyeBase.R"
    at.edit_bones['eyeLevel_L.001'].name = "eye.L"
    at.edit_bones['eyeLevel_R.001'].name = "eye.R"
    # nose
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["headBase"].select_tail=True
    V_noseBase = (0, .138, 0)
    boneMirror(at, V_noseBase, False)
    V_nose = (0, 0.02, -.02)
    boneMirror(at, V_nose, False)
    at.edit_bones['headBase.001'].name = "noseBase"
    at.edit_bones['headBase.002'].name = "nose"
    #
    # Add front fix
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["bBackJ5"].select_tail=True
    V_fixChestFront = (0, .06, -.03)
    boneMirror(at, V_fixChestFront, False)    
    V_fixChestFront1 = (0.185, 0, -.1)
    boneMirror(at, V_fixChestFront1, True)
    V_fixChestFront2 = (-.04, 0, -.12)
    boneMirror(at, V_fixChestFront2, True)
    at.edit_bones['bBackJ5.001'].name = "fixChestFront"
    at.edit_bones['bBackJ5.001_R'].name = "fixChestFront1.L"
    at.edit_bones['bBackJ5.001_L'].name = "fixChestFront1.R"
    at.edit_bones['bBackJ5.001_R.001'].name = "fixChestFront2.L"
    at.edit_bones['bBackJ5.001_L.001'].name = "fixChestFront2.R"
    # Add center fix
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["bBackJ5"].select_tail=True
    V_fixChestCenter1 = (0.19, 0, -.13)
    boneMirror(at, V_fixChestCenter1, True)
    V_fixChestCenter2 = (-.05, 0, -.12)
    boneMirror(at, V_fixChestCenter2, True)
    at.edit_bones['bBackJ5_R'].name = "fixChestCenter1.L"
    at.edit_bones['bBackJ5_L'].name = "fixChestCenter1.R"
    at.edit_bones['bBackJ5_R.001'].name = "fixChestCenter2.L"
    at.edit_bones['bBackJ5_L.001'].name = "fixChestCenter2.R"
    # Add rear fix
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["bBackJ5"].select_head=True
    V_fixChestBack = (0, -.06, 0)
    boneMirror(at, V_fixChestBack, False)    
    V_fixChestBack1 = (0.195, 0, -.02)
    boneMirror(at, V_fixChestBack1, True)
    V_fixChestBack2 = (-.06, 0, -.12)
    boneMirror(at, V_fixChestBack2, True)
    at.edit_bones['bBackJ5.001'].name = "fixChestBack"
    at.edit_bones['bBackJ5.001_R'].name = "fixChestBack1.L"
    at.edit_bones['bBackJ5.001_L'].name = "fixChestBack1.R"
    at.edit_bones['bBackJ5.001_R.001'].name = "fixChestBack2.L"
    at.edit_bones['bBackJ5.001_L.001'].name = "fixChestBack2.R"
    #
    # Upper shoulder
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["bBackJ5"].select_tail=True
    V_fixUpperShoulder1 = (0, -.06, -.03)
    boneMirror(at, V_fixUpperShoulder1, False)
    V_fixUpperShoulder2 = (0.195, 0, -.02)
    boneMirror(at, V_fixUpperShoulder2, True)
    at.edit_bones['bBackJ5.001'].name = "fixShoulderBack.L"
    at.edit_bones['bBackJ5.001_R'].name = "fixShoulderBack1.L"
    at.edit_bones['bBackJ5.001_L'].name = "fixShoulderBack1.R"
    #self = "Nothing"

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

class Centaur():
    bl_label = "centaurPanel"
    bl_description = "centaur"
    bl_options = {"REGISTER", "UNDO"}
    armatureName = "" # rgcentaur01_at for troubleshooting
    armature = ""
    def setCentaurPropertiesPanel():
        CONTROL_PT_Panel

centaur = Centaur

def buildCentaurSkeleton():      # ENDS 2800
    V_origin = [0.0, 0.0, 0.0]
    centaur = Centaur
    #addCharactersProperties()
    '''
    bpy.types.WindowManager.speed = bpy.props.FloatProperty(update=setHorizontalSpeed, name="Speed", default=0.0)
    bpy.types.WindowManager.direction = bpy.props.FloatProperty(update=setHorizontalSpeed, name="Direction", default=0.0)
    bpy.types.WindowManager.cycle = bpy.props.FloatProperty(update=centaurFns.setCentaurWalk, name="Cycle", default=1.0)
    # Pose character button
    bpy.types.WindowManager.armsUD = bpy.props.FloatProperty(update=centaurFns.setArms, name="ArmsUD", default=0.0)
    bpy.types.WindowManager.shoulderRotate = bpy.props.FloatProperty(update=centaurFns.setShoulder, name="Shoulder Rotate", default=3.0)
    bpy.types.WindowManager.shoulderUD = bpy.props.FloatProperty(update=centaurFns.setShoulder, name="ShoulderUD", default=3.0)
    bpy.types.WindowManager.armRotation = bpy.props.FloatProperty(update=centaurFns.setArmRotation, name="Arm Rotation", default=3.0)
    bpy.types.WindowManager.armTwistR = bpy.props.FloatProperty(update= centaurFns.setArmTwistR, name="R Arm Twist", default=0.0)
    bpy.types.WindowManager.armTwistL = bpy.props.FloatProperty(update= centaurFns.setArmTwistL, name="L Arm Twist", default=0.0)
    bpy.types.WindowManager.RHandSpread = bpy.props.FloatProperty(update=centaurFns.setRHand, name="RHand Spread", default=9.0)
    bpy.types.WindowManager.LHandSpread = bpy.props.FloatProperty(update=centaurFns.setLHand, name="LHand Spread", default=9.0)
    bpy.types.WindowManager.RHandOC = bpy.props.FloatProperty(update=centaurFns.setRHand, name="RHandOC", default=0.0)
    bpy.types.WindowManager.LHandOC = bpy.props.FloatProperty(update=centaurFns.setLHand, name="LHandOC", default=0.0)
    # Drop Arms button
    # De-activate Arm Movements Button
    # Activate Arm Movements Button
    bpy.types.WindowManager.swayLR = bpy.props.FloatProperty(update=centaurFns.setswayLR, name="Sway RL", default=0.0)
    bpy.types.WindowManager.swayFB = bpy.props.FloatProperty(update=centaurFns.setSwayFB, name="Sway FB", default=0.0)
    bpy.types.WindowManager.bounce = bpy.props.FloatProperty(update=centaurFns.setBounce, name="Bounce", default=1.4)
    bpy.types.WindowManager.hipRotate = bpy.props.FloatProperty(update=centaurFns.setHip, name="Hip Rotate", default=1.0)
    bpy.types.WindowManager.hipUD = bpy.props.FloatProperty(update=centaurFns.setHip, name="HipUD", default=2.0)
    # De-activate Leg Movements Button
    # Activate Leg Movements Button
    bpy.types.WindowManager.neckFB = bpy.props.FloatProperty(update=centaurFns.setNeck, name="NeckFB", default=0.0)
    bpy.types.WindowManager.neckLR = bpy.props.FloatProperty(update=centaurFns.setNeck, name="neckLR", default=0.0)
    bpy.types.WindowManager.neckTurn = bpy.props.FloatProperty(update=centaurFns.setNeck, name="NeckTurn", default=0.0)
    bpy.types.WindowManager.headUD = bpy.props.FloatProperty(update=centaurFns.setHead, name="HeadUD", default=0.0)
    bpy.types.WindowManager.headLR = bpy.props.FloatProperty(update=centaurFns.setHead, name="headLR", default=0.0)
    bpy.types.WindowManager.headTurn = bpy.props.FloatProperty(update=centaurFns.setHead, name="HeadTurn", default=0.0)
    bpy.types.WindowManager.jawOC = bpy.props.FloatProperty(update=centaurFns.setJaw, name="JawOC", default=0.0)
    bpy.types.WindowManager.eyeLR = bpy.props.FloatProperty(update=centaurFns.setEye, name="eyeLR", default=0.0)
    bpy.types.WindowManager.eyeUD = bpy.props.FloatProperty(update=centaurFns.setEye, name="EyeUD", default=0.0)
    bpy.types.WindowManager.tailUD = bpy.props.FloatProperty(update=centaurFns.setTail, name="TailUD", default=0.0)
    bpy.types.WindowManager.tailLR = bpy.props.FloatProperty(update=centaurFns.setTail, name="tailLR", default=0.0)
    bpy.types.WindowManager.tailCurl = bpy.props.FloatProperty(update=centaurFns.setTail, name="TailCurl", default=0.0)    
    # Advanced Front Leg Controls %%%% RP = Rotate position  RR = Rotate range  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Front Leg Defaults Button 
    bpy.types.WindowManager.femurJ1RP = bpy.props.FloatProperty(update=centaurFns.setCentaurWalk, name="femurJ1RP", default=0.0)
    bpy.types.WindowManager.femurJ1RR = bpy.props.FloatProperty(update=centaurFns.setCentaurWalk, name="femurJ1RR", default=1.0)
    bpy.types.WindowManager.tibiaJ1RP = bpy.props.FloatProperty(update=centaurFns.setCentaurWalk, name="tibiaJ1RP", default=0.0)
    bpy.types.WindowManager.tibiaJ1RR = bpy.props.FloatProperty(update=centaurFns.setCentaurWalk, name="tibiaJ1RR", default=1.0)
    bpy.types.WindowManager.ankleRP = bpy.props.FloatProperty(update=centaurFns.setCentaurWalk, name="ankleRP", default=0.0)
    bpy.types.WindowManager.ankleRR = bpy.props.FloatProperty(update=centaurFns.setCentaurWalk, name="ankleRR", default=1.0)
    bpy.types.WindowManager.toesRP = bpy.props.FloatProperty(update=centaurFns.setCentaurWalk, name="toesRP", default=-0.0)
    bpy.types.WindowManager.toesRR = bpy.props.FloatProperty(update=centaurFns.setCentaurWalk, name="toesRR", default=1.0)
    # Advanced Rear Leg Controls %%%% RP = Rotate position  RR = Rotate range  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Rear Leg Defaults Button
    bpy.types.WindowManager.rearFemurJ1RP = bpy.props.FloatProperty(update=centaurFns.setCentaurWalk, name="Rear Leg RP", default=0.0)
    bpy.types.WindowManager.rearFemurJ1RR = bpy.props.FloatProperty(update=centaurFns.setCentaurWalk, name="Rear Leg RR", default=1.0)
    bpy.types.WindowManager.rearTibiaJ1RP = bpy.props.FloatProperty(update=centaurFns.setCentaurWalk, name="rearTibiaJ1RP", default=0.0)
    bpy.types.WindowManager.rearTibiaJ1RR = bpy.props.FloatProperty(update=centaurFns.setCentaurWalk, name="rearTibiaJ1RR", default=1.0)
    bpy.types.WindowManager.rearAnkleRP = bpy.props.FloatProperty(update=centaurFns.setCentaurWalk, name="rearAnkleRP", default=0.0)
    bpy.types.WindowManager.rearAnkleRR = bpy.props.FloatProperty(update=centaurFns.setCentaurWalk, name="rearAnkleRR", default=1.0)
    bpy.types.WindowManager.rearToesRP = bpy.props.FloatProperty(update=centaurFns.setCentaurWalk, name="rearToesRP", default=0.0)
    bpy.types.WindowManager.rearToesRR = bpy.props.FloatProperty(update=centaurFns.setCentaurWalk, name="rearToesRR", default=1.0)
    '''
    #
    #
    # Initiate building of bones
    n = getSceneObjectNumber()  # Each character name will be numbered sequentially.
    strName = setName('centaur', n)  # biped, centaur, bird, centaur, spider, kangaroo
    mod = math.fmod(n, 2)
    if(mod == 0):
        x = 1.1 * n - mod
    else:
        x = 1.1 * -n - mod
    y = -.4 * n; z = 1.14  # For Armature
    at = buildRootArmature(centaur, strName, x, y, z) # Start character armature and bones
    # Build root bone
    Vhead = [0, 0, 0] # TODO check
    Vtail = [0, 0, 0.3]  # End location of handle relative to armature origin - this effects coordinate system
    bone = setHandle(at, strName, Vhead, Vtail)
    #
    #
    buildQuadrupedBase(at)
    #
    V_bBackJ1 = (0, .032, 0.1)
    buildHumanUpperBody("qBackJ0", V_bBackJ1)
    setEnvelopeWeights(at.name[:-3])
    #
    ob = bpy.context.object
    deselectAll()
    bpy.data.objects[at.name[:-3]].location[2] = z  # 1.14
    bpy.ops.object.mode_set(mode='OBJECT')
    centaur.armature = at
    bpy.context.view_layer.objects.active = ob
    bpy.data.objects[at.name[:-3]].select_set(True)
    context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.context.object.rotation_euler[2] = -1.5708

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# COMMON FUNCTION - buildQuadrupedBaase
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def buildQuadrupedBase(at):
    bpy.ops.object.mode_set(mode='EDIT')
    V_origin = (0, 0, 0)
    V_qBackJ0 = (0, .2, 0)
    qBackJ0 = createBone("qBackJ0", V_origin, V_qBackJ0, 0)
    #
    deselectAll()
    selectBonePartByName("qBackJ0", tail=True)
    V_join = (0, 0, -.12)
    boneMirror(at, V_join, False)
    V_drop = (0, 0, -.17)
    boneMirror(at, V_drop, False)
    V_pelvis = (0, 0, -.15)
    boneMirror(at, V_pelvis, False)
    at.edit_bones["qBackJ0.001"].name = "join"
    at.edit_bones["qBackJ0.002"].name = "drop"
    at.edit_bones["qBackJ0.003"].name = "pelvis"
    # 
    # Start mirroring
    V_hip = (0.12, 0, 0)
    boneMirror(at, V_hip, True)
    V_femurJ1 = (0, 0, -.18)
    boneMirror(at, V_femurJ1, True)
    V_femurJ2 = (0, 0, -.16)
    boneMirror(at, V_femurJ2, True)
    V_tibiaJ1 = (0, 0, -.1)
    boneMirror(at, V_tibiaJ1, True)
    V_tibiaJ2 = (0, 0, -.1)
    boneMirror(at, V_tibiaJ2, True)
    V_ankle = (0, .046, -.08)
    boneMirror(at, V_ankle, True)
    V_toe = (0, .09, -.07)
    boneMirror(at, V_toe, True)
    at.edit_bones["pelvis_R"].name = "hip.L"
    at.edit_bones['pelvis_L'].name = "hip.R"
    at.edit_bones['pelvis_R.001'].name = "femurJ1.L"
    at.edit_bones['pelvis_L.001'].name = "femurJ1.R"
    at.edit_bones['pelvis_R.002'].name = "femurJ2.L"
    at.edit_bones['pelvis_L.002'].name = "femurJ2.R"
    at.edit_bones['pelvis_R.003'].name = "tibiaJ1.L"
    at.edit_bones['pelvis_L.003'].name = "tibiaJ1.R"    
    at.edit_bones['pelvis_R.004'].name = "tibiaJ2.L"
    at.edit_bones['pelvis_L.004'].name = "tibiaJ2.R"    
    at.edit_bones['pelvis_R.005'].name = "ankle.L"
    at.edit_bones['pelvis_L.005'].name = "ankle.R"
    at.edit_bones['pelvis_R.006'].name = "toe.L"
    at.edit_bones['pelvis_L.006'].name = "toe.R"
    #
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["qBackJ0"].select_head=True
    V_qBackJ1 = (0, -0.14, -.06)
    boneMirror(at, V_qBackJ1, False)
    V_qBackJ2 = (0, -.11, 0)
    boneMirror(at, V_qBackJ2, False)
    V_qBackJ3 = (0, -.12, .02)
    boneMirror(at, V_qBackJ3, False)
    V_qBackJ4 = (0, -.12, .02)
    boneMirror(at, V_qBackJ4, False)
    V_qBackJ5 = (0, -.14, .01)
    boneMirror(at, V_qBackJ5, False)
    at.edit_bones['qBackJ0.001'].name = "qBackJ1"
    at.edit_bones['qBackJ0.002'].name = "qBackJ2"
    at.edit_bones['qBackJ0.003'].name = "qBackJ3"
    at.edit_bones['qBackJ0.004'].name = "qBackJ4"
    at.edit_bones['qBackJ0.005'].name = "qBackJ5"
    #
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["qBackJ1"].select_head=True
    V_qfixRib1Top = (.1, 0, -.04)
    boneMirror(at, V_qfixRib1Top, True)
    V_qfixRib1B = (0, -.06, -0.4)
    boneMirror(at, V_qfixRib1B, True)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["qBackJ1"].select_tail=True
    V_qfixRib2Top = (.1, .02, 0)
    boneMirror(at, V_qfixRib2Top, True)
    V_qfixRib2B = (0, -.06, -.4)
    boneMirror(at, V_qfixRib2B, True)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["qBackJ3"].select_tail=True
    V_qfixRib3Top = (.1, 0, 0)
    boneMirror(at, V_qfixRib3Top, True)
    V_qfixRib3B = (0, 0, -.38)
    boneMirror(at, V_qfixRib3B, True)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["qBackJ4"].select_tail=True
    V_qfixRib4Top = (.1, 0, 0)
    boneMirror(at, V_qfixRib4Top, True)
    V_qfixRib4B = (0, 0, -.36)
    boneMirror(at, V_qfixRib4B, True)  
    at.edit_bones['qBackJ1_R'].name = "qfixRib1Top.L"
    at.edit_bones['qBackJ1_L'].name = "qfixRib1Top.R"
    at.edit_bones['qBackJ1_R.001'].name = "qfixRib1B.L"
    at.edit_bones['qBackJ1_L.001'].name = "qfixRib1B.R"
    at.edit_bones['qBackJ1_R.002'].name = "qfixRib2Top.L"
    at.edit_bones['qBackJ1_L.002'].name = "qfixRib2Top.R"
    at.edit_bones['qBackJ1_R.003'].name = "qfixRib2B.L"
    at.edit_bones['qBackJ1_L.003'].name = "qfixRib2B.R"
    at.edit_bones['qBackJ3_R'].name = "qfixRib3Top.L"
    at.edit_bones['qBackJ3_L'].name = "qfixRib3Top.R"
    at.edit_bones['qBackJ3_R.001'].name = "qfixRib3B.L"
    at.edit_bones['qBackJ3_L.001'].name = "qfixRib3B.R"
    at.edit_bones['qBackJ4_R'].name = "qfixRib4Top.L"
    at.edit_bones['qBackJ4_L'].name = "qfixRib4Top.R"
    at.edit_bones['qBackJ4_R.001'].name = "qfixRib4B.L"
    at.edit_bones['qBackJ4_L.001'].name = "qfixRib4B.R"
    #  
    # Create Rump with more fixs
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["qBackJ5"].select_tail=True
    V_hRumpJ1 = (0, -.16, -.004)
    boneMirror(at, V_hRumpJ1, False)
    V_hRumpJ2 = (0, -.12, -.004)
    boneMirror(at, V_hRumpJ2, False)
    V_hRumpJ3 = (0, -.05, 0)
    boneMirror(at, V_hRumpJ3, False)
    at.edit_bones['qBackJ5.001'].name = "hRumpJ1"
    at.edit_bones['qBackJ5.002'].name = "hRumpJ2"
    at.edit_bones['qBackJ5.003'].name = "hRumpJ3"
    #
    V_hTailJ1 = (0, -.04, .0146)
    boneMirror(at, V_hTailJ1, False)
    V_hTailJ2 = (0, -.06, .012)
    boneMirror(at, V_hTailJ2, False)
    V_hTailJ3 = (0, -.06, .01)
    boneMirror(at, V_hTailJ3, False)
    V_hTailJ4 = (0, -.06, 0)
    boneMirror(at, V_hTailJ4, False)
    V_hTailJ5 = (0, -.06, 0)
    boneMirror(at, V_hTailJ5, False)
    V_hTailJ6 = (0, -.06, 0)
    boneMirror(at, V_hTailJ6, False)
    V_hTailJ7 = (0, -.06, 0)
    boneMirror(at, V_hTailJ7, False)
    V_hTailJ8 = (0, -.06, 0)
    boneMirror(at, V_hTailJ8, False)
    V_hTailJ9 = (0, -.06, 0)
    boneMirror(at, V_hTailJ9, False)
    at.edit_bones['hRumpJ3.001'].name = "hTailJ1"
    at.edit_bones['hRumpJ3.002'].name = "hTailJ2"
    at.edit_bones['hRumpJ3.003'].name = "hTailJ3"
    at.edit_bones['hRumpJ3.004'].name = "hTailJ4"
    at.edit_bones['hRumpJ3.005'].name = "hTailJ5"
    at.edit_bones['hRumpJ3.006'].name = "hTailJ6"
    at.edit_bones['hRumpJ3.007'].name = "hTailJ7"
    at.edit_bones['hRumpJ3.008'].name = "hTailJ8"
    at.edit_bones['hRumpJ3.009'].name = "hTailJ9"
    # Add rear stabilization
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["hRumpJ1"].select_tail=True
    V_hRumpfix1 = (0, -.04, -.2)
    boneMirror(at, V_hRumpfix1, False)
    V_hRumpfix2 = (0, .12, -.06)
    boneMirror(at, V_hRumpfix2, False)
    V_hRumpfix3 = (0, .15, -.07)
    boneMirror(at, V_hRumpfix3, False)
    at.edit_bones['hRumpJ1.001'].name = "fixRump1"
    at.edit_bones['hRumpJ1.002'].name = "fixRump2"
    at.edit_bones['hRumpJ1.003'].name = "fixRump3"
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["hRumpJ2"].select_tail=True
    V_hRumpfix3 = (0, .14, .05)
    boneMirror(at, V_hRumpfix3, False)
    V_hRumpfix4 = (0, .2, .04)
    boneMirror(at, V_hRumpfix4, False)
    at.edit_bones['hRumpJ2.001'].name = "fixSacrum1"
    at.edit_bones['hRumpJ2.002'].name = "fixSacrum2"
    #
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["qBackJ5"].select_tail=True
    V_rearHip = (.16, 0, 0)
    boneMirror(at, V_rearHip, True)
    V_qfix4 = (0, -.16, -.11)
    boneMirror(at, V_qfix4, True)
    V_qfix5 = (0, 0, -.12)
    boneMirror(at, V_qfix5, True)
    at.edit_bones['qBackJ5_L'].name = "rearHip.R"
    at.edit_bones['qBackJ5_R'].name = "rearHip.L"
    at.edit_bones['qBackJ5_R.001'].name = "qfixHind1.L"
    at.edit_bones['qBackJ5_L.001'].name = "qfixHind1.R"
    at.edit_bones['qBackJ5_R.002'].name = "qfixHind2.L"
    at.edit_bones['qBackJ5_L.002'].name = "qfixHind2.R"
    #
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["rearHip.L"].select_tail=True
    V_rearHipJ1 = (0, -.08, -.27)
    boneMirror(at, V_rearHipJ1, True)
    V_rearFemurJ1 = (0, -.08, -.2)
    boneMirror(at, V_rearFemurJ1, True)
    V_rearFemurJ2 = (0, -.08, -.2)
    boneMirror(at, V_rearFemurJ2, True)
    V_rearTibiaJ1 = (0, 0, -.15)
    boneMirror(at, V_rearTibiaJ1, True)
    V_rearTibiaJ2 = (0, 0, -.15)
    boneMirror(at, V_rearTibiaJ2, True)
    V_horseRRearAnkle = (0, .06, -.07)
    boneMirror(at, V_horseRRearAnkle, True)
    V_horseRToe = (0, .04, -.06)
    boneMirror(at, V_horseRToe, True)
    at.edit_bones['rearHip.L.001'].name = "rearHipJ1.L"
    at.edit_bones['rearHip.R.001'].name = "rearHipJ1.R"
    at.edit_bones['rearHip.L.002'].name = "rearFemurJ1.L"
    at.edit_bones['rearHip.R.002'].name = "rearFemurJ1.R"
    at.edit_bones['rearHip.L.003'].name = "rearFemurJ2.L"
    at.edit_bones['rearHip.R.003'].name = "rearFemurJ2.R"
    at.edit_bones['rearHip.L.004'].name = "rearTibiaJ1.L"
    at.edit_bones['rearHip.R.004'].name = "rearTibiaJ1.R"
    at.edit_bones['rearHip.L.005'].name = "rearTibiaJ2.L"
    at.edit_bones['rearHip.R.005'].name = "rearTibiaJ2.R"
    at.edit_bones['rearHip.L.006'].name = "rearAnkle.L"
    at.edit_bones['rearHip.R.006'].name = "rearAnkle.R"
    at.edit_bones['rearHip.L.007'].name = "rearToe.L"
    at.edit_bones['rearHip.R.007'].name = "rearToe.R"
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
#|
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# BEGIN QUADRUPED SECTION
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class Quadruped():
    bl_idname = "object.quadruped"
    bl_label = "Quadruped"
    bl_description = "Quadruped"
    bl_options = {"REGISTER", "UNDO"}
    name = ""
    hidden = False    

class QuadrupedBuild_Button(bpy.types.Operator):
    bl_idname = "object.quadruped_build_btn"
    bl_label = "Build Quadruped"
    bl_description = "Build Quadruped"
    hidden = False
    def execute(self, context):
        buildQuadrupedSkeleton()
        bpy.context.scene.frame_set(0)
        bpy.ops.object.mode_set(mode='OBJECT')
        return{'FINISHED'}

class QuadrupedWalk_Button(bpy.types.Operator):
    bl_idname = "quadrupedwalk.button"
    bl_label = "Walk"
    bl_description = "Walk"
    hidden = False
    def execute(self, context):
        quadrupedFns.setWalk(self, context)
        bpy.ops.object.mode_set(mode='OBJECT')
        return{'FINISHED'}

def buildQuadrupedSkeleton():
    V_origin = [0.0, 0.0, 0.0]
    quadruped = Quadruped
    #addCharactersProperties()
    '''
    bpy.types.WindowManager.speed = bpy.props.FloatProperty(update=setHorizontalSpeed, name="Speed", default=0.0)
    bpy.types.WindowManager.direction = bpy.props.FloatProperty(update=setHorizontalSpeed, name="Direction", default=0.0)
    bpy.types.WindowManager.cycle = bpy.props.FloatProperty(update=quadrupedFns.setQuadrupedWalk, name="Cycle", default=1.0)
    # Pose character button
    bpy.types.WindowManager.swayLR = bpy.props.FloatProperty(update=quadrupedFns.setSwayRL, name="Sway RL", default=0.0)
    bpy.types.WindowManager.swayFB = bpy.props.FloatProperty(update=quadrupedFns.setSwayFB, name="Sway FB", default=0.0)
    bpy.types.WindowManager.bounce = bpy.props.FloatProperty(update=quadrupedFns.setBounce, name="Bounce", default=1.4)
    bpy.types.WindowManager.hipRotate = bpy.props.FloatProperty(update=quadrupedFns.setHip, name="Hip Rotate", default=1.0)
    bpy.types.WindowManager.hipUD = bpy.props.FloatProperty(update=quadrupedFns.setHip, name="HipUD", default=2.0)
    # De-activate Leg Movements Button
    # Activate Leg Movements Button
    bpy.types.WindowManager.neckFB = bpy.props.FloatProperty(update=quadrupedFns.setNeck, name="NeckUD", default=0.0)
    bpy.types.WindowManager.neckLR = bpy.props.FloatProperty(update=quadrupedFns.setNeck, name="neckLR", default=0.0)
    bpy.types.WindowManager.neckTurn = bpy.props.FloatProperty(update=quadrupedFns.setNeck, name="NeckTurn", default=0.0)
    bpy.types.WindowManager.headUD = bpy.props.FloatProperty(update=quadrupedFns.setHead, name="HeadUD", default=0.0)
    bpy.types.WindowManager.headLR = bpy.props.FloatProperty(update=quadrupedFns.setHead, name="headLR", default=0.0)
    bpy.types.WindowManager.headTurn = bpy.props.FloatProperty(update=quadrupedFns.setHead, name="HeadTurn", default=0.0)
    bpy.types.WindowManager.jawOC = bpy.props.FloatProperty(update=quadrupedFns.setJaw, name="JawOC", default=0.0)
    bpy.types.WindowManager.eyeLR = bpy.props.FloatProperty(update=quadrupedFns.setEye, name="eyeLR", default=0.0)
    bpy.types.WindowManager.eyeUD = bpy.props.FloatProperty(update=quadrupedFns.setEye, name="EyeUD", default=0.0)
    bpy.types.WindowManager.tailUD = bpy.props.FloatProperty(update=quadrupedFns.setTail, name="TailUD", default=0.0)
    bpy.types.WindowManager.tailLR = bpy.props.FloatProperty(update=quadrupedFns.setTail, name="tailLR", default=0.0)
    bpy.types.WindowManager.tailCurl = bpy.props.FloatProperty(update=quadrupedFns.setTail, name="TailCurl", default=0.0)
    bpy.types.WindowManager.earUD = bpy.props.FloatProperty(update=quadrupedFns.setEars, name="earUD", default=0.0)
    bpy.types.WindowManager.earLR = bpy.props.FloatProperty(update=quadrupedFns.setEars, name="earLR", default=0.0)
    bpy.types.WindowManager.earCurl = bpy.props.FloatProperty(update=quadrupedFns.setEars, name="earCurl", default=0.0)
    bpy.types.WindowManager.earAxial = bpy.props.FloatProperty(update=quadrupedFns.setEars, name="earAxial", default=0.0)
    bpy.types.WindowManager.earOUD = bpy.props.FloatProperty(update=quadrupedFns.setEarsOpposite, name="earOUD", default=0.0)
    bpy.types.WindowManager.earOLR = bpy.props.FloatProperty(update=quadrupedFns.setEarsOpposite, name="earOLR", default=0.0)
    bpy.types.WindowManager.earOCurl = bpy.props.FloatProperty(update=quadrupedFns.setEarsOpposite, name="earOCurl", default=0.0)  
    bpy.types.WindowManager.earOAxial = bpy.props.FloatProperty(update=quadrupedFns.setEarsOpposite, name="earOAxial", default=0.0)  
    # Front Leg Defaults Button 
    bpy.types.WindowManager.femurJ1RP = bpy.props.FloatProperty(update=quadrupedFns.setQuadrupedWalk, name="femurJ1RP", default=0.0)
    bpy.types.WindowManager.femurJ1RR = bpy.props.FloatProperty(update=quadrupedFns.setQuadrupedWalk, name="femurJ1RR", default=1.0)
    bpy.types.WindowManager.tibiaJ1RP = bpy.props.FloatProperty(update=quadrupedFns.setQuadrupedWalk, name="tibiaJ1RP", default=0.0)
    bpy.types.WindowManager.tibiaJ1RR = bpy.props.FloatProperty(update=quadrupedFns.setQuadrupedWalk, name="tibiaJ1RR", default=1.0)
    bpy.types.WindowManager.ankleRP = bpy.props.FloatProperty(update=quadrupedFns.setQuadrupedWalk, name="ankleRP", default=0.0)
    bpy.types.WindowManager.ankleRR = bpy.props.FloatProperty(update=quadrupedFns.setQuadrupedWalk, name="ankleRR", default=1.0)
    bpy.types.WindowManager.toesRP = bpy.props.FloatProperty(update=quadrupedFns.setQuadrupedWalk, name="toesRP", default=-0.0)
    bpy.types.WindowManager.toesRR = bpy.props.FloatProperty(update=quadrupedFns.setQuadrupedWalk, name="toesRR", default=1.0)
    # Advanced Rear Leg Controls %%%% RP = Rotate position  RR = Rotate range  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Rear Leg Defaults Button
    bpy.types.WindowManager.rearFemurJ1RP = bpy.props.FloatProperty(update=quadrupedFns.setQuadrupedWalk, name="Rear Leg RP", default=0.0)
    bpy.types.WindowManager.rearFemurJ1RR = bpy.props.FloatProperty(update=quadrupedFns.setQuadrupedWalk, name="Rear Leg RR", default=1.0)
    bpy.types.WindowManager.rearTibiaJ1RP = bpy.props.FloatProperty(update=quadrupedFns.setQuadrupedWalk, name="rearTibiaJ1RP", default=0.0)
    bpy.types.WindowManager.rearTibiaJ1RR = bpy.props.FloatProperty(update=quadrupedFns.setQuadrupedWalk, name="rearTibiaJ1RR", default=1.0)
    bpy.types.WindowManager.rearAnkleRP = bpy.props.FloatProperty(update=quadrupedFns.setQuadrupedWalk, name="rearAnkleRP", default=0.0)
    bpy.types.WindowManager.rearAnkleRR = bpy.props.FloatProperty(update=quadrupedFns.setQuadrupedWalk, name="rearAnkleRR", default=1.0)
    bpy.types.WindowManager.rearToesRP = bpy.props.FloatProperty(update=quadrupedFns.setQuadrupedWalk, name="rearToesRP", default=0.0)
    bpy.types.WindowManager.rearToesRR = bpy.props.FloatProperty(update=quadrupedFns.setQuadrupedWalk, name="rearToesRR", default=1.0)
    '''
    #
    #
    # Initiate building of bones
    n = getSceneObjectNumber()  # Each character name will be numbered sequentially.
    quadruped.name = setName('quadruped', n)  # biped, quadruped, bird, quadruped, spider, kangaroo   
    mod = math.fmod(n, 2)
    if(mod == 0):
        x = 1.1 * n - mod
    else:
        x = 1.1 * -n - mod
    y = -.4 * n; z = 1.04  # For Armature
    at = buildRootArmature(quadruped, quadruped.name, x, y, z) # Start character armature and bones
    # Build root bone
    Vhead = [0, 0, 0]
    Vtail = [0, 0, 0.3]  # End location of handle relative to armature origin - this effects coordinate system
    bone = setHandle(at, quadruped.name, Vhead, Vtail)
    # charClass.rig.show_in_front = True
    #bpy.data.objects[quadruped.name].show_x_ray = True
    #
    #
    buildQuadrupedBase(at)
    #
    #
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # BUILD HEAD AND NECK
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["qBackJ0"].select_tail=True
    V_qNeckJ1 = (0, .05, 0.1)
    boneMirror(at, V_qNeckJ1, False)
    V_qNeckJ2 = (0, .05, 0.1)
    boneMirror(at, V_qNeckJ2, False)
    V_qNeckJ3 = (0, .05, 0.14)
    boneMirror(at, V_qNeckJ3, False)
    V_qNeckJ4 = (0, .05, .1)
    boneMirror(at, V_qNeckJ4, False)
    V_qNeckJ5 = (0, .05, .1)
    boneMirror(at, V_qNeckJ5, False)
    V_qNeckJ6 = (0, .05, .1)
    boneMirror(at, V_qNeckJ6, False)
    at.edit_bones['qBackJ0.001'].name = "bNeckJ1"
    at.edit_bones['qBackJ0.002'].name = "bNeckJ2"
    at.edit_bones['qBackJ0.003'].name = "bNeckJ3"
    at.edit_bones['qBackJ0.004'].name = "bNeckJ4"
    at.edit_bones['qBackJ0.005'].name = "bNeckJ5"
    at.edit_bones['qBackJ0.006'].name = "bNeckJ6"
    #
    # Start head
    V_headBase = (0, 0, 0.09)
    boneMirror(at, V_headBase, False)
    V_eyeLevel = (0, 0, .04)
    boneMirror(at, V_eyeLevel, False)
    V_headTop = (0, -.05, 0)
    boneMirror(at, V_headTop, False)
    V_headFore = (0, .08, .09)
    boneMirror(at, V_headFore, False)
    at.edit_bones['bNeckJ6.001'].name = "headBase"
    at.edit_bones['bNeckJ6.002'].name = "eyeLevel"
    at.edit_bones['bNeckJ6.003'].name = "headTop"
    at.edit_bones['bNeckJ6.004'].name = "headFore"
    # ears
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["eyeLevel"].select_tail=True
    V_earRoot = (.05, -.06, .06)
    boneMirror(at, V_earRoot, True)
    V_earBase = (0, -.02, .02)
    boneMirror(at, V_earBase, True)
    V_earJ1 = (0, -.015, .015)
    boneMirror(at, V_earJ1, True)
    V_earJ2 = (0, -.015, .015)
    boneMirror(at, V_earJ2, True)
    V_earJ3 = (0, -.015, .015)
    boneMirror(at, V_earJ3, True)
    V_earJ4 = (0, -.015, .015)
    boneMirror(at, V_earJ4, True)
    V_earJ5 = (0, -.015, .015)
    boneMirror(at, V_earJ5, True)
    at.edit_bones['eyeLevel_R'].name = "earRoot.L"
    at.edit_bones['eyeLevel_L'].name = "earRoot.R"
    at.edit_bones['eyeLevel_R.001'].name = "earBase.L"
    at.edit_bones['eyeLevel_L.001'].name = "earBase.R"
    at.edit_bones['eyeLevel_R.002'].name = "earJ1.L"
    at.edit_bones['eyeLevel_L.002'].name = "earJ1.R"
    at.edit_bones['eyeLevel_R.003'].name = "earJ2.L"
    at.edit_bones['eyeLevel_L.003'].name = "earJ2.R"
    at.edit_bones['eyeLevel_R.004'].name = "earJ3.L"
    at.edit_bones['eyeLevel_L.004'].name = "earJ3.R"
    at.edit_bones['eyeLevel_R.005'].name = "earJ4.L"
    at.edit_bones['eyeLevel_L.005'].name = "earJ4.R"
    at.edit_bones['eyeLevel_R.006'].name = "earJ5.L"
    at.edit_bones['eyeLevel_L.006'].name = "earJ5.R"
    # jaw
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["bNeckJ6"].select_tail=True
    V_baseJaw = (0, .02, 0) 
    boneMirror(at, V_baseJaw, False)
    V_jaw = (0, .02, 0)
    boneMirror(at, V_jaw, False)
    V_jaw1 = (.03, .01, 0)
    boneMirror(at, V_jaw1, True)
    V_jaw2 = (-.02, .07, 0)
    boneMirror(at, V_jaw2, True)
    at.edit_bones['bNeckJ6.001'].name = "baseJaw"
    at.edit_bones['bNeckJ6.002'].name = "jaw"
    at.edit_bones['bNeckJ6.002_R'].name = "jaw1.L"
    at.edit_bones['bNeckJ6.002_L'].name = "jaw1.R"
    #
    # Eye Level
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["eyeLevel"].select_tail=True
    V_eyebase = (-.03, 0.1, 0)
    boneMirror(at, V_eyebase, True)
    V_eye = (0, 0.03, 0)
    boneMirror(at, V_eye, True)
    at.edit_bones['eyeLevel_L'].name = "eyeBase.L"
    at.edit_bones['eyeLevel_R'].name = "eyeBase.R"
    at.edit_bones['eyeLevel_L.001'].name = "eye.L"
    at.edit_bones['eyeLevel_R.001'].name = "eye.R"
    # nose
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["headBase"].select_tail=True
    V_noseBase = (0, .138, 0)
    boneMirror(at, V_noseBase, False)
    V_nose = (0, 0.02, -.02)
    boneMirror(at, V_nose, False)
    at.edit_bones['headBase.001'].name = "noseBase"
    at.edit_bones['headBase.002'].name = "nose"
    #
    quadruped.armature = at
    setEnvelopeWeights(at.name[:-3])
    #
    bpy.data.objects[quadruped.name].location[2] = 1.14  # z
    deselectAll()
    bpy.ops.object.mode_set(mode='OBJECT')
    ob = bpy.data.objects.get(quadruped.name)
    context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.context.object.rotation_euler[2] = -1.5708

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# END QUADRUPED SECTION
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|
#|
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# BEGIN BIRD SECTION
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class Bird():
    bl_idname = "object.bird"
    bl_label = "Build Bird"
    bl_description = "Build Bird"
    bl_options = {"REGISTER", "UNDO"}
    name = ""
    hidden = False   

class Bird_Button(bpy.types.Operator):
    bl_idname = "object.bird_build_btn"
    bl_label = "Build Bird"
    bl_description = "Build Bird"
    hidden = False
    def execute(self, context):
        buildBirdSkeleton()
        bpy.context.scene.frame_set(0)
        bpy.ops.object.mode_set(mode='OBJECT')
        return{'FINISHED'}

def buildBirdSkeleton():  # START BUILDING SKELETON %%%%%%%%%%%%%%%%%%%%%
    bird = Bird
    '''
    addCharactersProperties()
    bpy.types.WindowManager.speed = bpy.props.FloatProperty(update=setHorizontalSpeed, name="Bird Speed", default=0.0)
    bpy.types.WindowManager.direction = bpy.props.FloatProperty(update=setHorizontalSpeed, name="Direction", default=0.0)
    bpy.types.WindowManager.cycle = bpy.props.FloatProperty(update=birdFns.setWalk, name="Bird Cycle", default=6.0)
    bpy.types.WindowManager.swayLR = bpy.props.FloatProperty(update=birdFns.setSwayLR, name="Sway LR", default=1.0)
    bpy.types.WindowManager.swayFB = bpy.props.FloatProperty(update=birdFns.setSwayFB, name="Sway FB", default=0.0)
    bpy.types.WindowManager.bounce = bpy.props.FloatProperty(update=birdFns.setBounce, name="Bird Bounce", default=1.0)
    bpy.types.WindowManager.neckFB = bpy.props.FloatProperty(update=birdFns.setNeck, name="neckFB", default=6.0)
    bpy.types.WindowManager.legSpread = bpy.props.FloatProperty(update=birdFns.setLegSpread, name="Leg Spread", default=0.0)
    bpy.types.WindowManager.wingsSpeed = bpy.props.FloatProperty(update=activateWings, name="Bird Wing Speed", default=1.0)
    bpy.types.WindowManager.wingsRP = bpy.props.FloatProperty(update=activateWings, name="Wing Rot Position", default=0.0)
    bpy.types.WindowManager.wingsRR = bpy.props.FloatProperty(update=activateWings, name="Wing Rot Range", default=3.0, min=0.0)
    bpy.types.WindowManager.wingsFB = bpy.props.FloatProperty(update=setFwdBackwardPosition, name="Bird WingsFB", default=0.0)
    bpy.types.WindowManager.wingsAxial = bpy.props.FloatProperty(update=setAxialPosition, name="WingsAxial", default=0.0)
    bpy.types.WindowManager.wingsCurveFB = bpy.props.FloatProperty(update=activateWings, name="wingsCurveFB", default=0.0)
    bpy.types.WindowManager.wingsCurveUD = bpy.props.FloatProperty(update=activateWings, name="wingsCurveUD", default=0.0)
    bpy.types.WindowManager.wingsInnerFeathers = bpy.props.FloatProperty(update=setInnerFeathers, name="Rot Inner Feathers", default=0.0)
    bpy.types.WindowManager.wingsOuterFeathers = bpy.props.FloatProperty(update=setOuterFeathers, name="Rot Outer Feathers", default=0.0)
    bpy.types.WindowManager.tailUD = bpy.props.FloatProperty(update=birdFns.setTail, name="tailUD", default=0.0)
    bpy.types.WindowManager.tailRL = bpy.props.FloatProperty(update=birdFns.setTail, name="tailRL", default=0.0)
    bpy.types.WindowManager.tailSpread = bpy.props.FloatProperty(update=birdFns.setTail, name="tailSpread", default=0.0)
    bpy.types.WindowManager.claws = bpy.props.FloatProperty(update=birdFns.setClaws, name="claws", default=0.0)
    bpy.types.WindowManager.jawOC = bpy.props.FloatProperty(update=birdFns.setJaw, name="jawOC", default=0.0)
    bpy.types.WindowManager.eyeLR = bpy.props.FloatProperty(update=birdFns.setEye, name="eyeLR", default=0.0)
    bpy.types.WindowManager.eyeUD = bpy.props.FloatProperty(update=birdFns.setEye, name="eyeUD", default=0.0)
    bpy.types.WindowManager.crestFB = bpy.props.FloatProperty(update=birdFns.setCrest, name="crestFB", default=0.0)
    bpy.types.WindowManager.crestLR = bpy.props.FloatProperty(update=birdFns.setCrest, name="crestLR", default=0.0)
    # Advanced Controls %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    bpy.types.WindowManager.femurJ1RP = bpy.props.FloatProperty(update=birdFns.setWalk, name="femurJ1RP", default=0.0)
    bpy.types.WindowManager.femurJ1RR = bpy.props.FloatProperty(update=birdFns.setWalk, name="femurJ1RR", default=1.0)
    bpy.types.WindowManager.tibiaJ1RP = bpy.props.FloatProperty(update=birdFns.setWalk, name="tibiaJ1RP", default=0.0)
    bpy.types.WindowManager.tibiaJ1RR = bpy.props.FloatProperty(update=birdFns.setWalk, name="tibiaJ1RR", default=1.0)
    bpy.types.WindowManager.ankleRP = bpy.props.FloatProperty(update=birdFns.setWalk, name="ankleRP", default=0.0)
    bpy.types.WindowManager.ankleRR = bpy.props.FloatProperty(update=birdFns.setWalk, name="ankleRR", default=1.0)
    bpy.types.WindowManager.toesRP = bpy.props.FloatProperty(update=birdFns.setWalk, name="toesRP", default=0.0)
    bpy.types.WindowManager.toesRR = bpy.props.FloatProperty(update=birdFns.setWalk, name="toesRR", default=1.0)
    '''
    # 
    # Initiate building of bones
    n = getSceneObjectNumber()  # Each character name will be numbered sequentially.
    bird.name = setName('bird', n)  # biped, quadruped, bird, centaur, spider, kangaroo
    mod = math.fmod(n, 2)
    if(mod == 0):
        x = 1.1 * n - mod
    else:
        x = 1.1 * -n - mod
    y = -.4 * n; z = 1.39  # buildRootArmature(type, strCharName, x, y, z) type is the character class
    at = buildRootArmature(bird, bird.name, x, y, z) # Start character armature and bones
    Vhead = [0, 0, 0]
    Vtail = [0.0, -0.3, 0]  # End location of handle relative to armature origin - this effects coordinate system
    bone = setHandle(at, bird.name, Vhead, Vtail)
    # bpy.data.objects[bird.name].show_x_ray = True
    # charClass.rig.show_in_front = True
    #
    #
    VbackCenterTip = (0, -0.1, -.15)
    backCenter = createBone("backCenter", bone.head, VbackCenterTip)
    backCenter.parent = at.edit_bones[bird.name + '_bone']
    VbackL1 = (0, -0.15, -.15)
    boneMirror(at, VbackL1, False)
    VbackL2 = (0, -0.1, -.1)
    boneMirror(at, VbackL2, False)
    VbackL3 = (0, -0.1, -.04)
    boneMirror(at, VbackL3, False)
    VtailJ1 = (0, -0.1, -.04)
    boneMirror(at, VtailJ1, False)    
    VtailJ2 = (0, -.1, 0)
    boneMirror(at, VtailJ2, False)
    VtailJ3 = (0, -.06, 0)
    boneMirror(at, VtailJ3, False)
    at.edit_bones['backCenter.001'].name = "backL1"
    at.edit_bones['backCenter.002'].name = "backL2"
    at.edit_bones['backCenter.003'].name = "backL3"
    at.edit_bones['backCenter.004'].name = "tailJ1"
    at.edit_bones['backCenter.005'].name = "tailJ2"
    at.edit_bones['backCenter.006'].name = "tailJ3"
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["tailJ3"].select_tail=True
    Vfb1 = (0.022, .024, 0)
    boneMirror(at, Vfb1, True)
    Vfb2 = (0.022, .024, 0)
    boneMirror(at, Vfb2, True)
    Vfb3 = (0.022, .024, 0)
    boneMirror(at, Vfb3, True)
    Vfb4 = (0.022, .024, 0)
    boneMirror(at, Vfb4, True)
    at.edit_bones['tailJ3_R'].name = "fb1.L" # fb = feather base
    at.edit_bones['tailJ3_L'].name = "fb1.R"
    at.edit_bones['tailJ3_R.001'].name = "fb2.L"
    at.edit_bones['tailJ3_L.001'].name = "fb2.R"
    at.edit_bones['tailJ3_R.002'].name = "fb3.L"
    at.edit_bones['tailJ3_L.002'].name = "fb3.R"
    at.edit_bones['tailJ3_R.003'].name = "fb4.L"
    at.edit_bones['tailJ3_L.003'].name = "fb4.R"
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["tailJ3"].select_tail=True
    Vfa1 = (0, -.08, 0)  
    boneMirror(at, Vfa1, False)  # fa = Feather attach
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["fb1.R"].select_tail=True
    Vfa2 = (0, -.08, 0)  
    boneMirror(at, Vfa2, True)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["fb2.R"].select_tail=True
    Vfa3 = (0, -.08, 0)  
    boneMirror(at, Vfa3, True)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["fb3.R"].select_tail=True
    Vfa3 = (0, -.08, 0)  
    boneMirror(at, Vfa3, True)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["fb4.R"].select_tail=True
    Vfa4 = (0, -.08, 0)  
    boneMirror(at, Vfa4, True)
    at.edit_bones['tailJ3.001'].name = "faMiddle"
    at.edit_bones['fb1.L.001'].name = "fa1.L"
    at.edit_bones['fb1.R.001'].name = "fa1.R"
    at.edit_bones['fb2.L.001'].name = "fa2.L"
    at.edit_bones['fb2.R.001'].name = "fa2.R"
    at.edit_bones['fb3.L.001'].name = "fa3.L"
    at.edit_bones['fb3.R.001'].name = "fa3.R"
    at.edit_bones['fb4.L.001'].name = "fa4.L"
    at.edit_bones['fb4.R.001'].name = "fa4.R"
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Start Top part of spine  
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    bpy.ops.armature.select_all(action='DESELECT')
    V_origin = (0, 0, 0)
    Vneck01 = (0, .12, -.02)
    b = createBone("neck01", V_origin, Vneck01)
    b.parent = at.edit_bones['backCenter']
    Vneck02 = (0, .04, 0.04)
    boneMirror(at, Vneck02, False)
    Vneck03 = (0, .03, .04)
    boneMirror(at, Vneck03, False)
    Vneck04 = (0, .02, .04)
    boneMirror(at, Vneck04, False)
    Vneck05 = (0, 0, .04)
    boneMirror(at, Vneck05, False)
    Vneck06 = (0, 0, .04)
    boneMirror(at, Vneck06, False)
    VheadBase = (0, -.03, .05)
    boneMirror(at, VheadBase, False)
    at.edit_bones['neck01.001'].name = "neck02"
    at.edit_bones['neck01.002'].name = "neck03"
    at.edit_bones['neck01.003'].name = "neck04"
    at.edit_bones['neck01.004'].name = "neck05"
    at.edit_bones['neck01.005'].name = "neck06"
    at.edit_bones['neck01.006'].name = "headBase"
    #
    VheadTop = (0, 0.17, .03)
    boneMirror(at, VheadTop, False)
    Vcrest = (0, -.1, .08)
    boneMirror(at, Vcrest, False)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones['headBase.001'].name = "headTop"
    at.edit_bones['headBase.002'].name = "crest"
    #
    at.edit_bones["neck06"].select_tail=True
    Vjaw1 = (0, .08, -.03)
    boneMirror(at, Vjaw1, False)
    Vjaw2 = (0, .03, -.05)
    boneMirror(at, Vjaw2, False)
    Vjaw3 = (0, 0.109, .053)
    boneMirror(at, Vjaw3, False)
    Vjaw4 = (0, 0.13, -.028)
    boneMirror(at, Vjaw4, False)
    Vjaw4 = (0, 0.12, -.026)
    boneMirror(at, Vjaw4, False)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones['neck06.001'].name = "jaw1"
    at.edit_bones['neck06.002'].name = "jaw2"
    at.edit_bones['neck06.003'].name = "jaw3"
    at.edit_bones['neck06.004'].name = "jaw4"
    at.edit_bones['neck06.005'].name = "jaw5"
    #
    at.edit_bones["jaw1"].select_tail=True
    VbeakBase = (0, 0.08, .07)
    boneMirror(at, VbeakBase, False)
    Vbeak1 = (0, 0.16, 0)
    boneMirror(at, Vbeak1, False)
    Vbeak2 = (0, 0.18, -.05)
    boneMirror(at, Vbeak2, False)
    at.edit_bones['jaw1.001'].name = "beak1"
    at.edit_bones['jaw1.002'].name = "beak2"
    at.edit_bones['jaw1.003'].name = "beak3"
    #
    at.edit_bones['headBase'].parent = at.edit_bones['neck06']
    at.edit_bones['jaw1'].parent = at.edit_bones['neck06']
    bpy.ops.armature.select_all(action='DESELECT')
    #
    at.edit_bones["headBase"].select_tail=True
    VeyeBase = (0.06, .104, -.02)
    boneMirror(at, VeyeBase, True)
    Veye = (0, .02, 0)
    boneMirror(at, Veye, True)
    at.edit_bones['headBase_L'].name = "baseEye.L"
    at.edit_bones['headBase_R'].name = "baseEye.R"
    at.edit_bones['headBase_L.001'].name = "eye.L"
    at.edit_bones['headBase_R.001'].name = "eye.R"
    bpy.ops.armature.select_all(action='DESELECT')
    #
    at.edit_bones["neck01"].select_tail=True
    Vffix1 = (0, 0.06, -.1)
    boneMirror(at, Vffix1, False)
    Vffix2 = (0, -.05, -.1)
    boneMirror(at, Vffix2, False)
    Vffix3 = (0, -.07, -.1)
    boneMirror(at, Vffix3, False)
    Vffix4 = (0, -.08, -.1)
    boneMirror(at, Vffix4, False)
    Vffix5 = (0, -.09, -.1)
    boneMirror(at, Vffix5, False)
    at.edit_bones['neck01.001'].name = "ffix1"
    at.edit_bones['neck01.002'].name = "ffix2"
    at.edit_bones['neck01.003'].name = "ffix3"
    at.edit_bones['neck01.004'].name = "ffix4"
    at.edit_bones['neck01.005'].name = "ffix5"
    bpy.ops.armature.select_all(action='DESELECT')
    #
    # xxx1
    createWings(at)
    #
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["backL2"].select_tail=True
    VhipBase = (0, 0.06, -0.1)
    boneMirror(at, VhipBase, False)
    at.edit_bones['backL2.001'].name = "hipBase"
    Vhip = (.18, 0, 0)
    boneMirror(at, Vhip, True)
    VhipBone = (0, .01, -0.12)
    boneMirror(at, VhipBone, True)
    VfemurJ1 = (0, -0.02, -0.12)
    boneMirror(at, VfemurJ1, True)
    VfemurJ2 = (0, -0.02, -0.12)
    boneMirror(at, VfemurJ2, True)
    VfemurJ3 = (0, 0, -0.12)
    boneMirror(at, VfemurJ3, True)
    VlegJ5 = (0, .01, -.1)
    boneMirror(at, VlegJ5, True)
    VtibiaJ2 = (0, .01, -.1)
    boneMirror(at, VtibiaJ2, True)
    VtibiaJ3 = (0, .01, -.11)
    boneMirror(at, VtibiaJ3, True)
    Vankle = (0, .01, -.05)
    boneMirror(at, Vankle, True)
    VrearToeJ1 = (-.016, -0.07, .01)
    boneMirror(at, VrearToeJ1, True)
    VrearToeJ2 = (-.015, -0.07, 0)
    boneMirror(at, VrearToeJ2, True)
    VrearToeJ3 = (-.015, -0.07, 0)
    boneMirror(at, VrearToeJ3, True)
    VrearToeJ4 = (-.015, -0.07, 0)
    boneMirror(at, VrearToeJ4, True)
    #
    at.edit_bones['hipBase_R'].name = "hip.L"
    at.edit_bones['hipBase_L'].name = "hip.R"
    at.edit_bones['hipBase_R.001'].name = "hipBone.L"
    at.edit_bones['hipBase_L.001'].name = "hipBone.R"
    at.edit_bones['hipBase_R.002'].name = "femurJ1.L"
    at.edit_bones['hipBase_L.002'].name = "femurJ1.R"    
    at.edit_bones['hipBase_R.003'].name = "femurJ2.L"
    at.edit_bones['hipBase_L.003'].name = "femurJ2.R"
    at.edit_bones['hipBase_R.004'].name = "femurJ3.L"
    at.edit_bones['hipBase_L.004'].name = "femurJ3.R"
    at.edit_bones['hipBase_R.005'].name = "tibiaJ1.L"
    at.edit_bones['hipBase_L.005'].name = "tibiaJ1.R"
    at.edit_bones['hipBase_R.006'].name = "tibiaJ2.L"
    at.edit_bones['hipBase_L.006'].name = "tibiaJ2.R"
    at.edit_bones['hipBase_R.007'].name = "tibiaJ3.L"
    at.edit_bones['hipBase_L.007'].name = "tibiaJ3.R"
    at.edit_bones['hipBase_R.008'].name = "ankle.L"
    at.edit_bones['hipBase_L.008'].name = "ankle.R"
    at.edit_bones['hipBase_R.009'].name = "rearToeJ1.L"
    at.edit_bones['hipBase_L.009'].name = "rearToeJ1.R"
    at.edit_bones['hipBase_R.010'].name = "rearToeJ2.L"
    at.edit_bones['hipBase_L.010'].name = "rearToeJ2.R"
    at.edit_bones['hipBase_R.011'].name = "rearToeJ3.L"
    at.edit_bones['hipBase_L.011'].name = "rearToeJ3.R"
    at.edit_bones['hipBase_R.012'].name = "rearToeJ4.L"
    at.edit_bones['hipBase_L.012'].name = "rearToeJ4.R"
    bpy.ops.armature.select_all(action='DESELECT')
    # Center Claw
    at.edit_bones["ankle.L"].select_tail=True
    VcenterToe = (0, .07, 0)
    boneMirror(at, VcenterToe, True)
    boneMirror(at, VcenterToe, True)
    boneMirror(at, VcenterToe, True)
    boneMirror(at, VcenterToe, True)
    at.edit_bones['ankle.L.001'].name = "centerToeJ1.L"
    at.edit_bones['ankle.R.001'].name = "centerToeJ1.R"
    at.edit_bones['ankle.L.002'].name = "centerToeJ2.L"
    at.edit_bones['ankle.R.002'].name = "centerToeJ2.R"
    at.edit_bones['ankle.L.003'].name = "centerToeJ3.L"
    at.edit_bones['ankle.R.003'].name = "centerToeJ3.R"
    at.edit_bones['ankle.L.004'].name = "centerToeJ4.L"
    at.edit_bones['ankle.R.004'].name = "centerToeJ4.R"
    bpy.ops.armature.select_all(action='DESELECT')
    #
    at.edit_bones["ankle.L"].select_tail=False
    bpy.ops.armature.select_all(action='DESELECT')
    # Left Claw
    at.edit_bones["ankle.L"].select_tail=True
    VouterToe = (-.0358, .066, 0)
    boneMirror(at, VouterToe, True)
    boneMirror(at, VouterToe, True)
    boneMirror(at, VouterToe, True)
    boneMirror(at, VouterToe, True)
    at.edit_bones['ankle.L.001'].name = "outerToeJ1.L"
    at.edit_bones['ankle.R.001'].name = "outerToeJ1.R"
    at.edit_bones['ankle.L.002'].name = "outerToeJ2.L"
    at.edit_bones['ankle.R.002'].name = "outerToeJ2.R"
    at.edit_bones['ankle.L.003'].name = "outerToeJ3.L"
    at.edit_bones['ankle.R.003'].name = "outerToeJ3.R"
    at.edit_bones['ankle.L.004'].name = "outerToeJ4.L"
    at.edit_bones['ankle.R.004'].name = "outerToeJ4.R"
    bpy.ops.armature.select_all(action='DESELECT')
    # Right Claw
    at.edit_bones["ankle.L"].select_tail=True
    VinnerToe = (.034, .065, 0)
    boneMirror(at, VinnerToe, True)
    boneMirror(at, VinnerToe, True)
    boneMirror(at, VinnerToe, True)
    boneMirror(at, VinnerToe, True)
    at.edit_bones['ankle.L.001'].name = "innerToeJ1.L"
    at.edit_bones['ankle.R.001'].name = "innerToeJ1.R"
    at.edit_bones['ankle.L.002'].name = "innerToeJ2.L"
    at.edit_bones['ankle.R.002'].name = "innerToeJ2.R"
    at.edit_bones['ankle.L.003'].name = "innerToeJ3.L"
    at.edit_bones['ankle.R.003'].name = "innerToeJ3.R"
    at.edit_bones['ankle.L.004'].name = "innerToeJ4.L"
    at.edit_bones['ankle.R.004'].name = "innerToeJ4.R"
    #
    #setEnvelopeWeights()
    deselectAll()
    ob = bpy.data.objects.get(bird.name)
    #bpy.context.scene.objects.active = ob
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)

    bird.armature = at
    setEnvelopeWeights(bird.name)
    bpy.data.objects[bird.name].location[2] = z  # z height
    bpy.ops.object.mode_set(mode='OBJECT')
    ob = bpy.data.objects.get(bird.name)
    context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.context.object.rotation_euler[2] = -1.5708

def createWings(at):
    bird = Bird
    name = at.name[:-3]
    if(name.startswith("rgbird")):
        root = "backCenter"
    if(name.startswith("rgadWings")):
        root = name + "_bone"
    # BuildWings
    at.edit_bones[root].select_head=True
    Vbase = (-.12, 0, 0)
    boneMirror(at, Vbase, True)
    Vwings_J1 = (-.06, 0, 0)
    boneMirror(at, Vwings_J1, True)
    Vwings_J2 = (-.03, 0, 0)
    boneMirror(at, Vwings_J2, True)
    Vwings_J3 = (-.03, 0, 0)
    boneMirror(at, Vwings_J3, True)
    Vwings_J4 = (-.03, 0, 0)
    boneMirror(at, Vwings_J4, True)
    Vwings_J5 = (-.03, 0, 0)
    boneMirror(at, Vwings_J5, True)
    Vwings_J6 = (-.03, 0, 0)
    boneMirror(at, Vwings_J6, True)
    Vwings_J7 = (-.03, 0, 0)
    boneMirror(at, Vwings_J7, True)
    Vwings_J8 = (-.03, 0, 0)
    boneMirror(at, Vwings_J8, True)
    Vwings_J9 = (-.03, 0, 0)
    boneMirror(at, Vwings_J9, True)
    Vwings_J10 = (-.03, 0, 0)
    boneMirror(at, Vwings_J10, True)
    Vwings_J11 = (-.015, 0, 0)
    boneMirror(at, Vwings_J11, True)
    Vwings_J12 = (-.015, 0, 0)
    boneMirror(at, Vwings_J12, True)
    Vwings_J13 = (-.015, 0, 0)
    boneMirror(at, Vwings_J13, True)
    Vwings_J14 = (-.015, 0, 0)
    boneMirror(at, Vwings_J14, True)
    Vwings_J15 = (-.015, 0, 0)
    boneMirror(at, Vwings_J15, True)
    Vwings_J16 = (-0.06, 0, 0)
    boneMirror(at, Vwings_J16, True)
    # 
    prefix = ""
    if(name.startswith("rgbird")):  # Start designation with "wings" for bird
        prefix = "rgwings"
    if(name.startswith("rgadWings")):  # Start designation with "adWings" for adWings
        prefix = "rgadWings"
    at.edit_bones[root + '_L'].name = prefix + "Base1.L"
    at.edit_bones[root + '_R'].name = prefix + "Base1.R"
    at.edit_bones[root + '_L.001'].name = prefix + "_J1.L"
    at.edit_bones[root + '_R.001'].name = prefix + "_J1.R"
    at.edit_bones[root + '_L.002'].name = prefix + "_J2.L"
    at.edit_bones[root + '_R.002'].name = prefix + "_J2.R"
    at.edit_bones[root + '_L.003'].name = prefix + "_J3.L"
    at.edit_bones[root + '_R.003'].name = prefix + "_J3.R"
    at.edit_bones[root + '_L.004'].name = prefix + "_J4.L"
    at.edit_bones[root + '_R.004'].name = prefix + "_J4.R"
    at.edit_bones[root + '_L.005'].name = prefix + "_J5.L"
    at.edit_bones[root + '_R.005'].name = prefix + "_J5.R"
    at.edit_bones[root + '_L.006'].name = prefix + "_J6.L"
    at.edit_bones[root + '_R.006'].name = prefix + "_J6.R"
    at.edit_bones[root + '_L.007'].name = prefix + "_J7.L"
    at.edit_bones[root + '_R.007'].name = prefix + "_J7.R"
    at.edit_bones[root + '_L.008'].name = prefix + "_J8.L"
    at.edit_bones[root + '_R.008'].name = prefix + "_J8.R"
    at.edit_bones[root + '_L.009'].name = prefix + "_J9.L"
    at.edit_bones[root + '_R.009'].name = prefix + "_J9.R"
    at.edit_bones[root + '_L.010'].name = prefix + "_J10.L"
    at.edit_bones[root + '_R.010'].name = prefix + "_J10.R"
    at.edit_bones[root + '_L.011'].name = prefix + "_J11.L"
    at.edit_bones[root + '_R.011'].name = prefix + "_J11.R"
    at.edit_bones[root + '_L.012'].name = prefix + "_J12.L"
    at.edit_bones[root + '_R.012'].name = prefix + "_J12.R"
    at.edit_bones[root + '_L.013'].name = prefix + "_J13.L"
    at.edit_bones[root + '_R.013'].name = prefix + "_J13.R"
    at.edit_bones[root + '_L.014'].name = prefix + "_J14.L"
    at.edit_bones[root + '_R.014'].name = prefix + "_J14.R"
    at.edit_bones[root + '_L.015'].name = prefix + "_J15.L"
    at.edit_bones[root + '_R.015'].name = prefix + "_J15.R"
    at.edit_bones[root + '_L.016'].name = prefix + "_J16.L"
    at.edit_bones[root + '_R.016'].name = prefix + "_J16.R"
    bpy.ops.armature.select_all(action='DESELECT')
    #
    at.edit_bones[prefix + "_J1.L"].select_tail=True
    n = 0
    offset = .0046
    Vfeathers = (0, -.04, 0) # All of these  are the  same size
    boneMirror(at, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones[prefix + "_J2.L"].select_tail=True
    Vfeathers = (n, -.04, 0)
    boneMirror(at, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones[prefix + "_J3.L"].select_tail=True
    n = n - offset
    Vfeathers = (n, -.04, 0)
    boneMirror(at, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones[prefix + "_J4.L"].select_tail=True
    n = n - offset
    Vfeathers = (n, -.04, 0)
    boneMirror(at, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones[prefix + "_J5.L"].select_tail=True
    n = n - offset
    Vfeathers = (n, -.04, 0)
    boneMirror(at, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones[prefix + "_J6.L"].select_tail=True
    n = n - offset
    Vfeathers = (n, -.04, 0)
    boneMirror(at, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones[prefix + "_J7.L"].select_tail=True
    n = n - offset
    Vfeathers = (n, -.04, 0)
    boneMirror(at, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones[prefix + "_J8.L"].select_tail=True
    n = n - offset
    Vfeathers = (n, -.04, 0)
    boneMirror(at, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones[prefix + "_J9.L"].select_tail=True
    n = n - offset
    Vfeathers = (n, -.04, 0)
    boneMirror(at, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones[prefix + "_J10.L"].select_tail=True
    n = n - offset
    Vfeathers = (n, -.034, 0)
    boneMirror(at, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones[prefix + "_J11.L"].select_tail=True
    offset = .002
    n = n - offset
    Vfeathers = (n, -.026, 0)
    boneMirror(at, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones[prefix + "_J12.L"].select_tail=True
    n = n - offset
    Vfeathers = (n, -.024, 0)
    boneMirror(at, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones[prefix + "_J13.L"].select_tail=True
    n = n - offset
    Vfeathers = (n, -.018, 0)
    boneMirror(at, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones[prefix + "_J14.L"].select_tail=True
    Vfeathers = (n, -.012, 0)
    boneMirror(at, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones[prefix + "_J15.L"].select_tail=True
    Vfeathers = (n, -.009, 0)
    boneMirror(at, Vfeathers, True)
    at.edit_bones[prefix + '_J1.L.001'].name = prefix + "Feathers1.L"
    at.edit_bones[prefix + '_J1.R.001'].name = prefix + "Feathers1.R"
    at.edit_bones[prefix + '_J2.L.001'].name = prefix + "Feathers2.L"
    at.edit_bones[prefix + '_J2.R.001'].name = prefix + "Feathers2.R"
    at.edit_bones[prefix + '_J3.L.001'].name = prefix + "Feathers3.L"
    at.edit_bones[prefix + '_J3.R.001'].name = prefix + "Feathers3.R"
    at.edit_bones[prefix + '_J4.L.001'].name = prefix + "Feathers4.L"
    at.edit_bones[prefix + '_J4.R.001'].name = prefix + "Feathers4.R"
    at.edit_bones[prefix + '_J5.L.001'].name = prefix + "Feathers5.L"
    at.edit_bones[prefix + '_J5.R.001'].name = prefix + "Feathers5.R"
    at.edit_bones[prefix + '_J6.L.001'].name = prefix + "Feathers6.L"
    at.edit_bones[prefix + '_J6.R.001'].name = prefix + "Feathers6.R"
    at.edit_bones[prefix + '_J7.L.001'].name = prefix + "Feathers7.L"
    at.edit_bones[prefix + '_J7.R.001'].name = prefix + "Feathers7.R"
    at.edit_bones[prefix + '_J8.L.001'].name = prefix + "Feathers8.L"
    at.edit_bones[prefix + '_J8.R.001'].name = prefix + "Feathers8.R"
    at.edit_bones[prefix + '_J9.L.001'].name = prefix + "Feathers9.L"
    at.edit_bones[prefix + '_J9.R.001'].name = prefix + "Feathers9.R"
    at.edit_bones[prefix + '_J10.L.001'].name = prefix + "Feathers10.L"
    at.edit_bones[prefix + '_J10.R.001'].name = prefix + "Feathers10.R"
    at.edit_bones[prefix + '_J11.L.001'].name = prefix + "Feathers11.L"
    at.edit_bones[prefix + '_J11.R.001'].name = prefix + "Feathers11.R"
    at.edit_bones[prefix + '_J12.L.001'].name = prefix + "Feathers12.L"
    at.edit_bones[prefix + '_J12.R.001'].name = prefix + "Feathers12.R"
    at.edit_bones[prefix + '_J13.L.001'].name = prefix + "Feathers13.L"
    at.edit_bones[prefix + '_J13.R.001'].name = prefix + "Feathers13.R"
    at.edit_bones[prefix + '_J14.L.001'].name = prefix + "Feathers14.L"
    at.edit_bones[prefix + '_J14.R.001'].name = prefix + "Feathers14.R"
    at.edit_bones[prefix + '_J15.L.001'].name = prefix + "Feathers15.L"
    at.edit_bones[prefix + '_J15.R.001'].name = prefix + "Feathers15.R"
    bpy.ops.armature.select_all(action='DESELECT')
    #
    for b in bpy.data.objects[name].pose.bones:
        b.rotation_mode = 'XYZ'
    for b in bpy.context.object.data.edit_bones:
        # Set weights for adWings
        if(b.name == name + '_bone'):
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
#|
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# BEGIN SPIDER SECTION
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class Spider():
    bl_idname = "object.spider"
    bl_label = "Build Spider"
    bl_description = "Build Spider"
    bl_options = {"REGISTER", "UNDO"}
    name = ""

class Spider_Button(bpy.types.Operator):
    bl_idname = "object.spider_build_btn"
    bl_label = "Build Spider"
    bl_description = "Build Spider"
    hidden = False
    def execute(self, context):
        buildSpiderSkeleton()
        bpy.context.scene.frame_set(0)
        bpy.ops.object.mode_set(mode='OBJECT')
        return{'FINISHED'}

def buildSpiderSkeleton():  # START BUILDING SKELETON %%%%%%%%%%%%%%%%%%%%%
    spider = Spider
    #addCharactersProperties()
    '''
    bpy.types.WindowManager.speed = bpy.props.FloatProperty(update=spiderFns.setSpiderWalk, name="Speed", default=0.0)
    bpy.types.WindowManager.direction = bpy.props.FloatProperty(update=spiderFns.setSpiderWalk, name="Direction", default=0.0)
    bpy.types.WindowManager.cycle = bpy.props.FloatProperty(update=spiderFns.setSpiderWalk, name="Cycle", default=6.0)
    '''
    n = getSceneObjectNumber()  # Each character name will be numbered sequentially.
    strName = setName('spider', n)  # biped, quadruped, bird, centaur, spider, kangaroo
    mod = math.fmod(n, 2)
    if(mod == 0):
        x = 1.1 * n - mod
    else:
        x = 1.1 * -n - mod
    y = -.4 * n; z = .1  # buildRootArmature(type, strCharName, x, y, z) type is the character class
    at = buildRootArmature(spider, strName, x, y, z) # Start character armature and bones
    Vhead = [0, 0, 0]
    Vtail = [0, 0.0, 0.6]  # End location of handle relative to armature origin - this effects coordinate system
    bone = setHandle(at, strName, Vhead, Vtail)
    # bpy.data.objects[strName].show_x_ray = True
    Vradius1 = (0, .254, 0)
    radius1 = createBone("radius1", bone.head, Vradius1)
    radius1.parent = at.edit_bones[strName + '_bone']
    Vframe = (.2, 0, 0)
    boneMirror(at, Vframe, mirror=True)
    Vframe = (0, 0, .062)
    boneMirror(at, Vframe, mirror=True)
    Vframe = (.2, 0, .082)
    boneMirror(at, Vframe, mirror=True)
    Vframe = (.4, 0, -.2)
    boneMirror(at, Vframe, mirror=True)
    Vframe = (.1, 0, 0)
    boneMirror(at, Vframe, mirror=True)
    at.edit_bones['radius1_L'].name = "frame2F"  # F for front
    at.edit_bones['radius1_R'].name = "frame1F"
    at.edit_bones['radius1_L.001'].name = "sideToSide2F"
    at.edit_bones['radius1_R.001'].name = "sideToSide1F"
    at.edit_bones['radius1_L.002'].name = "leg2J1F.R"
    at.edit_bones['radius1_R.002'].name = "leg1J1F.L"
    at.edit_bones['radius1_L.003'].name = "leg2J2F.R"
    at.edit_bones['radius1_R.003'].name = "leg1J2F.L"
    at.edit_bones['radius1_L.004'].name = "leg2J3F.R"
    at.edit_bones['radius1_R.004'].name = "leg1J3F.L"
    bpy.ops.armature.select_all(action='DESELECT')
    #
    Vradius3 = (0, -.25, 0)
    radius3 = createBone("radius3", bone.head, Vradius3)
    radius3.parent = at.edit_bones[strName + '_bone']
    Vframe = (.22, 0, 0)
    boneMirror(at, Vframe, mirror=True)
    Vframe = (0, 0, .062)
    boneMirror(at, Vframe, mirror=True)
    Vframe = (.2, 0, .082)
    boneMirror(at, Vframe, mirror=True)
    Vframe = (.4, 0, -.2)
    boneMirror(at, Vframe, mirror=True)
    Vframe = (.1, 0, 0)
    boneMirror(at, Vframe, mirror=True)
    at.edit_bones['radius3_L'].name = "frame5.R"
    at.edit_bones['radius3_R'].name = "frame6.L"
    at.edit_bones['radius3_L.001'].name = "sideToSide5.R"
    at.edit_bones['radius3_R.001'].name = "sideToSide6.L"
    at.edit_bones['radius3_L.002'].name = "leg5J1.R"
    at.edit_bones['radius3_R.002'].name = "leg6J1.L"
    at.edit_bones['radius3_L.003'].name = "leg5J2.R"
    at.edit_bones['radius3_R.003'].name = "leg6J2.L"
    at.edit_bones['radius3_L.004'].name = "leg5J3.R"
    at.edit_bones['radius3_R.004'].name = "leg6J3.L"
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones[strName + '_bone'].select_tail=True
    bpy.ops.object.mode_set(mode='POSE')
    #bpy.data.objects[strName].pose.bones[strName + '_bone'].rotation_euler[1] = 1.5708
    #rotate(strName, strName + '_bone', 1.5708, 1)
    #x = y = 2.0 * n;
    VOrigin = (0, 0, .02)
    Vradius2 = (.254, 0, 0)
    radius2 = createBone("radius2", VOrigin, Vradius2)
    radius2.parent = at.edit_bones[strName + '_bone']
    Vframe = (0, .082, 0)
    boneMirror(at, Vframe, mirror=False)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["radius2"].select_tail=True
    Vframe = (0, -.082, 0)
    boneMirror(at, Vframe, mirror=False)
    Vframe = (0, 0, .062)
    boneMirror(at, Vframe, mirror=False)
    Vframe = (.2, 0, .082)
    boneMirror(at, Vframe, mirror=False)
    Vframe = (.4, 0, -.2)
    boneMirror(at, Vframe, mirror=False)
    Vframe = (.1, 0, 0)
    boneMirror(at, Vframe, mirror=False)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["radius2.001"].select_tail=True
    Vframe = (0, 0, .062)
    boneMirror(at, Vframe, mirror=False)
    Vframe = (.2, 0, .082)
    boneMirror(at, Vframe, mirror=False)
    Vframe = (.4, 0, -.2)
    boneMirror(at, Vframe, mirror=False)
    Vframe = (.1, 0, 0)
    boneMirror(at, Vframe, mirror=False)
    at.edit_bones['radius2.001'].name = "frame3R.F"  # Right Front
    at.edit_bones['radius2.002'].name = "frame4R.B"  # Right Back
    at.edit_bones['radius2.003'].name = "sideToSide4R.B"
    at.edit_bones['radius2.004'].name = "leg4J1R.B"
    at.edit_bones['radius2.005'].name = "leg4J2R.B"
    at.edit_bones['radius2.006'].name = "leg4J3R.B"
    at.edit_bones['radius2.007'].name = "sideToSide3R.F"
    at.edit_bones['radius2.008'].name = "leg3J1R.F"
    at.edit_bones['radius2.009'].name = "leg3J2R.F"
    at.edit_bones['radius2.010'].name = "leg3J3R.F"
    #
    bpy.ops.armature.select_all(action='DESELECT')
    Vradius4 = (-.254, 0, 0)
    radius4 = createBone("radius4", VOrigin, Vradius4)
    radius4.parent = at.edit_bones[strName + '_bone']
    Vframe = (0, .082, 0)
    boneMirror(at, Vframe, mirror=False)
    Vframe = (0, 0, .062)
    boneMirror(at, Vframe, mirror=False)
    Vframe = (-.2, 0, .082)
    boneMirror(at, Vframe, mirror=False)
    Vframe = (-.4, 0, -.2)
    boneMirror(at, Vframe, mirror=False)
    Vframe = (-.1, 0, 0)
    boneMirror(at, Vframe, mirror=False)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["radius4"].select_tail=True
    Vframe = (0, -.082, 0)
    boneMirror(at, Vframe, mirror=False) # frame
    Vframe = (0, 0, .062)
    boneMirror(at, Vframe, mirror=False) # sideToSide
    Vframe = (-.2, 0, .082)
    boneMirror(at, Vframe, mirror=False)
    Vframe = (-.4, 0, -.2)
    boneMirror(at, Vframe, mirror=False)
    Vframe = (-.1, 0, 0)
    boneMirror(at, Vframe, mirror=False)
    at.edit_bones['radius4.001'].name = "frame8L.F"  # Left Front
    at.edit_bones['radius4.002'].name = "sideToSide8L.F"  
    at.edit_bones['radius4.003'].name = "leg8J1L.F"
    at.edit_bones['radius4.004'].name = "leg8J2L.F"
    at.edit_bones['radius4.005'].name = "leg8J3L.F"
    at.edit_bones['radius4.006'].name = "frame7L.B"   # Left Back
    at.edit_bones['radius4.007'].name = "sideToSide7L.B"
    at.edit_bones['radius4.008'].name = "leg7J1L.B"
    at.edit_bones['radius4.009'].name = "leg7J2L.B"
    at.edit_bones['radius4.010'].name = "leg7J3L.B"
    bpy.ops.armature.select_all(action='DESELECT')
    #
    # ADD TAIL
    at.edit_bones["radius3"].select_tail=True
    Vframe = (0, -.12, .08)
    boneMirror(at, Vframe, mirror=False)
    Vframe = (0, -.26, 0)
    boneMirror(at, Vframe, mirror=False)
    Vframe = (0, -.26, 0)
    boneMirror(at, Vframe, mirror=False)
    Vframe = (0, -.26, 0)
    boneMirror(at, Vframe, mirror=False)
    at.edit_bones['radius3.001'].name = "tail1"
    at.edit_bones['radius3.002'].name = "tail2"
    at.edit_bones['radius3.003'].name = "tail3"
    at.edit_bones['radius3.004'].name = "tail4"
    #
    for b in bpy.data.objects[strName].pose.bones:
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
    ob = bpy.data.objects.get(strName)
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.object.mode_set(mode='OBJECT')

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# END SPIDER SECTION
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|
#|
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# BEGIN WINGS SECTION
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class Wings():
    bl_idname = "object.wings"
    bl_label = "Build Wings"
    bl_description = "Build Wings"
    name = ""

class Wings_Button(bpy.types.Operator):  
    bl_idname = "object.wings_build_btn"
    bl_label = "Build Wings"
    bl_description = "Build Wings"
    hidden = False
    def execute(self, context):
        buildWings()
        bpy.context.scene.frame_set(0)
        bpy.ops.object.mode_set(mode='OBJECT')
        return{'FINISHED'}

def buildWings():  # START BUILDING WINGS %%%%%%%%%%%%%%%%%%%%%
    wings = Wings
    #addCharactersProperties()
    '''
    bpy.types.WindowManager.adWingsSpeed = bpy.props.FloatProperty(update=activateWings, name="Solo Wing Speed", default=1.0)
    bpy.types.WindowManager.adWingsRP = bpy.props.FloatProperty(update=activateWings, name="Wing Rot Position", default=0.0)
    bpy.types.WindowManager.adWingsRR = bpy.props.FloatProperty(update=activateWings, name="Wing Rot Range", default=3.0, min=0.0)
    bpy.types.WindowManager.adWingsCurveUD = bpy.props.FloatProperty(update=activateWings, name="wingsCurveUD", default=0.0)
    bpy.types.WindowManager.adWingsCurveFB = bpy.props.FloatProperty(update=activateWings, name="wingsCurveFB", default=0.0)
    bpy.types.WindowManager.adWingsFB = bpy.props.FloatProperty(update=setFwdBackwardPosition, name="Solo WingFB", default=0.0)
    bpy.types.WindowManager.adWingsAxial = bpy.props.FloatProperty(update=setAxialPosition, name="WingAxial", default=0.0)
    bpy.types.WindowManager.adWingsInnerFeathers = bpy.props.FloatProperty(update=setInnerFeathers, name="Rot Inner Feathers", default=0.0)
    bpy.types.WindowManager.adWingsOuterFeathers = bpy.props.FloatProperty(update=setOuterFeathers, name="Rot Outer Feathers", default=0.0)
    '''
    # 
    # Initiate building of bones
    n = getSceneObjectNumber()  # Each character name will be numbered sequentially.
    wings.name = setName('adWings', n)  # biped, quadruped, bird, centaur, spider, kangaroo
    x = 0; y = -.8 - n * .2; z = 1.9
    at = buildRootArmature(wings, wings.name, x, y, z) # Start character armature and bones
    Vhead = [0, 0, 0]
    Vtail = [0.0, 0.1, 0]  # End location of handle relative to armature origin - this effects coordinate system
    bone = setHandle(at, wings.name, Vhead, Vtail)
    # Build wings shared part between bird and solo wings xxx2
    createWings(at)
    deselectAll()
    ob = bpy.data.objects.get(wings.name)
    context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.context.object.rotation_euler[2] = -1.5708

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# END WINGS SECTION
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


def register():
    from bpy.utils import register_class
    register_class(Biped_Build_Btn)
    register_class(Centaur_Build_Btn)    
    register_class(Pose_Btn)
    register_class(Drop_Arms_Btn)
    register_class(Walk_Btn)
    register_class(Run_Btn)
    register_class(Arm_Action_Btn)
    register_class(Leg_Action_Btn)
    register_class(Reset_btn)
    #
    register_class(CONTROL_PT_Panel)
    bpy.utils.register_class(BIPED_OT_control_I)
    bpy.utils.register_class(BIPED_OT_control_II)
    #
    register_class(QuadrupedBuild_Button)
    register_class(Bird_Button)
    register_class(Spider_Button)
    register_class(Wings_Button)

def unregister():
    from bpy.utils import unregister_class
    unregister_class(Biped_Build_Btn)
    unregister_class(Centaur_Build_Btn)
    unregister_class(Pose_Btn)
    unregister_class(Drop_Arms_Btn)
    unregister_class(Walk_Btn)
    unregister_class(Run_Btn)
    unregister_class(Arm_Action_Btn)
    unregister_class(Leg_Action_Btn)
    unregister_class(Reset_btn)
    #
    unregister_class(CONTROL_PT_Panel)
    bpy.utils.unregister_class(BIPED_OT_control_I)
    bpy.utils.unregister_class(BIPED_OT_control_II)
    #
    unregister_class(QuadrupedBuild_Button)
    unregister_class(Bird_Button)
    unregister_class(Spider_Button)
    unregister_class(Wings_Button)

if __name__ == "__main__":
    register()
