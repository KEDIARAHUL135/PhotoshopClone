import cv2
import heapq
import numpy as np

import drawing
import selectRegionClass
import helping_functions as hf
from selectRegionClass import AskLayerNumsToCopy, CropVisible, ExtractSelectedRegion



########################################################### Lasso Tool ################################################################################

class _LassoToolClass(selectRegionClass._SelectRegion):
    def __init__(self, Canvas, window_title, AskLayerNames=True, CorrectXYWhileSelecting=True, RegionMovable=True):
        super().__init__(Canvas, window_title, AskLayerNames=AskLayerNames, 
                         CorrectXYWhileSelecting=CorrectXYWhileSelecting, RegionMovable=RegionMovable)

        self.SelectedContour = []

    # How to draw the region
    def DrawRegion(self):
        if not self.isSelected:
            drawing.Inc_Contour(self.FrameToShow, self.SelectedContour)
        else:
            drawing.Com_Contours(self.FrameToShow, [self.SelectedContour])

    
    # When moue left button is pressed down
    def Mouse_EVENT_LBUTTONDOWN(self):
        self.SelectedContour = []
        self.SelectedContour.append([self.x, self.y])

    # When mouse is moved while selecting
    def Mouse_EVENT_MOUSEMOVE_selecting(self):
        self.SelectedContour.append([self.x, self.y])
        
    # When mouse left button is released - check if something is selected
    def Mouse_EVENT_LBUTTONUP(self):
        if len(self.SelectedContour) <= 2:
            self.isSelected = False

    # When selected, move the region
    def Region_isSelected(self):
        if self.Key == 87 or self.Key == 119:       # If 'W'/'w' - move up
            self.SelectedContour = hf.ShiftContour(self.SelectedContour, ToOrigin=False, ShiftBy=[0, -1])
        elif self.Key == 65 or self.Key == 97:      # If 'A'/'a' - move left
            self.SelectedContour = hf.ShiftContour(self.SelectedContour, ToOrigin=False, ShiftBy=[-1, 0])
        elif self.Key == 83 or self.Key == 115:     # If 'S'/'s' - move down
            self.SelectedContour = hf.ShiftContour(self.SelectedContour, ToOrigin=False, ShiftBy=[0, 1])
        elif self.Key == 68 or self.Key == 100:     # If 'D'/'d' - move right
            self.SelectedContour = hf.ShiftContour(self.SelectedContour, ToOrigin=False, ShiftBy=[1, 0])
        
    # When region is selected and confirmed
    def GetSelectedRegionDetails(self):
        # Finding Selected regions bounding box, its contour shifted to origin, and its shifted mask image
        # Selected_BB = list(cv2.boundingRect(np.array(SelectedContour)))
        _, self.Selected_Mask, self.Selected_BB = hf.ShiftContour(self.SelectedContour, Get_Mask_BB=True)

        # Redrawing mask to conver any uncovered area
        OuterContour, _ = cv2.findContours(self.Selected_Mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        cv2.drawContours(self.Selected_Mask, OuterContour, -1, 255, -1)


def LassoTool(Canvas, window_title):
    ToolObject = _LassoToolClass(Canvas, window_title)
    ToolObject.RunTool()


#######################################################################################################################################################


########################################################### Polygon Lasso Tool ########################################################################

class _PolygonLassoToolClass(selectRegionClass._SelectRegion):
    def __init__(self, Canvas, window_title, AskLayerNames=True, CorrectXYWhileSelecting=True, RegionMovable=True):
        super().__init__(Canvas, window_title, AskLayerNames=AskLayerNames, 
                         CorrectXYWhileSelecting=CorrectXYWhileSelecting, RegionMovable=RegionMovable)

        self.Selected_Points = []

    # How to draw the region
    def DrawRegion(self):
        if self.selecting:
            for i in range(len(self.Selected_Points)-1):
                cv2.line(self.FrameToShow, tuple(self.Selected_Points[i][0]), tuple(self.Selected_Points[i+1][0]), (127, 127, 127), 1)
            cv2.line(self.FrameToShow, tuple(self.Selected_Points[-1][0]), (self.x, self.y), (127, 127, 127), 1)
        elif self.isSelected:
            cv2.drawContours(self.FrameToShow, [np.array(self.Selected_Points)], -1, (127, 127, 127), 1)

    # Callback function will be fully modified
    def CallBackFunc(self, event, x, y, flags, params):
        # If while selecting the region, mouse goes out of the frame, then clip it position 
        # to the nearest corner/edge of the frame
        if self.selecting:
            self.x, self.y = hf.Correct_xy_While_Selecting(self.x, self.y, [0, self.CanvasShape[1]-1], [0, self.CanvasShape[0]-1])
        
        # Storing mouse pointer values to self variable for access outside the function
        self.x, self.y = x, y
        
        # Starts selecting - Left button is pressed down
        if event == cv2.EVENT_FLAG_LBUTTON:
            self.selecting = True
            if self.isSelected:     # If already selected, start drawing a new one
                self.isSelected = False
                self.Selected_Points = []
            self.Selected_Points.append([[x, y]])
            
        # Selecting the region
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.selecting:
                self.SetCanvasFrame()

        # Stop selecting the layer.
        elif event == cv2.EVENT_LBUTTONDBLCLK:
            self.isSelected = True
            self.selecting = False
            if len(self.Selected_Points) <= 2:
                self.Selected_Points = []
                self.isSelected = False
            else:
                self.Selected_Points.append([[x, y]])
            self.SetCanvasFrame()

    # Move when region is selected
    def Region_isSelected(self):
        if self.Key == 87 or self.Key == 119:     # If 'W'/'w' - move up
            self.Selected_Points = hf.ShiftContour(self.Selected_Points, ToOrigin=False, ShiftBy=[0, -1])
        elif self.Key == 65 or self.Key == 97:      # If 'A'/'a' - move left
            self.Selected_Points = hf.ShiftContour(self.Selected_Points, ToOrigin=False, ShiftBy=[-1, 0])
        elif self.Key == 83 or self.Key == 115:     # If 'S'/'s' - move down
            self.Selected_Points = hf.ShiftContour(self.Selected_Points, ToOrigin=False, ShiftBy=[0, 1])
        elif self.Key == 68 or self.Key == 100:     # If 'D'/'d' - move right
            self.Selected_Points = hf.ShiftContour(self.Selected_Points, ToOrigin=False, ShiftBy=[1, 0])
        
    # Extracting selected regions BB and Mask
    def GetSelectedRegionDetails(self):
        # Finding Selected regions bounding box, its contour shifted to origin, and its shifted mask image
        # Selected_BB = list(cv2.boundingRect(np.array(SelectedContour)))
        _, self.Selected_Mask, self.Selected_BB = hf.ShiftContour(self.Selected_Points, Get_Mask_BB=True)

        # Redrawing mask to conver any uncovered area
        OuterContour, _ = cv2.findContours(self.Selected_Mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        cv2.drawContours(self.Selected_Mask, OuterContour, -1, 255, -1)
        

def PolygonLassoTool(Canvas, window_title):
    ToolObject = _PolygonLassoToolClass(Canvas, window_title)
    ToolObject.RunTool()

#######################################################################################################################################################


########################################################### Magnetic Lasso Tool #######################################################################


def Dij_SetROI():
    global CombinedFrame, CanvasShape, dij_src_F, dij_end_F, RunningPoints_F, FinalPoints_F, Weights
    global ROI_Frame, ROI_Shape, dij_src_roi, dij_end_roi, ROI_Rect, ROI_Weights

    # Getting ROI's bounding rect
    ExtraROIBoundary = 10
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
    #CombinedFrame = cv2.blur(CombinedFrame, (3, 3))
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
        Weights[i] = cv2.max(255 - (B*B + G*G + R*R + 0.01), 0)



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
            dij_src_roi, dij_end_roi, ROI_Shape, ROI_Rect, RunningPoints_roi, ROI_Weights

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

    # 1 if the node is visited, 0 if the node is not visited
    IsVisited = np.zeros((ROI_Shape[0], ROI_Shape[1], 1), dtype=bool)

    # Distances of the points from source
    Distances = np.ones((ROI_Shape[0], ROI_Shape[1], 1), dtype=np.float32) * 100000000.0
    Distances[dij_src_roi[1]][dij_src_roi[0]] = 0       # Distance of source to source is zero

    # Parents of all the points
    # [-1, -1] for no parent (source node)
    Parent = [[[-1, -1] for j in range(ROI_Shape[1])] for i in range(ROI_Shape[0])]


    # Initializing priority queue
    PQueue = []

    # Current node
    [currX, currY] = dij_src_roi

    # Finding shortest path for all vertices
    while True:
        # Setting current node as visited
        IsVisited[currY][currX] = True

        # Loop through all neighbours
        for i in range(-1, 2, 1):
            for j in range(-1, 2, 1):
                # Continue if the neighbour is already visited
                if IsVisited[currY + i][currX + j]:
                    continue

                # Finding new and old distances of the newghbour
                OldDist = Distances[currY + i][currX + j]
                NewDist = Distances[currY][currX] + ROI_Weights[(i+1)*3 + (j+1)][currY][currX]

                # if new distance is lesser than old distance
                if NewDist < OldDist:
                    # Updating distance
                    Distances[currY + i][currX + j] = NewDist

                    # Updating parent of this neighbour is the current point
                    Parent[currY + i][currX + j] = [currX, currY]

                    # Pushing this neighbour to priority Queue
                    if not IsVisited[currY + i][currX + j] and \
                       0 < (currX + j) < (ROI_Shape[1] - 1) and \
                       0 < (currY + i) < (ROI_Shape[0] - 1):
                        heapq.heappush(PQueue, (NewDist, currX + j, currY + i))

        #### End of updating neighbours loop

        # Break if priority queue is empty
        if len(PQueue) == 0:
            break

        # Finding the minimum distance element in priority queue, 
        # check if it is visited, 
        # if not, remove it and update currX&Y
        minPQEle = heapq.heappop(PQueue)
        while IsVisited[minPQEle[2]][minPQEle[1]]:
            try:
                minPQEle = heapq.heappop(PQueue)
            except IndexError:
                break

        currX, currY = minPQEle[1], minPQEle[2]

    
    # Getting the shortest path from src to end
    RunningPoints_roi = ExtractParentPath(dij_end_roi, Parent)

    # Converting Running point from wrt roi to frame
    RunningPoints_F = RunningPoints_to_frame(RunningPoints_roi, ROI_Rect[0], ROI_Rect[1])



def DrawPoints(Image, Points, Colour=[127, 127, 127]):
    for i in range(len(Points)):
        Image[Points[i][1]][Points[i][0]] = Colour

    return Image


def DrawPointsOnFrame():
    global FrameToShow, CombinedFrame, RunningPoints_F, FinalPoints_F

    # Drawing points
    FrameToShow = CombinedFrame.copy()
    FrameToShow = DrawPoints(FrameToShow, FinalPoints_F, Colour=[0, 255, 0])
    FrameToShow = DrawPoints(FrameToShow, RunningPoints_F, Colour=[0, 0, 255])


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
            
        else:
            if not selecting:
                selecting = True
                dij_src_F = [x, y]
                RunningPoints_F = []
                RunningPoints_roi = []
                FinalPoints_F = []

            else:
                # Add shortest path to final points
                FinalPoints_F += RunningPoints_F[:-15]
                dij_src_F = RunningPoints_F[-15]#[x, y]

    # Selecting the region
    elif event == cv2.EVENT_MOUSEMOVE:
        if selecting:
            # Call dijsktra's 
            Dij_ShortestPath()
            # Draw selected and running
            DrawPointsOnFrame()


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
        cv2.drawContours(FrameToShow, [np.array(SelectedContour)], -1, (127, 127, 127), 1)


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

        if Key == 8:                        # If Backspace pressed
            if len(FinalPoints_F) > 1:
                PoppedEle = FinalPoints_F.pop()
                dij_src_F = PoppedEle
                RunningPoints_F.insert(0, PoppedEle)
                DrawPointsOnFrame()
                
        if Key == 89 or Key == 121:         # If 'Y'/'y' - confirm
            if isSelected:                  # If the region is selected
                break
            else:                           # If the region is not selected yet
                print("\nSelect a region first to confirm.")
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

