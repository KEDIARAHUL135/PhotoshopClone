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

    hf.Sleep()


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

    print("\nEnter the layer numbers (comma(',') separated) you wish to see.")
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


def DeleteLayers(all_layers, window_title):
    # Storing initial layers data
    all_layers_copy = all_layers.Copy()

    # Checking if at least 1 layer is present so that it can be deleted.
    if len(all_layers_copy.layers) < 1:
        print("\nNot enough layers to delete. There should be atleast 1 layer.\n")
        return

    print("\nEnter the layer numbers (comma (',') separated) you wish to delete.")

    IsAborted = False
    while True:
        all_layers_copy.PrintLayerNames()
        # Showing layers
        all_layers_copy.Show(Title=window_title)
        cv2.waitKey(1)

        command = input("\nEnter 'Y'/'N' to confirm/abort deletion else enter any other key to continue: ")

        if 'y' in command or 'Y' in command:    # if 'y'/'Y' entered -> Confirm deletion
            break

        elif 'n' in command or 'N' in command:  # If 'n'/'N' entered -> Abort deletion
            IsAborted = True
            break

        # Asking for layer numbers cand checking if valid numbers passed.
        layer_nos = AskForLayerNumbers(0, len(all_layers_copy.layers) - 1)
        if layer_nos is None:                   # layer_nos = None if invalid layer nos entered
            continue

        # Ask again if less than 1 layer numbers entered.
        if len(layer_nos) < 1:
            print("Invalid number of layer numbers entered. Enter atleast 1 numbers.")
            continue

        # Delete layer corresponding to passed layer numbers.
        all_layers_copy.DeleteLayers(layer_nos)

    if IsAborted:
        print("\nDeleting of layers aborted.\n")

    else:
        print("\nDeleting of layers successful.\n")
        all_layers_copy.Copy(copyTo=all_layers)

    cv2.destroyWindow(window_title)



def RearrangeLayers(all_layers, window_title):
    # Copying layer's data.
    all_layers_copy = all_layers.Copy()

    # Checking if at least 1 layer is present so that it can be deleted.
    if len(all_layers_copy.layers) < 2:
        print("\nNot enough layers to rearrange. There should be atleast 2 layer.\n")
        return

    print("\nEnter 2 comma(',') separated numbers of the layer you want to exchange.")

    IsAborted = False
    while True:
        all_layers_copy.PrintLayerNames()
        all_layers_copy.Show(Title=window_title)
        cv2.waitKey(1)

        command = input("\nEnter 'Y'/'N' to confirm/abort rearrangement else enter any other key to continue: ")

        if 'y' in command or 'Y' in command:    # if 'y'/'Y' entered -> Confirm rearrange
            break

        elif 'n' in command or 'N' in command:  # if 'n'/'N' entered -> Abort rearrange
            IsAborted = True
            break

        # Asking for layer numbers cand checking if valid numbers passed.
        layer_nos = AskForLayerNumbers(0, len(all_layers_copy.layers) - 1)
        if layer_nos is None:                   # layer_nos = None if invalid layer nos entered
            continue

        # If more or less than two layer numbers passed, ask again
        # Because 2 layer are exchanged in positions at a time.
        if len(layer_nos) != 2 :
            print("Invalid number of layer numbers entered. Enter exactly 2 numbers.")
            continue

        # Exchange layers.
        all_layers_copy.ExchangeLayers(layer_nos[0], layer_nos[1])

    if IsAborted:
        print("\nRearranging of layers aborted.\n")

    else:
        print("\nRearranging of layers successful.\n")
        all_layers_copy.Copy(copyTo=all_layers)

    cv2.destroyWindow(window_title)


def MergeLayers(all_layers, window_title):
    # Copying layer's data.
    all_layers_copy = all_layers.Copy()

    # Checking if at least 2 layers present.
    if len(all_layers_copy.layers) < 2:
        print("\nNot enough layers to merge. There should be atleast 2 layer.\n")
        return

    print("\nEnter 2 comma(',') separated numbers of the layer you want to merge.")

    IsAborted = False
    while True:
        all_layers_copy.PrintLayerNames()
        all_layers_copy.Show(Title=window_title)
        cv2.waitKey(1)

        layer_nos = input("\nEnter 'Y'/'N' to confirm/abort rearrangement else enter any other key to continue: ")

        if 'y' in layer_nos or 'Y' in layer_nos:    # if 'y'/'Y' entered -> Confirm merge
            break

        elif 'n' in layer_nos or 'N' in layer_nos:  # if 'n'/'N' entered -> Abort merge
            IsAborted = True
            break

        # Asking for layer numbers and checking if valid numbers passed.
        layer_nos = AskForLayerNumbers(0, len(all_layers_copy.layers) - 1)
        if layer_nos is None:                       # layer_nos = None if invalid layer nos entered
            continue

        # Ask again if less than 2 layer numbers passed.
        # Because atleast 2 layers should be there to merge.
        if len(layer_nos) < 2:
            print("Invalid number of layer numbers entered. Enter atleast 2 numbers.")
            continue

        # Merge layers.
        all_layers_copy.MergeLayers(layer_nos)

    if IsAborted:
        print("\nMerging of layers aborted.\n")

    else:
        print("\nMerging of layers successful.\n")
        all_layers_copy.Copy(copyTo=all_layers)

    cv2.destroyWindow(window_title)


def RenameLayers(all_layers):
    # Copying layer's data.
    all_layers_copy = all_layers.Copy()

    # Checking if at least 1 layer is present so that it can be renamed.
    if len(all_layers_copy.layers) < 1:
        print("\nNot enough layers to rename. There should be atleast 1 layer.\n")
        return
    
    print("\nEnter the layer number you wish to rename.")

    IsAborted = False
    while True:
        all_layers_copy.PrintLayerNames()

        command = input("\nEnter 'Y'/'N' to confirm/abort renaming else enter any other key to continue: ")

        if 'y' in command or 'Y' in command:    # If 'y'/'Y' entered -> confirm rename
            break

        elif 'n' in command or 'N' in command:  # if 'n'/'N' entered -> Abort rename
            IsAborted = True
            break

        # Ask for layer number to rename, if invalid layer number passed, ask again
        layer_no = AskForLayerNumbers(0, len(all_layers_copy.layers) - 1)
        if layer_no is None:                    # layer_nos = None if invalid layer nos entered
            continue

        # If more or less than 1 layer number entered, ask again.
        if len(layer_no) != 1:
            print("Invalid number of layer number entered. Enter exactly 1 number.")
            continue

        # Asking for new name
        rename_to = input("Enter the new name: ")
        # Renaming layer
        all_layers_copy.RenameLayer(layer_no[0], rename_to)

    if IsAborted:
        print("\nRenaming of layers aborted.\n")

    else:
        print("\nRenaming of layers successful.\n")
        all_layers_copy.Copy(copyTo=all_layers)


def LayerProcesses(all_layers, window_title):
    while True:
        print()
        print("Enter 'R' to rearrange layers.")
        print("Enter 'D' to delete layers.")
        print("Enter 'M' to merge layers.")
        print("Enter 'E' to rename layers.")

        command = input("\nEnter command: ")
        command = command.replace(" ", "")

        if len(command) > 1:                        # If more than 1 command entered.
            print("Too many commands entered. Enter only one command.\n")
            continue

        elif 'r' in command or 'R' in command:      # 'r'/'R' entered -> Rearrange layers
            RearrangeLayers(all_layers, window_title)
            break

        elif 'd' in command or 'D' in command:      # 'd'/'D' entered -> Delete layers
            DeleteLayers(all_layers, window_title)
            break

        elif 'm' in command or 'M' in command:      # 'm'/'M' entered -> Merge layers
            MergeLayers(all_layers, window_title)
            break
        
        elif 'e' in command or 'E' in command:      # 'e'/'E' entered -> Rename layers
            RenameLayers(all_layers)
            break

        else:                                       # If invalid command is passed.
            print("Invalid command passed. Enter command again.\n")
            continue
        
    cv2.destroyWindow(window_title)
    hf.Sleep()

    return
