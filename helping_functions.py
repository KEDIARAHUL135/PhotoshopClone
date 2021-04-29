import os
import time


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