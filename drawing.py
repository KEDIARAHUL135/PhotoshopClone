import cv2
import numpy as np

import helping_functions as hf


Len = 6
HorizontalOrientation = -1
VerticalOrientation = -2

# Drawing horizontal line
def HorLine(Image, x1, x2, y):
    # 0 <= x1 <= x2 < Image width
    if x1 > x2: 
        x1, x2 = x2, x1
    x1, x2 = max(0, x1), min(x2, Image.shape[1]-1)

    Last_x = x1         # Last x value
    isWhite = True      # Flag for switching b/w black and white
    for x in range(x1 + Len, x2 + 1, Len):
        if isWhite:
            Image[y, Last_x : x + 1, :] = 255
            isWhite = False
        else:
            Image[y, Last_x : x + 1, :] = 0
            isWhite = True

        Last_x = x
    
    # Drawing the last segment
    if isWhite:
        Image[y, Last_x : x2 + 1, :] = 255
    else:
        Image[y, Last_x : x2 + 1, :] = 0


# Drawing verticle line
def VerLine(Image, x, y1, y2):
    # 0 <= y1 <= y2 < Image height
    if y1 > y2: 
        y1, y2 = y2, y1
    y1, y2 = max(0, y1), min(y2, Image.shape[0]-1)
    
    Last_y = y1         # Last y value
    isWhite = True      # Flag for switching b/w black and white
    for y in range(y1 + Len, y2 + 1, Len):
        if isWhite:
            Image[Last_y : y + 1, x, :] = 255
            isWhite = False
        else:
            Image[Last_y : y + 1, x, :] = 0
            isWhite = True

        Last_y = y

    # Drawing the last segment
    if isWhite:
        Image[Last_y : y2 + 1, x, :] = 255
    else:
        Image[Last_y : y2 + 1, x, :] = 0


# Gets coordinates of all the points on the line
def GetLinePoints(Pt1, Pt2):
    [x, y] = Pt1    # Starting Point

    dist = hf.Distance(Pt1, Pt2)    # Line length
    
    if dist == 0:   # If line length is 0, return no points
        return []
        
    # dx is small increment in x value for each increment of 
    # y value by dy such that the new point still lies on the line.
    # [if (x, y) lies on the line, 
    # then (x + dx, y + dy) also lies on the line]
    dx = (Pt2[0] - Pt1[0]) / dist
    dy = (Pt2[1] - Pt1[1]) / dist

    Points = [[x, y]]

    minX = min(Pt1[0], Pt2[0])
    maxX = max(Pt1[0], Pt2[0])
    minY = min(Pt1[1], Pt2[1])
    maxY = max(Pt1[1], Pt2[1])
    
    # Loop until the new point lies inside the image
    while minX <= x <= maxX and minY <= y <= maxY:
        x += dx
        y += dy
        Pt = [int(x), int(y)]

        if not (Pt[0] == Points[-1][0] and Pt[1] == Points[-1][1]):
            Points.append(Pt)
    
    return Points


# Drawing a line at some angle except 0 or 90.
def LineAtAngle(Image, Pt1, Pt2, isDashed):
    # Getting the line points
    Points = GetLinePoints(Pt1, Pt2)

    if isDashed:
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

    else:
        for Pt in Points:
            Image[Pt[1]][Pt[0]] = [127, 127, 127]
            # if (Image[Pt[1]][Pt[0]] <= 127).all():
            #     Image[Pt[1]][Pt[0]] = [255, 255, 255]
            # else:
            #     Image[Pt[1]][Pt[0]] = [0, 0, 0]


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
        LineAtAngle(Image, Pt1, Pt2, True)
        

# Drawing normal rectangle (sides parallel to axes)
def Rectangle(Image, Pt1, Pt2):
    x1 = min(Pt1[0], Pt2[0])
    x2 = max(Pt1[0], Pt2[0])
    y1 = min(Pt1[1], Pt2[1])
    y2 = max(Pt1[1], Pt2[1])

    if x1 == x2 and y1 == y2:
        return

    # Drawing the 4 lines of the rectangle
    Line(Image, [x1, y1], [x2, y1], HorizontalOrientation)
    Line(Image, [x2, y1], [x2, y2], VerticalOrientation)
    Line(Image, [x2, y2], [x1, y2], HorizontalOrientation)
    Line(Image, [x1, y2], [x1, y1], VerticalOrientation)


#####################################################################################################

# Drawing ellipse
def Ellipse(Image, Center, Axes, Angle, startAngle, endAngle):
    if Axes[0] == 0 and Axes[1] == 0:
        return

    # each segment will make angle theta with the center
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

# Drawing incomplete (open) contour. Instead of dashed lines, 
# colour of each point depends on the image brightness at that point.
def Inc_Contour(Image, Contour):
    # Looping over all points
    for i in range(1, len(Contour)):
        # Extracting the grayscale colour of the point
        ColourVal = Image[Contour[i][1]][Contour[i][0]]

        if ColourVal[0] <= 127 and ColourVal[1] <= 127 and ColourVal[2] <= 127:
            cv2.line(Image, tuple(Contour[i]), tuple(Contour[i-1]), (255, 255, 255), 1)

        else:
            cv2.line(Image, tuple(Contour[i]), tuple(Contour[i-1]), (0, 0, 0), 1)
            

# Drawing complete (closed) contour with dashed lines.
def Com_Contours(Image, Contours):
    for Contour in Contours:    # For each contour
        Sum = 0
        isWhite = True

        # is contour point of the type [x, y] or [[x, y]]
        if len(Contour[0]) == 1:
            isExtraAxis = True
        else:
            isExtraAxis = False

        # Looping on each point of the contour
        for i in range(1, len(Contour)):
            if isExtraAxis:
                x1, y1 = Contour[i-1][0]
                x2, y2 = Contour[i][0]
            else:
                x1, y1 = Contour[i-1]
                x2, y2 = Contour[i]

            # Distance between two consecutive points of the contour
            dist = hf.Distance([x1, y1], [x2, y2])

            # Connecting these points with a line
            if isWhite:
                cv2.line(Image, (x1, y1), (x2, y2), (255, 255, 255), 1)
            else:
                cv2.line(Image, (x1, y1), (x2, y2), (0, 0, 0), 1)

            # Checking if part length exceeded. If yes, then switch colour.
            Sum += dist
            if Sum > Len:
                isWhite = not isWhite
                Sum = 0
            
        # Joining the first and last points
        if isExtraAxis:
            x1, y1 = Contour[0][0]
            x2, y2 = Contour[-1][0]
        else:
            x1, y1 = Contour[0]
            x2, y2 = Contour[-1]

        LineAtAngle(Image, [x1, y1], [x2, y2], True)
