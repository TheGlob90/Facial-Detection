import cv2
import numpy as np
from PIL import Image
import PySimpleGUI as sg
import os


def getImagesAndLabels(path, detector):
    imagePaths = [os.path.join(path,f) for f in os.listdir(path)]     
    faceSamples=[]
    ids = []
    # layout the window
    layout = [[sg.Text('Training facesm, please wait.')],
            [sg.ProgressBar(imagePaths, orientation='h', size=(20, 20), key='progressbar')],
            [sg.Cancel()]]
    # create the window`
    window = sg.Window('Custom Progress Meter', layout, modal = True)
    progress_bar = window['progressbar']
    # Initialize individual sampling face count
    count = 0
    for imagePath in imagePaths:
        # Keeps the quality of life files from being used during training
        if (imagePath == 'dataset\\.gitignore') or (imagePath == 'dataset/.gitignore') or (imagePath == 'dataset/representations_vgg_face.pkl') or (imagePath == 'dataset\\representations_vgg_face.pkl'):
            continue
        PIL_img = Image.open(imagePath).convert('L') # grayscale
        img_numpy = np.array(PIL_img,'uint8')
        id = int(os.path.split(imagePath)[-1].split(".")[1])
        faces = detector.detectMultiScale(img_numpy)
        for (x,y,w,h) in faces:
            faceSamples.append(img_numpy[y:y+h,x:x+w])
            ids.append(id)
        count = count + 1
        progress_bar.UpdateBar(count)
    return faceSamples,ids

def main(cascade):
    detector = cv2.CascadeClassifier(cascade)
    # Path for face image database
    path = 'dataset'
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    # function to get the images and label data
    print ("\n [INFO] Training faces. It will take a few seconds. Wait ...")
    faces,ids = getImagesAndLabels(path, detector)
    recognizer.train(faces, np.array(ids))
    # Save the model into trainer/trainer.yml
    recognizer.write('trainer/trainer.yml') 
    # Print the numer of faces trained and end program
    print("\n [INFO] {0} faces trained. Exiting Program".format(len(np.unique(ids))))