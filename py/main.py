import cv2

from setup import download_task
from capture_controller import CaptureController
from detector import Detector
from direction_calculator import calculate_directions

download_task()

detector = Detector()
captcont = CaptureController()

while True:

    timestamp, mp_image = captcont.get_frame()
    landmarks = detector.get_landmarks(mp_image, timestamp).pose_landmarks[0]
    node_directions = calculate_directions(landmarks)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        for direction_name in node_directions:
            nd = node_directions[direction_name]
            print('\n\n\nDIRNAME:', direction_name, '\n\nVALUES:')
            for i in range(3):
                print(nd[i])
        break


detector.cleanup()
captcont.cleanup()
