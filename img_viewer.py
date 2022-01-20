import face_recognition
import os
from shutil import copy
import cv2
import time
import multiprocessing
import shutil
import PySimpleGUI as sg


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

    print("Encoded")
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



def find_images(lower, upper, files, knownFace, pid):
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
                    if not os.path.exists('my_photos'):
                        os.makedirs('my_photos')
                    copy(filename, 'my_photos')
                    break

                if pid == 1:
                    counter1 += 1
                elif pid == 2:
                    counter2 += 1



    



def capture_image_window():
    sg.theme('Dark Grey 13')
    capture_window_layout = [
        [sg.Text('Capture Image')],
        [sg.B('OK'), sg.Cancel()]
    ]
    capture_window = sg.Window('Capture Image Window', capture_window_layout)
    while True:
        event, values = capture_window.read()
        if event in (None, 'Cancel', sg.WIN_CLOSED):
            
            capture_window.close()
            
            index_window.close()
            break
            
        elif event == 'OK':
            
            capture_image()
            capture_window.close()


def index_window():
    # Create PySimpleGUI App for this program
    sg.theme('Dark Grey 13')
    index_layout = [
        [sg.Text('Add path of the folder containing images to be indexed.')],
        [sg.In(size=(25, 1), enable_events=True, key="-IN-"),
            sg.FolderBrowse(),],
        [sg.Submit(), sg.Cancel()]
    ]
    index_window = sg.Window('Index Window', index_layout)

    while True:
        event, values = index_window.read()
        if event in (None, 'Cancel', sg.WIN_CLOSED):
            index_window.close()
            break
            
        elif event == 'Submit':
            directory=values['-IN-']
            index_window.close()
            
            return directory








if __name__ == '__main__':
    start= time.time()
    knownFace=[]
    files=[]
    directory=index_window()
    if(directory==''):
        print("No directory selected")
        exit()
    
    
    else:
        for filename in os.listdir(directory):
            f = os.path.join(directory, filename)
        if (f.lower().endswith(".jpg") or f.lower().endswith(".png") or f.lower().endswith(".jpeg")):
            files.append(f)
        capture_image_window()

    
    print("Starting...")



    # start= time.time()
    # knownFace=[]
    # files=[]
    # for filename in os.listdir(directory):
    #     f = os.path.join(directory, filename)
    #     if (f.lower().endswith(".jpg") or f.lower().endswith(".png") or f.lower().endswith(".jpeg")):
    #         files.append(f)

    # print(files)
    # p1=multiprocessing.Process(target=find_images, args=(0,int(len(files)/2),files,knownFace,1))
    # p2=multiprocessing.Process(target=find_images, args=(int(len(files)/2),len(files),files,knownFace,2))
    # p1.start()
    # p2.start()
    # p1.join()
    # p2.join()
    # shutil.rmtree('faces', ignore_errors=True)
    # shutil.rmtree('known', ignore_errors=True)
    # end=time.time()
    # print(end-start)
    window.close()