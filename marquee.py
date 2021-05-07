import cv2
import numpy as np

import input_output
import helping_functions as hf



def AskLayerNumsToCopy(a, b):
    while True:
        print("\nEnter the layer numbers you want to copy with this tool (-1 for all layers).")
        layer_nos = input_output.AskForLayerNumbers(a, b)

        if layer_nos is None:
            print("You must enter atleast one layer number.")
            continue
        else:
            return layer_nos


def CropVisible(Image):
    # Extracting alpha channel
    Alpha = Image[:, :, [-1]]
    
    # Thresholding alpha channel (all values > 0 = 255)
    AlphaTh = cv2.threshold(Alpha, 1, 255, cv2.THRESH_BINARY)[1]

    # Finding contours
    Contours, _ = cv2.findContours(AlphaTh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    # If no contours found - return None (no visible part)
    if len(Contours) == 0:
        return None

    # Extracting bounding box of the visible part(s)
    BB = cv2.boundingRect(Contours[0])
    if len(Contours) > 1:   # Taking union of bounding boxes if more than one
        for i in range(1, len(Contours)):
            BB = hf.Union(BB, cv2.boundingRect(Contours[i]))

    # Cropping out the visible part
    VisiblePartImage = Image[BB[1] : BB[1] + BB[3], BB[0] : BB[0] + BB[2]].copy()

    return VisiblePartImage



def ExtractSelectedRegion(Canvas, Selected_BB, Selected_Mask, layer_nos):
    # Bounding box of the region
    [x, y, w, h] = Selected_BB

    # Sorting the layer numbers in increasing order
    if layer_nos.count(-1) != 0:
        layer_nos = [i for i in range(len(Canvas.layers))]
    layer_nos = sorted(layer_nos)

    # Selected region combined image
    Selected_Image = np.zeros((h, w, 4), dtype=np.uint8)

    for layer_no in layer_nos:
        # Intersecting rectangle
        # IntRect is the coordinates of intersecting rectange wrt the canvas
        IntRect = hf.Intersection(Selected_BB, Canvas.layers[layer_no].Position + list(Canvas.layers[layer_no].Shape)[::-1])
        if IntRect is None:         # If no intersecting part
            continue
        # Converting IntRect to wrt image and wrt selected region
        IntRect_Image = [IntRect[0] - Canvas.layers[layer_no].Position[0],
                         IntRect[1] - Canvas.layers[layer_no].Position[1],
                         IntRect[2], IntRect[3]]
        IntRect_Region = [IntRect[0] - Selected_BB[0], IntRect[1] - Selected_BB[1],
                          IntRect[2], IntRect[3]]
        _x, _y, _w, _h = IntRect_Region

        # Cropping out layer's image
        LayerImg = Canvas.layers[layer_no].Image[IntRect_Image[1] : IntRect_Image[1]+IntRect_Image[3], 
                                                 IntRect_Image[0] : IntRect_Image[0]+IntRect_Image[2]].copy()

        # Adding these layer images to the selected image
        alpha = LayerImg[:, :, [-1]].astype(float)/255
        alpha = cv2.merge((alpha, alpha, alpha))
        Selected_Image[_y:_y+_h, _x:_x+_w, :-1] = cv2.add(cv2.multiply(alpha, LayerImg[:, :, :-1], dtype=cv2.CV_64F),
                                                          cv2.multiply(1.0 - alpha, Selected_Image[_y:_y+_h, _x:_x+_w, :-1], dtype=cv2.CV_64F))
        Selected_Image[_y:_y+_h, _x:_x+_w, -1] = cv2.max(LayerImg[:, :, [-1]], Selected_Image[_y:_y+_h, _x:_x+_w, [-1]])

        # Masking the part of image invisible that was not in the selected region mask
        Selected_Image[:, :, -1] = cv2.bitwise_and(Selected_Image[:, :, [-1]], Selected_Mask)

    # Crop the visible part of the selected image (alpha > 0)
    Selected_Image = CropVisible(Selected_Image)
    if Selected_Image is None:
        print("\nSelected region is empty. No new layer creared.")
        return

    # Add the new layer of the selected region
    Canvas.AddLayer(Selected_Image, Index=(layer_nos[-1]+1))


####################################################### Rectangular Marquee Tool ##############################################################################

def CallBackFunc_RectMarqueeTool(event, x, y, flags, params):
    # Taking global params
    global selecting, isSelected, CombinedFrame, FrameToShow, CanvasShape, X1_, Y1_, X2_, Y2_

    # If while selecting the region, mouse goes out of the frame, then clip it position 
    # to the nearest corner/edge of the frame
    if selecting:
        x, y = hf.Correct_xy_While_Selecting(x, y, [0, CanvasShape[1]-1], [0, CanvasShape[0]-1])
    
    
    # Starts selecting - Left button is pressed down
    if event == cv2.EVENT_LBUTTONDOWN:
        selecting = True
        isSelected = False
        X1_, Y1_ = x, y

    # Selecting the region
    elif event == cv2.EVENT_MOUSEMOVE:
        if selecting:
            FrameToShow = CombinedFrame.copy()
            cv2.rectangle(FrameToShow, (X1_, Y1_), (x, y), (127, 127, 127), 1)

    # Stop selecting the layer.
    elif event == cv2.EVENT_LBUTTONUP:
        FrameToShow = CombinedFrame.copy()
        cv2.rectangle(FrameToShow, (X1_, Y1_), (x, y), (127, 127, 127), 1)
        selecting = False
        X2_, Y2_ = x, y
        if not (X1_ == X2_ and Y1_ == Y2_):
            isSelected = True



def RectangularMarqueeTool(Canvas, window_title):
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
    cv2.setMouseCallback(window_title, CallBackFunc_RectMarqueeTool)

    # Setting some params used in callback function
    global selecting, isSelected, CombinedFrame, FrameToShow, CanvasShape, X1_, Y1_, X2_, Y2_
    selecting = False       # True if region is being selected      
    isSelected = False      # True if region is selected
    Canvas.CombineLayers()
    CombinedFrame = Canvas.CombinedImage.copy()     # the combined frame of the canvas
    FrameToShow = CombinedFrame.copy()              # The frame which will be shown (with the selected region)
    CanvasShape = Canvas.Shape                      # Shape of the canvas
    X1_, Y1_, X2_, Y2_ = 0, 0, 0, 0                 # Selected rectangle position of top left and bottom right corner

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
                Y1_ -= 1
                Y2_ -= 1
            if Key == 65 or Key == 97:      # If 'A'/'a' - move left
                X1_ -= 1
                X2_ -= 1
            if Key == 83 or Key == 115:     # If 'S'/'s' - move down
                Y1_ += 1
                Y2_ += 1
            if Key == 68 or Key == 100:     # If 'D'/'d' - move right
                X1_ += 1
                X2_ += 1
            
            FrameToShow = CombinedFrame.copy()
            cv2.rectangle(FrameToShow, (X1_, Y1_), (X2_, Y2_), (127, 127, 127), 1)
            

    if not IsAborted:
        # Correcting rectangular's points
        X1_, Y1_, X2_, Y2_ = hf.CorrectRectPoints(X1_, Y1_, X2_, Y2_)
        Selected_BB = [X1_, Y1_, (X2_-X1_+1), (Y2_-Y1_+1)]
        Selected_Mask = np.ones((Selected_BB[3], Selected_BB[2], 1), dtype=np.uint8)
        ExtractSelectedRegion(Canvas, Selected_BB, Selected_Mask, layer_nos_to_copy)
    
    else:
        print("\nRegion selection aborted.")


###############################################################################################################################################################
