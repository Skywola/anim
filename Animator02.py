import bpy, math
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
quat = mathutils.Quaternion

def clock(freq=9, amp=.5):  # Standard Walk speed
    frame = bpy.context.scene.frame_current
    stp = amp * abs(frame/freq % 4 - 2) - amp
    return round(stp, 2)

bpy.app.driver_namespace['clock'] = clock

def linkObjectsToScene(rig):
    coll = context.view_layer.active_layer_collection.collection
    coll.objects.link(rig)
    context.view_layer.objects.active = rig
    bpy.context.view_layer.update()

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Start Utility Class and its associated functions
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class UtilsFns:
    bl_idname = "object.utilsfns"    # all lower case
    bl_label = "Build Biped"
    bl_description = "Build Biped"
    bl_options = {'REGISTER', 'UNDO'}
    charTypes = ["rgbiped","rgquadruped","rgbird","rgcentaur","rgadWings"]
	bipedHeight = 1.04
    strName = ""
    speed = 0.0
    direction = 0.0
    xlocation = 0.0
    ylocation = 0.0
    zlocation = 1.04
    swayLR = 0.0
    swayFB = 1.0
    bounce = 2.0
    headUD = 0.0
    headLR = 0.0
    headTurn = 0.0
    neckFB = 6.0
    neckLR = 0.0
    neckTurn = 0.0
    legSpread = 0.0
    earUD = 0.0
    earLR = 0.0
    earCurl = 0.0
    earAxial = 0.0
    earOUD = 0.0
    earOLR = 0.0
    earOCurl = 0.0
    earOAxial = 0.0
    jawOC = 0.0
    eyeLR = 0.0
    eyeUD = 0.0
    crestFB = 0.0
    crestLR = 0.0
    femurJ1RP = 0.0  # Advanced Controls
    femurJ1RR = 1.0
    femurJ1PP = 0.0
    rearFemurJ1RP = 0.0
    rearFemurJ1RR = 1.0
    rearFemurJ1PP = 0.0
    tibiaJ1RP = 0.0
    tibiaJ1RR = 1.0
    tibiaJ1PP = 0.0
    rearTibiaJ1RP = 0.0
    rearTibiaJ1RR = 1.0
    rearTibiaJ1PP = 0.0
    ankleRP = 0.0
    ankleRR = 1.0
    anklePP = -0.2
    rearAnkleRP = 0
    rearAnkleRR = 1.0
    rearAnklePP = 0.0
    toesRP = -.26
    toesRR = 1.0
    toesPP = 0.0
    rearToesRP = 0.0
    rearToesRR = 1.0
    rearToesPP = 0
    click = False
    cycle = 8.0
    str1xCycle = "sin(radians(" + str(cycle) + "*frame))"
    strHalfCycle = "sin(radians(" + str(cycle / 2) + "*frame))"
    str2xCycle = "sin(radians(" + str(cycle * 2) + "*frame))"
    str0AtFrame0 = " * (frame * (1/(frame+.0001)))" # Zero at frame zero, otherwise a one
    str1AtFrame0 = " * abs((frame/(frame + .0001))-1)"  # produce a one at frame zero, otherwise a zero
    phase = "0"
    strCyclePhased = "sin(radians(-" + str(phase) + "+" + str(cycle) + "*frame))"
    reinforce = True  # Option - Add extra bones for stabilization
    showNames = False  # Option - show bone names - for build only
    show_axes = False  # Option - Show armature axis - for build only
    toggleArmAction = True  # For toggling buttons
    toggleLegAction = True
    #
    def buildRootArmature(type, strCharName, x, y, z):
        at = bpy.data.armatures.new(strCharName + '_at')  # at = Armature
        bpy.context.scene.frame_start = 0
        type.rig = bpy.data.objects.new(strCharName, at)  # rig = Armature object
        type.rig.show_in_front = True
        type.x = x
        type.y = y
        type.rig.location = (x, y, z)  # Set armature location
        linkObjectsToScene(type.rig)
        return at
    #
    #
    def setHandle(at, strCharName, Vtail):
        bpy.ops.object.editmode_toggle()
        bone = at.edit_bones.new(strCharName + '_bone')
        bone.head = (0.0, 0.0, 0.0)  # LOCAL COORDINATE, [0,0,0] places bone directly on armature.
        bone.tail = Vtail
        return bone
    #
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

    #
    def boneMirror(armature, vector, mirror=False):
        bpy.data.armatures[armature.name].use_mirror_x = mirror
        x = vector[0]; y = vector[1]; z = vector[2]
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.armature.extrude_forked(ARMATURE_OT_extrude={"forked":True}, TRANSFORM_OT_translate={"value":(x, y, z)})
        bone = bpy.context.object.data.bones.active
        return bone

    # increment rig number each time one is built.
    def getSceneObjectNumber():
        n = 0
        for ob in list(bpy.data.objects):
            if ob.name.startswith('rg') == True:
                n = n + 1
        return n
    #
    def setName(type, n):
        name = "rg" + type + "0" + str(n + 1)  # Assume n < 10 
        if (n > 9):  # Change x.name if previous assumption is wrong
            name = "rg" + type + str(n + 1)
        return name
    #    
    # Rotate the easy way
    def rotate(bipedStrName, str_bone_name, rad=0, axis=0):
        bpy.ops.object.mode_set(mode='POSE')
        ob = bpy.context.object
        euler = ob.pose.bones[str_bone_name]
        euler.rotation_mode = 'XYZ'
        bpy.data.objects[bipedStrName].pose.bones[str_bone_name].rotation_euler[axis] = rad
    #
    def deselectAll():
        bpy.ops.object.mode_set(mode='OBJECT')
        for ob in bpy.context.selected_objects:
            ob.select_set(False)
    #
    def getSelectedCharacterName():
        for obj in bpy.context.selected_objects:
            if(obj.name in u.charTypes):
                context.view_layer.objects.active = obj
                obj.select_set(True)
                u.strName = obj.name
                break
            if(obj.parent):  # If user is not in OBJECT MODE, search 
                parent = obj.parent  # up the tree to the root bone.
                if(parent.name.startswith("rg")):
                    obj.select_set(False)
                    context.view_layer.objects.active = parent
                    parent.select_set(True)
                    break                   

    # Set horizontal speed for all characters based on the handle x,y,z coordinates.
	# This speed adjusts for the direction the character is heading
    def setHorizontalSpeed(self, context):
        u.getSelectedCharacterName()
        ob = bpy.data.objects.get(u.strName)
        if(hasattr(bpy.types.WindowManager, "speed")):
            u.speed = bpy.context.window_manager.speed * .1
        strPosition = str(bpy.context.scene.frame_current / 2800 * u.speed)
        bpy.ops.object.mode_set(mode='POSE')
        z = bpy.data.objects[u.strName].pose.bones[u.strName + '_bone'].rotation_euler.z
        fnx = strPosition + "*frame * -cos(" + str(z) + ")"
        fny = strPosition + "*frame * -sin(" + str(z) + ")"
        for obj in bpy.context.selected_objects:
            if(obj.name in u.charTypes):
			    # Horizontal handle x=LR y=FB z=UP
                u.setDriver(u.getEuler(u.strName + '_bone'), fnx, 1, 'location')
                u.setDriver(u.getEuler(u.strName + '_bone'), fny, 0, 'location')
        bpy.ops.object.mode_set(mode='OBJECT')
        ob.select_set(True)

    def setLocation(self, context):
        u.getSelectedCharacterName()
        ob = bpy.data.objects.get(u.strName)
        if(hasattr(bpy.types.WindowManager, "xlocation")):
            u.xlocation = math.radians(bpy.context.window_manager.xlocation)
        bpy.data.objects[u.strName].location.x = u.xlocation
        if(hasattr(bpy.types.WindowManager, "ylocation")):
            u.ylocation = math.radians(bpy.context.window_manager.ylocation)
        bpy.data.objects[u.strName].location.y = u.ylocation
        if(hasattr(bpy.types.WindowManager, "zlocation")):
            u.zlocation = math.radians(bpy.context.window_manager.zlocation + u.bipedHeight)
        bpy.data.objects[u.strName].location.z = u.zlocation
		#
        #ob.location.x = u.xlocation
        #ob.location.y = u.ylocation
        #ob.location.z = u.zlocation

    def getCharacterPanel(): # Because this is a floating panel, it is not
        u.getSelectedCharacterName()  # entered as a normal _PT_ panel
        bpy.ops.object.mode_set(mode='OBJECT')
        if(u.strName.startswith("rgbiped")):
            bpy.context.scene.frame_set(0)
        else:
            print("A character must be selected to get a panel for it!")

    # u.getEuler output represents:
    # bpy.data.objects['rg00biped'].pose.bones["backCenter"]
    def getEuler(str_bone_name):
        bpy.ops.object.mode_set(mode='POSE')
        ob = bpy.context.object
        bone = ob.pose.bones[str_bone_name]
        bone.rotation_mode = 'XYZ'
        return bone
    #
    # Equation for bone joints, with euler transform, axis 0=x 1=y 2=z
    # Note also that fn must be inserted as a STLING in the expression!
    def setDriver(bone, fn="0", axis=0, movementType='rotation_euler'):
        eulerDriver = bone.driver_add(movementType)
        eulerDriver[axis].driver.type = 'SCRIPTED'
        eulerDriver[axis].driver.expression = fn
        return eulerDriver
    #      
    # Set Driver For Single Axis Only:
    def setAxisDriver(euler, fn="0", axis=0, movementType='rotation_euler'):
        edriver = euler.driver_add(movementType, axis)
        edriver.driver.type = 'SCRIPTED'
        edriver.driver.expression = fn
        return edriver
    #
    def setDirection(self, context):
        u.getSelectedCharacterName()
        ob = bpy.data.objects.get(u.strName)
		# bpy.props.needsUpdating = True
        if(hasattr(bpy.types.WindowManager, "direction")):
            u.direction = math.radians(bpy.context.window_manager.direction)
        bpy.data.objects[u.strName].rotation_euler.z = u.direction

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# End Utility Class   End of generic code.
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# |
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# COMMON FUNCTION - addCharactersPr0perties
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def addCharactersProperties(self, context):
    winMan = bpy.types.WindowManager
    for obj in bpy.context.scene.objects:
        if(obj.name.startswith("rgbiped")):  # BIPED
            if(not hasattr(winMan, "Cycle")):
                winMan.cycle = bpy.props.FloatProperty(update=u.setHorizontalSpeed, name="cycle", default=1.0)
            if(not hasattr(winMan, "Speed")):
                winMan.speed = bpy.props.FloatProperty(update=u.setHorizontalSpeed, name="speed", default=0.0)
            if(not hasattr(winMan, "Direction")):
                winMan.direction = bpy.props.FloatProperty(update=u.setDirection, name="Direction", default=0.0)
            if(not hasattr(winMan, "xlocation")):
                winMan.xlocation = bpy.props.FloatProperty(update=u.setLocation, name="xlocation", default=0.0)
            if(not hasattr(winMan, "ylocation")):
                winMan.ylocation = bpy.props.FloatProperty(update=u.setLocation, name="ylocation", default=0.0)
            if(not hasattr(winMan, "zlocation")):
                winMan.zlocation = bpy.props.FloatProperty(update=u.setLocation, name="zlocation", default=1.04)
            if(not hasattr(winMan, "cycle")):
                winMan.cycle = bpy.props.FloatProperty(update=bipedFns.setBipedWalk, name="Cycle", default=1.0)
            if(not hasattr(winMan, "swayLR")):
                winMan.swayLR = bpy.props.FloatProperty(update=bipedFns.setSwayLR, name="Sway LR", default=1.0)
            if(not hasattr(winMan, "swayFB")):
                winMan.swayFB = bpy.props.FloatProperty(update=bipedFns.setSwayFB, name="Sway FB", default=0.0)
            if(not hasattr(winMan, "bounce")):
                winMan.bounce = bpy.props.FloatProperty(update=bipedFns.setBounce, name="Bounce", default=0.1)
            if(not hasattr(winMan, "legSpread")):
                winMan.legSpread = bpy.props.FloatProperty(update=bipedFns.setLegSpread, name="Leg Spread", default=0.0)
            if(not hasattr(winMan, "legArch")):
                winMan.legArch = bpy.props.FloatProperty(update=bipedFns.setLegArch, name="Leg Arch", default=0.0)
            if(not hasattr(winMan, "hipRotate")):
                winMan.hipRotate = bpy.props.FloatProperty(update=bipedFns.setHip, name="Hip Rotate", default=2.0)
            if(not hasattr(winMan, "hipSway")):
                winMan.hipSway = bpy.props.FloatProperty(update=bipedFns.setHip, name="Hip Sway", default=0.0)
            if(not hasattr(winMan, "hipUD")):
                winMan.hipUD = bpy.props.FloatProperty(update=bipedFns.setHip, name="HipUD", default=2.0)
            if(not hasattr(winMan, "skate")):
                winMan.skate = bpy.props.FloatProperty(update=bipedFns.setSkate, name="Skate", default=0.0)
            if(not hasattr(winMan, "armsUD")):
                winMan.armsUD = bpy.props.FloatProperty(update=bipedFns.setArms, name="ArmsUD", default=0.0)
            if(not hasattr(winMan, "shoulderRotate")):
                winMan.shoulderRotate = bpy.props.FloatProperty(update=bipedFns.setShoulder, name="Shoulder Rotate", default=3.0)
            if(not hasattr(winMan, "shoulderUD")):
                winMan.shoulderUD = bpy.props.FloatProperty(update=bipedFns.setShoulder, name="ShoulderUD", default=3.0)
            if(not hasattr(winMan, "armTwistL")):
                winMan.armTwistL = bpy.props.FloatProperty(update= bipedFns.setArmTwistL, name="L Arm Twist", default=0.0)
            if(not hasattr(winMan, "armTwistR")):
                winMan.armTwistR = bpy.props.FloatProperty(update= bipedFns.setArmTwistR, name="R Arm Twist", default=0.0)
            if(not hasattr(winMan, "armRotation")):
                winMan.armRotation = bpy.props.FloatProperty(update=bipedFns.setArmRotation, name="Arm Rotation", default=3.0)
            if(not hasattr(winMan, "LHandSpread")):
                winMan.LHandSpread = bpy.props.FloatProperty(update=bipedFns.setLHand, name="LHand Spread", default=0.0)
            if(not hasattr(winMan, "LHandOC")):
                winMan.LHandOC = bpy.props.FloatProperty(update=bipedFns.setLHand, name="LHandOC", default=0.0)
            if(not hasattr(winMan, "RHandSpread")):
                winMan.RHandSpread = bpy.props.FloatProperty(update=bipedFns.setRHand, name="RHand Spread", default=0.0)
            if(not hasattr(winMan, "RHandOC")):
                winMan.RHandOC = bpy.props.FloatProperty(update=bipedFns.setRHand, name="RHandOC", default=0.0)
            if(not hasattr(winMan, "headUD")):
                winMan.headUD = bpy.props.FloatProperty(update=bipedFns.setHead, name="HeadUD", default=0.0)
            if(not hasattr(winMan, "headLR")):
                winMan.headLR = bpy.props.FloatProperty(update=bipedFns.setHead, name="HeadLR", default=0.0)
            if(not hasattr(winMan, "headTurn")):
                winMan.headTurn = bpy.props.FloatProperty(update=bipedFns.setHead, name="HeadTurn", default=0.0)
            if(not hasattr(winMan, "jawOC")):
                winMan.jawOC = bpy.props.FloatProperty(update=bipedFns.setJaw, name="JawOC", default=0.0)
            if(not hasattr(winMan, "eyeLR")):
                winMan.eyeLR = bpy.props.FloatProperty(update=bipedFns.setEye, name="EyeLR", default=0.0)
            if(not hasattr(winMan, "eyeUD")):
                winMan.eyeUD = bpy.props.FloatProperty(update=bipedFns.setEye, name="EyeUD", default=0.0)
            if(not hasattr(winMan, "femurJ1RP")):
                winMan.femurJ1RP = bpy.props.FloatProperty(update=bipedFns.setBipedWalk, name="femurJ1RP", default=0.0)
            if(not hasattr(winMan, "femurJ1RR")):
                winMan.femurJ1RR = bpy.props.FloatProperty(update=bipedFns.setBipedWalk, name="femurJ1RR", default=1.0)
            if(not hasattr(winMan, "tibiaJ1RP")):
                winMan.tibiaJ1RP = bpy.props.FloatProperty(update=bipedFns.setBipedWalk, name="tibiaJ1RP", default=0.0)
            if(not hasattr(winMan, "tibiaJ1RR")):
                winMan.tibiaJ1RR = bpy.props.FloatProperty(update=bipedFns.setBipedWalk, name="tibiaJ1RR", default=1.0)
            if(not hasattr(winMan, "ankleRP")):
                winMan.ankleRP = bpy.props.FloatProperty(update=bipedFns.setBipedWalk, name="ankleRP", default=0.0)
            if(not hasattr(winMan, "ankleRR")):
                winMan.ankleRR = bpy.props.FloatProperty(update=bipedFns.setBipedWalk, name="ankleRR", default=1.0)
            if(not hasattr(winMan, "toesRP")):
                winMan.toesRP = bpy.props.FloatProperty(update=bipedFns.setBipedWalk, name="toesRP", default=-0.0)
            if(not hasattr(winMan, "toesRR")):
                winMan.toesRR = bpy.props.FloatProperty(update=bipedFns.setBipedWalk, name="toesRR", default=1.0)          
                #
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# END COMMON FUNCTION - addCharactersPr0perties
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Common panel for all characters and appendages.
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
        u.getCharacterPanel()
        bpy.ops.object.mode_set(mode='OBJECT')
        return{'FINISHED'}

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# END of Common panel for all characters and appendages.
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# |
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# CHARACTERS CLASSES: Character Creation Panel
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
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
        bpy.context.object.pose.bones["armJ1.L"].rotation_euler[2] = -1.57
        bpy.context.object.pose.bones["armJ1.R"].rotation_euler[2] = 1.57
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
        bipedFns.setBipedWalk(self, context)
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
        bipedFns.setRun(self, context)
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
        if(u.toggleArmAction == True):
            #u.setWalk()  Below is  not likely to work
            bipedFns.setArmRotation(self, context)
        else:
            bipedFns.unSetArmRotation(self, context)
        u.toggleArmAction = not u.toggleArmAction
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
        if(u.toggleLegAction == True):
            bipedFns.setBipedWalk()
        else:
            bipedFns.unSetLegRotation(self, context)
        bpy.ops.object.mode_set(mode='OBJECT')
        u.toggleLegAction = not u.toggleLegAction
        return{'FINISHED'}

class Reset_btn(bpy.types.Operator):
    '''Revert To Default Settings'''
    bl_idname = "object.reset_btn"
    bl_label = "Reset Advanced Controls"
    bl_description = "Reset Advanced Controls"
    bl_options = {"REGISTER", "UNDO"}
    hidden = False
    def execute(self, context):
        bipedFns.revertAdvancedControls(self, context)
        bpy.ops.object.mode_set(mode='OBJECT')
        return{'FINISHED'}

class CONTROL_PT_Panel(bpy.types.Panel):
    #bl_idname = "object.CONTROL_PT_Panel"
    bl_label = "Character Control"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Animator'
    bl_context = "objectmode"
    def draw(self, context):
        layout = self.layout
        layout.row().operator("object.biped_build_btn")  # Build Biped
        layout.row().operator("object.pose_btn")  # Pose Character (Common to all)
        layout.row().operator("object.drop_arms_btn")  # Drop Arms
        layout.row().operator("object.walk_btn")  # Set Walk
        layout.row().operator("object.run_btn")  # Set Run
        layout.row().operator("object.arm_action_btn")  # Activate Arms
        layout.row().operator("object.leg_action_btn")  # Activate Arms
        layout.row().operator("object.reset_btn")  # Revert Advanced Controls
        layout.row().operator("object.control_btn") # Character controls
        # Pop-up
        
class Biped(UtilsFns):
    bl_label = "bipedUtils"
    bl_description = "biped"
    bl_options = {"REGISTER", "UNDO"}
    def setBipedPropertiesPanel():
        CONTROL_PT_Panel

class WM_OT_control(bpy.types.Operator):
    bl_idname = "object.control_btn"
    """Control Dialog box"""
    bl_label = "Controls Dialog Box"
    ob = bpy.context.object

    #winMan.speed = bpy.props.FloatProperty( name="speed", update=u.setHorizontalSpeed, default=0.0)
    speed : bpy.props.FloatProperty(name="speed:")
    direction : bpy.props.FloatProperty(name= "direction:")
    xlocation : bpy.props.FloatProperty(name= "xlocation:")
    ylocation : bpy.props.FloatProperty(name= "ylocation:")
    zlocation : bpy.props.FloatProperty(name= "zlocation:")
    swayLR : bpy.props.FloatProperty(name= "swayLR:")
    swayFB : bpy.props.FloatProperty(name= "swayFB:")
   
    def execute(self, context):
	    u = UtilsFns
	    ob = bpy.context.object
		u.speed = self.speed
		u.setHorizontalSpeed(self, context)
        ob.rotation_euler.z = radians(self.direction)
        ob.location.x = self.xlocation
        ob.location.y = self.ylocation
        ob.location.z = self.zlocation + u.bipedHeight
		u.setLocation(self, context)
        u.swayLR = self.swayLR
        return {'FINISHED'}
   
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# END CHARACTERS CLASS
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# COMMON FUNCTION - bui1dHumanUpperBody     To 1779
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def buildHumanUpperBody(at, V_bBackJ1 = (0, 0, 0.1)):
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["join"].select_head=True
    # V_bBackJ1 = (0, 0, 0.1)  Now passed in via parameter
    u.boneMirror(at, V_bBackJ1, False)
    V_bBackJ2 = (0, 0, 0.1)
    u.boneMirror(at, V_bBackJ2, False)
    V_bBackJ3 = (0, 0, 0.14)
    u.boneMirror(at, V_bBackJ3, False)
    V_bBackJ4 = (0, 0, 0.1)
    u.boneMirror(at, V_bBackJ4, False)
    V_bBackJ5 = (0, 0, 0.1)
    u.boneMirror(at, V_bBackJ5, False)
    at.edit_bones["join.001"].name = "bBackJ1"
    at.edit_bones["join.002"].name = "bBackJ2"
    at.edit_bones["join.003"].name = "bBackJ3"
    at.edit_bones["join.004"].name = "bBackJ4"
    at.edit_bones["join.005"].name = "bBackJ5"
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Start arms  
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Shoulder area
    V_clavicle = (.11, 0, -.02)
    u.boneMirror(at, V_clavicle, True)
    V_shoulder = (.19, 0, -.03)
    u.boneMirror(at, V_shoulder, True)
    V_armJ1 = (.12, 0, 0)
    u.boneMirror(at, V_armJ1, True)
    V_armJ2 = (.14, 0, -.01)
    u.boneMirror(at, V_armJ2, True)
    V_armJ3 = (.08, 0, 0)
    u.boneMirror(at, V_armJ3, True)
    V_armJ4 = (.1, 0, 0)
    u.boneMirror(at, V_armJ4, True)
    V_armJ5 = (.1, 0, 0)
    u.boneMirror(at, V_armJ5, True)
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
    u.boneMirror(at, V_wristBase2, True)
    V_midJ1 = (.046, 0, 0)
    u.boneMirror(at, V_midJ1, True)
    V_midJ2 = (.04, 0, 0)
    u.boneMirror(at, V_midJ2, True)
    V_midJ3 = (.02, 0, 0)
    u.boneMirror(at, V_midJ3, True)
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
    u.boneMirror(at, V_wristBase1, True)
    V_indexJ1 = (.032, .011, 0)
    u.boneMirror(at, V_indexJ1, True)
    V_indexJ2 = (.024, .01, 0)
    u.boneMirror(at, V_indexJ2, True)
    V_indexJ3 = (.02, .008, 0)
    u.boneMirror(at, V_indexJ3, True)
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
    u.boneMirror(at, V_wristBase3, True)
    V_ringJ1 = (.042, -.01, 0)
    u.boneMirror(at, V_ringJ1, True)
    V_ringJ2 = (.032, -.007, 0)
    u.boneMirror(at, V_ringJ2, True)
    V_ringJ3 = (.02, -.004, 0)
    u.boneMirror(at, V_ringJ3, True)
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
    u.boneMirror(at, V_pinkyBase, True)
    V_pinkyJ1 = (.024, -.016, 0)
    u.boneMirror(at, V_pinkyJ1, True)
    V_pinkyJ2 = (.02, -.012, 0)
    u.boneMirror(at, V_pinkyJ2, True)
    V_pinkyJ3 = (.02, -.01, 0)
    u.boneMirror(at, V_pinkyJ3, True)
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
    u.boneMirror(at, V_thumbBase, True)
    V_thumbJ1 = (.038, .044, -0.01)
    u.boneMirror(at, V_thumbJ1, True)
    V_thumbJ2 = (.032, .02, -0.006)
    u.boneMirror(at, V_thumbJ2, True)
    V_thumbJ3 = (.02, .01, 0)
    u.boneMirror(at, V_thumbJ3, True)
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
    u.boneMirror(at, V_neckJ1, False)
    V_neckJ2 = (0, 0, 0.03)
    u.boneMirror(at, V_neckJ2, False)
    V_neckJ3 = (0, 0, 0.03)
    u.boneMirror(at, V_neckJ3, False)
    V_neckJ4 = (0, 0, 0.03)
    u.boneMirror(at, V_neckJ4, False)
    V_headBase = (0, 0, 0.09)
    u.boneMirror(at, V_headBase, False)
    V_eyeLevel = (0, 0, .04)
    u.boneMirror(at, V_eyeLevel, False)
    V_headTop = (0, -.05, 0)
    u.boneMirror(at, V_headTop, False)
    V_headFore = (0, .08, .09)
    u.boneMirror(at, V_headFore, False)
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
    u.boneMirror(at, V_jaw, False)
    V_jaw1 = (.06, .02, 0)
    u.boneMirror(at, V_jaw1, True)
    V_jaw2 = (-.05, .1, 0)
    u.boneMirror(at, V_jaw2, True)
    at.edit_bones['neckJ4.001'].name = "jaw"
    at.edit_bones['neckJ4.001_R'].name = "jaw1.L"
    at.edit_bones['neckJ4.001_L'].name = "jaw1.R"
    at.edit_bones['neckJ4.001_R.001'].name = "jaw2.L"
    at.edit_bones['neckJ4.001_L.001'].name = "jaw2.R"
    # upperMouth
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["neckJ4"].select_tail=True
    V_baseMouth1 = (0, .026, 0.046) 
    u.boneMirror(at, V_baseMouth1, False)
    V_baseMouth2 = (.06, .02, 0)
    u.boneMirror(at, V_baseMouth2, True)
    V_baseMouth3 = (-.05, .11, -.004)
    u.boneMirror(at, V_baseMouth3, True)
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
    u.boneMirror(at, V_eyebase, True)
    V_eye = (0, 0.03, 0)
    u.boneMirror(at, V_eye, True)
    at.edit_bones['eyeLevel_L'].name = "eyeBase.L"
    at.edit_bones['eyeLevel_R'].name = "eyeBase.R"
    at.edit_bones['eyeLevel_L.001'].name = "eye.L"
    at.edit_bones['eyeLevel_R.001'].name = "eye.R"
    # nose
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["headBase"].select_tail=True
    V_noseBase = (0, .138, 0)
    u.boneMirror(at, V_noseBase, False)
    V_nose = (0, 0.02, -.02)
    u.boneMirror(at, V_nose, False)
    at.edit_bones['headBase.001'].name = "noseBase"
    at.edit_bones['headBase.002'].name = "nose"
    #
    # Add front fix
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["bBackJ5"].select_tail=True
    V_fixChestFront = (0, .06, -.03)
    u.boneMirror(at, V_fixChestFront, False)    
    V_fixChestFront1 = (0.185, 0, -.1)
    u.boneMirror(at, V_fixChestFront1, True)
    V_fixChestFront2 = (-.04, 0, -.12)
    u.boneMirror(at, V_fixChestFront2, True)
    at.edit_bones['bBackJ5.001'].name = "fixChestFront"
    at.edit_bones['bBackJ5.001_R'].name = "fixChestFront1.L"
    at.edit_bones['bBackJ5.001_L'].name = "fixChestFront1.R"
    at.edit_bones['bBackJ5.001_R.001'].name = "fixChestFront2.L"
    at.edit_bones['bBackJ5.001_L.001'].name = "fixChestFront2.R"
    # Add center fix
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["bBackJ5"].select_tail=True
    V_fixChestCenter1 = (0.19, 0, -.13)
    u.boneMirror(at, V_fixChestCenter1, True)
    V_fixChestCenter2 = (-.05, 0, -.12)
    u.boneMirror(at, V_fixChestCenter2, True)
    at.edit_bones['bBackJ5_R'].name = "fixChestCenter1.L"
    at.edit_bones['bBackJ5_L'].name = "fixChestCenter1.R"
    at.edit_bones['bBackJ5_R.001'].name = "fixChestCenter2.L"
    at.edit_bones['bBackJ5_L.001'].name = "fixChestCenter2.R"
    # Add rear fix
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["bBackJ5"].select_head=True
    V_fixChestBack = (0, -.06, 0)
    u.boneMirror(at, V_fixChestBack, False)    
    V_fixChestBack1 = (0.195, 0, -.02)
    u.boneMirror(at, V_fixChestBack1, True)
    V_fixChestBack2 = (-.06, 0, -.12)
    u.boneMirror(at, V_fixChestBack2, True)
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
    u.boneMirror(at, V_fixUpperShoulder1, False)
    V_fixUpperShoulder2 = (0.195, 0, -.02)
    u.boneMirror(at, V_fixUpperShoulder2, True)
    at.edit_bones['bBackJ5.001'].name = "fixShoulderBack.L"
    at.edit_bones['bBackJ5.001_R'].name = "fixShoulderBack1.L"
    at.edit_bones['bBackJ5.001_L'].name = "fixShoulderBack1.R"
    #
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# END COMMON FUNCTION - bui1dHumanUpperBody
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# COMMON FUNCTION - setEnve1opeWeights
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def setEnvelopeWeights():
    # The position of the following two for loops is important;
    # it initializes all bones to have a specific envelope weight
    # in case the bone has not been set manually as below. It 
    # cannot be placed afterwards, or it will override the settings.
    for b in bpy.data.objects[u.strName].pose.bones:
        b.rotation_mode = 'XYZ'
    for b in bpy.context.object.data.edit_bones:
        b.envelope_distance = 0.05  # Default envelope distance
        b.head_radius = 0.02
        b.tail_radius = 0.02
        #b.envelope_weight = 2.0
    #
    name = u.strName.replace("rg", "")
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
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# END FUNCTIONS FOR COMMON SHARED PARTS IN CHARACTERS
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# |
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Start Build Biped Skeleton      ENDS 2233
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def buildBipedSkeleton():
    biped = Biped # instantiated, but does not need to return to any other function
    # Initiate building of bones
    n = u.getSceneObjectNumber()  # Each character name will be numbered sequentially.
    u.strName = u.setName('biped', n)
    mod = math.fmod(n, 2)
    if(mod == 0):
        x = 1.1 * n - mod
    else:
        x = 1.1 * -n - mod
    y = -.4 * n; z = 1.04  # bui1dRootArmature(type, strCharName, x, y, z) type is the character class
    at = u.buildRootArmature(biped, u.strName, x, y, z) # Start character armature and bones
    Vtail = [0.0, -0.3, .3]  # End location of handle relative to armature origin - this effects coordinate system
    bone = u.setHandle(at, u.strName, Vtail)
    bpy.data.objects[u.strName].show_in_front = True
    #
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Biped Skeleton LOWER BODY BUILD
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    V_origin = (0, 0, 0)
    V_join = (0, 0, -.13)
    join = u.createBone("join", V_origin, V_join, 0)
    join.parent = at.edit_bones[u.strName + '_bone']
    #
    # start mirroring! 
    V_hip = (.12, 0, 0)
    u.boneMirror(at, V_hip, True)
    V_femurJ1 = (0, 0, -.23)
    u.boneMirror(at, V_femurJ1, True)
    V_femurJ2 = (0, 0, -.24)
    u.boneMirror(at, V_femurJ2, True)
    V_tibiaJ1 = (0, 0, -.2)
    u.boneMirror(at, V_tibiaJ1, True)
    V_tibiaJ2 = (0, 0, -.14)
    u.boneMirror(at, V_tibiaJ2, True)
    V_ankle = (0, .18, -.06)
    u.boneMirror(at, V_ankle, True)
    V_toe = (0, .08, 0)
    u.boneMirror(at, V_toe, True)
    at.edit_bones["join_L"].name = "hip.R"
    at.edit_bones['join_R'].name = "hip.L"
    at.edit_bones['join_R.001'].name = "femurJ1.L"
    at.edit_bones['join_L.001'].name = "femurJ1.R"
    at.edit_bones['join_R.002'].name = "femurJ2.L"
    at.edit_bones['join_L.002'].name = "femurJ2.R"
    at.edit_bones['join_R.003'].name = "tibiaJ1.L"
    at.edit_bones['join_L.003'].name = "tibiaJ1.R"    
    at.edit_bones['join_R.004'].name = "tibiaJ2.L"
    at.edit_bones['join_L.004'].name = "tibiaJ2.R"    
    at.edit_bones['join_R.005'].name = "ankle.L"
    at.edit_bones['join_L.005'].name = "ankle.R"
    at.edit_bones['join_R.006'].name = "toe.L"
    at.edit_bones['join_L.006'].name = "toe.R"
    #
    # Heel starts were the tibia ends, same place as the ankle bone
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["ankle.L"].select_tail=True
    at.edit_bones["ankle.R"].select_tail=True
    V_heel = (0, -.2, -.01)
    u.boneMirror(at, V_heel, True)
    at.edit_bones['ankle.L.001'].name = "heel.L"
    at.edit_bones['ankle.R.001'].name = "heel.R"
    #
    #
    bpy.ops.armature.select_all(action='DESELECT')
    V_origin = (0, 0, 0)
    V_posterior = (0, -.1, -.04)
    posterior = u.createBone("fixPosterior", V_origin, V_posterior, 0)
    posterior.parent = at.edit_bones[u.strName + '_bone']
    V_posterior1 = (-.12, 0, -.01)
    u.boneMirror(at, V_posterior1, True)
    V_posterior2 = (0, 0, -.14)
    u.boneMirror(at, V_posterior2, True)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["fixPosterior"].select_tail=True
    V_tailBone = (0, 0, -.14)
    u.boneMirror(at, V_tailBone, False)
    at.edit_bones['fixPosterior_L'].name = "fixPosterior1.L"
    at.edit_bones['fixPosterior_R'].name = "fixPosterior1.R"
    at.edit_bones['fixPosterior_L.001'].name = "fixPosterior2.L"
    at.edit_bones['fixPosterior_R.001'].name = "fixPosterior2.R"
    at.edit_bones['fixPosterior.001'].name = "fixPosterior2.C"
    #
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # END OF Biped Skeleton LOWER BODY BUILD
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #
    buildHumanUpperBody(at)
    setEnvelopeWeights()
    # 
    biped.armature = at
    u.deselectAll()
    ob = bpy.data.objects.get(u.strName)
    #bpy.context.scene.objects.active = ob
    context.view_layer.objects.active = ob
    ob.select_set(True)
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #  END BIPED SKELETON BUILD
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# End Build Skeleton Functions
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# |
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Start Character Operations Functions
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class BipedFns(object):
    bl_label = "bipedFns"
    bl_description = "bipedfunctions"
    bl_options = {"REGISTER", "UNDO"}
    def setCycleRates(self, context):
        u.getSelectedCharacterName()
        u.cycle = 8.0  # Default cycle
        if(hasattr(bpy.types.WindowManager, "cycle")):
            u.cycle = bpy.context.window_manager.cycle + 8
        #u.str1xCycle = "sin(radians(" + str(u.cycle) + "*frame))"  # cycle equation
        u.str1xCycle = 'clock()'
        u.strHalfCycle = "sin(radians(" + str(u.cycle / 2) + "*frame))"  # halfcyclespeed equation
        u.str2xCycle = "sin(radians(" + str(u.cycle * 2) + "*frame))" # Double Speed
        u.strQuadrupleCycleRate = "sin(radians(" + str(u.cycle * 4) + "*frame))"
        u.strCyclePhased = "sin(radians(-" + biped.phase + "+" + str(u.cycle) + "*frame))"
    #
    # The only reason for using this function is to get the currently 
    # selected character name and apply the correct functions.
    def setWalk():
        u.getSelectedCharacterName()
        if(u.strName.startswith("rgbiped")):
            bipedFns.setBipedWalk(self, context)
        else:
            print("A character must be selected to activate it!")
    #
    def setBipedWalk(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        u.getSelectedCharacterName()
        addCharactersProperties(self, context) # Create based on char type
        bipedFns.setCycleRates(self, context)
        # KEY: RP = Rotate Position  RR = Rotate Range
        if(hasattr(bpy.types.WindowManager, "femurJ1RP")):
            u.femurJ1RP = str(bpy.context.window_manager.femurJ1RP)
        if(hasattr(bpy.types.WindowManager, "femurJ1RR")):
            u.femurJ1RR = str(bpy.context.window_manager.femurJ1RR)
        femurJ1PP = "0.0" # Static pose position
        #
        RP = "+" + str(.1)
        fnL = "(" + u.str1xCycle + RP + ")" + u.str0AtFrame0
        u.setDriver(u.getEuler('femurJ1.L'), fnL, 0)
        fnR = "(-1*" + u.str1xCycle + RP + ")" + u.str0AtFrame0
        u.setDriver(u.getEuler('femurJ1.R'), fnR, 0)
        # tibiaJ1
        if(hasattr(bpy.types.WindowManager, "tibiaJ1RP")):
            u.tibiaJ1RP = str(bpy.context.window_manager.tibiaJ1RP)
        if(hasattr(bpy.types.WindowManager, "tibiaJ1RR")):
            u.tibiaJ1RR = str(bpy.context.window_manager.tibiaJ1RR)
        RP = "-" + str(.4)
        fnL = "(" + u.str1xCycle + RP + ")" + u.str0AtFrame0
        u.setAxisDriver(u.getEuler('tibiaJ1.L'), fnL, 0)
        fnR = "(-1*" + u.str1xCycle + RP + ")" + u.str0AtFrame0
        u.setAxisDriver(u.getEuler('tibiaJ1.R'), fnR, 0)
        # Ankles
        if(hasattr(bpy.types.WindowManager, "ankleRP")):
            u.ankleRP = str(bpy.context.window_manager.ankleRP)
        if(hasattr(bpy.types.WindowManager, "ankleRR")):
            u.ankleRR = str(bpy.context.window_manager.ankleRR)
        RP = "+" + str(.3)
        fnL = "(-1*" + u.str1xCycle + RP + ")" + u.str0AtFrame0
        u.setAxisDriver(u.getEuler('ankle.L'), fnL, 0)
        fnR = "(" + u.str1xCycle + RP + ")" + u.str0AtFrame0
        u.setAxisDriver(u.getEuler('ankle.R'), fnR, 0)
        # Toes
        if(hasattr(bpy.types.WindowManager, "toesRP")):
            u.toesRP = str(bpy.context.window_manager.toesRP)
        if(hasattr(bpy.types.WindowManager, "toesRR")):
            u.toesRR = str(bpy.context.window_manager.toesRR)
        RP = "+" + str(.1)
        fnL = "(-1*" + u.str1xCycle + RP + ")" + u.str0AtFrame0
        u.setAxisDriver(u.getEuler('toe.L'), fnL + u.str0AtFrame0, 0)
        fnR = "(" + u.str1xCycle + RP + ")" + u.str0AtFrame0
        u.setAxisDriver(u.getEuler('toe.R'), fnR + u.str0AtFrame0, 0)
        #
        # Upper Back
        RP = "*" + str(.4)
        fn = "(" + u.str1xCycle + RP + ")" + u.str0AtFrame0
        bBackJ4Driver = u.setDriver(u.getEuler('bBackJ4'), fn, 1)

        # Compensate for shoulder r0tate by rotating neck and head in opposite direction, in three parts
        RR = "*" + str(.13)
        fn = "(-1*" + u.str1xCycle + RR + ")" + u.str0AtFrame0
        neckJ2Driver = u.setDriver(u.getEuler('neckJ2'), fn, 1)
        neckJ3Driver = u.setDriver(u.getEuler('neckJ3'), fn, 1)
        neckJ4Driver = u.setDriver(u.getEuler('neckJ4'), fn, 1)
        # Arms rotation
        if(hasattr(bpy.types.WindowManager, "armRotation")):
            armRotation = str(bpy.context.window_manager.armRotation * .2)
        RR = "*" + str(1)
        fnL = "(" + u.str1xCycle + RR + ")" + u.str0AtFrame0
        u.setAxisDriver(u.getEuler('armJ1.L'), fnL, 0)
        fnR = "(-1*" + u.str1xCycle + RR + ")" + u.str0AtFrame0
        u.setAxisDriver(u.getEuler('armJ1.R'), fnR, 0)
        # Elbows
        RP = "-" + str(1.4)
        RR = "*" + str(.2)
        fnL = "(" + u.str1xCycle + RP + RR + ")" + u.str0AtFrame0
        u.setAxisDriver(u.getEuler('armJ3.L'), fnL, 0)
        fnR = "(-1*" + u.str1xCycle + RP + RR + ")" + u.str0AtFrame0
        u.setAxisDriver(u.getEuler('armJ3.R'), fnR, 0)
        #
        bpy.context.object.pose.bones["armJ1.L"].rotation_euler[2] = 1.57
        bpy.context.object.pose.bones["armJ1.R"].rotation_euler[2] = -1.57
        ob = bpy.data.objects.get(u.strName)		
        ob.select_set(True)
        biped = Biped
        biped.setBipedPropertiesPanel()
        bpy.context.scene.frame_set(0)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
    def unsetBipedWalk(self, context):
        u.getSelectedCharacterName()
        for b in bpy.data.objects[u.strName].pose.bones:
            b.driver_remove('rotation_euler', -1)
        #
    def setRun(self, context):
        u.getSelectedCharacterName()
        bipedFns.unsetBipedWalk(self, context)
        bpy.data.window_managers['WinMan'].cycle = 12
        bipedFns.setCycleRates(self, context)
        bpy.data.window_managers['WinMan'].hipRotate = 2.0
        bpy.data.window_managers['WinMan'].swayLR = 2.0
        bpy.data.window_managers['WinMan'].swayFB = 4.0
        bpy.data.window_managers['WinMan'].bounce = .3
        bpy.data.window_managers['WinMan'].hipUD = 2.0 
        bpy.data.window_managers['WinMan'].shoulderRotate = 8.0 
        bpy.data.window_managers['WinMan'].shoulderUD = 4.0 
        bpy.data.window_managers['WinMan'].armRotation = 3.0 
        bpy.data.window_managers['WinMan'].femurJ1RR = 2.6
        bpy.data.window_managers['WinMan'].tibiaJ1RP = .6 
        bpy.data.window_managers['WinMan'].tibiaJ1RR = 1.0
        bpy.data.window_managers['WinMan'].ankleRP = 0.0
        bpy.data.window_managers['WinMan'].toesRP = -.1
        bipedFns.setBipedWalk(self, context)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
    def unSetLegRotation(self, context):
        u.getSelectedCharacterName()
        undo = bpy.data.objects[u.strName].pose.bones['femurJ1.L']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['femurJ1.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['tibiaJ1.L']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['tibiaJ1.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['ankle.L']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['ankle.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['toe.L']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['toe.R']
        undo.driver_remove('rotation_euler', -1)
        #
    # This is for restoring advanced control defaults for each bone in the leg: 
    # RP = Rotate Position
    # RR = Rotate Range
    def revertAdvancedControls(self, context):
        bpy.data.window_managers["WinMan"].femurJ1RP = 0.0
        bpy.data.window_managers["WinMan"].femurJ1RR = 1.0
        bpy.data.window_managers["WinMan"].tibiaJ1RP = 0.0
        bpy.data.window_managers["WinMan"].tibiaJ1RR = 1.0
        bpy.data.window_managers["WinMan"].ankleRP = 0.0
        bpy.data.window_managers["WinMan"].ankleRR = 1.0
        bpy.data.window_managers["WinMan"].toesRP = 0.0        
        bpy.data.window_managers["WinMan"].toesRR = 1.0
        bipedFns.setBipedWalk(self, context)
        #
    def setArmRotation(self, context):
        u.getSelectedCharacterName()
        armRotation = '3.0'
        if(hasattr(bpy.types.WindowManager, "armRotation")):
            armRotation = str(bpy.context.window_manager.armRotation * .2)
        # Arms rotation
        fn = "-(asin(" + u.str1xCycle + ") * " + armRotation + ")/3.14"
        armJLDriver = u.setAxisDriver(u.getEuler('armJ1.L'), fn, 1)
        fn = "-(asin(" + u.str1xCycle + ") * " + armRotation + ")/3.14"
        armJRDriver = u.setAxisDriver(u.getEuler('armJ1.R'), fn, 1)
        # Elbows
        fn = "-((asin(" + u.str1xCycle + ") * " + armRotation + ")/3.14 + .3) * (frame*(1/(frame+.0001)))"
        radiusLDriver = u.setAxisDriver(u.getEuler('armJ3.L'), fn, 2)
        fn = "-((asin(" + u.str1xCycle + ") * " + armRotation + ")/3.14 - .3) * (frame*(1/(frame+.0001)))"
        radiusRDriver = u.setAxisDriver(u.getEuler('armJ3.R'), fn, 2)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
        #
    def unSetArmRotation(self, context):
        u.getSelectedCharacterName()
        undo = bpy.data.objects[u.strName].pose.bones['armJ1.L']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['armJ1.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['armJ3.L']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['armJ3.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['bBackJ4']
        undo.driver_remove('rotation_euler', -1)
        #        
        #
    def setSwayLR(self, context):  # left - right sway movement
        u.getSelectedCharacterName()
        swayLR = "1.0"
        if(hasattr(bpy.types.WindowManager, "swayLR")):
            u.swayLR = str(bpy.context.window_manager.swayLR)
        fn = "-(asin(" + u.str1xCycle + ")* " + u.swayLR + "*.01)"
        # bBackJ1
        u.setDriver(u.getEuler('bBackJ1'), fn, 2)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
    def setSwayFB(self, context):  # forward - backward sway movement
        u.getSelectedCharacterName()
        if(hasattr(bpy.types.WindowManager, "swayFB")):
            u.swayFB = str(bpy.context.window_manager.swayFB)
        fn = "-(asin(" + u.str1xCycle + ")* " + u.swayFB + "*.01)"
        u.setDriver(u.getEuler('bBackJ1'), fn, 0)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
    def setBounce(self, context):  # Bounce
        u.getSelectedCharacterName()
        bounce = "1.0"
        if(hasattr(bpy.types.WindowManager, "bounce")):
            u.bounce = str(bpy.context.window_manager.bounce)
        eqBounce = "-(asin(" + u.str1xCycle + ")* " + u.bounce + "*.01)"
        dr_Bounce = u.setDriver(u.getEuler(u.strName + '_bone'), eqBounce, 2, 'location') # Bounce
        bpy.ops.object.mode_set(mode='OBJECT')
        #        
    def setLegSpread(self, context): # Leg Spread
        u.getSelectedCharacterName()
        bpy.ops.object.mode_set(mode='POSE')
        if(hasattr(bpy.types.WindowManager, "legSpread")):
            u.legSpread = bpy.context.window_manager.legSpread 
        u.legSpread = -math.radians(u.legSpread)
        dr1 = u.setDriver(u.getEuler('femurJ1.L'), str(-u.legSpread), 2)
        dr2 = u.setDriver(u.getEuler('femurJ1.R'), str(u.legSpread), 2)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
        #
    def setLegArch(self, context):
        u.getSelectedCharacterName()
        if(hasattr(bpy.types.WindowManager, "legArch")):
            u.legArch = bpy.context.window_manager.legArch * .1  # Leg Arch
        fn = u.legArch
        u.setDriver(u.getEuler('femurJ1.L'), str(-fn), 1)
        u.setDriver(u.getEuler('femurJ1.R'), str(fn), 1)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
        #
    def setSkate(self, context):
        u.getSelectedCharacterName()
        skate = '0.0'
        if(hasattr(bpy.types.WindowManager, "skate")):
            u.skate = str(bpy.context.window_manager.skate*.06)
        fn = "-(asin(" + u.str1xCycle + ") * " + u.skate + ")/3.14"
        u.setAxisDriver(u.getEuler('femurJ1.L'), fn, 2)
        fn = "-(asin(" + u.str1xCycle + ") * " + u.skate + ")/3.14"
        u.setAxisDriver(u.getEuler('femurJ1.R'), fn, 2)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
        #
    # Head
    def setJaw(self, context): # Jaw open - close
        u.getSelectedCharacterName()
        u.jawOC = bpy.context.window_manager.jawOC * -.1
        u.rotate(u.strName, 'jaw', u.jawOC, 0)
        bpy.context.object.data.bones['jaw'].select  = True
        bpy.ops.object.mode_set(mode='POSE')
        #
        #
    # If centered at rear joint, parented, can be used  for eye movements
    def setEye(self, context):
        u.getSelectedCharacterName()
        u.eyeLR = bpy.context.window_manager.eyeLR * .1    # Left - Right turn motion 
        u.rotate(u.strName, 'eye.L', u.eyeLR, 2)
        u.rotate(u.strName, 'eye.R', u.eyeLR, 2)
        #
        u.eyeUD = bpy.context.window_manager.eyeUD * .1   # Eye up - down
        u.rotate(u.strName, 'eye.L', u.eyeUD, 0)
        u.rotate(u.strName, 'eye.R', u.eyeUD, 0)
        bpy.context.object.data.bones['eye.L'].select  = True
        bpy.context.object.data.bones['eye.R'].select  = True
        bpy.ops.object.mode_set(mode='POSE')
        #
    # Set Head Up - Down
    def setHead(self, context):
        u.getSelectedCharacterName()
        # Up - Down turn motion 
        if(hasattr(bpy.types.WindowManager, "headUD")):
            u.headUD = str(bpy.context.window_manager.headUD)
        fn = str(u.headUD)
        u.setAxisDriver(u.getEuler('neckJ2'), fn, 0)
        u.setAxisDriver(u.getEuler('neckJ3'), fn, 0)
        u.setAxisDriver(u.getEuler('neckJ4'), fn, 0)
        # Sideways motion 
        if(hasattr(bpy.types.WindowManager, "headLR")):
            u.headLR = str(bpy.context.window_manager.headLR)
        fn = str(u.headLR) + "* -.1"  
        u.setAxisDriver(u.getEuler('neckJ2'), fn, 2)
        u.setAxisDriver(u.getEuler('neckJ3'), fn, 2)
        u.setAxisDriver(u.getEuler('neckJ4'), fn, 2)
        # head turn
        if(hasattr(bpy.types.WindowManager, "headTurn")):
            u.headTurn = str(bpy.context.window_manager.headTurn * .1)
        fn = "-(asin(" + u.str1xCycle + ") * .2)/3.14 + " + u.headTurn
        neckJ2Driver = u.setAxisDriver(u.getEuler('neckJ2'), fn, 1)
        neckJ3Driver = u.setAxisDriver(u.getEuler('neckJ3'), fn, 1)
        neckJ4Driver = u.setAxisDriver(u.getEuler('neckJ4'), fn, 1)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
    def setArms(self, context):
        u.getSelectedCharacterName()
        armsUD = bpy.context.window_manager.armsUD
        armsUD = - math.radians(armsUD)
        u.rotate(u.strName, 'armJ1.L', armsUD, 0)
        u.rotate(u.strName, 'armJ1.R', armsUD, 0)
        bpy.context.object.data.bones['armJ1.L'].select  = True
        bpy.context.object.data.bones['armJ1.R'].select  = True
        bpy.ops.object.mode_set(mode='POSE')
        #
    def setArmTwistL(self, context):
        u.getSelectedCharacterName()
        armTwistL = bpy.context.window_manager.armTwistL  * -.1
        u.rotate(u.strName, 'armJ2.L', armTwistL, 1)
        u.rotate(u.strName, 'armJ3.L', armTwistL, 1)
        u.rotate(u.strName, 'armJ4.L', armTwistL, 1)
        u.rotate(u.strName, 'armJ5.L', armTwistL, 1)
        bpy.context.object.data.bones['armJ2.L'].select  = True
        bpy.context.object.data.bones['armJ3.L'].select  = True
        bpy.context.object.data.bones['armJ4.L'].select  = True
        bpy.context.object.data.bones['armJ5.L'].select  = True
        bpy.ops.object.mode_set(mode='POSE')
        #
    def setArmTwistR(self, context):
        u.getSelectedCharacterName()
        armTwistR = bpy.context.window_manager.armTwistR   * -.1
        u.rotate(u.strName, 'armJ2.R', armTwistR, 1)
        u.rotate(u.strName, 'armJ3.R', armTwistR, 1)
        u.rotate(u.strName, 'armJ4.R', armTwistR, 1)
        u.rotate(u.strName, 'armJ5.R', armTwistR, 1)
        bpy.context.object.data.bones['armJ2.R'].select  = True
        bpy.context.object.data.bones['armJ3.R'].select  = True
        bpy.context.object.data.bones['armJ4.R'].select  = True
        bpy.context.object.data.bones['armJ5.R'].select  = True
        bpy.ops.object.mode_set(mode='POSE')
        #
    def setLHand(self, context): # Left hand open - close
        u.getSelectedCharacterName()
        LHandOC = bpy.context.window_manager.LHandOC * -.1
        for i in range(1, 4):
            u.rotate(u.strName, 'indexJ' + str(i) + '.L', LHandOC, 0)
            u.rotate(u.strName, 'midJ' + str(i) + '.L', LHandOC, 0)
            u.rotate(u.strName, 'ringJ' + str(i) + '.L', LHandOC, 0)
            u.rotate(u.strName, 'pinkyJ' + str(i) + '.L', LHandOC, 0)
        LHandSpread = bpy.context.window_manager.LHandSpread + 10   # Left Hand spread
        index = (LHandSpread) * -.04 + .8  # Left hand spread
        u.rotate(u.strName, 'indexJ1.L', index, 2)
        ring = (LHandSpread) * .017 - .36  # Left hand spread
        u.rotate(u.strName, 'ringJ1.L', ring, 2)
        pinky = (LHandSpread) * .052 - 1.0 # Left hand spread
        u.rotate(u.strName, 'pinkyJ1.L', pinky, 2)
        for i in range(1, 4):
            bpy.context.object.data.bones['indexJ' + str(i) + '.L'].select  = True       
            bpy.context.object.data.bones['midJ' + str(i) + '.L'].select  = True
            bpy.context.object.data.bones['ringJ' + str(i) + '.L'].select  = True
            bpy.context.object.data.bones['pinkyJ' + str(i) + '.L'].select  = True
        bpy.ops.object.mode_set(mode='POSE')
        #
    def setRHand(self, context): # Right hand open - close
        u.getSelectedCharacterName()
        RHandOC = bpy.context.window_manager.RHandOC   * -.1
        for i in range(1, 4):
            u.rotate(u.strName, 'indexJ' + str(i) + '.R', RHandOC, 0)
            u.rotate(u.strName, 'midJ' + str(i) + '.R', RHandOC, 0)
            u.rotate(u.strName, 'ringJ' + str(i) + '.R', RHandOC, 0)
            u.rotate(u.strName, 'pinkyJ' + str(i) + '.R', RHandOC, 0)
        RHandSpread = bpy.context.window_manager.RHandSpread + 10
        index = (RHandSpread) * .04 - .8 # Right hand spread
        u.rotate(u.strName, 'indexJ1.R', index, 2)
        ring = (RHandSpread) * -.017 + .36 # Right hand spread
        u.rotate(u.strName, 'ringJ1.R', ring, 2)
        pinky = (RHandSpread) * -.052 + 1.0 # Right hand spread
        u.rotate(u.strName, 'pinkyJ1.R', pinky, 2)
        for i in range(1, 4):
            bpy.context.object.data.bones['indexJ' + str(i) + '.R'].select  = True       
            bpy.context.object.data.bones['midJ' + str(i) + '.R'].select  = True
            bpy.context.object.data.bones['ringJ' + str(i) + '.R'].select  = True
            bpy.context.object.data.bones['pinkyJ' + str(i) + '.R'].select  = True
        bpy.ops.object.mode_set(mode='POSE')
        #
    def setShoulder(self, context):
        u.getSelectedCharacterName()
        if(hasattr(bpy.types.WindowManager, "shoulderRotate")):
            u.shoulderRotate = str(bpy.context.window_manager.shoulderRotate*.1)
        # Upper Back
        fn = "(asin(" + u.str1xCycle + ") * " + shoulderRotate + ")/3.14"
        bBackJ4Driver = u.setDriver(u.getEuler('bBackJ4'), fn, 1)
        # Compensate for shoulder r0tate by rotating neck and head in opposite direction, in three parts
        fn = "-(asin(" + u.str1xCycle + ") * " + u.shoulderRotate + "/3)/3.14"
        neckJ2Driver = u.setDriver(u.getEuler('neckJ2'), fn, 1)
        neckJ3Driver = u.setDriver(u.getEuler('neckJ3'), fn, 1)
        neckJ4Driver = u.setDriver(u.getEuler('neckJ4'), fn, 1)
        # Shoulder up - down movement
        if(hasattr(bpy.types.WindowManager, "shoulderUD")):
            u.shoulderUD = str(bpy.context.window_manager.shoulderUD*.06)
        fn = "(asin(" + u.str1xCycle + ") * " + u.shoulderUD + ")/3.14"
        u.setDriver(u.getEuler('shoulder.L'), fn, 0)
        fn = "-(asin(" + u.str1xCycle + ") * " + u.shoulderUD + ")/3.14"
        u.setDriver(u.getEuler('shoulder.R'), fn, 0)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
    def setHip(self, context):
        u.getSelectedCharacterName()
        # Hip sway
        if(hasattr(bpy.types.WindowManager, "hipSway")):
            u.hipSway = str(bpy.context.window_manager.hipSway*.1)
        fn = "(asin(" + u.str1xCycle + ") * " + u.hipSway + ")/3.14"
        u.setDriver(u.getEuler('pelvis'), fn, 2) # was 0
        # Pelvis / Hip rotation    
        if(hasattr(bpy.types.WindowManager, "hipRotate")):
            u.hipRotate = str(bpy.context.window_manager.hipRotate*.1)
        fn = "(asin(" + u.str1xCycle + ") * " + u.hipRotate + ")/3.14"
        u.setDriver(u.getEuler('pelvis'), fn, 1)
        # hip up - down movement
        if(hasattr(bpy.types.WindowManager, "hipUD")):
            u.hipUD = str(bpy.context.window_manager.hipUD*.06)
        fn = "(asin(" + u.str1xCycle + ") * " + u.hipUD + ")/3.14"
        u.setDriver(u.getEuler('hip.L'), fn, 0)
        fn = "-(asin(" + u.str1xCycle + ") * " + u.hipUD + ")/3.14"
        u.setDriver(u.getEuler('hip.R'), fn, 0)
        bpy.ops.object.mode_set(mode='OBJECT')
        ob = bpy.data.objects.get(u.strName)
        # bpy.context.scene.objects.active = ob
        context.view_layer.objects.active = ob
        ob.select_set(True)
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# End of BipedFns CLASS
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# End Character Functions
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def register():
    from bpy.utils import register_class
    register_class(Biped_Build_Btn)
    register_class(Pose_Btn)
    register_class(Drop_Arms_Btn)
    register_class(Walk_Btn)
    register_class(Run_Btn)
    register_class(Arm_Action_Btn)
    register_class(Leg_Action_Btn)
    register_class(Reset_btn)
    #
    register_class(CONTROL_PT_Panel)
    bpy.utils.register_class(WM_OT_control)


def unregister():
    from bpy.utils import unregister_class
    unregister_class(Biped_Build_Btn)
    unregister_class(Pose_Btn)
    unregister_class(Drop_Arms_Btn)
    unregister_class(Walk_Btn)
    unregister_class(Run_Btn)
    unregister_class(Arm_Action_Btn)
    unregister_class(Leg_Action_Btn)
    unregister_class(Reset_btn)
    #
    unregister_class(CONTROL_PT_Panel)
    bpy.utils.unregister_class(WM_OT_control)

if __name__ == "__main__":
    register()

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# End Registration
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%	
u = UtilsFns
biped = Biped
bipedFns = BipedFns
