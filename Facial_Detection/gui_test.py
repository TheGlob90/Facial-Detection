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

        [sg.Button("Keypad")],
        
        [sg.Button("EXIT")]] # Button to Exit the GUI from other screen

    # Creates the tabs in the GUI so you can select a different one
    tabgrp = [[sg.TabGroup([[sg.Tab('Welcome', layout1, title_color='Black', border_width=10,tooltip='Camera', element_justification='center'),
                sg.Tab('Settings', layout2, title_color='Black')]])]]

    # Create the window and show it without the plot
    window = sg.Window("Facial Recognition", tabgrp, resizable=True).Finalize()

    keys_entered = ''
    while True:
        event, values = window.read(timeout=20)
        if event == "Exit" or event == sg.WIN_CLOSED or event == "EXIT":
            break

        # New face button is pressed
        if event == "New Face":
            # For each person, enter one numeric face id
            face_id = values[0]
            user_name = values[1]
            # Makes sure they have entered in both a name and ID for the user
            if face_id == '' or user_name == '' or face_id.isnumeric() == False:
                sg.Popup('Add a valid ID or name for the user', keep_on_top = True)
                continue
            # Makes sure the ID isn't already in use
            # Goes based on the idea that Users will give increased IDs and not skip numbers
            # Eg 1, 2, 3, etc 
            if int(face_id) <= len(names) and not(names[int(face_id) - 1] == '\n'):
                sg.Popup('ID already in use', keep_on_top = True)
                continue
            # Writes the new name to the text file to be loaded on startup
            # Takes care of the name if it is the first ID
            if int(face_id) == 1:
                names_f = open("Names.txt", 'a')
                names_f.seek(0,0)
                names_f.write(user_name)
                names_f.close()
                names_f = open("Names.txt", 'r')
                last_line = names_f.readlines()[-1]
                names.append(last_line)
                names_f.close()
            # Adding an ID back on the end
            elif int(face_id) > len(names):
                names_f = open("Names.txt", 'a')
                names_f.write('\n' + user_name)
                names_f.close()
                names_f = open("Names.txt", 'r')
                last_line = names_f.readlines()[-1]
                names.append(last_line)
                names_f.close()
            # If an ID gets removed and we want to overwite the now empty spot
            elif names[int(face_id) - 1] == '\n':
                file_contents = []
                with open('Names.txt', 'r') as names_f:
                    file_contents = names_f.readlines()
                names_f.close()
                user_name += '\n'
                file_contents[int(face_id) - 1] = user_name
                with open('Names.txt', 'w') as names_f:
                    names_f.writelines(file_contents)
                names_f.close()
                # Data collection can't handle having the '\n' character so it must be removed
                user_name = user_name.replace('\n', '')
                names[int(face_id) - 1] = user_name
            # Calls the data collection function
            dc.main(face_id, user_name, cascPath)
            # Trains the ML model after taking the images
            ft.main(cascPath)
             # Creates a popup telling the user the face was trained
            sg.Popup('Face added as ID #' + str(face_id) + " and name " + values[1], keep_on_top = True)

        # If the Facial Recognition button is clicked
        if event == "Facial Recognition":
            name = fr.main(cascPath, names)
            sg.Popup('Welcome back ' + name, keep_on_top = True)

        # Used for showing us the keypad
        # Needs to stay within the while loop or it will break
        keypad_layout = [
            [sg.Input('', size=(10, 1), key='input')],
            [sg.Button('1'), sg.Button('2'), sg.Button('3'), sg.Button('4')],
            [sg.Button('5'), sg.Button('6'), sg.Button('7'), sg.Button('8')],
            [sg.Button('9'), sg.Button('0'), sg.Button('⏎', key='Submit'), sg.Button('Clear')],
            [sg.Text('', size=(15, 1), font=('Helvetica', 18),
                     text_color='red', key='out')],
        ]

        # If the keypad button is pressed
        if event == "Keypad":
            keypad = sg.Window('Keypad', keypad_layout,
                        default_button_element_size=(5, 2),
                        auto_size_buttons=False,
                        grab_anywhere=False)
            # Loop through until we close the keypad or enter a code
            while True:
                event, values = keypad.read()  # read the form
                if event is None:  # if the X button clicked, just exit
                    break
                if event == 'Clear':  # clear keys if clear button
                    keys_entered = ''
                elif event in '1234567890':
                    keys_entered = values['input']  # get what's been entered so far
                    keys_entered += event  # add the new digit
                elif event == 'Submit':
                    keys_entered = values['input']
                    break
                # change the form to reflect current key string
                keypad['input'].update(keys_entered)
            keypad.close()
            sg.Popup("Code entered: " + keys_entered, keep_on_top = True)

    window.close()
    print("Thread 1 done \n")

# Sets the theme for the GUI
sg.theme('SystemDefault')

# Creates the threads that are used
mainThread = threading.Thread(target=main)
commThread = threading.Thread(target=test)

# Reads in the cascade file to be used
cascPath = sys.argv[1]
faceCascade = cv2.CascadeClassifier(cascPath)

# Starts the two threads
mainThread.start()
commThread.start()

# Joins the threads once they finish
mainThread.join()
commThread.join()

print("ENDED")