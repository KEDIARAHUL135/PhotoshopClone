import cv2
import numpy as np

import image


def Initialize(args):
    if args["ImagePath"] is not None:
        Img = image.ReadImage(args["ImagePath"])

        if Img is None:
            print("Provide a correct image path.")
            exit()