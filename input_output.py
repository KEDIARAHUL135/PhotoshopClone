import cv2
import numpy as np

import lasso
import image
import marquee
import helping_functions as hf


def AddNewLayer(Canvas):
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
        Canvas.AddLayer(NewImage)
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


def ChooseLayersToShow(Canvas, window_title):
    # Checking boundary condition
    if len(Canvas.layers) == 0:             # If no layer is present
        print("\nYou should have atleast 1 layer to show/hide layers.\n")
        return

    print("\nEnter the layer numbers (comma(',') separated) you wish to see.")
    print("-1 for all layers and -2 for no layer.\n")
    Canvas.PrintLayerNames()

    # Creating a copy of Canvas to work on
    Canvas_copy = Canvas.Copy()

    IsAborted = False
    while True:
        Canvas_copy.Show(Title=window_title)
        key = cv2.waitKey(1)

        command = input("\nEnter 'Y/N' to confirm/abort arrangement else enter any other key to select different set of layers: ")
        
        if 'Y' in command or 'y' in command:        # 'Y' or 'y' is pressed. - confirm
            break
        elif 'N' in command or 'n' in command:      # 'N' or 'n' is pressed. - abort
            IsAborted = True
            break
        
        # Asking for layer nos and checking if valid umbers passed
        layer_nos = AskForLayerNumbers(-2, len(Canvas_copy.layers) - 1)
        if layer_nos is None:           # layer_nos = None if invalid layer nos entered
            continue

        # Setting layers' visibility as asked
        Canvas_copy.SetLayersVisibility(layer_nos)
        
    if IsAborted:
        print("\nChoosing of layers aborted.\n")

    else:
        print("\nChoosing of layers successful.\n")
        Canvas_copy.Copy(copyTo=Canvas)

    cv2.destroyWindow(window_title)

    hf.Sleep()

    return


def DeleteLayers(Canvas, window_title):
    # Storing initial layers data
    Canvas_copy = Canvas.Copy()

    # Checking if at least 1 layer is present so that it can be deleted.
    if len(Canvas_copy.layers) < 1:
        print("\nNot enough layers to delete. There should be atleast 1 layer.\n")
        return

    print("\nEnter the layer numbers (comma (',') separated) you wish to delete.")

    IsAborted = False
    while True:
        Canvas_copy.PrintLayerNames()
        # Showing layers
        Canvas_copy.Show(Title=window_title)
        cv2.waitKey(1)

        command = input("\nEnter 'Y'/'N' to confirm/abort deletion else enter any other key to continue: ")

        if 'y' in command or 'Y' in command:    # if 'y'/'Y' entered -> Confirm deletion
            break

        elif 'n' in command or 'N' in command:  # If 'n'/'N' entered -> Abort deletion
            IsAborted = True
            break

        # Asking for layer numbers cand checking if valid numbers passed.
        layer_nos = AskForLayerNumbers(0, len(Canvas_copy.layers) - 1)
        if layer_nos is None:                   # layer_nos = None if invalid layer nos entered
            continue

        # Ask again if less than 1 layer numbers entered.
        if len(layer_nos) < 1:
            print("Invalid number of layer numbers entered. Enter atleast 1 numbers.")
            continue

        # Delete layer corresponding to passed layer numbers.
        Canvas_copy.DeleteLayers(layer_nos)

    if IsAborted:
        print("\nDeleting of layers aborted.\n")

    else:
        print("\nDeleting of layers successful.\n")
        Canvas_copy.Copy(copyTo=Canvas)

    cv2.destroyWindow(window_title)



def RearrangeLayers(Canvas, window_title):
    # Copying layer's data.
    Canvas_copy = Canvas.Copy()

    # Checking if at least 1 layer is present so that it can be deleted.
    if len(Canvas_copy.layers) < 2:
        print("\nNot enough layers to rearrange. There should be atleast 2 layer.\n")
        return

    print("\nEnter 2 comma(',') separated numbers of the layer you want to exchange.")

    IsAborted = False
    while True:
        Canvas_copy.PrintLayerNames()
        Canvas_copy.Show(Title=window_title)
        cv2.waitKey(1)

        command = input("\nEnter 'Y'/'N' to confirm/abort rearrangement else enter any other key to continue: ")

        if 'y' in command or 'Y' in command:    # if 'y'/'Y' entered -> Confirm rearrange
            break

        elif 'n' in command or 'N' in command:  # if 'n'/'N' entered -> Abort rearrange
            IsAborted = True
            break

        # Asking for layer numbers cand checking if valid numbers passed.
        layer_nos = AskForLayerNumbers(0, len(Canvas_copy.layers) - 1)
        if layer_nos is None:                   # layer_nos = None if invalid layer nos entered
            continue

        # If more or less than two layer numbers passed, ask again
        # Because 2 layer are exchanged in positions at a time.
        if len(layer_nos) != 2 :
            print("Invalid number of layer numbers entered. Enter exactly 2 numbers.")
            continue

        # Exchange layers.
        Canvas_copy.ExchangeLayers(layer_nos[0], layer_nos[1])

    if IsAborted:
        print("\nRearranging of layers aborted.\n")

    else:
        print("\nRearranging of layers successful.\n")
        Canvas_copy.Copy(copyTo=Canvas)

    cv2.destroyWindow(window_title)


def MergeLayers(Canvas, window_title):
    # Copying layer's data.
    Canvas_copy = Canvas.Copy()

    # Checking if at least 2 layers present.
    if len(Canvas_copy.layers) < 2:
        print("\nNot enough layers to merge. There should be atleast 2 layer.\n")
        return

    print("\nEnter comma(',') separated numbers of the layers you want to merge.")

    IsAborted = False
    while True:
        Canvas_copy.PrintLayerNames()
        Canvas_copy.Show(Title=window_title)
        cv2.waitKey(1)

        layer_nos = input("\nEnter 'Y'/'N' to confirm/abort rearrangement else enter any other key to continue: ")

        if 'y' in layer_nos or 'Y' in layer_nos:    # if 'y'/'Y' entered -> Confirm merge
            break

        elif 'n' in layer_nos or 'N' in layer_nos:  # if 'n'/'N' entered -> Abort merge
            IsAborted = True
            break

        # Asking for layer numbers and checking if valid numbers passed.
        layer_nos = AskForLayerNumbers(0, len(Canvas_copy.layers) - 1)
        if layer_nos is None:                       # layer_nos = None if invalid layer nos entered
            continue

        # Ask again if less than 2 layer numbers passed.
        # Because atleast 2 layers should be there to merge.
        if len(layer_nos) < 2:
            print("Invalid number of layer numbers entered. Enter atleast 2 numbers.")
            continue

        # Merge layers.
        Canvas_copy.MergeLayers(layer_nos)

    if IsAborted:
        print("\nMerging of layers aborted.\n")

    else:
        print("\nMerging of layers successful.\n")
        Canvas_copy.Copy(copyTo=Canvas)

    cv2.destroyWindow(window_title)


def RenameLayers(Canvas):
    # Copying layer's data.
    Canvas_copy = Canvas.Copy()

    # Checking if at least 1 layer is present so that it can be renamed.
    if len(Canvas_copy.layers) < 1:
        print("\nNot enough layers to rename. There should be atleast 1 layer.\n")
        return
    
    print("\nEnter the layer number you wish to rename.")

    IsAborted = False
    while True:
        Canvas_copy.PrintLayerNames()

        command = input("\nEnter 'Y'/'N' to confirm/abort renaming else enter any other key to continue: ")

        if 'y' in command or 'Y' in command:    # If 'y'/'Y' entered -> confirm rename
            break

        elif 'n' in command or 'N' in command:  # if 'n'/'N' entered -> Abort rename
            IsAborted = True
            break

        # Ask for layer number to rename, if invalid layer number passed, ask again
        layer_no = AskForLayerNumbers(0, len(Canvas_copy.layers) - 1)
        if layer_no is None:                    # layer_nos = None if invalid layer nos entered
            continue

        # If more or less than 1 layer number entered, ask again.
        if len(layer_no) != 1:
            print("Invalid number of layer number entered. Enter exactly 1 number.")
            continue

        # Asking for new name
        rename_to = input("Enter the new name: ")
        # Renaming layer
        Canvas_copy.RenameLayer(layer_no[0], rename_to)

    if IsAborted:
        print("\nRenaming of layers aborted.\n")

    else:
        print("\nRenaming of layers successful.\n")
        Canvas_copy.Copy(copyTo=Canvas)



def DuplicateLayers(Canvas):
    # Copying layer's data.
    Canvas_copy = Canvas.Copy()

    # Checking if at least 1 layer is present so that it can be renamed.
    if len(Canvas_copy.layers) < 1:
        print("\nNot enough layers to duplicate. There should be atleast 1 layer.\n")
        return
    
    print("\nEnter the layer number you wish to duplicate.")

    IsAborted = False
    while True:
        Canvas_copy.PrintLayerNames()

        command = input("\nEnter 'Y'/'N' to confirm/abort duplicating else enter any other key to continue: ")

        if 'y' in command or 'Y' in command:    # If 'y'/'Y' entered -> confirm rename
            break

        elif 'n' in command or 'N' in command:  # if 'n'/'N' entered -> Abort rename
            IsAborted = True
            break

        # Ask for layer number to rename, if invalid layer number passed, ask again
        layer_no = AskForLayerNumbers(0, len(Canvas_copy.layers) - 1)
        if layer_no is None:                    # layer_nos = None if invalid layer nos entered
            continue

        # If more or less than 1 layer number entered, ask again.
        if len(layer_no) != 1:
            print("Invalid number of layer number entered. Enter exactly 1 number.")
            continue

        # Duplicating layer
        Canvas_copy.DuplicateLayer(layer_no[0])

    if IsAborted:
        print("\nDuplicating of layers aborted.\n")

    else:
        print("\nDuplicating of layers successful.\n")
        Canvas_copy.Copy(copyTo=Canvas)


def LayerOperations(Canvas, window_title):
    while True:
        print()
        print("Enter 'R' to rearrange layers.")
        print("Enter 'D' to delete layers.")
        print("Enter 'M' to merge layers.")
        print("Enter 'E' to rename layers.")
        print("Enter 'C' to duplicate layers.")

        command = input("\nEnter command: ")
        command = command.replace(" ", "")

        if len(command) > 1:                        # If more than 1 command entered.
            print("Too many commands entered. Enter only one command.\n")
            continue

        elif 'r' in command or 'R' in command:      # 'r'/'R' entered -> Rearrange layers
            RearrangeLayers(Canvas, window_title)
            break

        elif 'd' in command or 'D' in command:      # 'd'/'D' entered -> Delete layers
            DeleteLayers(Canvas, window_title)
            break

        elif 'm' in command or 'M' in command:      # 'm'/'M' entered -> Merge layers
            MergeLayers(Canvas, window_title)
            break
        
        elif 'e' in command or 'E' in command:      # 'e'/'E' entered -> Rename layers
            RenameLayers(Canvas)
            break

        elif 'c' in command or 'C' in command:      # 'c'/'C' entered -> Duplicate layer
            DuplicateLayers(Canvas)
            break

        else:                                       # If invalid command is passed.
            print("Invalid command passed. Enter command again.\n")
            continue
        
    cv2.destroyWindow(window_title)
    hf.Sleep()

    return



def MarqueeTool(Canvas, window_title):
    while True:
        print()
        print("Enter 'R' for Rectangular Marquee Tool.")
        print("Enter 'E' for Elliptical Marquee Tool.")
        print("Enter 'W' for Single Row Marquee Tool.")
        print("Enter 'C' for Single Column Marquee Tool.")

        command = input("\nEnter command: ")
        command = command.replace(" ", "")

        if len(command) > 1:                        # If more than 1 command entered.
            print("Too many commands entered. Enter only one command.\n")
            continue

        elif 'r' in command or 'R' in command:      # 'r'/'R' entered -> Rectangular Marquee Tool
            marquee.RectangularMarqueeTool(Canvas, window_title)
            break

        elif 'e' in command or 'E' in command:      # 'e'/'E' entered -> Elliptical Marquee Tool
            marquee.EllipticalMarqueeTool(Canvas, window_title)
            break

        elif 'w' in command or 'W' in command:      # 'w'/'W' entered -> Single Row Marquee Tool
            marquee.SingleRowMarqueeTool(Canvas, window_title)
            break
        
        elif 'c' in command or 'C' in command:      # 'c'/'C' entered -> Single Column Marquee Tool
            marquee.SingleColMarqueeTool(Canvas, window_title)
            break

        else:                                       # If invalid command is passed.
            print("Invalid command passed. Enter command again.\n")
            continue
        
    hf.Sleep()

    return


def LassoTool(Canvas, window_title):
    while True:
        print()
        print("Enter 'L' for Lasso Tool.")
        print("Enter 'P' for Polygon Lasso Tool.")
        print("Enter 'M' for Magnetic Lasso Tool.")

        command = input("\nEnter command: ")
        command = command.replace(" ", "")

        if len(command) > 1:                        # If more than 1 command entered.
            print("Too many commands entered. Enter only one command.\n")
            continue

        elif 'l' in command or 'L' in command:      # 'l'/'L' entered -> Lasso Tool
            lasso.LassoTool(Canvas, window_title)
            break

        elif 'p' in command or 'P' in command:      # 'p'/'P' entered -> Polygon Lasso Tool
            lasso.PolygonLassoTool(Canvas, window_title)
            break

        elif 'm' in command or 'M' in command:      # 'm'/'M' entered -> Magnetic Lasso Tool
            lasso.MagneticLassoTool(Canvas, window_title)
            break
        
        else:                                       # If invalid command is passed.
            print("Invalid command passed. Enter command again.\n")
            continue
        
    hf.Sleep()

    return
