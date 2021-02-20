FOR BLENDER 2.9, PROTOTYPE - This is the NEW coding, concentrated on object oriented principles, using classes.
Currently, this is a step back from the previous coding, but the coding is far better in terms of quality and
understandability.  I am posting this code at this point in case anyone else  is interested in using it, building
from it . . . 
Coder : Shawn D Irwin (skywola@hotmail.com)

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License 
as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the 
implied warranty of MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General 
Public License for more details.  For a copy of the GNU General Public License, see
http://www.gnu.org/licenses

This program will allow you (when it is completed) to animate a biped, bird, quadruped, centaur, or 
a spider very rapidly in Blender. (See www.blender.org)
You just click the button to add the bones, parent the character mesh to the bones, hit 
the play button, set the speed, and off it goes. You will need to download the Blender file from this site, 
this is not yet a plugin, I want it to be out for a while before I add it as a plugin. 

INSTRUCTIONS FOR BLENDER 2.79 VERSION OF THIS PLUGIN:
Run in the console the animator00.py file, then run the build00.py file in the console. Press the
play button, and it will start walking.  Note that this is very early prototype code, so using
it for an actual animation at this point is probably possible, but not as good as it will be once
the project is finished, there is still a long way to go, still need to add shoulder sway, hip sway, 
etc. and to put up the user interface.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

When completed, this program will automatically animate a Biped, Quadruped, Bird, Centaur or a Spider . . . in Blender (www.blender.org).  This project, (When completed) will allow you to choosing a character type, and it will create the skeleton for the character, skin the character to the skeleton and, when you press the play button the character will walk or run. The quadraped will also hop or gallop. The project will be done via Python, it does not require any fooling with IK, and it has "Stabilization" (it adds bones that allow the character to move freely without major distortions in the character skin), which minimizes having to paint skin weights.

When created, the bones are in the pose position, and you then attach the character to it, click the activate button, hit PLAY, and the character walks or runs away. Just like that . . . . if you hit rewind, you can re-pose the character. You can make the character walk or run in any direction, or create a crowd of characters, all walking or running in different directions. You can manipulate all the fingers of each hand at once, to open or close the hand or you can control the fingers individually. 


   You can track my progress for this project on Blender Open Artist Group. https://www.linkedin.com/groups/6677523  This is a work in process, so I do upload updates after I create them, you can monitor them.
