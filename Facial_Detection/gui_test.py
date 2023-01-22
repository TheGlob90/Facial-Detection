import PySimpleGUI as sg
import cv2
import numpy as np
import sys
import os
import data_collection as dc
import face_training as ft
import face_rec as fr

def main():

    global numOfFaces
    numOfFaces = 0

    # Define the window layout for the camera
    layout1 = [
        [sg.Text("OpenCV Demo", size=(60, 1), justification="center")],
        [sg.Text("Number of Faces: ", size=(60,1), justification="center", key='text')],
        [sg.Image(filename="", key="-IMAGE-")],
        [sg.Button("Exit", size=(10, 1))],

    ]

    #Define the window layour for the settings
    layout2 = [[sg.Radio("None", "Radio", True, size=(10, 1))],
        # [
        #     sg.Radio("threshold", "Radio", size=(10, 1), key="-THRESH-"),
        #     sg.Slider(
        #         (0, 255),128,1,
        #         orientation="h",
        #         size=(40, 15),
        #         key="-THRESH SLIDER-",
        #     ),
        # ],

        # [
        #     sg.Radio("canny", "Radio", size=(10, 1), key="-CANNY-"),
        #     sg.Slider(
        #         (0, 255),
        #         128,
        #         1,
        #         orientation="h",
        #         size=(20, 15),
        #         key="-CANNY SLIDER A-",
        #     ),
        #     sg.Slider(
        #         (0, 255),
        #         128,
        #         1,
        #         orientation="h",
        #         size=(20, 15),
        #         key="-CANNY SLIDER B-",
        #     ),
        # ],
        # [

        #     sg.Radio("blur", "Radio", size=(10, 1), key="-BLUR-"),
        #     sg.Slider(
        #         (1, 11),
        #         1,
        #         1,
        #         orientation="h",
        #         size=(40, 15),
        #         key="-BLUR SLIDER-",
        #     ),
        # ],
        # [

        #     sg.Radio("hue", "Radio", size=(10, 1), key="-HUE-"),
        #     sg.Slider(
        #         (0, 225),
        #         0,
        #         1,
        #         orientation="h",
        #         size=(40, 15),
        #         key="-HUE SLIDER-",
        #     ),
        # ],
        # [
        #     sg.Radio("enhance", "Radio", size=(10, 1), key="-ENHANCE-"),
        #     sg.Slider(
        #         (1, 255),
        #         128,
        #         1,
        #         orientation="h",
        #         size=(40, 15),
        #         key="-ENHANCE SLIDER-",
        #     ),
        # ], 
        
        [sg.Button("New Face")],
        
        [sg.Button("EXIT")]]

    tabgrp = [[sg.TabGroup([[sg.Tab('Camera', layout1, title_color='Black', border_width=10,tooltip='Camera', element_justification='center'),
                sg.Tab('Settings', layout2, title_color='Black')]])]]

    # Create the window and show it without the plot
    window = sg.Window("Facial Recognition", tabgrp, resizable=True)

    cap = cv2.VideoCapture(0)


    while True:
        event, values = window.read(timeout=20)
        if event == "Exit" or event == sg.WIN_CLOSED or event == "EXIT":
            break

        ret, frame = cap.read()

        if event == "New Face":
            dc.main()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.FONT_HERSHEY_SIMPLEX
        )

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        numOfFaces = len(faces)

        # if values["-THRESH-"]:
        #     frame = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)[:, :, 0]
        #     frame = cv2.threshold(
        #         frame, values["-THRESH SLIDER-"], 255, cv2.THRESH_BINARY
        #     )[1]

        # elif values["-CANNY-"]:
        #     frame = cv2.Canny(
        #         frame, values["-CANNY SLIDER A-"], values["-CANNY SLIDER B-"]
        #     )

        # elif values["-BLUR-"]:
        #     frame = cv2.GaussianBlur(frame, (21, 21), values["-BLUR SLIDER-"])

        # elif values["-HUE-"]:
        #     frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        #     frame[:, :, 0] += int(values["-HUE SLIDER-"])
        #     frame = cv2.cvtColor(frame, cv2.COLOR_HSV2BGR)

        # elif values["-ENHANCE-"]:
        #     enh_val = values["-ENHANCE SLIDER-"] / 40
        #     clahe = cv2.createCLAHE(clipLimit=enh_val, tileGridSize=(8, 8))
        #     lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        #     lab[:, :, 0] = clahe.apply(lab[:, :, 0])
        #     frame = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

        imgbytes = cv2.imencode(".png", frame)[1].tobytes()
        window["-IMAGE-"].update(data=imgbytes)
        window['text'].update("Number of Faces: " + str(numOfFaces))

    window.close()

sg.theme('SystemDefault')
cascPath = sys.argv[1]
faceCascade = cv2.CascadeClassifier(cascPath)
main()