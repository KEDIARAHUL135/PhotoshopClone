import cv2
import numpy as np
import argparse

import layers
import macros as m
import input_output
from pressed_key_lookup import *


# Parsing the arguments
def ArgParse():
    global args 		# Declaring globally to acces it from anywhere. 

    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    
    ap.add_argument("-img", "--ImagePath", default=None,
                    help="Path of the image file.")
    ap.add_argument("-s", "--Shape", default=None, type=int, nargs=2,
                    help="Shape of the canvas(integer values only) - [height, width]")

    args = vars(ap.parse_args())            # Converting it to dictionary.
    


# Printing the action statements for the user to select a tool/feature
def PrintActionStatements():
    print()
    print("======================================================================================")
    for i in action_statements:
        print(i)
    print("======================================================================================")
    print()



if __name__ == "__main__":
    ArgParse()          # Parsing command line arguments

    # Reading and initializing the image
    all_layers = layers.Initialize(args)

    while True:
        window_title = m.DEFAULT_CANVAS_TITLE

        # Printing 
        PrintActionStatements()

        # Showing all layers
        all_layers.Show()
        key_pressed = cv2.waitKey(0)
        action_str = action[key_pressed]
        
        if action_str is None:                      # Continue if valid key is not pressed
            continue

        elif action_str == "ADD_LAYER":             # Add a new layer
            input_output.AddNewLayer(all_layers)

        elif action_str == "BREAK":                 # Breaking
            break


    cv2.destroyAllWindows()
