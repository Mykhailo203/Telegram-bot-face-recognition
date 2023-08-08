import cv2
import face_recognition
from simple_facerec import SimpleFacerec


sfr = SimpleFacerec
#sfr.load_encoding_images("img/")

cap = cv2.VideoCapture(0)


while True:
    ret, frame = cap.read()

    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1)

    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()
