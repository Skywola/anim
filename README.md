
# anim
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

Blender-Python Animation files -

The method for animating a character is listed below.  The Blend file  now contains the character
mesh I am using as a calibrator, you can freely use it or sub in your own character, just make 
sure you set the bones in a similar way on your character, or you may have some extra skinning 
or painting weights to do.

Steps:
1. Run the script in the text editor by clicking on the "Run Script" button on the  lower right
2. If the control panel is not open in the 3D view, push the "n" button to bring up the panel.
3. Scroll to the bottom of the panel if needed by placing your cursor over  the  panel and rolling 
    the mouse button or  clicking and dragging the scroll bar.
4. Click on the  "Build Biped" button.
5. Hold down the shift button, select the  mesh, then select the bones. 
    (Make sure  you are in the object mode, you  should  already be.)
6. When both the  mesh and the bones are selected, hold down the control  button
   and press the "p" button at the same time.  You should  see a menu  come up 
   with the option "With envelope weights".  If it does not show (Blender bug) ,
   re-select the mesh and then the bones and try again.  Once you get it click on
  it, and  the character will be skinned to the bone set.
  IMPORTANT: USE ENVELOPE WEIGHTS FOR THE BIPED, BUT USE AUTOMATIC WEIGHTS FOR
  THE BIRD . . . . I am still experimenting weights, I would like to be able
  to use the same settings for both, but so far I have not reached that point.
7. Click "Activate Biped Panel".
8. Select the play button and  make  any adjustments you  want, like 
    clicking the "Drop Arms" button!


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

This program will automatically animated a Biped, Quadruped, Bird, Centaur or a Spider . . . in Blender (www.blender.org).  This project, (When completed) will allow you to choosing a character type, and it will create the skeleton for the character, skin the character to the skeleton and, when you press the play button the character will walk or run. The quadraped will also hop or gallop. The project will be done via Python, it does not require any fooling with IK, and it has "Stabilization" (it adds bones that allow the character to move freely without major distortions in the character skin), which minimizes having to paint skin weights.

When created, the bones are in the pose position, and you then attach the character to it, click the activate button, hit PLAY, and the character walks or runs away. Just like that . . . . if you hit rewind, you can re-pose the character. You can make the character walk or run in any direction, or create a crowd of characters, all walking or running in different directions. You can manipulate all the fingers of each hand at once, to open or close the hand or you can control the fingers individually. 
   You can track my progress for this project on Blender Open Artist Group. https://www.linkedin.com/groups/6677523  Currently I am working on refactoring and perfecting all of the characters and their movements.  After that is done I will work on a general interface to handle the  creation of all the  characters, add more gaits to some characters, i.e. biped run, bird, hop, quadruped gallop, trot, pace, etc. and, I may add a dragon and a kangaroo.
