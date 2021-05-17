from typing import Final
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


########################################################### Magnetic Lasso Tool #######################################################################


def Dij_SetROI():
    global CombinedFrame, CanvasShape, dij_src_F, dij_end_F, RunningPoints_F, FinalPoints_F, Weights
    global ROI_Frame, ROI_Shape, dij_src_roi, dij_end_roi, ROI_Rect, ROI_Weights

    # Getting ROI's bounding rect
    ExtraROIBoundary = 60
    ROI_w = abs(dij_src_F[0] - dij_end_F[0]) + (ExtraROIBoundary * 2)
    ROI_h = abs(dij_src_F[1] - dij_end_F[1]) + (ExtraROIBoundary * 2)
    ROI_x = min(dij_src_F[0], dij_end_F[0]) - ExtraROIBoundary
    ROI_y = min(dij_src_F[1], dij_end_F[1]) - ExtraROIBoundary
    [ROI_x, ROI_y, ROI_w, ROI_h] = hf.Intersection([0, 0, CanvasShape[1], CanvasShape[0]], [ROI_x, ROI_y, ROI_w, ROI_h])

    # Setting global variables
    ROI_Rect = [ROI_x, ROI_y, ROI_w, ROI_h]
    ROI_Shape = [ROI_h, ROI_w]
    ROI_Frame = CombinedFrame[ROI_y : ROI_y + ROI_h, ROI_x : ROI_x + ROI_w]
    dij_src_roi = [dij_src_F[0] - ROI_x, dij_src_F[1] - ROI_y]
    dij_end_roi = [dij_end_F[0] - ROI_x, dij_end_F[1] - ROI_y]
    ROI_Weights = np.asarray(Weights)[ : , ROI_y : ROI_y + ROI_h, ROI_x : ROI_x + ROI_w]



def Dij_SetWeights():
    global Weights, CombinedFrame
    Weights = [None] * 9

    # Storing the weights of each neighbours in list of length 9
    # [0 1 2]
    # [3 4 5]
    # [6 7 8]
    Kernels = [None] * 9

    Kernels[0] = np.array([[    0,   0.7,     0],
                           [ -0.7,     0,     0],
                           [    0,     0,     0]], dtype=np.float32)
    Kernels[1] = np.array([[-0.25,     0,  0.25],
                           [-0.25,     0,  0.25],
                           [    0,     0,     0]], dtype=np.float32)
    Kernels[2] = np.array([[    0,   0.7,     0],
                           [    0,     0,  -0.7],
                           [    0,     0,     0]], dtype=np.float32)
    Kernels[3] = np.array([[ 0.25,  0.25,     0],
                           [    0,     0,     0],
                           [-0.25, -0.25,     0]], dtype=np.float32)
    Kernels[4] = np.array([[    0,     0,     0],
                           [    0, 10**6,     0],
                           [    0,     0,     0]], dtype=np.float32)
    Kernels[5] = np.array([[    0, -0.25, -0.25],
                           [    0,     0,     0],
                           [    0,  0.25,  0.25]], dtype=np.float32)
    Kernels[6] = np.array([[    0,     0,     0],
                           [ -0.7,     0,     0],
                           [    0,   0.7,     0]], dtype=np.float32)
    Kernels[7] = np.array([[    0,     0,     0],
                           [ 0.25,     0, -0.25],
                           [ 0.25,     0, -0.25]], dtype=np.float32)
    Kernels[8] = np.array([[    0,     0,     0],
                           [    0,     0,   0.7],
                           [    0,  -0.7,     0]], dtype=np.float32)

    
    # Finding weights
    for i in range(9):
        # Applying convolution
        # Temp will be 3 channeled image
        Temp = cv2.filter2D(CombinedFrame, -1, Kernels[i])

        # Merging the channels to get weights as: B^2 + G^2 + R^2 + 0.01
        # This will ensure that weights are positive and non zero (For Dijsktra's algo)
        # Compliment of B, G, R will be taken to support larger differences
        B, G, R = cv2.split(Temp)
        B = 255 - B
        G = 255 - G
        R = 255 - R
        Weights[i] = B*B + G*G + R*R + 0.01



def FindMinDistPt(Distances, Queue):
    global ROI_Shape

    minDist = float("Inf")          # Minimum distance point found
    minDistPt = [-1, -1, -1]   # Index of minimum distance point : [x, y, rowMajor]

    for row in range(ROI_Shape[0]):
        for col in range(ROI_Shape[1]):
            if Distances[row][col] < minDist:
                rm = hf.ToRowMajor(col, row, ROI_Shape[1])
                if rm in Queue:
                    minDist = Distances[row][col]
                    minDistPt = [col, row, rm]

    return minDistPt


def UpdateDist_nd_Parent(Pt, Distances, Parent, Queue):
    global ROI_Weights, ROI_Shape, ROI_Rect

    x, y, rm = Pt

    # Top - Left
    if x > 0 and y > 0 and hf.ToRowMajor(x-1, y-1, ROI_Shape[1]) in Queue:
        if Distances[y][x] + ROI_Weights[0][y-1][x-1] < Distances[y-1][x-1]:
            Distances[y-1][x-1] = Distances[y][x] + ROI_Weights[0][y-1][x-1]
            Parent[y-1][x-1] = [x, y]
    
    # Top
    if y > 0 and hf.ToRowMajor(x, y-1, ROI_Shape[1]) in Queue:
        if Distances[y][x] + ROI_Weights[1][y-1][x] < Distances[y-1][x]:
            Distances[y-1][x] = Distances[y][x] + ROI_Weights[0][y-1][x]
            Parent[y-1][x] = [x, y]

    # Top - Right
    if x < (ROI_Shape[1] - 1) and y > 0 and hf.ToRowMajor(x+1, y-1, ROI_Shape[1]) in Queue:
        if Distances[y][x] + ROI_Weights[2][y-1][x+1] < Distances[y-1][x+1]:
            Distances[y-1][x+1] = Distances[y][x] + ROI_Weights[0][y-1][x+1]
            Parent[y-1][x+1] = [x, y]
    
    # Left
    if x > 0 and hf.ToRowMajor(x-1, y, ROI_Shape[1]) in Queue:
        if Distances[y][x] + ROI_Weights[3][y][x-1] < Distances[y][x-1]:
            Distances[y][x-1] = Distances[y][x] + ROI_Weights[0][y][x-1]
            Parent[y][x-1] = [x, y]
    
    # Middle
    #### No need to consider middle one

    # Right
    if x < (ROI_Shape[1] - 1) and hf.ToRowMajor(x+1, y, ROI_Shape[1]) in Queue:
        if Distances[y][x] + ROI_Weights[5][y][x+1] < Distances[y][x+1]:
            Distances[y][x+1] = Distances[y][x] + ROI_Weights[0][y][x+1]
            Parent[y][x+1] = [x, y]
    
    # Bottom - Left
    if x > 0 and y < (ROI_Shape[0] - 1) and hf.ToRowMajor(x-1, y+1, ROI_Shape[1]) in Queue:
        if Distances[y][x] + ROI_Weights[6][y+1][x-1] < Distances[y+1][x-1]:
            Distances[y+1][x-1] = Distances[y][x] + ROI_Weights[0][y+1][x-1]
            Parent[y+1][x-1] = [x, y]
    
    # Bottom
    if y < (ROI_Shape[0] - 1) and hf.ToRowMajor(x, y+1, ROI_Shape[1]) in Queue:
        if Distances[y][x] + ROI_Weights[7][y+1][x] < Distances[y+1][x]:
            Distances[y+1][x] = Distances[y][x] + ROI_Weights[0][y+1][x]
            Parent[y+1][x] = [x, y]

    # Bottom - Right
    if x < (ROI_Shape[1] - 1) and y < (ROI_Shape[0] - 1) and hf.ToRowMajor(x+1, y+1, ROI_Shape[1]) in Queue:
        if Distances[y][x] + ROI_Weights[8][y+1][x+1] < Distances[y+1][x+1]:
            Distances[y+1][x+1] = Distances[y][x] + ROI_Weights[0][y+1][x+1]
            Parent[y+1][x+1] = [x, y]
    
    return Distances, Parent


def ExtractParentPath(dij_end_roi, Parent):
    # Shortest path
    Path = []

    currentPt = [dij_end_roi[0], dij_end_roi[1]]
    while currentPt[0] != -1:
        # Adding this point to path
        Path.append(currentPt)

        # Getting parent and updating current point
        currentPt = Parent[currentPt[1]][currentPt[0]].copy()

    # Reversing the path (to get from src to end)
    Path.reverse()
    
    return Path


def RunningPoints_to_frame(InitialPoints, f_x, f_y):
    FinalPoints = []
    for i in range(len(InitialPoints)):
        FinalPoints.append([InitialPoints[i][0] + f_x, InitialPoints[i][1] + f_y])
    
    return FinalPoints



def Dij_ShortestPath():
    global dij_src_F, dij_end_F, Weights, CanvasShape, RunningPoints_F, \
            dij_src_roi, dij_end_roi, ROI_Shape, ROI_Rect, RunningPoints_roi

    # If dij_src_F and dij_end_F are neighbours - directly update running points 
    if abs(dij_src_F[0] - dij_end_F[0]) <= 1 and abs(dij_src_F[1] - dij_end_F[1]) <= 1:
        if dij_src_F[0] == dij_end_F[0] and dij_src_F[1] == dij_end_F[1]:
            RunningPoints_F = [[dij_src_F[0], dij_src_F[1]]]
        else:
            RunningPoints_F = [[dij_src_F[0], dij_src_F[1]],
                             [dij_end_F[0], dij_end_F[1]]]
        return

    # Setting Weights of neighbours
    if Weights is None:
        Dij_SetWeights()

    # Setting ROI for Dijsktra's
    Dij_SetROI()

    # Distances of the points from source
    Distances = np.ones((ROI_Shape[0], ROI_Shape[1], 1), dtype=np.float32) * 100000000.0
    Distances[dij_src_roi[1]][dij_src_roi[0]] = 0       # Distance of source to source is zero

    # Parents of all the points
    # [-1, -1] for no parent (source node)
    Parent = [[[-1, -1] for j in range(ROI_Shape[1])] for i in range(ROI_Shape[0])]

    # Adding all points in queue is row major 
    # [ rowMajor(x, y) = x + y*FrameShape[1] ]
    # [ x = rowMajor(x, y) % FrameShape[1] ; y = rowMajor(x, y) // FrameShape[1] ]
    Queue = [i for i in range(ROI_Shape[0] * ROI_Shape[1])]

    # Finding shortest path for all vertices
    while Queue:
        # Getting the index of minimum distance point
        minDistPt = FindMinDistPt(Distances, Queue)

        # Removing min distance point from queue
        Queue.remove(minDistPt[2])

        # Updating distance values and parent of the neighbouring points
        # Consider only those points which are still in Queue
        Distances, Parent = UpdateDist_nd_Parent(minDistPt, Distances, Parent, Queue)

    
    # Getting the shortest path from src to end
    RunningPoints_roi = ExtractParentPath(dij_end_roi, Parent)

    # Converting Running point from wrt roi to frame
    RunningPoints_F = RunningPoints_to_frame(RunningPoints_roi, ROI_Rect[0], ROI_Rect[1])



def DrawPoints(Image, Points, Colour=[127, 127, 127]):
    for i in range(len(Points)):
        Image[Points[i][1]][Points[i][0]] = Colour

    return Image


def CvtPointsToContour(Points):
    Contour = []
    for i in range(len(Points)):
        Contour.append([[Points[i][0], Points[i][1]]])

    return Contour


def CallBackFunc_MagLassoTool(event, x, y, flags, params):
    # Taking global params
    global selecting, isSelected, CombinedFrame, FrameToShow, CanvasShape, SelectedContour, \
            dij_src_F, dij_end_F, RunningPoints_F, FinalPoints_F, RunningPoints_roi

    # If while selecting the region, mouse goes out of the frame, then clip it position 
    # to the nearest corner/edge of the frame
    if selecting:
        x, y = hf.Correct_xy_While_Selecting(x, y, [0, CanvasShape[1]-1], [0, CanvasShape[0]-1])    
    
    # Setting dijsktra's end point to mouse cursor's current coordinate
    dij_end_F = [x, y]

    # Starts selecting - Left button is pressed down
    if event == cv2.EVENT_FLAG_LBUTTON:
        if isSelected:
            isSelected = False
            selecting = True
            dij_src_F = [x, y]
            RunningPoints_F = []
            RunningPoints_roi = []
            FinalPoints_F = []
            SelectedContour = []
            # Call dijsktra's ----- is needed
            # Dij_ShortestPath()
            
        else:
            if not selecting:
                selecting = True
                dij_src_F = [x, y]
                RunningPoints_F = []
                RunningPoints_roi = []
                FinalPoints_F = []
                # Call dijsktra's ----- is needed
                # Dij_ShortestPath()

            else:
                # Add shortest path to final points
                FinalPoints_F += RunningPoints_F
                dij_src_F = [x, y]

    # Selecting the region
    elif event == cv2.EVENT_MOUSEMOVE:
        if selecting:
            # Call dijsktra's 
            Dij_ShortestPath()
            # Draw selected and running
            FrameToShow = CombinedFrame.copy()
            FrameToShow = DrawPoints(FrameToShow, FinalPoints_F, Colour=[0, 255, 0])
            FrameToShow = DrawPoints(FrameToShow, RunningPoints_F, Colour=[0, 0, 255])


    # Stop selecting the layer.
    elif event == cv2.EVENT_LBUTTONDBLCLK:
        isSelected = True
        selecting = False
        # Check final points size here
        if len(FinalPoints_F) <= 2:
            FinalPoints_F = []
            isSelected = False
        
        # Add last running points to final points
        FinalPoints_F += RunningPoints_F
        # Convert finalPoints to Selected Contour
        SelectedContour = CvtPointsToContour(FinalPoints_F)
        # Draw contour
        FrameToShow = CombinedFrame.copy()
        cv2.drawContours(FrameToShow, [np.array(SelectedContour)], -1, (0, 255, 0), 1)#(127, 127, 127), 1)


def MagneticLassoTool(Canvas, window_title):
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
    cv2.setMouseCallback(window_title, CallBackFunc_MagLassoTool)

    # Setting some params used in callback function
    global selecting, isSelected, CombinedFrame, FrameToShow, CanvasShape, SelectedContour, \
            dij_src_F, dij_end_F, RunningPoints_F, FinalPoints_F, Weights, \
            ROI_Frame, ROI_Shape, dij_src_roi, dij_end_roi, ROI_Rect, RunningPoints_roi, ROI_Weights
    selecting = False       # True if region is being selected      
    isSelected = False      # True if region is selected
    Canvas.CombineLayers()
    CombinedFrame = Canvas.CombinedImage.copy()     # the combined frame of the canvas
    FrameToShow = CombinedFrame.copy()              # The frame which will be shown (with the selected region)
    CanvasShape = Canvas.Shape                      # Shape of the canvas
    SelectedContour = []                            # Contour of the selected region
    RunningPoints_F = []                              # The points that are being selected
    FinalPoints_F = []                                # The points that are finalized
    dij_src_F = None                                  # Strat point of dijstra's algo
    dij_end_F = None                                  # End point of dijstra's algo
    Weights = None                                  # Weights of all the neighbours for each pixel in the image
    # Same params wrt the ROI
    ROI_Frame, ROI_Shape, dij_src_roi, dij_end_roi, ROI_Rect, ROI_Weights = None, None, None, None, None, None
    RunningPoints_roi = []

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
        SelectedContourToOrigin, Selected_Mask, Selected_BB = hf.ShiftContour(SelectedContour, Get_Mask_BB=True)

        # Redrawing mask to conver any uncovered area
        OuterContour, _ = cv2.findContours(Selected_Mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        cv2.drawContours(Selected_Mask, OuterContour, -1, 255, -1)

        # Extracting the selected regions and copying them in a new layer
        ExtractSelectedRegion(Canvas, Selected_BB, Selected_Mask, layer_nos_to_copy)
    
    else:
        print("\nRegion selection aborted.")

