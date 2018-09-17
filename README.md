# Agent-GPY
A python bot which is tailor made to play Counter Strike 1.6 using Image Processing and Controller Emulation <br>

# Instructions
1. Install Python3
2. Download the source
3. Run Counter Strike 1.6, and pick a team
4. Run g.py using the following command <br>
  $ g.py -t \<team\> <br>
    (team can be either 'ct' or 't')

# Working mechanism/algorithm
1. Grab screen for the game's viewport
2. Use Haar Cascades to recognize teammates vs hostiles (The trained data had been made using a set of 1200 images of targets)
3. Use Controller Emulator scripts like PyAutoGUI to flick mouse after identifying targets on the viewport
4. Use the library to click
5. Check back the viewport data for movement clues <br>
  5.1. Use CV2 image processing library to get a greyscale version of the viewport <br>
  5.2. Use Gaussian Blur to blur out the high noise tiled regions on the screen <br>
  5.3. Run Hough Lines transform to get lines <br>
  5.4. Discard vertical lines <br>
  5.5. Check for two adequately long lines on opposite halves of the viewport with opposite slope, to recognize them as the edges at the feet of walls <br>
  5.6. Apply Forward movement input if you get a positive for the pattern in 5.5 <br>
  5.7. Check for oppositely sloped lines on the same halves <br>
  5.8. Apply Right/Left movement input against the half in which you get a positive for the pattern in 5.7
  
# Future Work
Try using the same code, train for images of real life objects/robots_from_opp_teams, and make a robot that plays the same objectives as in Counter Strike
