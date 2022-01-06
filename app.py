from PIL import Image
import face_recognition
import os
from shutil import copy
# Load the jpg file into a numpy array
directory=input("Enter directory: ")
knownImgPath=input("Enter path of known image: ")
known=face_recognition.load_image_file(knownImgPath)
knownEncoding=face_recognition.face_encodings(known)[0]
knownFace=[knownEncoding]
for filename in os.listdir(directory):
    print("******\n",filename,"\n******")
    image = face_recognition.load_image_file(os.path.join(directory,filename))
    face_locations = face_recognition.face_locations(image)
    print("I found {} face(s) in this photograph.".format(len(face_locations)))

    for face_location in face_locations:

        top, right, bottom, left = face_location
        
        face_image = image[top:bottom, left:right]
        pil_image = Image.fromarray(face_image)
        pil_image.save('temp_face.jpg')
        unknown=face_recognition.load_image_file('temp_face.jpg')
        unknownEncoding=face_recognition.face_encodings(unknown)[0]
        result=face_recognition.compare_faces(knownFace,unknownEncoding)
        print(result)
        os.remove('temp_face.jpg')
        if result==[True]:

            pil_image.show()
            if not os.path.exists('my_photos'):
                os.makedirs('my_photos')
            copy(os.path.join(directory,filename),'my_photos')
            break