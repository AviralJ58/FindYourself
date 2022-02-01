import face_recognition
import os
from shutil import copy
import cv2
import time
import multiprocessing
import shutil
import PySimpleGUI as sg
from PIL import Image, ImageTk, ImageSequence

def index_window():
    sg.Window('Title',[[sg.Image('icon.png')]], transparent_color=sg.theme_background_color(),
        no_titlebar=True,keep_on_top=True).read(timeout=1500,close=True)
    index_layout = [[sg.Image('img1.png')],
        [sg.Text('Add path of the folder containing images.',background_color='#0E1E42')],
        [sg.In(size=(25, 1), enable_events=True, key="-IN-"),
            sg.FolderBrowse(), ],
        [sg.Text('Add path of the folder to save the images.',background_color='#0E1E42')],
        [sg.In(size=(25, 1), enable_events=True, key="-OUT-"),
            sg.FolderBrowse(), ],
        [sg.B('OK'), sg.Cancel()],[sg.VPush(background_color='#0E1E42')]
    ]
    index_window = sg.Window('ImageFinder', index_layout, size=(
        500, 700), element_justification='center',  font=('Helvetica 15',15), icon='icon.ico', background_color='#0E1E42',margins=(0,0))

    while True:
        event, values = index_window.read()
        if event in (None, 'Cancel', sg.WIN_CLOSED):
            index_window.close()
            exit(0)

        elif event == 'OK':
            directory = values['-IN-']
            output = values['-OUT-']
            index_window.close()

            return directory, output

def capture_image_window(user):
    global p0
    capture_window_layout = [[sg.VPush(background_color='#0E1E42')],
        [sg.Text('The application needs some images to identify \nyou in photos. Please select an action.', justification='c',background_color='#0E1E42')],
        [sg.Button('Capture using Webcam')], [sg.Button('Upload a folder containing photos')], [sg.Cancel()],
        [sg.Text('Please wait for the process to complete!',key='cnf')],[sg.VPush(background_color='#0E1E42')]
    ]
    capture_window = sg.Window('Capture Image', capture_window_layout, size=(
        500, 400), element_justification='center', font='Helvetica 15',finalize=True, icon='icon.ico',background_color='#0E1E42')
    capture_window.Element('cnf').Update(visible = False)
    while True:
        event, values = capture_window.read()
        if event in (None, 'Cancel', sg.WIN_CLOSED):
            sg.popup('Operation cancelled',title='Terminating', font='Helvetica 15', 
                auto_close=True, auto_close_duration=3, background_color='#0E3E7B',icon='icon.ico')
            capture_window.close()
            exit(0)

        elif "Capture using Webcam" in event:
            capture_window.Element('cnf').Update(visible = True)
            sg.popup('Capturing images...',title='Capturing', font='Helvetica 15', 
                auto_close=True, auto_close_duration=3, background_color='#0E3E7B',icon='icon.ico')
            capture_window.disable()
            key= capture_image(user)
            if key != 1:
                sg.popup('Something went wrong. Please try again!', font='Helvetica 15', 
                    auto_close=True, auto_close_duration=3,background_color='#0E3E7B',icon='icon.ico')
                capture_window.enable()
                break

            else:
                p0 = multiprocessing.Process(target=gify)
                p0.start()
                capture_window.close()
                sg.popup('Images Captured! Processing, please wait!', title='Captured', font='Helvetica 15', 
                    auto_close=True, auto_close_duration=3, button_type='',background_color='#0E3E7B',icon='icon.ico')
                break
            
        elif "Upload a folder containing photos" in event:
            capture_window.close()
            key= upload_window(user)
            if key != 1:
                sg.popup('Something went wrong. Please try again!', font='Helvetica 15',
                    auto_close=True, auto_close_duration=3,background_color='#0E3E7B',icon='icon.ico')
                capture_window.enable()
                break

            else:
                p0 = multiprocessing.Process(target=gify)
                p0.start()
                break

def capture_image(user):
    global knownFace
    knownImgPath=os.path.join(user,'known')
    if not os.path.exists(knownImgPath):
        os.makedirs(knownImgPath)

    print("Capturing images... ")
    camera = cv2.VideoCapture(0)
    for i in range(10):
        time.sleep(1)
        print(i+1, "done")
        return_value, image = camera.read()
        cv2.imwrite(os.path.join(knownImgPath,'opencv'+str(i)+'.png'), image)
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
    sg.popup('Images Captured! Processing, please wait!', title='Captured', font='Helvetica 15', 
        auto_close=True, auto_close_duration=3, button_type='',background_color='#0E3E7B',icon='icon.ico')

    print("Encoding Complete!")
    return encode

def upload_window(user):
    window_layout = [[sg.VPush(background_color='#0E1E42')],
        [sg.Text('Upload a folder containing your photos. \nMore photos will increase accuracy. \nPlease make sure the folder contains solo images.', 
            justification='c',background_color='#0E1E42')],
        [sg.In(size=(25, 1), enable_events=True, key="-IN-"),
            sg.FolderBrowse(), ],
        [sg.B('OK'), sg.Cancel()],[sg.Text('Please wait for the process to complete!',key='cnf',background_color='#0E1E42')],[sg.VPush(background_color='#0E1E42')]
    ]
    window = sg.Window('ImageFinder', window_layout, size=(500, 500), 
        element_justification='center', font=('Helvetica 15',15), icon='icon.ico', finalize=True, background_color='#0E1E42')
    window.Element('cnf').Update(visible = False)

    while True:
        event, values = window.read()
        if event in (None, 'Cancel', sg.WIN_CLOSED):
            sg.popup('Operation cancelled',title='Terminating', font='Helvetica 15',background_color='#0E3E7B',icon='icon.ico')
            window.close()
            exit(0)

        elif event == 'OK':
            window.disable()
            window.Element('cnf').Update(visible = True)
            sg.popup('Uploading images...',title='Uploading', font='Helvetica 15',
                auto_close=True, auto_close_duration=3,background_color='#0E3E7B',icon='icon.ico')
            directory = values['-IN-']
            print("Encoding...")
            for filename in os.listdir(directory):
                f = os.path.join(directory, filename)
                if (f.lower().endswith(".jpg") or f.lower().endswith(".png") or f.lower().endswith(".jpeg")):
                    known = face_recognition.load_image_file(f)
                    try:
                        knownEncoding = face_recognition.face_encodings(known)[0]
                        knownFace.append(knownEncoding)
                    except IndexError:
                        print("Failed to encode. Trying again.")
                        window.close()
                        upload_window(user)

            encode = 1
            print("Encoding Complete!")
            window.close()
            return encode

            

def find_images(lower, upper, files, knownFace, pid, output, user):
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
        loc=os.path.join(user,'faces')
        temp1=(os.path.join(loc,'temp1'))
        temp2=(os.path.join(loc,'temp2'))
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 2)
            faces = img[y:y + h, x:x + w]
            if pid == 1:
                if not os.path.exists(temp1):
                    os.makedirs(temp1)

                cv2.imwrite(temp1+'\\temp_face' +
                            str(counter1)+'.jpg', faces)

            elif pid == 2:
                if not os.path.exists(temp2):
                    os.makedirs(temp2)

                cv2.imwrite(temp2+'\\temp_face' +
                            str(counter2)+'.jpg', faces)

            if pid == 1:
                unknown = face_recognition.load_image_file(
                    temp1+'\\temp_face'+str(counter1)+'.jpg')
            elif pid == 2:
                unknown = face_recognition.load_image_file(
                    temp2+'\\temp_face'+str(counter2)+'.jpg')

            unknownEncodings = face_recognition.face_encodings(unknown)

            if len(unknownEncodings) > 0:
                result = face_recognition.compare_faces(
                    knownFace, unknownEncodings[0], 0.55)

                if result.count(True) >= 5:
                    outPath=os.path.join(output,'images')
                    if not os.path.exists(outPath):
                        os.makedirs(outPath)
                    copy(filename, outPath)
                    break

                if pid == 1:
                    counter1 += 1
                elif pid == 2:
                    counter2 += 1


def gify():
    sg.theme_background_color('#3F51B5')
    gif_filename = r'loading.gif'

    layout = [[sg.Text('Finding you!', pad=(0, 30), text_color='#F7AC3B',  justification='c', key='-T-',font=('Helvetica 15',30),background_color='#3F51B5')],
              [sg.Image(key='-IMAGE-')]]

    window = sg.Window('Processing', layout, size=(400, 400), element_justification='c', margins=(0, 0), 
        element_padding=(0, 0), finalize=True, font='Helvetica 15', icon='icon.ico')

    window['-T-'].expand(True, True, True)

    interframe_duration = Image.open(gif_filename).info['duration']

    while True:
        for frame in ImageSequence.Iterator(Image.open(gif_filename)):
            event, values = window.read(timeout=interframe_duration)
            if event == sg.WIN_CLOSED:
                exit(0)
            window['-IMAGE-'].update(data=ImageTk.PhotoImage(frame))


def mainfunc(output,user):
    print("Starting...")
    p1 = multiprocessing.Process(target=find_images, args=(
        0, int(len(files)/2), files, knownFace, 1, output, user))
    p2 = multiprocessing.Process(target=find_images, args=(
        int(len(files)/2), len(files), files, knownFace, 2, output, user))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    print("Done!")

    shutil.rmtree(user, ignore_errors=True)
    end = time.time()
    print(end-start)

    if end-start > 0:
        p0.terminate()
        outPath=os.path.join(output,'images')
        sg.popup('Found you in {} photos.\nTime taken: {} secs'.format(
            len(os.listdir(outPath)), str(end-start)[:5]), title='Done', font='Helvetica 15',background_color='#0E3E7B',icon='icon.ico')
        return 0

if __name__ == '__main__':
    # On Windows calling this function is necessary.
    multiprocessing.freeze_support()
    start = time.time()
    knownFace = []
    files = []
    user=os.path.expanduser("~")
    user=os.path.join(user,'ImageFinder')
    directory, output = index_window()

    if(directory == ''):
        print("No directory selected")
        exit(0)
    if(output == ''):
        print("No output folder selected")
        exit(0)

    else:
        for filename in os.listdir(directory):
            f = os.path.join(directory, filename)
            if (f.lower().endswith(".jpg") or f.lower().endswith(".png") or f.lower().endswith(".jpeg")):
                f=os.path.normcase(f)
                files.append(f)
        
        capture_image_window(user)
        mainfunc(output,user)

        