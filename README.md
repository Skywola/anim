This code is open source, you are free to use it, modify it. Simply give credit where credit is due, by that I would mean, 
simply that I was the original author of the first manifestation of this program.

Coder : Shawn D Irwin (skywola@hotmail.c0m)  Replace the zero in the email address with an "o", [ trap for spambots ].

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License 
as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the 
implied warranty of MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General 
Public License for more details.  For a copy of the GNU General Public License, see
http://www.gnu.org/licenses

This program allows you to animate a biped, bird, quadruped, centaur, or a spider very 
rapidly in Blender. (See www.blender.org)
You just click the button to add the bones, parent the character mesh to the bones, hit 
the play button, set the speed, and off it goes. You will need to download the Blender file from this site, 
this is not yet a plugin, I want it to be out for a while before I add it as a plugin. 

THE INSTANT ANIMATION PANEL IS NO LONGER BE LOCATED ON THE RIGHT-SIDE PANEL, BUT ON THE 
LEFT-SIDE PANEL, LISTED UNDER THE FAR-LEFT VERTICALLY LOCATED SUB-MENU AS "INSTANT ANIMATION", 
IN ORDER TO BRING UP THE PROPER PANEL, PRESS "T" WHILE YOUR MOUSE IS OVER THE 3D VIEW.

Note also, the plugin will not include the basic models for each character type.

The tutorials are in two parts:

Part 1: https://youtu.be/B0P1kZtsqjE     General start-up get-it-running info.

Part 2: https://youtu.be/APiFoEbxS8E     More in depth.


To truly understand how to make the program work for you, you should watch BOTH 
tutorials. Questions, comments, ideas are welcome. Watch the tutorials to get started.

The method for animating a character is listed below, but the tutorials are more detailed and up-to-date.  
The Blend file now contains each character mesh I used as a calibrator, you can freely use them or sub 
in your own character.

Steps:
1. A. If you downloaded the .blend file:
         Run the script in the text editor by clicking on the "Run Script" button on the  lower right
   B. If you downloaded the plugin file:
      In Blender, go to File > User Preferences, then click the button at the bottom of the window called
      "Install Addon From File".  Navigate to the plugin file (IA_V2.0_Plugin.py) you downloaded, select it, and
      on the upper right, click the button "Install Add-on From File".  
2. If the control panel is not open in the 3D view, push the "t" button to bring up the panel.
3. Look on the far left of the panel for the sub-menu "Instant Animation", and click it.
4. Click on one of the character build buttons.
5. Hold down the shift button, select the  mesh, then select the bones. 
    (Make sure  you are in the object mode, you  should  already be.)
6. When both the  mesh and the bones are selected, hold down the control  button
   and press the "p" button at the same time.  You should  see a menu  come up 
   with the option "With envelope weights".  If it does not show (Blender bug) ,
   re-select the mesh and then the bones and try again.  Once you get it click on
  it, and  the character will be skinned to the bone set.
7. Click "Get Character Panel".
8. To make the character move, look for the "Speed" control and enter a "9", then your enter key.
9. Select the play button and make any adjustments you want, on the controls listed.

Addendum:  Be attentive when working with the wings;  it is easy to get confused between the "Bird Wings" and the "Solo Wings", and then  wonder why the program is not responding to the  wings you are  working on . . . you have to be in the right panel and switch panels when you are changing from the bird wings to the solo wings and vice versa.   I have added captions to the buttons to help prevent this from  happening, so the buttons will say "bird" or "solo", so you have to keep track of it.   I mention it because even I, the programmer himself, have become confused about it.  If you experience the wings not responding when you make a change this is the first thing you should suspect as the problem, select the character you  want to work on and click on the "Get Character Panel" button each time  you switch from one character or wing set to another.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

This program will automatically animated a Biped, Quadruped, Bird, Centaur or a Spider . . . in Blender (www.blender.org).  This project, (When completed) will allow you to choosing a character type, and it will create the skeleton for the character, skin the character to the skeleton and, when you press the play button the character will walk or run. The quadraped will also hop or gallop. The project will be done via Python, it does not require any fooling with IK, and it has "Stabilization" (it adds bones that allow the character to move freely without major distortions in the character skin), which minimizes having to paint skin weights.

When created, the bones are in the pose position, and you then attach the character to it, click the activate button, hit PLAY, and the character walks or runs away. Just like that . . . . if you hit rewind, you can re-pose the character. You can make the character walk or run in any direction, or create a crowd of characters, all walking or running in different directions. You can manipulate all the fingers of each hand at once, to open or close the hand or you can control the fingers individually. 


   You can track my progress for this project on Blender Open Artist Group. https://www.linkedin.com/groups/6677523  This is a work in process, so I do upload updates after I create them, you can monitor them.
