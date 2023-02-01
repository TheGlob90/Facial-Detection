import PySimpleGUI as sg
import cv2
import numpy as np
import sys
import os
import face_training as ft
import face_rec as fr
import data_collection as dc
import threading

def test():
    print("Second thread\n")
    test = 0
    for i in range(10000000):
        test = test + 1
    print("Test = " + str(test) + "\n")
    print("Thread 2 done \n")


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
            face_id = values[0]
            user_name = values[1]
            # Makes sure they have entered in both a name and ID for the user
            if face_id == '' or user_name == '':
                sg.Popup('Add a valid ID or name for the user', keep_on_top = True)
                continue
            # Makes sure the ID isn't already in use
            # Goes based on the idea that Users will give increased IDs and not skip numbers
            # Eg 1, 2, 3, etc 
            if face_id <= str(len(names)):
                sg.Popup('ID already in use', keep_on_top = True)
                continue
            # Writes the new name to the text file to be loaded on startup
            names_f = open("Names.txt", 'a')
            names_f.write(user_name + '\n')
            names_f.close()
            names_f = open("Names.txt", 'r')
            for line in names_f:
                names.append(line)
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
    print("Thread 1 done \n")

sg.theme('SystemDefault')
mainThread = threading.Thread(target=main)
commThread = threading.Thread(target=test)
cascPath = sys.argv[1]
faceCascade = cv2.CascadeClassifier(cascPath)
mainThread.start()
commThread.start()

mainThread.join()
commThread.join()
print("ENDED")