import os
import cv2
import numpy as np

import image
import macros as m



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