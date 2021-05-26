import cv2
import numpy as np

import input_output
import selectRegionClass
import helping_functions as hf



####################################################### Rectangular Marquee Tool ##############################################################################

class _RectangularMarqueeToolClass(selectRegionClass._SelectRegion):
    def __init__(self, Canvas, window_title, AskLayerNames=True, CorrectXYWhileSelecting=True):
        super().__init__(Canvas, window_title, AskLayerNames=AskLayerNames, 
                         CorrectXYWhileSelecting=CorrectXYWhileSelecting)

        # Selected rectangle position of top left and bottom right corner
        self.X1_, self.Y1_ = 0, 0
        self.X2_, self.Y2_ = 0, 0

    # Defining how to draw the selected region
    def DrawRegion(self):
        cv2.rectangle(self.FrameToShow, (self.X1_, self.Y1_), (self.X2_, self.Y2_), (127, 127, 127), 1)

    # If left button is pressed
    def Mouse_EVENT_LBUTTONDOWN(self):
        self.X1_, self.Y1_ = self.x, self.y

    # If mouse is moved while selecting the region
    def Mouse_EVENT_MOUSEMOVE_selecting(self):
        self.X2_, self.Y2_ = self.x, self.y

    # If mouse left button is released
    def Mouse_EVENT_LBUTTONUP(self):
        self.X2_, self.Y2_ = self.x, self.y
        if self.X1_ == self.X2_ and self.Y1_ == self.Y2_:
            self.isSelected = False
    
    # Inside the while loop if the area is selected
    def Region_isSelected(self):
        if self.Key == 87 or self.Key == 119:     # If 'W'/'w' - move up
            self.Y1_ -= 1
            self.Y2_ -= 1
        if self.Key == 65 or self.Key == 97:      # If 'A'/'a' - move left
            self.X1_ -= 1
            self.X2_ -= 1
        if self.Key == 83 or self.Key == 115:     # If 'S'/'s' - move down
            self.Y1_ += 1
            self.Y2_ += 1
        if self.Key == 68 or self.Key == 100:     # If 'D'/'d' - move right
            self.X1_ += 1
            self.X2_ += 1

    # If the region is selected and confirmed, setting selected region details
    def GetSelectedRegionDetails(self):
        # Correcting rectangular's points
        self.X1_, self.Y1_, self.X2_, self.Y2_ = hf.CorrectRectPoints(self.X1_, self.Y1_, self.X2_, self.Y2_)
        self.Selected_BB = [self.X1_, self.Y1_, (self.X2_-self.X1_+1), (self.Y2_-self.Y1_+1)]
        self.Selected_Mask = np.ones((self.Selected_BB[3], self.Selected_BB[2], 1), dtype=np.uint8) * 255
        

def RectangularMarqueeTool(Canvas, window_title):
    ToolObject = _RectangularMarqueeToolClass(Canvas, window_title)
    ToolObject.RunTool()
    

###############################################################################################################################################################


######################################################## Elliptical Marquee Tool ##############################################################################

class _EllipticalMarqueeToolClass(selectRegionClass._SelectRegion):
    def __init__(self, Canvas, window_title, AskLayerNames=True, CorrectXYWhileSelecting=False):
        super().__init__(Canvas, window_title, AskLayerNames=AskLayerNames, CorrectXYWhileSelecting=CorrectXYWhileSelecting)
        # Initializing the variables for this tool
        # Position of mouse from where ellipse is started selecting
        self.ix, self.iy = 0, 0
        # Selected ellipse's center coordinates and lengths of major and minor axes
        self.X_, self.Y_, self.A_, self.B_ = 0, 0, 0, 0

    # Draw the selected region
    def DrawRegion(self):
        cv2.ellipse(self.FrameToShow, (self.X_, self.Y_), (self.A_, self.B_), 0, 0, 360, (127, 127, 127), 1)
    
    # Mouse left button is pressed down, set initial points of ellipse
    def Mouse_EVENT_LBUTTONDOWN(self):
        self.ix, self.iy = self.x, self.y

    # When selecting and mouse is moving, get and draw ellipse
    def Mouse_EVENT_MOUSEMOVE_selecting(self):
        self.X_, self.Y_ = (self.ix + self.x)//2, (self.iy + self.y)//2
        self.A_, self.B_ = abs(self.ix - self.x)//2, abs(self.iy - self.y)//2

    # Mouse left button released, set ellipse data and draw ellipse
    def Mouse_EVENT_LBUTTONUP(self):
        self.X_, self.Y_ = (self.ix + self.x)//2, (self.iy + self.y)//2
        self.A_, self.B_ = abs(self.ix - self.x)//2, abs(self.iy - self.y)//2
        if self.ix == self.x and self.iy == self.y:
            self.isSelected = False

    # If region is selected and being moved
    def Region_isSelected(self):
        if self.Key == 87 or self.Key == 119:     # If 'W'/'w' - move up
            self.Y_ -= 1
        if self.Key == 65 or self.Key == 97:      # If 'A'/'a' - move left
            self.X_ -= 1
        if self.Key == 83 or self.Key == 115:     # If 'S'/'s' - move down
            self.Y_ += 1
        if self.Key == 68 or self.Key == 100:     # If 'D'/'d' - move right
            self.X_ += 1
        
    # Getting bounding box and the mask image of the selected region
    def GetSelectedRegionDetails(self):
        # Correcting rectangular's points
        self.Selected_BB = [self.X_ - self.A_, self.Y_ - self.B_, 2*self.A_, 2*self.B_]
        self.Selected_Mask = np.zeros((self.Selected_BB[3], self.Selected_BB[2], 1), dtype=np.uint8)
        cv2.ellipse(self.Selected_Mask, (self.A_, self.B_), (self.A_, self.B_), 0, 0, 360, 255, -1)



def EllipticalMarqueeTool(Canvas, window_title):
    ToolObject = _EllipticalMarqueeToolClass(Canvas, window_title)
    ToolObject.RunTool()
    

###############################################################################################################################################################

######################################################## Single Row Marquee Tool ##############################################################################

def CallBackFunc_SRowMarqueeTool(event, x, y, flags, params):
    # Taking global params
    global selecting, isSelected, CombinedFrame, FrameToShow, CanvasShape, X_, Y_

    # Starts selecting - Left button is pressed down
    if event == cv2.EVENT_LBUTTONDOWN:
        selecting = True
        isSelected = False
        FrameToShow = CombinedFrame.copy()
        X_ = 0
        Y_ = y
        cv2.line(FrameToShow, (X_, Y_), (X_ + CanvasShape[1]-1, Y_), (127, 127, 127), 1)

    # Selecting the region
    elif event == cv2.EVENT_MOUSEMOVE:
        if selecting:
            FrameToShow = CombinedFrame.copy()
            Y_ = y
            cv2.line(FrameToShow, (X_, Y_), (X_ + CanvasShape[1]-1, Y_), (127, 127, 127), 1)

    # Stop selecting the layer.
    elif event == cv2.EVENT_LBUTTONUP:
        selecting = False
        isSelected = True
        FrameToShow = CombinedFrame.copy()
        Y_ = y
        cv2.line(FrameToShow, (X_, Y_), (X_ + CanvasShape[1]-1, Y_), (127, 127, 127), 1)



def SingleRowMarqueeTool(Canvas, window_title):
    hf.Clear()
    # Taking layer numbers user wants to copy
    Canvas.PrintLayerNames()
    layer_nos_to_copy = selectRegionClass.AskLayerNumsToCopy(-1, len(Canvas.layers) - 1)

    print("\nPress 'Y' to confirm selection and copy it in a new layer else press 'N' to abort.")
    print("You can also used the keys 'W', and 'S' to move the")
    print("selected region Up, and Down respectively.")

    # Clearing mouse buffer data (old mouse data) - this is a bug in OpenCV probably
    cv2.namedWindow(window_title)
    cv2.setMouseCallback(window_title, hf.EmptyCallBackFunc)
    Canvas.Show(Title=window_title)
    cv2.waitKey(1)

    # Setting mouse callback
    cv2.setMouseCallback(window_title, CallBackFunc_SRowMarqueeTool)

    # Setting some params used in callback function
    global selecting, isSelected, CombinedFrame, FrameToShow, CanvasShape, X_, Y_
    selecting = False       # True if region is being selected      
    isSelected = False      # True if region is selected
    Canvas.CombineLayers()
    CombinedFrame = Canvas.CombinedImage.copy()     # the combined frame of the canvas
    FrameToShow = CombinedFrame.copy()              # The frame which will be shown (with the selected region)
    CanvasShape = Canvas.Shape                      # Shape of the canvas
    X_ = 0                                          # Starting point of the row selected
    Y_ = 0                                          # Y-coordinate of the row selected


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
                Y_ -= 1
            if Key == 65 or Key == 97:      # If 'A'/'a' - move left
                X_ -= 1
            if Key == 83 or Key == 115:     # If 'S'/'s' - move down
                Y_ += 1
            if Key == 68 or Key == 100:     # If 'D'/'d' - move right
                X_ += 1
            
            FrameToShow = CombinedFrame.copy()
            cv2.line(FrameToShow, (X_, Y_), (X_ + CanvasShape[1]-1, Y_), (127, 127, 127), 1)
            

    if not IsAborted:
        # Correcting rectangular's points
        Selected_BB = [X_, Y_, CanvasShape[1], 1]
        Selected_Mask = np.ones((Selected_BB[3], Selected_BB[2], 1), dtype=np.uint8) * 255
        selectRegionClass.ExtractSelectedRegion(Canvas, Selected_BB, Selected_Mask, layer_nos_to_copy)
    
    else:
        print("\nRegion selection aborted.")


###############################################################################################################################################################

######################################################## Single Column Marquee Tool ###########################################################################

def CallBackFunc_SColMarqueeTool(event, x, y, flags, params):
    # Taking global params
    global selecting, isSelected, CombinedFrame, FrameToShow, CanvasShape, X_, Y_

    # Starts selecting - Left button is pressed down
    if event == cv2.EVENT_LBUTTONDOWN:
        selecting = True
        isSelected = False
        FrameToShow = CombinedFrame.copy()
        X_ = x
        Y_ = 0
        cv2.line(FrameToShow, (X_, Y_), (X_, Y_ + CanvasShape[0]-1), (127, 127, 127), 1)

    # Selecting the region
    elif event == cv2.EVENT_MOUSEMOVE:
        if selecting:
            FrameToShow = CombinedFrame.copy()
            X_ = x
            cv2.line(FrameToShow, (X_, Y_), (X_, Y_ + CanvasShape[0]-1), (127, 127, 127), 1)

    # Stop selecting the layer.
    elif event == cv2.EVENT_LBUTTONUP:
        selecting = False
        isSelected = True
        FrameToShow = CombinedFrame.copy()
        X_ = x
        cv2.line(FrameToShow, (X_, Y_), (X_, Y_ + CanvasShape[0]-1), (127, 127, 127), 1)



def SingleColMarqueeTool(Canvas, window_title):
    hf.Clear()
    # Taking layer numbers user wants to copy
    Canvas.PrintLayerNames()
    layer_nos_to_copy = selectRegionClass.AskLayerNumsToCopy(-1, len(Canvas.layers) - 1)

    print("\nPress 'Y' to confirm selection and copy it in a new layer else press 'N' to abort.")
    print("You can also used the keys 'A', and 'D', to move the")
    print("selected region Left, and Right respectively.")

    # Clearing mouse buffer data (old mouse data) - this is a bug in OpenCV probably
    cv2.namedWindow(window_title)
    cv2.setMouseCallback(window_title, hf.EmptyCallBackFunc)
    Canvas.Show(Title=window_title)
    cv2.waitKey(1)

    # Setting mouse callback
    cv2.setMouseCallback(window_title, CallBackFunc_SColMarqueeTool)

    # Setting some params used in callback function
    global selecting, isSelected, CombinedFrame, FrameToShow, CanvasShape, X_, Y_
    selecting = False       # True if region is being selected      
    isSelected = False      # True if region is selected
    Canvas.CombineLayers()
    CombinedFrame = Canvas.CombinedImage.copy()     # the combined frame of the canvas
    FrameToShow = CombinedFrame.copy()              # The frame which will be shown (with the selected region)
    CanvasShape = Canvas.Shape                      # Shape of the canvas
    X_ = 0                                          # X-coordinate of the column selected
    Y_ = 0                                          # Y-coordinate of the start point of the line


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
                Y_ -= 1
            if Key == 65 or Key == 97:      # If 'A'/'a' - move left
                X_ -= 1
            if Key == 83 or Key == 115:     # If 'S'/'s' - move down
                Y_ += 1
            if Key == 68 or Key == 100:     # If 'D'/'d' - move right
                X_ += 1
            
            FrameToShow = CombinedFrame.copy()
            cv2.line(FrameToShow, (X_, Y_), (X_, Y_ + CanvasShape[0]-1), (127, 127, 127), 1)
            

    if not IsAborted:
        # Correcting rectangular's points
        Selected_BB = [X_, Y_, 1, CanvasShape[0]]
        Selected_Mask = np.ones((Selected_BB[3], Selected_BB[2], 1), dtype=np.uint8) * 255
        selectRegionClass.ExtractSelectedRegion(Canvas, Selected_BB, Selected_Mask, layer_nos_to_copy)
    
    else:
        print("\nRegion selection aborted.")


###############################################################################################################################################################
