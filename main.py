import cv2
import numpy as np
import argparse

import move
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



def TakeOperation_Num(MaxNum):
    # Taking input
    Operation_Num = input("\nEnter the operation number: ")

    try:        # If valid number passed
        Operation_Num = Operation_Num.replace(" ", "")
        Operation_Num = int(Operation_Num)
        if 0 <= Operation_Num < MaxNum:
            return Operation_Num
        else:
            raise ValueError
    except:     # If invalid number passed
        print("\nInvalid operation number entered.")
        hf.Sleep()
        return None


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
        cv2.waitKey(1)

        # Taking operation number
        Operation_Num = TakeOperation_Num(len(action))
        if Operation_Num is None:                   # Invalid operation number entered
            continue
        # Getting action string
        action_str = action[Operation_Num]
        
        if action_str is None:                      # Continue if valid key is not pressed
            continue

        elif action_str == "ADD_LAYER":             # Add a new layer
            input_output.AddNewLayer(Canvas)

        elif action_str == "SHOW_SELECTED_LAYERS":  # Show selected layers
            input_output.ChooseLayersToShow(Canvas, "Layers selection")

        elif action_str == "LAYER_OPERATIONS":      # Rearrange/ Delete/ Merge/ Rename/ Duplicate layers
            input_output.LayerOperations(Canvas, "Layer operations")

        elif action_str == "MOVE_TOOL":             # Move tool
            move.MoveTool(Canvas, window_title)

        elif action_str == "MARQUEE_TOOL":          # Marquee tool
            input_output.MarqueeTool(Canvas, window_title)

        elif action_str == "LASSO_TOOL":            # Lasso Tool
            input_output.LassoTool(Canvas, window_title)
        
        elif action_str == "SELECTION_TOOL":        # Selection Tool
            input_output.SelectionTool(Canvas, window_title)

        elif action_str == "EXIT":                  # Exit code
            break


    cv2.destroyAllWindows()

    # Clearing the screen
    hf.Clear()