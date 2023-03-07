import cv2
import os
import PySimpleGUI as sg

def main(id_num, user_name, cascade):
    cam = cv2.VideoCapture(0)
    cam.set(3, 480) # set video width
    cam.set(4, 350) # set video height
    face_detector = cv2.CascadeClassifier(cascade)
    # For each person, enter one numeric face id
    face_id = id_num
    print("\n [INFO] Initializing face capture. Look the camera and wait ...")

    # layout the window
    layout = [[sg.Text('A custom progress meter')],
            [sg.ProgressBar(30, orientation='h', size=(20, 20), key='progressbar')],
            [sg.Image(filename="", key="-IMAGE-")],
            [sg.Cancel()]]
    # create the window`
    window = sg.Window('Custom Progress Meter', layout, modal = True, finalize=True)
    window.Maximize()
    progress_bar = window['progressbar']
    # Initialize individual sampling face count
    count = 0
    while(True):
        event, values = window.read(timeout=20)
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(gray, 1.3, 5)
        # cv2.imshow('image', img)
        progress_bar.UpdateBar(count)
        imgbytes = cv2.imencode(".png", img)[1].tobytes()
        window["-IMAGE-"].update(data=imgbytes)
        for (x,y,w,h) in faces:
            cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)     
            # Save the captured image into the datasets folder
            cv2.imwrite("dataset/" + str(user_name) + "." + str(face_id) + '.' +  
                        str(count) + ".jpg", gray[y:y+h,x:x+w])
            count += 1
        k = cv2.waitKey(100) & 0xff # Press 'ESC' for exiting video
        if k == 27:
            break
        elif count >= 30: # Take 30 face sample and stop video
             break
        elif event == 'Cancel':
            break
    # Do a bit of cleanup
    print("\n [INFO] Exiting Program and cleanup stuff")
    cam.release()
    window.close()
    cv2.destroyAllWindows()