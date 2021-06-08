import cv2
import numpy as np

import selectRegionClass
import helping_functions as hf


############################################################## Object Selection Tool ###########################################################################

class _ObjectSelectionToolClass(selectRegionClass._SelectRegion):
    def __init__(self, Canvas, window_title, AskLayerNames=True, CorrectXYWhileSelecting=True, RegionMovable=True):
        super().__init__(Canvas, window_title, AskLayerNames=AskLayerNames, 
                         CorrectXYWhileSelecting=CorrectXYWhileSelecting, RegionMovable=RegionMovable)

        self.X1, self.Y1 = -1, -1
        self.X2, self.Y2 = -1, -1

        self.SelectedContours = []

    # How to draw the selected region
    def DrawRegion(self):
        if self.selecting:
            cv2.drawContours(self.FrameToShow, np.array(self.SelectedContours), -1, (127, 127, 127), 1)
        else:
            cv2.drawContours(self.FrameToShow, self.SelectedContours, -1, (127, 127, 127), 1)

    # When mouse left button is pressed
    def Mouse_EVENT_LBUTTONDOWN(self):
        self.X1, self.Y1 = self.x, self.y
        self.X2, self.Y2 = self.x, self.y
        self.SelectedContours = []

    # When selecting and mouse is moving
    def Mouse_EVENT_MOUSEMOVE_selecting(self):
        self.X2, self.Y2 = self.x, self.y
        # Converting this selecting rectangle to selected contour for now for visualization
        self.SelectedContours = [ np.asarray([[[self.X1, self.Y1]], 
                                              [[self.X2, self.Y1]],
                                              [[self.X2, self.Y2]],
                                              [[self.X1, self.Y2]]]) ]

    # Grabcut algorithm
    def ApplyGrabcut(self, ItCount=5, Mode=cv2.GC_INIT_WITH_RECT):
        # Creating blank mask image
        Mask = np.zeros(self.CombinedFrame.shape[:2], dtype=np.uint8)

        # bgdModel & fgdModel variables to be passed
        bgdModel = np.zeros((1, 65), dtype=np.float64)
        fgdModel = np.zeros((1, 65), dtype=np.float64)

        # Selection rectangle
        Rect = [min(self.X1, self.X2), min(self.Y1, self.Y2), abs(self.X1 - self.X2) + 1, abs(self.Y1 - self.Y2) + 1]

        # Running Grabcut algorithm
        cv2.grabCut(self.CombinedFrame.copy(), Mask, Rect, bgdModel, fgdModel, ItCount, Mode)

        # Final mask image of foreground and background
        FgBgMask = np.where((Mask==2) | (Mask==0), 0, 1).astype(np.uint8)

        # Detecting contours - there can be more than one regions detected
        self.SelectedContours = cv2.findContours(FgBgMask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0]
    
    # When mouse left button is released
    def Mouse_EVENT_LBUTTONUP(self):
        self.X2, self.Y2 = self.x, self.y
        if self.X1 == self.X2 and self.Y1 == self.Y2:
            self.isSelected = False
            return
        self.ApplyGrabcut()

    # When region is selected and being moved
    def Region_isSelected(self):
        if self.Key == 87 or self.Key == 119:       # If 'W'/'w' - move up
            for i in range(len(self.SelectedContours)):
                self.SelectedContours[i] = hf.ShiftContour(self.SelectedContours[i], ToOrigin=False, ShiftBy=[0, -1])
        elif self.Key == 65 or self.Key == 97:      # If 'A'/'a' - move left
            for i in range(len(self.SelectedContours)):
                self.SelectedContours[i] = hf.ShiftContour(self.SelectedContours[i], ToOrigin=False, ShiftBy=[-1, 0])
        elif self.Key == 83 or self.Key == 115:     # If 'S'/'s' - move down
            for i in range(len(self.SelectedContours)):
                self.SelectedContours[i] = hf.ShiftContour(self.SelectedContours[i], ToOrigin=False, ShiftBy=[0, 1])
        elif self.Key == 68 or self.Key == 100:     # If 'D'/'d' - move right
            for i in range(len(self.SelectedContours)):
                self.SelectedContours[i] = hf.ShiftContour(self.SelectedContours[i], ToOrigin=False, ShiftBy=[1, 0])        
        
    # When region is confirmed
    def GetSelectedRegionDetails(self):
        # As there can be no contours also
        if len(self.SelectedContours) == 0:
            self.Selected_BB = [0, 0, 10, 10]
            self.Selected_Mask = np.zeros((10, 10, 1), dtype=np.uint8)
            return

        # Getting bounding box of the contour - [x1, y1, x2, y2]
        def GetBoundingBox(Contour):
            BB = cv2.boundingRect(Contour)
            return [BB[0], BB[1], BB[0]+BB[2]-1, BB[1]+BB[3]-1]

        # As there can be more than one contours, we have to find a common bounding box
        self.Selected_BB = GetBoundingBox(self.SelectedContours[0])
        for i in range(1, len(self.SelectedContours)):
            BB = GetBoundingBox(self.SelectedContours[i])
            self.Selected_BB[0] = min(self.Selected_BB[0], BB[0])
            self.Selected_BB[1] = min(self.Selected_BB[1], BB[1])
            self.Selected_BB[2] = max(self.Selected_BB[2], BB[2])
            self.Selected_BB[3] = max(self.Selected_BB[3], BB[3])
        self.Selected_BB[2] = self.Selected_BB[2] - self.Selected_BB[0] + 1
        self.Selected_BB[3] = self.Selected_BB[3] - self.Selected_BB[1] + 1

        # Getting the mask image
        MaskImage = np.zeros((self.CanvasShape[0], self.CanvasShape[1], 1), dtype=np.uint8)
        cv2.drawContours(MaskImage, np.array(self.SelectedContours), -1, 255, -1)
        x, y, w, h = self.Selected_BB
        self.Selected_Mask = MaskImage[y : y + h, x : x + w].copy()



# Main object selection tool function
def ObjectSelectionTool(Canvas, window_title):
    ToolObject = _ObjectSelectionToolClass(Canvas, window_title)
    ToolObject.RunTool()


################################################################################################################################################################


############################################################### Quick Selection Tool ###########################################################################

class _QuickSelectionToolClass(selectRegionClass._SelectRegion):
    def __init__(self, Canvas, window_title, AskLayerNames=True, CorrectXYWhileSelecting=True, RegionMovable=True):
        super().__init__(Canvas, window_title, AskLayerNames=AskLayerNames, 
                         CorrectXYWhileSelecting=CorrectXYWhileSelecting, RegionMovable=RegionMovable)

        # All pixels = PR_BG for unknown area
        self.RegionMask = np.ones((self.CanvasShape[0], self.CanvasShape[1], 1), dtype=np.uint8) * cv2.GC_PR_BGD

    # Drawing selected regions on the canvas
    def DrawRegion(self):
        Mask = np.zeros(self.RegionMask.shape, dtype=np.uint8)
        Mask[(self.RegionMask==cv2.GC_FGD) | (self.RegionMask==cv2.GC_PR_FGD)] = 255
        Contours = cv2.findContours(Mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)[-2]
        if len(Contours) != 0:
            cv2.drawContours(self.FrameToShow, Contours, -1, (127, 127, 127), 1)

    # printing extra instructions
    def PrintInstructions(self):
        print("Press-Hold and drag mouse left button to Add Selection areas.")
        print("The new selection arrea will be added when you release the mouse left button.")
        print("Double click mouse left button to Start a New Selection.")
        print()


    def SetRegionMask_Selecting(self):
        SelectedPointRadius = 2
        cv2.circle(self.RegionMask, (self.x, self.y), SelectedPointRadius, cv2.GC_FGD, -1)

    # Redefining callback method
    def CallBackFunc(self, event, x, y, flags, params):
        # If while selecting the region, mouse goes out of the frame, then clip it position 
        # to the nearest corner/edge of the frame
        if self.selecting and self.CorrectXYWhileSelecting:
            x, y = hf.Correct_xy_While_Selecting(x, y, [0, self.CanvasShape[1]-1], [0, self.CanvasShape[0]-1])

        # Storing mouse pointer values to self variable for access outside the function
        self.x, self.y = x, y

        # Starts selecting - Left button is pressed down
        if event == cv2.EVENT_LBUTTONDOWN or event == cv2.EVENT_RBUTTONDOWN:
            self.selecting = True
            self.isSelected = False
            self.SetRegionMask_Selecting()
            self.SetCanvasFrame()

        # Selecting the region
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.selecting:
                self.SetRegionMask_Selecting()
                self.SetCanvasFrame()

        # Stop selecting the layer.
        elif event == cv2.EVENT_LBUTTONUP or event == cv2.EVENT_RBUTTONUP:
            self.selecting = False
            self.isSelected = True
            self.ApplyGrabcut(ItCount=1)
            self.SetCanvasFrame()

        # Reset region masks
        elif event == cv2.EVENT_LBUTTONDBLCLK:
            self.selecting = False
            self.isSelected = False
            self.RegionMask = np.ones((self.CanvasShape[0], self.CanvasShape[1], 1), dtype=np.uint8) * cv2.GC_PR_BGD
            self.SetCanvasFrame()


    # Applying grabcut
    def ApplyGrabcut(self, ItCount=5, Mode=cv2.GC_INIT_WITH_MASK):
        # bgdModel & fgdModel variables to be passed
        bgdModel = np.zeros((1, 65), dtype=np.float64)
        fgdModel = np.zeros((1, 65), dtype=np.float64)

        # Running Grabcut algorithm
        try:        # Grabcut will throw an error if there is no foreground point in the input mask
            GC_Output, bgdModel, fgdModel = cv2.grabCut(self.CombinedFrame, self.RegionMask.copy(), None, bgdModel, fgdModel, ItCount, Mode)
            
            # Getting the foreground part connected to mouse pointer position only and adding it
            # Foreground found is black and background is white for applying floodfill
            FGD_Mask = np.ones(GC_Output.shape, dtype=np.uint8) * 255
            FGD_Mask[(GC_Output==cv2.GC_FGD) | (GC_Output==cv2.GC_PR_FGD)] = 0
            mask = np.zeros((FGD_Mask.shape[0] + 2, FGD_Mask.shape[1] + 2), dtype=np.uint8)
            cv2.floodFill(FGD_Mask, mask, (self.x, self.y), 127)
            self.RegionMask[FGD_Mask==127] = cv2.GC_FGD
        except:     # If no foreground point, no need to run floodfill, all points are in background
            self.RegionMask[:, :] = cv2.GC_PR_BGD

    # Getting selected region BB and mask
    def GetSelectedRegionDetails(self):
        self.Selected_Mask = np.zeros(self.RegionMask.shape, dtype=np.uint8)
        self.Selected_Mask[(self.RegionMask==cv2.GC_FGD) | (self.RegionMask==cv2.GC_PR_FGD)] = 255
        self.Selected_BB = [0, 0, self.CanvasShape[1], self.CanvasShape[0]]

    

def QuickSelectionTool(Canvas, window_title):
    ToolObject = _QuickSelectionToolClass(Canvas, window_title, RegionMovable=False)
    ToolObject.RunTool()
    