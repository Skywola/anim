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


# Get name from whatever bone is selected in whatever mode
def getSelectedCharacterName():
    obj = bpy.context.object
    if(characterExists()):
        context.view_layer.objects.active = obj
        obj.select_set(True)
        genProp.strName = obj.name
        return 0
    if(obj.parent):  # If user is not in OBJECT MODE, search 
        parent = obj.parent  # up the tree to the root bone.
        if(parent.name.startswith("rg")):
            obj.select_set(False)
            context.view_layer.objects.active = parent
            parent.select_set(True)
            return 0
    return 0

def setLocation(self, context):  # TODO This needs to be worked into the set walk, run functions
    bpy.ops.object.mode_set(mode='OBJECT')

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# genProp COMMON PROPERTIES
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
genProp.blank = bpy.props.FloatProperty(name="blank", default=0)
genProp.strName = bpy.props.StringProperty(name="strName", default="None")
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
    getSelectedCharacterName()
    ob = bpy.data.objects.get(genProp.strName)
    if(hasattr(bpy.types.WindowManager, "direction")):
        direction = math.radians(cwmPanel.direction)
    bpy.data.objects[genProp.strName].rotation_euler.z = direction

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

''' # Skate motion, but interferes with already used axis
def setSkate(self, context): # Leg Spread
    # Ref - cwmPanel = bpy.context.window_manager
    #ob = bpy.context.object
    #bpy.ops.object.mode_set(mode='POSE')
    LS = str(radians(cwmPanel.Leg_Spread))
    skate = str(cwmPanel.skate*.06)
    fn = "-(asin(clock()) * " + skate + ")/3.14 + " + LS
    setAxisDriver(getEuler('femurJ1.L'), fn, 2)
    fn = "-(asin(clock()) * " + skate + ")/3.14 - " + LS
    setAxisDriver(getEuler('femurJ1.R'), fn, 2)
    bpy.ops.object.mode_set(mode='OBJECT')
'''

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

def unsetBipedWalk(self, context):
    getSelectedCharacterName()
    for b in bpy.data.objects[genProp.strName].pose.bones:
        b.driver_remove('rotation_euler', -1)

def setRun(self, context):
    getSelectedCharacterName()
    unsetBipedWalk(self, context)
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
    getSelectedCharacterName()
    undo = bpy.data.objects[genProp.strName].pose.bones['femurJ1.L']
    undo.driver_remove('rotation_euler', -1)
    undo = bpy.data.objects[genProp.strName].pose.bones['femurJ1.R']
    undo.driver_remove('rotation_euler', -1)
    undo = bpy.data.objects[genProp.strName].pose.bones['tibiaJ1.L']
    undo.driver_remove('rotation_euler', -1)
    undo = bpy.data.objects[genProp.strName].pose.bones['tibiaJ1.R']
    undo.driver_remove('rotation_euler', -1)
    undo = bpy.data.objects[genProp.strName].pose.bones['ankle.L']
    undo.driver_remove('rotation_euler', -1)
    undo = bpy.data.objects[genProp.strName].pose.bones['ankle.R']
    undo.driver_remove('rotation_euler', -1)
    undo = bpy.data.objects[genProp.strName].pose.bones['toe.L']
    undo.driver_remove('rotation_euler', -1)
    undo = bpy.data.objects[genProp.strName].pose.bones['toe.R']
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
    getSelectedCharacterName()
    undo = bpy.data.objects[genProp.strName].pose.bones['armJ1.L']
    undo.driver_remove('rotation_euler', -1)
    undo = bpy.data.objects[genProp.strName].pose.bones['armJ1.R']
    undo.driver_remove('rotation_euler', -1)
    undo = bpy.data.objects[genProp.strName].pose.bones['armJ3.L']
    undo.driver_remove('rotation_euler', -1)
    undo = bpy.data.objects[genProp.strName].pose.bones['armJ3.R']
    undo.driver_remove('rotation_euler', -1)
    undo = bpy.data.objects[genProp.strName].pose.bones['bBackJ4']
    undo.driver_remove('rotation_euler', -1)

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# BIPED PROPERTIES (with update= ) AND THEIR FUNCTIONS PRECEEDING THEM
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def setLegArch(self, context):
    fn = cwmPanel.Leg_Arch * .02  # Leg Arch
    setAxisDriver(getEuler('femurJ1.L'), str(-fn), 1)
    setAxisDriver(getEuler('femurJ1.R'), str(fn), 1)

def setArms(self, context):  # TODO This roars slider
    UD = math.radians(cwmPanel.Arms_UD)
    rotate(genProp.strName, 'armJ1.L', UD, 2)
    rotate(genProp.strName, 'armJ1.R', -UD, 2)
    bpy.context.object.data.bones['armJ1.L'].select  = True
    bpy.context.object.data.bones['armJ1.R'].select  = True
    #bpy.ops.object.mode_set(mode='POSE')

def setArmTwistL(self, context):
    getSelectedCharacterName()
    LArm_Twist = cwmPanel.LArm_Twist  * -.1
    rotate(genProp.strName, 'armJ2.L', LArm_Twist, 1)
    rotate(genProp.strName, 'armJ3.L', LArm_Twist, 1)
    rotate(genProp.strName, 'armJ4.L', LArm_Twist, 1)
    rotate(genProp.strName, 'armJ5.L', LArm_Twist, 1)
    bpy.context.object.data.bones['armJ2.L'].select  = True
    bpy.context.object.data.bones['armJ3.L'].select  = True
    bpy.context.object.data.bones['armJ4.L'].select  = True
    bpy.context.object.data.bones['armJ5.L'].select  = True
    bpy.ops.object.mode_set(mode='POSE')

def setArmTwistR(self, context):
    getSelectedCharacterName()
    RArm_Twist = cwmPanel.RArm_Twist   * .1
    rotate(genProp.strName, 'armJ2.R', RArm_Twist, 1)
    rotate(genProp.strName, 'armJ3.R', RArm_Twist, 1)
    rotate(genProp.strName, 'armJ4.R', RArm_Twist, 1)
    rotate(genProp.strName, 'armJ5.R', RArm_Twist, 1)
    bpy.context.object.data.bones['armJ2.R'].select  = True
    bpy.context.object.data.bones['armJ3.R'].select  = True
    bpy.context.object.data.bones['armJ4.R'].select  = True
    bpy.context.object.data.bones['armJ5.R'].select  = True
    bpy.ops.object.mode_set(mode='POSE')

def setArmRotation(self, context):
    getSelectedCharacterName()
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
    getSelectedCharacterName()
    LHand_OC = cwmPanel.LHand_OC   * .1
    for i in range(1, 4):
        rotate(genProp.strName, 'indexJ' + str(i) + '.L', LHand_OC, 2)
        rotate(genProp.strName, 'midJ' + str(i) + '.L', LHand_OC, 2)
        rotate(genProp.strName, 'ringJ' + str(i) + '.L', LHand_OC, 2)
        rotate(genProp.strName, 'pinkyJ' + str(i) + '.L', LHand_OC, 2)
    for i in range(1, 4):
        bpy.context.object.data.bones['indexJ' + str(i) + '.L'].select  = True       
        bpy.context.object.data.bones['midJ' + str(i) + '.L'].select  = True
        bpy.context.object.data.bones['ringJ' + str(i) + '.L'].select  = True
        bpy.context.object.data.bones['pinkyJ' + str(i) + '.L'].select  = True
    bpy.ops.object.mode_set(mode='POSE')
    
def LHandSpread(self, context): # Light hand spread
    LHand_Spread = cwmPanel.LHand_Spread - 30
    index = (LHand_Spread) * -.04 - .8 # Light hand spread
    rotate(genProp.strName, 'indexJ1.L', index, 0)
    ring = (LHand_Spread) * .017 + .36 # Light hand spread
    rotate(genProp.strName, 'ringJ1.L', ring, 0)
    pinky = (LHand_Spread) * .052 + 1.0 # Light hand spread
    rotate(genProp.strName, 'pinkyJ1.L', pinky, 0)
    for i in range(1, 4):
        bpy.context.object.data.bones['indexJ' + str(i) + '.L'].select  = True       
        bpy.context.object.data.bones['midJ' + str(i) + '.L'].select  = True
        bpy.context.object.data.bones['ringJ' + str(i) + '.L'].select  = True
        bpy.context.object.data.bones['pinkyJ' + str(i) + '.L'].select  = True
    bpy.ops.object.mode_set(mode='POSE')

def RHandOpenClose(self, context): # Right hand open - close
    getSelectedCharacterName()
    RHand_OC = cwmPanel.RHand_OC   * -.1
    for i in range(1, 4):
        rotate(genProp.strName, 'indexJ' + str(i) + '.R', RHand_OC, 2)
        rotate(genProp.strName, 'midJ' + str(i) + '.R', RHand_OC, 2)
        rotate(genProp.strName, 'ringJ' + str(i) + '.R', RHand_OC, 2)
        rotate(genProp.strName, 'pinkyJ' + str(i) + '.R', RHand_OC, 2)
    for i in range(1, 4):
        bpy.context.object.data.bones['indexJ' + str(i) + '.R'].select  = True       
        bpy.context.object.data.bones['midJ' + str(i) + '.R'].select  = True
        bpy.context.object.data.bones['ringJ' + str(i) + '.R'].select  = True
        bpy.context.object.data.bones['pinkyJ' + str(i) + '.R'].select  = True
    bpy.ops.object.mode_set(mode='POSE')
    
def RHandSpread(self, context): # Right hand spread
    RHand_Spread = cwmPanel.RHand_Spread - 30
    index = (RHand_Spread) * -.04 - .8 # Right hand spread
    rotate(genProp.strName, 'indexJ1.R', index, 0)
    ring = (RHand_Spread) * .017 + .36 # Right hand spread
    rotate(genProp.strName, 'ringJ1.R', ring, 0)
    pinky = (RHand_Spread) * .052 + 1.0 # Right hand spread
    rotate(genProp.strName, 'pinkyJ1.R', pinky, 0)
    for i in range(1, 4):
        bpy.context.object.data.bones['indexJ' + str(i) + '.R'].select  = True       
        bpy.context.object.data.bones['midJ' + str(i) + '.R'].select  = True
        bpy.context.object.data.bones['ringJ' + str(i) + '.R'].select  = True
        bpy.context.object.data.bones['pinkyJ' + str(i) + '.R'].select  = True
    bpy.ops.object.mode_set(mode='POSE')

def setHead(self, context):
    getSelectedCharacterName()
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
    getSelectedCharacterName()
    Jaw_OC = cwmPanel.Jaw_OC * -.1
    rotate(genProp.strName, 'jaw', Jaw_OC, 0)
    bpy.context.object.data.bones['jaw'].select  = True
    bpy.ops.object.mode_set(mode='POSE')

# If centered at rear joint, parented, can be used  for eye movements
def setEye(self, context):
    getSelectedCharacterName()
    Eye_LR = cwmPanel.Eye_LR * .1    # Left - Right turn motion 
    rotate(genProp.strName, 'eye.L', Eye_LR, 2)
    rotate(genProp.strName, 'eye.R', Eye_LR, 2)
    #
    Eye_UD = cwmPanel.Eye_UD * .1   # Eye up - down
    rotate(genProp.strName, 'eye.L', Eye_UD, 0)
    rotate(genProp.strName, 'eye.R', Eye_UD, 0)
    bpy.context.object.data.bones['eye.L'].select  = True
    bpy.context.object.data.bones['eye.R'].select  = True
    bpy.ops.object.mode_set(mode='POSE')

def setBipedWalk(self, context):
    ob = bpy.context.object
    bpy.ops.object.mode_set(mode='OBJECT')
    getSelectedCharacterName()
    #
    z = radians(bpy.data.objects[genProp.strName].pose.bones[genProp.strName + '_bone'].rotation_euler.z)
    fnx = "setHorizontalSpeed() * cos(" + str(z) + ")"
    setAxisDriver(getEuler(genProp.strName+'_bone'), fnx, 1, 'location')
    fny = "setHorizontalSpeed() * sin(" + str(z) + ")"
    setAxisDriver(getEuler(genProp.strName+'_bone'), fny, 0, 'location')
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
    ob = bpy.data.objects.get(genProp.strName)        
    ob.select_set(True)
    biped = Biped
    biped.setBipedPropertiesPanel()
    bpy.context.scene.frame_set(1)
    bpy.ops.object.mode_set(mode='OBJECT')

def setHip(self, context):
    getSelectedCharacterName()
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
    ob = bpy.data.objects.get(genProp.strName)
    context.view_layer.objects.active = ob
    ob.select_set(True)


# PopUp Window Properties declared strictly for class WM_OT_controol window
genProp.cycle = bpy.props.FloatProperty(update=update, name="Cycle", default=1.0)
genProp.speed = bpy.props.FloatProperty(update=update, name="Speed")
genProp.direction = bpy.props.FloatProperty(update=setDirection, name="Direction", default=0.0)
genProp.X_Location = bpy.props.FloatProperty(update=update, name="X_Location", default=0.0)
genProp.Y_Location = bpy.props.FloatProperty(update=update, name="Y_Location", default=0.0)
genProp.Z_Location = bpy.props.FloatProperty(update=update, name="Z_Location", default=1.2)
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
# Sliders
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
    '''Pose Character Bones'''
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

class Character_Panel_Btn(bpy.types.Operator): # Because this is a floating panel, it is not
    '''Activate Character'''                     # entered as a standard _P T_ panel
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
        layout.row().operator("object.biped_build_btn")  # Build Biped
        #layout.row().operator("object.pose_btn")  # Pose Character (Common to all)
        #layout.row().operator("object.drop_arms_btn")  # Drop Arms
        layout.row().operator("object.walk_btn")  # Set Walk
        #layout.row().operator("object.run_btn")  # Set Run
        layout.row().operator("object.control1_btn") # Character controls
        layout.row().operator("object.control2_btn") # Character controls
        #layout.row().operator("object.arm_action_btn")  # Arm action
        #layout.row().operator("object.leg_action_btn")  # Leg action
        #layout.row().operator("object.reset_btn")  # Revert Advanced Controls

class WM_OT_control_I(bpy.types.Operator):
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
    #skate : bpy.props.FloatProperty(name= "Skate", default=0.0)
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
        ob.location = (self.X_Location, self.Y_Location, self.Z_Location)
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

class WM_OT_control_II(bpy.types.Operator):
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
        getSelectedCharacterName()
        bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}
    #
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)



class Biped_Build_Btn(bpy.types.Operator):  # Button
    '''Build Biped Character Bones'''
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
    '''Drop Biped Arms'''
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
    '''Pose Biped'''
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
    '''Biped Walk'''
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
    '''Biped Run'''
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
    '''Biped Arm Action'''
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
    '''Biped Leg Action'''
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
    '''Revert To Default Settings'''
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
    bl_label = "bipedUtils"
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
#|
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
def getSelectedCharacterName():
    charTypes = ("rgbiped","rgquadruped","rgbird", "rgcentaur","rgspider")
    for obj in bpy.context.selected_objects:
        if(obj.name in charTypes):
            context.view_layer.objects.active = obj
            obj.select_set(True)
            genProp.strName = obj.name
            break
        if(obj.parent):  # If user is not in OBJECT MODE, search 
            parent = obj.parent  # up the tree to the root bone.
            if(parent.name.startswith("rg")):
                obj.select_set(False)
                context.view_layer.objects.active = parent
                parent.select_set(True)
                break

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

def buildRootArmature(type, strCharName, x, y, z):
    at = bpy.data.armatures.new(strCharName + '_at')  # at = Armature
    biped.armature = at
    biped.armatureName = at.name
    bpy.context.scene.frame_start = 0
    type.rig = bpy.data.objects.new(strCharName, at)  # rig = Armature object
    type.rig.show_in_front = True
    type.x = x
    type.y = y
    type.rig.location = (x, y, z)  # Set armature point locatioon
    # Link to scene
    coll = bpy.context.view_layer.active_layer_collection.collection
    coll.objects.link(type.rig)
    bpy.context.view_layer.objects.active = type.rig
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
    charTypes = ["rgbiped","rgquadruped","rgbird","rgcentaur","rgadWings"]
    for character in bpy.context.selected_objects:
        if(character.name[:-2] in charTypes):
            return True
    return false

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
    getSelectedCharacterName()
    if(genProp.strName.startswith("rgbiped")):
        setBipedWalk(self, context)
    else:
        print("A character must be selected to activate it!")

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# setEnve1opeWeights - COMMON FUNCTION 
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def setEnvelopeWeights():
    # The position of the following two for loops is important;
    # it initializes all bones to have a specific envelope weight
    # in case the bone has not been set manually as below. It 
    # cannot be placed afterwards, or it will override the settings.
    for b in bpy.data.objects[genProp.strName].pose.bones:
        b.rotation_mode = 'XYZ'
    for b in bpy.context.object.data.edit_bones:
        b.envelope_distance = 0.05  # Default envelope distance
        b.head_radius = 0.02
        b.tail_radius = 0.02
        #b.envelope_weight = 2.0
    #
    name = genProp.strName.replace("rg", "")
    for b in bpy.context.object.data.edit_bones:
        # Set weights for biped lower body
        if(name.startswith("biped")):
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
        if(name.startswith("biped")) or (name.startswith("centaur")):
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
    genProp.strName = setName('biped', n)
    mod = math.fmod(n, 2)
    if(mod == 0):
        x = 1.0 * n - mod    # Can you build an armature at the origin
    else:                    # then start building bones independent of it?
        x = 1.0 * -n - mod
    y = -.4 * n; z = cwmPanel.Z_Location  # y = Head of handle (Armature point)
    # at is named genProp.strName_at or genProp.strName_at.00#  
    at = buildRootArmature(biped, genProp.strName, x, y, z) # creates point, no bone yet
    biped.armature = at
    # %%% FIRST BONE %%% FIRST CHARACTER WILL E NAMED rgbiped01
    VHead = [0, 0, 0]
    Vtail = [0, -.3, 0] # Tail of Handle  
    bone = setHandle(at, genProp.strName, VHead, Vtail) 
    bpy.data.objects[genProp.strName].show_in_front = True
    #
    V_angle = (0, 0, 0) # Bottom (Tail)
    angle = boneMirror(at, V_angle, False)
    #bone_name = getActiveBoneName()
    #at.edit_bones[bone_name].name = ""
    #angle.parent = at.edit_bones[genProp.strName + '_bone']
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
    setEnvelopeWeights()
    #
    deselectAll()
    ob = bpy.data.objects.get(genProp.strName)
    context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.context.object.rotation_euler[2] = -1.5708

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#  END BIPED SKELETON BUILD
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# COMMON FUNCTION - bui1dHumanUpperBody     To 1779
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def buildHumanUpperBody(V_bBackJ1 = (0, 0, 0.1)):
    biped = Biped
    at = biped.armature
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["angle"].select_tail=True
    boneMirror(at, V_bBackJ1, False)
    V_bBackJ2 = (0, 0, 0.1)
    boneMirror(at, V_bBackJ2, False)
    V_bBackJ3 = (0, 0, 0.14)
    boneMirror(at, V_bBackJ3, False)
    V_bBackJ4 = (0, 0, 0.1)
    boneMirror(at, V_bBackJ4, False)
    V_bBackJ5 = (0, 0, 0.1)
    boneMirror(at, V_bBackJ5, False)
    at.edit_bones["angle.001"].name = "bBackJ1"
    at.edit_bones["angle.002"].name = "bBackJ2"
    at.edit_bones["angle.003"].name = "bBackJ3"
    at.edit_bones["angle.004"].name = "bBackJ4"
    at.edit_bones["angle.005"].name = "bBackJ5"
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

def register():
    from bpy.utils import register_class
    register_class(Biped_Build_Btn)
    register_class(Pose_Btn)
    register_class(Drop_Arms_Btn)
    register_class(Walk_Btn)
    register_class(Run_Btn)
    #register_class(Arm_Action_Btn)
    #register_class(Leg_Action_Btn)
    #register_class(Reset_btn)
    #
    register_class(CONTROL_PT_Panel)
    bpy.utils.register_class(WM_OT_control_I)
    bpy.utils.register_class(WM_OT_control_II)

def unregister():
    from bpy.utils import unregister_class
    unregister_class(Biped_Build_Btn)
    unregister_class(Pose_Btn)
    unregister_class(Drop_Arms_Btn)
    unregister_class(Walk_Btn)
    unregister_class(Run_Btn)
    #unregister_class(Arm_Action_Btn)
    #unregister_class(Leg_Action_Btn)
    #unregister_class(Reset_btn)
    #
    unregister_class(CONTROL_PT_Panel)
    bpy.utils.unregister_class(WM_OT_control_I)
    bpy.utils.unregister_class(WM_OT_control_II)

if __name__ == "__main__":
    register()
