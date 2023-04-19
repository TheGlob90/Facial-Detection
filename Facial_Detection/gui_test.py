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
import json
import speaker as sp
import time

# Sets the theme for the GUI
sg.theme('Dark Teal 6')
header=("bold", 25)
default=('Any', 15)
default_set=('Any', 8)


settings_values = {
                        "device-name": "",
                        "code": "",
                        "face-timeout": "", 
                        "code-timeout": "",
                        "sensors": "",
                        "names": []
            }

sensors = {"name": [],
           "address": []}

# Adds a new face to the facial recgonition
def newFace(face_id, names, user_name):
    # Writes the new name to the text file to be loaded on startup
    names.append(user_name)
    settings_values['names'] = names
    settings_json = json.dumps(settings_values, indent=4)
    writeJSON("settings.json", settings_json)

# Writing to sample.json
def writeJSON(filename, data):
  with open(str(filename), "w") as outfile:
      outfile.write(data)
  outfile.close()

# Function each sensor needs to run on for bluetooth connection
def threads(thread_name, window, addr):
    sock = bc.connect(addr)
    while True:
        ret = bc.rx_and_echo(sock)
        ret = ret.decode()
        if ret == '1':
            window.write_event_value('ALARM', thread_name)
        elif exit_event.is_set():
            break
    bc.disconnect(sock)

    print("Thread done \n")

# Runs the keypad once the alarm has been triggered
def keypad_f(code, timeout):
    # Defines the layout for our keypad window
    keypad_layout = [
            [sg.Input('', size=(10, 1), key='input')],
            [sg.Button('1'), sg.Button('2'), sg.Button('3'), sg.Button('4')],
            [sg.Button('5'), sg.Button('6'), sg.Button('7'), sg.Button('8')],
            [sg.Button('9'), sg.Button('0'), sg.Button('⏎', key='Submit'), sg.Button('Clear')],
            [sg.Text('', size=(15, 1), font=('Helvetica', 18),
                     text_color='red', key='out')],
        ]
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
    return count

def runSettings():
    global settings_values
    settings_saved = False
    #Settings Layout
    settings_layout = [
                    [sg.Text("Settings", 
                             size=(60, 1), 
                             justification="center",
                             font=header)],
                    [sg.Text("We need to run through some settings to get started.", 
                             size=(50, 1), 
                             font=default_set, 
                             justification="center")],
                    [sg.Text('General', 
                             size=(30,1), 
                             justification="left", 
                             font=header)],
                    [sg.HSeparator(pad=(500, 1))],
                    [sg.Push(), sg.Text('Please enter a name for this device.', 
                             font=default_set), sg.Push(),
                     sg.InputText(default_text = settings_values['device-name'], 
                                  key='DEVICENAME', 
                                  size=(25,1)), sg.Push()],
                    [sg.Text('Security', 
                             size=(30,1),
                             justification="left", 
                             font=header)],
                    [sg.HSeparator(pad=(500, 1))],
                    [sg.Push(), sg.Text('Please enter a deactivation password.', 
                             font=default_set), sg.Push(),
                     sg.InputText(default_text = settings_values['code'], 
                                  key='CODE', 
                                  size=(25,1)), sg.Push()],
                    [sg.Push(), sg.Text('Please enter the timeout time for facial detection. DEFAULT:100', 
                             font=default_set), sg.Push(),
                     sg.InputText(default_text = settings_values['face-timeout'], 
                                  key='TIMEOUT_F', 
                                  size=(25,1)), sg.Push()],
                    [sg.Push(), sg.Text('Please enter the timeout time for passcode. DEFAULT:200',
                             font=default_set), sg.Push(),
                     sg.InputText(default_text = settings_values['code-timeout'], 
                                  key='TIMEOUT_P', 
                                  size=(25,1)), sg.Push()],
                    [sg.Text('Connect', 
                             size=(30,1), 
                             justification="left", 
                             font=header)],
                    [sg.HSeparator(pad=(500, 1))],
                    [sg.Text("Let's add some sensors to the system!", 
                             size=(60,1), 
                             justification="left",
                             font=default_set)],
                    [sg.Button("Scan for Sensors",
                               font=default)],
                    [sg.Listbox("", 
                                size=(80,5), 
                                key='DEVICES')],
                    [sg.Button("Save Settings"), 
                     sg.Button("EXIT", 
                               size=(10, 1))],                
    ]

    settings = sg.Window("(AI)-larm STARTUP", settings_layout, resizable=True, finalize=True, element_justification='c')
    settings.maximize()

    while True:
        event, values = settings.read()  # read the form
        if event == sg.WIN_CLOSED or event == "EXIT":  # if the X button clicked, just exit
            break
        if event == "Scan for Sensors":
            scanbt, sensoraddr = bc.scan_devices()
            settings['DEVICES'].update((scanbt))
            sensname = []
            for x in range(len(sensoraddr)):
                sensname.append(sg.popup_get_text("Add a name for the sensor " + sensoraddr[x]))
            sensors['name'] = sensname
            sensors['address'] = sensoraddr

        if event == "Save Settings":
            settings_values['device-name'] = values['DEVICENAME']
            settings_values['code'] = values['CODE']
            settings_values['face-timeout'] = values['TIMEOUT_F']
            settings_values['code-timeout'] = values['TIMEOUT_P']
            settings_values['sensors'] = sensors
            settings_json = json.dumps(settings_values, indent=4)
            writeJSON("settings.json", settings_json)
            settings_saved = True
            break
    settings.close()
    if(settings_saved == True):
        os.execv(sys.executable, ['python3'] + sys.argv)

def main():
    global settings_values
    names = settings_values['names']
    devicename = settings_values['device-name']

    sensor_addr = settings_values['sensors']['address']
    sensor_name = settings_values['sensors']['name']

    status = "DISARMED"
    sensor_list = ""

    if(len(sensor_name) == 0):
        sensor_list = "No sensors added."
    else:
        for s in range(len(sensor_name)):
            sensor_list += sensor_name[s] + "\n"
    print(sensor_list)

    # Define the window layout for the intro screen.
    homescreen = [
        [sg.Text("Welcome to \n(AI)-larm", 
                 justification="center", 
                 font=("bold", 30))],
        [sg.HSeparator(pad=(500,1))],
        [sg.Text("Device: ", 
                 font=default, 
                 justification="center"),
         sg.Text(devicename, 
                 font=default,
                 background_color="teal")],
        [sg.Text("Today is: ", 
                 font=default,
                 justification='c'),
         sg.Text('', 
                 font=default,
                 key='DATE',
                 background_color="teal")],
        [sg.Text("The current time is: ", 
                 font=default,
                 justification='c'),
         sg.Text('', 
                 font=default,
                 key='TIME',
                 background_color="teal")],
        [sg.VPush()],
        [sg.Text("System Status", 
                 font=header,
                 justification='c')],
        [sg.HSeparator(pad=(500,1))],
        [sg.Text("The system is currently ", 
                 font=default,
                 justification='c'),
         sg.Text(status, 
                 font=default,
                 key='STATUS',
                 background_color="green")],
        [sg.Text("Your sensors: \n" + sensor_list, 
                 font=default,
                 justification='c')],
        [sg.Button("ARM SYSTEM", font=header)],
        [sg.VPush()],
        [sg.Text("Options", 
                 font=header)],
        [sg.HSeparator(pad=(500,1))],
        [sg.Text('Name: ',
                 font=default), 
         sg.InputText(key='USER'), 
         sg.Button("Add New Face")], # Button to add a new face to be trained
        [sg.Button("Facial Recognition")], # Button to run the facial recognition software
        [sg.Button("Change settings")], # Button used to change settings
        [sg.Button("EXIT")] # Button to Exit the GUI from other screen
    ]                                                                

    # Create the window and show it without the plot
    window = sg.Window("Facial Recognition", homescreen, resizable=True, finalize=True, element_justification='c', border_depth=5)
    i = 0
    threads = []
    while i < len(sensor_addr):
        t = threading.Thread(target=threads, args=(sensor_name[i], window, sensor_addr[i],), daemon=True).start()
        threads.append(t)
        i = i + 1
    window.Maximize()
    window['DATE'].update(time.strftime('%B:%d:%Y'))
    window['TIME'].update(time.strftime('%H:%M:%S'))

    while True:
        event, values = window.read(timeout=10)

        # TODO: Add in alarm if user fails to deactivate

        # Arm the system to allow alarms to be triggered
        if(event == "ARM SYSTEM"):
            status = "ARMED"
            window['STATUS'].update(status, background_color="red")

        # If the alarm is triggered and the system is armed go off
        if(event == "ALARM" and status == "ARMED"):
            name = fr.main(cascPath, names, settings_values['face-timeout'])
            if (name == "unknown"):
                count = keypad_f(settings_values['code'], settings_values['code-timeout'])
                if count >= int(settings_values['code-timeout']):
                    sp.speaker()
                else:
                    sg.Popup("Welcome back! Sensor " + values["ALARM"] + " went off", keep_on_top = True)
                    status = "DISARMED"
            else:
                sg.Popup('Welcome back ' + name + " Sensor " + values["ALARM"] + " went off", keep_on_top = True)
                status = "DISARMED"
                window['STATUS'].update(status, background_color="green")


        # Exit event to close the GUI
        if event == "Exit" or event == sg.WIN_CLOSED or event == "EXIT":
            break


        # New face button is pressed
        if event == "New Face":
            # For each person, enter one numeric face id
            face_id = len(names) + 1
            user_name = values['USER']
            # Makes sure they have entered in both a name and ID for the user
            if user_name == '':
                sg.Popup('Add a valid name for the user', keep_on_top = True)
                continue
            # Adds the new face to the settings file
            newFace(face_id, names, user_name)
            # Calls the data collection function
            dc.main(face_id, user_name, cascPath)
            # Trains the ML model after taking the images
            ft.main(cascPath)
            # Creates a popup telling the user the face was trained
            sg.Popup('Face added as ID #' + str(face_id) + " and name " + str(user_name), keep_on_top = True)

        # If the Facial Recognition button is clicked
        if event == "Facial Recognition":
            name = fr.main(cascPath, names, settings_values['face-timeout'])
            if name == "unknown":
                keypad_f(settings_values['code'], settings_values['code-timeout'])
            else:
                sg.Popup('Welcome back ' + name, keep_on_top = True)

        # Allows users to change the settings once the device is running
        if event == "Change settings":
            runSettings()
            # Reads in the code from the .json file
            with open('settings.json', 'r') as f:
                settings_values = json.load(f)

        window['DATE'].update(time.strftime('%B %d, %Y'))
        window['TIME'].update(time.strftime('%H:%M:%S'))
    window.close()
    for x in threads:
        x.join()

# Reads in the cascade file to be used
cascPath = sys.argv[1]
faceCascade = cv2.CascadeClassifier(cascPath)

exit_event = threading.Event()

# If settings file doesn't exist we need to generate it
if(os.path.isfile('./settings.json') == False):
        runSettings()

with open('settings.json', 'r') as f:
    settings_values = json.load(f)

main()

exit_event.set()

print("ENDED")