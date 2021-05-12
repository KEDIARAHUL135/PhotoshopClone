import cv2
import numpy as np

import helping_functions as hf
from marquee import AskLayerNumsToCopy, CropVisible, ExtractSelectedRegion



########################################################### Lasso Tool ################################################################################

def CallBackFunc_LassoTool(event, x, y, flags, params):
    # Taking global params
    global selecting, isSelected, CombinedFrame, FrameToShow, CanvasShape, SelectedContour

    # If while selecting the region, mouse goes out of the frame, then clip it position 
    # to the nearest corner/edge of the frame
    if selecting:
        x, y = hf.Correct_xy_While_Selecting(x, y, [0, CanvasShape[1]-1], [0, CanvasShape[0]-1])
    
    
    # Starts selecting - Left button is pressed down
    if event == cv2.EVENT_LBUTTONDOWN:
        selecting = True
        isSelected = False
        SelectedContour = []
        SelectedContour.append([[x, y]])

    # Selecting the region
    elif event == cv2.EVENT_MOUSEMOVE:
        if selecting:
            SelectedContour.append([[x, y]])
            FrameToShow = CombinedFrame.copy()
            cv2.drawContours(FrameToShow, [np.array(SelectedContour)], -1, (127, 127, 127), 1)

    # Stop selecting the layer.
    elif event == cv2.EVENT_LBUTTONUP:
        FrameToShow = CombinedFrame.copy()
        cv2.drawContours(FrameToShow, [np.array(SelectedContour)], -1, (127, 127, 127), 1)
        selecting = False
        if len(SelectedContour) > 2:
            isSelected = True


def LassoTool(Canvas, window_title):
    hf.Clear()
    # Taking layer numbers user wants to copy
    Canvas.PrintLayerNames()
    layer_nos_to_copy = AskLayerNumsToCopy(-1, len(Canvas.layers) - 1)

    print("\nPress 'Y' to confirm selection and copy it in a new layer else press 'N' to abort.")
    print("You can also used the keys 'W', 'A', 'S', and 'D', to move the")
    print("selected region Up, Left, Down, and Right respectively.")

    # Clearing mouse buffer data (old mouse data) - this is a bug in OpenCV probably
    cv2.namedWindow(window_title)
    cv2.setMouseCallback(window_title, hf.EmptyCallBackFunc)
    Canvas.Show(Title=window_title)
    cv2.waitKey(1)

    # Setting mouse callback
    cv2.setMouseCallback(window_title, CallBackFunc_LassoTool)

    # Setting some params used in callback function
    global selecting, isSelected, CombinedFrame, FrameToShow, CanvasShape, SelectedContour
    selecting = False       # True if region is being selected      
    isSelected = False      # True if region is selected
    Canvas.CombineLayers()
    CombinedFrame = Canvas.CombinedImage.copy()     # the combined frame of the canvas
    FrameToShow = CombinedFrame.copy()              # The frame which will be shown (with the selected region)
    CanvasShape = Canvas.Shape                      # Shape of the canvas
    SelectedContour = []                            # Contour of the selected region


    IsAborted = False
    while True:
        # Showing canvas
        cv2.imshow(window_title, FrameToShow)
        Key = cv2.waitKey(1)

        if Key == 89 or Key == 121:         # If 'Y'/'y' - confirm
            if isSelected:                  # If the region is selected
                break
            else:                           # If the region is not selected yet
                print("Select a region first to confirm.")
                continue
        elif Key == 78 or Key == 110:       # If 'N'/'n' - abort
            IsAborted = True
            break
        
        # If the region is selected, check if the user is trying to move it
        if isSelected:
            if Key == 87 or Key == 119:     # If 'W'/'w' - move up
                SelectedContour = hf.ShiftContour(SelectedContour, ToOrigin=False, ShiftBy=[0, -1])
            if Key == 65 or Key == 97:      # If 'A'/'a' - move left
                SelectedContour = hf.ShiftContour(SelectedContour, ToOrigin=False, ShiftBy=[-1, 0])
            if Key == 83 or Key == 115:     # If 'S'/'s' - move down
                SelectedContour = hf.ShiftContour(SelectedContour, ToOrigin=False, ShiftBy=[0, 1])
            if Key == 68 or Key == 100:     # If 'D'/'d' - move right
                SelectedContour = hf.ShiftContour(SelectedContour, ToOrigin=False, ShiftBy=[1, 0])
            
            FrameToShow = CombinedFrame.copy()
            cv2.drawContours(FrameToShow, [np.array(SelectedContour)], -1, (127, 127, 127), 1)
            

    if not IsAborted:
        # Finding Selected regions bounding box, its contour shifted to origin, and its shifted mask image
        # Selected_BB = list(cv2.boundingRect(np.array(SelectedContour)))
        SelectedContourToOrigin, Selected_Mask, Selected_BB = hf.ShiftContour(SelectedContour, Get_Mask_BB=True)

        # Redrawing mask to conver any uncovered area
        OuterContour, _ = cv2.findContours(Selected_Mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        cv2.drawContours(Selected_Mask, OuterContour, -1, 255, -1)

        # Extracting the selected regions and copying them in a new layer
        ExtractSelectedRegion(Canvas, Selected_BB, Selected_Mask, layer_nos_to_copy)
    
    else:
        print("\nRegion selection aborted.")


#######################################################################################################################################################


########################################################### Polygon Lasso Tool ########################################################################

def CallBackFunc_PolyLassoTool(event, x, y, flags, params):
    # Taking global params
    global selecting, isSelected, CombinedFrame, FrameToShow, CanvasShape, SelectedContour

    # If while selecting the region, mouse goes out of the frame, then clip it position 
    # to the nearest corner/edge of the frame
    if selecting:
        x, y = hf.Correct_xy_While_Selecting(x, y, [0, CanvasShape[1]-1], [0, CanvasShape[0]-1])
    
    
    # Starts selecting - Left button is pressed down
    if event == cv2.EVENT_FLAG_LBUTTON:
        if isSelected:
            isSelected = False
            selecting = True
            SelectedContour = []
            SelectedContour.append([[x, y]])
        else:
            if not selecting:
                selecting = True
                SelectedContour = []
                SelectedContour.append([[x, y]])
            else:
                SelectedContour.append([[x, y]])


    # Selecting the region
    elif event == cv2.EVENT_MOUSEMOVE:
        if selecting:
            FrameToShow = CombinedFrame.copy()
            ContourCopy = SelectedContour.copy()
            ContourCopy.append([[x, y]])
            cv2.drawContours(FrameToShow, [np.array(ContourCopy)], -1, (127, 127, 127), 1)

    # Stop selecting the layer.
    elif event == cv2.EVENT_LBUTTONDBLCLK:
        isSelected = True
        selecting = False
        if len(SelectedContour) <= 2:
            SelectedContour = []
            isSelected = False
        SelectedContour.append([[x, y]])
        FrameToShow = CombinedFrame.copy()
        cv2.drawContours(FrameToShow, [np.array(SelectedContour)], -1, (127, 127, 127), 1)


def PolygonLassoTool(Canvas, window_title):
    hf.Clear()
    # Taking layer numbers user wants to copy
    Canvas.PrintLayerNames()
    layer_nos_to_copy = AskLayerNumsToCopy(-1, len(Canvas.layers) - 1)

    print("\nPress 'Y' to confirm selection and copy it in a new layer else press 'N' to abort.")
    print("You can also used the keys 'W', 'A', 'S', and 'D', to move the")
    print("selected region Up, Left, Down, and Right respectively.")

    # Clearing mouse buffer data (old mouse data) - this is a bug in OpenCV probably
    cv2.namedWindow(window_title)
    cv2.setMouseCallback(window_title, hf.EmptyCallBackFunc)
    Canvas.Show(Title=window_title)
    cv2.waitKey(1)

    # Setting mouse callback
    cv2.setMouseCallback(window_title, CallBackFunc_PolyLassoTool)

    # Setting some params used in callback function
    global selecting, isSelected, CombinedFrame, FrameToShow, CanvasShape, SelectedContour
    selecting = False       # True if region is being selected      
    isSelected = False      # True if region is selected
    Canvas.CombineLayers()
    CombinedFrame = Canvas.CombinedImage.copy()     # the combined frame of the canvas
    FrameToShow = CombinedFrame.copy()              # The frame which will be shown (with the selected region)
    CanvasShape = Canvas.Shape                      # Shape of the canvas
    SelectedContour = []                            # Contour of the selected region


    IsAborted = False
    while True:
        # Showing canvas
        cv2.imshow(window_title, FrameToShow)
        Key = cv2.waitKey(1)

        if Key == 89 or Key == 121:         # If 'Y'/'y' - confirm
            if isSelected:                  # If the region is selected
                break
            else:                           # If the region is not selected yet
                print("Select a region first to confirm.")
                continue
        elif Key == 78 or Key == 110:       # If 'N'/'n' - abort
            IsAborted = True
            break
        
        # If the region is selected, check if the user is trying to move it
        if isSelected:
            if Key == 87 or Key == 119:     # If 'W'/'w' - move up
                SelectedContour = hf.ShiftContour(SelectedContour, ToOrigin=False, ShiftBy=[0, -1])
            if Key == 65 or Key == 97:      # If 'A'/'a' - move left
                SelectedContour = hf.ShiftContour(SelectedContour, ToOrigin=False, ShiftBy=[-1, 0])
            if Key == 83 or Key == 115:     # If 'S'/'s' - move down
                SelectedContour = hf.ShiftContour(SelectedContour, ToOrigin=False, ShiftBy=[0, 1])
            if Key == 68 or Key == 100:     # If 'D'/'d' - move right
                SelectedContour = hf.ShiftContour(SelectedContour, ToOrigin=False, ShiftBy=[1, 0])
            
            FrameToShow = CombinedFrame.copy()
            cv2.drawContours(FrameToShow, [np.array(SelectedContour)], -1, (127, 127, 127), 1)
            

    if not IsAborted:
        # Finding Selected regions bounding box, its contour shifted to origin, and its shifted mask image
        # Selected_BB = list(cv2.boundingRect(np.array(SelectedContour)))
        SelectedContourToOrigin, Selected_Mask, Selected_BB = hf.ShiftContour(SelectedContour, Get_Mask_BB=True)

        # Redrawing mask to conver any uncovered area
        OuterContour, _ = cv2.findContours(Selected_Mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        cv2.drawContours(Selected_Mask, OuterContour, -1, 255, -1)

        # Extracting the selected regions and copying them in a new layer
        ExtractSelectedRegion(Canvas, Selected_BB, Selected_Mask, layer_nos_to_copy)
    
    else:
        print("\nRegion selection aborted.")


#######################################################################################################################################################