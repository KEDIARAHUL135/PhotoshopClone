import cv2
import numpy as np

import image
import helping_functions as hf


def AddNewLayer(all_layers):
    print("\nEnter '@' to abort adding of new image.")
        
    while True:
        NewImagePath = input("\nEnter image path: ")

        if '@' in NewImagePath:     # Abort if '@' entered
            print("Aborting adding of image.\n")
            break

        # Reading new image
        NewImage = image.ReadImage(NewImagePath)
        if NewImage is None:        # If image is not found/read
            print("Enter a valid image path...")
            continue

        # Calling function for adding new layer
        all_layers.AddLayer(NewImage)
        print("\nLayer added successfully.")

        break


def AskForLayerNumbers(a, b):
    # range [a, b] denotes the acceptable values of layer numbers 
    print("\nYou can enter '@' to abort this process")
    while True:
        # Asking user layer numbers
        nos = input("Enter layer numbers: ")

        # If - abort
        if '@' in nos:
            return '@'

        # Getting list of numbers passed. Error is thrown if invalid character passed.
        try:
            nos = [int(num) for num in nos.replace(" ", "").split(',')]
            break
        except:
            print("\nInvalid layer number passed. Pass layer numbers again.")
            continue

    # Checking if numbers passed are if valid range.
    for i in nos:
        if i < a or i > b:
            print("\nInvalid layer number passed. Pass layer numbers again.")
            nos = AskForLayerNumbers(a, b)
            break
    
    # If no numbers passed.
    if nos is None:
        print("\nNo numbers passed")
        return None
    if type(nos) == str:
        return '@'
    if len(nos) == 0:
        print("\nNo numbers passed")
        return None
    
    return nos


def ChooseLayersToShow(all_layers, window_title):
    # Checking boundary condition
    if len(all_layers.layers) == 0:             # If no layer is present
        print("\nYou should have atleast 1 layer to show/hide layers.\n")
        return

    print("\nPass the layer numbers (comma(',') separated) you wish to see.")
    print("-1 for all layers and -2 for no layer.\n")
    all_layers.PrintLayerNames()

    # Creating a copy of all_layers to work on
    all_layers_copy = all_layers.Copy()

    IsAborted = False
    while True:
        print("\nPress 'Y' to confirm else press any other key to select different set of layers.")
        all_layers_copy.Show(Title=window_title)
        key = cv2.waitKey(0)
        
        if key == 89 or key == 121:     # 'Y' or 'y' is pressed.
            break
        
        # Asking for layer nos and checking if valid umbers passed
        layer_nos = AskForLayerNumbers(-2, len(all_layers_copy.layers) - 1)
        if type(layer_nos) == str:
            IsAborted = True
            break
        if layer_nos is None:           # layer_nos = None if invalid layer nos entered
            continue

        if layer_nos.count(-1) != 0:     # If -1 entered - Show all layers
            for i in range(len(all_layers_copy.layers)):
                all_layers_copy.layers[i].IsVisible = True

        elif layer_nos.count(-2) != 0:  # If -2 entered - Show no layer
            for i in range(len(all_layers_copy.layers)):
                all_layers_copy.layers[i].IsVisible = False
        
        else:                           # If valid layer numbers passed, show them
            for layer_no in range(len(all_layers_copy.layers)):
                if layer_nos.count(layer_no):
                    all_layers_copy.layers[layer_no].IsVisible = True
                else:
                    all_layers_copy.layers[layer_no].IsVisible = False

    if IsAborted:
        print("Choosing of layers aborted.\n")

    else:
        print("Choosing of layers successful.\n")
        all_layers_copy.Copy(copyTo=all_layers)

    cv2.destroyWindow(window_title)

    return