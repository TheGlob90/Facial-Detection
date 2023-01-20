# Facial-Detection
Before you start, make sure you have Python 3 installed and have cv2 and pillow installed.
```
pip install pillow, opencv-python
```
To properly run the program you need to first need to collect data of a face. To do this, run the command shown below.
```
 python3 data_collection.py
```
Once you have collected images of the face you want to train the model with, you then train the model.
```
python3 face_training.py
```
Then you can run the program to detect a face.
```
python3 face_rec.py
```
