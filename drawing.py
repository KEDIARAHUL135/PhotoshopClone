import cv2
import numpy as np

Len = 6
HorizontalOrientation = -1
VerticalOrientation = -2

# Drawing horizontal line
def HorLine(Image, x1, x2, y):
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


# Drawing line (currently only horizontal and verticle lines are supported)
def Line(Image, Pt1, Pt2, Orientation):
    if Orientation == HorizontalOrientation:
        if Pt1[0] > Pt2[0]:
            Pt1[0], Pt2[0] = Pt2[0], Pt1[0]
        HorLine(Image, min(Pt1[0], Pt2[0]), max(Pt1[0], Pt2[0]), Pt1[1])
    
    elif Orientation == VerticalOrientation:
        if Pt1[1] > Pt2[1]:
            Pt1[1], Pt2[1] = Pt2[1], Pt1[1]
        VerLine(Image, Pt1[0], min(Pt1[1], Pt2[1]), max(Pt1[1], Pt2[1]))
        

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
