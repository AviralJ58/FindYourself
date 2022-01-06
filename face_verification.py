from mtcnn.mtcnn import MTCNN
import cv2
import numpy as np
from keras_vggface.utils import preprocess_input
from keras_vggface.vggface import VGGFace
from scipy.spatial.distance import cosine
import warnings
import os

warnings.filterwarnings("ignore")

def create_bbox(image):
    detector=MTCNN()
    faces=detector.detect_faces(image)
    bounding_box=faces[0]['box']
    cv2.rectangle(image, (bounding_box[0], bounding_box[1]), (bounding_box[0]+bounding_box[2], bounding_box[1]+bounding_box[3]),(0,155,255),2)
    return image

def extract_face(image,resize=(224,224)):
    detector=MTCNN()
    image=cv2.imread(image)
    faces=detector.detect_faces(image)
    x1,y1,width,height=faces[0]['box']
    x2,y2=x1+width,y1+height
    face_boundary=image[y1:y2,x1:x2]
    face_image=cv2.resize(face_boundary,resize)
    return face_image

def get_embeddings(faces):
    face=np.asarray(faces,'float32')
    face=preprocess_input(face, version=2)
    model=VGGFace(model='resnet50',include_top=False,input_shape=(224,224,3),pooling='avg')
    return model.predict(face)

def get_similarity(faces):
    embeddings=get_embeddings(faces)
    score=cosine(embeddings[0],embeddings[1])
    if score<=0.5:
        return "Face Matched",score
    return "Face Not Matched",score

def verify_face():
    global verification,color
    cam = cv2.VideoCapture(0)
    while True:
        ret, frame = cam.read()
        if not ret:
            print("Failed to grab frame")
            break


        k = cv2.waitKey(1)
        font = cv2.FONT_HERSHEY_SIMPLEX
        fontScale = 1
        thickness = 2
        if k%256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break
        elif k%256 == 32:
            # SPACE pressed
            img_name = "face.png"
            cv2.imwrite(img_name, frame)
            print("Written!")
            cv2.destroyWindow('Face')
            for filename in os.listdir(directory):
                faces=[extract_face(image) for image in ['Photo.jpg',os.path.join(directory,filename)]]
                verification,confidence=get_similarity(faces)
                if verification=='Face Matched':
                    if not os.path.exists('my_photos'):
                        os.makedirs('my_photos')
                        os.rename(os.path.join(directory,filename),os.path.join('my_photos',filename))
                        print("Photo matched")
                    color=(0,128,0)
                elif verification=='Face Not Matched':
                    color=(48,48,255)
        
        textsize = cv2.getTextSize(verification, font, 1, 2)[0]
        textX = int((frame.shape[1] - textsize[0]) / 2)
        cv2.putText(frame,verification,(textX,400),font,fontScale,color,thickness,cv2.LINE_AA)
        cv2.imshow("Face", frame)

    cam.release()
    cv2.destroyAllWindows()

verification='Not verified'
color = (255,191,0)
directory=input('Enter directory: ')
# for filename in os.listdir(directory):
#     print(filename)
verify_face()