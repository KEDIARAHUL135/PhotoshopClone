import cv2
import numpy as np

import selectRegionClass
import helping_functions as hf



####################################################### Rectangular Marquee Tool ##############################################################################

class _RectangularMarqueeToolClass(selectRegionClass._SelectRegion):
    def __init__(self, Canvas, window_title, AskLayerNames=True, CorrectXYWhileSelecting=True, RegionMovable=True):
        super().__init__(Canvas, window_title, AskLayerNames=AskLayerNames, 
                         CorrectXYWhileSelecting=CorrectXYWhileSelecting, RegionMovable=RegionMovable)

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
        if self.Key == 87 or self.Key == 119:       # If 'W'/'w' - move up
            self.Y1_ -= 1
            self.Y2_ -= 1
        elif self.Key == 65 or self.Key == 97:      # If 'A'/'a' - move left
            self.X1_ -= 1
            self.X2_ -= 1
        elif self.Key == 83 or self.Key == 115:     # If 'S'/'s' - move down
            self.Y1_ += 1
            self.Y2_ += 1
        elif self.Key == 68 or self.Key == 100:     # If 'D'/'d' - move right
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
    def __init__(self, Canvas, window_title, AskLayerNames=True, CorrectXYWhileSelecting=False, RegionMovable=True):
        super().__init__(Canvas, window_title, AskLayerNames=AskLayerNames, 
                         CorrectXYWhileSelecting=CorrectXYWhileSelecting, RegionMovable=RegionMovable)
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
        if self.Key == 87 or self.Key == 119:       # If 'W'/'w' - move up
            self.Y_ -= 1
        elif self.Key == 65 or self.Key == 97:      # If 'A'/'a' - move left
            self.X_ -= 1
        elif self.Key == 83 or self.Key == 115:     # If 'S'/'s' - move down
            self.Y_ += 1
        elif self.Key == 68 or self.Key == 100:     # If 'D'/'d' - move right
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

class _SingleRowMarqueeToolClass(selectRegionClass._SelectRegion):
    def __init__(self, Canvas, window_title, AskLayerNames=True, CorrectXYWhileSelecting=True, RegionMovable=True):
        super().__init__(Canvas, window_title, AskLayerNames=AskLayerNames, 
                         CorrectXYWhileSelecting=CorrectXYWhileSelecting, RegionMovable=RegionMovable)

        self.X_ = 0      # Starting point of the row selected
        self.Y_ = 0      # Y-coordinate of the row selected

    # Drawing selected line
    def DrawRegion(self):
        cv2.line(self.FrameToShow, (self.X_, self.Y_), (self.X_ + self.CanvasShape[1]-1, self.Y_), (127, 127, 127), 1)

    # Mouse left button is pressed down
    def Mouse_EVENT_LBUTTONDOWN(self):
        self.X_ = 0
        self.Y_ = self.y

    # Mouse is moved while selecting the region
    def Mouse_EVENT_MOUSEMOVE_selecting(self):
        self.Y_ = self.y

    # Mouse left button is released
    def Mouse_EVENT_LBUTTONUP(self):
        self.Y_ = self.y

    # When region is selected - move it
    def Region_isSelected(self):
        if self.Key == 87 or self.Key == 119:       # If 'W'/'w' - move up
            self.Y_ -= 1
        elif self.Key == 65 or self.Key == 97:      # If 'A'/'a' - move left
            self.X_ -= 1
        elif self.Key == 83 or self.Key == 115:     # If 'S'/'s' - move down
            self.Y_ += 1
        elif self.Key == 68 or self.Key == 100:     # If 'D'/'d' - move right
            self.X_ += 1        
        
    # When region is selected, setting bounding box and mask of the selected region
    def GetSelectedRegionDetails(self):
        # Correcting rectangular's points
        self.Selected_BB = [self.X_, self.Y_, self.CanvasShape[1], 1]
        self.Selected_Mask = np.ones((self.Selected_BB[3], self.Selected_BB[2], 1), dtype=np.uint8) * 255


def SingleRowMarqueeTool(Canvas, window_title):
    ToolObject = _SingleRowMarqueeToolClass(Canvas, window_title)
    ToolObject.RunTool()


###############################################################################################################################################################

######################################################## Single Column Marquee Tool ###########################################################################

class _SingleColMarqueeToolClass(selectRegionClass._SelectRegion):
    def __init__(self, Canvas, window_title, AskLayerNames=True, CorrectXYWhileSelecting=True, RegionMovable=True):
        super().__init__(Canvas, window_title, AskLayerNames=AskLayerNames, 
                         CorrectXYWhileSelecting=CorrectXYWhileSelecting, RegionMovable=RegionMovable)

        self.X_ = 0      # Starting point of the row selected
        self.Y_ = 0      # Y-coordinate of the row selected

    # Drawing selected line
    def DrawRegion(self):
        cv2.line(self.FrameToShow, (self.X_, self.Y_), (self.X_, self.Y_ + self.CanvasShape[0]-1), (127, 127, 127), 1)

    # Mouse left button is pressed down
    def Mouse_EVENT_LBUTTONDOWN(self):
        self.X_ = self.x
        self.Y_ = 0

    # Mouse is moved while selecting the region
    def Mouse_EVENT_MOUSEMOVE_selecting(self):
        self.X_ = self.x

    # Mouse left button is released
    def Mouse_EVENT_LBUTTONUP(self):
        self.X_ = self.x

    # When region is selected - move it
    def Region_isSelected(self):
        if self.Key == 87 or self.Key == 119:       # If 'W'/'w' - move up
            self.Y_ -= 1
        elif self.Key == 65 or self.Key == 97:      # If 'A'/'a' - move left
            self.X_ -= 1
        elif self.Key == 83 or self.Key == 115:     # If 'S'/'s' - move down
            self.Y_ += 1
        elif self.Key == 68 or self.Key == 100:     # If 'D'/'d' - move right
            self.X_ += 1      
        
    # When region is selected, setting bounding box and mask of the selected region
    def GetSelectedRegionDetails(self):
        # Correcting rectangular's points
        self.Selected_BB = [self.X_, self.Y_, 1, self.CanvasShape[0]]
        self.Selected_Mask = np.ones((self.Selected_BB[3], self.Selected_BB[2], 1), dtype=np.uint8) * 255


def SingleColMarqueeTool(Canvas, window_title):
    ToolObject = _SingleColMarqueeToolClass(Canvas, window_title)
    ToolObject.RunTool()

###############################################################################################################################################################
