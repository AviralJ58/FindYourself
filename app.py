import face_recognition
import os
from shutil import copy
import cv2
import time
# Load the jpg file into a numpy array
directory=input("Enter directory: ")
knownImgPath='known'#input("Enter path of known images: ")
knownFace=[]
counter=0

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
    knownEncoding=face_recognition.face_encodings(known)[0]
    knownFace.append(knownEncoding)
print("Encoded")

for filename in os.listdir(directory):
    print("******\n",filename,"\n******")
    image = face_recognition.load_image_file(os.path.join(directory,filename))
    faceCascade=cv2.CascadeClassifier("haarcascade\haarcascade_frontalface_alt.xml")
    img=cv2.imread(os.path.join(directory,filename))
    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    faces=faceCascade.detectMultiScale(gray,1.1,7,minSize=[30,30])
    # face_locations = face_recognition.face_locations(image)
    print("I found {} face(s) in this photograph.".format(len(faces)))

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 2)
        faces = img[y:y + h, x:x + w]
        cv2.imwrite('faces\\temp_face'+str(counter)+'.jpg', faces)
  
        unknown=face_recognition.load_image_file('faces\\temp_face'+str(counter)+'.jpg')
        unknownEncodings=face_recognition.face_encodings(unknown)
        if len(unknownEncodings)>0:
            result=face_recognition.compare_faces(knownFace,unknownEncodings[0],0.5)
            print(result)
        
        if result.count(True)>=5:
            cv2.imshow("face",faces)
            if not os.path.exists('my_photos'):
                os.makedirs('my_photos')
            copy(os.path.join(directory,filename),'my_photos')
            break
        else:
            os.remove('faces\\temp_face'+str(counter)+'.jpg')
        counter+=1