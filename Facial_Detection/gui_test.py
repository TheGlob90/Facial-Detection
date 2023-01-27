import PySimpleGUI as sg
import cv2
import numpy as np
import sys
import os
import face_training as ft
import face_rec as fr
import data_collection as dc

def main():

    global numOfFaces
    numOfFaces = 0
    names = []

    # names related to ids: example ==> Brandon: id=1,  etc
    # Used for matching a face to a name
    names_f = open("Names.txt", 'r')
    for line in names_f:
        names.append(line)
    names_f.close()

    # Define the window layout for the intro screen.
    layout1 = [
        [sg.Text("Welcome to (AI)-larm", size=(60, 1), justification="center")],
        [sg.Button("Exit", size=(10, 1))],

    ]

    #Define the window layout for the settings
    layout2 = [
        [sg.Text('Enter the ID for the new face to be added.'), sg.InputText()],
                                                                             
        [sg.Text('Enter the name of the person being added.'), sg.InputText()],

        [sg.Button("New Face")], # Button to add a new face to be trained
                   
        [sg.Button("Facial Recognition")], # Button to run the facial recognition software
        
        [sg.Button("EXIT")]] # Button to Exit the GUI from other screen

    # Creates the tabs in the GUI so you can select a different one
    tabgrp = [[sg.TabGroup([[sg.Tab('Welcome', layout1, title_color='Black', border_width=10,tooltip='Camera', element_justification='center'),
                sg.Tab('Settings', layout2, title_color='Black')]])]]

    # Create the window and show it without the plot
    window = sg.Window("Facial Recognition", tabgrp, resizable=True, scaling = 6)

    # # Video capture used by cv2 to run the camera.
    # cap = cv2.VideoCapture(0)


    while True:
        event, values = window.read(timeout=20)
        if event == "Exit" or event == sg.WIN_CLOSED or event == "EXIT":
            break

        # # Used to access the frames that the camera captures
        # ret, frame = cap.read()

        # New face button is pressed
        if event == "New Face":
            # For each person, enter one numeric face id
            # TODO: Force the model not to start unless they have entered an ID and a name
            # TODO: Don't allow them to write over an ID already used
            face_id = values[0]
            user_name = values[1]
            # Writes the new name to the text file to be loaded on startup
            names_f = open("Names.txt", 'a')
            names_f.write(user_name)
            names_f.close()
            # Calls the data collection function
            dc.main(face_id, user_name, cascPath)
            # Trains the ML model after taking the images
            # TODO: Add in a progress bar for training the model.
            ft.main(cascPath)
             # Creates a popup telling the user the face was trained
            sg.Popup('Face added as ID #' + face_id + " and name " + values[1], keep_on_top = True)

        if event == "Facial Recognition":
            fr.main(cascPath, names)


        # # Converts camera image into grey image to be used for facial detection
        # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # # List that holds all of the faces detected within a frame
        # faces = faceCascade.detectMultiScale(
        #     gray,
        #     scaleFactor=1.1,
        #     minNeighbors=5,
        #     minSize=(30, 30),
        #     flags=cv2.FONT_HERSHEY_SIMPLEX
        # )

        # # Draw a rectangle around each face found in the frame at a time
        # for (x, y, w, h) in faces:
        #     cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        # numOfFaces = len(faces)

        # imgbytes = cv2.imencode(".png", frame)[1].tobytes()
        # window["-IMAGE-"].update(data=imgbytes)
        # window['text'].update("Number of Faces: " + str(numOfFaces))

    window.close()

sg.theme('SystemDefault')
cascPath = sys.argv[1]
faceCascade = cv2.CascadeClassifier(cascPath)
main()