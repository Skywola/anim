# cycle control - this is the engine that creates the movement!
def clock(cycle=1.0, freq=9, amp=.5):  # Sets the pace
    frame = bpy.context.scene.frame_current
    stp = amp * abs((cycle*frame)/freq % 4 - 2) - amp
    return round(stp, 2)

# add to namespace
bpy.app.driver_namespace['clock'] = clock  # Important

def set_pivot(coordinates=Vector()):
    bpy.ops.object.mode_set(mode='EDIT')
    ob = bpy.context.active_object
    mw = ob.matrix_world
    o = mw.inverted() @ Vector(coordinates)
    ob.data.transform(Matrix.Translation(-o))
    mw.translation = coordinates
    bpy.ops.object.mode_set(mode='OBJECT')

# getEuler output represents:
# bpy.data.objects['rg00biped'].pose.bones["backCenter"]
def getEuler(str_bone_name):  # *** Switching to pose mode must be external
    ob = bpy.context.object
    bone = ob.pose.bones[str_bone_name]
    bone.rotation_mode = 'XYZ'
    return bone

def deselectAll():
    for obj in bpy.context.selected_objects:
        obj.select_set(False)

def deleteAll():
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# vector
# string
def boneExtrude(vector, name):
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.armature.extrude_forked(TRANSFORM_OT_translate={"value":vector})
    bpy.context.active_bone.name = name
    bone = bpy.context.active_bone
    return bone

def getSceneObjectNumber():
    n = 0
    for o in bpy.data.objects:
        if("at" in o.name):
            n += 1
    return n

def new_armature(name, x=0, y=0, z=0):
    bpy.context.scene.frame_start = 0
    n = getSceneObjectNumber()
    armature = bpy.data.armatures.new(name + str(n) + '_at')  # at = Armature
    rig = bpy.data.objects.new(name, armature) # rig = Armature object
    rig.show_in_front = True
    rig.location = (x, y, z)  # Set armature point locatioon
    # Link to scene
    coll = bpy.context.view_layer.active_layer_collection.collection
    coll.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    bpy.context.view_layer.update()
    return rig

# Make bone creation easy
'''
def createBone(name="boneName", pHead=Vector(), pTail=Vector(), roll=0, con=False):
    bpy.ops.object.mode_set(mode='EDIT')
    bData = bpy.context.active_object.data
    bone = bData.edit_bones.new(name)
    bone.head[:] = [pHead.x, pHead.y, pHead.z]
    bone.tail[:] = [pTail.x, pTail.y, pTail.z]
    bone.roll = roll
    bone.use_connect = con
    return bone
'''

# Different data paths are used to access different bone data -
# obj = bpy.data.objects['Armature']
# obj.data.edit_bones # adding, deleting, positioning bones
# obj.data.bones # adjusting bone properties
# obj.pose.bones # adding constraints, custom shapes...

def createBone(name, head, tail):
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    obArm = bpy.context.active_object
    ebs = obArm.data.edit_bones
    eb = ebs.new(name)
    eb.head = head
    eb.tail = tail
    return eb

# Set Driver For Single Axis Only:
def setAxisDriver(euler, fn="0", axis=0, movementType='rotation_euler'):
    edriver = euler.driver_add(movementType, axis)
    edriver.driver.type = 'SCRIPTED'
    edriver.driver.expression = fn
    return edriver

def setActiveArmature(classBone, deselect=True):
    bpy.ops.object.mode_set(mode='OBJECT')
    if(deselect):
        bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = classBone.armature
    bpy.data.objects[classBone.armature.name].select_set(True)

# Right arm will need to be set to 90 in most cases
def dropArm(arm, rot=-90):
    bpy.ops.object.mode_set(mode='OBJECT')
    deselectAll()
    arm.armature.select_set(True)
    arm.armature.rotation_euler.x = radians(rot)

def animateBipedLeg(char, leg, flip=False):
    set_pivot((char.location.x, char.location.y, char.leg_height))
    fn = str(leg.rotateRangeFemur) +'*(clock()+'+ str(leg.rotatePositionFemur)+")" + leg.ZeroAtFrame0
    if(flip):
        fn = "-1*" + fn
    bJ1 = leg.bones[0]
    Driver1 = setAxisDriver(getEuler(bJ1.name), fn, 2)
    #
    # Leg Tibia
    fn = str(leg.rotateRangeTibia) +'*(clock()+'+ str(leg.rotatePositionTibia)+")" + leg.ZeroAtFrame0
    if(flip):
        fn = str(leg.rotateRangeTibia) +'*(clock()+'+ str(leg.rotatePositionTibia*-1)+")" + leg.ZeroAtFrame0
        fn = "-1*" + fn
    bJ3L = leg.bones[2]
    Driver3 = setAxisDriver(getEuler(bJ3L.name), fn, 2)
    #
    # Ankle
    fn = str(leg.rotateRangeAnkle) +'*(clock()+'+ str(leg.rotatePositionAnkle)+")" + leg.ZeroAtFrame0
    if(flip):
        fn = str(leg.rotateRangeAnkle) +'*-1*(clock()+'+ str(leg.rotatePositionAnkle)+")" + leg.ZeroAtFrame0
    bJ5 = leg.bones[4]
    setAxisDriver(getEuler(bJ5.name), fn, 2)
    

def animateBipedArm(char, arm, flip=False):
    set_pivot((char.location.x, char.location.y, ch.shoulder_height))
    # Humerus - Arms rotation
    fn = "-(" + str(arm.rotatePositionHumerus)+"+clock()*" + str(arm.rotateRangeHumerus) + ")" + arm.ZeroAtFrame0
    aJ1 = arm.bones[0]
    setAxisDriver(getEuler(aJ1.name), fn, 2)
    # Ulna - Arms rotation
    fn = "(-1*" + str(arm.rotatePositionUlna)+"-clock()*" + str(arm.rotateRangeUlna) + ")" + arm.ZeroAtFrame0
    if(flip):
        fn = "(" + str(armR.rotatePositionUlna)+"-clock()*" + str(armR.rotateRangeUlna) + ")" + arm.ZeroAtFrame0
    aJ3 = arm.bones[2]
    setAxisDriver(getEuler(aJ3.name), fn, 2)

def setShoulderSwayFB(char, component, axis=1): # left-right sway movement
    bpy.context.view_layer.objects.active = component.armature
    fn = "-(asin(clock())* " + str(char.shoulder_FB) + "*.2)"
    J1 = component.bones[0]
    setAxisDriver(getEuler(J1.name), fn, axis, 'rotation_euler')

def setShoulderSwayUD(char, component, axis=1): # left-right sway movement
    bpy.context.view_layer.objects.active = component.armature
    fn = "-(asin(clock())* " + str(char.shoulder_UD) + "*.2)"
    J1 = component.bones[0]
    setAxisDriver(getEuler(J1.name), fn, axis, 'rotation_euler')

def setSwayLR(char, component, axis=1): # left-right sway movement
    bpy.context.view_layer.objects.active = component.armature
    fn = "-(asin(clock())* " + str(char.sway_LR) + "*.2)"
    J1 = component.bones[0]
    setAxisDriver(getEuler(J1.name), fn, axis, 'rotation_euler')
    
def setSwayFB():  # forward - backward sway movement
    fn = "-(asin(" + 'clock()' + ")* " + str(ch.sway_FB) + "*.01)"
    cJ1 = ch.bones[0]
    setAxisDriver(getEuler(cJ1.name), fn, 0, 'rotation_euler')
    
def setDirection(ch, dir=0):
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.view_layer.objects.active = ch.armature
    bpy.context.view_layer.objects.active.rotation_euler.z = math.radians(dir)



def setBounce(): # Bounce
    fn = "-(asin(clock())*" + str(ch.bounce) + "*.01)"
    cJ1 = ch.bones[0]
    setAxisDriver(getEuler(cJ1.name), fn, 2, 'location')



## Body Controls
def update(self, context):
    bpy.ops.object.mode_set(mode='POSE')
    bpy.context.scene.frame_current = 1
    bpy.ops.object.mode_set(mode='OBJECT')

# ch = getCurrentlySelectedChar():


# Rotate the easy way
def rotate(str_bone_name, rad=0, axis=0):
    rad = radians(rad)
    bpy.ops.object.mode_set(mode='POSE')
    ob = bpy.context.object
    if(ob.name.startswith("rg")): # ***Now specific to Character types***
        euler = ob.pose.bones[str_bone_name]
        euler.rotation_mode = 'XYZ'
        bpy.data.objects[ob.name].pose.bones[str_bone_name].rotation_euler[axis] = rad



def setShoulder():
    shoulder_FB = str(ch.shoulder_FB*.04)
    fn = "(asin(clock()) * " + shoulder_FB + ")/3.14"
    cJs = ch.bones[5]
    setAxisDriver(getEuler(cJs.name), fn, 1)
    # Compensate for rotation by r0tating neck and head in opposite directiion, in three parts
    fn = "-(asin(clock()) * " + shoulder_FB + "/3)/3.14"
    cJs = ch.bones[6]
    setAxisDriver(getEuler(cJs.name), fn, 1)
    cJs = ch.bones[7]
    setAxisDriver(getEuler(cJs.name), fn, 1)
    cJs = ch.bones[8]
    setAxisDriver(getEuler(cJs.name), fn, 1)
    # Shoulder up - down movement
    shoulder_UD = str(ch.shoulder_UD*.06)
    fn = "-(asin(clock()) * " + shoulder_UD + ")/3.14"
    cJs = ch.bones[9]
    setAxisDriver(getEuler(cJs.name), fn, 2)
    fn = "-(asin(clock()) * " + shoulder_UD + ")/3.14"
    cJs = ch.bones[10]
    setAxisDriver(getEuler(cJs.name), fn, 2)

# walk speed control
def setHorizontalSpeed():
    spd = ch.speed
    frame = bpy.context.scene.frame_current
    spd = frame * .04 * spd
    return round(spd, 2)

# add this function to the namespace
bpy.app.driver_namespace['setHorizontalSpeed'] = setHorizontalSpeed

    
## LEG controls
def setRun():
    ch.cycle = 4.0
    ch.bounce = 1.2
    ch.hip_rotate = 2.0
    ch.sway_LR = 2.0   
    ch.sway_FB = 4.0
    ch.hip_UD = 3.0 
    ch.shoulder_FB = 2.0
    ch.shoulder_UD = 4.0 
    ch.Arm_Rotation = 4.0
    ch.rotatePositionHumerus = 0.0
    ch.rotateRangeHumerus = 1.0
    ch.rotatePositionUlna = 0.0
    ch.rotateRangeUlna = 1.0
    ch.rotatePositionFemur = 0.1   # was genProp. from here down
    ch.rotatePositionTibia = -.4 # 1.0
    ch.rotatePositionAnkle = 0.1
    ch.rotatePositionToe = -.1
    ch.rotateRangeFemur = 2.2
    ch.rotateRangeTibia = 1.0   # .6
    ch.rotateRangeAnkle = 2.2
    ch.rotateRangeToe = 1.8   # 2.2
    ch.rotateRangeBack = 1.0  # Need calibration
    ch.rotateRangeNeck = 1.0  # Need calibration
    setCharacterAction(self, context)
    bpy.ops.object.mode_set(mode='OBJECT')

def unSetLegRotation():
    # For each bone remove driver (Alternatively, just reset to zero or delete)
    for b in leg.bones:
        undo = bpy.data.objects[leg.name].pose.bones[b.name]
        undo.driver_remove('rotation_euler', -1)

def unSetArmRotation(self, context):
    for b in arm.bones:
        undo = bpy.data.objects[arm.name].pose.bones[b.name]
        undo.driver_remove('rotation_euler', -1)


def setLegArch(leg):
    fn = leg.Leg_Arch * .02  # Leg Arch
    lJ1 = leg.bones[0]
    setAxisDriver(getEuler(lJ1.name), str(-fn), 1)
    setAxisDriver(getEuler(lJ1.name), str(fn), 1)

def setArms(arm):  # TODO This roars slider
    UD = math.radians(arm.Arms_UD)
    aJ1 = arm.bones[0]
    rotate(aJ1.name, UD, 2)
    rotate(aJ1.name, -UD, 2)
    bpy.context.object.data.bones[aJ1.name].select  = True
    bpy.context.object.data.bones[aJ1.name].select  = True
    bpy.ops.object.mode_set(mode='POSE')

def setArmTwistL(arm):   # Should be able to merge this and the fn below it.
    LArm_Twist = arm.LArm_Twist  * -.1
    aJ2 = arm.bones[1]
    rotate(aJ2.name, LArm_Twist, 1)
    aJ3 = arm.bones[2]
    rotate(aJ3.name, LArm_Twist, 1)
    aJ4 = arm.bones[3]
    rotate(aJ4.name, LArm_Twist, 1)
    aJ5 = arm.bones[4]
    rotate(aJ5.name, LArm_Twist, 1)
    bpy.context.object.data.bones[aJ2.name].select  = True
    bpy.context.object.data.bones[aJ3.name].select  = True
    bpy.context.object.data.bones[aJ4.name].select  = True
    bpy.context.object.data.bones[aJ5.name].select  = True
    bpy.ops.object.mode_set(mode='POSE')

def setArmTwistR(self, context):
    name = getSelectedCharacterName()
    RArm_Twist = ch.RArm_Twist   * .1
    rotate('armJ2.R', RArm_Twist, 1)
    rotate('armJ3.R', RArm_Twist, 1)
    rotate('armJ4.R', RArm_Twist, 1)
    rotate('armJ5.R', RArm_Twist, 1)
    bpy.context.object.data.bones['armJ2.R'].select  = True
    bpy.context.object.data.bones['armJ3.R'].select  = True
    bpy.context.object.data.bones['armJ4.R'].select  = True
    bpy.context.object.data.bones['armJ5.R'].select  = True
    bpy.ops.object.mode_set(mode='POSE')
    

