import cv2
import numpy as np

import helping_functions as hf


def CallBackFunc_MoveTool(event, x, y, flags, Canvas):
    # Taking global params
    global moving, movingLayer, im_x, im_y, ii_x, ii_y

    # Starts moving - Left button is pressed down
    if event == cv2.EVENT_LBUTTONDOWN:
        im_x, im_y = x, y               # Setting initial mouse coordinates
        
        # Finding the moving layer's index
        movingLayer = -1                # Dummy value
        for i in range(len(Canvas.layers) - 1, -1, -1):     # Moving from top to bottom layer
            # Layer x, y, and height and width
            lx, ly = Canvas.layers[i].Position
            lh, lw = Canvas.layers[i].Shape

            if lx <= x < lx + lw and ly <= y < ly + lh:
                movingLayer = i
                ii_x, ii_y = lx, ly
                break

        # Checking if any layer is selected and changing "moving" flag accrodingly.
        if movingLayer == -1:           # Background layer
            moving = False
        else:                           # Start moving selected layer
            moving = True

    # Moving the layer while pressing down the mouse left button
    elif event == cv2.EVENT_MOUSEMOVE:
        if moving:      # If a layer is selected and we are moving it
            # Changing the image position coordinates according to the difference
            # between the initial and the final position of the mouse pointer.
            Canvas.layers[movingLayer].Position = [ii_x + x - im_x, ii_y + y - im_y]

    # Stop moving the layer.
    elif event == cv2.EVENT_LBUTTONUP:
        moving = False


def MoveTool(Canvas, window_title):
    print("\nPress 'Y' to confirm and exit move tool else keep editing.\n")

    # Clearing mouse buffer data (old mouse data) - this is a bug in OpenCV probably
    cv2.namedWindow(window_title)
    cv2.setMouseCallback(window_title, hf.EmptyCallBackFunc)
    Canvas.Show(Title=window_title)
    cv2.waitKey(1)

    # Setting mouse callback
    cv2.setMouseCallback(window_title, CallBackFunc_MoveTool, Canvas)

    # Setting some params used in callback function
    global moving, movingLayer, im_x, im_y, ii_x, ii_y
    moving = False      # True when image is selected and being moved
    # movingLayer : Index of the layer being moved
    # im_x, im_y : Coordinates of the point where mouse left button is pressed 
    # ii_x, ii_y : Coordinates of the initial position of the image being moved
    

    while True:
        # Showing canvas
        Canvas.Show(Title=window_title)
        Key = cv2.waitKey(1)

        if Key == 89 or Key == 121:     # If 'Y'/'y' pressed
            break

    cv2.destroyWindow(window_title)