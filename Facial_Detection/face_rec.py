import cv2
import numpy as np
import os 
import PySimpleGUI as sg

def main(cascade, names, timeout):
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    # Read the trained .yml file that was generated previously
    recognizer.read('trainer/trainer.yml')
    # Give the type of cascade we are using at this time
    faceCascade = cv2.CascadeClassifier(cascade)
    font = cv2.FONT_HERSHEY_SIMPLEX
    #indicate id counter
    id = 0
    # Initialize and start realtime video capture
    cam = cv2.VideoCapture(0)
    cam.set(3, 480) # set video widht
    cam.set(4, 350) # set video height
    # Define min window size to be recognized as a face
    minW = 0.01*cam.get(3)
    minH = 0.01*cam.get(4)
    # Loop until we kill the program
    count = 0
    recognized = 0
    num_of_times = []
    while count <= int(timeout):
        ret, img =cam.read()
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    
        faces = faceCascade.detectMultiScale( 
            gray,
            scaleFactor = 1.2,
            minNeighbors = 5,
            minSize = (int(minW), int(minH)),
        )
        for(x,y,w,h) in faces:
            cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
            id, confidence = recognizer.predict(gray[y:y+h,x:x+w])
        
            # If confidence is less then 70 ==> "0" : perfect match 
            # The smaller the number confidence needs to be less than, the harder it is to get a match
            if (confidence < 100):
                id = names[id - 1]
                id = id.replace('\n', '')
                num_of_times.append(id)
                recognized = recognized + 1
            else:
                id = "unknown"
        
            cv2.putText(
                        img, 
                        str(id), 
                        (x+5,y-5), 
                        font, 
                        1, 
                        (255,255,255), 
                        2
                    ) 
    
        cv2.imshow('camera',img) 
        k = cv2.waitKey(10) & 0xff # Press 'ESC' for exiting video
        if k == 27:
            break
        if recognized == 20:
            highest_count = 0
            loop_count = 0
            for i in names:
                current = num_of_times.count(i)
                if(current > highest_count):
                    highest_count = current
                    id = str(names[loop_count])
                loop_count = loop_count + 1
            break
        count = count + 1
    # Do a bit of cleanup
    if count > int(timeout):
        id = "unknown"
    print("\n [INFO] Exiting Program and cleanup stuff")
    cam.release()
    cv2.destroyAllWindows()
    return(str(id))