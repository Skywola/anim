# http://tutorial-art-design.blogspot.com/2013/06/procedural-domino-array-animation-using.html
# bpy.ops.object.mode_set(mode='OBJECT')   # bpy.ops.object.mode_set(mode='POSE')

ch = Character(b)
torso = Torso(ch)
pelvis = Pelvis(ch)
legL = Leg(ch, left)
legR = Leg(ch, right)
armL = Arm(ch, left)
armR = Arm(ch, right)
head = Head(ch)

setActiveArmature(legL)
animateBipedLeg(ch, legL, False)  # False is for flip
setActiveArmature(pelvis, False)
bpy.ops.object.parent_set(type='BONE')

setActiveArmature(legR)
animateBipedLeg(ch, legR, True)
setActiveArmature(pelvis, False)
bpy.ops.object.parent_set(type='BONE')

setActiveArmature(armL)
dropArm(armL, -90)
animateBipedArm(ch, armL, False)
setActiveArmature(torso, False)
bpy.ops.object.parent_set(type='BONE')

setActiveArmature(armR)
dropArm(armR, 90)
animateBipedArm(ch, armR, True)
setActiveArmature(torso, False)
bpy.ops.object.parent_set(type='BONE')
 
setActiveArmature(torso)
setShoulderSwayFB(ch, torso)
setActiveArmature(armL)




setActiveArmature(armR)


ch2 = Character(b)
t2 = Torso(ch2)
p2 = Pelvis(ch2)
legL2 = Leg(ch2, left)
legR2 = Leg(ch2, right)
armL2 = Arm(ch2, left)
armR2 = Arm(ch2, right)
head2 = Head(ch2)

setActiveArmature(legL2)
animateBipedLeg(ch2, legL2, False)  # False is for flip
setActiveArmature(legR2)
animateBipedLeg(ch2, legR2, True)

setActiveArmature(armL2)
dropArm(armL2, -90)
animateBipedArm(ch2, armL2, False)
setActiveArmature(armR2)
dropArm(armR2, 90)
animateBipedArm(ch2, armR2, True)

'''
# Biped
char = Character(b)
armL = Arm(b, ch.biped_shoulderlocationL, left)
armL = Arm(b, ch.biped_shoulderlocationR, right)
legL = Leg(b, ch.biped_hiplocationL, left)
legR = Leg(b, ch.biped_hiplocationR, right)
head = Head(b, ch.biped_neckbase_location)

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

# Centaur
quad = Character(q)
legL = Leg(q, quad.quadruped_hiplocation_frontL, left)
legR = Leg(q, quad.quadruped_hiplocation_frontR, right)
legL = Leg(q, quad.quadruped_hiplocation_backL, left, back)
legL = Leg(q, quad.quadruped_hiplocation_backR, right, back)
char = Character(b)
armL = Arm(b, ch.biped_shoulderlocationL, left)
armL = Arm(b, ch.biped_shoulderlocationR, right)
head = Head(b, ch.biped_neckbase_location)

'''

'''

bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# nm = bpy.context.active_pose_bone.name  # 'biped1_right_legJ1' 'biped1_right_legJ8'
'''

