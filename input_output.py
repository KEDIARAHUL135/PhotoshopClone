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
    while True:
        # Asking user layer numbers
        nos = input("Enter layer numbers: ")

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
    elif len(nos) == 0:
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
        all_layers_copy.Show(Title=window_title)
        key = cv2.waitKey(1)

        command = input("\nEnter 'Y/N' to confirm/abort arrangement else enter any other key to select different set of layers: ")
        
        if 'Y' in command or 'y' in command:        # 'Y' or 'y' is pressed. - confirm
            break
        elif 'N' in command or 'n' in command:      # 'Y' or 'y' is pressed. - confirm
            IsAborted = True
            break
        
        # Asking for layer nos and checking if valid umbers passed
        layer_nos = AskForLayerNumbers(-2, len(all_layers_copy.layers) - 1)
        if layer_nos is None:           # layer_nos = None if invalid layer nos entered
            continue

        # Setting layers' visibility as asked
        all_layers_copy.SetLayersVisibility(layer_nos)
        
    if IsAborted:
        print("\nChoosing of layers aborted.\n")

    else:
        print("\nChoosing of layers successful.\n")
        all_layers_copy.Copy(copyTo=all_layers)

    cv2.destroyWindow(window_title)

    hf.Sleep()

    return