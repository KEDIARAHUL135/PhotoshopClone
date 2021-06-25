import cv2
import numpy as np

import helping_functions as hf


Len = 6
HorizontalOrientation = -1
VerticalOrientation = -2

# Drawing horizontal line
def HorLine(Image, x1, x2, y):
    if x1 > x2: 
        x1, x2 = x2, x1
    x1, x2 = max(0, x1), min(x2, Image.shape[1]-1)

    Last_x = x1
    isWhite = True
    for x in range(x1 + Len, x2 + 1, Len):
        if isWhite:
            Image[y, Last_x : x + 1, :] = 255
            isWhite = False
        else:
            Image[y, Last_x : x + 1, :] = 0
            isWhite = True

        Last_x = x
    
    if isWhite:
        Image[y, Last_x : x2 + 1, :] = 255
    else:
        Image[y, Last_x : x2 + 1, :] = 0


# Drawing verticle line
def VerLine(Image, x, y1, y2):
    if y1 > y2: 
        y1, y2 = y2, y1
    y1, y2 = max(0, y1), min(y2, Image.shape[0]-1)
    
    Last_y = y1
    isWhite = True
    for y in range(y1 + Len, y2 + 1, Len):
        if isWhite:
            Image[Last_y : y + 1, x, :] = 255
            isWhite = False
        else:
            Image[Last_y : y + 1, x, :] = 0
            isWhite = True

        Last_y = y

    if isWhite:
        Image[Last_y : y2 + 1, x, :] = 255
    else:
        Image[Last_y : y2 + 1, x, :] = 0


def GetLinePoints(Pt1, Pt2):
    [x, y] = Pt1

    dist = hf.Distance(Pt1, Pt2)
    dx = (Pt2[0] - Pt1[0]) / (3 * dist)
    dy = (Pt2[1] - Pt1[1]) / (3 * dist)

    Points = [[x, y]]
    while min(Pt1[0], Pt2[0]) <= x <= max(Pt1[0], Pt2[0]) and min(Pt1[1], Pt2[1]) <= y <= max(Pt1[1], Pt2[1]):
        x += dx
        y += dy
        Pt = [int(x), int(y)]

        if Pt != Points[-1]:
            Points.append(Pt)
    
    return Points


# Drawing a line at some angle except 0 or 90.
def LineAtAngle(Image, Pt1, Pt2):
    # Getting the line points
    Points = GetLinePoints(Pt1, Pt2)

    # Drawing dashed line
    isWhite = True
    for i in range(0, len(Points), Len):
        for j in range(i, Len+i):
            try:    # Index out of range error for j = len(Points)
                if isWhite:
                    Image[Points[j][1]][Points[j][0]] = [255, 255, 255]
                else:
                    Image[Points[j][1]][Points[j][0]] = [0, 0, 0]
            except:
                pass
        
        # Switching colour
        isWhite = not isWhite


# Drawing line (currently only horizontal and verticle lines are supported)
def Line(Image, Pt1, Pt2, Orientation=0):
    # Horizontal Line
    if Orientation == HorizontalOrientation:
        if Pt1[0] > Pt2[0]:
            Pt1[0], Pt2[0] = Pt2[0], Pt1[0]
        HorLine(Image, min(Pt1[0], Pt2[0]), max(Pt1[0], Pt2[0]), Pt1[1])
    
    # Vertical Line
    elif Orientation == VerticalOrientation:
        if Pt1[1] > Pt2[1]:
            Pt1[1], Pt2[1] = Pt2[1], Pt1[1]
        VerLine(Image, Pt1[0], min(Pt1[1], Pt2[1]), max(Pt1[1], Pt2[1]))

    # Line at angle
    else:
        LineAtAngle(Image, Pt1, Pt2)
        

# Drawing normal rectangle (sides parallel to axes)
def Rectangle(Image, Pt1, Pt2):
    x1 = min(Pt1[0], Pt2[0])
    x2 = max(Pt1[0], Pt2[0])
    y1 = min(Pt1[1], Pt2[1])
    y2 = max(Pt1[1], Pt2[1])

    if x1 == x2 and y1 == y2:
        return

    Line(Image, [x1, y1], [x2, y1], HorizontalOrientation)
    Line(Image, [x2, y1], [x2, y2], VerticalOrientation)
    Line(Image, [x2, y2], [x1, y2], HorizontalOrientation)
    Line(Image, [x1, y2], [x1, y1], VerticalOrientation)


#####################################################################################################

# Drawing ellipse
def Ellipse(Image, Center, Axes, Angle, startAngle, endAngle):
    if Axes[0] == 0 and Axes[1] == 0:
        return

    theta = int(np.round(np.degrees(((2 * Len) / (Axes[0] + Axes[1])))))

    PartAngles = [i for i in range(0, 360+theta+1, theta)]

    isWhite = True
    for i in range(1, len(PartAngles)):
        if isWhite:
            cv2.ellipse(Image, Center, Axes, Angle, PartAngles[i-1], PartAngles[i], (255, )*Image.shape[-1], 1)
            isWhite = False
        else:
            cv2.ellipse(Image, Center, Axes, Angle, PartAngles[i-1], PartAngles[i], (0, )*Image.shape[-1], 1)
            isWhite = True

#####################################################################################################

def Inc_Contour(Image, Contour):
    # Looping over all points
    for i in range(1, len(Contour)):
        # Extracting the grayscale colour of the point
        ColourVal = Image[Contour[i][1]][Contour[i][0]]

        if ColourVal[0] <= 127 and ColourVal[1] <= 127 and ColourVal[2] <= 127:
            cv2.line(Image, tuple(Contour[i]), tuple(Contour[i-1]), (255, 255, 255), 1)

        else:
            cv2.line(Image, tuple(Contour[i]), tuple(Contour[i-1]), (0, 0, 0), 1)
            

def Com_Contours(Image, Contours):
    for Contour in Contours:
        Sum = 0
        isWhite = True

        for i in range(1, len(Contour)):
            x1, y1 = Contour[i-1]
            x2, y2 = Contour[i]

            dist = hf.Distance([x1, y1], [x2, y2])

            if isWhite:
                cv2.line(Image, (x1, y1), (x2, y2), (255, 255, 255), 1)
            else:
                cv2.line(Image, (x1, y1), (x2, y2), (0, 0, 0), 1)

            Sum += dist
            if Sum > Len:
                isWhite = not isWhite
                Sum = 0
            
        # Joining the first and last points
        x1, y1 = Contour[0]
        x2, y2 = Contour[-1]

        LineAtAngle(Image, [x1, y1], [x2, y2])
