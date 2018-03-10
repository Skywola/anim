# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Coded by Shawn D Irwin September 2017 to ongoing . . . Open Source!
# Outline of Sections:
# Utils - Utility functions that are commonly used with all characters
# Start panel - Panel that shows character build buttons and activate button
# Character Classes - Character Classes.
# BuildSkeleton - Building character's rig
# CharacterFns - Functions used for individual characters, separated from each other
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
bl_info = {     
    "name": "Instant Animation",
    "author": "Shawn Irwin", 
    "location": "View3D > Tools > Instant Animation", 
    "version": (2, 0, 0), 
    "blender": (2, 7, 9), 
    "description": "Rapid automatic animation.", 
    "wiki_url": "http://tachufind.com/instan.htm", 
    "category": "Development" 
} 

import bpy, math
from bpy.types import Panel, Menu
from rna_prop_ui import PropertyPanel
context = bpy.context
bpy.context.scene.frame_start = 0
#
def linkObjectsToScene(rig):
    scn = bpy.context.scene
    scn.objects.link(rig)
    scn.objects.active = rig
    scn.update()
#
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Start Utility Class
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class Utils:
    strName = ""
    speed = 0.0
    direction = 0.0 
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
    wingsSpeed = 1.0
    wingsRP = 0.0
    wingsRR = 3.0
    wingsFB = 0.0
    wingsAxial = 0.0
    wingsCurveFB = 0.0
    wingsCurveUD = 0.0
    wingsInnerFeathers = 0.0
    wingsOuterFeathers = 0.0
    tailUD = 0.0
    tailLR = 0.0
    tailCurl = 0.0
    tailSpread = 0.0
    claws = 0
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
    # For adWings
    adWingsSpeed = 1.0
    adWingsRP = 0.0
    adWingsRR = 3.0
    adWingsFB = 0.0
    adWingsAxial = 0.0
    adWingsCurveFB = 0.0
    adWingsCurveUD = 0.0
    adWingsInner = 0.0
    adWingsOuter = 0.0
    strCycleRate = "sin(radians(" + str(cycle) + "*frame))"  # String form of cycle equation
    strHalfCycleRate = "sin(radians(" + str(cycle / 2) + "*frame))"  # String form of halfcyclespeed equation
    strDoubleCycleRate = "sin(radians(" + str(cycle * 2) + "*frame))" # Double Speed
    strx0AtFrame0 = " * (frame * (1/(frame+.0001)))"  # produce a zero at frame zero, otherwise a one
    strx1AtFrame0 = " * abs((frame/(frame + .0001))-1)"  # produce a one at frame zero, otherwise a zero
    phase = "0"
    strCyclePhased = "sin(radians(-" + str(phase) + "+" + str(cycle) + "*frame))"
    reinforce = True  # Option - Add extra bones for stabilization
    showNames = False  # Option - show bone names - for build only
    show_xray = True  # Option
    show_axes = False  # Option - Show armature axis - for build only
    # posEngine = "asin(" + strCycleRate + ")"
    # negEngine = "-asin(" + strCycleRate + ")"
    # frame = bpy.context.scene.frame_current  # This  may not be needed
    #
    #
    def buildRootArmature(type, strCharName, x, y, z):
        at = bpy.data.armatures.new(strCharName + '_at')  # at = Armature
        type.rig = bpy.data.objects.new(strCharName, at)  # rig = Armature object
        type.rig.show_x_ray = True
        type.x = x
        type.y = y
        type.rig.location = (x, y, z)  # Set armature location
        linkObjectsToScene(type.rig)
        return at
    #
    #
    def setHandle(at, strCharName, Vtail):
        bpy.ops.object.mode_set(mode='EDIT')
        bone = at.edit_bones.new(strCharName + '_bone')
        bone.head = (0.0, 0.0, 0.0)  # LOCAL COOLDINATE, [0,0,0] places bone directly on armature.
        bone.tail = Vtail
        return bone
    #
    #
    # increment rig number each time one is built.
    def getSceneObjectNumber():
        n = 0
        for ob in list(bpy.data.objects):
            if ob.name.startswith('rg') == True:
                n = n + 1
        return n
    #
    #
    # Options for character types -  biped, quadruped, bird, spider, dragon, kangaroo
    def setName(type, n):
        name = "rg" + type + "0" + str(n + 1)  # Assume n < 10 
        if (n > 9):  # Change x.name if previous assumption is wrong
            name = "rg" + type + str(n + 1)
        return name
    #    
    #
    # Rotate the easy way
    def rotate(bipedStrName, str_bone_name, rad=0, axis=0):
        bpy.ops.object.mode_set(mode='POSE')
        ob = bpy.context.object
        euler = ob.pose.bones[str_bone_name]
        euler.rotation_mode = 'XYZ'
        bpy.data.objects[bipedStrName].pose.bones[str_bone_name].rotation_euler[axis] = rad
    #
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
    #
    def boneMirror(at, vector, mirror=False): # Parameters - armature,  vector, mirroring
        bpy.data.armatures[at.name].use_mirror_x = mirror
        x = vector[0]; y = vector[1]; z = vector[2]
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.armature.extrude_forked(ARMATURE_OT_extrude={"forked":True}, TRANSFORM_OT_translate={"value":(x, y, z), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})
        b = bpy.context.object.data.bones.active
        return b
    #
    #
    # u.getEuler output represents:
    # bpy.data.objects['rg00biped'].pose.bones["backCenter"]
    def getEuler(str_bone_name):
        bpy.ops.object.mode_set(mode='POSE')
        ob = bpy.context.object
        euler = ob.pose.bones[str_bone_name]
        euler.rotation_mode = 'XYZ'
        return euler
    #
    #
    # Equation for bone joints, with euler transform, axis 0=x 1=y 2=z
    # Note also that fn must be inserted as a STLING in the expression!
    def setDriver(euler, fn="0", axis=0, movementType='rotation_euler'):
        eulerDriver = euler.driver_add(movementType)
        eulerDriver[axis].driver.type = 'SCRIPTED'
        eulerDriver[axis].driver.expression = fn
        return eulerDriver
    #
    #      
    # Set Driver For Single Axis Only:
    def setAxisDriver(euler, fn="0", axis=0, movementType='rotation_euler'):
        edriver = euler.driver_add(movementType, axis)
        edriver.driver.type = 'SCRIPTED'
        edriver.driver.expression = fn
        return edriver
    #
    #
    def deselectAll():
        # deselect all objects.
        bpy.ops.object.mode_set(mode='OBJECT')
        for ob in bpy.context.selected_objects:
            ob.select = False
    #
    #
    # This function does NOT use return, because otherwise it could over-write the current character
    # u.strName with the name of some unrelated selected object, that is not a character.
    def getSelectedCharacterName():
        name = ""
        n = 0
        for obj in bpy.context.selected_objects:
            n = n + 1
            if(obj.name.startswith("rg")):
                bpy.context.scene.objects.active = obj
                obj.select = True
                name = obj.name
                break
            if(obj.parent):
                parent = obj.parent
                if(parent.name.startswith("rg")):
                    obj.select = False
                    bpy.context.scene.objects.active = parent
                    parent.select = True
                    name = parent.name
                    break
        char = name.replace("rg", "")
        if(char.startswith("bird")):
            u.strName = name
        if(char.startswith("centaur")):
            u.strName = name
        if(char.startswith("quadruped")):
            u.strName = name
        if(char.startswith("biped")):
            u.strName = name
        if(char.startswith("spider")):
            u.strName = name
        # "wings" for the bird
        if(char.startswith("wings")):
            u.strName = name
        # "adWings" for the solo adWings
        if(char.startswith("adWings")):
            u.strName = name
        if(n == 0):
            print("*********************************************")
            print("No characters in scene!")
        if(name == ""):
            print("*********************************************")
            print("A character must be selected to activate it!")
            print("*********************************************")
            # print("name = " + name + "   char = " + char)
    #
    #
    def activateCharacter():
        u.getSelectedCharacterName()
        bpy.ops.object.mode_set(mode='OBJECT')
        name = u.strName.replace("rg", "")
        if(name.startswith("biped")):
            biped = Biped
            bipedFns.setBipedWalk(biped, context)
            biped.setBipedPropertiesPanel()
            bpy.utils.register_module(__name__)  # adds in panel
            bpy.context.scene.frame_set(0)
        if(name.startswith("bird")):
            bird = Bird
            birdFns.setWalk(bird, context)
            bird.setBirdPropertiesPanel()
            bpy.utils.register_module(__name__)  # adds in panel
            bpy.context.scene.frame_set(0)
        if(name.startswith("centaur")):
            centaur = Centaur
            centaurFns.setCentaurWalk(centaur, context)
            centaur.setCentaurPropertiesPanel()
            bpy.utils.register_module(__name__)  # adds in panel
            bpy.context.scene.frame_set(0)
        if(name.startswith("quadruped")):
            quadruped == Quadruped
            quadrupedFns.setQuadrupedWalk(quadruped, context)
            quadruped.setQuadrupedPropertiesPanel()
            bpy.utils.register_module(__name__)  # adds in panel
            bpy.context.scene.frame_set(0)
        if(name.startswith("spider")):
            spider = Spider
            spider.setSpiderPropertiesPanel()
            spiderFns.setSpiderWalk(spider, context)
            spider.setSpiderPropertiesPanel()
            bpy.utils.register_module(__name__)  # adds in panel
            bpy.context.scene.frame_set(0)
        # appendages that can be added to a character
        if(name.startswith("adWings")):
            wings = Wings
            wings.activateWingsPropertiesPanel()
            bpy.utils.register_module(__name__)  # adds in panel
            bpy.context.scene.frame_set(0)
        else:
            print("A character must be selected to activate it!")
#
    # Set horizontal speed and direction for all characters based on the handle x,y,z coordinates.
    def setHorizontalSpeed(self, context):
        u.getSelectedCharacterName()
        ob = bpy.data.objects.get(u.strName)
        if(hasattr(bpy.types.WindowManager, "direction")):
            u.direction = math.radians(bpy.context.window_manager.direction)
        bpy.data.objects[u.strName].rotation_euler.z = u.direction
        if(hasattr(bpy.types.WindowManager, "speed")):
            u.speed = bpy.context.window_manager.speed * .1
        strPosition = str(bpy.context.scene.frame_current / 2800 * u.speed)
        bpy.ops.object.mode_set(mode='POSE')
        z = bpy.data.objects[u.strName].pose.bones[u.strName + '_bone'].rotation_euler.z
        fnx = strPosition + "*frame * -cos(" + str(z) + ")"
        fny = strPosition + "*frame * -sin(" + str(z) + ")"
        char = u.strName.find('bird') + u.strName.find('biped') + 1
        if(char > -1):  # bird or biped
            u.setDriver(u.getEuler(u.strName + '_bone'), fnx, 1, 'location') # Horizontal handle x=LR y=FB z=UP
            u.setDriver(u.getEuler(u.strName + '_bone'), fny, 0, 'location') 
        char = u.strName.find('centaur') + u.strName.find('quadruped') + 1
        if(char > -1): # centaur or quadruped
            u.setDriver(u.getEuler(u.strName + '_bone'), fnx, 2, 'location') # Vertical handle x=LR z=FB y=UP
            u.setDriver(u.getEuler(u.strName + '_bone'), fny, 1, 'location') 
        char = u.strName.find('spider')
        if(char > -1): # spider
            u.setDriver(u.getEuler(u.strName + '_bone'), fnx, 2, 'location') # Vertical handle x=LR z=FB y=UP
            u.setDriver(u.getEuler(u.strName + '_bone'), fny, 0, 'location')
        bpy.ops.object.mode_set(mode='OBJECT')
        ob.select = True
#
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# End Utility Class   End of generic code.
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Common part of the panel that will show for all characters and appendages.
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def setCommonPanel():
    class Biped_Button(bpy.types.Operator):
        bl_idname = "b1.button"
        bl_label = "Build Biped"
        bl_description = "Build Biped"
        hidden = False
        def execute(self, context):
            buildBipedSkeleton()
            bpy.context.scene.frame_set(0)
            bpy.ops.object.mode_set(mode='OBJECT')
            return{'FINISHED'}
    #
    class Bird_Button(bpy.types.Operator):
        bl_idname = "b2.button"
        bl_label = "Build Bird"
        bl_description = "Build Bird"
        hidden = False
        def execute(self, context):
            buildBirdSkeleton()
            bpy.context.scene.frame_set(0)
            bpy.ops.object.mode_set(mode='OBJECT')
            return{'FINISHED'}
    #
    class Centaur_Button(bpy.types.Operator):
        bl_idname = "b3.button"
        bl_label = "Build Centaur"
        bl_description = "Build Centaur"
        hidden = False
        def execute(self, context):
            buildCentaurSkeleton()
            bpy.context.scene.frame_set(0)
            bpy.ops.object.mode_set(mode='OBJECT')
            return{'FINISHED'}
    #
    class Quadruped_Button(bpy.types.Operator):
        bl_idname = "b4.button"
        bl_label = "Build Quadruped"
        bl_description = "Build Quadruped"
        hidden = False
        def execute(self, context):
            buildQuadrupedSkeleton()
            bpy.context.scene.frame_set(0)
            bpy.ops.object.mode_set(mode='OBJECT')
            return{'FINISHED'}
    #
    class Spider_Button(bpy.types.Operator):
        bl_idname = "b5.button"
        bl_label = "Build Spider"
        bl_description = "Build Spider"
        hidden = False
        def execute(self, context):
            buildSpiderSkeleton()
            bpy.context.scene.frame_set(0)
            bpy.ops.object.mode_set(mode='OBJECT')
            return{'FINISHED'}
    # Start Appendages
    class Wings_Button(bpy.types.Operator):  
        bl_idname = "b6.button"
        bl_label = "Build Wings"
        bl_description = "Build Wings"
        hidden = False
        def execute(self, context):
            buildWings()
            bpy.context.scene.frame_set(0)
            bpy.ops.object.mode_set(mode='OBJECT')
            return{'FINISHED'}
    #
    class Activate_Button(bpy.types.Operator):
        bl_idname = "b7.button"
        bl_label = "Get Character Panel"
        bl_description = "Get Character Panel"
        hidden = False
        def execute(self, context):
            u.activateCharacter()
            bpy.ops.object.mode_set(mode='OBJECT')
            return{'FINISHED'}
    #
    class Pose_Button(bpy.types.Operator):
        bl_idname = "b8.button"
        bl_label = "Pose Character"
        bl_description = "Pose Character"
        hidden = False
        def execute(self, context):
            bpy.ops.screen.animation_cancel(restore_frame=True)
            bpy.context.scene.frame_set(0)
            bpy.ops.object.mode_set(mode='OBJECT')
            return{'FINISHED'}
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# END Common part of the panel that will show for all characters and appendages.
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# |
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Start Panel - Character Creation Panel
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
setCommonPanel()
#        
class Creation_Panel(bpy.types.Panel):
    bl_idname = "selected_object"
    bl_label = "Character Control Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Instant Animation'
    bl_context = "objectmode"
    def draw(self, context):
        layout = self.layout
        layout.row().operator("b1.button")  # Create Biped
        layout.row().operator("b2.button")  # Create Bird
        layout.row().operator("b3.button")  # Create Centaur
        layout.row().operator("b4.button")  # Create Quadruped
        layout.row().operator("b5.button")  # Create Spider
        layout.row().operator("b6.button")  # Create Wings
        layout.row().operator("b7.button")  # Create Activation Panel
        layout.row().operator("b8.button")  # Pose Character

def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# End of Start Panel - Character Creation Panel
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# |
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Character Classes: Create character properties and buttons panel
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class Biped(Utils):
    bl_idname = "object.biped"
    def setBipedPropertiesPanel():
        setCommonPanel() # Covers buttons 1-99 (Leaving room  for more appendages)
        # Start Character-specific Panel
        class Biped_Button(bpy.types.Operator):
            bl_idname = "b100.button"
            bl_label = "Drop Arms"
            bl_description = "Drop Character Arms"
            hidden = False
            def execute(self, context):
                bpy.context.object.pose.bones["armJ1.R"].rotation_euler[0] = -1.57
                bpy.context.object.pose.bones["armJ1.L"].rotation_euler[0] = -1.57
                bpy.ops.object.mode_set(mode='OBJECT')
                return{'FINISHED'}
    #
    #
        class Biped_Button(bpy.types.Operator):
            bl_idname = "b101.button"
            bl_label = "Pose Character"
            bl_description = "Pose Character"
            hidden = False
            def execute(self, context):
                bpy.context.object.pose.bones["armJ1.R"].rotation_euler[0] = 0
                bpy.context.object.pose.bones["armJ1.L"].rotation_euler[0] = 0
                bpy.ops.screen.animation_cancel(restore_frame=True)
                bpy.ops.object.mode_set(mode='OBJECT')
                return{'FINISHED'}
    #
    #    
        class Biped_Button(bpy.types.Operator):
            bl_idname = "b102.button"
            bl_label = "Set Walk"
            bl_description = "Set Walk"
            hidden = False
            def execute(self, context):
                bipedFns.revertAdvancedControls(self, context)
                bipedFns.setBipedWalk(self, context)
                bpy.ops.object.mode_set(mode='OBJECT')
                return{'FINISHED'} 
    #
    #
        class Biped_Button(bpy.types.Operator):
            bl_idname = "b103.button"
            bl_label = "Set Run"
            bl_description = "Set Run"
            hidden = False
            def execute(self, context):
                bipedFns.setRun(self, context)
                bpy.ops.object.mode_set(mode='OBJECT')
                return{'FINISHED'} 
    #
    #
        class Biped_Button(bpy.types.Operator):
            bl_idname = "b104.button"
            bl_label = "Deactivate Leg Movement"
            bl_description = "Deactivate Leg Movement"
            hidden = False
            def execute(self, context):
                bipedFns.unSetLegRotation(self, context)
                bpy.ops.object.mode_set(mode='OBJECT')
                return{'FINISHED'} 
    #
    #
        class Biped_Button(bpy.types.Operator):
            bl_idname = "b105.button"
            bl_label = "Activate Leg Movement"
            bl_description = "Activate Leg Movement"
            hidden = False
            def execute(self, context):
                bipedFns.setBipedWalk(self, context)
                bpy.ops.object.mode_set(mode='OBJECT')
                return{'FINISHED'}
    #
    #
        class Biped_Button(bpy.types.Operator):
            bl_idname = "b106.button"
            bl_label = "Deactivate Arm Movement"
            bl_description = "Deactivate Arm Movement"
            hidden = False
            def execute(self, context):
                bipedFns.unSetArmRotation(self, context)
                bpy.ops.object.mode_set(mode='OBJECT')
                return{'FINISHED'} 
    #
    #
        class Biped_Button(bpy.types.Operator):
            bl_idname = "b107.button"
            bl_label = "Activate Arm Movement"
            bl_description = "Activate Arm Movement"
            hidden = False
            def execute(self, context):
                bipedFns.setArmRotation(self, context)
                bpy.ops.object.mode_set(mode='OBJECT')
                return{'FINISHED'}
    #
    #
        class Biped_Button(bpy.types.Operator):
            bl_idname = "b108.button"
            bl_label = "Revert Advanced Controls"
            bl_description = "Revert Advanced Controls"
            hidden = False
            def execute(self, context):
                bipedFns.revertAdvancedControls(self, context)
                bpy.ops.object.mode_set(mode='OBJECT')
                return{'FINISHED'} 
    #
    #
        class Biped_Panel(bpy.types.Panel):
            bl_label = "Biped Control"
            bl_idname = "selected_object"
            bl_space_type = 'VIEW_3D'
            bl_region_type = 'TOOLS'
            bl_category = 'Instant Animation'
            bl_context = "objectmode"
            def draw(self, context):
                layout = self.layout
                layout.row().operator("b1.button")  # Build Biped
                layout.row().operator("b2.button")  # Build Bird
                layout.row().operator("b3.button")  # Build Centaur
                layout.row().operator("b4.button")  # Build Quadruped
                layout.row().operator("b5.button")  # Build Spider
                layout.row().operator("b6.button")  # Get Character Panel
                layout.row().operator("b7.button")  # Pose Character
                layout.row().operator("b8.button")  # Build Wings
                # End Common Panel, next button number starts with 100
                layout.row().prop(context.window_manager, 'speed')
                layout.row().prop(context.window_manager, 'direction')
                layout.row().prop(context.window_manager, 'cycle')
                layout.row().operator("b100.button")  # Drop Arms
                layout.row().operator("b101.button")  # Pose
                layout.row().operator("b102.button")  # Set Walk
                layout.row().operator("b103.button")  # Set Run
                layout.row().prop(context.window_manager, 'swayLR')
                layout.row().prop(context.window_manager, 'swayFB')
                layout.row().prop(context.window_manager, 'bounce')
                layout.row().prop(context.window_manager, 'legSpread')
                layout.row().prop(context.window_manager, 'legArch')
                layout.row().prop(context.window_manager, 'hipRotate')
                layout.row().prop(context.window_manager, 'hipSway')
                layout.row().prop(context.window_manager, 'hipUD')
                layout.row().prop(context.window_manager, 'skate')
                layout.row().operator("b104.button")  # Deactivate Arm Movement
                layout.row().operator("b105.button")  # Activate Arms
                layout.row().prop(context.window_manager, 'armsUD')
                layout.row().prop(context.window_manager, 'shoulderRotate')
                layout.row().prop(context.window_manager, 'shoulderUD')
                layout.row().prop(context.window_manager, 'armTwistL')
                layout.row().prop(context.window_manager, 'armTwistR')
                layout.row().prop(context.window_manager, 'armRotation')
                layout.row().operator("b106.button")  # Deactivate Arm Movement
                layout.row().operator("b107.button")  # Activate Arms
                layout.row().prop(context.window_manager, 'LHandSpread')
                layout.row().prop(context.window_manager, 'LHandOC')
                layout.row().prop(context.window_manager, 'RHandSpread')
                layout.row().prop(context.window_manager, 'RHandOC')
                layout.row().prop(context.window_manager, 'headUD')
                layout.row().prop(context.window_manager, 'headLR')
                layout.row().prop(context.window_manager, 'headTurn')
                layout.row().prop(context.window_manager, 'jawOC')
                layout.row().prop(context.window_manager, 'eyeLR')
                layout.row().prop(context.window_manager, 'eyeUD')
                layout.row().operator("b108.button")  # Revert Advanced Controls
                layout.row().prop(context.window_manager, 'femurJ1RP')
                layout.row().prop(context.window_manager, 'femurJ1RR')
                layout.row().prop(context.window_manager, 'tibiaJ1RP')
                layout.row().prop(context.window_manager, 'tibiaJ1RR')
                layout.row().prop(context.window_manager, 'ankleRP')
                layout.row().prop(context.window_manager, 'ankleRR')
                layout.row().prop(context.window_manager, 'toesRP')
                layout.row().prop(context.window_manager, 'toesRR')
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # END BIPED CLASS
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

class Bird(Utils):
    bl_idname = "object.bird"
    def setBirdPropertiesPanel():
        setCommonPanel() # Covers buttons 1-99 (Leaving room  for more appendages)
        # Start Character-specific Panel with button numbers starting at 100
        class Bird_Button(bpy.types.Operator):
            bl_idname = "b100.button"
            bl_label = "Clear Bird Walk"
            bl_description = "Clear Walk"
            hidden = False
            def execute(self, context):
                bpy.context.scene.frame_set(0)
                birdFns.unsetWalk(self, context)
                bpy.ops.object.mode_set(mode='OBJECT')
                return{'FINISHED'}
    #
        class Bird_Button(bpy.types.Operator):
            bl_idname = "b101.button"
            bl_label = "Set Bird Walk"
            bl_description = "Set Walk"
            hidden = False
            def execute(self, context):
                bpy.context.scene.frame_set(0)
                u.click = True
                birdFns.setWalk(self, context)
                u.click = False
                bpy.ops.object.mode_set(mode='OBJECT')
                return{'FINISHED'}
    #
        class Bird_Button(bpy.types.Operator):
            bl_idname = "b102.button"
            bl_label = "Set Bird Hop"
            bl_description = "Set Bird Hop"
            hidden = False
            def execute(self, context):
                u.click = True
                birdFns.setHop(self, context)
                u.click = False
                bpy.context.scene.frame_set(0)
                bpy.ops.object.mode_set(mode='OBJECT')
                return{'FINISHED'}
    #
        class Bird_Button(bpy.types.Operator):
            bl_idname = "b103.button"
            bl_label = "Set Bird Run"
            bl_description = "Set Bird Run"
            hidden = False
            def execute(self, context):
                u.click = True
                birdFns.setRun(self, context)
                u.click = False
                bpy.context.scene.frame_set(0)
                bpy.ops.object.mode_set(mode='OBJECT')
                return{'FINISHED'}
    #
        class Bird_Button(bpy.types.Operator):
            bl_idname = "b104.button"
            bl_label = "Activate Bird Wings"
            bl_description = "Activate Bird Wings"
            hidden = False
            def execute(self, context):
                activateWings(self, context)
                bpy.context.scene.frame_set(0)
                bpy.ops.object.mode_set(mode='OBJECT')
                return{'FINISHED'}
    #
        class Bird_Button(bpy.types.Operator):
            bl_idname = "b105.button"
            bl_label = "Fold Bird Wings"
            bl_description = "Fold Wings"
            hidden = False
            def execute(self, context):
                unSetWings(self, context)
                foldWings(self, context)
                bpy.context.scene.frame_set(0)
                return{'FINISHED'}
    #
        class Bird_Button(bpy.types.Operator):
            bl_idname = "b106.button"
            bl_label = "Clear Bird Wings"
            bl_description = "Clear Wings"
            hidden = False
            def execute(self, context):
                unSetWings(self, context)
                bpy.context.scene.frame_set(0)
                bpy.ops.object.mode_set(mode='OBJECT')
                return{'FINISHED'}
    #
        class Bird_Button(bpy.types.Operator):
            bl_idname = "b107.button"
            bl_label = "Revert Advanced Controls"
            bl_description = "Revert Advanced Controls"
            hidden = False
            def execute(self, context):
                birdFns.unSetWings(self, context)
                birdFns.revertAdvancedControls(self, context)
                bpy.context.scene.frame_set(0)
                bpy.ops.object.mode_set(mode='OBJECT')
                return{'FINISHED'} 
    #
        class Bird_Panel(bpy.types.Panel):
            bl_label = "Bird Control"
            bl_idname = "selected_object"
            bl_space_type = 'VIEW_3D'
            bl_region_type = 'TOOLS'
            bl_category = 'Instant Animation'
            bl_context = "objectmode"
            def draw(self, context):
                layout = self.layout
                layout.row().operator("b1.button")  # Build Biped
                layout.row().operator("b2.button")  # Build Bird
                layout.row().operator("b3.button")  # Build Centaur
                layout.row().operator("b4.button")  # Build Quadruped
                layout.row().operator("b5.button")  # Build Spider
                layout.row().operator("b6.button")  # Get Character Panel
                layout.row().operator("b7.button")  # Pose Character
                layout.row().operator("b8.button")  # Build Wings
                # End Common Panel, next button number starts with 100
                layout.row().prop(context.window_manager, 'speed')
                layout.row().prop(context.window_manager, 'direction')
                layout.row().prop(context.window_manager, 'cycle')
                layout.row().prop(context.window_manager, 'bounce')
                layout.row().prop(context.window_manager, 'swayLR')
                layout.row().prop(context.window_manager, 'swayFB')
                layout.row().operator("b100.button")  # Clear Walk
                layout.row().operator("b101.button")  # Set Walk
                layout.row().operator("b102.button")  # Set Hop
                layout.row().operator("b103.button")  # Set Run
                layout.row().prop(context.window_manager, 'neckFB')
                layout.row().prop(context.window_manager, 'legSpread')
                layout.row().operator("b104.button")  # Activate Wings
                layout.row().operator("b105.button")  # Fold Wings
                layout.row().operator("b106.button")  # Unfold Wings
                layout.row().prop(context.window_manager, 'wingsSpeed')
                layout.row().prop(context.window_manager, 'wingsRP')
                layout.row().prop(context.window_manager, 'wingsRR')
                layout.row().prop(context.window_manager, 'wingsAxial')
                layout.row().prop(context.window_manager, 'wingsFB')
                layout.row().prop(context.window_manager, 'wingsCurveFB')
                layout.row().prop(context.window_manager, 'wingsCurveUD')
                layout.row().prop(context.window_manager, 'wingsInnerFeathers')
                layout.row().prop(context.window_manager, 'wingsOuterFeathers')
                layout.row().prop(context.window_manager, 'tailUD')
                layout.row().prop(context.window_manager, 'tailRL')
                layout.row().prop(context.window_manager, 'tailSpread')
                layout.row().prop(context.window_manager, 'claws')
                layout.row().prop(context.window_manager, 'jawOC')
                layout.row().prop(context.window_manager, 'eyeLR')
                layout.row().prop(context.window_manager, 'eyeUD')
                layout.row().prop(context.window_manager, 'crestFB')
                layout.row().prop(context.window_manager, 'crestLR')
                layout.row().operator("b107.button")  # Revert Advanced Controls
                layout.row().prop(context.window_manager, 'femurJ1RP')
                layout.row().prop(context.window_manager, 'femurJ1RR')
                layout.row().prop(context.window_manager, 'tibiaJ1RP')
                layout.row().prop(context.window_manager, 'tibiaJ1RR')
                layout.row().prop(context.window_manager, 'ankleRP')
                layout.row().prop(context.window_manager, 'ankleRR')
                layout.row().prop(context.window_manager, 'toesRP')
                layout.row().prop(context.window_manager, 'toesRR')
    # ***************************************************************
    # END BIRD CLASS
    # ***************************************************************
    
class Centaur(Utils):
    bl_idname = "object.centaur"
    def setCentaurPropertiesPanel():
        setCommonPanel() # Covers buttons 1-99 (Leaving room  for more appendages)
        # Start Character-specific Panel with button numbers starting at 100
        class Centaur_Button(bpy.types.Operator):
            bl_idname = "b100.button"
            bl_label = "Drop Arms"
            bl_description = "Drop Character Arms"
            hidden = False
            def execute(self, context):
                bpy.context.object.pose.bones["armJ1.L"].rotation_euler[0] = -1.57
                bpy.context.object.pose.bones["armJ1.R"].rotation_euler[0] = -1.57
                bpy.ops.object.mode_set(mode='OBJECT')
                return{'FINISHED'}
    #
        class Centaur_Button(bpy.types.Operator):
            bl_idname = "b101.button"
            bl_label = "Walk"
            bl_description = "Walk"
            hidden = False
            def execute(self, context):
                centaurFns.setWalk(self, context)
                bpy.ops.object.mode_set(mode='OBJECT')
                return{'FINISHED'}
    #
        class Centaur_Button(bpy.types.Operator):
            bl_idname = "b102.button"
            bl_label = "Trot"
            bl_description = "Trot"
            hidden = False
            def execute(self, context):
                centaurFns.setTrot(self, context)
                bpy.ops.object.mode_set(mode='OBJECT')
                return{'FINISHED'}
    #
        class Centaur_Button(bpy.types.Operator):
            bl_idname = "b103.button"
            bl_label = "Pace"
            bl_description = "Pace"
            hidden = False
            def execute(self, context):
                bpy.context.scene.frame_set(0)
                centaurFns.setPace(self, context)
                bpy.ops.object.mode_set(mode='OBJECT')
                return{'FINISHED'}
    #
        class Centaur_Button(bpy.types.Operator):
            bl_idname = "b104.button"
            bl_label = "Gallop"
            bl_description = "Gallop"
            hidden = False
            def execute(self, context):
                bpy.context.scene.frame_set(0)
                centaurFns.setGallop(self, context)
                bpy.ops.object.mode_set(mode='OBJECT')
                return{'FINISHED'}
    #
        class Centaur_Button(bpy.types.Operator):
            bl_idname = "b105.button"
            bl_label = "Deactivate Arm Movement"
            bl_description = "Deactivate Arm Movement"
            hidden = False
            def execute(self, context):
                centaurFns.unsetArmRotation(self, context)
                bpy.ops.object.mode_set(mode='OBJECT')
                return{'FINISHED'} 
    #
        class Centaur_Button(bpy.types.Operator):
            bl_idname = "b106.button"
            bl_label = "Activate Arm Movement"
            bl_description = "Activate Arm Movement"
            hidden = False
            def execute(self, context):
                centaurFns.setArmRotation(self, context)
                bpy.ops.object.mode_set(mode='OBJECT')
                return{'FINISHED'}
    #
        class Centaur_Button(bpy.types.Operator):
            bl_idname = "b107.button"
            bl_label = "Deactivate Leg Movement"
            bl_description = "Deactivate Leg Movement"
            hidden = False
            def execute(self, context):
                centaurFns.unsetCentaurWalk(self, context)
                bpy.ops.object.mode_set(mode='OBJECT')
                return{'FINISHED'} 
    #
        class Centaur_Button(bpy.types.Operator):
            bl_idname = "b108.button"
            bl_label = "Front Leg Defaults"
            bl_description = "Front Leg Defaults"
            hidden = False
            def execute(self, context):
                centaurFns.setFrontLegDefaults(self, context)
                bpy.ops.object.mode_set(mode='OBJECT')
                return{'FINISHED'} 
    #
        class Centaur_Button(bpy.types.Operator):
            bl_idname = "b109.button"
            bl_label = "Rear Leg Defaults"
            bl_description = "Rear Leg Defaults"
            hidden = False
            def execute(self, context):
                centaurFns.setRearLegDefaults(self, context)
                bpy.ops.object.mode_set(mode='OBJECT')
                return{'FINISHED'} 
    #
        class Centaur_Panel(bpy.types.Panel):
            bl_label = "Centaur Control"
            bl_idname = "selected_object"
            bl_space_type = 'VIEW_3D'
            bl_region_type = 'TOOLS'
            bl_category = 'Instant Animation'
            bl_context = "objectmode"
            def draw(self, context):
                layout = self.layout
                layout.row().operator("b1.button")  # Build Biped
                layout.row().operator("b2.button")  # Build Bird
                layout.row().operator("b3.button")  # Build Centaur
                layout.row().operator("b4.button")  # Build Quadruped
                layout.row().operator("b5.button")  # Build Spider
                layout.row().operator("b6.button")  # Get Character Panel
                layout.row().operator("b7.button")  # Pose Character
                layout.row().operator("b8.button")  # Build Wings
                # End Common Panel, next button number starts with 100
                layout.row().prop(context.window_manager, 'speed')
                layout.row().prop(context.window_manager, 'direction')
                layout.row().prop(context.window_manager, 'cycle')
                layout.row().operator("b100.button") # Drop Arms button
                layout.row().operator("b101.button") # Walk
                layout.row().operator("b102.button") # Trot
                layout.row().operator("b103.button") # Pace
                layout.row().operator("b104.button") # Gallop
                layout.row().prop(context.window_manager, 'swayLR')
                layout.row().prop(context.window_manager, 'swayFB')
                layout.row().prop(context.window_manager, 'bounce')
                layout.row().prop(context.window_manager, 'hipRotate')
                layout.row().prop(context.window_manager, 'hipUD')
                layout.row().operator("b105.button")  # Deactivate Arm Movement
                layout.row().operator("b106.button")  # Activate Arms
                layout.row().prop(context.window_manager, 'armsUD')
                layout.row().prop(context.window_manager, 'shoulderRotate')
                layout.row().prop(context.window_manager, 'shoulderUD')
                layout.row().prop(context.window_manager, 'armRotation')
                layout.row().prop(context.window_manager, 'armTwistR')
                layout.row().prop(context.window_manager, 'armTwistL')
                layout.row().prop(context.window_manager, 'RHandSpread')
                layout.row().prop(context.window_manager, 'LHandSpread')
                layout.row().prop(context.window_manager, 'RHandOC')
                layout.row().prop(context.window_manager, 'LHandOC')
                layout.row().operator("b107.button") # Deactivate Leg Movement
                layout.row().prop(context.window_manager, 'neckFB')
                layout.row().prop(context.window_manager, 'neckLR')
                layout.row().prop(context.window_manager, 'neckTurn')
                layout.row().prop(context.window_manager, 'headUD')
                layout.row().prop(context.window_manager, 'headLR')
                layout.row().prop(context.window_manager, 'headTurn')
                layout.row().prop(context.window_manager, 'jawOC')
                layout.row().prop(context.window_manager, 'eyeUD')
                layout.row().prop(context.window_manager, 'eyeLR')
                layout.row().prop(context.window_manager, 'tailUD')
                layout.row().prop(context.window_manager, 'tailLR')
                layout.row().prop(context.window_manager, 'tailCurl')
    # ***************************************************************
    # END CENTAUR CLASS
    # ***************************************************************

class Quadruped(Utils):
    bl_idname = "object.quadruped"
    def setQuadrupedPropertiesPanel():
        setCommonPanel() # Covers buttons 1-99 (Leaving room  for more appendages)
        # Start Character-specific Panel with button numbers starting at 100               
        class Quadruped_Button(bpy.types.Operator):
            bl_idname = "b100.button"
            bl_label = "Walk"
            bl_description = "Walk"
            hidden = False
            def execute(self, context):
                quadrupedFns.setWalk(self, context)
                bpy.ops.object.mode_set(mode='OBJECT')
                return{'FINISHED'}
    #
        class Quadruped_Button(bpy.types.Operator):
            bl_idname = "b101.button"
            bl_label = "Trot"
            bl_description = "Trot"
            hidden = False
            def execute(self, context):
                quadrupedFns.setTrot(self, context)
                bpy.ops.object.mode_set(mode='OBJECT')
                return{'FINISHED'}
    #
        class Quadruped_Button(bpy.types.Operator):
            bl_idname = "b102.button"
            bl_label = "Pace"
            bl_description = "Pace"
            hidden = False
            def execute(self, context):
                bpy.context.scene.frame_set(0)
                quadrupedFns.setPace(self, context)
                bpy.ops.object.mode_set(mode='OBJECT')
                return{'FINISHED'}
    #
        class Quadruped_Button(bpy.types.Operator):
            bl_idname = "b103.button"
            bl_label = "Gallop"
            bl_description = "Gallop"
            hidden = False
            def execute(self, context):
                bpy.context.scene.frame_set(0)
                quadrupedFns.setGallop(self, context)
                bpy.ops.object.mode_set(mode='OBJECT')
                return{'FINISHED'}
    #
        class Quadruped_Button(bpy.types.Operator):
            bl_idname = "b104.button"
            bl_label = "Deactivate Leg Movement"
            bl_description = "Deactivate Leg Movement"
            hidden = False
            def execute(self, context):
                quadrupedFns.unsetQuadrupedWalk(self, context)
                bpy.ops.object.mode_set(mode='OBJECT')
                return{'FINISHED'} 
    #
        class Quadruped_Button(bpy.types.Operator):
            bl_idname = "b105.button"
            bl_label = "Front Leg Defaults"
            bl_description = "Front Leg Defaults"
            hidden = False
            def execute(self, context):
                quadrupedFns.setFrontLegDefaults(self, context)
                bpy.ops.object.mode_set(mode='OBJECT')
                return{'FINISHED'} 
    #
        class Quadruped_Button(bpy.types.Operator):
            bl_idname = "b106.button"
            bl_label = "Rear Leg Defaults"
            bl_description = "Rear Leg Defaults"
            hidden = False
            def execute(self, context):
                quadrupedFns.setRearLegDefaults(self, context)
                bpy.ops.object.mode_set(mode='OBJECT')
                return{'FINISHED'} 
    #
        class Quadruped_Panel(bpy.types.Panel):
            bl_label = "Quadruped Control"
            bl_idname = "selected_object"
            bl_space_type = 'VIEW_3D'
            bl_region_type = 'TOOLS'
            bl_category = 'Instant Animation'
            bl_context = "objectmode"
            def draw(self, context):
                layout = self.layout
                layout.row().operator("b1.button")  # Build Biped
                layout.row().operator("b2.button")  # Build Bird
                layout.row().operator("b3.button")  # Build Centaur
                layout.row().operator("b4.button")  # Build Quadruped
                layout.row().operator("b5.button")  # Build Spider
                layout.row().operator("b6.button")  # Get Character Panel
                layout.row().operator("b7.button")  # Pose Character
                layout.row().operator("b8.button")  # Build Wings
                # End Common Panel, next button number starts with 100
                layout.row().prop(context.window_manager, 'speed')
                layout.row().prop(context.window_manager, 'direction')
                layout.row().prop(context.window_manager, 'cycle')
                layout.row().operator("b100.button") # Pose
                layout.row().operator("b101.button") # Walk
                layout.row().operator("b102.button") # Trot
                layout.row().operator("b103.button") # Pace
                layout.row().operator("b104.button") # Gallop
                layout.row().prop(context.window_manager, 'swayLR')
                layout.row().prop(context.window_manager, 'swayFB')
                layout.row().prop(context.window_manager, 'bounce')
                layout.row().prop(context.window_manager, 'hipRotate')
                layout.row().prop(context.window_manager, 'hipUD')
                layout.row().operator("b105.button") # Deactivate Leg Movement
                layout.row().prop(context.window_manager, 'neckFB')
                layout.row().prop(context.window_manager, 'neckLR')
                layout.row().prop(context.window_manager, 'neckTurn')
                layout.row().prop(context.window_manager, 'headUD')
                layout.row().prop(context.window_manager, 'headLR')
                layout.row().prop(context.window_manager, 'headTurn')
                layout.row().prop(context.window_manager, 'jawOC')
                layout.row().prop(context.window_manager, 'eyeUD')
                layout.row().prop(context.window_manager, 'eyeLR')
                layout.row().prop(context.window_manager, 'tailUD')
                layout.row().prop(context.window_manager, 'tailLR')
                layout.row().prop(context.window_manager, 'tailCurl')
                layout.row().prop(context.window_manager, 'earUD')
                layout.row().prop(context.window_manager, 'earLR')
                layout.row().prop(context.window_manager, 'earCurl')
                layout.row().prop(context.window_manager, 'earAxial')
                layout.row().prop(context.window_manager, 'earOUD')
                layout.row().prop(context.window_manager, 'earOLR')
                layout.row().prop(context.window_manager, 'earOCurl')
                layout.row().prop(context.window_manager, 'earOAxial')
    # ***************************************************************
    # END QUADRUPED CLASS
    # ***************************************************************

class Spider(Utils):
    bl_idname = "object.spider"
    def setSpiderPropertiesPanel():
        setCommonPanel() # Covers buttons 1-99 (Leaving room  for more appendages)
        # Start Character-specific Panel with button numbers starting at 100
        class Spider_Panel(bpy.types.Panel):
            bl_label = "Spider Control"
            bl_idname = "selected_object"
            bl_space_type = 'VIEW_3D'
            bl_region_type = 'TOOLS'
            bl_category = 'Instant Animation'
            bl_context = "objectmode"
            def draw(self, context):
                layout = self.layout
                layout.row().operator("b1.button")  # Build Biped
                layout.row().operator("b2.button")  # Build Bird
                layout.row().operator("b3.button")  # Build Centaur
                layout.row().operator("b4.button")  # Build Quadruped
                layout.row().operator("b5.button")  # Build Spider
                layout.row().operator("b6.button")  # Get Character Panel
                layout.row().operator("b7.button")  # Pose Character
                layout.row().operator("b8.button")  # Build Wings
                # End Common Panel, next button number starts with 100
                layout.row().prop(context.window_manager, 'speed')
                layout.row().prop(context.window_manager, 'cycle')
                layout.row().prop(context.window_manager, 'direction')
# ***************************************************************
# END SPIDER CLASS
# ***************************************************************
#
# Start Appendages
class Wings(Utils):
    bl_idname = "object.wings"
    def activateWingsPropertiesPanel():
        setCommonPanel() # Covers buttons 1-99 (Leaving room  for more appendages)
        # Start Character-specific Panel with button numbers starting at 100
        class Wings_Button(bpy.types.Operator):
            bl_idname = "b100.button"
            bl_label = "Activate Solo Wings"
            bl_description = "Activate Solo Wings"
            hidden = False
            def execute(self, context):
                activateWings(self, context)
                bpy.context.scene.frame_set(0)
                bpy.ops.object.mode_set(mode='OBJECT')
                return{'FINISHED'}
    #
        class Wings_Button(bpy.types.Operator):
            bl_idname = "b101.button"
            bl_label = "Fold Solo Wings"
            bl_description = "Fold Solo Wings"
            hidden = False
            def execute(self, context):
                unSetWings(self, context)
                foldWings(self, context)
                bpy.context.scene.frame_set(0)
                return{'FINISHED'}
    #
        class Wings_Button(bpy.types.Operator):
            bl_idname = "b102.button"
            bl_label = "Clear Solo Wings"
            bl_description = "Clear Solo Wings"
            hidden = False
            def execute(self, context):
                unSetWings(self, context)
                unSetWings(self, context)
                bpy.context.scene.frame_set(0)
                bpy.ops.object.mode_set(mode='OBJECT')
                return{'FINISHED'}
    #
        class Wings_Panel(bpy.types.Panel):
            bl_label = "Wings Control"
            bl_idname = "selected_object"
            bl_space_type = 'VIEW_3D'
            bl_region_type = 'TOOLS'
            bl_category = 'Instant Animation'
            bl_context = "objectmode"
            def draw(self, context):
                layout = self.layout
                layout.row().operator("b1.button")  # Build Biped
                layout.row().operator("b2.button")  # Build Bird
                layout.row().operator("b3.button")  # Build Centaur
                layout.row().operator("b4.button")  # Build Quadruped
                layout.row().operator("b5.button")  # Build Spider
                layout.row().operator("b6.button")  # Get Character Panel
                layout.row().operator("b7.button")  # Pose Character
                layout.row().operator("b8.button")  # Build Wings
                # End Common Panel, next button number starts with 100
                layout.row().prop(context.window_manager, 'adWingsSpeed')
                layout.row().operator("b100.button")  # Activate Wings
                layout.row().operator("b101.button")  # Fold Wings
                layout.row().operator("b102.button")  # Unfold Wings
                layout.row().prop(context.window_manager, 'adWingsRP')
                layout.row().prop(context.window_manager, 'adWingsRR')
                layout.row().prop(context.window_manager, 'adWingsAxial')
                layout.row().prop(context.window_manager, 'adWingsFB')
                layout.row().prop(context.window_manager, 'adWingsCurveFB')
                layout.row().prop(context.window_manager, 'adWingsCurveUD')
                layout.row().prop(context.window_manager, 'adWingsInnerFeathers')
                layout.row().prop(context.window_manager, 'adWingsOuterFeathers')
# ***************************************************************
# END WINGS CLASS
# ***************************************************************
#
#
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# End Character Classes: Create character properties and buttons panel
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#
#
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# COMMON SHARED PARTS IN CHARACTER FUNCTIONS
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# COMMON FUNCTION - buildHumanUpperBody     To 1779
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
# END COMMON FUNCTION - buildHumanUpperBody
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# COMMON FUNCTION - buildQuadrupedBase
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def buildQuadrupedBase(at):
    bpy.ops.object.mode_set(mode='EDIT')
    V_origin = (0, 0, 0)
    V_qBackJ0 = (0, .2, 0)
    qBackJ0 = u.createBone("qBackJ0", V_origin, V_qBackJ0, 0)
    qBackJ0.parent = at.edit_bones[u.strName + '_bone']
    #
    V_join = (0, 0, -.12)
    u.boneMirror(at, V_join, False)
    V_drop = (0, 0, -.17)
    u.boneMirror(at, V_drop, False)
    V_pelvis = (0, 0, -.15)
    u.boneMirror(at, V_pelvis, False)
    at.edit_bones["qBackJ0.001"].name = "join"
    at.edit_bones["qBackJ0.002"].name = "drop"
    at.edit_bones["qBackJ0.003"].name = "pelvis"
    # 
    # Start mirroring
    V_hip = (0.12, 0, 0)
    u.boneMirror(at, V_hip, True)
    V_femurJ1 = (0, 0, -.18)
    u.boneMirror(at, V_femurJ1, True)
    V_femurJ2 = (0, 0, -.16)
    u.boneMirror(at, V_femurJ2, True)
    V_tibiaJ1 = (0, 0, -.1)
    u.boneMirror(at, V_tibiaJ1, True)
    V_tibiaJ2 = (0, 0, -.1)
    u.boneMirror(at, V_tibiaJ2, True)
    V_ankle = (0, .046, -.08)
    u.boneMirror(at, V_ankle, True)
    V_toe = (0, .09, -.07)
    u.boneMirror(at, V_toe, True)
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
    #
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["qBackJ0"].select_head=True
    V_qBackJ1 = (0, -0.14, -.06)
    u.boneMirror(at, V_qBackJ1, False)
    V_qBackJ2 = (0, -.11, 0)
    u.boneMirror(at, V_qBackJ2, False)
    V_qBackJ3 = (0, -.12, .02)
    u.boneMirror(at, V_qBackJ3, False)
    V_qBackJ4 = (0, -.12, .02)
    u.boneMirror(at, V_qBackJ4, False)
    V_qBackJ5 = (0, -.14, .01)
    u.boneMirror(at, V_qBackJ5, False)
    at.edit_bones['qBackJ0.001'].name = "qBackJ1"
    at.edit_bones['qBackJ0.002'].name = "qBackJ2"
    at.edit_bones['qBackJ0.003'].name = "qBackJ3"
    at.edit_bones['qBackJ0.004'].name = "qBackJ4"
    at.edit_bones['qBackJ0.005'].name = "qBackJ5"
    #
    #
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["qBackJ1"].select_head=True
    V_qfixRib1Top = (.1, 0, -.04)
    u.boneMirror(at, V_qfixRib1Top, True)
    V_qfixRib1B = (0, -.06, -0.4)
    u.boneMirror(at, V_qfixRib1B, True)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["qBackJ1"].select_tail=True
    V_qfixRib2Top = (.1, .02, 0)
    u.boneMirror(at, V_qfixRib2Top, True)
    V_qfixRib2B = (0, -.06, -.4)
    u.boneMirror(at, V_qfixRib2B, True)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["qBackJ3"].select_tail=True
    V_qfixRib3Top = (.1, 0, 0)
    u.boneMirror(at, V_qfixRib3Top, True)
    V_qfixRib3B = (0, 0, -.38)
    u.boneMirror(at, V_qfixRib3B, True)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["qBackJ4"].select_tail=True
    V_qfixRib4Top = (.1, 0, 0)
    u.boneMirror(at, V_qfixRib4Top, True)
    V_qfixRib4B = (0, 0, -.36)
    u.boneMirror(at, V_qfixRib4B, True)  
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
    u.boneMirror(at, V_hRumpJ1, False)
    V_hRumpJ2 = (0, -.12, -.004)
    u.boneMirror(at, V_hRumpJ2, False)
    V_hRumpJ3 = (0, -.05, 0)
    u.boneMirror(at, V_hRumpJ3, False)
    at.edit_bones['qBackJ5.001'].name = "hRumpJ1"
    at.edit_bones['qBackJ5.002'].name = "hRumpJ2"
    at.edit_bones['qBackJ5.003'].name = "hRumpJ3"
    #
    V_hTailJ1 = (0, -.04, .0146)
    u.boneMirror(at, V_hTailJ1, False)
    V_hTailJ2 = (0, -.06, .012)
    u.boneMirror(at, V_hTailJ2, False)
    V_hTailJ3 = (0, -.06, .01)
    u.boneMirror(at, V_hTailJ3, False)
    V_hTailJ4 = (0, -.06, 0)
    u.boneMirror(at, V_hTailJ4, False)
    V_hTailJ5 = (0, -.06, 0)
    u.boneMirror(at, V_hTailJ5, False)
    V_hTailJ6 = (0, -.06, 0)
    u.boneMirror(at, V_hTailJ6, False)
    V_hTailJ7 = (0, -.06, 0)
    u.boneMirror(at, V_hTailJ7, False)
    V_hTailJ8 = (0, -.06, 0)
    u.boneMirror(at, V_hTailJ8, False)
    V_hTailJ9 = (0, -.06, 0)
    u.boneMirror(at, V_hTailJ9, False)
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
    u.boneMirror(at, V_hRumpfix1, False)
    V_hRumpfix2 = (0, .12, -.06)
    u.boneMirror(at, V_hRumpfix2, False)
    V_hRumpfix3 = (0, .15, -.07)
    u.boneMirror(at, V_hRumpfix3, False)
    at.edit_bones['hRumpJ1.001'].name = "fixRump1"
    at.edit_bones['hRumpJ1.002'].name = "fixRump2"
    at.edit_bones['hRumpJ1.003'].name = "fixRump3"
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["hRumpJ2"].select_tail=True
    V_hRumpfix3 = (0, .14, .05)
    u.boneMirror(at, V_hRumpfix3, False)
    V_hRumpfix4 = (0, .2, .04)
    u.boneMirror(at, V_hRumpfix4, False)
    at.edit_bones['hRumpJ2.001'].name = "fixSacrum1"
    at.edit_bones['hRumpJ2.002'].name = "fixSacrum2"
    #
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["qBackJ5"].select_tail=True
    V_rearHip = (.16, 0, 0)
    u.boneMirror(at, V_rearHip, True)
    V_qfix4 = (0, -.16, -.11)
    u.boneMirror(at, V_qfix4, True)
    V_qfix5 = (0, 0, -.12)
    u.boneMirror(at, V_qfix5, True)
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
    u.boneMirror(at, V_rearHipJ1, True)
    V_rearFemurJ1 = (0, -.08, -.2)
    u.boneMirror(at, V_rearFemurJ1, True)
    V_rearFemurJ2 = (0, -.08, -.2)
    u.boneMirror(at, V_rearFemurJ2, True)
    V_rearTibiaJ1 = (0, 0, -.15)
    u.boneMirror(at, V_rearTibiaJ1, True)
    V_rearTibiaJ2 = (0, 0, -.15)
    u.boneMirror(at, V_rearTibiaJ2, True)
    V_horseRRearAnkle = (0, .06, -.07)
    u.boneMirror(at, V_horseRRearAnkle, True)
    V_horseRToe = (0, .04, -.06)
    u.boneMirror(at, V_horseRToe, True)
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
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# END COMMON FUNCTION - buildQuadrupedBase
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# COMMON FUNCTION - setEnvelopeWeights
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
        #
        # Set weights for Quadruped parts, the body and four legs
        if(name.startswith("quadruped")) or (name.startswith("centaur")):
            if(b.name.startswith("hTail")):
                b.envelope_distance = 0.06
            if(b.name == "hTailJ1") or (b.name == "hTailJ2"):
                b.envelope_distance = 0.03
            if(b.name.startswith("shoulder")):
                b.envelope_distance = 0.06
            if(b.name.startswith("clavicle")):
                b.envelope_distance = 0.04
            if(b.name.startswith("fix")):
                b.envelope_distance = 0.044
            if(b.name.startswith("eyeLevel")):
                b.envelope_distance = 0.09
            if(b.name == "nose") or (b.name == "noseTip"):
                b.envelope_distance = 0.02
            if(b.name == "eyeR") or (b.name == "eyeL"):
                b.envelope_distance = 0.0
            if(b.name == "drop"):
                b.envelope_distance = 0.21
            if(b.name == "pelvis"):
                b.envelope_distance = 0.1
            if(b.name.startswith("femur")):
                b.envelope_distance = 0.08
            if(b.name.startswith("tibia")):
                b.envelope_distance = 0.08
            if(b.name.startswith("ankle")):
                b.envelope_distance = 0.12
            if(b.name.startswith("toe")):
                b.envelope_distance = 0.12
            if(b.name.startswith("rearHipJ1")) or (b.name.startswith("rearFemurJ1")):
                b.envelope_distance = 0.2
            if(b.name.startswith("rearFemurJ2")) or (b.name.startswith("rearTibiaJ1")):
                b.envelope_distance = 0.1
            if(b.name.startswith("rearTibiaJ2")):
                b.envelope_distance = 0.1
            if(b.name.startswith("rearAnkle")):
                b.envelope_distance = 0.12
            if(b.name.startswith("rearToe")):
                b.envelope_distance = 0.1
            if(b.name.startswith("fix")):
                b.envelope_distance = 0.08
            if(b.name.startswith("qfixRib")):
                b.envelope_distance = 0.13
            if(b.name.startswith("qfixRib2Top")) or (b.name.startswith("qfixRib4Top")):
                b.envelope_distance = 0.15
            if(b.name.startswith("qfixRib1B")):
                b.envelope_distance = 0.15
            if(b.name.startswith("qfixRib2B")) or (b.name.startswith("qfixRib3B")):
                b.envelope_distance = 0.19
            if(b.name.startswith("hRumpfix")):
                b.envelope_distance = 0.11
            if(b.name == "hRumpfix1A"):
                b.envelope_distance = 0.06
            if(b.name.startswith("fixRump1")):
                b.envelope_distance = 0.16
            if(b.name.startswith("fixRump2")):
                b.envelope_distance = 0.16
            if(b.name.startswith("fixRump3")):
                b.envelope_distance = 0.11
            if(b.name.startswith("qfixHind2")):
                b.envelope_distance = 0.17
        #
        #
        if(name.startswith("bird")):
            # Set bird envelope weights
            for b in bpy.context.object.data.edit_bones:
                if(b.name == u.strName):
                    b.envelope_distance = 0
                    b.head_radius = 0.04
                    b.tail_radius = 0.02
                if(b.name =="backCenter"):
                    b.envelope_distance = 0.12
                    b.head_radius = 0.001
                    b.tail_radius = 0.060
                if(b.name =="backL1"):
                    b.envelope_distance = 0.22
                    b.head_radius = .02
                    b.tail_radius = .04
                if(b.name =="backL2"):
                    b.envelope_distance = 0.26
                    b.head_radius = .02
                    b.tail_radius = .04
                if(b.name =="backL3"):
                    b.envelope_distance = 0.28
                if(b.name =="tailJ1"):
                    b.envelope_distance = 0.18
                if(b.name.startswith("ffix")):
                    b.envelope_distance = 0.12
                if(b.name =="ffix1"):
                    b.envelope_distance = 0.17
                if(b.name =="ffix3"):
                    b.envelope_distance = 0.23
                if(b.name =="ffix4"):
                    b.envelope_distance = 0.26
                if(b.name =="ffix5"):
                    b.envelope_distance = 0.2
                if(b.name.startswith("neck")):
                    b.envelope_distance = 0.12
                if(b.name == "neck05") or (b.name == "neck02"):
                    b.envelope_distance = 0.14
                if(b.name.startswith("head")):
                    b.envelope_distance = 0.16
                if(b.name == "headBase"):
                    b.envelope_distance = 0.2
                if(b.name.startswith("jaw")):
                    b.envelope_distance = .03
                if(b.name.startswith("beak")):
                    b.envelope_distance = .04
                if(b.name == "hipBase"):
                    b.envelope_distance = 0.2
                if(b.name == "hipBone"):
                    b.envelope_distance = 0.1
                if(b.name.startswith("fixPosterior2")):
                    b.envelope_distance = 0.08
                if(b.name.startswith("femur")):
                    b.envelope_distance = 0.05
                if(b.name.startswith("femurJ1")):
                    b.envelope_distance = 0.1
                if(b.name.startswith("tibia")):
                    b.envelope_distance = 0.06
                if(b.name.startswith("inside")):
                    b.envelope_distance = .05
                if(b.name.startswith("front")):
                    b.envelope_distance = .05
                if(b.name.startswith("outside")):
                    b.envelope_distance = .05
                if(b.name.startswith("rear")):
                    b.envelope_distance = .06
                if(b.name.startswith("wing")):
                    b.envelope_distance = 0.06
                if(b.name.startswith("baseWing")):
                    b.envelope_distance = 0.1
                if(b.name.startswith("eye")):
                    b.envelope_distance = 0
                if(b.name.startswith("fa")):  # Tail manipulators fa#.L, R
                    b.envelope_distance = 0        
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# END COMMON FUNCTION - setEnvelopeWeights
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# COMMON FUNCTION - createWings
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def createWings(at):
    name = u.strName.replace("rg", "")
    if(name.startswith("bird")):
        root = "backCenter"
    if(name.startswith("adWings")):
        root = u.strName + "_bone"
    # BuildWings
    at.edit_bones[root].select_head=True
    Vbase = (-.12, 0, 0)
    u.boneMirror(at, Vbase, True)
    Vwings_J1 = (-.06, 0, 0)
    u.boneMirror(at, Vwings_J1, True)
    Vwings_J2 = (-.03, 0, 0)
    u.boneMirror(at, Vwings_J2, True)
    Vwings_J3 = (-.03, 0, 0)
    u.boneMirror(at, Vwings_J3, True)
    Vwings_J4 = (-.03, 0, 0)
    u.boneMirror(at, Vwings_J4, True)
    Vwings_J5 = (-.03, 0, 0)
    u.boneMirror(at, Vwings_J5, True)
    Vwings_J6 = (-.03, 0, 0)
    u.boneMirror(at, Vwings_J6, True)
    Vwings_J7 = (-.03, 0, 0)
    u.boneMirror(at, Vwings_J7, True)
    Vwings_J8 = (-.03, 0, 0)
    u.boneMirror(at, Vwings_J8, True)
    Vwings_J9 = (-.03, 0, 0)
    u.boneMirror(at, Vwings_J9, True)
    Vwings_J10 = (-.03, 0, 0)
    u.boneMirror(at, Vwings_J10, True)
    Vwings_J11 = (-.015, 0, 0)
    u.boneMirror(at, Vwings_J11, True)
    Vwings_J12 = (-.015, 0, 0)
    u.boneMirror(at, Vwings_J12, True)
    Vwings_J13 = (-.015, 0, 0)
    u.boneMirror(at, Vwings_J13, True)
    Vwings_J14 = (-.015, 0, 0)
    u.boneMirror(at, Vwings_J14, True)
    Vwings_J15 = (-.015, 0, 0)
    u.boneMirror(at, Vwings_J15, True)
    Vwings_J16 = (-0.06, 0, 0)
    u.boneMirror(at, Vwings_J16, True)
    # 
    if(name.startswith("bird")):  # Start designation with "wings" for bird
        prefix = "wings"
    if(name.startswith("adWings")):  # Start designation with "adWings" for adWings
        prefix = "adWings"
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
    u.boneMirror(at, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones[prefix + "_J2.L"].select_tail=True
    Vfeathers = (n, -.04, 0)
    u.boneMirror(at, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones[prefix + "_J3.L"].select_tail=True
    n = n - offset
    Vfeathers = (n, -.04, 0)
    u.boneMirror(at, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones[prefix + "_J4.L"].select_tail=True
    n = n - offset
    Vfeathers = (n, -.04, 0)
    u.boneMirror(at, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones[prefix + "_J5.L"].select_tail=True
    n = n - offset
    Vfeathers = (n, -.04, 0)
    u.boneMirror(at, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones[prefix + "_J6.L"].select_tail=True
    n = n - offset
    Vfeathers = (n, -.04, 0)
    u.boneMirror(at, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones[prefix + "_J7.L"].select_tail=True
    n = n - offset
    Vfeathers = (n, -.04, 0)
    u.boneMirror(at, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones[prefix + "_J8.L"].select_tail=True
    n = n - offset
    Vfeathers = (n, -.04, 0)
    u.boneMirror(at, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones[prefix + "_J9.L"].select_tail=True
    n = n - offset
    Vfeathers = (n, -.04, 0)
    u.boneMirror(at, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones[prefix + "_J10.L"].select_tail=True
    n = n - offset
    Vfeathers = (n, -.034, 0)
    u.boneMirror(at, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones[prefix + "_J11.L"].select_tail=True
    offset = .002
    n = n - offset
    Vfeathers = (n, -.026, 0)
    u.boneMirror(at, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones[prefix + "_J12.L"].select_tail=True
    n = n - offset
    Vfeathers = (n, -.024, 0)
    u.boneMirror(at, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones[prefix + "_J13.L"].select_tail=True
    n = n - offset
    Vfeathers = (n, -.018, 0)
    u.boneMirror(at, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones[prefix + "_J14.L"].select_tail=True
    Vfeathers = (n, -.012, 0)
    u.boneMirror(at, Vfeathers, True)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones[prefix + "_J15.L"].select_tail=True
    Vfeathers = (n, -.009, 0)
    u.boneMirror(at, Vfeathers, True)
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
    for b in bpy.data.objects[u.strName].pose.bones:
        b.rotation_mode = 'XYZ'
    name = u.strName.replace("rg", "")
    for b in bpy.context.object.data.edit_bones:
        # Set weights for adWings
        if(b.name == u.strName + '_bone'):
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
# END COMMON FUNCTION - createWings
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# COMMON FUNCTION - activateWings
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def activateWings(self, context):
    u.getSelectedCharacterName()
    name = u.strName.replace("rg", "")
    if(name.startswith("bird")):  # Start designation with "wings" for bird
        prefix = "wings"
        speed = bpy.context.window_manager.wingsSpeed * 11
        RP = str(bpy.context.window_manager.wingsRP)
        RR = str(bpy.context.window_manager.wingsRR)
    if(name.startswith("adWings")):  # Start designation with "adWings" for adWings
        prefix = "adWings"
        speed = bpy.context.window_manager.adWingsSpeed * 11
        RP = str(bpy.context.window_manager.adWingsRP)
        RR = str(bpy.context.window_manager.adWingsRR)
    speed = "sin(radians(" + str(speed) + "*frame))"
    fnFlap = "(" + RP + "-(asin(" + speed + "))* .2 * " + RR + ")"
    u.setAxisDriver(u.getEuler(prefix + '_J1.R'), fnFlap + u.strx0AtFrame0, 0)
    u.setAxisDriver(u.getEuler(prefix + '_J1.L'), fnFlap + u.strx0AtFrame0, 0)
    # Wing fwd-bkwd curvature
    if(prefix == "wings"):
        curveFB = str(bpy.context.window_manager.wingsCurveFB * .01)
    if(prefix == "adWings"):
        curveFB = str(bpy.context.window_manager.adWingsCurveFB * .01)
    u.setDriver(u.getEuler(prefix + '_J3.L'), curveFB + "* -1", 2)
    u.setDriver(u.getEuler(prefix + '_J4.L'), curveFB + "* -1", 2)
    u.setDriver(u.getEuler(prefix + '_J5.L'), curveFB + "* -1", 2)
    u.setDriver(u.getEuler(prefix + '_J6.L'), curveFB + "* -1", 2)
    u.setDriver(u.getEuler(prefix + '_J7.L'), curveFB + "* -1", 2)
    u.setDriver(u.getEuler(prefix + '_J8.L'), curveFB + "* -1", 2)
    u.setDriver(u.getEuler(prefix + '_J9.L'), curveFB + "* -1", 2)
    #
    u.setDriver(u.getEuler(prefix + '_J3.R'), curveFB, 2)
    u.setDriver(u.getEuler(prefix + '_J4.R'), curveFB, 2)
    u.setDriver(u.getEuler(prefix + '_J5.R'), curveFB, 2)
    u.setDriver(u.getEuler(prefix + '_J6.R'), curveFB, 2)
    u.setDriver(u.getEuler(prefix + '_J7.R'), curveFB, 2)
    u.setDriver(u.getEuler(prefix + '_J8.R'), curveFB, 2)
    u.setDriver(u.getEuler(prefix + '_J9.R'), curveFB, 2)
    # Wing up-down curvature
    # This curves the wing dynamically, unlike the static curve of fwd-backward
    if(prefix == "wings"):
        curveUD = str(bpy.context.window_manager.wingsCurveUD * .01)
    if(prefix == "adWings"):
        curveUD = str(bpy.context.window_manager.adWingsCurveUD * .01)
    u.setDriver(u.getEuler(prefix + '_J3.L'), curveUD + " * " + fnFlap, 0)
    u.setDriver(u.getEuler(prefix + '_J4.L'), curveUD + " * " + fnFlap, 0)
    u.setDriver(u.getEuler(prefix + '_J5.L'), curveUD + " * " + fnFlap, 0)
    u.setDriver(u.getEuler(prefix + '_J6.L'), curveUD + " * " + fnFlap, 0)
    u.setDriver(u.getEuler(prefix + '_J7.L'), curveUD + " * " + fnFlap, 0)
    u.setDriver(u.getEuler(prefix + '_J8.L'), curveUD + " * " + fnFlap, 0)
    u.setDriver(u.getEuler(prefix + '_J9.L'), curveUD + " * " + fnFlap, 0) 
    #
    u.setDriver(u.getEuler(prefix + '_J3.R'), curveUD + " * " + fnFlap, 0)
    u.setDriver(u.getEuler(prefix + '_J4.R'), curveUD + " * " + fnFlap, 0)
    u.setDriver(u.getEuler(prefix + '_J5.R'), curveUD + " * " + fnFlap, 0)
    u.setDriver(u.getEuler(prefix + '_J6.R'), curveUD + " * " + fnFlap, 0)
    u.setDriver(u.getEuler(prefix + '_J7.R'), curveUD + " * " + fnFlap, 0)
    u.setDriver(u.getEuler(prefix + '_J8.R'), curveUD + " * " + fnFlap, 0)
    u.setDriver(u.getEuler(prefix + '_J9.R'), curveUD + " * " + fnFlap, 0)
    bpy.ops.object.mode_set(mode='OBJECT')
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# END COMMON FUNCTION - activateWings
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%        
#
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# COMMON FUNCTION - setAxialPosition
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def setAxialPosition(self, context):
    u.getSelectedCharacterName()
    name = u.strName.replace("rg", "")
    if(name.startswith("bird")):  # Start designation with "wings" for bird
        prefix = "wings"
        axial = bpy.context.window_manager.wingsAxial * .1
    if(name.startswith("adWings")):  # Start designation with "adWings" for adWings
        prefix = "adWings"
        axial = bpy.context.window_manager.adWingsAxial * .1
    u.rotate(u.strName, prefix + '_J1.L', axial, 1)
    u.rotate(u.strName, prefix + '_J1.R', axial * -1, 1)
    bpy.context.object.data.bones[prefix + '_J1.L'].select  = True
    bpy.context.object.data.bones[prefix + '_J1.R'].select  = True
    bpy.ops.object.mode_set(mode='POSE')
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# END COMMON FUNCTION - setAxialPosition
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# COMMON FUNCTION - setFwdBackwardPosition
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def setFwdBackwardPosition(self, context):
    u.getSelectedCharacterName()
    name = u.strName.replace("rg", "")
    if(name.startswith("bird")):  # Start designation with "wings" for bird
        prefix = "wings"
        FB2 = bpy.context.window_manager.wingsFB * .1
    if(name.startswith("adWings")):  # Start designation with "adWings" for solo adWings
        prefix = "adWings"
        FB2 = bpy.context.window_manager.adWingsFB * .1
    u.rotate(u.strName, prefix + '_J1.L', FB2, 2)
    u.rotate(u.strName, prefix + '_J1.R', FB2 * -1, 2)
    bpy.context.object.data.bones[prefix + '_J1.L'].select  = True
    bpy.context.object.data.bones[prefix + '_J1.R'].select  = True
    bpy.ops.object.mode_set(mode='POSE')
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# END COMMON FUNCTION - setFwdBackwardPosition
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# COMMON FUNCTION - unSetWings
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def unSetWings(self, context):
    u.getSelectedCharacterName()
    name = u.strName.replace("rg", "")
    if(name.startswith("bird")):  # Start designation with "wings" for bird
        prefix = "wings"
    if(name.startswith("adWings")):  # Start designation with "adWings" for adWings
        prefix = "adWings"
    for i in range(1, 10):
        for j in range(0, 3):
            u.setDriver(u.getEuler(prefix + '_J' + str(i) + '.L'), "0", j)
            u.setDriver(u.getEuler(prefix + '_J' + str(i) + '.R'), "0", j)
        # Left wing
        bpy.data.objects[u.strName].pose.bones[prefix + '_J' + str(i) + '.L'].rotation_euler.x = 0
        bpy.data.objects[u.strName].pose.bones[prefix + '_J' + str(i) + '.L'].rotation_euler.y = 0
        bpy.data.objects[u.strName].pose.bones[prefix + '_J' + str(i) + '.L'].rotation_euler.z = 0
        # Right wing
        bpy.data.objects[u.strName].pose.bones[prefix + '_J' + str(i) + '.R'].rotation_euler.x = 0
        bpy.data.objects[u.strName].pose.bones[prefix + '_J' + str(i) + '.R'].rotation_euler.y = 0
        bpy.data.objects[u.strName].pose.bones[prefix + '_J' + str(i) + '.R'].rotation_euler.z = 0
    undo = bpy.data.objects[u.strName].pose.bones[u.strName + '_bone']
    undo.driver_remove('location', -1)
    for i in range(1, 10):
        undo = bpy.data.objects[u.strName].pose.bones[prefix + '_J' + str(i) + '.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones[prefix + '_J' + str(i) + '.L']
        undo.driver_remove('rotation_euler', -1)
    clearFeathers(self, context)
    bpy.ops.object.mode_set(mode='OBJECT')
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# END COMMON FUNCTION - unSetWings
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# COMMON FUNCTION - foldWings
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def foldWings(self, context):
    u.getSelectedCharacterName()
    name = u.strName.replace("rg", "")
    if(name.startswith("bird")):  # Start designation with "wings" for bird
        prefix = "wings"
    if(name.startswith("adWings")):  # Start designation with "adWings" for adWings
        prefix = "adWings"
    # Left wing
    u.setDriver(u.getEuler(prefix + '_J1.L'), "-1.2", 0) # up-down
    u.setDriver(u.getEuler(prefix + '_J1.L'), "-.9", 1) # rotational location
    u.setDriver(u.getEuler(prefix + '_J4.L'), "1.3", 2) # Second fold
    u.setDriver(u.getEuler(prefix + '_J4.L'), ".2", 0) # Second fold up-down
    u.setDriver(u.getEuler(prefix + '_J7.L'), ".4", 2) # Outer fold
    u.setDriver(u.getEuler(prefix + '_J8.L'), ".1", 2) # Outer fold
    # Right wing
    u.setDriver(u.getEuler(prefix + '_J1.R'), "-1.2", 0) # up-down
    u.setDriver(u.getEuler(prefix + '_J1.R'), ".9", 1)  # rotational location
    u.setDriver(u.getEuler(prefix + '_J4.R'), "-1.3", 2) # Second fold
    u.setDriver(u.getEuler(prefix + '_J4.R'), ".2", 0) # Second fold up-down
    u.setDriver(u.getEuler(prefix + '_J7.R'), "-.4", 2) # Outer fold
    u.setDriver(u.getEuler(prefix + '_J8.R'), "-.1", 2) # Outer fold
    for i in range(1, 9):
        bpy.context.object.data.bones[prefix + '_J' + str(i) + '.L'].select  = True
        bpy.context.object.data.bones[prefix + '_J' + str(i) + '.R'].select  = True
    # foldFeathers sets feather location, selects them, and goes to pose mode
    foldFeathers(self, context)
    bpy.ops.object.mode_set(mode='POSE')
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# END COMMON FUNCTION - foldWings
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# COMMON FUNCTION - setWingFoldedFeathers
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def foldFeathers(self, context):
    u.getSelectedCharacterName()
    name = u.strName.replace("rg", "")
    if(name.startswith("bird")):  # Start designation with "wings" for bird
        feather = "wingsFeathers"  
    if(name.startswith("adWings")):  # Start designation with "adWings" for adWings
        feather = "adWingsFeathers"
    # If needed for feather lift, use axis 0
    u.rotate(u.strName, feather + '1.L', rad=.2, axis=2) # Inner Wing
    u.rotate(u.strName, feather + '1.R', rad=-.2, axis=2) 
    u.rotate(u.strName, feather + '2.L', rad=.2, axis=2) 
    u.rotate(u.strName, feather + '2.R', rad=-.2, axis=2) 
    u.rotate(u.strName, feather + '3.L', rad=.3, axis=2) 
    u.rotate(u.strName, feather + '3.R', rad=-.3, axis=2) 
    #
    u.rotate(u.strName, feather + '4.L', rad=-.6, axis=2) # Outer Wing
    u.rotate(u.strName, feather + '4.R', rad=.6, axis=2) 
    u.rotate(u.strName, feather + '5.L', rad=-.6, axis=2)
    u.rotate(u.strName, feather + '5.R', rad=.6, axis=2) 
    u.rotate(u.strName, feather + '6.L', rad=-.6, axis=2)
    u.rotate(u.strName, feather + '6.R', rad=.6, axis=2) 
    u.rotate(u.strName, feather + '7.L', rad=-.9, axis=2)
    u.rotate(u.strName, feather + '7.R', rad=.9, axis=2)
    u.rotate(u.strName, feather + '8.L', rad=-1.1, axis=2)
    u.rotate(u.strName, feather + '8.R', rad=1.1, axis=2)
    for i in range(1, 9):
        bpy.context.object.data.bones[feather + str(i) + '.L'].select  = True
        bpy.context.object.data.bones[feather + str(i) + '.R'].select  = True
    bpy.ops.object.mode_set(mode='POSE')
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# END COMMON FUNCTION - setWingFoldedFeathers
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# COMMON FUNCTION - setWingFeathers
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def clearFeathers(self, context):
    u.getSelectedCharacterName()
    name = u.strName.replace("rg", "")
    if(name.startswith("bird")):  # Start designation with "wings" for bird
        feather = "wingsFeathers"  
    if(name.startswith("adWings")):  # Start designation with "adWings" for adWings
        feather = "adWingsFeathers"
    # If needed for feather lift, use axis 0
    for i in range(1, 16):
        u.rotate(u.strName, feather + str(i) + '.L', rad=0, axis=2) # feather 1 - 3  Inner Wing
        u.rotate(u.strName, feather + str(i) + '.R', rad=0, axis=2) # feather 4 - 15  Outer Wing
    u.rotate(u.strName, "wings_J16.L", rad=0, axis=2)
    u.rotate(u.strName, "wings_J16.R", rad=0, axis=2)
    bpy.ops.object.mode_set(mode='OBJECT')
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# END COMMON FUNCTION - setWingFeathers
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# COMMON FUNCTION - setInnerFeathers
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def setInnerFeathers(self, context):
    u.getSelectedCharacterName()
    name = u.strName.replace("rg", "")
    if(name.startswith("bird")):  # Start designation with "wings" for bird
        feather = "wingsFeathers"
        featherRot = math.radians(bpy.context.window_manager.wingsInnerFeathers)
    if(name.startswith("adWings")):  # Start designation with "adWings" for adWings
        feather = "adWingsFeathers"
        featherRot = math.radians(bpy.context.window_manager.adWingsInnerFeathers)
    # If needed for feather lift, use axis 0
    u.rotate(u.strName, feather + '1.L', rad=-featherRot, axis=2) # Inner Wing
    u.rotate(u.strName, feather + '1.R', rad=featherRot, axis=2) 
    u.rotate(u.strName, feather + '2.L', rad=-featherRot, axis=2) 
    u.rotate(u.strName, feather + '2.R', rad=featherRot, axis=2) 
    u.rotate(u.strName, feather + '3.L', rad=-featherRot, axis=2) 
    u.rotate(u.strName, feather + '3.R', rad=featherRot, axis=2)
    for i in range(1, 4):
        bpy.context.object.data.bones[feather + str(i) + '.L'].select  = True
        bpy.context.object.data.bones[feather + str(i) + '.R'].select  = True
    bpy.ops.object.mode_set(mode='POSE')
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# END COMMON FUNCTION - setInnerFeathers
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# COMMON FUNCTION - setOuterFeathers
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def setOuterFeathers(self, context):
    u.getSelectedCharacterName()
    name = u.strName.replace("rg", "")
    if(name.startswith("bird")):  # Start designation with "wings" for bird
        feather = "wingsFeathers"
        featherRot = math.radians(bpy.context.window_manager.wingsOuterFeathers)
    if(name.startswith("adWings")):  # Start designation with "adWings" for adWings
        feather = "adWingsFeathers"
        featherRot = math.radians(bpy.context.window_manager.adWingsOuterFeathers)
    # If needed for feather lift, use axis 0
    for i in range(4, 16):  # Outer Wing
        u.rotate(u.strName, feather + str(i) + '.L', rad=featherRot, axis=2)
        u.rotate(u.strName, feather + str(i) + '.R', rad=-featherRot, axis=2)
    u.rotate(u.strName, "wings_J16.L", rad=featherRot, axis=2)
    u.rotate(u.strName, "wings_J16.R", rad=-featherRot, axis=2)
    for i in range(4, 16):
        bpy.context.object.data.bones[feather + str(i) + '.L'].select  = True
        bpy.context.object.data.bones[feather + str(i) + '.R'].select  = True
    bpy.context.object.data.bones["wings_J16.L"].select  = True
    bpy.context.object.data.bones["wings_J16.R"].select  = True
    bpy.ops.object.mode_set(mode='POSE')
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# END COMMON FUNCTION - setOuterFeathers
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# END FUNCTIONS FOR COMMON SHARED PARTS IN CHARACTERS
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#
# |
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Start Build Biped Skeleton      ENDS 2233
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def buildBipedSkeleton():
    biped = Biped
    bpy.types.WindowManager.speed = bpy.props.FloatProperty(update=u.setHorizontalSpeed, name="Speed", default=0.0)
    bpy.types.WindowManager.direction = bpy.props.FloatProperty(update=u.setHorizontalSpeed, name="Direction", default=0.0)
    bpy.types.WindowManager.cycle = bpy.props.FloatProperty(update=bipedFns.setBipedWalk, name="Cycle", default=1.0)
    bpy.types.WindowManager.swayLR = bpy.props.FloatProperty(update=bipedFns.setSwayLR, name="Sway LR", default=1.0)
    bpy.types.WindowManager.swayFB = bpy.props.FloatProperty(update=bipedFns.setSwayFB, name="Sway FB", default=0.0)
    bpy.types.WindowManager.bounce = bpy.props.FloatProperty(update=bipedFns.setBounce, name="Bounce", default=0.1)
    bpy.types.WindowManager.legSpread = bpy.props.FloatProperty(update=bipedFns.setLegSpread, name="Leg Spread", default=0.0)
    bpy.types.WindowManager.legArch = bpy.props.FloatProperty(update=bipedFns.setLegArch, name="Leg Arch", default=0.0)
    bpy.types.WindowManager.hipRotate = bpy.props.FloatProperty(update=bipedFns.setHip, name="Hip Rotate", default=2.0)
    bpy.types.WindowManager.hipSway = bpy.props.FloatProperty(update=bipedFns.setHip, name="Hip Sway", default=0.0)
    bpy.types.WindowManager.hipUD = bpy.props.FloatProperty(update=bipedFns.setHip, name="HipUD", default=2.0)
    bpy.types.WindowManager.skate = bpy.props.FloatProperty(update=bipedFns.setSkate, name="Skate", default=0.0)
    bpy.types.WindowManager.armsUD = bpy.props.FloatProperty(update=bipedFns.setArms, name="ArmsUD", default=0.0)
    bpy.types.WindowManager.shoulderRotate = bpy.props.FloatProperty(update=bipedFns.setShoulder, name="Shoulder Rotate", default=3.0)
    bpy.types.WindowManager.shoulderUD = bpy.props.FloatProperty(update=bipedFns.setShoulder, name="ShoulderUD", default=3.0)
    bpy.types.WindowManager.armTwistL = bpy.props.FloatProperty(update= bipedFns.setArmTwistL, name="L Arm Twist", default=0.0)
    bpy.types.WindowManager.armTwistR = bpy.props.FloatProperty(update= bipedFns.setArmTwistR, name="R Arm Twist", default=0.0)
    bpy.types.WindowManager.armRotation = bpy.props.FloatProperty(update=bipedFns.setArmRotation, name="Arm Rotation", default=3.0)
    bpy.types.WindowManager.LHandSpread = bpy.props.FloatProperty(update=bipedFns.setLHand, name="LHand Spread", default=0.0)
    bpy.types.WindowManager.LHandOC = bpy.props.FloatProperty(update=bipedFns.setLHand, name="LHandOC", default=0.0)
    bpy.types.WindowManager.RHandSpread = bpy.props.FloatProperty(update=bipedFns.setRHand, name="RHand Spread", default=0.0)
    bpy.types.WindowManager.RHandOC = bpy.props.FloatProperty(update=bipedFns.setRHand, name="RHandOC", default=0.0)
    bpy.types.WindowManager.headUD = bpy.props.FloatProperty(update=bipedFns.setHead, name="HeadUD", default=0.0)
    bpy.types.WindowManager.headLR = bpy.props.FloatProperty(update=bipedFns.setHead, name="HeadLR", default=0.0)
    bpy.types.WindowManager.headTurn = bpy.props.FloatProperty(update=bipedFns.setHead, name="HeadTurn", default=0.0)
    bpy.types.WindowManager.jawOC = bpy.props.FloatProperty(update=bipedFns.setJaw, name="JawOC", default=0.0)
    bpy.types.WindowManager.eyeLR = bpy.props.FloatProperty(update=bipedFns.setEye, name="EyeLR", default=0.0)
    bpy.types.WindowManager.eyeUD = bpy.props.FloatProperty(update=bipedFns.setEye, name="EyeUD", default=0.0)
    # Advanced Controls %%%% RP = Rotate position  RR = Rotate range  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    bpy.types.WindowManager.femurJ1RP = bpy.props.FloatProperty(update=bipedFns.setBipedWalk, name="femurJ1RP", default=0.0)
    bpy.types.WindowManager.femurJ1RR = bpy.props.FloatProperty(update=bipedFns.setBipedWalk, name="femurJ1RR", default=1.0)
    bpy.types.WindowManager.tibiaJ1RP = bpy.props.FloatProperty(update=bipedFns.setBipedWalk, name="tibiaJ1RP", default=0.0)
    bpy.types.WindowManager.tibiaJ1RR = bpy.props.FloatProperty(update=bipedFns.setBipedWalk, name="tibiaJ1RR", default=1.0)
    bpy.types.WindowManager.ankleRP = bpy.props.FloatProperty(update=bipedFns.setBipedWalk, name="ankleRP", default=0.0)
    bpy.types.WindowManager.ankleRR = bpy.props.FloatProperty(update=bipedFns.setBipedWalk, name="ankleRR", default=1.0)
    bpy.types.WindowManager.toesRP = bpy.props.FloatProperty(update=bipedFns.setBipedWalk, name="toesRP", default=-0.0)
    bpy.types.WindowManager.toesRR = bpy.props.FloatProperty(update=bipedFns.setBipedWalk, name="toesRR", default=1.0)
    # 
    # Initiate building of bones
    n = u.getSceneObjectNumber()  # Each character name will be numbered sequentially.
    u.strName = u.setName('biped', n)  # biped, quadruped, bird, centaur, spider, kangaroo
    #
    #
    mod = math.fmod(n, 2)
    if(mod == 0):
        x = 1.1 * n - mod
    else:
        x = 1.1 * -n - mod
    y = -.4 * n; z = 1.04  # buildRootArmature(type, strCharName, x, y, z) type is the character class
    at = u.buildRootArmature(biped, u.strName, x, y, z) # Start character armature and bones
    Vtail = [0.0, -0.3, 0]  # End location of handle relative to armature origin - this effects coordinate system
    bone = u.setHandle(at, u.strName, Vtail)
    bpy.data.objects[u.strName].show_x_ray = True
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
    bpy.context.scene.objects.active = ob
    ob.select = True
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #  END BIPED SKELETON BUILD
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


def buildBirdSkeleton():  # START BUILDING SKELETON %%%%%%%%%%%%%%%%%%%%%
    bpy.types.WindowManager.speed = bpy.props.FloatProperty(update=u.setHorizontalSpeed, name="Bird Speed", default=0.0)
    bpy.types.WindowManager.direction = bpy.props.FloatProperty(update=u.setHorizontalSpeed, name="Direction", default=0.0)
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
    # 
    # Initiate building of bones
    n = u.getSceneObjectNumber()  # Each character name will be numbered sequentially.
    u.strName = u.setName('bird', n)  # biped, quadruped, bird, centaur, spider, kangaroo
    mod = math.fmod(n, 2)
    if(mod == 0):
        x = 1.1 * n - mod
    else:
        x = 1.1 * -n - mod
    y = -.4 * n; z = 1.36  # buildRootArmature(type, strCharName, x, y, z) type is the character class
    at = u.buildRootArmature(bird, u.strName, x, y, z) # Start character armature and bones
    Vtail = [0.0, -0.3, 0]  # End location of handle relative to armature origin - this effects coordinate system
    bone = u.setHandle(at, u.strName, Vtail)
    bpy.data.objects[u.strName].show_x_ray = True
    #
    #
    VbackCenterTip = (0, -0.1, -.15)
    backCenter = u.createBone("backCenter", bone.head, VbackCenterTip)
    backCenter.parent = at.edit_bones[u.strName + '_bone']
    VbackL1 = (0, -0.15, -.15)
    u.boneMirror(at, VbackL1, False)
    VbackL2 = (0, -0.1, -.1)
    u.boneMirror(at, VbackL2, False)
    VbackL3 = (0, -0.1, -.04)
    u.boneMirror(at, VbackL3, False)
    VtailJ1 = (0, -0.1, -.04)
    u.boneMirror(at, VtailJ1, False)    
    VtailJ2 = (0, -.1, 0)
    u.boneMirror(at, VtailJ2, False)
    VtailJ3 = (0, -.06, 0)
    u.boneMirror(at, VtailJ3, False)
    at.edit_bones['backCenter.001'].name = "backL1"
    at.edit_bones['backCenter.002'].name = "backL2"
    at.edit_bones['backCenter.003'].name = "backL3"
    at.edit_bones['backCenter.004'].name = "tailJ1"
    at.edit_bones['backCenter.005'].name = "tailJ2"
    at.edit_bones['backCenter.006'].name = "tailJ3"
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["tailJ3"].select_tail=True
    Vfb1 = (0.022, .024, 0)
    u.boneMirror(at, Vfb1, True)
    Vfb2 = (0.022, .024, 0)
    u.boneMirror(at, Vfb2, True)
    Vfb3 = (0.022, .024, 0)
    u.boneMirror(at, Vfb3, True)
    Vfb4 = (0.022, .024, 0)
    u.boneMirror(at, Vfb4, True)
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
    u.boneMirror(at, Vfa1, False)  # fa = Feather attach
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["fb1.R"].select_tail=True
    Vfa2 = (0, -.08, 0)  
    u.boneMirror(at, Vfa2, True)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["fb2.R"].select_tail=True
    Vfa3 = (0, -.08, 0)  
    u.boneMirror(at, Vfa3, True)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["fb3.R"].select_tail=True
    Vfa3 = (0, -.08, 0)  
    u.boneMirror(at, Vfa3, True)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["fb4.R"].select_tail=True
    Vfa4 = (0, -.08, 0)  
    u.boneMirror(at, Vfa4, True)
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
    b = u.createBone("neck01", V_origin, Vneck01)
    b.parent = at.edit_bones['backCenter']
    Vneck02 = (0, .04, 0.04)
    u.boneMirror(at, Vneck02, False)
    Vneck03 = (0, .03, .04)
    u.boneMirror(at, Vneck03, False)
    Vneck04 = (0, .02, .04)
    u.boneMirror(at, Vneck04, False)
    Vneck05 = (0, 0, .04)
    u.boneMirror(at, Vneck05, False)
    Vneck06 = (0, 0, .04)
    u.boneMirror(at, Vneck06, False)
    VheadBase = (0, -.03, .05)
    u.boneMirror(at, VheadBase, False)
    at.edit_bones['neck01.001'].name = "neck02"
    at.edit_bones['neck01.002'].name = "neck03"
    at.edit_bones['neck01.003'].name = "neck04"
    at.edit_bones['neck01.004'].name = "neck05"
    at.edit_bones['neck01.005'].name = "neck06"
    at.edit_bones['neck01.006'].name = "headBase"
    #
    VheadTop = (0, 0.17, .03)
    u.boneMirror(at, VheadTop, False)
    Vcrest = (0, -.1, .08)
    u.boneMirror(at, Vcrest, False)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones['headBase.001'].name = "headTop"
    at.edit_bones['headBase.002'].name = "crest"
    #
    at.edit_bones["neck06"].select_tail=True
    Vjaw1 = (0, .08, -.03)
    u.boneMirror(at, Vjaw1, False)
    Vjaw2 = (0, .03, -.05)
    u.boneMirror(at, Vjaw2, False)
    Vjaw3 = (0, 0.109, .053)
    u.boneMirror(at, Vjaw3, False)
    Vjaw4 = (0, 0.13, -.028)
    u.boneMirror(at, Vjaw4, False)
    Vjaw4 = (0, 0.12, -.026)
    u.boneMirror(at, Vjaw4, False)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones['neck06.001'].name = "jaw1"
    at.edit_bones['neck06.002'].name = "jaw2"
    at.edit_bones['neck06.003'].name = "jaw3"
    at.edit_bones['neck06.004'].name = "jaw4"
    at.edit_bones['neck06.005'].name = "jaw5"
    #
    at.edit_bones["jaw1"].select_tail=True
    VbeakBase = (0, 0.08, .07)
    u.boneMirror(at, VbeakBase, False)
    Vbeak1 = (0, 0.16, 0)
    u.boneMirror(at, Vbeak1, False)
    Vbeak2 = (0, 0.18, -.05)
    u.boneMirror(at, Vbeak2, False)
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
    u.boneMirror(at, VeyeBase, True)
    Veye = (0, .02, 0)
    u.boneMirror(at, Veye, True)
    at.edit_bones['headBase_L'].name = "baseEye.L"
    at.edit_bones['headBase_R'].name = "baseEye.R"
    at.edit_bones['headBase_L.001'].name = "eye.L"
    at.edit_bones['headBase_R.001'].name = "eye.R"
    bpy.ops.armature.select_all(action='DESELECT')
    #
    at.edit_bones["neck01"].select_tail=True
    Vffix1 = (0, 0.06, -.1)
    u.boneMirror(at, Vffix1, False)
    Vffix2 = (0, -.05, -.1)
    u.boneMirror(at, Vffix2, False)
    Vffix3 = (0, -.07, -.1)
    u.boneMirror(at, Vffix3, False)
    Vffix4 = (0, -.08, -.1)
    u.boneMirror(at, Vffix4, False)
    Vffix5 = (0, -.09, -.1)
    u.boneMirror(at, Vffix5, False)
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
    u.boneMirror(at, VhipBase, False)
    at.edit_bones['backL2.001'].name = "hipBase"
    Vhip = (.18, 0, 0)
    u.boneMirror(at, Vhip, True)
    VhipBone = (0, .01, -0.12)
    u.boneMirror(at, VhipBone, True)
    VfemurJ1 = (0, -0.02, -0.12)
    u.boneMirror(at, VfemurJ1, True)
    VfemurJ2 = (0, -0.02, -0.12)
    u.boneMirror(at, VfemurJ2, True)
    VfemurJ3 = (0, 0, -0.12)
    u.boneMirror(at, VfemurJ3, True)
    VlegJ5 = (0, .01, -.1)
    u.boneMirror(at, VlegJ5, True)
    VtibiaJ2 = (0, .01, -.1)
    u.boneMirror(at, VtibiaJ2, True)
    VtibiaJ3 = (0, .01, -.11)
    u.boneMirror(at, VtibiaJ3, True)
    Vankle = (0, .01, -.05)
    u.boneMirror(at, Vankle, True)
    VrearToeJ1 = (-.016, -0.07, .01)
    u.boneMirror(at, VrearToeJ1, True)
    VrearToeJ2 = (-.015, -0.07, 0)
    u.boneMirror(at, VrearToeJ2, True)
    VrearToeJ3 = (-.015, -0.07, 0)
    u.boneMirror(at, VrearToeJ3, True)
    VrearToeJ4 = (-.015, -0.07, 0)
    u.boneMirror(at, VrearToeJ4, True)
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
    u.boneMirror(at, VcenterToe, True)
    u.boneMirror(at, VcenterToe, True)
    u.boneMirror(at, VcenterToe, True)
    u.boneMirror(at, VcenterToe, True)
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
    u.boneMirror(at, VouterToe, True)
    u.boneMirror(at, VouterToe, True)
    u.boneMirror(at, VouterToe, True)
    u.boneMirror(at, VouterToe, True)
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
    u.boneMirror(at, VinnerToe, True)
    u.boneMirror(at, VinnerToe, True)
    u.boneMirror(at, VinnerToe, True)
    u.boneMirror(at, VinnerToe, True)
    at.edit_bones['ankle.L.001'].name = "innerToeJ1.L"
    at.edit_bones['ankle.R.001'].name = "innerToeJ1.R"
    at.edit_bones['ankle.L.002'].name = "innerToeJ2.L"
    at.edit_bones['ankle.R.002'].name = "innerToeJ2.R"
    at.edit_bones['ankle.L.003'].name = "innerToeJ3.L"
    at.edit_bones['ankle.R.003'].name = "innerToeJ3.R"
    at.edit_bones['ankle.L.004'].name = "innerToeJ4.L"
    at.edit_bones['ankle.R.004'].name = "innerToeJ4.R"
    #
    setEnvelopeWeights()
    u.deselectAll()
    ob = bpy.data.objects.get(u.strName)
    bpy.context.scene.objects.active = ob
    ob.select = True
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # End Bird Build Skeleton  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def buildCentaurSkeleton():      # ENDS 2800
    V_origin = [0.0, 0.0, 0.0]
    centaur = Centaur
    u = Utils
    bpy.types.WindowManager.speed = bpy.props.FloatProperty(update=u.setHorizontalSpeed, name="Speed", default=0.0)
    bpy.types.WindowManager.direction = bpy.props.FloatProperty(update=u.setHorizontalSpeed, name="Direction", default=0.0)
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
    #
    #
    # Initiate building of bones
    n = u.getSceneObjectNumber()  # Each character name will be numbered sequentially.
    u.strName = u.setName('centaur', n)  # biped, centaur, bird, centaur, spider, kangaroo
    mod = math.fmod(n, 2)
    if(mod == 0):
        x = 1.1 * n - mod
    else:
        x = 1.1 * -n - mod
    y = -.4 * n; z = 1.14  # For Armature
    at = u.buildRootArmature(centaur, u.strName, x, y, z) # Start character armature and bones
    # Build root bone
    Vtail = [0, 0, 0.3]  # End location of handle relative to armature origin - this effects coordinate system
    bone = u.setHandle(at, u.strName, Vtail)
    bpy.data.objects[u.strName].show_x_ray = True
    #
    #
    buildQuadrupedBase(at)
    #
    V_bBackJ1 = (0, .032, 0.1)
    buildHumanUpperBody(at, V_bBackJ1)
    setEnvelopeWeights()
    # 
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.data.objects[u.strName].location[2] = z  # 1.14
    bpy.data.objects[u.strName].show_x_ray = True
    centaur.armature = at
    u.deselectAll()
    ob = bpy.data.objects.get(u.strName)
    bpy.context.scene.objects.active = ob
    ob.select = True
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #  END CENTAUR SKELETON BUILD
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


def buildQuadrupedSkeleton():
    V_origin = [0.0, 0.0, 0.0]
    quadruped = Quadruped
    u = Utils
    bpy.types.WindowManager.speed = bpy.props.FloatProperty(update=u.setHorizontalSpeed, name="Speed", default=0.0)
    bpy.types.WindowManager.direction = bpy.props.FloatProperty(update=u.setHorizontalSpeed, name="Direction", default=0.0)
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
    #
    #
    # Initiate building of bones
    n = u.getSceneObjectNumber()  # Each character name will be numbered sequentially.
    u.strName = u.setName('quadruped', n)  # biped, quadruped, bird, quadruped, spider, kangaroo   
    mod = math.fmod(n, 2)
    if(mod == 0):
        x = 1.1 * n - mod
    else:
        x = 1.1 * -n - mod
    y = -.4 * n; z = 1.04  # For Armature
    at = u.buildRootArmature(quadruped, u.strName, x, y, z) # Start character armature and bones
    # Build root bone
    Vtail = [0, 0, 0.3]  # End location of handle relative to armature origin - this effects coordinate system
    bone = u.setHandle(at, u.strName, Vtail)
    bpy.data.objects[u.strName].show_x_ray = True
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
    u.boneMirror(at, V_qNeckJ1, False)
    V_qNeckJ2 = (0, .05, 0.1)
    u.boneMirror(at, V_qNeckJ2, False)
    V_qNeckJ3 = (0, .05, 0.14)
    u.boneMirror(at, V_qNeckJ3, False)
    V_qNeckJ4 = (0, .05, .1)
    u.boneMirror(at, V_qNeckJ4, False)
    V_qNeckJ5 = (0, .05, .1)
    u.boneMirror(at, V_qNeckJ5, False)
    V_qNeckJ6 = (0, .05, .1)
    u.boneMirror(at, V_qNeckJ6, False)
    at.edit_bones['qBackJ0.001'].name = "bNeckJ1"
    at.edit_bones['qBackJ0.002'].name = "bNeckJ2"
    at.edit_bones['qBackJ0.003'].name = "bNeckJ3"
    at.edit_bones['qBackJ0.004'].name = "bNeckJ4"
    at.edit_bones['qBackJ0.005'].name = "bNeckJ5"
    at.edit_bones['qBackJ0.006'].name = "bNeckJ6"
    #
    # Start head
    V_headBase = (0, 0, 0.09)
    u.boneMirror(at, V_headBase, False)
    V_eyeLevel = (0, 0, .04)
    u.boneMirror(at, V_eyeLevel, False)
    V_headTop = (0, -.05, 0)
    u.boneMirror(at, V_headTop, False)
    V_headFore = (0, .08, .09)
    u.boneMirror(at, V_headFore, False)
    at.edit_bones['bNeckJ6.001'].name = "headBase"
    at.edit_bones['bNeckJ6.002'].name = "eyeLevel"
    at.edit_bones['bNeckJ6.003'].name = "headTop"
    at.edit_bones['bNeckJ6.004'].name = "headFore"
    # ears
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["eyeLevel"].select_tail=True
    V_earRoot = (.05, -.06, .06)
    u.boneMirror(at, V_earRoot, True)
    V_earBase = (0, -.02, .02)
    u.boneMirror(at, V_earBase, True)
    V_earJ1 = (0, -.015, .015)
    u.boneMirror(at, V_earJ1, True)
    V_earJ2 = (0, -.015, .015)
    u.boneMirror(at, V_earJ2, True)
    V_earJ3 = (0, -.015, .015)
    u.boneMirror(at, V_earJ3, True)
    V_earJ4 = (0, -.015, .015)
    u.boneMirror(at, V_earJ4, True)
    V_earJ5 = (0, -.015, .015)
    u.boneMirror(at, V_earJ5, True)
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
    u.boneMirror(at, V_baseJaw, False)
    V_jaw = (0, .02, 0)
    u.boneMirror(at, V_jaw, False)
    V_jaw1 = (.03, .01, 0)
    u.boneMirror(at, V_jaw1, True)
    V_jaw2 = (-.02, .07, 0)
    u.boneMirror(at, V_jaw2, True)
    at.edit_bones['bNeckJ6.001'].name = "baseJaw"
    at.edit_bones['bNeckJ6.002'].name = "jaw"
    at.edit_bones['bNeckJ6.002_R'].name = "jaw1.L"
    at.edit_bones['bNeckJ6.002_L'].name = "jaw1.R"
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
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # BUILD HEAD AND NECK
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #
    #
    setEnvelopeWeights()
    #
    bpy.ops.object.mode_set(mode='OBJECT')
    # 
    #
    bpy.data.objects[u.strName].location[2] = 1.14  # z
    bpy.data.objects[u.strName].show_x_ray = True
    bpy.ops.object.mode_set(mode='OBJECT')
    quadruped.armature = at
    u.deselectAll()
    ob = bpy.data.objects.get(u.strName)
    bpy.context.scene.objects.active = ob
    ob.select = True
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # End Build Quadruped Skeleton 
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    
    
def buildSpiderSkeleton():  # START BUILDING SKELETON %%%%%%%%%%%%%%%%%%%%%
    bpy.types.WindowManager.speed = bpy.props.FloatProperty(update=spiderFns.setSpiderWalk, name="Speed", default=0.0)
    bpy.types.WindowManager.direction = bpy.props.FloatProperty(update=spiderFns.setSpiderWalk, name="Direction", default=0.0)
    bpy.types.WindowManager.cycle = bpy.props.FloatProperty(update=spiderFns.setSpiderWalk, name="Cycle", default=6.0)
    n = u.getSceneObjectNumber()  # Each character name will be numbered sequentially.
    u.strName = u.setName('spider', n)  # biped, quadruped, bird, centaur, spider, kangaroo
    mod = math.fmod(n, 2)
    if(mod == 0):
        x = 1.1 * n - mod
    else:
        x = 1.1 * -n - mod
    y = -.4 * n; z = .1  # buildRootArmature(type, strCharName, x, y, z) type is the character class
    at = u.buildRootArmature(spider, u.strName, x, y, z) # Start character armature and bones
    Vtail = [0, 0.0, 0.6]  # End location of handle relative to armature origin - this effects coordinate system
    bone = u.setHandle(at, u.strName, Vtail)
    bpy.data.objects[u.strName].show_x_ray = True
    Vradius1 = (0, .254, 0)
    radius1 = u.createBone("radius1", bone.head, Vradius1)
    radius1.parent = at.edit_bones[u.strName + '_bone']
    Vframe = (.2, 0, 0)
    u.boneMirror(at, Vframe, mirror=True)
    Vframe = (0, 0, .062)
    u.boneMirror(at, Vframe, mirror=True)
    Vframe = (.2, 0, .082)
    u.boneMirror(at, Vframe, mirror=True)
    Vframe = (.4, 0, -.2)
    u.boneMirror(at, Vframe, mirror=True)
    Vframe = (.1, 0, 0)
    u.boneMirror(at, Vframe, mirror=True)
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
    radius3 = u.createBone("radius3", bone.head, Vradius3)
    radius3.parent = at.edit_bones[u.strName + '_bone']
    Vframe = (.22, 0, 0)
    u.boneMirror(at, Vframe, mirror=True)
    Vframe = (0, 0, .062)
    u.boneMirror(at, Vframe, mirror=True)
    Vframe = (.2, 0, .082)
    u.boneMirror(at, Vframe, mirror=True)
    Vframe = (.4, 0, -.2)
    u.boneMirror(at, Vframe, mirror=True)
    Vframe = (.1, 0, 0)
    u.boneMirror(at, Vframe, mirror=True)
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
    at.edit_bones[u.strName + '_bone'].select_tail=True
    bpy.ops.object.mode_set(mode='POSE')
    #bpy.data.objects[u.strName].pose.bones[u.strName + '_bone'].rotation_euler[1] = 1.5708
    #u.rotate(u.strName, u.strName + '_bone', 1.5708, 1)
    #x = y = 2.0 * n;
    VOrigin = (0, 0, .02)
    Vradius2 = (.254, 0, 0)
    radius2 = u.createBone("radius2", VOrigin, Vradius2)
    radius2.parent = at.edit_bones[u.strName + '_bone']
    Vframe = (0, .082, 0)
    u.boneMirror(at, Vframe, mirror=False)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["radius2"].select_tail=True
    Vframe = (0, -.082, 0)
    u.boneMirror(at, Vframe, mirror=False)
    Vframe = (0, 0, .062)
    u.boneMirror(at, Vframe, mirror=False)
    Vframe = (.2, 0, .082)
    u.boneMirror(at, Vframe, mirror=False)
    Vframe = (.4, 0, -.2)
    u.boneMirror(at, Vframe, mirror=False)
    Vframe = (.1, 0, 0)
    u.boneMirror(at, Vframe, mirror=False)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["radius2.001"].select_tail=True
    Vframe = (0, 0, .062)
    u.boneMirror(at, Vframe, mirror=False)
    Vframe = (.2, 0, .082)
    u.boneMirror(at, Vframe, mirror=False)
    Vframe = (.4, 0, -.2)
    u.boneMirror(at, Vframe, mirror=False)
    Vframe = (.1, 0, 0)
    u.boneMirror(at, Vframe, mirror=False)
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
    radius4 = u.createBone("radius4", VOrigin, Vradius4)
    radius4.parent = at.edit_bones[u.strName + '_bone']
    Vframe = (0, .082, 0)
    u.boneMirror(at, Vframe, mirror=False)
    Vframe = (0, 0, .062)
    u.boneMirror(at, Vframe, mirror=False)
    Vframe = (-.2, 0, .082)
    u.boneMirror(at, Vframe, mirror=False)
    Vframe = (-.4, 0, -.2)
    u.boneMirror(at, Vframe, mirror=False)
    Vframe = (-.1, 0, 0)
    u.boneMirror(at, Vframe, mirror=False)
    bpy.ops.armature.select_all(action='DESELECT')
    at.edit_bones["radius4"].select_tail=True
    Vframe = (0, -.082, 0)
    u.boneMirror(at, Vframe, mirror=False) # frame
    Vframe = (0, 0, .062)
    u.boneMirror(at, Vframe, mirror=False) # sideToSide
    Vframe = (-.2, 0, .082)
    u.boneMirror(at, Vframe, mirror=False)
    Vframe = (-.4, 0, -.2)
    u.boneMirror(at, Vframe, mirror=False)
    Vframe = (-.1, 0, 0)
    u.boneMirror(at, Vframe, mirror=False)
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
    u.boneMirror(at, Vframe, mirror=False)
    Vframe = (0, -.26, 0)
    u.boneMirror(at, Vframe, mirror=False)
    Vframe = (0, -.26, 0)
    u.boneMirror(at, Vframe, mirror=False)
    Vframe = (0, -.26, 0)
    u.boneMirror(at, Vframe, mirror=False)
    at.edit_bones['radius3.001'].name = "tail1"
    at.edit_bones['radius3.002'].name = "tail2"
    at.edit_bones['radius3.003'].name = "tail3"
    at.edit_bones['radius3.004'].name = "tail4"
    #
    for b in bpy.data.objects[u.strName].pose.bones:
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
    u.deselectAll()
    ob = bpy.data.objects.get(u.strName)
    bpy.context.scene.objects.active = ob
    ob.select = True
    bpy.ops.object.mode_set(mode='OBJECT')
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # End Build Spider Skeleton
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Start Build Wings
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def buildWings():  # START BUILDING WINGS %%%%%%%%%%%%%%%%%%%%%
    bpy.types.WindowManager.adWingsSpeed = bpy.props.FloatProperty(update=activateWings, name="Solo Wing Speed", default=1.0)
    bpy.types.WindowManager.adWingsRP = bpy.props.FloatProperty(update=activateWings, name="Wing Rot Position", default=0.0)
    bpy.types.WindowManager.adWingsRR = bpy.props.FloatProperty(update=activateWings, name="Wing Rot Range", default=3.0, min=0.0)
    bpy.types.WindowManager.adWingsCurveUD = bpy.props.FloatProperty(update=activateWings, name="wingsCurveUD", default=0.0)
    bpy.types.WindowManager.adWingsCurveFB = bpy.props.FloatProperty(update=activateWings, name="wingsCurveFB", default=0.0)
    bpy.types.WindowManager.adWingsFB = bpy.props.FloatProperty(update=setFwdBackwardPosition, name="Solo WingFB", default=0.0)
    bpy.types.WindowManager.adWingsAxial = bpy.props.FloatProperty(update=setAxialPosition, name="WingAxial", default=0.0)
    bpy.types.WindowManager.adWingsInnerFeathers = bpy.props.FloatProperty(update=setInnerFeathers, name="Rot Inner Feathers", default=0.0)
    bpy.types.WindowManager.adWingsOuterFeathers = bpy.props.FloatProperty(update=setOuterFeathers, name="Rot Outer Feathers", default=0.0)
    # 
    # Initiate building of bones
    n = u.getSceneObjectNumber()  # Each character name will be numbered sequentially.
    u.strName = u.setName('adWings', n)  # biped, quadruped, bird, centaur, spider, kangaroo
    x = 0; y = -.8 - n * .2; z = 1.9
    at = u.buildRootArmature(bird, u.strName, x, y, z) # Start character armature and bones
    Vtail = [0.0, 0.4, 0]  # End location of handle relative to armature origin - this effects coordinate system
    bone = u.setHandle(at, u.strName, Vtail)
    bpy.data.objects[u.strName].show_x_ray = True
    #
    #
    # Build wings shared part between bird and solo wings xxx2
    createWings(at)
    u.deselectAll()
    ob = bpy.data.objects.get(u.strName)
    bpy.context.scene.objects.active = ob
    ob.select = True
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# End Build Wings
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# End Build Skeleton Functions
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# |
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Start Character Operations Functions
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class BipedFns(object):
    def setCycleRates(self, context):
        u.getSelectedCharacterName()
        u.cycle = 8.0  # Default cycle
        if(hasattr(bpy.types.WindowManager, "cycle")):
            u.cycle = bpy.context.window_manager.cycle + 8
        u.strCycleRate = "sin(radians(" + str(u.cycle) + "*frame))"  # String form of cycle equation
        u.strHalfCycleRate = "sin(radians(" + str(u.cycle / 2) + "*frame))"  # String form of halfcyclespeed equation
        u.strDoubleCycleRate = "sin(radians(" + str(u.cycle * 2) + "*frame))" # Double Speed
        u.strQuadrupleCycleRate = "sin(radians(" + str(u.cycle * 4) + "*frame))"
        u.strCyclePhased = "sin(radians(-" + biped.phase + "+" + str(u.cycle) + "*frame))"
    #
    #
    def setBipedWalk(self, context):
        u.getSelectedCharacterName()
        ob = bpy.data.objects.get(u.strName)
        biped = Biped
        biped.phase = "-1.2"
        bipedFns.setCycleRates(self, context)
        u.strx0AtFrame0 = "*(frame * (1/(frame+.01)))"  # produce a zero at frame zero, otherwise a one
        #
        # KEY: RP = Rotate Position  RR = Rotate Range
        # femurJ1
        if(hasattr(bpy.types.WindowManager, "femurJ1RP")):
            u.femurJ1RP = str(bpy.context.window_manager.femurJ1RP)
        if(hasattr(bpy.types.WindowManager, "femurJ1RR")):
            u.femurJ1RR = str(bpy.context.window_manager.femurJ1RR)
        femurJ1PP = "0.0" # Static pose position
        #
        fnFemurL = "(.02 + (-(asin(" + u.strCycleRate + ")))* .3)"
        fnL = "(" + u.femurJ1RP + "+" + u.femurJ1RR + "*" + fnFemurL + ")" + u.strx0AtFrame0
        u.setDriver(u.getEuler('femurJ1.L'), "-1*" + fnL, 0)  
        # Rotate Range caused bad pose position! Fix was using parenthesis to isolate strx0AtFrame0 
        fnFemurR = "(.02 + ((asin(" + u.strCycleRate + ")))* .3)"
        fnR = "(" + u.femurJ1RP + "+" + u.femurJ1RR + "*" + fnFemurR + ")" + u.strx0AtFrame0
        u.setDriver(u.getEuler('femurJ1.R'), "-1*" + fnR, 0)
        # tibiaJ1
        if(hasattr(bpy.types.WindowManager, "tibiaJ1RP")):
            u.tibiaJ1RP = str(bpy.context.window_manager.tibiaJ1RP)
        if(hasattr(bpy.types.WindowManager, "tibiaJ1RR")):
            u.tibiaJ1RR = str(bpy.context.window_manager.tibiaJ1RR)
        eqL1 = u.tibiaJ1RP + " - 0.4 + pow(atan(" + u.strHalfCycleRate + "),2)"
        eqL2 = "pow(-atan(" + u.strHalfCycleRate + "),2)/8"
        fnL = "(.2 + " + eqL1 + " * 1.9 - " + eqL2 + ") * -1 *" + str(u.tibiaJ1RR)
        u.setAxisDriver(u.getEuler('tibiaJ1.L'), fnL + u.strx0AtFrame0, 0)
        eqR1 = u.tibiaJ1RP + "- 0.4 - pow(atan(" + u.strHalfCycleRate + "),2)"
        eqR2 = "pow(-atan(" + u.strHalfCycleRate + "),2)/8"
        fnR = "(1.4 + " + eqR1 + " * 1.9 - " + eqR2 + ") * -1 *" + str(u.tibiaJ1RR)
        u.setAxisDriver(u.getEuler('tibiaJ1.R'), fnR + u.strx0AtFrame0, 0)
        # Ankles
        fnFemurL = "(-.2 + (-(asin(" + u.strCyclePhased + ")))* .3)"
        # For Pose at frame zero - Override function on frame zero, allowing for posing.
        if(hasattr(bpy.types.WindowManager, "ankleRP")):
            u.ankleRP = str(bpy.context.window_manager.ankleRP)
        if(hasattr(bpy.types.WindowManager, "ankleRR")):
            u.ankleRR = str(bpy.context.window_manager.ankleRR)
        fnL = "((" + str(u.ankleRP) + "+" + fnFemurL + "+1.5)*.04)*" + str(u.ankleRR)
        u.setAxisDriver(u.getEuler('ankle.L'), fnL + u.strx0AtFrame0, 0)
        fnR = "((" + str(u.ankleRP) + "+" + fnFemurR + "+1.5)*.04)*" + str(u.ankleRR)
        u.setAxisDriver(u.getEuler('ankle.R'), fnR + u.strx0AtFrame0, 0)
        # Toes
        if(hasattr(bpy.types.WindowManager, "toesRP")):
            u.toesRP = str(bpy.context.window_manager.toesRP)
        toesRR = "1.0"  # Default rotate range
        if(hasattr(bpy.types.WindowManager, "toesRR")):
            u.toesRR = str(bpy.context.window_manager.toesRR)
        toesPP = "0.0"   # Static pose position
        fnL = "-.6*(.1+" + u.toesRP + "+" + u.toesRR + ")*" + fnFemurR
        #fnL = "(-.9 + " + u.toesRP + "(asin(" + u.strCycleRate + "))* .3 * " + u.toesRR + " + .5)"
        u.setAxisDriver(u.getEuler('toe.L'), fnL + u.strx0AtFrame0, 0)
        fnR = "-.6*(.1+" + u.toesRP + "+" + u.toesRR + ")*" + fnFemurL
        #fnR = "(-.9 + " + u.toesRP + "(asin(" + u.strCycleRate + "))* .3 * " + u.toesRR + " + .5)"
        u.setAxisDriver(u.getEuler('toe.R'), fnR + u.strx0AtFrame0, 0)
        # 
        #
        # Upper Back
        fn = "(asin(" + u.strCycleRate + ") * .6)/3.14"
        bBackJ4Driver = u.setDriver(u.getEuler('bBackJ4'), fn, 1)
        # Compensate for shoulder rotate by rotating neck and head in opposite direction, in three parts
        fn = "-(asin(" + u.strCycleRate + ") * .2)/3.14"
        neckJ2Driver = u.setDriver(u.getEuler('neckJ2'), fn, 1)
        neckJ3Driver = u.setDriver(u.getEuler('neckJ3'), fn, 1)
        neckJ4Driver = u.setDriver(u.getEuler('neckJ4'), fn, 1)
        # Arms rotation
        armRotation = '3.0'
        if(hasattr(bpy.types.WindowManager, "armRotation")):
            armRotation = str(bpy.context.window_manager.armRotation * .2)
        fn = "(asin(" + u.strCycleRate + ") * .8)/3.14"
        armJLDriver = u.setAxisDriver(u.getEuler('armJ1.L'), fn, 1)  # 1 was
        armJRDriver = u.setAxisDriver(u.getEuler('armJ1.R'), fn, 1)  # 1 was
        # Elbows
        fn = "((asin(" + u.strCycleRate + ") * .7)/3.14 - .3) * (frame*(1/(frame+.0001)))"
        radiusLDriver = u.setAxisDriver(u.getEuler('armJ3.L'), fn, 2)
        fn = "((asin(" + u.strCycleRate + ") * .7)/3.14 + .3) * (frame*(1/(frame+.0001)))"
        radiusRDriver = u.setAxisDriver(u.getEuler('armJ3.R'), fn, 2)
        bpy.context.object.pose.bones["armJ1.L"].rotation_euler[0] = -1.5708
        bpy.context.object.pose.bones["armJ1.R"].rotation_euler[0] = -1.5708
        ob.select = True
        bpy.ops.object.mode_set(mode='OBJECT')
        #
        #
    def unsetBipedWalk(self, context):
        u.getSelectedCharacterName()
        for b in bpy.data.objects[u.strName].pose.bones:
            b.driver_remove('rotation_euler', -1)
        #
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
        #
    # This is for restoring advanced control defaults for each bone in the leg: 
    # RP = Rotate Position
    # RR = Rotate Range
    def revertAdvancedControls(self, context):
        # bird.unsetBipedWalk(self, context)
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
        #
        #
        #
    def setArmRotation(self, context):
        u.getSelectedCharacterName()
        armRotation = '3.0'
        if(hasattr(bpy.types.WindowManager, "armRotation")):
            armRotation = str(bpy.context.window_manager.armRotation * .2)
        # Arms rotation
        fn = "-(asin(" + u.strCycleRate + ") * " + armRotation + ")/3.14"
        armJLDriver = u.setAxisDriver(u.getEuler('armJ1.L'), fn, 1)
        fn = "-(asin(" + u.strCycleRate + ") * " + armRotation + ")/3.14"
        armJRDriver = u.setAxisDriver(u.getEuler('armJ1.R'), fn, 1)
        # Elbows
        fn = "-((asin(" + u.strCycleRate + ") * " + armRotation + ")/3.14 + .3) * (frame*(1/(frame+.0001)))"
        radiusLDriver = u.setAxisDriver(u.getEuler('armJ3.L'), fn, 2)
        fn = "-((asin(" + u.strCycleRate + ") * " + armRotation + ")/3.14 - .3) * (frame*(1/(frame+.0001)))"
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
        fn = "-(asin(" + u.strCycleRate + ")* " + u.swayLR + "*.01)"
        # bBackJ1
        u.setDriver(u.getEuler('bBackJ1'), fn, 2)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
    def setSwayFB(self, context):  # forward - backward sway movement
        u.getSelectedCharacterName()
        if(hasattr(bpy.types.WindowManager, "swayFB")):
            u.swayFB = str(bpy.context.window_manager.swayFB)
        fn = "-(asin(" + u.strCycleRate + ")* " + u.swayFB + "*.01)"
        u.setDriver(u.getEuler('bBackJ1'), fn, 0)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
    def setBounce(self, context):  # Bounce
        u.getSelectedCharacterName()
        bounce = "1.0"
        if(hasattr(bpy.types.WindowManager, "bounce")):
            u.bounce = str(bpy.context.window_manager.bounce)
        eqBounce = "-(asin(" + u.strCycleRate + ")* " + u.bounce + "*.01)"
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
        fn = "-(asin(" + u.strCycleRate + ") * " + u.skate + ")/3.14"
        u.setAxisDriver(u.getEuler('femurJ1.L'), fn, 2)
        fn = "-(asin(" + u.strCycleRate + ") * " + u.skate + ")/3.14"
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
    # If centered at rear joint, parented,
    # can be used  for eye movements
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
        fn = "-(asin(" + u.strCycleRate + ") * .2)/3.14 + " + u.headTurn
        neckJ2Driver = u.setAxisDriver(u.getEuler('neckJ2'), fn, 1)
        neckJ3Driver = u.setAxisDriver(u.getEuler('neckJ3'), fn, 1)
        neckJ4Driver = u.setAxisDriver(u.getEuler('neckJ4'), fn, 1)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
        #
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
        #
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
        #
        #
    def setShoulder(self, context):
        u.getSelectedCharacterName()
        if(hasattr(bpy.types.WindowManager, "shoulderRotate")):
            u.shoulderRotate = str(bpy.context.window_manager.shoulderRotate*.1)
        # Upper Back
        fn = "(asin(" + u.strCycleRate + ") * " + shoulderRotate + ")/3.14"
        bBackJ4Driver = u.setDriver(u.getEuler('bBackJ4'), fn, 1)
        # Compensate for shoulder rotate by rotating neck and head in opposite direction, in three parts
        fn = "-(asin(" + u.strCycleRate + ") * " + u.shoulderRotate + "/3)/3.14"
        neckJ2Driver = u.setDriver(u.getEuler('neckJ2'), fn, 1)
        neckJ3Driver = u.setDriver(u.getEuler('neckJ3'), fn, 1)
        neckJ4Driver = u.setDriver(u.getEuler('neckJ4'), fn, 1)
        # Shoulder up - down movement
        if(hasattr(bpy.types.WindowManager, "shoulderUD")):
            u.shoulderUD = str(bpy.context.window_manager.shoulderUD*.06)
        fn = "(asin(" + u.strCycleRate + ") * " + u.shoulderUD + ")/3.14"
        u.setDriver(u.getEuler('shoulder.L'), fn, 0)
        fn = "-(asin(" + u.strCycleRate + ") * " + u.shoulderUD + ")/3.14"
        u.setDriver(u.getEuler('shoulder.R'), fn, 0)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
        #
    def setHip(self, context):
        u.getSelectedCharacterName()
        # Hip sway
        if(hasattr(bpy.types.WindowManager, "hipSway")):
            u.hipSway = str(bpy.context.window_manager.hipSway*.1)
        fn = "(asin(" + u.strCycleRate + ") * " + u.hipSway + ")/3.14"
        u.setDriver(u.getEuler('pelvis'), fn, 2) # was 0
        # Pelvis / Hip rotation    
        if(hasattr(bpy.types.WindowManager, "hipRotate")):
            u.hipRotate = str(bpy.context.window_manager.hipRotate*.1)
        fn = "(asin(" + u.strCycleRate + ") * " + u.hipRotate + ")/3.14"
        u.setDriver(u.getEuler('pelvis'), fn, 1)
        # hip up - down movement
        if(hasattr(bpy.types.WindowManager, "hipUD")):
            u.hipUD = str(bpy.context.window_manager.hipUD*.06)
        fn = "(asin(" + u.strCycleRate + ") * " + u.hipUD + ")/3.14"
        u.setDriver(u.getEuler('hip.L'), fn, 0)
        fn = "-(asin(" + u.strCycleRate + ") * " + u.hipUD + ")/3.14"
        u.setDriver(u.getEuler('hip.R'), fn, 0)
        bpy.ops.object.mode_set(mode='OBJECT')
        ob = bpy.data.objects.get(u.strName)
        bpy.context.scene.objects.active = ob
        ob.select = True
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # End of BipedFns CLASS
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class BirdFns:
    def setWalk(self, context):  
        u.getSelectedCharacterName()
        u.mode = "walk"  # Options: walk, run or hop
        u.swayLR = 0.4
        u.swayFB =0.0
        u.bounce = 1.0
        u.neckFB = 6.0
        u.wingsSpeed = 1.0
        u.tailUD = 0.0
        u.hipRP = 0
        u.hipRR = 1.0
        u.femurJ1RR = 1.0
        u.ankleRP = 0
        u.ankleRR = 1
        u.toesRP = 0
        u.toesRR = 1
        birdFns.setNeck(self, context)
        u.cycle = 14.0
        birdFns.setDriversAction(self, context)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
    def setRun(self, context):
        birdFns.unsetClaws(self, context)
        u.getSelectedCharacterName()
        u.swayLR = 2.0
        u.swayFB = 1.0
        u.bounce = 4.0
        u.neckFB = 9.0
        u.wingsSpeed = 1.6
        u.tailUD = 6.0
        u.femurJ1RR = 1.8
        u.cycle = 28.0
        birdFns.setNeck(self, context)
        birdFns.setDriversAction(self, context)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
    def setHop(self, context):
        birdFns.unsetClaws(self, context)
        u.getSelectedCharacterName()
        u.bounce = 18.0
        u.swayLR = 1.0
        u.neckFB = 4.0
        u.wingsSpeed = 1.0
        u.tailUD = 0.0
        u.femurJ1RR = 1.0
        u.cycle = 14.0
        birdFns.setNeck(self, context)
        # 
        # Bounce
        fn = "(asin(" + u.strCycleRate + ") * " + str(u.bounce) + "* .01)"
        u.setDriver(u.getEuler(u.strName + '_bone'), fn, 2, 'location')
        # 
        # Neck FB movement
        if(hasattr(bpy.types.WindowManager, "neckFB")):
            u.neckFB = str(bpy.context.window_manager.neckFB)
        fn = "-(asin(" + u.strCycleRate + ")* " + u.neckFB + "*.04)"  
        u.setDriver(u.getEuler('neck02'), fn, 0)
        fn = ".2-(asin(" + u.strCycleRate + ")* " + u.neckFB + "*.04)"  
        u.setDriver(u.getEuler('neck03'), fn, 0)
        fn = "-(asin(" + u.strCycleRate + ")* " + u.neckFB + "*.02)"
        u.setDriver(u.getEuler('neck04'), fn, 0)
        fn = "-(asin(" + u.strCycleRate + ")* " + u.neckFB + "*.02)"
        u.setDriver(u.getEuler('neck05'), fn, 0)
        fn = "-.2-(asin(" + u.strCycleRate + ")* " + u.neckFB + "*-.08)"
        u.setDriver(u.getEuler('neck06'), fn, 0)
        # 
        # setHop
        # Hip
        fnFemur = "-(asin(" + u.strCycleRate + ")) * .3"
        u.setDriver(u.getEuler('femurJ1.L'), fnFemur + u.strx0AtFrame0, 0)  
        u.setDriver(u.getEuler('femurJ1.R'), fnFemur + u.strx0AtFrame0, 0)  
        #
        # Tibia
        eq1 = "pow(atan(" + u.strHalfCycleRate + "),2)"
        eq2 = "pow(-atan(" + u.strHalfCycleRate + "),2)/8"
        fn = "(-.4 + " + eq1 + " * 2.2 - " + eq2 + ")"
        u.setDriver(u.getEuler('tibiaJ1.R'), fn + u.strx0AtFrame0, 0)
        u.setDriver(u.getEuler('tibiaJ1.L'), fn + u.strx0AtFrame0, 0)
        #
        # Ankle
        fn = "(" + fnFemur + " - 1.2) * .4"
        u.setAxisDriver(u.getEuler('ankle.L'), fn + u.strx0AtFrame0, 0)
        u.setAxisDriver(u.getEuler('ankle.R'), fn + u.strx0AtFrame0, 0)
        #
        # setHop
        # Foot Joint2 Toes Walk Movement
        toesPP = "-0.26"   # Static pose position
        eq = ".24 - atan(" + u.strCycleRate + ") * -.4"
        fn = eq + u.strx0AtFrame0 + "+(" + toesPP + u.strx1AtFrame0 + ")"
        u.setDriver(u.getEuler('centerToeJ2.L'), fn)
        u.setDriver(u.getEuler('outerToeJ2.L'), fn)
        u.setDriver(u.getEuler('innerToeJ2.L'), fn)
        u.setDriver(u.getEuler('centerToeJ2.R'), fn)
        u.setDriver(u.getEuler('outerToeJ2.R'), fn)
        u.setDriver(u.getEuler('innerToeJ2.R'), fn)
        bpy.ops.object.mode_set(mode='OBJECT')
        # END setHop
    def setCycleRates(self, context):
        u.getSelectedCharacterName()
        if(not u.click):
            if(hasattr(bpy.types.WindowManager, "cycle")):
                u.cycle = bpy.context.window_manager.cycle + 8
        u.strCycleRate = "sin(radians(" + str(u.cycle) + "*frame))"  # String form of u.cycle equation
        u.strHalfCycleRate = "sin(radians(" + str(u.cycle / 2) + "*frame))"  # String form of halfcyclespeed equation
        u.strDoubleCycleRate = "sin(radians(" + str(u.cycle * 2) + "*frame))" # Double Speed
    #
    def setDriversAction(self, context):
        birdFns.unsetClaws(self, context)
        u.getSelectedCharacterName()
        birdFns.setCycleRates(self, context)
        if(hasattr(bpy.types.WindowManager, "swayLR")):
            u.swayLR = str(bpy.context.window_manager.swayLR)
        eqLR = "-(asin(" + u.strCycleRate + ")* " + str(u.swayLR) + "*.04)"
        ug = u.setDriver(u.getEuler(u.strName + '_bone'), eqLR, 1)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
        if(hasattr(bpy.types.WindowManager, "swayFB")):
            u.swayFB = str(bpy.context.window_manager.swayFB)
        eqFB = "-(asin(" + u.strCycleRate + ")* " + str(u.swayFB) + "*.04)"
        dr_SwayFB = u.setDriver(u.getEuler(u.strName + '_bone'), eqFB, 2)
        bpy.ops.object.mode_set(mode='OBJECT')
        # setDriversAction
        #
        if(hasattr(bpy.types.WindowManager, "bounce")):
            u.bounce = bpy.context.window_manager.bounce
        eqBounce = "-(asin(" + u.strDoubleCycleRate + ")* " + str(u.bounce) + "*.01)"
        u.setDriver(u.getEuler(u.strName + '_bone'), eqBounce, 2, 'location') # Bounce 1
        # KEY: RP = Rotate Position  RR = Rotate Range
        #
        # Femur
        if(hasattr(bpy.types.WindowManager, "femurJ1RP")):
            u.femurJ1RP = bpy.context.window_manager.femurJ1RP
        if(hasattr(bpy.types.WindowManager, "femurJ1RR")):
            u.femurJ1RR = bpy.context.window_manager.femurJ1RR
        femurJ1PP = "0.0"  # Static pose position
        fnFemurL = "(.2 + ((asin(" + u.strCycleRate + ")))* .3)"
        fnL = "(" + str(u.femurJ1RP) + "+" + str(u.femurJ1RR) + "*" + fnFemurL + ")"
        u.setDriver(u.getEuler('femurJ1.L'), fnL + u.strx0AtFrame0, 0)  
        fnFemurR = "(.2 + (-(asin(" + u.strCycleRate + ")))* .3)"
        fnR = "(" + str(u.femurJ1RP) + "+" + str(u.femurJ1RR) + "*" + fnFemurR + ")"
        u.setDriver(u.getEuler('femurJ1.R'), fnR + u.strx0AtFrame0, 0)
        #
        # setDriversAction
        # Tibia
        if(hasattr(bpy.types.WindowManager, "tibiaJ1RP")):
            u.tibiaJ1RP = str(bpy.context.window_manager.tibiaJ1RP)
        if(hasattr(bpy.types.WindowManager, "tibiaJ1RR")):
            u.tibiaJ1RR = str(bpy.context.window_manager.tibiaJ1RR)
        tibiaPP = "0.0"  # Static pose position
        eq1 = "+pow(atan(" + u.strHalfCycleRate + "),2)"
        eq2 = "-pow(-atan(" + u.strHalfCycleRate + "),2)/8"
        eq3 = str(u.tibiaJ1RP) + " + (-.5 " + eq1 + " * 2.2 " + eq2 + ")*" + str(u.tibiaJ1RR)
        fnL = eq3 + u.strx0AtFrame0 + "+(" + str(tibiaPP) + ")"
        u.setDriver(u.getEuler('tibiaJ1.L'), fnL + u.strx0AtFrame0, 0)   #   + "; if(frame==0):;fnL='0'", 0)
        eq1 = "-pow(atan(" + u.strHalfCycleRate + "),2)"
        eq2 = "+pow(-atan(" + u.strHalfCycleRate + "),2)/8"
        eq3 = str(u.tibiaJ1RP) + " + (.8 " + eq1 + " * 2.2 " + eq2 + ")*" + str(u.tibiaJ1RR)
        fnR = eq3 + u.strx0AtFrame0 + "+(" + str(tibiaPP) + ")"
        u.setDriver(u.getEuler('tibiaJ1.R'), fnR + u.strx0AtFrame0, 0)
        # setDriversAction
        #
        # Ankle
        if(hasattr(bpy.types.WindowManager, "ankleRP")):
            u.ankleRP = bpy.context.window_manager.ankleRP
        if(hasattr(bpy.types.WindowManager, "ankleRR")):
            u.ankleRR = bpy.context.window_manager.ankleRR
        fnL = "-.09 +(" + str(u.ankleRP) + "+" + fnFemurL + ")*.4 *" + str(u.ankleRR)
        u.setAxisDriver(u.getEuler('ankle.L'), fnL + u.strx0AtFrame0, 0)
        fnR = "-.09 +(" + str(u.ankleRP) + "+" + fnFemurL + ")*.4 *" + str(u.ankleRR)
        u.setAxisDriver(u.getEuler('ankle.R'), fnR + u.strx0AtFrame0, 0)
        # Prevent rear tarsal drag by using this equation too.
        u.setDriver(u.getEuler('rearToeJ1.L'), "-1 *" + fnR + u.strx0AtFrame0, 0)
        u.setDriver(u.getEuler('rearToeJ1.R'), "-1 *" + fnL + u.strx0AtFrame0, 0)
        #
        # setDriversAction
        # Foot Joint2 Toes Walk Movement
        if(hasattr(bpy.types.WindowManager, "toesRP")):
            u.toesRP = bpy.context.window_manager.toesRP
        if(hasattr(bpy.types.WindowManager, "toesRR")):
            u.toesRR = bpy.context.window_manager.toesRR
        toesPP = "-0.26"   # Static pose position
        eqR = str(u.toesRP) + "+.5+atan(" + u.strCycleRate + ") * .4 * " + str(u.toesRR)
        fn = eqR + u.strx0AtFrame0 + "+(" + toesPP + u.strx1AtFrame0 + ")"
        u.setDriver(u.getEuler('centerToeJ2.L'), fn)
        u.setDriver(u.getEuler('outerToeJ2.L'), fn)
        u.setDriver(u.getEuler('innerToeJ2.L'), fn)
        eqL = str(u.toesRP) + "+.5-atan(" + u.strCycleRate + ") * .4 * " + str(u.toesRR)
        fn = eqL + u.strx0AtFrame0 + "+(" + toesPP + u.strx1AtFrame0 + ")"
        u.setDriver(u.getEuler('centerToeJ2.R'), fn)
        u.setDriver(u.getEuler('outerToeJ2.R'), fn)
        u.setDriver(u.getEuler('innerToeJ2.R'), fn)
        bpy.ops.object.mode_set(mode='OBJECT')
        # END setDriversAction
    def unsetWalk(self, context):
        birdFns.unsetClaws(self, context)
        u.getSelectedCharacterName()
        u.bounce = 0
        undo = bpy.data.objects[u.strName].pose.bones[u.strName + '_bone']
        undo.driver_remove('rotation_euler', -1)
        undo.driver_remove('location', -1)
        undo = bpy.data.objects[u.strName].pose.bones['femurJ1.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['femurJ1.L']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['tibiaJ1.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['tibiaJ1.L']
        undo.driver_remove('rotation_euler', -1)       
        undo = bpy.data.objects[u.strName].pose.bones['ankle.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['ankle.L']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['centerToeJ2.L']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['outerToeJ2.L']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['innerToeJ2.L']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['centerToeJ2.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['outerToeJ2.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['innerToeJ2.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['neck02']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['neck03']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['neck04']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['neck05']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['neck06']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['headBase']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['headTop']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['rearToeJ1.L']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['rearToeJ1.R']
        undo.driver_remove('rotation_euler', -1)
    # ####
    def setClaws(self, context):
        u.getSelectedCharacterName()
        birdFns.unsetWalk(self, context)
        if(hasattr(bpy.types.WindowManager, "claws")):
            u.claws = -bpy.context.window_manager.claws * .1
        u.rotate(u.strName, 'rearToeJ1.L', u.claws, 0)
        u.rotate(u.strName, 'rearToeJ1.R', u.claws, 0)
        u.rotate(u.strName, 'rearToeJ2.L', u.claws, 0)
        u.rotate(u.strName, 'rearToeJ2.R', u.claws, 0)
        u.rotate(u.strName, 'rearToeJ3.L', u.claws, 0)
        u.rotate(u.strName, 'rearToeJ3.R', u.claws, 0)
        u.rotate(u.strName, 'rearToeJ4.L', u.claws, 0)
        u.rotate(u.strName, 'rearToeJ4.R', u.claws, 0)
        u.rotate(u.strName, 'outerToeJ1.L', u.claws * .08, 0)
        u.rotate(u.strName, 'outerToeJ1.R', u.claws * .08, 0)
        u.rotate(u.strName, 'outerToeJ2.L', u.claws, 0)
        u.rotate(u.strName, 'outerToeJ2.R', u.claws, 0)
        u.rotate(u.strName, 'outerToeJ3.L', u.claws, 0)
        u.rotate(u.strName, 'outerToeJ3.R', u.claws, 0)
        u.rotate(u.strName, 'outerToeJ4.L', u.claws, 0)
        u.rotate(u.strName, 'outerToeJ4.R', u.claws, 0)
        u.rotate(u.strName, 'innerToeJ1.L', u.claws * .08, 0)
        u.rotate(u.strName, 'innerToeJ1.R', u.claws * .08, 0)        
        u.rotate(u.strName, 'innerToeJ2.L', u.claws, 0)
        u.rotate(u.strName, 'innerToeJ2.R', u.claws, 0)
        u.rotate(u.strName, 'innerToeJ3.L', u.claws, 0)
        u.rotate(u.strName, 'innerToeJ3.R', u.claws, 0)
        u.rotate(u.strName, 'innerToeJ4.L', u.claws, 0)
        u.rotate(u.strName, 'innerToeJ4.R', u.claws, 0)
        u.rotate(u.strName, 'centerToeJ1.L', u.claws * .08, 0)
        u.rotate(u.strName, 'centerToeJ1.R', u.claws * .08, 0)
        u.rotate(u.strName, 'centerToeJ2.L', u.claws, 0)
        u.rotate(u.strName, 'centerToeJ2.R', u.claws, 0)
        u.rotate(u.strName, 'centerToeJ3.L', u.claws, 0)
        u.rotate(u.strName, 'centerToeJ3.R', u.claws, 0)
        u.rotate(u.strName, 'centerToeJ4.L', u.claws, 0)
        u.rotate(u.strName, 'centerToeJ4.R', u.claws, 0)
        clawsList = ["rearToeJ1", "rearToeJ2", "rearToeJ3", "rearToeJ4", 
            "outerToeJ1", "outerToeJ2", "outerToeJ3", "outerToeJ4", 
            "innerToeJ1", "innerToeJ2", "innerToeJ3", "innerToeJ4", 
             "centerToeJ1", "centerToeJ2", "centerToeJ3", "centerToeJ4"]
        bpy.ops.object.mode_set(mode='POSE')
        for bone in clawsList:
            bpy.context.object.data.bones[bone + ".L"].select  = True
            bpy.context.object.data.bones[bone + ".R"].select  = True
    #
    def unsetClaws(self, context):
        u.rotate(u.strName, 'rearToeJ1.L', 0, 0)
        u.rotate(u.strName, 'rearToeJ1.R', 0, 0)
        u.rotate(u.strName, 'rearToeJ2.L', 0, 0)
        u.rotate(u.strName, 'rearToeJ2.R', 0, 0)
        u.rotate(u.strName, 'rearToeJ3.L', 0, 0)
        u.rotate(u.strName, 'rearToeJ3.R', 0, 0)
        u.rotate(u.strName, 'rearToeJ4.L', 0, 0)
        u.rotate(u.strName, 'rearToeJ4.R', 0, 0)
        u.rotate(u.strName, 'outerToeJ1.L', 0, 0)
        u.rotate(u.strName, 'outerToeJ1.R', 0, 0)
        u.rotate(u.strName, 'outerToeJ2.L', 0, 0)
        u.rotate(u.strName, 'outerToeJ2.R', 0, 0)
        u.rotate(u.strName, 'outerToeJ3.L', 0, 0)
        u.rotate(u.strName, 'outerToeJ3.R', 0, 0)
        u.rotate(u.strName, 'outerToeJ4.L', 0, 0)
        u.rotate(u.strName, 'outerToeJ4.R', 0, 0)
        u.rotate(u.strName, 'innerToeJ1.L', 0, 0)
        u.rotate(u.strName, 'innerToeJ1.R', 0, 0)        
        u.rotate(u.strName, 'innerToeJ2.L', 0, 0)
        u.rotate(u.strName, 'innerToeJ2.R', 0, 0)
        u.rotate(u.strName, 'innerToeJ3.L', 0, 0)
        u.rotate(u.strName, 'innerToeJ3.R', 0, 0)
        u.rotate(u.strName, 'innerToeJ4.L', 0, 0)
        u.rotate(u.strName, 'innerToeJ4.R', 0, 0)
        u.rotate(u.strName, 'centerToeJ1.L', 0, 0)
        u.rotate(u.strName, 'centerToeJ1.R', 0, 0)
        u.rotate(u.strName, 'centerToeJ2.L', 0, 0)
        u.rotate(u.strName, 'centerToeJ2.R', 0, 0)
        u.rotate(u.strName, 'centerToeJ3.L', 0, 0)
        u.rotate(u.strName, 'centerToeJ3.R', 0, 0)
        u.rotate(u.strName, 'centerToeJ4.L', 0, 0)
        u.rotate(u.strName, 'centerToeJ4.R', 0, 0)
        bpy.ops.object.mode_set(mode='OBJECT')
    #
    def setTail(self, context):
        u.getSelectedCharacterName()
        if(hasattr(bpy.types.WindowManager, "tailUD")):
            u.tailUD = bpy.context.window_manager.tailUD * .1
        u.rotate(u.strName, "tailJ3", u.tailUD, 0)
        #
        if(hasattr(bpy.types.WindowManager, "tailRL")):
            u.tailRL = bpy.context.window_manager.tailRL * .1
        u.rotate(u.strName, "tailJ3", u.tailUD, 0)
        #
        if(hasattr(bpy.types.WindowManager, "tailSpread")):
            u.tailSpread = bpy.context.window_manager.tailSpread
        fn = u.tailSpread * .1
        u.rotate(u.strName, "fa1.L", -fn * .4, 2)
        u.rotate(u.strName, "fa1.R", fn * .4, 2)
        u.rotate(u.strName, "fa2.L", -fn * .6, 2)
        u.rotate(u.strName, "fa2.R", fn * .6, 2)
        u.rotate(u.strName, "fa3.L", -fn * .8, 2)
        u.rotate(u.strName, "fa3.R", fn * .8, 2)
        u.rotate(u.strName, "fa4.L", -fn, 2)
        u.rotate(u.strName, "fa4.R", fn, 2)
        bpy.ops.object.mode_set(mode='POSE')
        bpy.context.object.data.bones["tailJ3"].select  = True
        bpy.context.object.data.bones["fa1.L"].select  = True
        bpy.context.object.data.bones["fa1.R"].select  = True
        bpy.context.object.data.bones["fa2.L"].select  = True
        bpy.context.object.data.bones["fa2.R"].select  = True
        bpy.context.object.data.bones["fa3.L"].select  = True
        bpy.context.object.data.bones["fa3.R"].select  = True
        bpy.context.object.data.bones["fa4.L"].select  = True
        bpy.context.object.data.bones["fa4.R"].select  = True
        #
    # Head
    def setJaw(self, context):
        u.getSelectedCharacterName()
        if(hasattr(bpy.types.WindowManager, "jawOC")):
            u.jawOC = bpy.context.window_manager.jawOC * -.1
        u.rotate(u.strName, "jaw3", u.jawOC, 0)
        bpy.ops.object.mode_set(mode='POSE')
        bpy.context.object.data.bones["jaw3"].select  = True
        #
    # # Left - Right turn motion 
    def setEye(self, context):
        u.getSelectedCharacterName()
        if(hasattr(bpy.types.WindowManager, "eyeLR")):
            u.eyeLR = bpy.context.window_manager.eyeLR * .1
        u.rotate(u.strName, "eye.L", u.eyeLR, 2)
        u.rotate(u.strName, "eye.R", u.eyeLR, 2)
        # Up - Down turn motion 
        if(hasattr(bpy.types.WindowManager, "eyeUD")):
            u.eyeUD = bpy.context.window_manager.eyeUD * .1
        u.rotate(u.strName, "eye.L", u.eyeUD, 0)
        u.rotate(u.strName, "eye.R", u.eyeUD, 0)
        bpy.ops.object.mode_set(mode='POSE')
        bpy.context.object.data.bones["eye.L"].select  = True
        bpy.context.object.data.bones["eye.R"].select  = True
        #
    # If the bird has a crest, Forward - Backward
    def setCrest(self, context):
        u.getSelectedCharacterName()
        if(hasattr(bpy.types.WindowManager, "crestFB")):
            u.crestFB = bpy.context.window_manager.crestFB * .1
        u.rotate(u.strName, "crest", u.crestFB, 0)
        # Crest Left - Right
        if(hasattr(bpy.types.WindowManager, "crestLR")):
            u.crestLR = bpy.context.window_manager.crestLR * .1
        u.rotate(u.strName, "crest", u.crestLR, 2)
        bpy.ops.object.mode_set(mode='POSE')
        bpy.context.object.data.bones["crest"].select  = True
        #
        #
    # Restore advanced control defaults for each bone in the leg: 
    # RP = Rotate Position   RR = Rotate Range
    def revertAdvancedControls(self, context):
        u.getSelectedCharacterName()
        u.femurJ1RP = 0.0
        u.femurJ1RR = 1.0
        u.tibiaJ1RP = 0.0
        u.tibiaJ1RR = 1.0
        u.ankleRP = 1.4
        u.ankleRR = 1.0
        u.toesRP = -0.26
        u.toesRR = 1.0
        birdFns.setWalk(self, context)
        #
    def setSwayLR(self, context):  # left - right sway movement
        u.getSelectedCharacterName()
        if(hasattr(bpy.types.WindowManager, "swayLR")):
            u.swayLR = str(bpy.context.window_manager.swayLR)
        eq = "-(asin(" + u.strCycleRate + ")* " + u.swayLR + "*.04)"
        dr_swayLR = u.setDriver(u.getEuler(u.strName + '_bone'), eq, 1)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
    def setSwayFB(self, context):  # forward - backward sway movement
        u.getSelectedCharacterName()
        if(hasattr(bpy.types.WindowManager, "swayFB")):
            u.swayFB = str(bpy.context.window_manager.swayFB)
        eq = "-(asin(" + u.strCycleRate + ")* " + u.swayFB + "*.04)"
        dr_SwayFB = u.setDriver(u.getEuler(u.strName + '_bone'), eq, 0)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
    def setBounce(self, context):  # Bounce
        u.getSelectedCharacterName()
        u.bounce = str(bpy.context.window_manager.bounce)
        eqBounce = "-(asin(" + u.strDoubleCycleRate + ")* " + u.bounce + "*.01)"
        u.setDriver(u.getEuler(u.strName + '_bone'), eqBounce, 2, 'location') # Bounce
        bpy.ops.object.mode_set(mode='OBJECT')
    # End of functions that use cycle
    #
    # See common functions for wing functions
    # 
    def setLegSpread(self, context):
        u.getSelectedCharacterName()
        if(hasattr(bpy.types.WindowManager, "legSpread")):
            u.legSpread = bpy.context.window_manager.legSpread
        fn = "-radians(" + str(u.legSpread) + ")"
        ls = u.setDriver(u.getEuler('femurJ1.R'), fn, 2)
        fn = "radians(" + str(u.legSpread) + ")"
        ls2 = u.setDriver(u.getEuler('femurJ1.L'), fn, 2)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
    def setNeck(self, context):
        u.getSelectedCharacterName()
        # Neck FB movement
        if(hasattr(bpy.types.WindowManager, "neckFB")):
            u.neckFB = bpy.context.window_manager.neckFB
        fn = "-(asin(" + u.strDoubleCycleRate + ")* " + str(u.neckFB) + "*.02)"  
        u.setDriver(u.getEuler('neck02'), fn, 0)
        fn = ".2-(asin(" + u.strDoubleCycleRate + ")* " + str(u.neckFB) + "*.04)"  
        u.setDriver(u.getEuler('neck03'), fn, 0)
        fn = ".2-(asin(" + u.strDoubleCycleRate + ")* " + str(u.neckFB) + "*-.02)"
        u.setDriver(u.getEuler('neck04'), fn, 0)
        fn = "-.2-(asin(" + u.strDoubleCycleRate + ")* " + str(u.neckFB) + "*-.02)"
        u.setDriver(u.getEuler('neck05'), fn, 0)
        fn = "-.2-(asin(" + u.strDoubleCycleRate + ")* " + str(u.neckFB) + "*-.02)"
        u.setDriver(u.getEuler('neck06'), fn, 0)
        bpy.ops.object.mode_set(mode='OBJECT')
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # End of BirdFns CLASS
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# To 5520
class CentaurFns(object):
    def setCycleRates(self, context):
        u.getSelectedCharacterName()
        if(hasattr(bpy.types.WindowManager, "cycle")):
            u.cycle = bpy.context.window_manager.cycle + 8
        u.strCycleRate = "sin(radians(" + str(u.cycle) + "*frame))"  # String form of cycle equation
        u.strHalfCycleRate = "sin(radians(" + str(u.cycle / 2) + "*frame))"  # String form of halfcyclespeed equation
        u.strDoubleCycleRate = "sin(radians(" + str(u.cycle * 2) + "*frame))" # Double Speed
        u.strQuadrupleCycleRate = "sin(radians(" + str(u.cycle * 4) + "*frame))"
        u.strx0AtFrame0 = " * (frame * (1/(frame+.0001)))"  # produce a zero at frame zero, otherwise a one
        u.strx1AtFrame0 = " * abs((frame/(frame + .0001))-1)"  # produce a one at frame zero, otherwise a zero
        #        
        #
    def setCentaurWalk(self, context):
        u.getSelectedCharacterName()
        centaurFns.setCycleRates(self, context)
        #
        # KEY: RP = Rotate Position  RR = Rotate Range
        # FRONT LEG FUNCTIONS
        u.strx0AtFrame0 = " * (frame * (1/(frame+.0001)))"  # produce a zero at frame zero, otherwise a one
        u.strx1AtFrame0 = " * abs((frame/(frame + .0001))-1)"  # produce a one at frame zero, otherwise a zero
        if(hasattr(bpy.types.WindowManager, "femurJ1RP")):
            u.femurJ1RP = str(bpy.context.window_manager.femurJ1RP)
        if(hasattr(bpy.types.WindowManager, "femurJ1RR")):
            u.femurJ1RR = str(bpy.context.window_manager.femurJ1RR)
        eqR = "(" + u.femurJ1RP + "+(asin(" + u.strCycleRate + "))* .3 * " + u.femurJ1RR + ")"
        fnR = eqR + u.strx0AtFrame0 + "+(" + str(u.femurJ1PP) + u.strx1AtFrame0 + ")"
        u.setAxisDriver(u.getEuler('femurJ1.R'), fnR, 0)
        eqL = "(" + u.femurJ1RP + "-(asin(" + u.strCycleRate + "))* .3 * " + u.femurJ1RR + ")"
        fnL = eqL + u.strx0AtFrame0 + "+(" + str(u.femurJ1PP) + u.strx1AtFrame0 + ")"
        u.setAxisDriver(u.getEuler('femurJ1.L'), fnL, 0)
        #
        # setCentaurWalk
        # tibiaJ1
        if(hasattr(bpy.types.WindowManager, "tibiaJ1RP")):
            u.tibiaJ1RP = str(bpy.context.window_manager.tibiaJ1RP)
        if(hasattr(bpy.types.WindowManager, "tibiaJ1RR")):
            u.tibiaJ1RR = str(bpy.context.window_manager.tibiaJ1RR)
        eqL1 = u.tibiaJ1RP + " - 0.4 + pow(atan(" + u.strHalfCycleRate + "),2)"
        eqL2 = "pow(-atan(" + u.strHalfCycleRate + "),2)/8*" + u.tibiaJ1RR
        fnL = "(0.1 + " + eqL1 + " * 1.9 - " + eqL2 + ") * -1"
        u.setAxisDriver(u.getEuler('tibiaJ1.L'), fnL + u.strx0AtFrame0, 0)
        eqR1 = u.tibiaJ1RP + "- 0.4 - pow(atan(" + u.strHalfCycleRate + "),2)"
        eqR2 = "pow(-atan(" + u.strHalfCycleRate + "),2)/8*" + u.tibiaJ1RR
        fnR = "(1.3 + " + eqR1 + " * 1.9 - " + eqR2 + ") * -1"
        u.setAxisDriver(u.getEuler('tibiaJ1.R'), fnR + u.strx0AtFrame0, 0)
        #
        # setCentaurWalk
        # Front Ankles
        if(hasattr(bpy.types.WindowManager, "ankleRP")):
           u.ankleRP = bpy.context.window_manager.ankleRP * -.1
        ankleRR = "1.0"  # Default rotate range
        if(hasattr(bpy.types.WindowManager, "ankleRR")):
           u.ankleRR = bpy.context.window_manager.ankleRR
        eqR = "(-.9 + " + str(u.ankleRP) + "-(asin(" + u.strCycleRate + "))* .3 * " + str(u.ankleRR) + " + .5)"
        fnR = eqR + u.strx0AtFrame0 + "+(" + str(u.anklePP) + u.strx1AtFrame0 + ")"
        u.setAxisDriver(u.getEuler('ankle.R'), fnR, 0)
        eqL = "(-.9 + " + str(u.ankleRP) + "-(asin(" + u.strCycleRate + "))* .3 * " + str(u.ankleRR) + " + .5)"
        fnL = eqL + u.strx0AtFrame0 + "+(" + str(u.anklePP) + u.strx1AtFrame0 + ")"        
        u.setAxisDriver(u.getEuler('ankle.L'), fnL, 0)
        #
        # setCentaurWalk
        # Front Toes
        toesRP = "0.0"  # Default rotate position
        if(hasattr(bpy.types.WindowManager, "toesRP")):
            u.toesRP = bpy.context.window_manager.toesRP
        if(hasattr(bpy.types.WindowManager, "toesRR")):
            u.toesRR = bpy.context.window_manager.toesRR
        eqR = str(u.toesRP) + "+.4+atan(" + u.strCycleRate + ") * .6 * " + str(u.toesRR)
        fnR = eqR + u.strx0AtFrame0 + "+(-.26 + " + str(u.toesPP) + u.strx1AtFrame0 + ")"
        u.setAxisDriver(u.getEuler('toe.R'), fnR, 0)
        eqL = str(u.toesRP) + "+.4-atan(" + u.strCycleRate + ") * .6 * " + str(u.toesRR)
        fnL = eqL + u.strx0AtFrame0 + "+(-.26 + " + str(u.toesPP) + u.strx1AtFrame0 + ")"
        u.setAxisDriver(u.getEuler('toe.L'), fnL, 0)
        # END FRONT LEG FUNCTIONS
        #
        # setCentaurWalk
        #  REAR LEG FUNCTIONS
        rearFemurJ1RP = "0.0"  # Default rotate position
        if(hasattr(bpy.types.WindowManager, "rearFemurJ1RP")):
            rearFemurJ1RP = str((bpy.context.window_manager.rearFemurJ1RP + 1) * .4)
        rearFemurJ1RR = "1.0"  # Default rotate range
        if(hasattr(bpy.types.WindowManager, "rearFemurJ1RR")):
            rearFemurJ1RR = str(bpy.context.window_manager.rearFemurJ1RR)
        rearFemurJ1PP = "0.0" # Static pose position
        eqL = "(" + rearFemurJ1RP + "- 0.4 -(asin(" + u.strCycleRate + "))* .3 * " + rearFemurJ1RR + ")"
        fnL = eqL + u.strx0AtFrame0 + "+(" + rearFemurJ1PP + u.strx1AtFrame0 + ")"
        u.setAxisDriver(u.getEuler('rearFemurJ1.L'), fnL, 0)
        eqR = "(" + rearFemurJ1RP + "- 0.4 +(asin(" + u.strCycleRate + "))* .3 * " + rearFemurJ1RR + ")"
        fnR = eqR + u.strx0AtFrame0 + "+(" + rearFemurJ1PP + u.strx1AtFrame0 + ")"
        u.setAxisDriver(u.getEuler('rearFemurJ1.R'), fnR, 0)
        #
        # setCentaurWalk
        # Rear rearTibiaJ1s AKA Tibia
        rearTibiaJ1RP = "13.6"  # Default rotate position
        if(hasattr(bpy.types.WindowManager, "rearTibiaJ1RP")):
            u.rearTibiaJ1RP = bpy.context.window_manager.rearTibiaJ1RP + 13.6 * -.1
        rearTibiaJ1RR = "1.2"  # Default rotate range
        if(hasattr(bpy.types.WindowManager, "rearTibiaJ1RR")):
            u.rearTibiaJ1RR = bpy.context.window_manager.rearTibiaJ1RR * 1.2
        eq1 = str(u.rearTibiaJ1RP) + " - 0.4 + pow(atan(" + u.strHalfCycleRate + "),2)"
        eq2 = "pow(-atan(" + u.strHalfCycleRate + "),2)/8"
        eqL1 = "(1.0 + " + eq1 + " * 2.2 - " + eq2 + ")"
        eqL2 = eqL1 + u.strx0AtFrame0 + "+(" + str(u.rearTibiaJ1PP) + u.strx1AtFrame0 + ")"
        fnL = "(" + eqL2 + ")" + " * -1 * " + str(u.rearTibiaJ1RR)
        u.setAxisDriver(u.getEuler('rearTibiaJ1.L'), fnL, 0)
        eq1 = str(u.rearTibiaJ1RP) + " +1.2 + pow(atan(" + u.strHalfCycleRate + "),2)"
        eq2 = "pow(+atan(" + u.strHalfCycleRate + "),2)/8"
        eqR1 = "(-.3 + " + eq1 + " * 2.2 - " + eq2 + ")"
        eqR2 = eqR1 + u.strx0AtFrame0 + "+(" + str(u.rearTibiaJ1PP) + u.strx1AtFrame0 + ")"
        fnR = "(" + eqR2 + ") * " + str(u.rearTibiaJ1RR)
        u.setAxisDriver(u.getEuler('rearTibiaJ1.R'), fnR, 0)
        #
        #
        # setCentaurWalk
        # Rear Ankles
        rearAnkleRP = "0.0"  # Default rotate position
        if(hasattr(bpy.types.WindowManager, "rearAnkleRP")):
            u.rearAnkleRP = str(bpy.context.window_manager.rearAnkleRP * -.1)
        if(hasattr(bpy.types.WindowManager, "rearAnkleRR")):
            u.rearAnkleRR = str(bpy.context.window_manager.rearAnkleRR)
        fnL = "(-2.2 + " + u.rearAnkleRP + "+ 1.3 -(asin(" + u.strCycleRate + "))* -.3 * " + u.rearAnkleRR + ")"
        u.setAxisDriver(u.getEuler('rearAnkle.L'), fnL + u.strx0AtFrame0, 0)
        fnR = "(-2.2 + " + u.rearAnkleRP + "+ 1.3 +(asin(" + u.strCycleRate + "))* -.3 * " + u.rearAnkleRR + ")"
        u.setAxisDriver(u.getEuler('rearAnkle.R'), fnR + u.strx0AtFrame0, 0)
        #
        # setCentaurWalk
        # Rear Toes
        if(hasattr(bpy.types.WindowManager, "rearToesRP")):
            u.rearToesRP = str(bpy.context.window_manager.rearToesRP * -.1)
        if(hasattr(bpy.types.WindowManager, "rearToesRR")):
            u.rearToesRR = str(bpy.context.window_manager.rearToesRR)
        eqL = u.rearToesRP + "-.2+atan(" + u.strCycleRate + ") * .6 * " + u.rearToesRR
        fn = eqL + u.strx0AtFrame0 + "+(" + str(u.rearToesPP) + u.strx1AtFrame0 + ")"
        u.setAxisDriver(u.getEuler('rearToe.L'), fn + u.strx0AtFrame0, 0)
        eqR = u.rearToesRP + "-.2-atan(" + u.strCycleRate + ") * .6 * " + u.rearToesRR
        fn = eqR + u.strx0AtFrame0 + "+(" + str(u.rearToesPP) + u.strx1AtFrame0 + ")"
        u.setAxisDriver(u.getEuler('rearToe.R'), fn + u.strx0AtFrame0, 0)
        bpy.ops.object.mode_set(mode='OBJECT')
        # END REAR LEG FUNCTIONS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # 
        # setCentaurWalk
        # UPPER BACK FUNCTIONS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        fn = "(asin(" + u.strCycleRate + ") * .6)/3.14"
        bBackJ4Driver = u.setAxisDriver(u.getEuler('bBackJ4'), fn, 1)
        # Compensate for shoulder rotate by rotating neck and head in opposite direction, in three parts
        fn = "-(asin(" + u.strCycleRate + ") * .2)/3.14"
        neckJ2Driver = u.setAxisDriver(u.getEuler('neckJ2'), fn, 1)
        neckJ3Driver = u.setAxisDriver(u.getEuler('neckJ3'), fn, 1)
        neckJ4Driver = u.setAxisDriver(u.getEuler('neckJ4'), fn, 1)
        #
        # setCentaurWalk
        # Arms rotation
        bpy.context.object.pose.bones["armJ1.R"].rotation_euler[0] = -1.5708
        fn = "(asin(" + u.strCycleRate + ") * .8)/3.14"
        armJRDriver = u.setAxisDriver(u.getEuler('armJ1.R'), fn, 1)
        armJLDriver = u.setAxisDriver(u.getEuler('armJ1.L'), fn, 1)
        bpy.context.object.pose.bones["armJ1.L"].rotation_euler[0] = -1.5708
        bpy.context.object.pose.bones["armJ1.R"].rotation_euler[0] = -1.5708
        # Elbows
        fn = "((asin(" + u.strCycleRate + ") * .7)/3.14 - .3) * (frame*(1/(frame+.0001)))"
        radiusLDriver = u.setDriver(u.getEuler('armJ3.L'), fn, 2) 
        fn = "((asin(" + u.strCycleRate + ") * .7)/3.14 + .3) * (frame*(1/(frame+.0001)))"
        radiusRDriver = u.setDriver(u.getEuler('armJ3.R'), fn, 2)
        bpy.ops.object.mode_set(mode='OBJECT')
        # Set rearHipJ1R, rearHipJ1L, qfix3, qfix4
        centaurFns.setHip(self, context)
        # END UPPER BACK FUNCTIONS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%        
        # END setCentaurWalk
        #
        # This uses presets like the other gait changers, but also requires actual modification
        # of some of the equations to get the leg movement right.
    def setGallop(self, context):
        u.getSelectedCharacterName()
        centaurFns.unsetCentaurWalk(self, context)
        centaurFns.setCycleRates(self, context)
        #
        # setGallop
        # FRONT LEG GALLOP FUNCTIONS
        # Joint 1
        u.femurJ1RR = 1.2  # Set in panel to show the change
        leg_J1PP = "0.0" # Static pose position
        fnL = "(.6 * " + u.strCycleRate + " + 0.5 +(asin(" + u.strCycleRate + "))* .3 * " + str(u.femurJ1RR) + ")"
        u.setAxisDriver(u.getEuler('femurJ1.L'), fnL + u.strx0AtFrame0, 0)
        fnR = "(.1 * " + u.strCycleRate + " + 0.5 +(asin(" + u.strCycleRate + "))* .3 * " + str(u.femurJ1RR) + ")"
        u.setAxisDriver(u.getEuler('femurJ1.R'), fnR + u.strx0AtFrame0, 0)
        #
        # setGallop
        # Joint 2
        if(hasattr(bpy.types.WindowManager, "tibiaJ1RP")):
            u.tibiaJ1RP = str(bpy.context.window_manager.tibiaJ1RP)
        if(hasattr(bpy.types.WindowManager, "tibiaJ1RR")):
            u.tibiaJ1RR = str(bpy.context.window_manager.tibiaJ1RR)
        leg_J2PP = "0.0"  # Static pose position
        eq1 = u.tibiaJ1RP + "- 0.4 - pow(atan(" + u.strHalfCycleRate + "),2)"
        eq2 = "pow(-atan(" + u.strHalfCycleRate + "),2)/8"
        eqL1 = "-(.6 + " + eq1 + " * 2.2 - " + eq2 + ")"
        eqL2 = eqL1 + u.strx0AtFrame0 + "+(" + leg_J2PP + u.strx1AtFrame0 + ")"
        fnL = "(" + eqL2 + ") * " + u.tibiaJ1RR
        u.setAxisDriver(u.getEuler('tibiaJ1.L'), fnL + "*-1", 0)
        # eq1 and eq2 same as above
        eqR1 = "(.6 + " + eq1 + " * 2.2 - " + eq2 + ")"
        eqR2 = eqR1 + u.strx0AtFrame0 + "+(" + leg_J2PP + u.strx1AtFrame0 + ")"
        fnR = "(" + eqR2 + ")" + " * -1 * " + u.tibiaJ1RR
        u.setAxisDriver(u.getEuler('tibiaJ1.R'), fnR + "*-1", 0)
        #
        # setGallop
        # Front Ankles
        if(hasattr(bpy.types.WindowManager, "ankleRP")):
            u.ankleRP = bpy.context.window_manager.ankleRP
        if(hasattr(bpy.types.WindowManager, "ankleRR")):
            u.ankleRR = bpy.context.window_manager.ankleRR
        #anklePP = "-1.2"  # Static pose position
        eqL = "(-1.9 + " + str(u.ankleRP) + "+ 1.3 -(asin(" + u.strCycleRate + "))* .3 * " + str(u.ankleRR) + ")"
        fnL = eqL + u.strx0AtFrame0 + "+(" + str(u.anklePP) + u.strx1AtFrame0 + ")"
        u.setAxisDriver(u.getEuler('ankle.L'), fnL + u.strx0AtFrame0, 0)
        eqR = "(-2.0 + " + str(u.ankleRP) + "+ 1.3 -(asin(" + u.strCycleRate + "))* .3 * " + str(u.ankleRR) + ")"
        fnR = eqR + u.strx0AtFrame0 + "+(" + str(u.anklePP) + u.strx1AtFrame0 + ")"
        u.setAxisDriver(u.getEuler('ankle.R'), fnR + u.strx0AtFrame0, 0)
        # setGallop
        # Front Toes
        toesRP = "0.0"  # Default rotate position
        if(hasattr(bpy.types.WindowManager, "toesRP")):
            toesRP = bpy.context.window_manager.toesRP
        if(hasattr(bpy.types.WindowManager, "toesRR")):
            u.toesRR = bpy.context.window_manager.toesRR
        eqL = "(-1.8 + " + str(u.toesRP) + "+ 1.3 -(asin(" + u.strCycleRate + "))* .3 * " + str(u.toesRR) + ")"
        fnL = eqL + u.strx0AtFrame0 + "+(" + str(u.toesPP) + u.strx1AtFrame0 + ")"
        u.setAxisDriver(u.getEuler('toe.L'), fnL, 0)
        eqR = "(-2.0 + " + str(u.toesRP) + "+ 1.3 +(asin(" + u.strCycleRate + "))* .3 * " + str(u.toesRR) + ")"
        fnR = eqR + u.strx0AtFrame0 + "+(" + str(u.toesPP) + u.strx1AtFrame0 + ")"
        u.setAxisDriver(u.getEuler('toe.R'), fnR, 0)
        # END FRONT LEG FUNCTIONS
        #
        #
        # setGallop
        # REAR LEG FUNCTIONS
        bpy.data.window_managers['WinMan'].hipRotate = 2.0 # Set in panel to show the change
        hipRotate = "2.0"
        fn = "-(asin(" + u.strCycleRate + ") * .2 * " + hipRotate + ")/3.14" 
        u.setAxisDriver(u.getEuler('rearHip.L'), fn, 2)
        u.setAxisDriver(u.getEuler('rearHip.R'), fn, 2)
        #
        # fixs 4 and 5 are rear leg muscle manipulators
        legRotation = ".8 * " + fn
        u.setAxisDriver(u.getEuler('qfixHind1.L'), legRotation, 0)
        u.setAxisDriver(u.getEuler('qfixHind1.L'), legRotation, 0)
        u.setAxisDriver(u.getEuler('qfixHind2.R'), legRotation, 0)
        u.setAxisDriver(u.getEuler('qfixHind2.R'), legRotation, 0)
        #
        rearFemurJ1RP = "-0.1"  # Default rotate position
        if(hasattr(bpy.types.WindowManager, "rearFemurJ1RP")):
            rearFemurJ1RP = str((bpy.context.window_manager.rearFemurJ1RP + 1) * .4)
        rearFemurJ1RR = "1.0"
        rearFemurJ1PP = "0.0" # Static pose position
        eqL = "-(.5 * " + u.strCycleRate + "- 0.3 +(asin(" + u.strCycleRate + "))* .24 * " + rearFemurJ1RR + ")"
        fnL = "-.2 +" + eqL + u.strx0AtFrame0 + "+(" + rearFemurJ1PP + u.strx1AtFrame0 + ")"
        u.setAxisDriver(u.getEuler('rearFemurJ1.L'), fnL, 0)
        eqR = "-.4-(.1 * " + u.strCycleRate + "- 0.3 +(asin(" + u.strCycleRate + "))* .24 * " + rearFemurJ1RR + ")"
        fnR = eqR + u.strx0AtFrame0 + "+(" + rearFemurJ1PP + u.strx1AtFrame0 + ")"
        u.setAxisDriver(u.getEuler('rearFemurJ1.R'), fnR, 0)
        #
        # setGallop
        # Rear rearTibiaJ1s
        # rearTibiaJ1RP = "13.6"  # Default rotate position
        if(hasattr(bpy.types.WindowManager, "rearTibiaJ1RP")):
            u.rearTibiaJ1RP = str(bpy.context.window_manager.rearTibiaJ1RP + 13.6 * -.1)
        #rearTibiaJ1RR = "1.2"  # Default rotate range
        if(hasattr(bpy.types.WindowManager, "rearTibiaJ1RR")):
            u.rearTibiaJ1RR = str(bpy.context.window_manager.rearTibiaJ1RR * 1.2)
        eq1 = u.rearTibiaJ1RP + " - 1.2 + pow(atan(" + u.strHalfCycleRate + "),2)"
        eq2 = "pow(-atan(" + u.strHalfCycleRate + "),2)/8"
        #
        fnL = "(2.1 + " + eq1 + " * 2.2 - " + eq2 + ")" + " * " + u.rearTibiaJ1RR
        u.setAxisDriver(u.getEuler('rearTibiaJ1.L'), fnL + u.strx0AtFrame0, 0)
        fnR = "(1.8 + " + eq1 + " * 2.2 - " + eq2 + ")" + " * " + u.rearTibiaJ1RR
        u.setAxisDriver(u.getEuler('rearTibiaJ1.R'), fnR + u.strx0AtFrame0, 0)
        #
        # setGallop
        # Rear Ankles
        if(hasattr(bpy.types.WindowManager, "rearAnkleRP")):
            u.rearAnkleRP = str(bpy.context.window_manager.rearAnkleRP * -.1)
        if(hasattr(bpy.types.WindowManager, "rearAnkleRR")):
            u.rearAnkleRR = str(bpy.context.window_manager.rearAnkleRR)
        #rearAnklePP = "-0.6"  # Static pose position
        # use above equations
        eqL = "(-2.4 + " + u.rearAnkleRP + "+ 1.3 +(asin(" + u.strCycleRate + "))* .3 * " + u.rearAnkleRR + ")"
        fnL = eqL + u.strx0AtFrame0 + "+(" + str(u.rearAnklePP) + u.strx1AtFrame0 + ")"
        u.setAxisDriver(u.getEuler('rearAnkle.L'), fnL, 0)
        # eq2 is the same
        eqR = "(-2.4 + " + u.rearAnkleRP + "+ 1.3 +(asin(" + u.strCycleRate + "))* .3 * " + u.rearAnkleRR + ")"
        fnR = eqR + u.strx0AtFrame0 + "+(" + str(u.rearAnklePP) + u.strx1AtFrame0 + ")"
        u.setAxisDriver(u.getEuler('rearAnkle.R'), fnR, 0)
        #
        # setGallop
        # Rear Toes
        if(hasattr(bpy.types.WindowManager, "rearToesRP")):
            u.rearToesRP = str(bpy.context.window_manager.rearToesRP + 7.0 * -.1)
        if(hasattr(bpy.types.WindowManager, "rearToesRR")):
            u.rearToesRR = str(bpy.context.window_manager.rearToesRR)
        eqL = u.rearAnkleRP + "+ 1.3 -(asin(" + u.strCycleRate + "))* .3 * " + u.rearToesRR + ")"
        fn = eqL + u.strx0AtFrame0 + "+(" + str(u.rearToesPP) + u.strx1AtFrame0 + ")"
        u.setAxisDriver(u.getEuler('rearToe.L'), fn + u.strx1AtFrame0, 0)
        eqR = u.rearToesRP + "+ 1.3 +(asin(" + u.strCycleRate + "))* .3 * " + u.rearToesRR + ")"
        fn = eqR + u.strx0AtFrame0 + "+(" + str(u.rearToesPP) + u.strx1AtFrame0 + ")"
        u.setAxisDriver(u.getEuler('rearToe.R'), fn + u.strx1AtFrame0, 0)
        #
        # setGallop
        # SwayFB
        bpy.data.window_managers['WinMan'].swayFB = 8.0 # Set in panel to show the change
        u.swayFB = "8.0"
        if(hasattr(bpy.types.WindowManager, "swayFB")):
            u.swayFB = str(bpy.context.window_manager.swayFB)
        fn = "-(asin(" + u.strCycleRate + ")* " + u.swayFB + "*.01)"
        u.setDriver(u.getEuler(u.strName + '_bone'), fn, 2)        
        # END REAR LEG FUNCTIONS
        # 
        # setGallop
        # UPPER BACK FUNCTIONS
        fn = "(asin(" + u.strCycleRate + ") * .6)/3.14"
        bBackJ4Driver = u.setDriver(u.getEuler('bBackJ4'), fn, 1)
        # Compensate for shoulder rotate by rotating neck and head in opposite direction, in three parts
        fn = "-(asin(" + u.strCycleRate + ") * .2)/3.14"
        neckJ2Driver = u.setDriver(u.getEuler('neckJ2'), fn, 1)
        neckJ3Driver = u.setDriver(u.getEuler('neckJ3'), fn, 1)
        neckJ4Driver = u.setDriver(u.getEuler('neckJ4'), fn, 1)
        #
        # setGallop
        # Arms rotation
        # armJ
        bpy.context.object.pose.bones["armJ1.L"].rotation_euler[0] = -1.5708
        fn = "(asin(" + u.strCycleRate + ") * .8)/3.14"
        armJLDriver = u.setAxisDriver(u.getEuler('armJ1.L'), fn, 1)
        bpy.context.object.pose.bones["armJ1.R"].rotation_euler[0] = -1.5708
        fn = "(asin(" + u.strCycleRate + ") * .8)/3.14"
        armJRDriver = u.setAxisDriver(u.getEuler('armJ1.R'), fn, 1)
        # Elbows
        fn = "((asin(" + u.strCycleRate + ") * .7)/3.14 - .3) * (frame*(1/(frame+.0001)))"
        radiusLDriver = u.setDriver(u.getEuler('armJ3.L'), fn, 2)
        fn = "((asin(" + u.strCycleRate + ") * .7)/3.14 + .3) * (frame*(1/(frame+.0001)))"
        radiusRDriver = u.setDriver(u.getEuler('armJ3.R'), fn, 2)
        u.rotate(u.strName, "armJ1.L", -1.57, 0)
        u.rotate(u.strName, "armJ1.R", -1.57, 0)
        bpy.ops.object.mode_set(mode='OBJECT')
        # END UPPER BACK FUNCTIONS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%        
        #
        # END Gallop %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#        
    def unsetCentaurWalk(self, context):
        u.getSelectedCharacterName()
        undo = bpy.data.objects[u.strName].pose.bones[u.strName + '_bone']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['femurJ1.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['femurJ1.L']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['tibiaJ1.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['tibiaJ1.L']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['ankle.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['ankle.L']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['toe.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['toe.L']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['hip.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['hip.L']
        undo.driver_remove('rotation_euler', -1)
        # Horse parts
        undo = bpy.data.objects[u.strName].pose.bones['join']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['rearHip.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['rearHip.L']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['rearHipJ1.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['rearHipJ1.L']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['rearFemurJ1.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['rearFemurJ1.L']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['rearTibiaJ1.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['rearTibiaJ1.L']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['rearAnkle.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['rearAnkle.L']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['rearToe.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['rearToe.L']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['bBackJ4']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['neckJ2']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['neckJ3']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['neckJ4']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['shoulder.L']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['shoulder.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['armJ1.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['armJ1.L']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['armJ3.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['armJ3.L']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['qfixHind1.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['qfixHind1.L']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['qfixHind2.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['qfixHind2.L']
        undo.driver_remove('rotation_euler', -1)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
        #
    def setWalk(self, context):
        u.getSelectedCharacterName()
        centaurFns.unsetCentaurWalk(self, context)
        centaurFns.setCycleRates(self, context)
        bpy.data.window_managers["WinMan"].bounce = 0.0
        bpy.data.window_managers['WinMan'].swayFB = 1.0
        bpy.data.window_managers['WinMan'].hipRotate = 4.0
        bpy.data.window_managers['WinMan'].femurJ1RP = 0.0
        bpy.data.window_managers['WinMan'].femurJ1RR = 1.0
        bpy.data.window_managers['WinMan'].tibiaJ1RP = 0.0
        bpy.data.window_managers['WinMan'].tibiaJ1RR = 1.0
        bpy.data.window_managers['WinMan'].ankleRP = 0.0
        bpy.data.window_managers['WinMan'].ankleRR = 1.0
        bpy.data.window_managers['WinMan'].toesRP = 0.0        
        bpy.data.window_managers['WinMan'].toesRR = 1.0
        bpy.data.window_managers['WinMan'].rearFemurJ1RP = 0.0
        bpy.data.window_managers['WinMan'].rearFemurJ1RR = 1.0
        bpy.data.window_managers['WinMan'].rearTibiaJ1RP = 0.0
        bpy.data.window_managers['WinMan'].rearTibiaJ1RR = 1.0
        bpy.data.window_managers['WinMan'].rearAnkleRP = 0.0
        bpy.data.window_managers['WinMan'].rearAnkleRR = 1.0
        bpy.data.window_managers['WinMan'].rearToesRP = 0.0        
        bpy.data.window_managers['WinMan'].rearToesRR = 1.0
        centaurFns.setCentaurWalk(self, context)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
        #
    def setTrot(self, context):
        u.getSelectedCharacterName()
        centaurFns.setWalk(self, context)
        bpy.data.window_managers['WinMan'].hipRotate = 4.0
        bpy.data.window_managers["WinMan"].cycle = 12.0
        centaurFns.setCycleRates(self, context)
        u.bounce = "3.0"
        eqBounce = "-(asin(" + u.strDoubleCycleRate + ")* " + u.bounce + "*.01)" # not 2
        dr_Bounce = u.setDriver(u.getEuler(u.strName + '_bone'), eqBounce, 1, 'location') # Bounce
        bpy.ops.object.mode_set(mode='OBJECT')
        #
        #
    def setPace(self, context):
        u.getSelectedCharacterName()
        centaurFns.unsetCentaurWalk(self, context)
        centaur.mode = "pace"  # Options: walk, run or hop
        # bpy.data.window_managers['WinMan'].cycle = 12
        centaurFns.setCycleRates(self, context)
        bpy.data.window_managers['WinMan'].hipRotate = 10.0
        bpy.data.window_managers['WinMan'].swayLR = 0.0
        bpy.data.window_managers['WinMan'].swayFB = 1.8
        u.bounce = "3.6"
        eqBounce = "-(asin(" + u.strCycleRate + ")* " + u.bounce + "*.01)" # not 2
        dr_Bounce = u.setDriver(u.getEuler(u.strName + '_bone'), eqBounce, 1, 'location') # Bounce
        bpy.data.window_managers['WinMan'].hipRotate = 14.0 
        bpy.data.window_managers['WinMan'].hipUD = 3.0 
        bpy.data.window_managers['WinMan'].shoulderRotate = 4.0 
        bpy.data.window_managers['WinMan'].shoulderUD = 3.0 
        bpy.data.window_managers['WinMan'].armRotation = 6.0 
        bpy.data.window_managers['WinMan'].femurJ1RP = -0.1 
        bpy.data.window_managers['WinMan'].femurJ1RR = 2.0 
        bpy.data.window_managers['WinMan'].tibiaJ1RR = 1.2 
        bpy.data.window_managers['WinMan'].rearFemurJ1RR = 2.0 
        bpy.data.window_managers['WinMan'].rearTibiaJ1RR = 1.2
        centaurFns.setCentaurWalk(self, context)
        # rearTibiaJ1RP = "13.6"  # Default rotate position
        if(hasattr(bpy.types.WindowManager, "rearTibiaJ1RP")):
            u.rearTibiaJ1RP = bpy.context.window_manager.rearTibiaJ1RP + 13.6 * -.1
        #rearTibiaJ1RR = "1.2"  # Default rotate range
        if(hasattr(bpy.types.WindowManager, "rearTibiaJ1RR")):
            u.rearTibiaJ1RR = bpy.context.window_manager.rearTibiaJ1RR * 1.2
        eq1 = "-" + str(u.rearTibiaJ1RP) + " + 1.2 + pow(atan(" + u.strHalfCycleRate + "),2)"
        eq2 = "pow(-atan(" + u.strHalfCycleRate + "),2)/8"
        eqL1 = "(.9 + " + eq1 + " * 2.2 - " + eq2 + ")"
        eqL2 = eqL1 + u.strx0AtFrame0 + "+(" + str(u.rearTibiaJ1PP) + u.strx1AtFrame0 + ")"
        fnL = "(" + eqL2 + ") * " + str(u.rearTibiaJ1RR)
        u.setAxisDriver(u.getEuler('rearTibiaJ1.L'), fnL, 0)
        # eq1, eq2 the same        
        eqR1 = "(1.0 + " + eq1 + " * 2.2 + " + eq2 + ")"
        eqR2 = eqR1 + u.strx0AtFrame0 + "+(" + str(u.rearTibiaJ1PP) + u.strx1AtFrame0 + ")"
        fnR = "(" + eqR2 + ")" + " * -1 * " + str(u.rearTibiaJ1RR)
        u.setAxisDriver(u.getEuler('rearTibiaJ1.R'), fnR, 0)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
        #
    # This is for restoring advanced control defaults for each bone in the leg: 
    # RP = Rotate Position
    # RR = Rotate Range
    def setFrontLegDefaults(self, context):
        bpy.data.window_managers['WinMan'].cycle = 8.0  
        centaurFns.setCycleRates(self, context)
        bpy.data.window_managers["WinMan"].femurJ1RP = 0.0
        bpy.data.window_managers["WinMan"].femurJ1RR = 1.0
        bpy.data.window_managers["WinMan"].tibiaJ1RP = 0.0
        bpy.data.window_managers["WinMan"].tibiaJ1RR = 1.0
        bpy.data.window_managers["WinMan"].ankleRP = 0.0
        bpy.data.window_managers["WinMan"].ankleRR = 1.0
        bpy.data.window_managers["WinMan"].toesRP = 0.0        
        bpy.data.window_managers["WinMan"].toesRR = 1.0
        centaurFns.setCentaurWalk(self, context)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
        #
    def setRearLegDefaults(self, context):
        bpy.data.window_managers['WinMan'].cycle = 8.0  
        centaurFns.setCycleRates(self, context)
        bpy.data.window_managers["WinMan"].rearFemurJ1RP = 0.0
        bpy.data.window_managers["WinMan"].rearFemurJ1RR = 1.0
        bpy.data.window_managers["WinMan"].rearTibiaJ1RP = 0.0
        bpy.data.window_managers["WinMan"].rearTibiaJ1RR = 1.0
        bpy.data.window_managers["WinMan"].rearAnkleRP = 0.0
        bpy.data.window_managers["WinMan"].rearAnkleRR = 1.0
        bpy.data.window_managers["WinMan"].rearToesRP = 0.0        
        bpy.data.window_managers["WinMan"].rearToesRR = 1.0
        centaurFns.setCentaurWalk(self, context)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
        #
    def setBounce(self, context):  # Bounce
        u.getSelectedCharacterName()
        u.bounce = "1.4"
        if(hasattr(bpy.types.WindowManager, "bounce")):
            u.bounce = str(bpy.context.window_manager.bounce)
        eqBounce = "-(asin(" + u.strDoubleCycleRate + ")* " + u.bounce + "*.01)" # not 2
        dr_Bounce = u.setDriver(u.getEuler(u.strName + '_bone'), eqBounce, 1, 'location') # Bounce
        bpy.ops.object.mode_set(mode='OBJECT')
        #
    def setSwayFB(self, context):  # forward - backward sway movement
        u.getSelectedCharacterName()
        u.swayFB = "2.0"
        if(hasattr(bpy.types.WindowManager, "swayFB")):
            u.swayFB = str(bpy.context.window_manager.swayFB)
        fn = "-(asin(" + u.strCycleRate + ")* " + u.swayFB + "*.01)"
        dr_SwayFB = u.setDriver(u.getEuler(u.strName + '_bone'), fn, 0)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
    def setswayLR(self, context):  # left - right sway movement
        u.getSelectedCharacterName()
        if(hasattr(bpy.types.WindowManager, "swayLR")):
            u.swayLR = str(bpy.context.window_manager.swayLR)
        fn = "-(asin(" + u.strCycleRate + ")* " + u.swayLR + "*.01)"
        u.setDriver(u.getEuler(u.strName + '_bone'), fn, 2)
        bpy.ops.object.mode_set(mode='OBJECT')
        #        
        #
    def setRearLegSpread(self, context):
        u.getSelectedCharacterName()
        if(hasattr(bpy.types.WindowManager, "legSpread")):
            u.legSpread = str(bpy.context.window_manager.legSpread)  # Leg Spread
        rot = math.radians(u.legSpread + " * -.1")
        u.rotate(u.strName, 'rearFemurJ1.L', rot, 1)
        u.rotate(u.strName, 'rearFemurJ1.R', rot, 1)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
        #
    # Head
    def setHead(self, context):
        u.getSelectedCharacterName()
        if(hasattr(bpy.types.WindowManager, "headUD")):
            u.headUD = bpy.context.window_manager.headUD * .2
        u.rotate(u.strName, 'neckJ4', u.headUD, 0)  # Uses rotate
        if(hasattr(bpy.types.WindowManager, "headLR")):
            u.headLR = bpy.context.window_manager.headLR * -.1
        u.rotate(u.strName, 'neckJ4', u.headLR, 2)  # Uses rotate
        if(hasattr(bpy.types.WindowManager, "headTurn")):
            u.headTurn = str(bpy.context.window_manager.headTurn * -.1)
        u.setAxisDriver(u.getEuler('neckJ4'), u.headTurn, 1)  # Uses driver, y-axis requires it.
        bpy.ops.object.mode_set(mode='OBJECT')
        #
        #
    def setNeck(self, context):
        u.getSelectedCharacterName()
        # Up - Down turn motion 
        if(hasattr(bpy.types.WindowManager, "neckFB")):
            u.neckFB = bpy.context.window_manager.neckFB
        u.neckFB = u.neckFB * .08
        u.rotate(u.strName, 'neckJ1', u.neckFB, 0)  # Uses rotate
        u.rotate(u.strName, 'neckJ2', u.neckFB, 0)
        u.rotate(u.strName, 'neckJ3', u.neckFB, 0)
        u.rotate(u.strName, 'neckJ4', u.neckFB, 0)
        # Sideways motion
        neckLR = "0.0"
        if(hasattr(bpy.types.WindowManager, "neckLR")):
            u.neckLR = bpy.context.window_manager.neckLR
        u.neckLR = -.08 * u.neckLR
        u.rotate(u.strName, 'neckJ1', u.neckLR, 2)  # Uses rotate
        u.rotate(u.strName, 'neckJ2', u.neckLR, 2)
        u.rotate(u.strName, 'neckJ3', u.neckLR, 2)
        u.rotate(u.strName, 'neckJ4', u.neckLR, 2)
        # Left - Right turn motion 
        if(hasattr(bpy.types.WindowManager, "neckTurn")):
            u.neckTurn = str(bpy.context.window_manager.neckTurn)
        fn = str(u.neckTurn) + "* .08"  # neck left - right
        bpy.context.object.pose.bones["neckJ1"].rotation_euler[1] = 0 # Leference points
        bpy.context.object.pose.bones["neckJ2"].rotation_euler[1] = 0
        bpy.context.object.pose.bones["neckJ3"].rotation_euler[1] = 0
        bpy.context.object.pose.bones["neckJ4"].rotation_euler[1] = 0
        u.setAxisDriver(u.getEuler('neckJ1'), fn, 1)
        u.setAxisDriver(u.getEuler('neckJ2'), fn, 1)
        u.setAxisDriver(u.getEuler('neckJ3'), fn, 1)
        u.setAxisDriver(u.getEuler('neckJ4'), fn, 1)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
        #
    def setJaw(self, context): # Jaw open - close
        u.getSelectedCharacterName()    
        if(hasattr(bpy.types.WindowManager, "jawOC")):
            u.jawOC = bpy.context.window_manager.jawOC
        u.jawOC = u.jawOC * -.1  # Jaw open - close
        u.rotate(u.strName, 'jaw', u.jawOC, 0)
        bpy.context.object.data.bones['jaw'].select  = True
        bpy.ops.object.mode_set(mode='POSE')
        #
        #
    # If centered at rear joint, parented,
    # can be used  for eye movements
    def setEye(self, context):
        u.getSelectedCharacterName()
        # Left - Right turn motion 
        if(hasattr(bpy.types.WindowManager, "eyeLR")):
            u.eyeLR = bpy.context.window_manager.eyeLR * .1
        u.rotate(u.strName, 'eye.L', u.eyeLR, 2)
        u.rotate(u.strName, 'eye.R', u.eyeLR, 2)
        #
        if(hasattr(bpy.types.WindowManager, "eyeUD")):
            u.eyeUD = bpy.context.window_manager.eyeUD * .1
        u.rotate(u.strName, 'eye.L', u.eyeUD, 0)
        u.rotate(u.strName, 'eye.R', u.eyeUD, 0)
        bpy.context.object.data.bones['eye.L'].select  = True
        bpy.context.object.data.bones['eye.R'].select  = True
        bpy.ops.object.mode_set(mode='POSE')
        #
        #
    def setTail(self, context):
        u.getSelectedCharacterName()
        if(hasattr(bpy.types.WindowManager, "tailUD")):
            u.tailUD = bpy.context.window_manager.tailUD * .1
        u.rotate(u.strName, 'hTailJ1', u.tailUD, 0)
        #
        if(hasattr(bpy.types.WindowManager, "tailLR")):
            u.tailLR = bpy.context.window_manager.tailLR * .1
        u.rotate(u.strName, 'hTailJ1', u.tailLR, 2)
        #
        #
        tailCurl = 0.0  # tail left - right
        if(hasattr(bpy.types.WindowManager, "tailCurl")):
            tailCurl = bpy.context.window_manager.tailCurl * .2
        u.rotate(u.strName, 'hTailJ2', tailCurl *.4, 0)
        u.rotate(u.strName, 'hTailJ3', tailCurl, 0)
        u.rotate(u.strName, 'hTailJ4', tailCurl, 0)
        u.rotate(u.strName, 'hTailJ5', tailCurl, 0)
        u.rotate(u.strName, 'hTailJ6', tailCurl, 0)
        u.rotate(u.strName, 'hTailJ7', tailCurl, 0)
        u.rotate(u.strName, 'hTailJ8', tailCurl, 0)
        u.rotate(u.strName, 'hTailJ9', tailCurl, 0)
        bpy.ops.object.mode_set(mode='POSE')
        bpy.context.object.data.bones["hTailJ1"].select  = True
        bpy.context.object.data.bones["hTailJ2"].select  = True
        bpy.context.object.data.bones["hTailJ3"].select  = True
        bpy.context.object.data.bones["hTailJ4"].select  = True
        bpy.context.object.data.bones["hTailJ5"].select  = True
        bpy.context.object.data.bones["hTailJ6"].select  = True
        bpy.context.object.data.bones["hTailJ7"].select  = True
        bpy.context.object.data.bones["hTailJ8"].select  = True
        bpy.context.object.data.bones["hTailJ9"].select  = True
        #
        #
    def setHip(self, context):
        u.getSelectedCharacterName()
        # Pelvis / Hip rotation    
        hipRotate = '0.0'
        if(hasattr(bpy.types.WindowManager, "hipRotate")):
            hipRotate = str(bpy.context.window_manager.hipRotate*.1)
        fn = "(asin(" + u.strCycleRate + ") * .2 * " + hipRotate + ")/3.14"
        pelvisDriver = u.setAxisDriver(u.getEuler('pelvis'), fn, 1)
        fn = "-(asin(" + u.strCycleRate + ") * .2 * " + hipRotate + ")/3.14" 
        u.setAxisDriver(u.getEuler('rearHip.L'), fn, 2)
        u.setAxisDriver(u.getEuler('rearHip.R'), fn, 2)
        #
        # fixs 3 and 5 are rear leg muscle manipulators
        legRotation = "-.8 * " + fn
        u.setAxisDriver(u.getEuler('qfixHind1.L'), legRotation, 0)
        u.setAxisDriver(u.getEuler('qfixHind1.R'), legRotation, 0)
        legRotation = ".8 * " + fn
        u.setAxisDriver(u.getEuler('qfixHind2.L'), legRotation, 0)
        u.setAxisDriver(u.getEuler('qfixHind2.R'), legRotation, 0)
        # hip up - down movement
        hipUD = '0.0'
        if(hasattr(bpy.types.WindowManager, "hipUD")):
            hipUD = str(bpy.context.window_manager.hipUD*.06)
        fn = "(asin(" + u.strCycleRate + ") * .4 *" + hipUD + ")/3.14"
        u.setAxisDriver(u.getEuler('hip.R'), fn, 0)
        u.setAxisDriver(u.getEuler('hip.L'), fn + " * -1", 0)  # Rear L Hip
        fn = "-(asin(" + u.strCycleRate + ") * " + hipUD + ")/3.14"
        u.setAxisDriver(u.getEuler('rearHip.L'), fn + " * -1", 0)  # Rear R Hip
        u.setAxisDriver(u.getEuler('rearHip.R'), fn, 0)
        u.setAxisDriver(u.getEuler('rearHipJ1.L'), fn, 0)  # Leg compensation for Rear L Hip
        u.setAxisDriver(u.getEuler('rearHipJ1.R'), fn, 0)  # Leg compensation for Rear R Hip
        bpy.ops.object.mode_set(mode='OBJECT')
        #
        #
    def setArmRotation(self, context):
        u.getSelectedCharacterName()
        fn = "(asin(" + u.strCycleRate + ") * .6)/3.14"
        bBackJ4Driver = u.setDriver(u.getEuler('bBackJ4'), fn, 1)
        armRotation = '3.0'
        if(hasattr(bpy.types.WindowManager, "armRotation")):
            armRotation = str(bpy.context.window_manager.armRotation * .2)
        # Arms rotation
        # armJ
        fn = "(asin(" + u.strCycleRate + ") * (" + armRotation + " + .1))/3.14"
        armJLDriver = u.setAxisDriver(u.getEuler('armJ1.L'), fn, 1)
        bpy.context.object.pose.bones["armJ1.L"].rotation_euler[0] = -1.5708
        fn = "(asin(" + u.strCycleRate + ") * (" + armRotation + " + .1))/3.14"
        armJRDriver = u.setAxisDriver(u.getEuler('armJ1.R'), fn, 1)
        bpy.context.object.pose.bones["armJ1.R"].rotation_euler[0] = -1.5708
        # Elbows
        fn = "((asin(" + u.strCycleRate + ") * " + armRotation + ")/3.14 - .3) * (frame*(1/(frame+.0001)))"
        radiusLDriver = u.setDriver(u.getEuler('armJ3.L'), fn, 2)
        fn = "((asin(" + u.strCycleRate + ") * " + armRotation + ")/3.14 + .3) * (frame*(1/(frame+.0001)))"
        radiusRDriver = u.setDriver(u.getEuler('armJ3.R'), fn, 2)
        fn = "-(asin(" + u.strCycleRate + ") * .2)/3.14"
        neckJ2Driver = u.setDriver(u.getEuler('neckJ2'), fn, 1)
        neckJ3Driver = u.setDriver(u.getEuler('neckJ3'), fn, 1)
        neckJ4Driver = u.setDriver(u.getEuler('neckJ4'), fn, 1)
        shoulderUD = '0.0'
        if(hasattr(bpy.types.WindowManager, "shoulderUD")):
            shoulderUD = str(bpy.context.window_manager.shoulderUD*.06)
        fn = "(asin(" + u.strCycleRate + ") * " + shoulderUD + ")/3.14"
        shoulderLDriver = u.setDriver(u.getEuler('shoulder.L'), fn, 0)
        fn = "(asin(" + u.strCycleRate + ") * " + shoulderUD + ")/3.14"
        shoulderRDriver = u.setDriver(u.getEuler('shoulder.R'), fn, 0)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
        #
    def unsetArmRotation(self, context):
        u.getSelectedCharacterName()
        undo = bpy.data.objects[u.strName].pose.bones['armJ1.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['armJ1.L']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['armJ3.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['armJ3.L']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['bBackJ4']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['neckJ2']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['neckJ3']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['neckJ4']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['shoulder.L']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['shoulder.R']
        undo.driver_remove('rotation_euler', -1)
        #
        #
    def setArms(self, context):
        u.getSelectedCharacterName()
        armsUD = 0.0
        if(hasattr(bpy.types.WindowManager, "armsUD")):
            armsUD = bpy.context.window_manager.armsUD
        armsUD = - math.radians(armsUD)
        u.rotate(u.strName, 'armJ1.L', armsUD, 0)
        u.rotate(u.strName, 'armJ1.R', armsUD, 0)
        u.rotate(u.strName, 'armJ3.L', 0, 0)
        u.rotate(u.strName, 'armJ3.R', 0, 0)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
    def setArmTwistR(self, context):
        u.getSelectedCharacterName()
        armTwistR =  0.0
        if(hasattr(bpy.types.WindowManager, "armTwistR")):
            armTwistR = bpy.context.window_manager.armTwistR
        armTwistR = armTwistR  * .1
        u.rotate(u.strName, 'armJ2.R', armTwistR, 1)
        u.rotate(u.strName, 'armJ3.R', armTwistR, 1)
        u.rotate(u.strName, 'armJ4.R', armTwistR, 1)
        u.rotate(u.strName, 'armJ5.R', armTwistR, 1)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
    def setArmTwistL(self, context):
        u.getSelectedCharacterName()
        armTwistL =  0.0
        if(hasattr(bpy.types.WindowManager, "armTwistL")):
            armTwistL = bpy.context.window_manager.armTwistL
        armTwistL = armTwistL  * -.1
        u.rotate(u.strName, 'armJ2.L', armTwistL, 1)
        u.rotate(u.strName, 'armJ3.L', armTwistL, 1)
        u.rotate(u.strName, 'armJ4.L', armTwistL, 1)
        u.rotate(u.strName, 'armJ5.L', armTwistL, 1)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
        #
    def setRHand(self, context): # Left hand open - close
        u.getSelectedCharacterName()
        RHandOC = 0.0
        if(hasattr(bpy.types.WindowManager, "RHandOC")):
            RHandOC = bpy.context.window_manager.RHandOC
        RHandOC = RHandOC * -.1  # hand open - close
        u.rotate(u.strName, 'indexJ1.R', RHandOC, 0)
        u.rotate(u.strName, 'indexJ2.R', RHandOC, 0)
        u.rotate(u.strName, 'indexJ3.R', RHandOC, 0)
        u.rotate(u.strName, 'midJ1.R', RHandOC, 0)
        u.rotate(u.strName, 'midJ2.R', RHandOC, 0)
        u.rotate(u.strName, 'midJ3.R', RHandOC, 0)
        u.rotate(u.strName, 'ringJ1.R', RHandOC, 0)
        u.rotate(u.strName, 'ringJ2.R', RHandOC, 0)
        u.rotate(u.strName, 'ringJ3.R', RHandOC, 0)
        u.rotate(u.strName, 'pinkyJ1.R', RHandOC, 0)
        u.rotate(u.strName, 'pinkyJ2.R', RHandOC, 0)
        u.rotate(u.strName, 'pinkyJ3.R', RHandOC, 0)
        RHandSpread = 0.0
        if(hasattr(bpy.types.WindowManager, "RHandSpread")):
            RHandSpread = bpy.context.window_manager.RHandSpread
        index = (RHandSpread  - 9) * .04 # Left hand spread, -10 so at zero, hand a non-spread position
        u.rotate(u.strName, 'indexJ1.R', index, 2)
        ring = (RHandSpread  - 9) * -.017  # Left hand spread
        u.rotate(u.strName, 'ringJ1.R', ring, 2)
        pinky = (RHandSpread  - 9) * -.052 # Left hand spread
        u.rotate(u.strName, 'pinkyJ1.R', pinky, 2)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
    def setLHand(self, context): # Right hand open - close
        u.getSelectedCharacterName()
        LHandOC = 9.0
        if(hasattr(bpy.types.WindowManager, "LHandOC")):
            LHandOC = bpy.context.window_manager.LHandOC
        LHandOC = LHandOC * -.1  # hand open - close
        u.rotate(u.strName, 'indexJ1.L', LHandOC, 0)
        u.rotate(u.strName, 'indexJ2.L', LHandOC, 0)
        u.rotate(u.strName, 'indexJ3.L', LHandOC, 0)
        u.rotate(u.strName, 'midJ1.L', LHandOC, 0)
        u.rotate(u.strName, 'midJ2.L', LHandOC, 0)
        u.rotate(u.strName, 'midJ3.L', LHandOC, 0)
        u.rotate(u.strName, 'ringJ1.L', LHandOC, 0)
        u.rotate(u.strName, 'ringJ2.L', LHandOC, 0)
        u.rotate(u.strName, 'ringJ3.L', LHandOC, 0)
        u.rotate(u.strName, 'pinkyJ1.L', LHandOC, 0)
        u.rotate(u.strName, 'pinkyJ2.L', LHandOC, 0)
        u.rotate(u.strName, 'pinkyJ3.L', LHandOC, 0)
        LHandSpread = 9.0
        if(hasattr(bpy.types.WindowManager, "LHandSpread")):
            LHandSpread = bpy.context.window_manager.LHandSpread
        index = (LHandSpread  - 9) * -.04 # Right hand spread, -10 so at zero, hand a non-spread position
        u.rotate(u.strName, 'indexJ1.L', index, 2)
        ring = (LHandSpread  - 9) * .017  # Right hand spread
        u.rotate(u.strName, 'ringJ1.L', ring, 2)
        pinky = (LHandSpread  - 9) * .052 # Right hand spread
        u.rotate(u.strName, 'pinkyJ1.L', pinky, 2)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
        #
    def setShoulder(self, context):
        u.getSelectedCharacterName()
        shoulderRotate = '0.0'
        if(hasattr(bpy.types.WindowManager, "shoulderRotate")):
            shoulderRotate = str(bpy.context.window_manager.shoulderRotate*.1)
        # Upper Back
        fn = "(asin(" + u.strCycleRate + ") * " + shoulderRotate + ")/3.14"
        bBackJ4Driver = u.setDriver(u.getEuler('bBackJ4'), fn, 1)
        # Compensate for shoulder rotate by rotating neck and head in opposite direction, in three parts
        fn = "-(asin(" + u.strCycleRate + ") * " + shoulderRotate + "/3)/3.14"
        neckJ2Driver = u.setDriver(u.getEuler('neckJ2'), fn, 1)
        neckJ3Driver = u.setDriver(u.getEuler('neckJ3'), fn, 1)
        neckJ4Driver = u.setDriver(u.getEuler('neckJ4'), fn, 1)
        # Shoulder up - down movement
        shoulderUD = '0.0'
        if(hasattr(bpy.types.WindowManager, "shoulderUD")):
            shoulderUD = str(bpy.context.window_manager.shoulderUD*.06)
        fn = "-(asin(" + u.strCycleRate + ") * " + shoulderUD + ")/3.14"
        shoulderLDriver = u.setDriver(u.getEuler('shoulder.L'), fn, 0)
        fn = "(asin(" + u.strCycleRate + ") * " + shoulderUD + ")/3.14"
        shoulderRDriver = u.setDriver(u.getEuler('shoulder.R'), fn, 0)
        bpy.ops.object.mode_set(mode='OBJECT')
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # End of CentaurFns CLASS
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# From 4598

# To 
class QuadrupedFns(object):
    def setCycleRates(self, context):
        u.getSelectedCharacterName()
        if(hasattr(bpy.types.WindowManager, "cycle")):
            u.cycle = bpy.context.window_manager.cycle + 8
        u.strCycleRate = "sin(radians(" + str(u.cycle) + "*frame))"  # String form of cycle equation
        u.strHalfCycleRate = "sin(radians(" + str(u.cycle / 2) + "*frame))"  # String form of halfcyclespeed equation
        u.strDoubleCycleRate = "sin(radians(" + str(u.cycle * 2) + "*frame))" # Double Speed
        u.strQuadrupleCycleRate = "sin(radians(" + str(u.cycle * 4) + "*frame))"
        u.strx0AtFrame0 = " * (frame * (1/(frame+.0001)))"  # produce a zero at frame zero, otherwise a one
        u.strx1AtFrame0 = " * abs((frame/(frame + .0001))-1)"  # produce a one at frame zero, otherwise a zero
        #        
        #
    def setQuadrupedWalk(self, context):
        u.getSelectedCharacterName()
        quadrupedFns.setCycleRates(self, context)
        #
        # KEY: RP = Rotate Position  RR = Rotate Range
        # FRONT LEG FUNCTIONS
        u.strx0AtFrame0 = " * (frame * (1/(frame+.0001)))"  # produce a zero at frame zero, otherwise a one
        u.strx1AtFrame0 = " * abs((frame/(frame + .0001))-1)"  # produce a one at frame zero, otherwise a zero
        if(hasattr(bpy.types.WindowManager, "femurJ1RP")):
            u.femurJ1RP = str(bpy.context.window_manager.femurJ1RP)
        if(hasattr(bpy.types.WindowManager, "femurJ1RR")):
            u.femurJ1RR = str(bpy.context.window_manager.femurJ1RR)
        eqR = "(" + u.femurJ1RP + "+(asin(" + u.strCycleRate + "))* .3 * " + u.femurJ1RR + ")"
        fnR = eqR + u.strx0AtFrame0 + "+(" + str(u.femurJ1PP) + u.strx1AtFrame0 + ")"
        u.setAxisDriver(u.getEuler('femurJ1.R'), fnR, 0)
        eqL = "(" + u.femurJ1RP + "-(asin(" + u.strCycleRate + "))* .3 * " + u.femurJ1RR + ")"
        fnL = eqL + u.strx0AtFrame0 + "+(" + str(u.femurJ1PP) + u.strx1AtFrame0 + ")"
        u.setAxisDriver(u.getEuler('femurJ1.L'), fnL, 0)
        #
        # setQuadrupedWalk
        # tibiaJ1
        if(hasattr(bpy.types.WindowManager, "tibiaJ1RP")):
            u.tibiaJ1RP = str(bpy.context.window_manager.tibiaJ1RP)
        if(hasattr(bpy.types.WindowManager, "tibiaJ1RR")):
            u.tibiaJ1RR = str(bpy.context.window_manager.tibiaJ1RR)
        eqL1 = u.tibiaJ1RP + " - 0.4 + pow(atan(" + u.strHalfCycleRate + "),2)"
        eqL2 = "pow(-atan(" + u.strHalfCycleRate + "),2)/8*" + u.tibiaJ1RR
        fnL = "(0.1 + " + eqL1 + " * 1.9 - " + eqL2 + ") * -1"
        u.setAxisDriver(u.getEuler('tibiaJ1.L'), fnL + u.strx0AtFrame0, 0)
        eqR1 = u.tibiaJ1RP + "- 0.4 - pow(atan(" + u.strHalfCycleRate + "),2)"
        eqR2 = "pow(-atan(" + u.strHalfCycleRate + "),2)/8*" + u.tibiaJ1RR
        fnR = "(1.3 + " + eqR1 + " * 1.9 - " + eqR2 + ") * -1"
        u.setAxisDriver(u.getEuler('tibiaJ1.R'), fnR + u.strx0AtFrame0, 0)
        #
        # setQuadrupedWalk
        # Front Ankles
        if(hasattr(bpy.types.WindowManager, "ankleRP")):
           u.ankleRP = bpy.context.window_manager.ankleRP * -.1
        ankleRR = "1.0"  # Default rotate range
        if(hasattr(bpy.types.WindowManager, "ankleRR")):
           u.ankleRR = bpy.context.window_manager.ankleRR
        eqR = "(-.9 + " + str(u.ankleRP) + "-(asin(" + u.strCycleRate + "))* .3 * " + str(u.ankleRR) + " + .5)"
        fnR = eqR + u.strx0AtFrame0 + "+(" + str(u.anklePP) + u.strx1AtFrame0 + ")"
        u.setAxisDriver(u.getEuler('ankle.R'), fnR, 0)
        eqL = "(-.9 + " + str(u.ankleRP) + "-(asin(" + u.strCycleRate + "))* .3 * " + str(u.ankleRR) + " + .5)"
        fnL = eqL + u.strx0AtFrame0 + "+(" + str(u.anklePP) + u.strx1AtFrame0 + ")"        
        u.setAxisDriver(u.getEuler('ankle.L'), fnL, 0)
        #
        # setQuadrupedWalk
        # Front Toes
        toesRP = "0.0"  # Default rotate position
        if(hasattr(bpy.types.WindowManager, "toesRP")):
            u.toesRP = bpy.context.window_manager.toesRP
        if(hasattr(bpy.types.WindowManager, "toesRR")):
            u.toesRR = bpy.context.window_manager.toesRR
        eqR = str(u.toesRP) + "+.4+atan(" + u.strCycleRate + ") * .6 * " + str(u.toesRR)
        fnR = eqR + u.strx0AtFrame0 + "+(-.26 + " + str(u.toesPP) + u.strx1AtFrame0 + ")"
        u.setAxisDriver(u.getEuler('toe.R'), fnR, 0)
        eqL = str(u.toesRP) + "+.4-atan(" + u.strCycleRate + ") * .6 * " + str(u.toesRR)
        fnL = eqL + u.strx0AtFrame0 + "+(-.26 + " + str(u.toesPP) + u.strx1AtFrame0 + ")"
        u.setAxisDriver(u.getEuler('toe.L'), fnL, 0)
        # END FRONT LEG FUNCTIONS
        #
        # setQuadrupedWalk
        #  REAR LEG FUNCTIONS
        rearFemurJ1RP = "0.0"  # Default rotate position
        if(hasattr(bpy.types.WindowManager, "rearFemurJ1RP")):
            rearFemurJ1RP = str((bpy.context.window_manager.rearFemurJ1RP + 1) * .4)
        rearFemurJ1RR = "1.0"  # Default rotate range
        if(hasattr(bpy.types.WindowManager, "rearFemurJ1RR")):
            rearFemurJ1RR = str(bpy.context.window_manager.rearFemurJ1RR)
        rearFemurJ1PP = "0.0" # Static pose position
        eqL = "(" + rearFemurJ1RP + "- 0.4 -(asin(" + u.strCycleRate + "))* .3 * " + rearFemurJ1RR + ")"
        fnL = eqL + u.strx0AtFrame0 + "+(" + rearFemurJ1PP + u.strx1AtFrame0 + ")"
        u.setAxisDriver(u.getEuler('rearFemurJ1.L'), fnL, 0)
        eqR = "(" + rearFemurJ1RP + "- 0.4 +(asin(" + u.strCycleRate + "))* .3 * " + rearFemurJ1RR + ")"
        fnR = eqR + u.strx0AtFrame0 + "+(" + rearFemurJ1PP + u.strx1AtFrame0 + ")"
        u.setAxisDriver(u.getEuler('rearFemurJ1.R'), fnR, 0)
        #
        # setQuadrupedWalk
        # Rear rearTibiaJ1s AKA Tibia
        rearTibiaJ1RP = "13.6"  # Default rotate position
        if(hasattr(bpy.types.WindowManager, "rearTibiaJ1RP")):
            u.rearTibiaJ1RP = bpy.context.window_manager.rearTibiaJ1RP + 13.6 * -.1
        rearTibiaJ1RR = "1.2"  # Default rotate range
        if(hasattr(bpy.types.WindowManager, "rearTibiaJ1RR")):
            u.rearTibiaJ1RR = bpy.context.window_manager.rearTibiaJ1RR * 1.2
        eq1 = str(u.rearTibiaJ1RP) + " - 0.4 + pow(atan(" + u.strHalfCycleRate + "),2)"
        eq2 = "pow(-atan(" + u.strHalfCycleRate + "),2)/8"
        eqL1 = "(1.0 + " + eq1 + " * 2.2 - " + eq2 + ")"
        eqL2 = eqL1 + u.strx0AtFrame0 + "+(" + str(u.rearTibiaJ1PP) + u.strx1AtFrame0 + ")"
        fnL = "(" + eqL2 + ")" + " * -1 * " + str(u.rearTibiaJ1RR)
        u.setAxisDriver(u.getEuler('rearTibiaJ1.L'), fnL, 0)
        eq1 = str(u.rearTibiaJ1RP) + " +1.2 + pow(atan(" + u.strHalfCycleRate + "),2)"
        eq2 = "pow(+atan(" + u.strHalfCycleRate + "),2)/8"
        eqR1 = "(-.3 + " + eq1 + " * 2.2 - " + eq2 + ")"
        eqR2 = eqR1 + u.strx0AtFrame0 + "+(" + str(u.rearTibiaJ1PP) + u.strx1AtFrame0 + ")"
        fnR = "(" + eqR2 + ") * " + str(u.rearTibiaJ1RR)
        u.setAxisDriver(u.getEuler('rearTibiaJ1.R'), fnR, 0)
        #
        #
        # setQuadrupedWalk
        # Rear Ankles
        rearAnkleRP = "0.0"  # Default rotate position
        if(hasattr(bpy.types.WindowManager, "rearAnkleRP")):
            u.rearAnkleRP = str(bpy.context.window_manager.rearAnkleRP * -.1)
        if(hasattr(bpy.types.WindowManager, "rearAnkleRR")):
            u.rearAnkleRR = str(bpy.context.window_manager.rearAnkleRR)
        fnL = "(-2.2 + " + u.rearAnkleRP + "+ 1.3 -(asin(" + u.strCycleRate + "))* -.3 * " + u.rearAnkleRR + ")"
        u.setAxisDriver(u.getEuler('rearAnkle.L'), fnL + u.strx0AtFrame0, 0)
        fnR = "(-2.2 + " + u.rearAnkleRP + "+ 1.3 +(asin(" + u.strCycleRate + "))* -.3 * " + u.rearAnkleRR + ")"
        u.setAxisDriver(u.getEuler('rearAnkle.R'), fnR + u.strx0AtFrame0, 0)
        #
        # setQuadrupedWalk
        # Rear Toes
        if(hasattr(bpy.types.WindowManager, "rearToesRP")):
            u.rearToesRP = str(bpy.context.window_manager.rearToesRP * -.1)
        if(hasattr(bpy.types.WindowManager, "rearToesRR")):
            u.rearToesRR = str(bpy.context.window_manager.rearToesRR)
        eqL = u.rearToesRP + "-.2+atan(" + u.strCycleRate + ") * .6 * " + u.rearToesRR
        fn = eqL + u.strx0AtFrame0 + "+(" + str(u.rearToesPP) + u.strx1AtFrame0 + ")"
        u.setAxisDriver(u.getEuler('rearToe.L'), fn + u.strx0AtFrame0, 0)
        eqR = u.rearToesRP + "-.2-atan(" + u.strCycleRate + ") * .6 * " + u.rearToesRR
        fn = eqR + u.strx0AtFrame0 + "+(" + str(u.rearToesPP) + u.strx1AtFrame0 + ")"
        u.setAxisDriver(u.getEuler('rearToe.R'), fn + u.strx0AtFrame0, 0)
        bpy.ops.object.mode_set(mode='OBJECT')
        # END REAR LEG FUNCTIONS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # setQuadrupedWalk
        # UPPER BACK FUNCTIONS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        fn = "(asin(" + u.strCycleRate + ") * .6)/3.14"
        u.setAxisDriver(u.getEuler('bNeckJ4'), fn, 0)
        # Compensate for shoulder rotate by rotating neck and head in opposite direction, in three parts
        fn = "-(asin(" + u.strCycleRate + ") * .2)/3.14"
        u.setAxisDriver(u.getEuler('bNeckJ4'), fn, 0)
        # END UPPER BACK FUNCTIONS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%        
        # END setQuadrupedWalk %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        #
        # This uses presets like the other gait changers, but also requires actual modification
        # of some of the equations to get the leg movement right.
    def setGallop(self, context):
        u.getSelectedCharacterName()
        quadrupedFns.unsetQuadrupedWalk(self, context)
        quadrupedFns.setCycleRates(self, context)
        #
        # setGallop
        # FRONT LEG GALLOP FUNCTIONS
        # Joint 1
        u.femurJ1RR = 1.2  # Set in panel to show the change
        leg_J1PP = "0.0" # Static pose position
        fnL = "(.6 * " + u.strCycleRate + " + 0.5 +(asin(" + u.strCycleRate + "))* .3 * " + str(u.femurJ1RR) + ")"
        u.setAxisDriver(u.getEuler('femurJ1.L'), fnL + u.strx0AtFrame0, 0)
        fnR = "(.1 * " + u.strCycleRate + " + 0.5 +(asin(" + u.strCycleRate + "))* .3 * " + str(u.femurJ1RR) + ")"
        u.setAxisDriver(u.getEuler('femurJ1.R'), fnR + u.strx0AtFrame0, 0)
        #
        # setGallop
        # Joint 2
        if(hasattr(bpy.types.WindowManager, "tibiaJ1RP")):
            u.tibiaJ1RP = str(bpy.context.window_manager.tibiaJ1RP)
        if(hasattr(bpy.types.WindowManager, "tibiaJ1RR")):
            u.tibiaJ1RR = str(bpy.context.window_manager.tibiaJ1RR)
        leg_J2PP = "0.0"  # Static pose position
        eq1 = u.tibiaJ1RP + "- 0.4 - pow(atan(" + u.strHalfCycleRate + "),2)"
        eq2 = "pow(-atan(" + u.strHalfCycleRate + "),2)/8"
        eqL1 = "-(.6 + " + eq1 + " * 2.2 - " + eq2 + ")"
        eqL2 = eqL1 + u.strx0AtFrame0 + "+(" + leg_J2PP + u.strx1AtFrame0 + ")"
        fnL = "(" + eqL2 + ") * " + u.tibiaJ1RR
        u.setAxisDriver(u.getEuler('tibiaJ1.L'), fnL + "*-1", 0)
        # eq1 and eq2 same as above
        eqR1 = "(.6 + " + eq1 + " * 2.2 - " + eq2 + ")"
        eqR2 = eqR1 + u.strx0AtFrame0 + "+(" + leg_J2PP + u.strx1AtFrame0 + ")"
        fnR = "(" + eqR2 + ")" + " * -1 * " + u.tibiaJ1RR
        u.setAxisDriver(u.getEuler('tibiaJ1.R'), fnR + "*-1", 0)
        #
        # setGallop
        # Front Ankles
        if(hasattr(bpy.types.WindowManager, "ankleRP")):
            u.ankleRP = bpy.context.window_manager.ankleRP
        if(hasattr(bpy.types.WindowManager, "ankleRR")):
            u.ankleRR = bpy.context.window_manager.ankleRR
        #anklePP = "-1.2"  # Static pose position
        eqL = "(-1.9 + " + str(u.ankleRP) + "+ 1.3 -(asin(" + u.strCycleRate + "))* .3 * " + str(u.ankleRR) + ")"
        fnL = eqL + u.strx0AtFrame0 + "+(" + str(u.anklePP) + u.strx1AtFrame0 + ")"
        u.setAxisDriver(u.getEuler('ankle.L'), fnL + u.strx0AtFrame0, 0)
        eqR = "(-2.0 + " + str(u.ankleRP) + "+ 1.3 -(asin(" + u.strCycleRate + "))* .3 * " + str(u.ankleRR) + ")"
        fnR = eqR + u.strx0AtFrame0 + "+(" + str(u.anklePP) + u.strx1AtFrame0 + ")"
        u.setAxisDriver(u.getEuler('ankle.R'), fnR + u.strx0AtFrame0, 0)
        # setGallop
        # Front Toes
        toesRP = "0.0"  # Default rotate position
        if(hasattr(bpy.types.WindowManager, "toesRP")):
            toesRP = bpy.context.window_manager.toesRP
        if(hasattr(bpy.types.WindowManager, "toesRR")):
            u.toesRR = bpy.context.window_manager.toesRR
        eqL = "(-1.8 + " + str(u.toesRP) + "+ 1.3 -(asin(" + u.strCycleRate + "))* .3 * " + str(u.toesRR) + ")"
        fnL = eqL + u.strx0AtFrame0 + "+(" + str(u.toesPP) + u.strx1AtFrame0 + ")"
        u.setAxisDriver(u.getEuler('toe.L'), fnL, 0)
        eqR = "(-2.0 + " + str(u.toesRP) + "+ 1.3 +(asin(" + u.strCycleRate + "))* .3 * " + str(u.toesRR) + ")"
        fnR = eqR + u.strx0AtFrame0 + "+(" + str(u.toesPP) + u.strx1AtFrame0 + ")"
        u.setAxisDriver(u.getEuler('toe.R'), fnR, 0)
        # END FRONT LEG FUNCTIONS
        #
        #
        # setGallop
        # REAR LEG FUNCTIONS
        bpy.data.window_managers['WinMan'].hipRotate = 2.0 # Set in panel to show the change
        hipRotate = "2.0"
        fn = "-(asin(" + u.strCycleRate + ") * .2 * " + hipRotate + ")/3.14" 
        u.setAxisDriver(u.getEuler('rearHip.L'), fn, 2)
        u.setAxisDriver(u.getEuler('rearHip.R'), fn, 2)
        #
        # fixs 4 and 5 are rear leg muscle manipulators
        legRotation = ".8 * " + fn
        u.setAxisDriver(u.getEuler('qfixHind1.L'), legRotation, 0)
        u.setAxisDriver(u.getEuler('qfixHind2.L'), legRotation, 0)
        u.setAxisDriver(u.getEuler('qfixHind1.R'), legRotation, 0)
        u.setAxisDriver(u.getEuler('qfixHind2.R'), legRotation, 0)
        #
        rearFemurJ1RP = "-0.1"  # Default rotate position
        if(hasattr(bpy.types.WindowManager, "rearFemurJ1RP")):
            rearFemurJ1RP = str((bpy.context.window_manager.rearFemurJ1RP + 1) * .4)
        rearFemurJ1RR = "1.0"
        rearFemurJ1PP = "0.0" # Static pose position
        eqL = "-(.5 * " + u.strCycleRate + "- 0.3 +(asin(" + u.strCycleRate + "))* .24 * " + rearFemurJ1RR + ")"
        fnL = "-.2 +" + eqL + u.strx0AtFrame0 + "+(" + rearFemurJ1PP + u.strx1AtFrame0 + ")"
        u.setAxisDriver(u.getEuler('rearFemurJ1.L'), fnL, 0)
        eqR = "-.4-(.1 * " + u.strCycleRate + "- 0.3 +(asin(" + u.strCycleRate + "))* .24 * " + rearFemurJ1RR + ")"
        fnR = eqR + u.strx0AtFrame0 + "+(" + rearFemurJ1PP + u.strx1AtFrame0 + ")"
        u.setAxisDriver(u.getEuler('rearFemurJ1.R'), fnR, 0)
        #
        # setGallop
        # Rear rearTibiaJ1s
        # rearTibiaJ1RP = "13.6"  # Default rotate position
        if(hasattr(bpy.types.WindowManager, "rearTibiaJ1RP")):
            u.rearTibiaJ1RP = str(bpy.context.window_manager.rearTibiaJ1RP + 13.6 * -.1)
        #rearTibiaJ1RR = "1.2"  # Default rotate range
        if(hasattr(bpy.types.WindowManager, "rearTibiaJ1RR")):
            u.rearTibiaJ1RR = str(bpy.context.window_manager.rearTibiaJ1RR * 1.2)
        eq1 = u.rearTibiaJ1RP + " - 1.2 + pow(atan(" + u.strHalfCycleRate + "),2)"
        eq2 = "pow(-atan(" + u.strHalfCycleRate + "),2)/8"
        #
        fnL = "(2.1 + " + eq1 + " * 2.2 - " + eq2 + ")" + " * " + u.rearTibiaJ1RR
        u.setAxisDriver(u.getEuler('rearTibiaJ1.L'), fnL + u.strx0AtFrame0, 0)
        fnR = "(1.8 + " + eq1 + " * 2.2 - " + eq2 + ")" + " * " + u.rearTibiaJ1RR
        u.setAxisDriver(u.getEuler('rearTibiaJ1.R'), fnR + u.strx0AtFrame0, 0)
        #
        # setGallop
        # Rear Ankles
        if(hasattr(bpy.types.WindowManager, "rearAnkleRP")):
            u.rearAnkleRP = str(bpy.context.window_manager.rearAnkleRP * -.1)
        if(hasattr(bpy.types.WindowManager, "rearAnkleRR")):
            u.rearAnkleRR = str(bpy.context.window_manager.rearAnkleRR)
        #rearAnklePP = "-0.6"  # Static pose position
        # use above equations
        eqL = "(-2.4 + " + u.rearAnkleRP + "+ 1.3 +(asin(" + u.strCycleRate + "))* .3 * " + u.rearAnkleRR + ")"
        fnL = eqL + u.strx0AtFrame0 + "+(" + str(u.rearAnklePP) + u.strx1AtFrame0 + ")"
        u.setAxisDriver(u.getEuler('rearAnkle.L'), fnL, 0)
        # eq2 is the same
        eqR = "(-2.4 + " + u.rearAnkleRP + "+ 1.3 +(asin(" + u.strCycleRate + "))* .3 * " + u.rearAnkleRR + ")"
        fnR = eqR + u.strx0AtFrame0 + "+(" + str(u.rearAnklePP) + u.strx1AtFrame0 + ")"
        u.setAxisDriver(u.getEuler('rearAnkle.R'), fnR, 0)
        #
        # setGallop
        # Rear Toes
        if(hasattr(bpy.types.WindowManager, "rearToesRP")):
            u.rearToesRP = str(bpy.context.window_manager.rearToesRP + 7.0 * -.1)
        if(hasattr(bpy.types.WindowManager, "rearToesRR")):
            u.rearToesRR = str(bpy.context.window_manager.rearToesRR)
        eqL = u.rearAnkleRP + "+ 1.3 -(asin(" + u.strCycleRate + "))* .3 * " + u.rearToesRR + ")"
        fn = eqL + u.strx0AtFrame0 + "+(" + str(u.rearToesPP) + u.strx1AtFrame0 + ")"
        u.setAxisDriver(u.getEuler('rearToe.L'), fn + u.strx1AtFrame0, 0)
        eqR = u.rearToesRP + "+ 1.3 +(asin(" + u.strCycleRate + "))* .3 * " + u.rearToesRR + ")"
        fn = eqR + u.strx0AtFrame0 + "+(" + str(u.rearToesPP) + u.strx1AtFrame0 + ")"
        u.setAxisDriver(u.getEuler('rearToe.R'), fn + u.strx1AtFrame0, 0)
        #
        # setGallop
        # SwayFB
        bpy.data.window_managers['WinMan'].swayFB = 8.0 # Set in panel to show the change
        u.swayFB = "8.0"
        if(hasattr(bpy.types.WindowManager, "swayFB")):
            u.swayFB = str(bpy.context.window_manager.swayFB)
        fn = "-(asin(" + u.strCycleRate + ")* " + u.swayFB + "*.01)"
        u.setDriver(u.getEuler(u.strName + '_bone'), fn, 2)        
        # END REAR LEG FUNCTIONS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # 
        # setGallop
        # UPPER BACK FUNCTIONS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        fn = "(asin(" + u.strCycleRate + ") * .6)/3.14"
        bBackJ4Driver = u.setDriver(u.getEuler('bNeckJ4'), fn, 1)
        # Compensate for shoulder rotate by rotating neck and head in opposite direction, in three parts
        fn = "-(asin(" + u.strCycleRate + ") * .2)/3.14"
        neckJ2Driver = u.setDriver(u.getEuler('bNeckJ2'), fn, 1)
        neckJ3Driver = u.setDriver(u.getEuler('bNeckJ3'), fn, 1)
        neckJ4Driver = u.setDriver(u.getEuler('bNeckJ4'), fn, 1)
        #
        u.rotate(u.strName, "rearFemurJ1.R", -.1047, 0)  # Rotate rear legs out so they do not hit front legs
        u.rotate(u.strName, "rearFemurJ1.L", .1047, 0)   # Rotate rear legs out so they do not hit front legs
        bpy.ops.object.mode_set(mode='OBJECT')
        # END UPPEL BACK FUNCTIONS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%        
        #
        # END Gallop %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#        
#        
    def unsetQuadrupedWalk(self, context):
        u.getSelectedCharacterName()
        undo = bpy.data.objects[u.strName].pose.bones[u.strName + '_bone']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['femurJ1.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['femurJ1.L']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['tibiaJ1.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['tibiaJ1.L']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['ankle.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['ankle.L']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['toe.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['toe.L']
        undo.driver_remove('rotation_euler', -1)
        # Horse parts
        undo = bpy.data.objects[u.strName].pose.bones['rearFemurJ1.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['rearFemurJ1.L']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['rearTibiaJ1.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['rearTibiaJ1.L']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['rearAnkle.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['rearAnkle.L']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['rearToe.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['rearToe.L']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['bNeckJ4']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['rearHip.L']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['rearHip.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['rearHipJ1.L']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['rearHipJ1.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['hip.L']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['hip.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['qfixHind1.L']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['qfixHind1.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['qfixHind2.L']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['qfixHind2.R']
        undo.driver_remove('rotation_euler', -1)
        undo = bpy.data.objects[u.strName].pose.bones['pelvis']
        undo.driver_remove('rotation_euler', -1)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
        #
    def setWalk(self, context):
        u.getSelectedCharacterName()
        quadrupedFns.unsetQuadrupedWalk(self, context)
        quadrupedFns.setCycleRates(self, context)
        bpy.data.window_managers["WinMan"].bounce = 0.0
        bpy.data.window_managers['WinMan'].swayFB = 1.0
        bpy.data.window_managers['WinMan'].hipRotate = 4.0
        bpy.data.window_managers['WinMan'].femurJ1RP = 0.0
        bpy.data.window_managers['WinMan'].femurJ1RR = 1.0
        bpy.data.window_managers['WinMan'].tibiaJ1RP = 0.0
        bpy.data.window_managers['WinMan'].tibiaJ1RR = 1.0
        bpy.data.window_managers['WinMan'].ankleRP = 0.0
        bpy.data.window_managers['WinMan'].ankleRR = 1.0
        bpy.data.window_managers['WinMan'].toesRP = 0.0        
        bpy.data.window_managers['WinMan'].toesRR = 1.0
        bpy.data.window_managers['WinMan'].rearFemurJ1RP = 0.0
        bpy.data.window_managers['WinMan'].rearFemurJ1RR = 1.0
        bpy.data.window_managers['WinMan'].rearTibiaJ1RP = 0.0
        bpy.data.window_managers['WinMan'].rearTibiaJ1RR = 1.0
        bpy.data.window_managers['WinMan'].rearAnkleRP = 0.0
        bpy.data.window_managers['WinMan'].rearAnkleRR = 1.0
        bpy.data.window_managers['WinMan'].rearToesRP = 0.0        
        bpy.data.window_managers['WinMan'].rearToesRR = 1.0
        quadrupedFns.setQuadrupedWalk(self, context)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
        #
    def setTrot(self, context):
        u.getSelectedCharacterName()
        quadrupedFns.setWalk(self, context)
        bpy.data.window_managers['WinMan'].hipRotate = 4.0
        bpy.data.window_managers["WinMan"].cycle = 12.0
        quadrupedFns.setCycleRates(self, context)
        bpy.data.window_managers['WinMan'].bounce = 3.0
        u.bounce = "3.0"
        eqBounce = "-(asin(" + u.strDoubleCycleRate + ")* " + u.bounce + "*.01)" # not 2
        dr_Bounce = u.setDriver(u.getEuler(u.strName + '_bone'), eqBounce, 1, 'location') # Bounce
        bpy.ops.object.mode_set(mode='OBJECT')
        #
        #
    def setPace(self, context):
        u.getSelectedCharacterName()
        quadrupedFns.unsetQuadrupedWalk(self, context)
        # bpy.data.window_managers['WinMan'].cycle = 12
        quadrupedFns.setCycleRates(self, context)
        bpy.data.window_managers['WinMan'].hipRotate = 10.0
        bpy.data.window_managers['WinMan'].swayLR = 0.0
        bpy.data.window_managers['WinMan'].swayFB = 1.8
        u.bounce = "3.6"
        eqBounce = "-(asin(" + u.strCycleRate + ")* " + u.bounce + "*.01)" # not 2
        dr_Bounce = u.setDriver(u.getEuler(u.strName + '_bone'), eqBounce, 1, 'location') # Bounce
        bpy.data.window_managers['WinMan'].hipRotate = 14.0 
        bpy.data.window_managers['WinMan'].hipUD = 3.0 
        bpy.data.window_managers['WinMan'].femurJ1RP = -0.1 
        bpy.data.window_managers['WinMan'].femurJ1RR = 2.0 
        bpy.data.window_managers['WinMan'].tibiaJ1RR = 1.2 
        bpy.data.window_managers['WinMan'].rearFemurJ1RR = 2.0 
        bpy.data.window_managers['WinMan'].rearTibiaJ1RR = 1.2
        quadrupedFns.setQuadrupedWalk(self, context)
        # rearTibiaJ1RP = "13.6"  # Default rotate position
        if(hasattr(bpy.types.WindowManager, "rearTibiaJ1RP")):
            u.rearTibiaJ1RP = bpy.context.window_manager.rearTibiaJ1RP + 13.6 * -.1
        #rearTibiaJ1RR = "1.2"  # Default rotate range
        if(hasattr(bpy.types.WindowManager, "rearTibiaJ1RR")):
            u.rearTibiaJ1RR = bpy.context.window_manager.rearTibiaJ1RR * 1.2
        eq1 = "-" + str(u.rearTibiaJ1RP) + " + 1.2 + pow(atan(" + u.strHalfCycleRate + "),2)"
        eq2 = "pow(-atan(" + u.strHalfCycleRate + "),2)/8"
        eqL1 = "(.9 + " + eq1 + " * 2.2 - " + eq2 + ")"
        eqL2 = eqL1 + u.strx0AtFrame0 + "+(" + str(u.rearTibiaJ1PP) + u.strx1AtFrame0 + ")"
        fnL = "(" + eqL2 + ") * " + str(u.rearTibiaJ1RR)
        u.setAxisDriver(u.getEuler('rearTibiaJ1.L'), fnL, 0)
        # eq1, eq2 the same        
        eqR1 = "(1.0 + " + eq1 + " * 2.2 + " + eq2 + ")"
        eqR2 = eqR1 + u.strx0AtFrame0 + "+(" + str(u.rearTibiaJ1PP) + u.strx1AtFrame0 + ")"
        fnR = "(" + eqR2 + ")" + " * -1 * " + str(u.rearTibiaJ1RR)
        u.setAxisDriver(u.getEuler('rearTibiaJ1.R'), fnR, 0)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
        #
    # This is for restoring advanced control defaults for each bone in the leg: 
    # RP = Rotate Position
    # RR = Rotate Range
    def setFrontLegDefaults(self, context):
        bpy.data.window_managers['WinMan'].cycle = 8.0  
        quadrupedFns.setCycleRates(self, context)
        bpy.data.window_managers["WinMan"].femurJ1RP = 0.0
        bpy.data.window_managers["WinMan"].femurJ1RR = 1.0
        bpy.data.window_managers["WinMan"].tibiaJ1RP = 0.0
        bpy.data.window_managers["WinMan"].tibiaJ1RR = 1.0
        bpy.data.window_managers["WinMan"].ankleRP = 0.0
        bpy.data.window_managers["WinMan"].ankleRR = 1.0
        bpy.data.window_managers["WinMan"].toesRP = 0.0        
        bpy.data.window_managers["WinMan"].toesRR = 1.0
        quadrupedFns.setQuadrupedWalk(self, context)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
        #
    def setRearLegDefaults(self, context):
        bpy.data.window_managers['WinMan'].cycle = 8.0  
        quadrupedFns.setCycleRates(self, context)
        bpy.data.window_managers["WinMan"].rearFemurJ1RP = 0.0
        bpy.data.window_managers["WinMan"].rearFemurJ1RR = 1.0
        bpy.data.window_managers["WinMan"].rearTibiaJ1RP = 0.0
        bpy.data.window_managers["WinMan"].rearTibiaJ1RR = 1.0
        bpy.data.window_managers["WinMan"].rearAnkleRP = 0.0
        bpy.data.window_managers["WinMan"].rearAnkleRR = 1.0
        bpy.data.window_managers["WinMan"].rearToesRP = 0.0        
        bpy.data.window_managers["WinMan"].rearToesRR = 1.0
        quadrupedFns.setQuadrupedWalk(self, context)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
        #
    def setBounce(self, context):  # Bounce
        u.getSelectedCharacterName()
        if(hasattr(bpy.types.WindowManager, "bounce")):
            u.bounce = str(bpy.context.window_manager.bounce)
        eqBounce = "-(asin(" + u.strDoubleCycleRate + ")* " + u.bounce + "*.01)" # not 2
        dr_Bounce = u.setDriver(u.getEuler(u.strName + '_bone'), eqBounce, 1, 'location') # Bounce
        bpy.ops.object.mode_set(mode='OBJECT')
        #
    def setSwayFB(self, context):  # forward - backward sway movement
        u.getSelectedCharacterName()
        if(hasattr(bpy.types.WindowManager, "swayFB")):
            u.swayFB = str(bpy.context.window_manager.swayFB)
        fn = "-(asin(" + u.strCycleRate + ")* " + u.swayFB + "*.01)"
        dr_SwayFB = u.setDriver(u.getEuler(u.strName + '_bone'), fn, 0)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
    def setSwayRL(self, context):  # left - right sway movement
        u.getSelectedCharacterName()
        if(hasattr(bpy.types.WindowManager, "swayLR")):
            u.swayLR = str(bpy.context.window_manager.swayLR)
        fn = "-(asin(" + u.strCycleRate + ")* " + u.swayLR + "*.01)"
        u.setDriver(u.getEuler(u.strName + '_bone'), fn, 2)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
        #
    def setRearLegSpread(self, context):
        u.getSelectedCharacterName()
        if(hasattr(bpy.types.WindowManager, "legSpread")):
            u.legSpread = str(bpy.context.window_manager.legSpread)  # Leg Spread
        rot = math.radians(u.legSpread + " * -.1")
        u.rotate(u.strName, 'rearFemurJ1.L', rot, 1)
        u.rotate(u.strName, 'rearFemurJ1.R', rot, 1)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
        #
    # Head
    def setHead(self, context):
        u.getSelectedCharacterName()
        if(hasattr(bpy.types.WindowManager, "headUD")):
            u.headUD = bpy.context.window_manager.headUD * .2
        u.rotate(u.strName, 'headBase', u.headUD, 0)  # Uses rotate
        if(hasattr(bpy.types.WindowManager, "headLR")):
            u.headLR = bpy.context.window_manager.headLR * -.1
        u.rotate(u.strName, 'headBase', u.headLR, 2)  # Uses rotate
        if(hasattr(bpy.types.WindowManager, "headTurn")):
            u.headTurn = str(bpy.context.window_manager.headTurn * -.1)
        u.setAxisDriver(u.getEuler('headBase'), u.headTurn, 1)  # Uses driver, y-axis requires it.
        bpy.ops.object.mode_set(mode='OBJECT')
        #
        #
    def setNeck(self, context):
        u.getSelectedCharacterName()
        # Up - Down turn motion 
        if(hasattr(bpy.types.WindowManager, "neckFB")):
            u.neckFB = bpy.context.window_manager.neckFB
        u.neckFB = u.neckFB * -.08
        u.rotate(u.strName, 'bNeckJ1', u.neckFB, 0)  # Uses rotate
        u.rotate(u.strName, 'bNeckJ2', u.neckFB, 0)
        u.rotate(u.strName, 'bNeckJ3', u.neckFB, 0)
        u.rotate(u.strName, 'bNeckJ4', u.neckFB, 0)
        # Sideways motion
        if(hasattr(bpy.types.WindowManager, "neckLR")):
            u.neckLR = bpy.context.window_manager.neckLR
        u.neckLR = -.08 * u.neckLR
        u.rotate(u.strName, 'bNeckJ1', u.neckLR, 2)  # Uses rotate
        u.rotate(u.strName, 'bNeckJ2', u.neckLR, 2)
        u.rotate(u.strName, 'bNeckJ3', u.neckLR, 2)
        u.rotate(u.strName, 'bNeckJ4', u.neckLR, 2)
        bpy.ops.object.mode_set(mode='OBJECT')
        # Left - Right turn motion 
        if(hasattr(bpy.types.WindowManager, "neckTurn")):
            u.neckTurn = str(bpy.context.window_manager.neckTurn)
        fn = str(u.neckTurn) + "* .08"  # neck left - right
        bpy.context.object.pose.bones["bNeckJ1"].rotation_euler[1] = 0 # Reference points
        bpy.context.object.pose.bones["bNeckJ2"].rotation_euler[1] = 0
        bpy.context.object.pose.bones["bNeckJ3"].rotation_euler[1] = 0
        bpy.context.object.pose.bones["bNeckJ4"].rotation_euler[1] = 0
        u.setAxisDriver(u.getEuler('bNeckJ1'), fn, 1)
        u.setAxisDriver(u.getEuler('bNeckJ2'), fn, 1)
        u.setAxisDriver(u.getEuler('bNeckJ3'), fn, 1)
        u.setAxisDriver(u.getEuler('bNeckJ4'), fn, 1)
        bpy.ops.object.mode_set(mode='OBJECT')
        #
        #
    def setJaw(self, context): # Jaw open - close
        u.getSelectedCharacterName()    
        if(hasattr(bpy.types.WindowManager, "jawOC")):
            u.jawOC = bpy.context.window_manager.jawOC
        u.jawOC = u.jawOC * -.1  # Jaw open - close
        u.rotate(u.strName, 'jaw', u.jawOC, 0)
        bpy.context.object.data.bones['jaw'].select  = True
        bpy.ops.object.mode_set(mode='POSE')
    # If centered at rear joint, parented,
    # can be used  for eye movements
    def setEye(self, context):
        u.getSelectedCharacterName()
        # Left - Right turn motion 
        if(hasattr(bpy.types.WindowManager, "eyeLR")):
            u.eyeLR = bpy.context.window_manager.eyeLR * .1
        u.rotate(u.strName, 'eye.L', u.eyeLR, 2)
        u.rotate(u.strName, 'eye.R', u.eyeLR, 2)
        #
        if(hasattr(bpy.types.WindowManager, "eyeUD")):
            u.eyeUD = bpy.context.window_manager.eyeUD * .1
        u.rotate(u.strName, 'eye.L', u.eyeUD, 0)
        u.rotate(u.strName, 'eye.R', u.eyeUD, 0)
        bpy.context.object.data.bones['eye.L'].select  = True
        bpy.context.object.data.bones['eye.R'].select  = True
        bpy.ops.object.mode_set(mode='POSE')
        #
        #
    def setTail(self, context):
        u.getSelectedCharacterName()
        if(hasattr(bpy.types.WindowManager, "tailUD")):
            u.tailUD = bpy.context.window_manager.tailUD * .1
        u.rotate(u.strName, 'hTailJ1', u.tailUD, 0)
        #
        if(hasattr(bpy.types.WindowManager, "tailLR")):
            u.tailLR = bpy.context.window_manager.tailLR * .1
        u.rotate(u.strName, 'hTailJ1', u.tailLR, 2)
        #
        #
        tailCurl = 0.0  # tail left - right
        if(hasattr(bpy.types.WindowManager, "tailCurl")):
            tailCurl = bpy.context.window_manager.tailCurl * .2
        u.rotate(u.strName, 'hTailJ2', tailCurl *.4, 0)
        u.rotate(u.strName, 'hTailJ3', tailCurl, 0)
        u.rotate(u.strName, 'hTailJ4', tailCurl, 0)
        u.rotate(u.strName, 'hTailJ5', tailCurl, 0)
        u.rotate(u.strName, 'hTailJ6', tailCurl, 0)
        u.rotate(u.strName, 'hTailJ7', tailCurl, 0)
        u.rotate(u.strName, 'hTailJ8', tailCurl, 0)
        u.rotate(u.strName, 'hTailJ9', tailCurl, 0)
        bpy.ops.object.mode_set(mode='POSE')
        bpy.context.object.data.bones["hTailJ1"].select  = True
        bpy.context.object.data.bones["hTailJ2"].select  = True
        bpy.context.object.data.bones["hTailJ3"].select  = True
        bpy.context.object.data.bones["hTailJ4"].select  = True
        bpy.context.object.data.bones["hTailJ5"].select  = True
        bpy.context.object.data.bones["hTailJ6"].select  = True
        bpy.context.object.data.bones["hTailJ7"].select  = True
        bpy.context.object.data.bones["hTtailJ8"].select  = True
        bpy.context.object.data.bones["hTailJ9"].select  = True
        #
        #
    def setEars(self, context):
        u.getSelectedCharacterName()
        if(hasattr(bpy.types.WindowManager, "earUD")):
            u.earUD = math.radians(bpy.context.window_manager.earUD)
        u.rotate(u.strName, 'earBase.L', u.earUD, 0)
        u.rotate(u.strName, 'earBase.R', u.earUD, 0)
        #
        if(hasattr(bpy.types.WindowManager, "earLR")):
            u.earLR = math.radians(bpy.context.window_manager.earLR)
        u.rotate(u.strName, 'earBase.L', u.earLR, 2)
        u.rotate(u.strName, 'earBase.R', u.earLR, 2)
        #
        if(hasattr(bpy.types.WindowManager, "earAxial")):
            u.earAxial = math.radians(bpy.context.window_manager.earAxial)
        u.rotate(u.strName, 'earBase.L', u.earAxial, 1)
        u.rotate(u.strName, 'earBase.R', u.earAxial, 1)
        #
        if(hasattr(bpy.types.WindowManager, "earCurl")):
            earCurl = bpy.context.window_manager.earCurl * .06
        u.rotate(u.strName, 'earJ1.L', earCurl *.2, 0)
        u.rotate(u.strName, 'earJ1.R', earCurl *.2, 0)
        u.rotate(u.strName, 'earJ2.L', earCurl, 0)
        u.rotate(u.strName, 'earJ2.R', earCurl, 0)
        u.rotate(u.strName, 'earJ3.L', earCurl, 0)
        u.rotate(u.strName, 'earJ3.R', earCurl, 0)
        u.rotate(u.strName, 'earJ4.L', earCurl, 0)
        u.rotate(u.strName, 'earJ4.R', earCurl, 0)
        u.rotate(u.strName, 'earJ5.L', earCurl, 0)
        u.rotate(u.strName, 'earJ5.R', earCurl, 0)
        bpy.context.object.data.bones['earBase.L'].select  = True
        bpy.context.object.data.bones['earBase.R'].select  = True
        bpy.context.object.data.bones['earJ1.L'].select  = True
        bpy.context.object.data.bones['earJ1.R'].select  = True
        bpy.context.object.data.bones['earJ2.L'].select  = True
        bpy.context.object.data.bones['earJ2.R'].select  = True
        bpy.context.object.data.bones['earJ3.L'].select  = True
        bpy.context.object.data.bones['earJ3.R'].select  = True
        bpy.context.object.data.bones['earJ4.L'].select  = True
        bpy.context.object.data.bones['earJ4.R'].select  = True
        bpy.context.object.data.bones['earJ5.L'].select  = True
        bpy.context.object.data.bones['earJ5.R'].select  = True
        bpy.ops.object.mode_set(mode='POSE')
        #
        #
        # Ears move in opposite directions
    def setEarsOpposite(self, context):
        if(hasattr(bpy.types.WindowManager, "earOUD")):
            u.earOUD = math.radians(bpy.context.window_manager.earOUD)
        u.rotate(u.strName, 'earBase.L', u.earOUD, 0)
        u.rotate(u.strName, 'earBase.R', -u.earOUD, 0)
        #
        if(hasattr(bpy.types.WindowManager, "earOLR")):
            u.earOLR = math.radians(bpy.context.window_manager.earOLR)
        u.rotate(u.strName, 'earBase.L', u.earOLR, 2)
        u.rotate(u.strName, 'earBase.R', -u.earOLR, 2)
        #
        if(hasattr(bpy.types.WindowManager, "earOAxial")):
            u.earOAxial = math.radians(bpy.context.window_manager.earOAxial)
        u.rotate(u.strName, 'earBase.L', u.earOAxial, 1)
        u.rotate(u.strName, 'earBase.R', -u.earOAxial, 1)
        #
        if(hasattr(bpy.types.WindowManager, "earOCurl")):
            earOCurl = bpy.context.window_manager.earOCurl * .06
        u.rotate(u.strName, 'earJ1.L', earOCurl *.2, 0)
        u.rotate(u.strName, 'earJ1.R', -earOCurl *.2, 0)
        u.rotate(u.strName, 'earJ2.L', earOCurl, 0)
        u.rotate(u.strName, 'earJ2.R', -earOCurl, 0)
        u.rotate(u.strName, 'earJ3.L', earOCurl, 0)
        u.rotate(u.strName, 'earJ3.R', -earOCurl, 0)
        u.rotate(u.strName, 'earJ4.L', earOCurl, 0)
        u.rotate(u.strName, 'earJ4.R', -earOCurl, 0)
        u.rotate(u.strName, 'earJ5.L', earOCurl, 0)
        u.rotate(u.strName, 'earJ5.R', -earOCurl, 0)
        bpy.context.object.data.bones['earBase.L'].select  = True
        bpy.context.object.data.bones['earBase.R'].select  = True
        bpy.context.object.data.bones['earJ1.L'].select  = True
        bpy.context.object.data.bones['earJ1.R'].select  = True
        bpy.context.object.data.bones['earJ2.L'].select  = True
        bpy.context.object.data.bones['earJ2.R'].select  = True
        bpy.context.object.data.bones['earJ3.L'].select  = True
        bpy.context.object.data.bones['earJ3.R'].select  = True
        bpy.context.object.data.bones['earJ4.L'].select  = True
        bpy.context.object.data.bones['earJ4.R'].select  = True
        bpy.context.object.data.bones['earJ5.L'].select  = True
        bpy.context.object.data.bones['earJ5.R'].select  = True
        bpy.ops.object.mode_set(mode='POSE')
        #
        #
    def setHip(self, context):
        u.getSelectedCharacterName()
        # Pelvis / Hip rotation    
        u.hipRotate = '0.0'
        if(hasattr(bpy.types.WindowManager, "hipRotate")):
            u.hipRotate = str(bpy.context.window_manager.hipRotate*.1)
        fn = "(asin(" + u.strCycleRate + ") * .2 * " + u.hipRotate + ")/3.14"
        pelvisDriver = u.setAxisDriver(u.getEuler('pelvis'), fn, 1)
        fn = "-(asin(" + u.strCycleRate + ") * .2 * " + u.hipRotate + ")/3.14" 
        u.setAxisDriver(u.getEuler('rearHip.L'), fn, 2)
        u.setAxisDriver(u.getEuler('rearHip.R'), fn, 2)
        #
        # fixs 3 and 5 are rear leg muscle manipulators
        legRotation = "-.8 * " + fn
        u.setAxisDriver(u.getEuler('qfix4.L'), legRotation, 0)
        u.setAxisDriver(u.getEuler('qfix4.R'), legRotation, 0)
        legRotation = ".8 * " + fn
        u.setAxisDriver(u.getEuler('qfix5.L'), legRotation, 0)
        u.setAxisDriver(u.getEuler('qfix5.R'), legRotation, 0)
        # hip up - down movement
        hipUD = '0.0'
        if(hasattr(bpy.types.WindowManager, "hipUD")):
            hipUD = str(bpy.context.window_manager.hipUD*.06)
        fn = "(asin(" + u.strCycleRate + ") * .4 *" + hipUD + ")/3.14"
        u.setAxisDriver(u.getEuler('hip.R'), fn, 0)
        u.setAxisDriver(u.getEuler('hip.L'), fn + " * -1", 0)  # Rear L Hip
        fn = "-(asin(" + u.strCycleRate + ") * " + hipUD + ")/3.14"
        u.setAxisDriver(u.getEuler('rearHip.L'), fn + " * -1", 0)  # Rear R Hip
        u.setAxisDriver(u.getEuler('rearHip.R'), fn, 0)
        u.setAxisDriver(u.getEuler('rearHipJ1.L'), fn, 0)  # Leg compensation for Rear L Hip
        u.setAxisDriver(u.getEuler('rearHipJ1.R'), fn, 0)  # Leg compensation for Rear R Hip
        bpy.ops.object.mode_set(mode='OBJECT')    
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # End of QuadrupedFns CLASS
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

class SpiderFns(object):
    def setSpiderWalk(self, context):
        u.getSelectedCharacterName()
        # spider.setCycleRates(self, context)
        if(hasattr(bpy.types.WindowManager, "cycle")):
            u.cycle = bpy.context.window_manager.cycle + 8
        u.strCycleRate = "sin(radians(" + str(u.cycle) + " * frame))"  # String form of cycle equation
        #
        u.setHorizontalSpeed(self, context)
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # LEG 1 Movement %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        fn = "(((.6366*asin(" + u.strCycleRate + ")*.2 + (fabs((.6366*asin(" + u.strCycleRate + ")))))*.2)+.22)"
        leg8Driver = u.setDriver(u.getEuler('leg1J1F.L'), fn, 0)  # Up-Down motion -****** SEE NOTE ABOVE *******
        #
        # Side to side motion
        fn = "(asin(" + u.strCycleRate + ") * .8)/3.14 - 1.2"  # Femur Side to side motion
        sideToSide8Driver = u.setDriver(u.getEuler('sideToSide1F'), fn, 1)  # Femur Side to side motion
        #
        fn = "-(asin(" + u.strCycleRate + ") * .8)/3.14 - 1.02"  # Tibia Up - Down motion
        tibia8Driver = u.setDriver(u.getEuler('leg1J2F.L'), fn, 0)   # Tibia Up-down motion
        #
        fn = "(asin(" + u.strCycleRate + ") * 1)/3.14 + .6"
        toe8Driver = u.setDriver(u.getEuler('leg1J3F.L'), fn, 0)  # Foot rotational position
        # End LEG 1 Movement %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        #
        #
        # LEG 2 Movement %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # Up-Down motion -****** SEE NOTE ABOVE *******
        fn = "(((.6366*asin(" + u.strCycleRate + ")*.2 + (fabs((.6366*asin(" + u.strCycleRate + ")))))*.2)+.22)"
        leg1Driver = u.setDriver(u.getEuler('leg2J1F.R'), fn, 0)
        #
        fn = "-(asin(" + u.strCycleRate + ") * .6)/3.14 + 1.2"  # Femur Side to side motion  
        sideToSide1Driver = u.setDriver(u.getEuler('sideToSide2F'), fn, 1)  # Femur Side to side motion
        #
        # Tibia Up - Down motion
        fn = "-(asin(" + u.strCycleRate + ") * .8)/3.14 - 1.1"  # Tibia Up - Down motion
        tibia1Driver = u.setDriver(u.getEuler('leg2J2F.R'), fn, 0)   # Tibia Up-down motion
        #
        # Toe rotational position
        fn = "(asin(" + u.strCycleRate + ") * .7)/3.14 + .8"  # Toe rotational position
        toe1Driver = u.setDriver(u.getEuler('leg2J3F.R'), fn, 0)  # Toe position
        # End LEG 2 Movement %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        #
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # LEG 3 Movement %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        fn = "((.6366*asin(" + u.strCycleRate + ")) + (fabs(.6366*asin(" + u.strCycleRate + "))))*.16+.28"
        leg2Driver = u.setDriver(u.getEuler('leg3J1R.F'), fn, 0)  # Up-Down motion -****** SEE NOTE ABOVE *******
        #
        # Side to side motion
        fn = "(asin(" + u.strCycleRate + ") * 1.1)/3.14 + .5"  # Side to side Femur
        sideToSide2Driver = u.setDriver(u.getEuler('sideToSide3R.F'), fn, 1)  # Femur Side to side motion
        #
        fn = "(asin(" + u.strCycleRate + ") * .2)/3.14 - 1.1"  # Up - Down Tibia
        tibia2Driver = u.setDriver(u.getEuler('leg3J2R.F'), fn, 0)   # Tibia Up-down motion
        #
        fn = "-(asin(" + u.strCycleRate + ") * .4)/3.14 + .7"  # foot rotation
        toe2Driver = u.setDriver(u.getEuler('leg3J3R.F'), fn, 0)  # Foot rotational position
        # End LEG 3 Movement %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        #
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # LEG 4 Movement %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # Femur Up-Down motion -****** SEE NOTE ABOVE *******
        fn = "(((.6366*asin(" + u.strCycleRate + ")*.2 + (fabs((.6366*asin(" + u.strCycleRate + ")))))*.2)+.22)"
        leg3Driver = u.setDriver(u.getEuler('leg4J1R.B'), fn, 0)  # Up-Down motion -****** SEE NOTE ABOVE *******
        #
        # Femur Side to side motion
        fn = "-(asin(" + u.strCycleRate + ") * .8)/3.14 - .66" 
        sideToSide3Driver = u.setDriver(u.getEuler('sideToSide4R.B'), fn, 1)  # Femur Side to side motion
        #
        # Tibia Up - Down motion
        fn = "(asin(" + u.strCycleRate + ") * .8)/3.14 - 1.02"  # Tibia Up - Down motion
        tibia3Driver = u.setDriver(u.getEuler('leg4J2R.B'), fn, 0)   # Tibia Up-down motion
        #
        # Toe rotational position
        fn = "-(asin(" + u.strCycleRate + ") * 1)/3.14 + .6"  # Toe rotational position
        toe3Driver = u.setDriver(u.getEuler('leg4J3R.B'), fn, 0)  # Toe position
        # End LEG 4 Movement %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        #
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # LEG 5 Movement %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        fn = "(asin(" + u.strCycleRate + ") * .8)/3.14 + .28"
        leg4Driver = u.setDriver(u.getEuler('leg5J1.R'), fn, 0)
        #
        fn = "-(asin(" + u.strCycleRate + ") * 2.2)/3.14 - .8"  # Tibia Up - Down motion
        tibia4Driver = u.setDriver(u.getEuler('leg5J2.R'), fn, 0)
        #
        fn = "(asin(" + u.strCycleRate + ") * .88)/3.14 + .6"    # Toe rotational position
        toe4Driver = u.setDriver(u.getEuler('leg5J3.R'), fn, 0)
        #
        bpy.context.object.pose.bones["leg5J1.R"].rotation_euler[2] = .34
        # End LEG 5 Movement %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        #
        #
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # LEG 6 Movement %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        fn = "(asin(" + u.strCycleRate + ") * .8)/3.14 + .28"
        leg5Driver = u.setDriver(u.getEuler('leg6J1.L'), fn, 0)
        #
        fn = "-(asin(" + u.strCycleRate + ") * 2.2)/3.14 - .8"   # Tibia Up - Down motion
        tibia5Driver = u.setDriver(u.getEuler('leg6J2.L'), fn, 0)
        #
        fn = "(asin(" + u.strCycleRate + ") * .88)/3.14 + .6"     # Toe rotational position
        toe5Driver = u.setDriver(u.getEuler('leg6J3.L'), fn, 0)
        #
        # bpy.context.object.pose.bones["sideToSide6.L"].rotation_euler[2] = -.34
        # End LEG 6 Movement %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        #
        #
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # LEG 7 Movement %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        fn = "(((.6366*asin(" + u.strCycleRate + ")*.2 + (fabs((.6366*asin(" + u.strCycleRate + ")))))*.2)+.22)"
        leg6Driver = u.setDriver(u.getEuler('leg7J1L.B'), fn, 0)  # Up-Down motion -****** SEE NOTE ABOVE *******
        #
        # Side to side motion
        fn = "(asin(" + u.strCycleRate + ") * .8)/3.14 + .66"  # Side to side Femur
        sideToSide6Driver = u.setDriver(u.getEuler('sideToSide7L.B'), fn, 1)  # Femur Side to side motion
        #
        fn = "(asin(" + u.strCycleRate + ") * .8)/3.14 - 1.02"  # Tibia Up - Down motion
        tibia6Driver = u.setDriver(u.getEuler('leg7J2L.B'), fn, 0)   # Tibia Up-down motion
        #
        fn = "(asin(" + u.strCycleRate + ") * .3)/3.14 + .7"  # foot rotation
        toe6Driver = u.setDriver(u.getEuler('leg7J3L.B'), fn, 0)  # Foot rotational position
        # End LEG 7 Movement %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        #
        #
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # LEG 8 Movement %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        fn = "((.636*asin(" + u.strCycleRate + ")) + (fabs(.6366*asin(" + u.strCycleRate + "))))*.16+.28"
        leg7Driver = u.setDriver(u.getEuler('leg8J1L.F'), fn, 0)  # Up-Down motion -****** SEE NOTE ABOVE *******
        #
        # Side to side motion
        fn = "-(asin(" + u.strCycleRate + ") * .8)/3.14 - .66"  # Side to side Femur
        sideToSide7Driver = u.setDriver(u.getEuler('sideToSide8L.F'), fn, 1)  # Femur Side to side motion
        #
        fn = "(asin(" + u.strCycleRate + ") * .2)/3.14 - 1.1"  # Up - Down Tibia
        tibia7Driver = u.setDriver(u.getEuler('leg8J2L.F'), fn, 0)   # Tibia Up-down motion
        #
        fn = "-(asin(" + u.strCycleRate + ") * .4)/3.14 + .7"  # foot rotation
        toe7Driver = u.setDriver(u.getEuler('leg8J3L.F'), fn, 0)  # Foot rotational position
        # End LEG 8 Movement %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        u.deselectAll()
        ob = bpy.data.objects.get(u.strName)
        bpy.context.scene.objects.active = ob
        ob.select = True
        u.rotate(u.strName, 'sideToSide1F', -1.3, 1)
        u.rotate(u.strName, 'sideToSide2F', 1.3, 1)
        u.rotate(u.strName, 'sideToSide3R.F', .7854, 1)
        u.rotate(u.strName, 'sideToSide4R.B', -.7854, 1)
        u.rotate(u.strName, 'sideToSide5.R', -.9854, 1)  # Greater, rear leg
        u.rotate(u.strName, 'sideToSide6.L', .9854, 1)   # Greater, rear leg
        u.rotate(u.strName, 'sideToSide7L.B', .7854, 1)
        u.rotate(u.strName, 'sideToSide8L.F', -.7854, 1)
        bpy.ops.object.mode_set(mode='OBJECT')
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # End of SpiderFns CLASS
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# End Character Functions
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
u = Utils
biped = Biped
bird = Bird
centaur = Centaur
quadruped = Quadruped
spider = Spider
#
birdFns = BirdFns
bipedFns = BipedFns
centaurFns = CentaurFns
quadrupedFns = QuadrupedFns
spiderFns = SpiderFns