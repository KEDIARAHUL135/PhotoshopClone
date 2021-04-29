import os
import cv2
import numpy as np

import image
import macros as m
import helping_functions as hf



# This class contains the details and objects about a single layer only
class _layer:
    def __init__(self, Image, IsVisible=True, Position=[0, 0], Name=None):
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


    def Copy(self):
        Layer_copy = _layer(self.Image.copy(), IsVisible=self.IsVisible, 
                            Position=self.Position.copy(),
                            Name=''.join(self.Name))

        return Layer_copy


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
        self.CombinedImage = self.BackgroundImg.copy()

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


    def PrintLayerNames(self):
        # Print layer names except backgroud layer name.
        print("\nLayers present are:")
        for i in range(len(self.layers)):
            print("{} : {}".format(i, self.layers[i].Name))

    
    def Copy(self, copyTo=None):
        if copyTo is None:
            all_layers_copy = _connectedLayers(shape=self.Shape)
        else:
            all_layers_copy = copyTo

        all_layers_copy.layers = [self.layers[i].Copy() for i in range(len(self.layers))]


        # Copying all other data of all_layers
        all_layers_copy.BackgroundImg = self.BackgroundImg.copy()     # Images can be copied like this
        all_layers_copy.Shape = self.Shape + tuple()
        all_layers_copy.CombinedImage = self.CombinedImage.copy()
        
        return all_layers_copy

    def SetLayersVisibility(self, layer_nos):
        # If -1 entered - Show all layers
        if layer_nos.count(-1) != 0:
            for i in range(len(self.layers)):
                self.layers[i].IsVisible = True

        # If -2 entered - Show no layer
        elif layer_nos.count(-2) != 0:  
            for i in range(len(self.layers)):
                self.layers[i].IsVisible = False
        
        # If valid layer numbers passed, show them
        else:
            for layer_no in range(len(self.layers)):
                if layer_nos.count(layer_no):
                    self.layers[layer_no].IsVisible = True
                else:
                    self.layers[layer_no].IsVisible = False


    def DeleteLayers(self, layer_nos):
        # Sorting layer_nos in decreasing order
        layer_nos = sorted(layer_nos, reverse=True)

        # Deleting the layers
        for layer_no in layer_nos:
            del self.layers[layer_no]


    def ExchangeLayers(self, l1, l2):
        self.layers[l1], self.layers[l2] = self.layers[l2], self.layers[l1]


    def MergeLayers(self, layer_nos):
        # Storting layer numbers in increasing order
        layer_nos = sorted(layer_nos)
        # Merged layer will be stored in place of the top-most 
        # layer's pos among the layers which are being merged.
        merged_layer_no = layer_nos[-1]
        
        # Getting Merged layer name. (Merged: l1_name + l2_name + ....)
        merged_layer_name = "Merged: "
        for i in layer_nos:
            merged_layer_name = merged_layer_name + self.layers[i].Name + " + "
        merged_layer_name = merged_layer_name[:-3]      # Removing last " + "


        # Joining/Merging all images and getting merged image position.
        merged_img, merged_img_pos, merged_img_shape = JoinImages([self.layers[i].Image.copy() for i in layer_nos], 
                                                                  [self.layers[i].Position for i in layer_nos],
                                                                  [self.layers[i].Shape for i in layer_nos])

        # Storing merged layers data.
        self.layers[merged_layer_no].Image = merged_img
        self.layers[merged_layer_no].IsVisible = True
        self.layers[merged_layer_no].Position = merged_img_pos
        self.layers[merged_layer_no].Shape = merged_img_shape
        self.layers[merged_layer_no].Name = merged_layer_name
        
        # Deleting all the remaining layers.
        self.DeleteLayers(layer_nos[:-1])


    def RenameLayer(self, layer_no, rename_to):
        # Renaming the layer.
        self.layers[layer_no].Name = rename_to



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
        FirstLayer = _layer(Img, Name="Layer 0", Position=[0, 0])
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


def JoinImages(Images, ImagePositions, ImageShapes):
    x1, y1, = np.transpose(np.asarray(ImagePositions))
    h, w = np.transpose(np.asarray(ImageShapes))

    # Join images and create a single big image.

    # Convert image position format - [x, y, w, h] -> [x1, y1, x2, y2]
    x2, y2 = hf.to_xyxy(x1, y1, w, h)

    # Storing the initial image and its position
    joined_img = Images[0]
    joined_img_pos1 = [x1[0], y1[0]]
    joined_img_pos2 = [x2[0], y2[0]]

    for i in range(1, len(Images)):
        # [x1_, y1_, x2_, y2_] - Position of combined big image in the canvas
        x1_ = min(joined_img_pos1[0], x1[i])
        y1_ = min(joined_img_pos1[1], y1[i])
        x2_ = max(joined_img_pos2[0], x2[i])
        y2_ = max(joined_img_pos2[1], y2[i])


        # Relative positions of both the images wrt the combined image - rel_i1_posi, rel_i2_posi
        ri1x1, ri1y1 = joined_img_pos1[0] - x1_, joined_img_pos1[1] - y1_
        ri1x2, ri1y2 = joined_img_pos2[0] - x1_, joined_img_pos2[1] - y1_
        ri2x1, ri2y1 = x1[i] - x1_, y1[i] - y1_
        ri2x2, ri2y2 = x2[i] - x1_, y2[i] - y1_

        # Combining both images to the joined image.
        new_img = np.zeros((y2_ - y1_ + 1, x2_ - x1_ + 1, 4), dtype=np.uint8)
        # First image (lower image) is added directly
        new_img[ri1y1 : ri1y2 + 1, ri1x1 : ri1x2 + 1] = joined_img.copy()
        # Second image (upper image) is added wrt the alpha channel
        alpha = Images[i][:, :, [-1]].astype(float)/255
        alpha = cv2.merge((alpha, alpha, alpha))
        new_img[ri2y1 : ri2y2 + 1, ri2x1 : ri2x2 + 1, :-1] = \
                                            cv2.add(cv2.multiply(alpha, Images[i][:, :, :-1], dtype=cv2.CV_64F),
                                                    cv2.multiply(1.0 - alpha, new_img[ri2y1 : ri2y2 + 1, 
                                                                                      ri2x1 : ri2x2 + 1, :-1], 
                                                                 dtype=cv2.CV_64F))
        new_img[ri2y1 : ri2y2 + 1, ri2x1 : ri2x2 + 1, -1] = cv2.max(Images[i][:, :, [-1]], new_img[ri2y1 : ri2y2 + 1, ri2x1 : ri2x2 + 1, [-1]])

        # For next iteration, first image = current combined image.
        joined_img_pos1 = [x1_, y1_]
        joined_img_pos2 = [x2_, y2_]
        joined_img = new_img.copy()

    # Convert image position back to previous format
    ji_x1, ji_y1 = joined_img_pos1[0], joined_img_pos1[1]
    ji_w, ji_h = hf.to_xywh(ji_x1, ji_y1, joined_img_pos2[0], joined_img_pos2[1])

    return joined_img, [ji_x1, ji_y1], [ji_h, ji_w]

