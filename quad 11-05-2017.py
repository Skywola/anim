# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Generalized header code section
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# THINGS THAT MAY VARY BASED ON THE CHARACTER:
# 1. Character name - biped, quadruped, bird, spider, dragon, kangaroo.
#    Line: 125
# 2. rig location 
#    Example: char.height = 1.4, char.x = .3 * n; char.y = 3.2 * n; char.z = 0.1;
#    This can set the initial height of the character, and 
#    n is used to offset characters when more than one are created
#    Lines: 136 - 139
# 3. bone.tail sets the general orientation of the handle created for 
#    moving the character - this could vary, based  on the type of character.
#    Line: 151
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
import bpy, math
from bpy.types import Panel, Menu
from rna_prop_ui import PropertyPanel
from abc import ABCMeta, abstractmethod

# General Use Functions. Rotate the easy way, changes to pose mode and back
# name a string i.e., rotate('backCenter', .2, 1)
def rotate(name, rad, axis=0):
    bpy.ops.object.mode_set(mode='POSE')
    bpy.context.object.data.bones[name].select = True
    Vector = (1, 0, 0)
    cAxis = (True, False, False)
    if (axis == 1):
        Vector = (0, 1, 0)
        cAxis = (False, True, False)
    if (axis == 2):
        Vector = (0, 0, 1)
        cAxis = (False, False, True)
    bpy.ops.transform.rotate(value=rad, axis=Vector, constraint_axis=cAxis, constraint_orientation='GLOBAL',
                             mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH',
                             proportional_size=1, release_confirm=True)
    bpy.context.object.data.bones[name].select = False


# Link objects to scene
def linkObjectsToScene(rig):
    scn = bpy.context.scene
    scn.objects.link(rig)
    scn.objects.active = rig
    scn.update()

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

# Options for character types -  biped, quadruped, bird, spider, dragon, kangaroo
def setCharacterName(type, n):
    name = "rg" + type + "0" + str(n + 1)  # Assume n < 10 
    if (n > 9):  # Change char.name if previous assumption is wrong
        name = "rg" + type + str(n + 1)
    return name

# getEuler output represents:
# bpy.data.objects['rg00centaur'].pose.bones["backCenter"]
def getEuler(str_bone_name):
    bpy.ops.object.mode_set(mode='POSE')
    ob = bpy.context.object
    euler = ob.pose.bones[str_bone_name]
    euler.rotation_mode = 'XYZ'
    return euler


# Equation for bone joints, with euler transform, axis 0=x 1=y 2=z
# Note also that fn must be inserted as a STRING in the expression!
# Example: setDriver(getEuler(centaur.strName + '_bone'), equationFB, 2)
def setDriver(euler, fn="0", axis=0, movementType='rotation_euler'):
    eulerDriver = euler.driver_add(movementType)
    eulerDriver[axis].driver.type = 'SCRIPTED'
    eulerDriver[axis].driver.expression = fn
    return eulerDriver


# Set Driver For Single Axis Only:
def setAxisDriver(euler, fn="0", axis=0, movementType='rotation_euler'):
    edriver = euler.driver_add(movementType, axis)
    edriver.driver.type = 'SCRIPTED'
    edriver.driver.expression = fn
    return edriver

    
context = bpy.context
bpy.context.scene.frame_start = 0
class Character(object):
    __metaclass__ = ABCMeta
    n = 0  # Character number
    strName = ""
    armmature = 'None'
    rig = 'None'
    rootBone = 'None'
    rootBoneHead = 'None'
    rootBoneTail = 'None'
    reinforce = True  # Option - Add extra bones for stabilization
    showNames = False  # Option - show bone names - for build only
    show_xray = True  # Option
    show_axes = False  # Option - Show armature axis - for build only
    rig = None
    height = 0
    x = 0
    y = 0
    z = 0
    frame = bpy.context.scene.frame_current
    cycleSpeed = 8.0  # This is the speed of leg movement
    # For Pose at frame zero - Override function on frame zero, allowing for posing.
    strZeroMovement = " * (frame * (1/(frame+.0001)))"  # This includes outside math operator *
    strZeroOutPose = " * abs((frame/(frame + .0001))-1)"  # Override posePosition when frame NOT zero
    @abstractmethod
    def character_type(self):
        return 'centaur'


char = Character
# Do not remove spaces below, they correspond to command line entries
for ob in list(bpy.data.objects):
    if ob.name.startswith('rg') == True:
        char.n = char.n + 1  # increment rig number each time  one  is built.

char.strName = setCharacterName('centaur', char.n)  # biped, quadruped, bird, spider, dragon, kangaroo
# Start character armature and bones
# Do not remove spaces above, they correspond to command line entries
at = bpy.data.armatures.new(char.strName + '_at')  # at = Armature 
char.rig = bpy.data.objects.new(char.strName, at)  # rig = Armature object
# rg00 (or the one in a series we are building) is now bpy.context.active_object
at.show_names = char.showNames
at.show_axes = char.show_axes

# Each new object created will be placed in a new location
char.height = 1.14  # Sets the height of the character handle
char.x = .3 * char.n;
char.y = char.n;
char.z = char.height;
char.rig.location = (char.x, char.y, char.height)  # Set armature location
char.rig.show_x_ray = char.show_xray
linkObjectsToScene(char.rig)

bpy.ops.object.mode_set(mode='EDIT')
# The lines below create the handle for moving the character
bone = at.edit_bones.new(char.strName + '_bone')

bone.head = [0.0, 0.0, 0.0]  # LOCAL COORDINATE, [0,0,0] places bone directly on armature.
bone.tail = [-0.2, 0, 0]  # x - horizontal handle   z - vertical handle
char.rootBoneHead = bone.head
char.rootBoneTail = bone.tail
char.rootBone = bone

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# End generalized header code section
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


class Centaur(Character):
    anklePP = 0.0
    #
    def buildSkeleton(self):
        V_pelvis = (0, 0, -.13)
        pelvis = createBone("pelvis", bone.head, V_pelvis, 0)
        pelvis.parent = at.edit_bones[centaur.strName + '_bone']
        hipWidth = .12
        # 
        V_hipR = (0, hipWidth, -.13)
        V_hipL = (0, -hipWidth, -.13)
        hipR = createBone("hipR", V_pelvis, V_hipR, 0)
        hipR.parent = at.edit_bones['pelvis']
        hipL = createBone("hipL", V_pelvis, V_hipL, 0)
        hipL.parent = at.edit_bones['pelvis']
        # 
        V_femurR = (0, hipWidth, -.6)
        V_femurL = (0, -hipWidth, -.6)    
        femurR = createBone("femurR", V_hipR, V_femurR, 0)
        femurR.parent = at.edit_bones['hipR']
        femurL = createBone("femurL", V_hipL, V_femurL, 0)
        femurL.parent = at.edit_bones['hipL']
        # 
        V_tibiaR = (0, hipWidth, -.94)
        V_tibiaL = (0, -hipWidth, -.94)
        tibiaR = createBone("tibiaR", V_femurR, V_tibiaR, 0)
        tibiaR.parent = at.edit_bones['femurR']
        tibiaL = createBone("tibiaL", V_femurL, V_tibiaL, 0)
        tibiaL.parent = at.edit_bones['femurL']
        #
        V_ankleR = (0, hipWidth, -1.02)
        V_ankleL = (0, -hipWidth, -1.02)
        ankleR = createBone("ankleR", (V_tibiaR), (V_ankleR), 0)
        ankleR.parent = at.edit_bones['tibiaR']
        ankleL = createBone("ankleL", (V_tibiaL), (V_ankleL), 0)
        ankleL.parent = at.edit_bones['tibiaL']  
        #
        V_toeR = (0, hipWidth, -1.1)
        V_toeL = (0, -hipWidth, -1.1)
        toeR = createBone("toeR", (V_ankleR), (V_toeR), 0)
        toeR.parent = at.edit_bones['ankleR']
        toeL = createBone("toeL", (V_ankleL), (V_toeL), 0)
        toeL.parent = at.edit_bones['ankleL']
        # END OF LOWER BODY BUILD
        #
        # Create Upper Body  
        V_neckBase = (0, 0, 0.08)
        neckBase = createBone("neckBase", bone.head, V_neckBase)
        neckBase.parent = at.edit_bones[centaur.strName + '_bone']
        # 
        V_neckJ1 = (0, 0, 0.14)
        neckJ1 = createBone("neckJ1", V_neckBase, V_neckJ1)
        neckJ1.parent = at.edit_bones['neckBase']
        # 
        V_neckJ2 = (0, 0, 0.2)
        neckJ2 = createBone("neckJ2", V_neckJ1, V_neckJ2)
        neckJ2.parent = at.edit_bones['neckJ1']
        # 
        V_neckJ3 = (0, 0, 0.26)
        neckJ3 = createBone("neckJ3", V_neckJ2, V_neckJ3)   
        neckJ3.parent = at.edit_bones['neckJ2']    
        # 
        V_neckJ4 = (0, 0, 0.32)   
        neckJ4 = createBone("neckJ4", V_neckJ3, V_neckJ4)   
        neckJ4.parent = at.edit_bones['neckJ3']
        # 
        V_neckJ5 = (0, 0, 0.38)
        neckJ5 = createBone("neckJ5", V_neckJ4, V_neckJ5) 
        neckJ5.parent = at.edit_bones['neckJ4']
        # 
        V_neckJ6 = (0, 0, 0.44)
        neckJ6 = createBone("neckJ6", V_neckJ5, V_neckJ6) 
        neckJ6.parent = at.edit_bones['neckJ5']
        #
        V_neckJ7 = (0, 0, 0.5)
        neckJ7 = createBone("neckJ7", (V_neckJ6), V_neckJ7)   
        neckJ7.parent = at.edit_bones['neckJ6']    
        # 
        V_jawBase = (0.06, 0, 0.5)
        jawBase = createBone("jawBase", V_neckJ7, V_jawBase)
        jawBase.parent = at.edit_bones['neckJ7']
        # 
        V_jaw = (0.106, 0, .5)
        jaw = createBone("jaw", V_jawBase, V_jaw)   
        jaw.parent = at.edit_bones['jawBase']
        # 
        V_headBase = (0, 0, 0.53)
        headBase = createBone("headBase", V_neckJ7, V_headBase) 
        headBase.parent = at.edit_bones['neckJ7']
        # 
        V_mouthTop = (0.106, 0, .54)
        mouthTop = createBone("mouthTop", V_headBase, V_mouthTop) 
        mouthTop.parent = at.edit_bones['headBase']
        # 
        V_headTop = (0, 0, 0.58)
        headTop = createBone("headTop", V_headBase, V_headTop)
        headTop.parent = at.edit_bones['headBase']
        # 
        V_eyebaseR = (0.08, -0.03, 0.58)
        V_eyebaseL = (0.08, 0.03, 0.58)
        eyebaseR = createBone("eyebaseR", V_headTop, V_eyebaseR)
        eyebaseR.parent = at.edit_bones['headTop']   
        eyebaseL = createBone("eyebaseL", V_headTop, V_eyebaseL)  
        eyebaseL.parent = at.edit_bones['headTop']
        # 
        V_eyeR = (0.102, -0.03, 0.58)
        V_eyeL = (0.102, 0.03, 0.58)
        eyeR = createBone("eyeR", V_eyebaseR, V_eyeR) 
        eyeR.parent = at.edit_bones['eyebaseR']   
        eyeL = createBone("eyeL", V_eyebaseL, V_eyeL) 
        eyeL.parent = at.edit_bones['eyebaseL']
        # 
        V_NoseBase = (0.11, 0, 0.57)
        noseBase = createBone("noseBase", V_headTop, V_NoseBase)
        noseBase.parent = at.edit_bones['headTop']
        # 
        V_Nose = (.11, 0, .55)
        nose = createBone("nose", V_NoseBase, V_Nose)   
        nose.parent = at.edit_bones['noseBase']
        #
        V_NoseTip = (.13, 0, .55) 
        noseTip = createBone("noseTip", V_Nose, V_NoseTip)   
        noseTip.parent = at.edit_bones['nose']
        # 
        rotate('neckBase', .2, 1)
        #
        # Create horse back  and  hind legs.
        # bpy.context.scene.cursor_location = VRigArmatHead
        # "h" Prefix for all horse parts
        V_horseUpperBack = (-0.4, 0, 0)
        V_bonetail = [-0.2, 0, 0]  # From above header section
        hUpperBack = createBone("hUpperBack", V_bonetail, V_horseUpperBack)
        hUpperBack.parent = at.edit_bones[centaur.strName + '_bone']
        #
        V_horseMidBack = (-.6, 0, 0)
        hMidBack = createBone("hMidBack", V_horseUpperBack, V_horseMidBack)
        hMidBack.parent = at.edit_bones['hUpperBack']
        #
        V_horseBackLower = (-.8, 0, 0)
        hBackSway = createBone("hBackSway", V_horseMidBack, V_horseBackLower)
        hBackSway.parent = at.edit_bones['hMidBack']
        #
        V_horseHipCenter = (-1, 0, 0)
        hHipCenter = createBone("hHipCenter", V_horseBackLower, V_horseHipCenter)
        hHipCenter.parent = at.edit_bones['hBackSway']
        #
        hRearHipWidth = .13
        V_horseLHip = (-1, -hRearHipWidth, 0)
        hHipL = createBone("hHipL", V_horseHipCenter, V_horseLHip)
        hHipL.parent = at.edit_bones['hHipCenter']

        V_horseRHip = (-1, hRearHipWidth, 0)
        hHipR = createBone("hHipR", V_horseHipCenter, V_horseRHip)
        hHipR.parent = at.edit_bones['hHipCenter']
        #
        V_horseHipExtL = (-.94, -hRearHipWidth, -.2)
        V_horseHipExtR = (-.94, hRearHipWidth, -.2)
        hHipExtL = createBone("hHipExtL", V_horseLHip, V_horseHipExtL)
        hHipExtL.parent = at.edit_bones['hHipL']
        hHipextR = createBone("hHipExtR", V_horseRHip, V_horseHipExtR)
        hHipextR.parent = at.edit_bones['hHipR']

        V_horseFemurL = (-1.04, -hRearHipWidth, -.6)
        V_horseFemurR = (-1.04, hRearHipWidth, -.6)
        hFemurL = createBone("hFemurL", V_horseHipExtL, V_horseFemurL)
        hFemurL.parent = at.edit_bones['hHipExtL']
        hFemurR = createBone("hFemurR", V_horseHipExtR, V_horseFemurR)
        hFemurR.parent = at.edit_bones['hHipExtR']

        V_horseTibiaL = (-.98, -hRearHipWidth, -.94)
        V_horseTibiaR = (-.98, hRearHipWidth, -.94)
        hTibiaL = createBone("hTibiaL", V_horseFemurL, V_horseTibiaL)
        hTibiaL.parent = at.edit_bones['hFemurL']
        hTibiaR = createBone("hTibiaR", V_horseFemurR, V_horseTibiaR)
        hTibiaR.parent = at.edit_bones['hFemurR']
        #
        V_horseLAnkle = (-.98, -hRearHipWidth, -1.02)
        V_horseRAnkle = (-.98, hRearHipWidth, -1.02)
        hAnkleL = createBone("hAnkleL", V_horseTibiaL, V_horseLAnkle)
        hAnkleL.parent = at.edit_bones['hTibiaL']
        hAnkleR = createBone("hAnkleR", V_horseTibiaR, V_horseRAnkle)
        hAnkleR.parent = at.edit_bones['hTibiaR']
        # 
        V_horseLToe = (-.98, -hRearHipWidth, -1.1)
        V_horseRToe = (-.98, hRearHipWidth, -1.1)
        hToeL = createBone("hToeL", V_horseLAnkle, V_horseLToe)
        hToeL.parent = at.edit_bones['hAnkleL']
        hToeR = createBone("hToeR", V_horseRAnkle, V_horseRToe)
        hToeR.parent = at.edit_bones['hAnkleR']
        #
        # Create tail
        V_hTailJ1 = (-1.1, 0, 0)
        hTailJ1 = createBone("hTailJ1", V_horseHipCenter, V_hTailJ1)
        hTailJ1.parent = at.edit_bones['hHipCenter']
        #
        V_hTailJ2 = (-1.18, 0, 0)
        hTailJ2 = createBone("hTailJ2", V_hTailJ1, V_hTailJ2)
        hTailJ2.parent = at.edit_bones['hTailJ1']
        #
        V_hTailJ3 = (-1.26, 0, 0)
        hTailJ3 = createBone("hTailJ3", V_hTailJ2, V_hTailJ3)
        hTailJ3.parent = at.edit_bones['hTailJ2']
        #
        V_hTailJ4 = (-1.34, 0, 0)
        hTailJ4 = createBone("hTailJ4", V_hTailJ3, V_hTailJ4)
        hTailJ4.parent = at.edit_bones['hTailJ3']
        #
        V_hTailJ5 = (-1.42, 0, 0)
        hTailJ5 = createBone("hTailJ5", V_hTailJ4, V_hTailJ5)
        hTailJ5.parent = at.edit_bones['hTailJ4']
        #
        V_hTailJ6 = (-1.50, 0, 0)
        hTailJ6 = createBone("hTailJ6", V_hTailJ5, V_hTailJ6)
        hTailJ6.parent = at.edit_bones['hTailJ5']
        #
        V_hTailJ7 = (-1.58, 0, 0)
        hTailJ7 = createBone("hTailJ7", V_hTailJ6, V_hTailJ7)
        hTailJ7.parent = at.edit_bones['hTailJ6']
        #
        bpy.ops.object.mode_set(mode='OBJECT')
        rotate('hTailJ2', -.57, 1)
        #
    def character_type(self):
        return 'centaur'

        
centaur = Centaur
centaur.buildSkeleton(char)
bpy.ops.object.mode_set(mode='OBJECT')
# Do rotations
# 
bpy.ops.object.mode_set(mode='EDIT')

# ###############################################################################
# NEW SPEED FUNCTION   no rate = normal speed   1 = 1/2 rate    2 = double rate
# ###############################################################################
def getCycleRate(rate=0):
    if(hasattr(bpy.types.WindowManager, "cycle")):
        cycleRate = bpy.context.window_manager.cycle + 8
    else:
        cycleRate = 8.0  # Default cycleSpeed
    strRateEquation = "sin(radians(" + str(cycleRate) + "*frame))"
    if(rate == 1):
        strRateEquation = "sin(radians(" + str(cycleRate / 2) + "*frame))"  # Half cycle rate
    if(rate == 2):
        strRateEquation = "sin(radians(" + str(cycleRate * 2) + "*frame))" # Double cycle rate 
    return strRateEquation


def setWalkMovement(self, context):
    if(hasattr(bpy.types.WindowManager, "cycle")):
        cycleSpeed = bpy.context.window_manager.cycle + 8
    else:
        cycleSpeed = 8.0  # Default cycleSpeed
    # Left hip
    fn = "(asin(" + getCycleRate() + ") * 1)/3.14"
    femurLDriver = setAxisDriver(getEuler('femurL'), fn, 2)
    # Right hip
    fn = "-(asin(" + getCycleRate() + ") * 1)/3.14"
    femurRDriver = setAxisDriver(getEuler('femurR'), fn, 2)
    # Left Knee rotate
    fn = "((asin(" + getCycleRate() + ") * 1.2)/3.14 + .4) * (frame*(1/(frame+.0001)))"
    tibiaLDriver = setDriver(getEuler('tibiaL'), fn, 2)
    # Right Knee rotate
    fn = "(-(asin(" + getCycleRate() + ") * 1.2)/3.14 + .4) * (frame*(1/(frame+.0001)))"
    tibiaRDriver = setDriver(getEuler('tibiaR'), fn, 2)
    # Ankle rotation
    # Left
    fn = "((asin(" + getCycleRate() + ") * 2)/3.14 + .9) * (frame*(1/(frame+.0001)))-.8"
    ankleLDriver = setDriver(getEuler('ankleL'), fn, 2)  # 2 is z-axis
    # Right
    fn = "(-(asin(" + getCycleRate() + ") * 2)/3.14 + .9) * (frame*(1/(frame+.0001)))-.8"
    ankleRDriver = setDriver(getEuler('ankleR'), fn, 2)
    # Toe rotation
    # Left
    fn = "((asin(" + getCycleRate() + ") * 1.2)/3.14 + .4) * (frame*(1/(frame+.0001)))+.4"
    toeLDriver = setDriver(getEuler('toeL'), fn, 2)
    # Right
    fn = "((-asin(" + getCycleRate() + ") * 1.2)/3.14 + .4) * (frame*(1/(frame+.0001)))+.4"
    toeRDriver = setDriver(getEuler('toeR'), fn, 2)
    #
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Horse part of body functionality
    # hip
    fn = "-(asin(" + getCycleRate() + ") * .8)/3.14"
    hFemurLDriver = setAxisDriver(getEuler('hFemurL'), fn, 2)
    fn = "(asin(" + getCycleRate() + ") * .8)/3.14"
    hFemurRDriver = setAxisDriver(getEuler('hFemurR'), fn, 2)
    # Knee rotate
    fn = "-(asin(" + getCycleRate() + ") * 1.0)/3.14 + .2"
    hTibiaLDriver = setDriver(getEuler('hTibiaL'), fn, 2)
    fn = "(asin(" + getCycleRate() + ") * 1.0)/3.14 + .2"
    hTibiaRDriver = setDriver(getEuler('hTibiaR'), fn, 2)
    # Ankle rotation
    fn = "(-(asin(" + getCycleRate() + ") * 2)/3.14 + 1.4) * (frame*(1/(frame+.0001)))-1.0"
    hAnkleLDriver = setDriver(getEuler('hAnkleL'), fn, 2)  # 2 is z-axis
    fn = "((asin(" + getCycleRate() + ") * 2)/3.14 + 1.4) * (frame*(1/(frame+.0001)))-1.0"
    hAnkleRDriver = setDriver(getEuler('hAnkleR'), fn, 2)
    # Toe rotation
    fn = "(-(asin(" + getCycleRate() + ") * 1.2)/3.14 + .2) * (frame*(1/(frame+.0001)))+.4"
    hToeLDriver = setDriver(getEuler('hToeL'), fn, 2)
    fn = "((asin(" + getCycleRate() + ") * 1.2)/3.14 + .2) * (frame*(1/(frame+.0001)))+.4"
    hToeRDriver = setDriver(getEuler('hToeR'), fn, 2)    

    
setWalkMovement(centaur, context)


# setHorizontalSpeed Function controls the horizontal position of the centaur based z-axis rotational orientation
# Not associated with getCycleRate.  Speed is horizontal speed.  Rate is walk cycle frequency.
def setHorizontalSpeed(self, context):
    if(hasattr(bpy.types.WindowManager, "speed")):
        horizontalSpeed = bpy.context.window_manager.speed
    else:
        horizontalSpeed = 0.0  # Default speed
    strPosition = str(bpy.context.scene.frame_current / 2800 * horizontalSpeed)
    strRotateZ = str(bpy.context.scene.objects.active.rotation_euler.z)
    fnx = strPosition + "*frame*-sin(" + strRotateZ + ")"
    fny = strPosition + "*frame*-cos(" + strRotateZ + ")"
    setDriver(getEuler(centaur.strName + '_bone'), fny, 1, 'location')  # bird is 0
    dr_loc = setDriver(getEuler(centaur.strName + '_bone'), fnx, 0, 'location')  # bird is 2 
    bpy.ops.object.mode_set(mode='OBJECT')

  
    
    
def setSwayLR(self, context):  # left - right sway movement
    if(hasattr(bpy.types.WindowManager, "swayLR")):
        swayLR = str(bpy.context.window_manager.swayLR)
    else:
        swayLR = "1.0"
    fn = "-(asin(" + getCycleRate() + ")* " + swayLR + "*.01)"
    setDriver(getEuler(centaur.strName + '_bone'), fn, 1)
    bpy.ops.object.mode_set(mode='OBJECT')

def setSwayFB(self, context):  # forward - backward sway movement
    if(hasattr(bpy.types.WindowManager, "swayFB")):
        swayFB = str(bpy.context.window_manager.swayFB)
    else:
        swayFB = "1.0"
    fn = "-(asin(" + getCycleRate() + ")* " + swayFB + "*.01)"
    dr_SwayFB = setDriver(getEuler(centaur.strName + '_bone'), fn, 0)
    bpy.ops.object.mode_set(mode='OBJECT')
    
def setBounce(self, context):  # Bounce
    if(hasattr(bpy.types.WindowManager, "bounce")):
        bounce = str(bpy.context.window_manager.bounce)
    else:
        bounce = "1.0"
    eqBounce = "-(asin(" + getCycleRate(2) + ")* " + bounce + "*.01)"
    dr_Bounce = setDriver(getEuler(centaur.strName + '_bone'), eqBounce, 2, 'location') # Bounce
    bpy.ops.object.mode_set(mode='OBJECT')

# Head
def setJaw(centaur, context): # Jaw open - close    
    if(hasattr(bpy.types.WindowManager, "jawOC")):
        jawOC = str(bpy.context.window_manager.jawOC)
    else:
        jawOC = "0.0"
    fn = jawOC + " * -.1"  # Jaw open - close
    setDriver(getEuler('jaw'), fn, 0)
    bpy.ops.object.mode_set(mode='OBJECT')


# If centered at rear joint, parented,
# can be used  for eye movements
def setEye(centaur, context):     
    # Left - Right turn motion 
    if(hasattr(bpy.types.WindowManager, "eyeLR")):
        eyeLR = str(bpy.context.window_manager.eyeLR)
    else:
        eyeLR = "0.0"
    fn = str(eyeLR) + "* .1"  # eye left - right
    setDriver(getEuler('eyeR'), fn, 2)
    fn = str(eyeLR) + "* .1"  # eye left - right
    setDriver(getEuler('eyeL'), fn, 2)
    # Up - Down turn motion 
    eyeUD = str(centaur.eyeUD)  # Eye left - right
    if(hasattr(bpy.types.WindowManager, "eyeUD")):
        eyeUD = str(bpy.context.window_manager.eyeUD)
    else:
        eyeUD = "0.0"
    fn = str(eyeUD) + "* .1"  # eye left - right
    setDriver(getEuler('eyeL'), fn, 0)
    fn = str(eyeUD) + "* .1"  # eye left - right
    setDriver(getEuler('eyeR'), fn, 0)
    bpy.ops.object.mode_set(mode='OBJECT')


def setNeck(centaur, context):
    # Up - Down turn motion 
    if(hasattr(bpy.types.WindowManager, "neckUD")):
        neckUD = str(bpy.context.window_manager.neckUD)
    else:
        neckUD = "0.0"
    fn = str(neckUD) + "* -.2"
    setAxisDriver(getEuler('neckJ1'), fn, 2)
    setAxisDriver(getEuler('neckJ2'), fn, 2)
    setAxisDriver(getEuler('neckJ3'), fn, 2)
    fn = str(neckUD) + "* -.04"
    setAxisDriver(getEuler('neckJ4'), fn, 2)
    setAxisDriver(getEuler('neckJ5'), fn, 2)
    setAxisDriver(getEuler('neckJ6'), fn, 2)
    # Sideways motion
    if(hasattr(bpy.types.WindowManager, "neckLR")):
        neckLR = str(bpy.context.window_manager.neckLR)
    else:
        neckLR = "0.0"
    fn = str(neckLR) + "* -.1"
    setAxisDriver(getEuler('neckJ2'), fn, 0)
    setAxisDriver(getEuler('neckJ3'), fn, 0)
    setAxisDriver(getEuler('neckJ4'), fn, 0)
    setAxisDriver(getEuler('neckJ5'), fn, 0)
    setAxisDriver(getEuler('neckJ6'), fn, 0)
    # Left - Right turn motion 
    if(hasattr(bpy.types.WindowManager, "neckTurn")):
        neckTurn = str(bpy.context.window_manager.neckTurn)
    else:
        neckTurn = "0.0"
    fn = str(neckTurn) + "* .04"  # neck left - right
    setAxisDriver(getEuler('neckJ2'), fn, 1)
    setAxisDriver(getEuler('neckJ3'), fn, 1)
    setAxisDriver(getEuler('neckJ4'), fn, 1)
    setAxisDriver(getEuler('neckJ5'), fn, 1)
    setAxisDriver(getEuler('neckJ6'), fn, 1)
    bpy.ops.object.mode_set(mode='OBJECT')



def setHead(centaur, context):
    # Up - Down turn motion 
    if(hasattr(bpy.types.WindowManager, "headUD")):
        headUD = str(bpy.context.window_manager.headUD)
    else:
        headUD = "0.0"
    fn = str(headUD) + "* .2"
    setAxisDriver(getEuler('neckJ7'), fn, 2)
    # Sideways motion
    if(hasattr(bpy.types.WindowManager, "neckLR")):
        headLR = str(bpy.context.window_manager.headLR)
    else:
        headLR = "0.0"
    fn = str(headLR) + "* -.1"
    setAxisDriver(getEuler('neckJ7'), fn, 0)
    
    
def setHip(centaur, context):
    # Pelvis / Hip rotation    
    if(hasattr(bpy.types.WindowManager, "hipRotate")):
        hipRotate = str(bpy.context.window_manager.hipRotate*.1)
    else:
        hipRotate = '0.0'
    fn = "(asin(" + getCycleRate() + ") * " + hipRotate + ")/3.14"
    pelvisDriver = setAxisDriver(getEuler('pelvis'), fn, 1)
    # hip up - down movement
    if(hasattr(bpy.types.WindowManager, "hipUD")):
        hipUD = str(bpy.context.window_manager.hipUD*.06)
    else:
        hipUD = '0.0'
    fn = "(asin(" + getCycleRate() + ") * " + hipUD + ")/3.14"
    scapulaLDriver = setDriver(getEuler('hipL'), fn, 0)
    fn = "-(asin(" + getCycleRate() + ") * " + hipUD + ")/3.14"
    scapulaRDriver = setDriver(getEuler('hipR'), fn, 0)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.mode_set(mode='OBJECT')


def setTail(centaur, context):
    if(hasattr(bpy.types.WindowManager, "tailLR")):
        fn = str(bpy.context.window_manager.tailLR*.02)
    else:
        fn = '0.0'
    hTailJ2Driver = setDriver(getEuler('hTailJ2'), fn, 2)
    hTailJ3Driver = setDriver(getEuler('hTailJ3'), fn, 2)
    hTailJ4Driver = setDriver(getEuler('hTailJ4'), fn, 2)
    hTailJ5Driver = setDriver(getEuler('hTailJ5'), fn, 2)
    hTailJ6Driver = setDriver(getEuler('hTailJ6'), fn, 2)
    hTailJ7Driver = setDriver(getEuler('hTailJ7'), fn, 2)
    if(hasattr(bpy.types.WindowManager, "tailUD")):
        fn = str(bpy.context.window_manager.tailUD*.02)
    else:
        fn = '0.0'
    hTailJ2Driver = setDriver(getEuler('hTailJ2'), fn, 0)
    hTailJ3Driver = setDriver(getEuler('hTailJ3'), fn, 0)
    hTailJ4Driver = setDriver(getEuler('hTailJ4'), fn, 0)
    hTailJ5Driver = setDriver(getEuler('hTailJ5'), fn, 0)
    hTailJ6Driver = setDriver(getEuler('hTailJ6'), fn, 0)
    hTailJ7Driver = setDriver(getEuler('hTailJ7'), fn, 0)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    
# deselect all objects.
bpy.ops.object.mode_set(mode='OBJECT')
for ob in bpy.context.selected_objects:
    ob.select = False

# Get the current vector coordinates of the centaur
centaur.x = bpy.context.scene.objects.active.location.x
centaur.y = bpy.context.scene.objects.active.location.y
centaur.z = bpy.context.scene.objects.active.location.z

bpy.types.WindowManager.speed = bpy.props.FloatProperty(update=setHorizontalSpeed, name="Speed", default=0.0)
bpy.types.WindowManager.cycle = bpy.props.FloatProperty(update=setWalkMovement, name="Cycle", default=1.0)
bpy.types.WindowManager.swayLR = bpy.props.FloatProperty(update=setSwayLR, name="Sway LR", default=1.0)
bpy.types.WindowManager.swayFB = bpy.props.FloatProperty(update=setSwayFB, name="Sway FB", default=0.0)
bpy.types.WindowManager.bounce = bpy.props.FloatProperty(update=setBounce, name="Bounce", default=1.0)
bpy.types.WindowManager.hipRotate = bpy.props.FloatProperty(update=setHip, name="Hip Rotate", default=2.0)
bpy.types.WindowManager.hipUD = bpy.props.FloatProperty(update=setHip, name="HipUD", default=2.0)
bpy.types.WindowManager.neckUD = bpy.props.FloatProperty(update=setNeck, name="NeckUD", default=0.0)
bpy.types.WindowManager.neckLR = bpy.props.FloatProperty(update=setNeck, name="NeckLR", default=0.0)
bpy.types.WindowManager.neckTurn = bpy.props.FloatProperty(update=setNeck, name="NeckTurn", default=0.0)
bpy.types.WindowManager.headUD = bpy.props.FloatProperty(update=setHead, name="HeadUD", default=0.0)
bpy.types.WindowManager.headLR = bpy.props.FloatProperty(update=setHead, name="HeadLR", default=0.0)
bpy.types.WindowManager.jawOC = bpy.props.FloatProperty(update=setJaw, name="JawOC", default=0.0)
bpy.types.WindowManager.eyeLR = bpy.props.FloatProperty(update=setEye, name="EyeLR", default=0.0)
bpy.types.WindowManager.eyeUD = bpy.props.FloatProperty(update=setEye, name="EyeUD", default=0.0)
bpy.types.WindowManager.tailLR = bpy.props.FloatProperty(update=setTail, name="TailLR", default=0.0)
bpy.types.WindowManager.tailUD = bpy.props.FloatProperty(update=setTail, name="TailUD", default=0.0)



class Pose_Button(bpy.types.Operator):
    bl_idname = "pose.button"
    bl_label = "Pose Character"
    bl_description = "Pose Character"
    hidden = False
    def execute(self, context):
        bpy.context.scene.frame_set(0)
        bpy.ops.object.mode_set(mode='OBJECT')
        return{'FINISHED'}

        
class OBPanel(bpy.types.Panel):
    bl_label = "centaur Control"
    bl_idname = "selected_object"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "UI"
    bl_context = "objectmode"
    def draw(self, context):
        layout = self.layout
        layout.row().prop(context.window_manager, 'speed')
        layout.row().prop(context.window_manager, 'cycle')
        layout.row().prop(context.window_manager, 'swayLR')
        layout.row().prop(context.window_manager, 'swayFB')
        layout.row().prop(context.window_manager, 'bounce')
        layout.row().prop(context.window_manager, 'hipRotate')
        layout.row().prop(context.window_manager, 'hipUD')
        layout.row().prop(context.window_manager, 'neckUD')
        layout.row().prop(context.window_manager, 'neckLR')
        layout.row().prop(context.window_manager, 'neckTurn')
        layout.row().prop(context.window_manager, 'headUD')
        layout.row().prop(context.window_manager, 'headLR')
        layout.row().prop(context.window_manager, 'jawOC')
        layout.row().prop(context.window_manager, 'eyeLR')
        layout.row().prop(context.window_manager, 'eyeUD')
        layout.row().prop(context.window_manager, 'tailLR')
        layout.row().prop(context.window_manager, 'tailUD')
        layout.row().operator("pose.button")


def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.mode_set(mode='OBJECT')

if __name__ == "__main__":
    register()
