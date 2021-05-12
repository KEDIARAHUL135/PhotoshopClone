import os
import cv2
import time
import numpy as np


def Get_Img_Canvas_ROI(ImageRect, CanvasShape):
    # Position of image on the canvas
    [i_pos_x, i_pos_y, i_pos_w, i_pos_h] = ImageRect
    # Canvas roi (place where image is present on the canvas)
    [c_roi_x, c_roi_y, c_roi_w, c_roi_h] = ImageRect
    # Coordinates of part of the image present inside the frame
    [i_roi_x, i_roi_y, i_roi_w, i_roi_h] = [0, 0, i_pos_w, i_pos_h]

    if i_pos_x < 0:                                 # If image is over left boundary
        if abs(i_pos_x) < i_pos_w:                  # If not completely over left boundary
            i_roi_x = -i_pos_x
            i_roi_w += i_pos_x
            c_roi_x = 0
            c_roi_w += i_pos_x
        
        else:                                       # If completely over left boundary
            return None, None
    
    if i_pos_y < 0:                                 # If image is over top boundary
        if abs(i_pos_y) < i_pos_h:                  # If not completely over top boundary
            i_roi_y = -i_pos_y
            i_roi_h += i_pos_y
            c_roi_y = 0
            c_roi_h += i_pos_y
        
        else:                                       # If completely over top boundary
            return None, None

    if i_pos_x + i_pos_w > CanvasShape[1]:          # If image is over right boundary
        if i_pos_x < CanvasShape[1]:                # If not completely over right boundary
            c_roi_w = CanvasShape[1] - c_roi_x
            i_roi_w -= (i_pos_x + i_pos_w - CanvasShape[1])
        
        else:                                       # If completely over right boundary
            return None, None
    
    if i_pos_y + i_pos_h > CanvasShape[0]:          # If image is over bottom boundary
        if i_pos_y < CanvasShape[0]:                # If not completely over bottom boundary
            c_roi_h = CanvasShape[0] - c_roi_y
            i_roi_h -= (i_pos_y + i_pos_h - CanvasShape[0])

        else:                                       # If completely over bottom boundary
            return None, None
    
    
    return [i_roi_x, i_roi_y, i_roi_w, i_roi_h], [c_roi_x, c_roi_y, c_roi_w, c_roi_h]



def Clear():
    # for windows
    if os.name == 'nt':
        _ = os.system('cls')

    # for mac and linux(here, os.name is 'posix')
    else:
        _ = os.system('clear')

def Sleep(Duration=1):
    time.sleep(Duration)


def to_xyxy(x, y, w, h):
    x2 = x + w - 1
    y2 = y + h - 1

    return x2, y2


def to_xywh(x1, y1, x2, y2):
    w = x2 - x1 + 1
    h = y2 - y1 + 1

    return w, h


def EmptyCallBackFunc(event, x, y, flags, Canvas):
    pass


def Correct_xy_While_Selecting(x, y, x_range, y_range):
    if x < x_range[0]:
        x = x_range[0]
    elif x > x_range[1]:
        x = x_range[1]
    
    if y < y_range[0]:
        y = y_range[0]
    elif y > y_range[1]:
        y = y_range[1]

    return x, y


def CorrectRectPoints(x1, y1, x2, y2):
    return min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)


def Intersection(Rect1, Rect2):
    x = max(Rect1[0], Rect2[0])
    y = max(Rect1[1], Rect2[1])
    w = min(Rect1[0] + Rect1[2], Rect2[0] + Rect2[2]) - x
    h = min(Rect1[1] + Rect1[3], Rect2[1] + Rect2[3]) - y
    
    if w < 0 or h < 0: 
        return None
    return [x, y, w, h]


def Union(Rect1, Rect2):
  x = min(Rect1[0], Rect2[0])
  y = min(Rect1[1], Rect2[1])
  w = max(Rect1[0] + Rect1[2], Rect2[0] + Rect2[2]) - x
  h = max(Rect1[1] + Rect1[3], Rect2[1] + Rect2[3]) - y
  return (x, y, w, h)


def ShiftContour(Contour, ToOrigin=True, ShiftBy=[0, 0], Get_Mask_BB=False):
    # Getting the bounding rectangle of the contour.
    (x, y, w, h) = cv2.boundingRect(np.array(Contour))

    # If shift contour to origin, we will have to shift it by the 
    # value equal to its bounding box's top left coorner coordinate
    if ToOrigin:
        ShiftBy = [-x, -y]

    # Shifting the contour
    ShiftedContour = []
    for i in range(len(Contour)):
        ShiftedContour.append([[(Contour[i][0][0] + ShiftBy[0]), (Contour[i][0][1] + ShiftBy[1])]])


    # If bounding box and mask image are asked
    if Get_Mask_BB:
        # Creating the mask image
        MaskImage = np.zeros((h, w, 1), dtype=np.uint8)
        cv2.drawContours(MaskImage, [np.array(ShiftedContour)], -1, 255, -1)

        return ShiftedContour, MaskImage, (x, y, w, h)

    # If only shifted contour required
    else:
        return ShiftedContour
