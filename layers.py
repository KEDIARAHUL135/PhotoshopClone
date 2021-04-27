import os
import cv2
import numpy as np

import image
import macros as m
import helping_functions as hf



# This class contains the details and objects about a single layer only
class _layer:
    def __init__(self, Image, IsVisible=True, Position=(0, 0), Name=None):
        self.Image = Image
        self.CheckImage()
        
        self.Shape = Image.shape[:2]
        self.IsVisible = IsVisible
        self.Position = Position
        self.Name = Name
  

    # Checking the image dimentions (should be 4 channeled)
    def CheckImage(self):
        c = self.Image.shape[2]
        if c != 4:
            raise TypeError("Image should be 4 channeled.")



# This class creates the main object of the project will all layers as list
# This class contains the methods for manipulating the different layers together.
class _connectedLayers:
    def __init__(self, **kwargs):
        self.BackgroundImg = None   # Background image will be stored here
        self.layers = []            # All the other layers will be stored in this list

        if "layer" in kwargs:               # If layer is passed
            FirstLayer = kwargs["layer"]    # Getting the first layer
            
            # Storing the background image
            self.BackgroundImg = image.CreateBackgroundImage(FirstLayer.Shape)
            # Adding the first layer
            self.layers.append(FirstLayer)

        # Storing only the background image depending on the shape if passed
        elif "shape" in kwargs:
            self.BackgroundImg = image.CreateBackgroundImage(kwargs["shape"])
        else:
            self.BackgroundImg = image.CreateBackgroundImage([m.DEFAULT_CANVAS_HEIGHT, m.DEFAULT_CANVAS_WIDTH])

        self.Shape = self.BackgroundImg.shape[:2]
    

    def AddLayer(self, Image):
        NewLayer = _layer(Image, Name="Layer " + str(len(self.layers)))
        self.layers.append(NewLayer)


    def CombineLayers(self):
        # Taking the background first
        self.CombinedImage = self.BackgroundImg

        # Combine layers one by one
        for i in range(len(self.layers)):
            # Combining if it is marked visible.
            if self.layers[i].IsVisible:

                # Getting image roi and canvas roi
                Image_ROI, Canvas_ROI = hf.Get_Img_Canvas_ROI(list(self.layers[i].Position) + list(self.layers[i].Shape)[::-1], self.Shape)
                if Image_ROI is None:   # If image completely lies outside the canvas
                    continue
                i_x, i_y, i_w, i_h = Image_ROI
                c_x, c_y, c_w, c_h = Canvas_ROI
                Image_ROI_img = self.layers[i].Image[i_y : i_y + i_h, i_x : i_x + i_w].copy()
                Canvas_ROI_img = self.CombinedImage[c_y : c_y + c_h, c_x : c_x + c_w].copy()

                # Extracting alpha channel, normalising it to range 0-1.
                alpha = Image_ROI_img[:, :, [-1]].astype(float)/255
                # Creating 3 channeled image from alpha channel
                alpha = cv2.merge((alpha, alpha, alpha))

                # Combining layer to the previously combined layers.
                self.CombinedImage[c_y : c_y + c_h, c_x : c_x + c_w] = cv2.add(cv2.multiply(alpha, Image_ROI_img[:, :, :-1], dtype=cv2.CV_64F),
                                                                               cv2.multiply(1.0 - alpha, Canvas_ROI_img, dtype=cv2.CV_64F))

        # Converting it to unsigned int.
        self.CombinedImage = np.uint8(self.CombinedImage)


    def Show(self, Title=m.DEFAULT_CANVAS_TITLE):
        # Checking title type. It should be string.
        if type(Title) != str:
            raise TypeError("Title must be a string.")

        # Combining all layers
        self.CombineLayers()

        # Showing the combined layers.
        cv2.imshow(Title, self.CombinedImage)



# Initializes the project layers
def Initialize(args):
    if args["ImagePath"] is not None:       # If image path is passed
        # Reading the image
        Img = image.ReadImage(args["ImagePath"])
        # If image path is not correct - exit
        if Img is None:
            print("\nProvide a correct image path.\n")
            exit()

        # Creating the first layer and all_layers object
        FirstLayer = _layer(Img, Name="Layer 0", Position=(0, 0))
        all_layers = _connectedLayers(layer=FirstLayer)

    else:
        # If shape is provided, use it, else, take default shape
        if args["Shape"] is not None:   
            Shape = args["Shape"]
        else:
            Shape = [m.DEFAULT_CANVAS_HEIGHT, m.DEFAULT_CANVAS_WIDTH]

        # Creating all_layers object
        all_layers = _connectedLayers(shape=Shape)


    return all_layers