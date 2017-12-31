# anim
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Blender-Python Animation files
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
NOTE!!! :
Biped posing problem has been  solved.  The method for animating a character
has changed and is listed below.  The Blend file  now contains the character
mest I am using as a calibrator, you can freely use it or sub in your own 
character, just make sure you set the bones in a similar way on your character,
or you may have some extra skinning or painting weights to do.

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
7. Click "Activate Biped Panel".
8. Select the play button and  make  any adjustments you  want, like 
    clicking the "Drop Arms" button!

Overall, I am still not satisfied with the walk performance, so I will likely
be adding tweaks  here  and there, but the greatest programming difficulties 
have been overcome, so the rest should be  relatively light work, and, as
mentioned, you can  tweak the controls yourself to change the movement.
For now, it will be onward to solving the  posing problem for any other 
characters it may effect, then once that is done, I will combine all the 
characters into one  functioning interface.



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%



OLDER INFO - for characters not modified after 12-30-2017
From now until I create a all-inclusive interface, when you open  the file in Blender, you  will need to click the "Run Script"
button in the lower right panel of the text editor, that way you will get all the options that you can modify to change the  characteristics of the movements, which is important! If you do not do that, you will have no way of seeing all of your options, nor  will you even see the character's bones.

In 2007, when I was using Maya, I created a program called Walkerman, a MEL program that automatically animated a Biped, Quadruped, Bird, Centaur or a Spider . . . Now I am working on a similar project for Blender (www.blender.org).  This program will allow you to choosing a character type, and it will create the skeleton for the character, skin the character to the skeleton and, when you press the play button the character will walk or run. The quadraped will also hop or gallop. The project will be done via Python, it does not require any fooling with IK, and it has "Stabilization" (it adds bones that allow the character to move freely without major distortions in the character skin), which minimizes having to paint skin weights.

When created, the bones are in the pose position, and you then attach the character to it, hit PLAY, and the character walks or runs away. Just like that . . . . if you hit rewind, you can re-pose the character. You can make the character walk or run in any direction, or create a crowd of characters, all walking or running in different directions. You can manipulate all the fingers of each hand at once, to open or close the hand or you can control the fingers individually. The old Walkerman program is approaching 30,000 downloads . . . I'd like to  see the same or better results for the Instant Animation program for Blender . . .  The goal is to complete this project by December.
What I have done so far is standardization of the code header, the bird, the biped, and I am making all of it available for download as open source on my github site.  You can track my progress on Blender Open Artist Group. https://www.linkedin.com/groups/6677523  Currently I have started the Centaur, and after that is complete, move on to the quadruped.  After that is done I will work on a general interface to handle the  creation of all the  characters, add more gaits to some characters, i.e. biped run, bird, hop, quadruped gallop, trot, pace, etc. and, I may add a dragon and a kangaroo.
