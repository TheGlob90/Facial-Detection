import PySimpleGUI as sg
import cv2
import numpy as np
import sys
import os
import face_training as ft
import face_rec as fr
import data_collection as dc
import threading
import bluetooth_connection as bc
import time
import json

# Sets the theme for the GUI
sg.theme('SystemDefault')

# addr = "54:43:B2:2B:A3:E2"

# Adds a new face to the facial recgonition
def newFace(face_id, names):
    # Writes the new name to the text file to be loaded on startup
    names.append(face_id)

# Writing to sample.json
def writeJSON(filename, data):
  with open(str(filename), "w") as outfile:
      outfile.write(data)
  outfile.close()

# Defines the layout for our keypad window
keypad_layout = [
            [sg.Input('', size=(10, 1), key='input')],
            [sg.Button('1'), sg.Button('2'), sg.Button('3'), sg.Button('4')],
            [sg.Button('5'), sg.Button('6'), sg.Button('7'), sg.Button('8')],
            [sg.Button('9'), sg.Button('0'), sg.Button('⏎', key='Submit'), sg.Button('Clear')],
            [sg.Text('', size=(15, 1), font=('Helvetica', 18),
                     text_color='red', key='out')],
        ]

# Function each sensor needs to run on for bluetooth connection
def threads(thread_name, window, addr):
    sock = bc.connect(addr)
    while True:
        ret = bc.rx_and_echo(sock)
        if ret == 1:
            window.write_event_value(thread_name, 'ALARM')
        elif ret == 2:
            break
    bc.disconnect(sock)

    print("Thread done \n")

# Runs the keypad once the alarm has been triggered
def keypad_f(code, timeout):
    keypad = sg.Window('ALARM!!', keypad_layout,
                        default_button_element_size=(5, 2),
                        auto_size_buttons=False,
                        grab_anywhere=False)
    count = 0
    keys_entered = ''
    # Loop through until we close the keypad or enter a code
    while count < int(timeout):
            event, values = keypad.read(timeout=10)  # read the form
            count = count + 1
            if event is None:  # if the X button clicked, just exit
                break
            if event == 'Clear':  # clear keys if clear button
                keys_entered = ''
            elif event in '1234567890':
                keys_entered = values['input']  # get what's been entered so far
                keys_entered += event  # add the new digit
            elif event == 'Submit':
                keys_entered = values['input']
                if keys_entered == code:
                    sg.Popup("Deactivated", keep_on_top = True)
                    break
                else:
                    sg.Popup("Wrong code", keep_on_top = True)
                    keys_entered = ''
                # change the form to reflect current key string
            keypad['input'].update(keys_entered)
    keypad.close()

def runSettings():
    #Settings Layout
    settings_layout = [
                    [sg.Text("Welcome to (AI)-larm", size=(60, 1), justification="center")],
                    [sg.Text("We need to run through some settings to get started.", size=(50, 1), justification="center")],
                    [sg.Text('General', size=(30,1), justification="left", font=("bold"))],
                    [sg.HSeparator()],
                    [sg.Text('Please enter a name for this device.'), sg.Push(), sg.InputText(key='DEVICENAME', size=(25,1))],
                    [sg.Text('Security', size=(30,1), justification="left", font=("bold"))],
                    [sg.HSeparator()],
                    [sg.Text('Please enter a deactivation password.'), sg.Push(), sg.InputText(key='CODE', size=(25,1))],
                    [sg.Text('Please enter the timeout time for facial detection. DEFAULT:100'), sg.Push(), sg.InputText(key='TIMEOUT_F', size=(25,1))],
                    [sg.Text('Please enter the timeout time for passcode. DEFAULT:200'), sg.Push(), sg.InputText(key='TIMEOUT_P', size=(25,1))],
                    [sg.Text('Connect', size=(30,1), justification="left", font=("bold"))],
                    [sg.HSeparator()],
                    [sg.Text("Let's add some sensors to the system!", size=(60,1), justification="left")],
                    [sg.Button("Scan for Sensors")],
                    [sg.Listbox("", size=(80,5), key='DEVICES')],
                    [sg.Button("Save Settings"), sg.Button("Exit", size=(10, 1))],                
    ]

    settings = sg.Window("(AI)-larm STARTUP", settings_layout, resizable=True, finalize=True)
    settings.maximize()

    while True:
        event, values = settings.read()  # read the form
        if event == sg.WIN_CLOSED or event == "Exit":  # if the X button clicked, just exit
            break
        if event == "Scan for Sensors":
            scanbt = bc.scan_devices()
            settings['DEVICES'].update((scanbt))

        if event == "Save Settings":
            settings_saved = {
                        "device-name" : values['DEVICENAME'],
                        "code" : values['CODE'],
                        "face-timeout" : values['TIMEOUT_F'],
                        "code-timeout" : values['TIMEOUT_P'],
                        # "sensors" : sensors,
                        # "names" : names
            }
            settings_json = json.dumps(settings_saved, indent=4)
            writeJSON("settings.json", settings_json)
            break
    settings.close()

def main():
    # Reads in the code from the .json file
    with open('settings.json', 'r') as f:
        setting_values = json.load(f)
    names = setting_values['names']

    # Returns the address for the ESP for connection
    alldevices, sensor_addr = bc.scan_devices()
    print(sensor_addr)

    # Define the window layout for the intro screen.
    homescreen = [
        [sg.Text("Welcome to (AI)-larm", size=(60, 1), justification="center")],
        [sg.Button("Exit", size=(10, 1))],

    ]

    #Define the window layout for the settings
    settings = [
        [sg.Text('Enter the ID for the new face to be added.'), sg.InputText()],
                                                                            
        [sg.Text('Enter the name of the person being added.'), sg.InputText()],

        [sg.Button("New Face")], # Button to add a new face to be trained
                
        [sg.Button("Facial Recognition")], # Button to run the facial recognition software

        [sg.Button("Change settings")], # Button used to change code
        
        [sg.Button("EXIT")]] # Button to Exit the GUI from other screen

    # Creates the tabs in the GUI so you can select a different one
    tabgrp = [[sg.TabGroup([[sg.Tab('Welcome', homescreen, title_color='Black', border_width=10,tooltip='Camera', element_justification='center'),
                sg.Tab('Settings', settings, title_color='Black')]])]]

    # Create the window and show it without the plot
    window = sg.Window("Facial Recognition", tabgrp, resizable=True, finalize=True)
    threading.Thread(target=threads, args=('ALARM', window, sensor_addr[0],), daemon=True).start()
    window.Maximize()

    keys_entered = ''
    while True:
        event, values = window.read()

        # TODO: Add in alarm if user fails to deactivate
        if(event == "ALARM"):
            name = fr.main(cascPath, names)
            if name == "unknown":
                keypad_f(setting_values['code'], setting_values['code-timeout'])
            else:
                sg.Popup('Welcome back ' + name, keep_on_top = True)

        # Exit event to close the GUI
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
            # Adds the new face to the settings file
            newFace(face_id, names)
            # Calls the data collection function
            dc.main(face_id, user_name, cascPath)
            # Trains the ML model after taking the images
            ft.main(cascPath)
            # Creates a popup telling the user the face was trained
            sg.Popup('Face added as ID #' + str(face_id) + " and name " + values[1], keep_on_top = True)

        # If the Facial Recognition button is clicked
        if event == "Facial Recognition":
            name = fr.main(cascPath, names, setting_values['face-timeout'])
            if name == "unknown":
                keypad_f(setting_values['code'], setting_values['code-timeout'])
            else:
                sg.Popup('Welcome back ' + name, keep_on_top = True)

        # Allows users to change the settings once the device is running
        if event == "Change settings":
            runSettings()
            # Reads in the code from the .json file
            with open('settings.json', 'r') as f:
                setting_values = json.load(f)

    window.close()

# Reads in the cascade file to be used
cascPath = sys.argv[1]
faceCascade = cv2.CascadeClassifier(cascPath)

# If settings file doesn't exist we need to generate it
if(os.path.isfile('./settings.json') == False):
        runSettings()
main()


print("ENDED")