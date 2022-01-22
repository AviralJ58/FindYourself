from PIL import Image, ImageTk, ImageSequence
import PySimpleGUI as sg
import face_recognition
import os
from shutil import copy
import cv2
import time
import multiprocessing
import shutil
def capture_image():
    global knownFace
    knownImgPath='known'

    print("Capturing images... ")
    camera = cv2.VideoCapture(0)
    for i in range(10):
        time.sleep(1)
        print(i+1,"done")
        return_value, image = camera.read()
        if not os.path.exists('known'):
            os.makedirs('known')
        cv2.imwrite('known\opencv'+str(i)+'.png', image)
    del(camera)

    print("Encoding...")
    for filename in os.listdir(knownImgPath):
        known=face_recognition.load_image_file(os.path.join(knownImgPath, filename))
        try:
            knownEncoding=face_recognition.face_encodings(known)[0]
            knownFace.append(knownEncoding)
        except IndexError:
            print("Failed to encode. Trying again.")
            capture_image()

    print("Encoded")

def find_images(lower,upper,files,knownFace,pid):
    counter1=0
    counter2=0
    for i in range(lower,upper):
        filename=files[i]
        faceCascade=cv2.CascadeClassifier("haarcascade\haarcascade_frontalface_alt.xml")
        img=cv2.imread(filename)
        gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        faces=faceCascade.detectMultiScale(gray,1.05,6,minSize=(30,30))
        print("Found {} face(s) in {}".format(len(faces),filename))

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 2)
            faces = img[y:y + h, x:x + w]
            if pid==1: 
                if not os.path.exists('faces\\temp1'):
                    os.makedirs('faces\\temp1')

                cv2.imwrite('faces\\temp1\\temp_face'+str(counter1)+'.jpg', faces)

            elif pid==2: 
                if not os.path.exists('faces\\temp2'):
                    os.makedirs('faces\\temp2')

                cv2.imwrite('faces\\temp2\\temp_face'+str(counter2)+'.jpg', faces)

            if pid==1: unknown=face_recognition.load_image_file('faces\\temp1\\temp_face'+str(counter1)+'.jpg')
            elif pid==2: unknown=face_recognition.load_image_file('faces\\temp2\\temp_face'+str(counter2)+'.jpg')

            unknownEncodings=face_recognition.face_encodings(unknown)

            if len(unknownEncodings)>0:
                result=face_recognition.compare_faces(knownFace,unknownEncodings[0],0.55)
            
                if result.count(True)>=5:
                    if not os.path.exists('my_photos'):
                        os.makedirs('my_photos')
                    copy(filename,'my_photos')
                    break

                if pid==1: counter1+=1         
                elif pid==2: counter2+=1                        

if __name__ =='__main__':
    start= time.time()
    knownFace=[]
    files=[]
    directory=input("Enter directory: ")
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        if (f.lower().endswith(".jpg") or f.lower().endswith(".png") or f.lower().endswith(".jpeg")):
            files.append(f)

    print(files)
    capture_image()
    p1=multiprocessing.Process(target=find_images, args=(0,int(len(files)/2),files,knownFace,1))
    p2=multiprocessing.Process(target=find_images, args=(int(len(files)/2),len(files),files,knownFace,2))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    shutil.rmtree('faces', ignore_errors=True)
    shutil.rmtree('known', ignore_errors=True)
    end=time.time()
    print(end-start)
"""
    Demo_Animated_GIFs_Using_PIL.py
    
    You'll find other animated GIF playback demos for PySimpleGUI that use the tkinter built-in GIF parser.
    That is how the built-in PySimpleGUI Image.update_animation is used.
    
    If you want to do the GIF file parsing yourself using PIL and update your Image element yourself, then
    this is one possible technique.
    This particular demo will loop playing the GIF file over and over.  To not loop, remove the while True statement.
    Copyright 2020 PySimpleGUI.org
"""

gif_filename = r'loading.gif'

layout = [[sg.Text('Happy Thursday!', background_color='#A37A3B', text_color='#FFF000',  justification='c', key='-T-', font=("Bodoni MT", 25))],
          [sg.Image(key='-IMAGE-')]]

window = sg.Window('Window Title', layout, element_justification='c', margins=(0,0), element_padding=(0,0), finalize=True)

window['-T-'].expand(True, True, True)      # Make the Text element expand to take up all available space

interframe_duration = Image.open(gif_filename).info['duration']     # get how long to delay between frames

while True:
    for frame in ImageSequence.Iterator(Image.open(gif_filename)):
        event, values = window.read(timeout=interframe_duration)
        if event == sg.WIN_CLOSED:
            exit(0)
        window['-IMAGE-'].update(data=ImageTk.PhotoImage(frame) )