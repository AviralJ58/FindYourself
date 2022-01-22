import face_recognition
import os
from shutil import copy
import cv2
import time
import multiprocessing
import shutil
import PySimpleGUI as sg
from PIL import Image, ImageTk, ImageSequence
sg.theme('Dark Blue 2')

def index_window():
    sg.theme('Dark Blue 2')
    index_layout = [
        [sg.Text('Add path of the folder containing images to be indexed.')],
        [sg.In(size=(25, 1), enable_events=True, key="-IN-"),
            sg.FolderBrowse(),],
        [sg.Text('Add path of the folder to save the images.')],
        [sg.In(size=(25, 1), enable_events=True, key="-OUT-"),
            sg.FolderBrowse(),],
        [sg.Submit(), sg.Cancel()]
    ]
    index_window = sg.Window('ImageFinder', index_layout,size=(400, 400),element_justification='center')

    while True:
        event, values = index_window.read()
        if event in (None, 'Cancel', sg.WIN_CLOSED):
            index_window.close()
            break
            
        elif event == 'Submit':
            directory=values['-IN-']
            output=values['-OUT-']
            index_window.close()
            
            return directory,output

def capture_image_window():
    sg.theme('Dark Grey 13')
    capture_window_layout = [
        [sg.Text('Capture Image')],
        [sg.B('OK'), sg.Cancel()]
    ]
    capture_window = sg.Window('Capture Image', capture_window_layout,size=(400, 400),element_justification='center')
    while True:
        event, values = capture_window.read()
        if event in (None, 'Cancel', sg.WIN_CLOSED):
            capture_window.close()
            break
            
        elif event == 'OK':
            
            key = capture_image()
            if key !=1:
                sg.popup('Something went wrong. Please try again!')
                break

            else:
                capture_window.close()
                sg.popup('Images Captured! Processing, please wait!')
                break

def capture_image():
    global knownFace
    knownImgPath = 'known'

    print("Capturing images... ")
    camera = cv2.VideoCapture(0)
    for i in range(10):
        time.sleep(1)
        print(i+1, "done")
        return_value, image = camera.read()
        if not os.path.exists('known'):
            os.makedirs('known')
        cv2.imwrite('known\opencv'+str(i)+'.png', image)
    del(camera)

    print("Encoding...")
    for filename in os.listdir(knownImgPath):
        known = face_recognition.load_image_file(
            os.path.join(knownImgPath, filename))
        try:
            knownEncoding = face_recognition.face_encodings(known)[0]
            knownFace.append(knownEncoding)
        except IndexError:
            print("Failed to encode. Trying again.")
            capture_image()

    encode = 1
    print("Encoding Complete!")
    return encode

def find_images(lower, upper, files, knownFace, pid,output):
    counter1 = 0
    counter2 = 0
    for i in range(lower, upper):
        filename = files[i]
        faceCascade = cv2.CascadeClassifier(
            "haarcascade\haarcascade_frontalface_alt.xml")
        img = cv2.imread(filename)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, 1.05, 6, minSize=(30, 30))
        print("Found {} face(s) in {}".format(len(faces), filename))

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 2)
            faces = img[y:y + h, x:x + w]
            if pid == 1:
                if not os.path.exists('faces\\temp1'):
                    os.makedirs('faces\\temp1')

                cv2.imwrite('faces\\temp1\\temp_face' +
                            str(counter1)+'.jpg', faces)

            elif pid == 2:
                if not os.path.exists('faces\\temp2'):
                    os.makedirs('faces\\temp2')

                cv2.imwrite('faces\\temp2\\temp_face' +
                            str(counter2)+'.jpg', faces)

            if pid == 1:
                unknown = face_recognition.load_image_file(
                    'faces\\temp1\\temp_face'+str(counter1)+'.jpg')
            elif pid == 2:
                unknown = face_recognition.load_image_file(
                    'faces\\temp2\\temp_face'+str(counter2)+'.jpg')

            unknownEncodings = face_recognition.face_encodings(unknown)

            if len(unknownEncodings) > 0:
                result = face_recognition.compare_faces(
                    knownFace, unknownEncodings[0], 0.55)

                if result.count(True) >= 5:
                    if not os.path.exists(output):
                        os.makedirs(output)
                    copy(filename, output)
                    break

                if pid == 1:
                    counter1 += 1
                elif pid == 2:
                    counter2 += 1

def gify():
    gif_filename = r'loading.gif'

    layout = [[sg.Text('Finding you!',pad=(0,30), text_color='#FFF000',  justification='c', key='-T-', font=("Bodoni MT", 25))],
            [sg.Image(key='-IMAGE-')]]

    window = sg.Window('Processing', layout,size=(400, 400),element_justification='c', margins=(0,0), element_padding=(0,0), finalize=True)

    window['-T-'].expand(True, True, True)      

    interframe_duration = Image.open(gif_filename).info['duration']     

    while True:
        for frame in ImageSequence.Iterator(Image.open(gif_filename)):
            event, values = window.read(timeout=interframe_duration)
            if event == sg.WIN_CLOSED:
                exit(0)
            window['-IMAGE-'].update(data=ImageTk.PhotoImage(frame) )


def mainfunc(output):
    print("Starting...")
    p0=multiprocessing.Process(target=gify)
    p1=multiprocessing.Process(target=find_images, args=(0,int(len(files)/2),files,knownFace,1,output))
    p2=multiprocessing.Process(target=find_images, args=(int(len(files)/2),len(files),files,knownFace,2,output))
    p0.start()
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    print("Done!")

    shutil.rmtree('faces', ignore_errors=True)
    shutil.rmtree('known', ignore_errors=True)
    end=time.time()
    print(end-start)

    if end-start>0:
        p0.terminate()
        sg.popup('Found you in {} photos.\nTime taken: {}'.format(len(os.listdir(output)),str(end-start)))
        return 0

if __name__ == '__main__':
    start= time.time()
    knownFace=[]
    files=[]
    directory,output=index_window()

    if(directory==''):
        print("No directory selected")
        exit()
    if(output==''):
        print("No output folder selected")
        exit()
    
    else:
        for filename in os.listdir(directory):
            f = os.path.join(directory, filename)
            if (f.lower().endswith(".jpg") or f.lower().endswith(".png") or f.lower().endswith(".jpeg")):
                files.append(f)
        capture_image_window()

    mainfunc(output)
    