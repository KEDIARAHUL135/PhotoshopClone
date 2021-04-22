import image


def AddNewLayer(all_layers):
    print("\nEnter '@' to abort adding of new image.")
        
    while True:
        NewImagePath = input("\nEnter image path: ")

        if '@' in NewImagePath:     # Abort if '@' entered
            print("Aborting adding of image.\n")
            break

        # Reading new image
        NewImage = image.ReadImage(NewImagePath)
        if NewImage is None:        # If image is not found/read
            print("Enter a valid image path...")
            continue

        # Calling function for adding new layer
        all_layers.AddLayer(NewImage)
        print("\nLayer added successfully.")

        break
