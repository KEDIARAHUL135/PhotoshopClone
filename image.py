import os
import cv2
import numpy as np

import macros as m


# Adds alpha channel to the image
def AddAlphaChannel(Image, mask=None):
    if mask is None:        # If mask is not provided
        MaskImage = np.ones((Image.shape[:2]), dtype=np.uint8) * 255
    
    else:                   # If mask is provided
        Height_Image, Width_Image = Image.shape[:2]
        Height_Mask, Width_Mask = mask.shape[:2]
        
        # Checking the size of mask
        if Height_Image == Height_Mask and Width_Image == Width_Mask:
            MaskImage = mask
        else:
            MaskImage = np.ones((Image.shape[:2]), dtype=np.uint8) * 255

    # Adding the alpha channel to the image
    b, g, r = cv2.split(Image)
    Image = cv2.merge((b, g, r, MaskImage))

    return Image


# Corrects the iamge dimentions.
# The image should be 4 channeled
def CorrectImage(Image):
    Channels = Image.shape[2]

    if Channels == 4:   # If image is 4-channeled - do nothing
        return Image
    
    elif Channels == 3: # If image is 3-channeled - add alpha channel
        Image = AddAlphaChannel(Image)

    elif Channels == 1: # If image is 1-channeled - convert to bgr and add alpha channel
        Image = cv2.cvtColor(Image, cv2.COLOR_GRAY2BGR)
        Image = AddAlphaChannel(Image)

    else:
        print("The Image cannot be corrected.")

    return Image
    


# Reads the image from the path given
def ReadImage(ImagePath):
    # If the file doesnot exists or is not a file
    if not os.path.exists(ImagePath) or not os.path.isfile(ImagePath):
        return None

    Image = cv2.imread(ImagePath, cv2.IMREAD_UNCHANGED)

    # If Image is not read properly
    if Image is None:
        return None
    if Image.size == 0:
        return None

    # Correcting the image if necessary
    Image = CorrectImage(Image)

    return Image


def CreateBackgroundImage(Shape):
    h, w = Shape

    # Creating the checkered image
    background_img = np.ones((h, w, 3), dtype=np.uint8) * 255

    for i in range(0, h, m.GRID_BOX_SIZE):
        for j in range(0, w, m.GRID_BOX_SIZE):
            if ((i+1) // m.GRID_BOX_SIZE) % 2 == 0:
                if ((j+1) // m.GRID_BOX_SIZE) % 2 != 0:
                    background_img[i:i+m.GRID_BOX_SIZE, j:j +
                                   m.GRID_BOX_SIZE] = [200, 200, 200]
            else:
                if ((j+1) // m.GRID_BOX_SIZE) % 2 == 0:
                    background_img[i:i+m.GRID_BOX_SIZE, j:j +
                                   m.GRID_BOX_SIZE] = [200, 200, 200]

    # Adding the alpha channel
    ## The alpha channel in the base image is of no importance but 
    ## we will have to create it as the layers should have the alpha channel
    background_img = CorrectImage(background_img)

    return background_img

