import cv2
import numpy as np
import argparse

import layers
import macros as m
import input_output
import helping_functions as hf
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
    print("=================================================================================================================")
    for i in action_statements:
        print(i)
    print("=================================================================================================================")
    print()



if __name__ == "__main__":
    ArgParse()          # Parsing command line arguments

    # Reading and initializing the image
    Canvas = layers.Initialize(args)

    while True:
        # Clearing the screen
        hf.Clear()
    
        # Setting window title
        window_title = m.DEFAULT_CANVAS_TITLE

        # Printing action statements for the user
        PrintActionStatements()

        # Showing all layers
        Canvas.Show()
        key_pressed = cv2.waitKey(0)
        action_str = action[key_pressed]
        
        if action_str is None:                      # Continue if valid key is not pressed
            continue

        elif action_str == "ADD_LAYER":             # Add a new layer
            input_output.AddNewLayer(Canvas)

        elif action_str == "SHOW_SELECTED_LAYERS":  # Show selected layers
            input_output.ChooseLayersToShow(Canvas, "Layers selection")

        elif action_str == "LAYER_OPERATIONS":       # Rearrange/ merge or delete layers
            input_output.LayerOperations(Canvas, "Layer operations")

        elif action_str == "BREAK":                 # Breaking
            break


    cv2.destroyAllWindows()

    # Clearing the screen
    hf.Clear()