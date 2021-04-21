import cv2
import numpy as np
import argparse

import macros
from pressed_key_lookup import *


# Parsing the arguments
def ArgParse():
    global args 		# Declaring globally to acces it from anywhere. 

    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    
    #### Add arguments here

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

    # Initialize the code here

    while True:
        window_title = DEFAULT_TITLE_OF_CANVAS

        # Printing 
        PrintActionStatements()

        # Showing all layers
        ### Show all layers
        key_pressed = cv2.waitKey(0)
        action_str = action[key_pressed]
        
        if action_str is None:                      # Continue if valid key is not pressed
            continue

        elif action_str == "BREAK":                 # Breaking
            break

        ### elif conditions here to check for input


    cv2.destroyAllWindows()
