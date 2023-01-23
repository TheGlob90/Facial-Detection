import PySimpleGUI as sg
import cv2
import numpy as np
import sys
import os
import face_training as ft
# import face_rec as fr

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
    layout2 = [
        [sg.Text('Enter the ID for the new face to be added.'), sg.InputText()],
                                                                             
        [sg.Text('Enter the name of the person being added.'), sg.InputText()],

        [sg.Button("New Face")], # Button to add a new face to be trained
        
        [sg.Button("EXIT")]] # Button to Exit the GUI from other screen

    tabgrp = [[sg.TabGroup([[sg.Tab('Camera', layout1, title_color='Black', border_width=10,tooltip='Camera', element_justification='center'),
                sg.Tab('Settings', layout2, title_color='Black')]])]]

    # Create the window and show it without the plot
    window = sg.Window("Facial Recognition", tabgrp, resizable=True)

    # Video capture used by cv2 to run the camera.
    cap = cv2.VideoCapture(0)


    while True:
        event, values = window.read(timeout=20)
        if event == "Exit" or event == sg.WIN_CLOSED or event == "EXIT":
            break

        ret, frame = cap.read()

        # New face button is pressed
        if event == "New Face":
            # For each person, enter one numeric face id
            # face_id = input('\n enter user id end press <return> ==>  ')
            face_id = values[0]
            print("\n [INFO] Initializing face capture. Look the camera and wait ...")
            # Initialize individual sampling face count
            count = 0
            while(True):
                ret, img = cap.read()
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = faceCascade.detectMultiScale(gray, 1.3, 5)
                for (x,y,w,h) in faces:
                    cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)     
                    count += 1
                    # Save the captured image into the datasets folder
                    cv2.imwrite("dataset/User." + str(face_id) + '.' +  
                            str(count) + ".jpg", gray[y:y+h,x:x+w])
                    cv2.imshow('image', img)
                k = cv2.waitKey(100) & 0xff # Press 'ESC' for exiting video
                if k == 27:
                    break
                elif count >= 30: # Take 30 face sample
                    break
            ft.main()# Trains the ML model after taking the images
            sg.Popup('Face added as id #' + face_id + " and name " + values[1], keep_on_top = True) # Creates a popup telling the user the face was trained

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

        imgbytes = cv2.imencode(".png", frame)[1].tobytes()
        window["-IMAGE-"].update(data=imgbytes)
        window['text'].update("Number of Faces: " + str(numOfFaces))

    window.close()

sg.theme('SystemDefault')
cascPath = sys.argv[1]
faceCascade = cv2.CascadeClassifier(cascPath)
main()