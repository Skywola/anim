# http://tutorial-art-design.blogspot.com/2013/06/procedural-domino-array-animation-using.html
# bpy.ops.object.mode_set(mode='OBJECT')   # bpy.ops.object.mode_set(mode='POSE')

ch = Character(b)
legL = Leg(b, hip, left)
ch.obs.append(legL)  # ** MUST ** save these for retrieval
# Leg Femur
fn = str(legL.rotateRangeFemur) +'*(clock()+'+ str(legL.rotatePositionFemur)+")" + legL.ZeroAtFrame0
bJ1L = legL.leg_bones[0]
Driver1 = setAxisDriver(getEuler(bJ1L.name), fn, 2)
# Leg Tibia
fn = str(legL.rotateRangeTibia) +'*(clock()+'+ str(legL.rotatePositionTibia)+")" + legL.ZeroAtFrame0
bJ3L = legL.leg_bones[2]
Driver3 = setAxisDriver(getEuler(bJ3L.name), fn, 2)
# Ankle
legL.rotateRangeAnkle = 0.8
fn = str(legL.rotateRangeAnkle) +'*(clock()+'+ str(legL.rotatePositionAnkle)+")" + legL.ZeroAtFrame0
bJ5L = legL.leg_bones[4]
setAxisDriver(getEuler(bJ5L.name), fn, 2)
#
# Now Right leg
legR = Leg(b, hip, right)
ch.obs.append(legR)
# Leg Femur
fn = str(legR.rotateRangeFemur) +'*(clock()+'+ str(legR.rotatePositionFemur)+")" + legR.ZeroAtFrame0
bJ1R = legR.leg_bones[0]
setAxisDriver(getEuler(bJ1R.name), "-1*" + fn, 2)
# Leg Tibia
fn = str(legR.rotateRangeTibia) +'*(clock()+'+ str(legR.rotatePositionTibia*-1)+")" + legR.ZeroAtFrame0
bJ3R = legR.leg_bones[2]
setAxisDriver(getEuler(bJ3R.name), "-1*" + fn, 2)
# Ankle
legR.rotateRangeAnkle = .08
fn = str(legR.rotateRangeAnkle) +'*-1*(clock()+'+ str(legR.rotatePositionAnkle)+")" + legR.ZeroAtFrame0
bJ5R = legR.leg_bones[4]
setAxisDriver(getEuler(bJ5R.name), fn, 2)
#
#
# Arms
armL = Arm(b, ch.biped_shoulderlocationL, left)
ch.obs.append(armL)  # ** MUST ** save these for retrieval
# Humerus - Arms rotation
fn = "(" + str(armL.rotatePositionHumerus)+"+clock()*" + str(armL.rotateRangeHumerus) + ")" + ZeroAtFrame0
aJ1L = armL.arm_bones[0]
setAxisDriver(getEuler(aJ1L.name), fn, 2)
# Ulna - Arms rotation
fn = "(-1*" + str(armL.rotatePositionUlna)+"+clock()*" + str(armL.rotateRangeUlna) + ")" + ZeroAtFrame0
aJ3L = armL.arm_bones[2]
setAxisDriver(getEuler(aJ3L.name), fn, 2)

armR = Arm(b, ch.biped_shoulderlocationL, right)
ch.obs.append(armR)
# Humerus - Arms rotation
fn = "(" + str(armR.rotatePositionHumerus)+"+clock()*" + str(armR.rotateRangeHumerus) + ")" + ZeroAtFrame0
aJ1R = armR.arm_bones[0]
setAxisDriver(getEuler(aJ1R.name), fn, 2)
# Ulna - Arms rotation
fn = "(" + str(armR.rotatePositionUlna)+"+clock()*" + str(armR.rotateRangeUlna) + ")" + ZeroAtFrame0
aJ3R = armR.arm_bones[2]
setAxisDriver(getEuler(aJ3R.name), fn, 2)

head = Head(b, ch.biped_neckbase_location)


'''
# Centaur
quad = Character(q)
legL = Leg(q, quad.quadruped_hiplocation_frontL, left)
legR = Leg(q, quad.quadruped_hiplocation_frontR, right)
legL = Leg(q, quad.quadruped_hiplocation_backL, left, back)
legL = Leg(q, quad.quadruped_hiplocation_backR, right, back)
char = Character(b)
armL = Arm(b, char.biped_shoulderlocationL, left)
armL = Arm(b, char.biped_shoulderlocationR, right)
head = Head(b, char.biped_neckbase_location)

# Biped
char = Character(b)
armL = Arm(b, char.biped_shoulderlocationL, left)
armL = Arm(b, char.biped_shoulderlocationR, right)
legL = Leg(b, char.biped_hiplocationL, left)
legR = Leg(b, char.biped_hiplocationR, right)
head = Head(b, char.biped_neckbase_location)

# Quad
quad = Character(q)
legL = Leg(q, quad.quadruped_hiplocation_frontL, left)
legR = Leg(q, quad.quadruped_hiplocation_frontR, right)
legL = Leg(q, quad.quadruped_hiplocation_backL, left, back)
legL = Leg(q, quad.quadruped_hiplocation_backR, right, back)
qhead = Head(q, quad.quadruped_necklocation)

# Avian - bird
avian = Character(a)
ahead = Head(a, avian.biped_neckbase_location)
xyz = avian.biped_location
legL = Leg(a, xyz, left)
legR = Leg(a, xyz, right)
tail = Tail(a, xyz)
wing = Wing(a, xyz, left)
wing = Wing(a, xyz, right)
'''

